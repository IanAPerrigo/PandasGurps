from uuid import UUID

from managers.entity_manager import EntityModelManager, BeingModelManager, EntityComponentManager
from managers.action_manager import ActionManager
from managers.observation_manager import ObservationManager
from data_models.grid import GridModel
from data_models.grid.ephemeral_grid import SubjectiveGridView, SubjectiveGridModel
from data_models.state.simulation_state import SubjectiveSimulationState
from data_models.state.observation.location_observation import LocationObservation


class ActorState:
    def __init__(self, subjective_grid: SubjectiveGridModel, subjective_grid_view: SubjectiveGridView,
                 subjective_simulation_state: SubjectiveSimulationState):
        self.subjective_grid = subjective_grid
        self.subjective_grid_view = subjective_grid_view
        self.subjective_simulation_state = subjective_simulation_state
        self.seq_num = 0


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
        self._subjective_grid_factory = grid_factory
        self.action_manager = action_manager
        self.entity_states = {}

    def _generate_new_state_for_entity(self, entity_id):
        # Create an ephemeral grid
        subjective_grid = self._subjective_grid_factory(source_grid=self.grid_model)
        subjective_grid_view = SubjectiveGridView(source_grid=subjective_grid)
        actors = set()
        subjective_simulation_state = SubjectiveSimulationState(subjective_grid_view, actors)
        actor_state = ActorState(subjective_grid, subjective_grid_view, subjective_simulation_state)

        self.entity_states[entity_id] = actor_state

    def generate_subjective_state_for(self, entity_id):
        if entity_id not in self.entity_model_manager:
            raise Exception("Entity not currently tracked in state.")

        observation_set = self.observation_manager.get_observations(entity_id)
        if observation_set is None:
            self.observation_manager.track_observations(entity_id)
            observation_set = self.observation_manager.get_observations(entity_id)

        if entity_id not in self.entity_states:
            self._generate_new_state_for_entity(entity_id)

        actor_state = self.entity_states[entity_id]

        # Grant knowledge of the actor's location.
        actor_pos = self.grid_model.get_location(entity_id)
        actor_state.subjective_grid.subject_location = actor_pos
        subj_actor_pos = actor_state.subjective_grid.get_location(entity_id)
        # If the actor isn't currently in the state, just insert it. Otherwise, move the entity.
        if subj_actor_pos is None:
            actor_state.subjective_grid.insert(actor_pos, entity_id)
        elif (subj_actor_pos != actor_pos).any():
            m_vec = actor_pos - subj_actor_pos
            actor_state.subjective_grid.move(entity_id, m_vec)

        # Get a list of the relevant entities that have been observed.
        observed_entities = observation_set.keys()

        for entity in observed_entities:
            location_observations = observation_set.get(entity, LocationObservation)
            if len(location_observations) > 1:
                raise Exception("Only zero or one location observation can exist at a time.")

            # Collapse the observation and add the entity to the subjective grid.
            if len(location_observations) == 1:
                loc_ob = location_observations[0]
                collapsed = loc_ob.collapse_observation()

                if not collapsed:
                    continue

                entity_loc = loc_ob.collapsed_value
                subj_entity_pos = actor_state.subjective_grid.get_location(loc_ob.target_id)

                # If the entity isn't currently in the state, just insert it. Otherwise, move the entity.
                if subj_entity_pos is None:
                    actor_state.subjective_grid.insert(entity_loc, loc_ob.target_id)
                elif (subj_entity_pos != entity_loc).any():
                    m_vec = entity_loc - subj_entity_pos
                    actor_state.subjective_grid.move(loc_ob.target_id, m_vec)

            # TODO: get entity observation.
            actor_state.subjective_simulation_state.actors.add(entity)

            # TODO: further resolve each entity model, in this case the visualObservations would be processed
            #   to render each model as they are described.

        actor_state.subjective_simulation_state.grid_view.populate()

