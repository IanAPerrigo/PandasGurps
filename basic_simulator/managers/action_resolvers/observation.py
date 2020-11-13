import numpy as np
from functools import reduce

from managers import SimulationStateManager
from managers.action_resolvers.generic import ActionResolver
from managers.action_resolvers.decorators import require_consciousness
from data_models.state.observation.location_observation import *
from data_models.actions.action import ActionStatus
from data_models.actions.observation import ObservationAction
from data_models.entities.stats import StatType
from utility.coordinates import cubic_manhattan
from utility.rolling import SuccessRoll, RollResult


class ObservationResolver(ActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self, simulation_manager: SimulationStateManager, roll_versus_factory, logger):
        super(ObservationResolver, self).__init__(simulation_manager)

        self.roll_versus_factory = roll_versus_factory
        self.logger = logger

    def _get_noise_for(self, subject_id, target_id, d, divisor=1.0):
        mod_value = 0
        if d > 10:
            mod_value = 10 - d
        elif d > 15:
            # TODO: this may be a hard limit in the grid model, rather than make this some arbitrary value,
            #   it will be enforced by having the grid contain only chunks within the distance needed, thereby
            #   only returning entities in the current chunks.
            return

        # TODO: clean up the modifier list to be of a real object type.
        modifiers = [lambda x: x + mod_value]
        per_roll = self.roll_versus_factory(subject_id, StatType.PER, modifiers)
        roll_result = per_roll.roll()
        noise = None
        if roll_result == RollResult.Success:
            # The basic idea is a function that rewards increased margin of success.
            # As the distance increases (between 1-10) the margin will divide the noise.
            # Best case is distance is low, margin is high, meaning there is almost entire certainty.
            # Worst case is d = 10, an margin is zero, yielding noise of 10 (pretty bad)
            # But as the distance goes over 10, -1 penalties are incurred, lowering the possible margins
            # of success. For every extra space, the bonus of the divisor will get worse.
            noise = divisor * d / (1 + per_roll.get_latest_margin())
        elif roll_result == RollResult.Critical_Success:
            # Critical success gives the exact location.
            noise = 0
        elif roll_result == RollResult.Critical_Failure:
            # Critical failure gives a very bad failure.
            noise = 10

        # TODO: roll versus concealment when it exists (contest)

        return noise, roll_result

    @require_consciousness
    def resolve(self, action: ObservationAction):
        subject_id = action.actor
        target_id = action.target_id
        existing_obsvs = self.simulation_manager.observation_manager.get_observations(subject_id)

        # Determine which type of observation is being done, Passive or Direct.
        if target_id is not None:
            # Direct observation, improve LocationObservation that already exists.
            center = self.simulation_manager.grid_model.get_loc_of_obj(subject_id)
            target_loc = self.simulation_manager.grid_model.get_loc_of_obj(target_id)
            distance = cubic_manhattan(center, target_loc)

            existing_loc_obsv = existing_obsvs.get(target_id, LocationObservation)[0]
            existing_noise = existing_loc_obsv.noise if existing_loc_obsv is not None else None

            noise, result = self._get_noise_for(subject_id, target_id, distance, 0.5)
            if noise is None:
                action.status = ActionStatus.RESOLVED
                return

            # If there was a critical failure, require an update if any observations exist.
            require_overwrite = False
            if result == RollResult.Critical_Failure:
                require_overwrite = True

            if existing_noise is not None and (require_overwrite or noise < existing_noise):
                # If an existing observation exists, and there is a reason to overwrite it.
                existing_obsvs.remove_all(target_id, LocationObservation)
            elif existing_noise is not None and noise >= existing_noise:
                # If there was an existing entry, but no reason to update it, return.
                action.status = ActionStatus.RESOLVED
                return

            loc_obsv = LocationObservation(center=center, noise=noise, subject_id=subject_id, target_id=target_id)
            self.simulation_manager.observation_manager.add_observation(loc_obsv)
        else:
            # TODO: this will only get the entities in a certain radius in the future
            #  to prevent loading more chunks than needed, along with not involving every entity on the grid.
            # TODO: ALSO NOTE: this code could be in the grid model, since other classes could benefit from the
            #   distance calculations.
            all_entities_dict = self.simulation_manager.grid_model.get_contents()
            center = np.reshape(all_entities_dict.get(subject_id), (1, 3))
            all_entities_dict.pop(subject_id)

            all_entities = list(all_entities_dict.items())
            all_locs = all_entities_dict.values()

            # Build the entity location matrix out.
            entity_location_matrix = reduce(lambda l0, l1: np.concatenate([l0, l1]), all_locs)

            num_entities = len(all_entities)
            entity_location_matrix = np.reshape(entity_location_matrix, (num_entities, 3))
            center_matrix = np.repeat(center, num_entities, axis=0)
            distances = cubic_manhattan(center_matrix, entity_location_matrix, axis=1)
            entity_distances = zip(all_entities, distances)

            for (tid, loc), d in entity_distances:
                noise, roll_result = self._get_noise_for(subject_id, tid, d)
                if noise is None:
                    continue

                # If an observation already exists, update it.
                if tid in existing_obsvs.keys():
                    existing_obsvs.remove_all(tid, LocationObservation)
                loc_obsv = LocationObservation(center=loc, noise=noise, subject_id=subject_id, target_id=tid)
                self.simulation_manager.observation_manager.add_observation(loc_obsv)

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
