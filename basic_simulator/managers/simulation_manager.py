from typing import Dict
import uuid

from data_models.actors import ActorModel
from data_models.grid import GridModel
from containers import grid
from managers.state.simulation_state import ObjectiveSimulationState, SubjectiveSimulationState
from managers.entity_manager import EntityModelManager


class SimulationStateManager:

    # TODO: inject required managers to generate new grids, or modify other game state
    # Injected data should be only models, no game components
    def __init__(self, grid_model: GridModel, entity_model_manager: EntityModelManager):
        self.entity_model_manager = entity_model_manager
        self.grid_model = grid_model
        self.entity_states = {}

    def generate_subjective_state_for(self, entity_id):
        if entity_id not in self.entity_model_manager:
            raise Exception("Entity not currently tracked in state.")

        # TODO: Generate the grid based on observations
        # Make a view of the grid
        objective_contents = self.grid_model.get_contents()

        subjective_grid = grid.GridModel.grid_model(x_size=self.grid_model.x_size, y_size=self.grid_model.y_size)
        subject_location = objective_contents.get(entity_id)

        # TODO: pass to resolvers to operate on the state instead of static modifications.
        SIGHT_RANGE = 10
        observed_entities = {}
        for observed_entity_id, location in objective_contents.items():
            if abs(location[0] - subject_location[0]) + abs(location[1] - subject_location[1]) <= SIGHT_RANGE:
                observed_entities[observed_entity_id] = location

        observed_actors = observed_entities.keys()

        for observed_entity_id, location in observed_entities.items():
            subjective_grid.insert(location, observed_entity_id)

        # TODO: further resolve each entity model 

        self.entity_states[entity_id] = SubjectiveSimulationState(subjective_grid, observed_actors)

