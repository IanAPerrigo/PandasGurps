from data_models.actions.maneuvers import Maneuver
from data_models.state.simulation_state import SimulationState


class Behavior:
    def act(self, state: SimulationState) -> Maneuver:
        raise NotImplementedError()
