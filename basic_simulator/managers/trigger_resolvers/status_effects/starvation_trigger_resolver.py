from typing import cast
from ..generic_trigger_manager import TriggerResolver

from data_models.entities.stats.stat_set import StatType
from data_models.triggers.status_effects.energy import StarvationTrigger
from data_models.entities.status_effects.energy import Fed, Starving, Resting
from data_models.entities.modifiers.modifier import Modifier

from managers.status_effect_manager import StatusEffectManager
from managers.simulation_manager import SimulationStateManager


class StarvationTriggerResolver(TriggerResolver):
    def __init__(self, simulation_manager: SimulationStateManager,
                 logger):
        self.simulation_manager = simulation_manager
        self.logger = logger

        # TODO: constant configuration (for tuneable game parameters)
        self.REQUIRED_REST_PERCENTAGE = 0.01

    @staticmethod
    def _flat_reduction(reduction_amount):
        return lambda v: v - reduction_amount

    def resolve(self, trigger: StarvationTrigger):
        b_m = self.simulation_manager.being_model_manager.get(trigger.entity_id)

        # TODO: when adv/dis that modify how much food is needed, implement it here if food per period changes.
        #   Note: maybe increased consumption will be just more periods to trigger on.

        starving_status = cast(Starving, b_m.status_effects.get_single(Starving))
        fed_status = cast(Fed, b_m.status_effects.get_single(Fed))

        # TODO: configurable based on adv/dis
        required_meals_per_day = 3

        # If the fed status is negative, then the actor is at a deficit.
        if fed_status.level < required_meals_per_day:
            starving_stacks = int(abs(required_meals_per_day - fed_status.level))
            starving_status.level += starving_stacks

            # Change the existing modifier to match the number of starving stacks.
            starving_status.max_fp_reduction.modify = self._flat_reduction(starving_status.level)

            # Truncate FP above the new maximum.
            new_max = b_m.stats[StatType.FP]
            if b_m.stats[StatType.CURR_FP] > new_max:
                b_m.base_stats[StatType.CURR_FP] = new_max
                # TODO: trigger event for loss of FP
        else:
            # If the actor has rested and has a surplus of 3 meals, remove a starvation stack.
            fed_stacks = fed_status.level
            rest_status = cast(Resting, b_m.status_effects.get_single(Resting))

            # TODO: increases or decreases based on character properties (slow eater, etc)
            modified_required_rest = self.REQUIRED_REST_PERCENTAGE

            # Determine if any rest with food occurred.
            # TODO: maybe separate these, ample rest + the right amount of food, not at the same time.
            num_restful_meals_required = len(rest_status.increased_on_tick.intersection(fed_status.increased_on_tick))

            if num_restful_meals_required >= required_meals_per_day:
                starvation_stacks_removed = int(num_restful_meals_required)
                starving_status.level -= starvation_stacks_removed
                starving_status.max_fp_reduction.modify = self._flat_reduction(starving_status.level)

        # New period, remove existing levels.
        fed_status.level = 0

