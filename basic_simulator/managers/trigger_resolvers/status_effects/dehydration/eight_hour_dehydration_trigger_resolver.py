from typing import cast
from managers.trigger_resolvers.generic_trigger_manager import TriggerResolver

from data_models.entities.stats.stat_set import StatType
from data_models.triggers.status_effects.energy import EightHourDehydrationTrigger
from data_models.entities.status_effects.energy import Hydrated, Dehydrated, Resting
from data_models.entities.modifiers.modifier import Modifier

from managers.status_effect_manager import StatusEffectManager
from managers.simulation_manager import SimulationStateManager


class EightHourDehydrationTriggerResolver(TriggerResolver):
    def __init__(self, simulation_manager: SimulationStateManager,
                 logger):
        self.simulation_manager = simulation_manager
        self.logger = logger

        # TODO: constant configuration (for tuneable game parameters)
        self.REQUIRED_REST_PERCENTAGE = 0.01

    @staticmethod
    def _flat_reduction(reduction_amount):
        return lambda v: v - reduction_amount

    def resolve(self, trigger: EightHourDehydrationTrigger):
        b_m = self.simulation_manager.being_model_manager.get(trigger.entity_id)

        # TODO: when adv/dis that modify how much water is needed, implement it here if water per period changes.
        #   Note: maybe increased consumption will be just more periods to trigger on.

        dehydrated_status = cast(Dehydrated, b_m.status_effects.get_single(Dehydrated))
        hydrated_status = cast(Hydrated, b_m.status_effects.get_single(Hydrated))

        # TODO: configurable number based on environment.
        required_drinks_per_day = 8
        required_drinks_per_period = required_drinks_per_day / 3

        periods_elapsed = trigger.tick_count % 3
        periods_elapsed = 3 if periods_elapsed == 0 else periods_elapsed
        drinks_required = periods_elapsed * required_drinks_per_period

        # If the hydrated status is negative, then the actor is at a deficit for the period.
        if hydrated_status.level < drinks_required:
            dehydrated_status.level += 1

            # Change the existing modifier to match the number of dehydration stacks.
            dehydrated_status.max_fp_reduction.modify = self._flat_reduction(dehydrated_status.level)

            # Truncate FP above the new maximum
            # (accessing the FP parameter should be updated by the change in modifier).
            new_max = b_m.stats[StatType.FP]
            if b_m.stats[StatType.CURR_FP] > new_max:
                b_m.base_stats[StatType.CURR_FP] = new_max
                # TODO: loss of FP event.
