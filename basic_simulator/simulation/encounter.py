from data_models.state.simulation_state import ObjectiveSimulationState


class Encounter:
    """ Manages the turn order, delegates the creation of subjective game states from the
     master objective game state.
    """

    def __init__(self, simulation_state: ObjectiveSimulationState):
        self.objective_simulation_state = simulation_state

        self.active_actors = list(simulation_state.actors.keys())
        # TODO: somehow sort based on rules...
        self._active_actors_iter = iter(self.active_actors)
        self.current_actor_id = None
        self.turn_counter = 0

    def advance_turn(self):
        self.turn_counter += 1

        self.current_actor_id = next(self._active_actors_iter, None)
        if self.current_actor_id is None:
            self._active_actors_iter = iter(self.active_actors)
            self.current_actor_id = next(self._active_actors_iter, None)
