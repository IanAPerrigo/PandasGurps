from uuid import UUID

from managers.entity_manager import EntityModelManager, BeingModelManager, EntityComponentManager
from managers.action_manager import ActionManager
from managers.observation_manager import ObservationManager
from data_models.grid import GridModel
from data_models.state.simulation_state import SubjectiveSimulationState
from data_models.state.observation.location_observation import LocationObservation
from utility.coordinates import cubic_manhattan, cube_to_offset


class SimulationStateManager:
    def __init__(self, grid_model: GridModel,
                 entity_component_manager: EntityComponentManager,
                 action_manager: ActionManager,
                 observation_manager: ObservationManager,
                 grid_factory
                 ):
        self.entity_model_manager = entity_component_manager.entity_model_manager
        self.being_model_manager = entity_component_manager.being_model_manager
        self.entity_fsm_manager = entity_component_manager.entity_fsm_manager
        self.entity_component_manager = entity_component_manager
        self.observation_manager = observation_manager
        self.grid_model = grid_model
        self._grid_factory = grid_factory
        self.action_manager = action_manager
        self.entity_states = {}

    def amend_subjective_state(self, entity_id):
        """
        Given a new observation, amend the existing state to include the new information.
        :param entity_id:
        :param observation:
        :return:
        """
        pass

    def _generate_new_state_for_entity(self, entity_id):
        subjective_grid = self._grid_factory()
        actors = {}
        self.entity_states[entity_id] = SubjectiveSimulationState(subjective_grid, actors)

    def generate_subjective_state_for(self, entity_id):
        if entity_id not in self.entity_model_manager:
            raise Exception("Entity not currently tracked in state.")

        observation_set = self.observation_manager.get_observations(entity_id)
        if observation_set is None:
            self.observation_manager.track_observations(entity_id)
            observation_set = self.observation_manager.get_observations(entity_id)

        if entity_id not in self.entity_states:
            self._generate_new_state_for_entity(entity_id)

        subjective_state = self.entity_states[entity_id]

        # Get a list of the relevant entities that have been observed.
        observed_entities = observation_set.keys()

        for entity in observed_entities:
            location_observations = observation_set.get(entity, LocationObservation)
            if len(location_observations) > 1:
                raise Exception("Only zero or one location observation can exist at a time.")

            # Collapse the observation and add the entity to the subjective grid.
            if len(location_observations) == 1:
                loc_ob = location_observations[0]
                loc_ob.collapse_observation()
                entity_loc = loc_ob.collapsed_value
                entity_loc = cube_to_offset(entity_loc)

                subjective_state.grid.insert(entity_loc, loc_ob.target_id)


            # TODO: further resolve each entity model, in this case the visualObservations would be processed
            #   to render each model as they are described.

