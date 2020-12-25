from typing import cast
from ..generic_trigger_manager import TriggerResolver

from data_models.entities.stats.stat_set import StatType
from data_models.triggers.status_effects.starvation import StarvationTrigger
from data_models.entities.status_effects.energy import Fed, Starving
from data_models.entities.modifiers.modifier import Modifier

from managers.status_effect_manager import StatusEffectManager
from managers.simulation_manager import SimulationStateManager


class StarvationTriggerResolver(TriggerResolver):
    """
    When a starvation trigger elapses, subtract the amount of meals per period required for the entity from
    the fed status.
    """
    def __init__(self, status_effect_manager: StatusEffectManager,
                 simulation_manager: SimulationStateManager):
        self.status_effect_manager = status_effect_manager
        self.simulation_manager = simulation_manager

    @staticmethod
    def _flat_reduction(reduction_amount):
        return lambda v: v - reduction_amount

    def resolve(self, trigger: StarvationTrigger):
        b_m = self.simulation_manager.being_model_manager.get(trigger.entity_id)

        # TODO: when adv/dis that modify how much food is needed, implement it here if food per period changes.
        #   Note: maybe increased consumption will be just more periods to trigger on.

        starving_status = cast(Starving, b_m.status_effects.get_single(Starving))
        fed_status = cast(Fed, b_m.status_effects.get_single(Fed))

        # Determine if any rest with food occurred.
        # TODO:

        # If the fed status is negative, then the actor is at a deficit.
        if fed_status.level < 0:
            starving_stacks = abs(fed_status.level)
            starving_status.level = starving_stacks
            # TODO: reset the number of fed stacks to zero (for the new period, no deficit).
            # TODO: Determine how much is lost, and 'add' that to the total of stacks (instead of setting it to that)

            # Change the existing modifier to match the number of starving stacks.
            starving_status.max_fp_reduction.modify = self._flat_reduction(starving_stacks)

            # Truncate FP above the new maximum.
            new_max = b_m.stats[StatType.FP.value]
            if b_m.stats[StatType.CURR_FP.value] > new_max:
                b_m.stats[StatType.CURR_FP.value] = new_max
                # TODO: log the loss of FP.

