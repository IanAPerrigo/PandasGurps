from typing import List
from ..generic_trigger_manager import TriggerResolver

# TODO: these will be injected via the order dictionary
from .dehydration.daily_dehydration_trigger_resolver import DailyDehydrationTrigger
from .dehydration.eight_hour_dehydration_trigger_resolver import EightHourDehydrationTrigger


class StatusEffectTriggerResolver(TriggerResolver):
    """
    Resolve a list of StatusEffect triggers, applying a resolution order (for repeatability).
    """
    def __init__(self, resolvers_for_type):
        self._resolvers = resolvers_for_type

        # TODO: derive from config
        self.default_order = 100

        # TODO: inject this
        self._resolver_order = {
            EightHourDehydrationTrigger: 10,
            DailyDehydrationTrigger: 20,
        }

    # TODO: list of triggers
    def resolve(self, triggers: List[object]):
        ordered_triggers = sorted(map(
            lambda t: (t, self._resolver_order.get(type(t), self.default_order)), triggers), key=lambda t: t[1])
        triggers = map(lambda t: t[0], ordered_triggers)

        for trigger in triggers:
            resolver_provider = self._resolvers(type(trigger))
            trigger_resolver = resolver_provider()
            trigger_resolver.resolve(trigger)
