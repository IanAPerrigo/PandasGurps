from direct.fsm.FSM import FSM

from managers.turn_manager import TurnManager
from managers.action_resolvers import GenericActionResolver
from managers.simulation_manager import SimulationStateManager
from managers.entity_manager import EntityFsmManager
from managers.interaction_event_manager import InteractionEventManager

from data_models.actions import ActionStatus
from data_models.actions.maneuvers import YieldTurnManeuver
from data_models.actors.status_effects.consciousness import *
from events import Event


class TurnManagementFSM(FSM):
    def __init__(self, turn_manager: TurnManager, action_resolver: GenericActionResolver,
                 simulation_manager: SimulationStateManager, entity_fsm_manager: EntityFsmManager,
                 interaction_event_manager: InteractionEventManager, logger):
        super(TurnManagementFSM, self).__init__(TurnManagementFSM.__name__)

        self.turn_manager = turn_manager
        self.action_resolver = action_resolver
        self.simulation_manager = simulation_manager
        self.entity_fsm_manager = entity_fsm_manager
        self.interaction_event_manager = interaction_event_manager
        self.logger = logger

    def enterManagerSetup(self):
        self.turn_manager.generate_turn_order()
        self.demand("NextTurn")

    def enterNextTurn(self):
        curr_actor = self.turn_manager.get_current_actor()

        if curr_actor is not None:
            # TODO: archive the actions taken by the current actor.
            # IDEA: have history be a serialized egg (python binary)

            # Clear the action manager of excess actions that were not used.
            self.simulation_manager.action_manager.reset_actions_for(curr_actor)

            fsm = self.entity_fsm_manager[curr_actor]
            fsm.request("Complete")

        # Advance the turn.
        self.turn_manager.advance_turn()
        curr_actor = self.turn_manager.get_current_actor()

        # If the top of the round was reached, regenerate the turn order.
        if curr_actor is None:
            self.turn_manager.generate_turn_order()
            self.turn_manager.advance_turn()

        # Begin the actors turn.
        self.demand("TurnBegin")

    def enterTurnBegin(self):
        curr_actor = self.turn_manager.get_current_actor()

        # Determine if this actor can take a turn.
        character_model = self.simulation_manager.entity_model_manager[curr_actor].character_model
        if DEAD in character_model.status_effects:
            # Actor is dead. Skip their turn, and the actor will be cleaned up next turn cycle.
            self.demand("NextTurn")
            return
        elif UNCONSCIOUS in character_model.status_effects:
            # Actor is unconscious, have them attempt to regain consciousness, then end the turn regardless of success.
            Event.signal("actor_regain_consciousness", curr_actor)
            self.demand("NextTurn")
            return
        elif HANGING_ONTO_CONSCIOUSNESS in character_model.status_effects:
            # Actor is hanging onto consciousness, have them attempt to retain it. If they failed to retain,
            # skip their turn. Otherwise, allow them to continue their their turn.
            Event.signal("actor_retain_consciousness", curr_actor)
            if UNCONSCIOUS in character_model.status_effects:
                self.demand("NextTurn")
                return

        # Generate a baseline subjective state.
        self.simulation_manager.generate_subjective_state_for(curr_actor)

        # Reset the list of actions for the current actor.
        self.simulation_manager.action_manager.reset_actions_for(curr_actor)

        # Yield control to the FSM.
        fsm = self.entity_fsm_manager[curr_actor]
        fsm._yield_turn = self._yield_turn
        fsm.keys = self.interaction_event_manager.event_instances
        fsm.step_complete = self._step_complete
        fsm.request("TakingTurn")

        self.demand("TurnLoop")

    def enterTurnLoop(self, *args):
        self.logger.info("[TurnLoop] entering")

    def filterTurnLoop(self, request, args):
        """
        Accept interactions for control from any FSM.
        :param request:
        :param args:
        :return:
        """
        self.logger.info("[TurnLoop] filtering (%s)" % request)

        if request == 'NextTurn':
            return 'NextTurn'

    def exitTurnLoop(self):
        self.logger.info("[TurnLoop] exiting")

    def _yield_turn(self):
        # Only directly yield a turn if the state isn't already transitioning.
        if not self.isInTransition():
            self.request('NextTurn')

    def _step_complete(self):
        first_failed, first_unready, processed_any_action = None, None, False
        curr_actor = self.turn_manager.get_current_actor()

        targets = self.simulation_manager.action_manager.get_submitted_actions(curr_actor)
        unresolved_actions = filter(lambda maneuver: maneuver.status != ActionStatus.RESOLVED, targets)
        for action in unresolved_actions:
            if action.status == ActionStatus.PARTIAL_UNREADY or \
                    action.status == ActionStatus.UNREADY:
                if not first_unready:
                    first_unready = action
            elif action.status == ActionStatus.FAILED:
                first_failed = action
                break
            elif not first_unready and not first_failed:
                self.action_resolver.resolve(action)

                # If the action resolution failed, no need to continue with resolution.
                if action.status == ActionStatus.FAILED:
                    first_failed = action
                    break

                processed_any_action = True

        num_yield_maneuvers = len(list(filter(lambda maneuver: isinstance(maneuver, YieldTurnManeuver), targets)))
        if num_yield_maneuvers > 0:
            self._yield_turn()

        if first_unready:
            # TODO: get all actions after the first unready and display them as "in-progress actions"
            # TODO: refactor this test attempt
            # if isinstance(first_unready, MoveManeuver):
            #     curr_loc = self.grid_model.get_loc_of_obj(first_unready.actor)
            #     unresolved_actions = filter(lambda action: action.status != ActionStatus.RESOLVED, first_unready.actions)
            #     for action in unresolved_actions:
            #         # TODO: filter for action type (currently only movements)
            #         loc = cube_to_offset(curr_loc)
            #         loc_comp = self.grid.path.find("location.%s.%s" % (loc[0], loc[1]))
            #         arrow_path_comp = ArrowPathComponent(parent=loc_comp, direction=action.direction)
            #         curr_loc = np.add(curr_loc, action.get_vector())
            pass
        elif first_failed:
            # TODO: an actual resolution to the problem. Currently will just wipe all actions after the failed action.
            # Delete all maneuvers after the failure.
            self.simulation_manager.action_manager.truncate_failure(first_failed)

        # Issue a grid update only if an action was processed.
        if processed_any_action:
            Event.signal("notify_grid_update")
            # TODO: issue other events (perhaps depending on the effects of the actions)
