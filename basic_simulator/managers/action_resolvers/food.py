import numpy as np

from . import SimulationStateManager, ConsciousnessRequiredActionResolver
from data_models.actions.action import ActionStatus
from data_models.actions.food import Harvest
from data_models.entities.status_effects.consciousness import *


class HarvestResolver(ConsciousnessRequiredActionResolver):

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(HarvestResolver, self).__init__(simulation_manager)

        self.logger = logger

    def resolve(self, action: Harvest):
        super(HarvestResolver, self).resolve(action)

        if action.status == ActionStatus.FAILED:
            return

        actor = action.actor
        actor_model = self.simulation_manager.being_model_manager.get(actor)

        # TODO: require entities in close quarters

        # TODO: locate the target and check if there are any status effects that allow harvesting
        #   auto-allowed: unconscious, dead, inanimate
        #   advantaged struggle: pinned
        #   disadvantaged struggle: none of the above statuses
        #   disallowed: non-existent
        target_model = self.simulation_manager.being_model_manager.get(action.target_id)

        # TODO: verify the weapon used deals cutting damage.

        did_succeed = False

        # Check if the harvest should auto-complete without a contest.
        if target_model.status_effects.is_affected_by(Dead) \
                or target_model.status_effects.is_affected_by(Unconscious)\
                or target_model.status_effects.is_affected_by(Inanimate):
            # Automatically allowed
            did_succeed = True
        # elif target_model.status_effects.is_affected_by(Pinned):
        #     # TODO: stub
        elif target_model.status_effects.is_affected_by(NonExistent):
            # Target is non-existent, meaning nothing is left to harvest.
            did_succeed = False
        else:
            # No special modifiers to the target. A disadvantaged harvest (target can fight back potentially)
            # TODO: attacker roll to hit (with active weapon).
            attacker_hit = True

            if attacker_hit:
                # TODO: roll defense for the target
                pass

        if did_succeed:
            # TODO: generate a meal
            pass

        action.status = ActionStatus.RESOLVED
