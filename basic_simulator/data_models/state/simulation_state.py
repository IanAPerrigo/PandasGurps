
class SimulationState:
    def __init__(self, grid, actors=None):
        """
        Inputs to this class are game objects.
        :param grid:
        """
        self.grid = grid
        self.actors = actors if actors is not None else []


class ObjectiveSimulationState(SimulationState):
    def __init__(self, grid, actors=None):
        """
        Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        super(ObjectiveSimulationState, self).__init__(grid, actors)


class SubjectiveSimulationState(SimulationState):
    def __init__(self, grid, actors=None):
        """
        Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        super(SubjectiveSimulationState, self).__init__(grid, actors)
