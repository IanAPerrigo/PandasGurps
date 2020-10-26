import random

from direct.showbase.ShowBase import ShowBase
from direct.fsm import FSM
from direct.directnotify.DirectNotify import DirectNotify
from panda3d.core import AmbientLight, DirectionalLight

from behaviors.actors import HumanPlayerBehavior

from events.component.actors import RefreshStats

from containers.grid import GridNode, GridConfig
from containers.managers import EntityComponentManagerContainer, EntityModelManagerContainer, EntityFsmManagerContainer
from containers.actors import *
from containers.managers.simulation_manager import SimulationManagerContainer
from containers.managers.turn_manager import TurnManagerContainer
from containers.managers.action_manager import ActionManagerContainer
from containers.managers.action_resolver import GenericResolverContainer
from containers.managers.action_resolver_locator import ActionResolverLocatorContainer
from containers.managers.gui_manager import InteractionEventManagerContainer
from containers.event_handlers import FatalDamageHandlerContainer

from kivy_ui import OverlayApp

# TODO: move to module that sets up resolvers
from containers.managers.action_resolver import *
from data_models.actions import MovementAction, MeleeAttack, ActionStatus
from data_models.actions.maneuvers import MoveManeuver, MoveAttackManeuver, YieldTurnManeuver
from managers.character_creation import *

# TODO: inject this logger
fsm_dbg = DirectNotify().newCategory("FSMDebug")
# TODO: Make DirectNotify a singleton?


class GurpsMain(ShowBase, FSM.FSM):
    def __init__(self, config={}):
        ShowBase.__init__(self)

        base.disableMouse()
        self.kivy_app = kivy_app = OverlayApp(self)
        kivy_app.run()

        # TODO: Might change if fsms need to be located by name
        FSM.FSM.__init__(self, 'fsm_%r' % id(self))

        self.set_background_color(.2, .2, .2, 1)

        # TODO: move to a camera control class
        self.camLens.setNearFar(1, 100)
        self.camLens.setFov(75)
        self.scroll = -20
        self.x_offset = 12
        self.z_offset = -6
        self.cam.setPos(self.cam.getX() + self.x_offset, self.scroll, self.cam.getZ() + self.z_offset)

        InteractionEventManagerContainer.config.override({
            "event_types": [
                '1', #"MOVE_MANEUVER",
                '2', #"MOVE_ATTACK_MANEUVER",
                'VECTOR_NORTH_WEST',
                'VECTOR_NORTH_EAST',
                'VECTOR_EAST',
                'VECTOR_SOUTH_EAST',
                'VECTOR_SOUTH_WEST',
                'VECTOR_WEST',
                'c',
                'm',
                'r',
                'space'
            ]
        })
        self.interaction_event_manager = InteractionEventManagerContainer.interaction_event_manager()

        # TODO: ultimately the showbase will be created from a container.
        #   this will be injected instead
        self.entity_component_manager = EntityComponentManagerContainer.entity_component_manager()
        self.entity_model_manager = EntityModelManagerContainer.entity_model_manager()
        self.entity_fsm_manager = EntityFsmManagerContainer.entity_fsm_manager()
        self.damage_handler = FatalDamageHandlerContainer.fatal_damage_handler()

        # TODo: Move to its own module
        ActionResolverLocatorContainer.config.override({
            MovementAction: MovementResolverContainer,
            MeleeAttack: MeleeAttackResolverContainer,
            MoveManeuver: MoveManeuverResolverContainer,
            MoveAttackManeuver: MoveAttackManeuverResolverContainer,
            YieldTurnManeuver: YieldTurnManeuverResolverContainer,
        })

        self.action_resolver_locator = ActionResolverLocatorContainer.action_resolver_locator()

        self.action_manager = ActionManagerContainer.action_manager()
        self.turn_manager = TurnManagerContainer.turn_manager_manager()
        self.simulation_manager = None
        self.action_resolver = None
        self.grid_model = None
        self.grid = None

        # TODO: config and singleton
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((1, 1, 1, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection((10, 10, 10))
        directionalLight.setColor((.5, .5, .5, 1))
        directionalLight.setSpecularColor((1, 1, 1, 1))
        # directionalLight.showFrustum()
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

        # Important! Enable the shader generator.
        render.setShaderAuto()

        # TODO: containerize
        self.character_creator = CharacterCreator()

        # TODO: load play area based on an event (menu, etc.)
        self.request('PlayAreaLoad')

    def enterPlayAreaLoad(self, *args):
        fsm_dbg.info("[PlayAreaLoad] entering")

        # Initialize grid.
        # TODO: load from configuration source.
        GridConfig.config.override({
            'x_size': 10,
            'y_size': 10
        })

        self.grid = GridNode.grid(render)
        self.grid_model = self.grid.data_model

        self.simulation_manager = SimulationManagerContainer.simulation_manager(self.grid_model,
                                                                                self.entity_model_manager,
                                                                                self.action_manager)

        self.action_resolver = GenericResolverContainer.resolver()

        # TODO: actor setup system (character creation)
        # Initialize all players.
        for _ in range(3):
            # TODO: load from config source.
            ActorConfig.config.override({
                'model_file': 'models/player.obj'
            })

            character = self.character_creator.generate_character_via_normals(0.5)
            ActorModel.config.override({
                "character_model": character
            })

            actor = ActorNode.actor(render)
            # TODO: determine if this should be wired here "self.action_resolver_locator"
            actor_fsm = ActorFsm.actor_fsm(data_model=actor.data_model,
                                           behavior=HumanPlayerBehavior(),
                                           action_resolver=self.action_resolver)
            self.entity_component_manager[actor.id] = actor
            self.entity_fsm_manager[actor.id] = actor_fsm

            # Signal a stats change.
            RefreshStats.signal(actor.id)

            actor_fsm.request('WaitForTurn')

            loc = (random.randint(0,9), random.randint(0,9))
            self.grid_model.insert(loc, actor.id)

        # TODO: should be done elsewhere as an update step
        taskMgr.add(self.grid.update_grid, "grid_update")
        self.turn_manager.generate_turn_order()
        self.demand("TurnBegin")

    def yield_turn(self):
        # Only directly yield a turn if the state isn't already transitioning.
        if not self.isInTransition():
            self.request('NextTurn')

    def step_complete(self):
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
            self.yield_turn()

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
            taskMgr.add(self.grid.update_grid, "grid_update")
            # TODO: issue other events (perhaps depending on the effects of the actions)

    def enterTurnBegin(self):
        # Advance the turn.
        self.turn_manager.advance_turn()
        curr_actor = self.turn_manager.get_current_actor()

        # Determine if this actor can take a turn.
        # TODO: e.g. if the actor is unconscious, their

        # Generate a baseline subjective state.
        self.simulation_manager.generate_subjective_state_for(curr_actor)

        # Clear the action manager of excess actions that were not used.
        self.simulation_manager.action_manager.clear()

        # Register the actor taking the turn.
        self.simulation_manager.action_manager.register_actor(curr_actor)

        # Yield control to the FSM.
        fsm = self.entity_fsm_manager[curr_actor]
        fsm.yield_turn = self.yield_turn
        fsm.keys = self.interaction_event_manager.event_instances
        fsm.step_complete = self.step_complete
        fsm.request("TakingTurn")
        self.demand("TurnLoop")

    def enterTurnLoop(self, *args):
        fsm_dbg.info("[TurnLoop] entering")

    def filterTurnLoop(self, request, args):
        """
        Accept interactions for control from any FSM.
        :param request:
        :param args:
        :return:
        """
        fsm_dbg.info("[TurnLoop] filtering (%s)" % request)

        if request == 'NextTurn':
            return 'NextTurn'

    def exitTurnLoop(self):
        fsm_dbg.info("[TurnLoop] exiting")

    def enterNextTurn(self):
        curr_actor = self.turn_manager.get_current_actor()

        # TODO: cleanup actions submitted by the current actor.
        #   involves logging taken actions to the history.

        fsm = self.entity_fsm_manager[curr_actor]
        fsm.request("Complete")
        self.demand("TurnBegin")


gurps_main = GurpsMain()
gurps_main.run()
