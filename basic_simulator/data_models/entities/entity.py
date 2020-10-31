from uuid import UUID

from .status_set import StatusSet
from .status_effects import StatusEffect


class Entity:
    def __init__(self, entity_id: UUID, status_effects: StatusSet = None):
        self.entity_id = entity_id
        self.status_effects = status_effects if status_effects is not None else StatusSet()

    def add_status_effect(self, a_status_effect: StatusEffect):
        self.status_effects.add(a_status_effect)

    def remove_status_effect(self, a_status_effect: StatusEffect):
        self.status_effects.remove(a_status_effect)

    def remove_all_status_effects(self, a_status_effect_type: type):
        self.status_effects.remove_all(a_status_effect_type)
