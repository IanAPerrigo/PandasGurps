from data_models.actions.maneuvers.move import MoveManeuver
from data_models.actions import ActionStatus
from .. import SimulationStateManager, ConsciousnessRequiredActionResolver


class MoveManeuverResolver(ConsciousnessRequiredActionResolver):
    """
    p. 364
    Move, but take no other action
    except those specified under Free
    Actions (p. 363). You may move any
    number of yards up to your full Move
    score. Most other maneuvers allow at
    least some movement on your turn;
    take this maneuver if all you want to
    do is move.
    """

    def __init__(self, simulation_manager: SimulationStateManager, logger, generic_resolver):
        super(MoveManeuverResolver, self).__init__(simulation_manager)

        self.logger = logger
        self.generic_resolver = generic_resolver # TODO: move to base class for ManeuverResolver or something like that

    def resolve(self, action: MoveManeuver):
        super(MoveManeuverResolver, self).resolve(action)
        if action.status == ActionStatus.FAILED:
            return

        if action.status == ActionStatus.RESOLVED:
            raise Exception("Cannot re-resolve a completed maneuver.")

        # Verify that there is only free actions and movement actions.
        # TODO

        # Resolve each action in the order provided (skipping already completed actions).
        unresolved_actions = filter(lambda action: action.status != ActionStatus.RESOLVED, action.actions)
        for sub_action in unresolved_actions:
            self.generic_resolver.resolve(sub_action)
            if sub_action.status == ActionStatus.FAILED:
                action.status = ActionStatus.FAILED
                break

        # TODO: though process
        #   Failed tasks should halt the progress of resolution, because other actions will be dependent on actions in the sequence.
        #   Every task after a failed task should remain as its previous state (assumed to be "ready")
        #   It will be the job of the GUI (or in the case of AI, automatically) to represent that an action failed,
        #   and to provide a way to clear all tasks out after the failure.

        if action.status == ActionStatus.PARTIAL_READY:
            action.status = ActionStatus.PARTIAL_UNREADY
        elif action.status == ActionStatus.READY:
            action.status = ActionStatus.RESOLVED
