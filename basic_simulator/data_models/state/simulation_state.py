from data_models.grid import GridModel


class SimulationState:
    def __init__(self, grid: GridModel, actors: dict):
        """
        Inputs to this class are game objects.
        :param grid:
        """
        self.grid = grid
        self.actors = actors if actors is not None else {}
        # TODO: a map of entities by id


class ObjectiveSimulationState(SimulationState):
    def __init__(self, grid: GridModel, actors: dict):
        """
        Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        super(ObjectiveSimulationState, self).__init__(grid, actors)
        # TODO: a map of entities by id (entity_model_map)


class SubjectiveSimulationState(SimulationState):
    def __init__(self, grid: GridModel, actors: dict):
        """
        Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        super(SubjectiveSimulationState, self).__init__(grid, actors)
        # TODO: a map of entities by id (filtered by observation, with each model masked by a view)
