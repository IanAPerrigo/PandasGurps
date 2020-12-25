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
        # TODO: ai implementation
        # Get deltas
        # deltas = state.grid_view.get_deltas_for(self.entity_id)
        # delta_locs = None
        #
        # # If there is an empty set of deltas, then the watcher isn't currently tracked.
        # if deltas is None:
        #     # Watch the view and get all the locations in the view.
        #     state.grid_view.watch(self.entity_id)
        #     delta_locs = state.grid_view.all()
        # else:
        #     delta_locs = dict()
        #     for delta in deltas:
        #         delta_locs[delta] = state.grid_view.at_key(delta)
        #
        # # TODO: data processing, image creation and manipulation.
        #
        #
        # my_pos = state.grid_view.get_location(self.entity_id)
        # locations = state.grid_view.all()

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
