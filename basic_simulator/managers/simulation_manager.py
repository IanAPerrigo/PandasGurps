from data_models.grid import GridModel
from data_models.state.simulation_state import SubjectiveSimulationState
from managers.entity_manager import EntityModelManager, BeingModelManager, EntityComponentManager
from managers.action_manager import ActionManager
from utility.coordinates import cubic_manhattan


class SimulationStateManager:
    def __init__(self, grid_model: GridModel,
                 entity_component_manager: EntityComponentManager,
                 action_manager: ActionManager,
                 grid_factory
                 ):
        self.entity_model_manager = entity_component_manager.entity_model_manager
        self.being_model_manager = entity_component_manager.being_model_manager
        self.entity_fsm_manager = entity_component_manager.entity_fsm_manager
        self.entity_component_manager = entity_component_manager
        self.grid_model = grid_model
        self._grid_factory = grid_factory
        self.action_manager = action_manager
        self.entity_states = {}

    def amend_subjective_state(self, entity_id, observation=None):
        """
        Given a new observation, amend the existing state to include the new information.
        :param entity_id:
        :param observation:
        :return:
        """
        pass

    # TODO: given a list of observations, generate what the actor sees.
    def generate_subjective_state_for(self, entity_id, observations=None):
        if entity_id not in self.entity_model_manager:
            raise Exception("Entity not currently tracked in state.")

        # TODO: Generate the grid based on observations
        # Make a view of the grid
        objective_contents = self.grid_model.get_contents()

        subjective_grid = self._grid_factory()
        subject_location = objective_contents.get(entity_id)

        # TODO: pass to resolvers to operate on the state instead of static modifications.
        SIGHT_RANGE = 10
        observed_entities = {}
        for observed_entity_id, location in objective_contents.items():
            if cubic_manhattan(location, subject_location) <= SIGHT_RANGE:
                observed_entities[observed_entity_id] = location

        observed_actors = observed_entities.keys()

        for observed_entity_id, location in observed_entities.items():
            subjective_grid.insert(location, observed_entity_id)

        # TODO: further resolve each entity model 

        self.entity_states[entity_id] = SubjectiveSimulationState(subjective_grid, observed_actors)

