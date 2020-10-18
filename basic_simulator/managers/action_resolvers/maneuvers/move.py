import random

from data_models.actions.maneuvers.move import MoveManeuver
from data_models.actions import ActionStatus
from .. import SimulationStateManager, ActionResolver, np

from utility.rolling import *


class MoveManeuverResolver(ActionResolver):
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

    # TODO: wire GenericResolver
    def __init__(self, simulation_manager: SimulationStateManager, logger, generic_resolver):
        super(MoveManeuverResolver, self).__init__(simulation_manager)

        self.logger = logger
        self.generic_resolver = generic_resolver # TODO: move to base class for ManeuverResolver or something like that

    def resolve(self, action: MoveManeuver):
        # TODO: skip resolution if the maneuver has already been resolved.
        if action.status == ActionStatus.RESOLVED:
            raise Exception("Cannot re-resolve a completed maneuver.")

        # Validate that number of hexes moved is less than the basic speed of the actor.
        # TODO

        # Verify that there is only free actions and movement actions.
        # TODO

        # Resolve each action in the order provided (skipping already completed actions).
        unresolved_actions = filter(lambda action: action.status != ActionStatus.RESOLVED, action.actions)
        # TODO: failed sub actions
        for sub_action in unresolved_actions:
            self.generic_resolver.resolve(sub_action)
            sub_action.status = ActionStatus.RESOLVED

        if action.status == ActionStatus.PARTIAL_READY:
            action.status = ActionStatus.PARTIAL_UNREADY
        elif action.status == ActionStatus.READY:
            action.status = ActionStatus.RESOLVED
