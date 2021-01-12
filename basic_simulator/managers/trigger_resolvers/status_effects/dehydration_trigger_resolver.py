from typing import cast
from ..generic_trigger_manager import TriggerResolver

from data_models.entities.stats.stat_set import StatType
from data_models.triggers.status_effects.energy import DehydrationTrigger
from data_models.entities.status_effects.energy import Hydrated, Dehydrated, Resting
from data_models.entities.modifiers.modifier import Modifier

from managers.status_effect_manager import StatusEffectManager
from managers.simulation_manager import SimulationStateManager


class DehydrationTriggerResolver(TriggerResolver):
    """
    When a dehydration trigger elapses, subtract the amount of drinks per period required for the entity from
    the hydrated status.
    """
    def __init__(self, simulation_manager: SimulationStateManager,
                 logger):
        self.simulation_manager = simulation_manager
        self.logger = logger

        # TODO: constant configuration (for tuneable game parameters)
        self.REQUIRED_REST_PERCENTAGE = 0.01

    @staticmethod
    def _flat_reduction(reduction_amount):
        return lambda v: v - reduction_amount

    def resolve(self, trigger: DehydrationTrigger):
        b_m = self.simulation_manager.being_model_manager.get(trigger.entity_id)

        # TODO: when adv/dis that modify how much water is needed, implement it here if water per period changes.
        #   Note: maybe increased consumption will be just more periods to trigger on.

        dehydrated_status = cast(Dehydrated, b_m.status_effects.get_single(Dehydrated))
        hydrated_status = cast(Hydrated, b_m.status_effects.get_single(Hydrated))

        # TODO: configurable number based on environment.
        required_drinks_per_day = 8

        # If the hydrated status is negative, then the actor is at a deficit.
        if hydrated_status.level < required_drinks_per_day:
            dehydration_stacks = int(abs(required_drinks_per_day - hydrated_status.level))
            dehydrated_status.level += dehydration_stacks

            fp_reduction = dehydrated_status.level
            hp_reduction = 0

            if dehydration_stacks >= required_drinks_per_day / 2:
                # Lose 1 FP and 1 HP due to severe dehydration.
                fp_reduction += 1
                hp_reduction += 1

            # Change the existing modifier to match the number of starving stacks.
            dehydrated_status.max_fp_reduction.modify = self._flat_reduction(fp_reduction)
            dehydrated_status.max_hp_reduction.modify = self._flat_reduction(hp_reduction)

            # Truncate FP above the new maximum
            # (accessing the FP parameter should be updated by the change in modifier).
            new_max = b_m.stats[StatType.FP]
            if b_m.stats[StatType.CURR_FP] > new_max:
                b_m.base_stats[StatType.CURR_FP] = new_max
                # TODO: loss of FP event.

            # Truncate HP above the new maximum
            # (accessing the HP parameter should be updated by the change in modifier).
            new_max = b_m.stats[StatType.HP]
            if b_m.stats[StatType.CURR_HP] > new_max:
                b_m.base_stats[StatType.CURR_HP] = new_max
                # TODO: loss of HP event.
        else:
            # If the actor has rested and has a surplus of 3 meals, remove a starvation stack.
            fed_stacks = fed_status.level
            rest_status = cast(Resting, b_m.status_effects.get_single(Resting))

            # TODO: increases or decreases based on character properties (slow eater, etc)
            modified_required_rest = self.REQUIRED_REST_PERCENTAGE

            num_restful_meals_required = len(rest_status.increased_on_tick.intersection(fed_status.increased_on_tick)) / 3

            if num_restful_meals_required >= 1:
                starvation_stacks_removed = int(num_restful_meals_required)
                starving_status.level -= starvation_stacks_removed

        # New period, remove existing levels.
        hydrated_status.level = 0

