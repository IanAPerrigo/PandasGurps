import numpy as np

from managers import SimulationStateManager
from managers.action_resolvers.generic import ActionResolver
from managers.action_resolvers.decorators import require_consciousness
from data_models.actions.action import ActionStatus
from data_models.actions.observation import ObservationAction
from data_models.entities.stats import StatType
from utility.coordinates import cubic_manhattan


class ObservationResolver(ActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(ObservationResolver, self).__init__(simulation_manager)

        self.logger = logger

    @require_consciousness
    def resolve(self, action: ObservationAction):
        actor = action.actor

        # Determine which type of observation is being done, Passive or Direct.
        if action.target_id is not None:
            # TODO: Direct observation, improve LocationObservation that already exists.
            pass
        else:
            # TODO: passive observation, give information about every entity within range.
            #   after that range, modifiers of -1 per yard are incurred.

            # TODO: this will only get the entities in a certain radius in the future
            #  to prevent loading more chunks than needed, along with not involving every entity on the grid.
            # TODO: ALSO NOTE: this code could be in the grid model, since other classes could benefit from the
            #   distance calculations.
            all_entities = self.simulation_manager.grid_model.get_contents()
            center = np.reshape(all_entities.get(actor), (1, 3))
            all_entities.pop(actor)
            all_entities = list(all_entities.items())
            entity_location_matrix = None

            # Build the entity location matrix out.
            for _, loc in all_entities:
                if entity_location_matrix is None:
                    entity_location_matrix = loc
                else:
                    entity_location_matrix = np.concatenate([entity_location_matrix, loc])

            num_entities = len(all_entities)
            entity_location_matrix = np.reshape(entity_location_matrix, (num_entities, 3))
            center_matrix = np.repeat(center, num_entities, axis=0)
            distances = cubic_manhattan(center_matrix, entity_location_matrix, axis=1)
            entity_distances = zip(all_entities, distances)
            for (eid, loc), d in entity_distances:
                # TODO: roll and determine if the entities can be seen by the subject.
                pass


        # Validate that number of hexes moved is less than the basic speed of the actor.
        # actor_model = self.simulation_manager.being_model_manager.get(actor)
        # curr_bm = actor_model.stats[StatType.CURR_BM]
        # # TODO: replace hardcoded hex movement cost.
        # hex_cost = 1
        # if curr_bm - hex_cost < 0:
        #     action.status = ActionStatus.FAILED
        #     return
        #
        # actor_model.base_stats[StatType.CURR_BM] -= hex_cost

        # TODO: manage movement challenges (terrain difficulty, walls, etc)
        # TODO: in order for this to work, the move resolver must know how much speed it remaining for a given turn.
        #   this also go for other actions, they must know the game state so they can determine whether or not to modify
        #   the game state.

        #vec = action.get_vector()
        #self.simulation_manager.grid_model.move(action.actor, np.array(vec))
        action.status = ActionStatus.RESOLVED
