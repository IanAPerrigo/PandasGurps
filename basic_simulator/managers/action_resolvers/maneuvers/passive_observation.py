
from managers.simulation_manager import SimulationStateManager
from managers.action_resolvers.generic import ActionResolver
from managers.action_resolvers.decorators import require_consciousness
from data_models.actions.maneuvers.passive_observation import PassiveObservationManeuver
from data_models.actions import ActionStatus


class PassiveObservationManeuverResolver(ActionResolver):
    """
    TODO:
    """

    def __init__(self, simulation_manager: SimulationStateManager, logger, generic_resolver):
        super(PassiveObservationManeuverResolver, self).__init__(simulation_manager)

        self.logger = logger
        self.generic_resolver = generic_resolver # TODO: move to base class for ManeuverResolver or something like that

    @require_consciousness
    def resolve(self, action: PassiveObservationManeuver):
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
                action.reason = sub_action.reason
                break

        if action.status == ActionStatus.PARTIAL_READY:
            action.status = ActionStatus.PARTIAL_UNREADY
        elif action.status == ActionStatus.READY:
            action.status = ActionStatus.RESOLVED
