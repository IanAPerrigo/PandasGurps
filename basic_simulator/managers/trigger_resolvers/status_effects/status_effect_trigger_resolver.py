from typing import List
from ..generic_trigger_manager import TriggerResolver


class StatusEffectTriggerResolver(TriggerResolver):
    """
    Resolve a list of StatusEffect triggers, applying a resolution order (for repeatability).
    """
    def __init__(self, resolvers_for_type):
        self._resolvers = resolvers_for_type

    # TODO: list of triggers
    def resolve(self, triggers: List[object]):
        # TODO: sort list based on existing rules in order to enforce fixed resolution orders.

        for trigger in triggers:
            resolver_provider = self._resolvers(type(trigger))
            trigger_resolver = resolver_provider()
            trigger_resolver.resolve(trigger)
