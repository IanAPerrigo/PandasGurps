from data_models.actions import MovementType, MovementAction, MeleeAttack, HarvestAction, EatAction
from data_models.actions.maneuvers import MoveManeuver, MoveAttackManeuver, YieldTurnManeuver
from data_models.actions import ActionStatus
from data_models.actions.observation import ObservationAction
from data_models.state.simulation_state import SimulationState
from behaviors import Behavior


class AiBehavior(Behavior):
    """
    TODO: include movement interface as dep
    """
    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.keys = None # TODO: should be a dep

        self.done = True

    def act(self, state: SimulationState):
        my_pos = state.grid_view.get_location(self.entity_id)
        locations = state.grid_view.all()

        if self.done:
            maneuver = YieldTurnManeuver()
            maneuver.status = ActionStatus.READY
            return maneuver
        else:
            action = ObservationAction()
            maneuver = MoveManeuver([action])
            maneuver.status = ActionStatus.READY
            self.done = True
            return maneuver
