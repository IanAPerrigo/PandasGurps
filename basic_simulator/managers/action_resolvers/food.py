import numpy as np

from .generic import ActionResolver
from .decorators import require_proximity, require_target_type, require_consciousness, required_target

from managers.simulation_manager import SimulationStateManager

from data_models.actions.action import ActionStatus
from data_models.actions.food import HarvestAction, EatAction
from data_models.entities.being import Being
from data_models.entities.status_effects.energy import *
from data_models.entities.status_effects.consciousness import *
from data_models.entities.food.food import Food

from utility.rolling import *
from events import Event
from events.component.actors import RefreshStats


class EatResolver(ActionResolver):
    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(EatResolver, self).__init__(simulation_manager)

        self.logger = logger

    @require_consciousness
    @required_target
    @require_target_type(target_type=Food)
    # TODO: require target status (edible) instead of hard typing to Food
    @require_proximity(exact=0)
    def resolve(self, action: EatAction):
        actor = action.actor
        actor_model = self.simulation_manager.being_model_manager.get(actor)

        # Delete the food
        food_model = self.simulation_manager.entity_model_manager.get(action.target_id)
        sustenance_value = food_model.sustenance_value
        self.simulation_manager.entity_component_manager.pop(action.target_id)

        # Add or update the status effect for 'Fed'.
        fed_statuses = actor_model.status_effects.get(Fed)
        if len(fed_statuses) != 1:
            raise Exception("Every being should have exactly one fed status.")

        # Add the sustenance value to the level of fed (amount of energy in the meal)
        fed_statuses[0].level += sustenance_value
        action.status = ActionStatus.RESOLVED


class HarvestResolver(ActionResolver):

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(HarvestResolver, self).__init__(simulation_manager)

        self.logger = logger

    @require_consciousness
    @required_target(explicit=False, selection_type=Being)
    @require_proximity(exact=0)
    def resolve(self, action: HarvestAction):
        actor = action.actor
        actor_model = self.simulation_manager.being_model_manager.get(actor)

        # Require entities to be in close quarters.
        sub_loc = self.simulation_manager.grid_model.get_loc_of_obj(actor)

        # Check if there are any status effects that allow harvesting
        #   auto-allowed: unconscious, dead, inanimate
        #   advantaged struggle: pinned
        #   disadvantaged struggle: none of the above statuses
        #   disallowed: non-existent
        target_model = self.simulation_manager.being_model_manager.get(action.target_id)

        # TODO: verify the weapon used deals cutting damage.

        did_succeed = False

        # TODO: STUB: ignore existing tooling and use hardcoded values
        attacker_hit_score = 10
        defender_defense_score = 8

        # Check if the harvest should auto-complete without a contest.
        if target_model.status_effects.is_affected_by(Dead) \
                or target_model.status_effects.is_affected_by(Unconscious)\
                or target_model.status_effects.is_affected_by(Inanimate):
            # Automatically allowed
            did_succeed = True
        # elif target_model.status_effects.is_affected_by(Pinned):
        #     # TODO: stub
        else:
            # No special modifiers to the target. A disadvantaged harvest (target can fight back potentially)
            hit_roll = SuccessRoll(attacker_hit_score)
            hit_result = hit_roll.roll()
            self.logger.info("Attacker rolling to hit (3d6): [%s] | %d" % (hit_result.value, hit_roll.last_result))

            if hit_result == RollResult.Failure or hit_result == RollResult.Critical_Failure:
                did_succeed = False
            else:
                defense_roll = SuccessRoll(defender_defense_score)
                defense_result = defense_roll.roll()

                self.logger.info(
                    "Defender rolling to defend (3d6): [%s] | %d" % (defense_result.value, defense_roll.last_result))
                if defense_result == RollResult.Critical_Success or defense_result == RollResult.Success:
                    # Attack misses.
                    did_succeed = False
                else:
                    # Attack hits
                    did_succeed = True

        if target_model.status_effects.is_affected_by(NonExistent):
            # Target is non-existent, meaning nothing is left to harvest.
            did_succeed = False

        if did_succeed:
            # Harvest connects, calculate damage and generate a meal.
            attacker_damage_descriptor = Roll(1, 6) # TODO: this will be derived from the active weapon / action descriptor.
            attack_damage = attacker_damage_descriptor.roll()

            self.logger.info(
                "Attacker dealing damage (%s): %d" % (attacker_damage_descriptor.get_description(), attack_damage))

            target_model.base_stats['CURR_HP'] -= attack_damage  # TODO: brittle, replace with StatType ref

            # Generate a meal, and add it to the world.
            food = BasicMealComponentContainer.component()
            # TODO: generate sustenance some how based on the efficiency of the harvest, quality of the target, etc.
            self.simulation_manager.entity_component_manager[food.data_model.entity_id] = food
            self.simulation_manager.grid_model.insert(sub_loc, food.data_model.entity_id)

            # TODO: move this to a different location (a place that manages what is displayed at what time)
            food.load()

            Event.signal("actor_damaged", target_model.entity_id, attack_damage)
            RefreshStats.signal(target_model.entity_id)

            # TODO: make this event lighter weight, then have it register the expensive call to be called at a better
            #  place (turn_management loop)
            Event.signal("notify_grid_update")

        action.status = ActionStatus.RESOLVED
