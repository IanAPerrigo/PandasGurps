from data_models.grid import GridModel, GridView
from data_models.grid.ephemeral_grid import SubjectiveGridView


class SimulationState:
    def __init__(self, grid_view: GridView, actors: set):
        """
        Inputs to this class are game objects.
        :param grid:
        """
        self.grid_view = grid_view
        self.actors = actors if actors is not None else set()
        # TODO: a map of entities by id


class ObjectiveSimulationState(SimulationState):
    def __init__(self, grid_view: GridView, actors: set):
        """
        Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        super(ObjectiveSimulationState, self).__init__(grid_view, actors)
        # TODO: a map of entities by id (entity_model_map)


class SubjectiveSimulationState(SimulationState):
    def __init__(self, grid_view: GridView, actors: set):
        """
        Inputs to this class are game objects. Data objects are derived from these
        game objects to create subjective state.

        :param grid:
        """
        super(SubjectiveSimulationState, self).__init__(grid_view, actors)
        # TODO: a map of entities by id (filtered by observation, with each model masked by a view)
