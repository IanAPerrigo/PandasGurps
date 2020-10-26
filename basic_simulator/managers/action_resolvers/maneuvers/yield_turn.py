from data_models.actions.maneuvers.yield_turn import YieldTurnManeuver
from data_models.actions import ActionStatus
from .. import SimulationStateManager, ActionResolver


class YieldTurnManeuverResolver(ActionResolver):
    """
    Yield the turn to
    """

    def __init__(self, simulation_manager: SimulationStateManager, logger, generic_resolver):
        super(YieldTurnManeuverResolver, self).__init__(simulation_manager)

        self.logger = logger
        self.generic_resolver = generic_resolver # TODO: move to base class for ManeuverResolver or something like that

    def resolve(self, action: YieldTurnManeuver):
        if action.status == ActionStatus.FAILED:
            return

        if action.status == ActionStatus.RESOLVED:
            raise Exception("Cannot re-resolve a completed maneuver.")

        action.status = ActionStatus.RESOLVED
