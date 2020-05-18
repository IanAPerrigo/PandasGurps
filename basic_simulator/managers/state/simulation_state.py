

class ObjectiveSimulationState:
    def __init__(self, grid, actors=None):
        """ Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        self.grid = grid
        self.actors = actors if actors is not None else []


class SubjectiveSimulationState:
    def __init__(self, grid, actors=None):
        """ Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        self.grid = grid
        self.actors = actors if actors is not None else []
