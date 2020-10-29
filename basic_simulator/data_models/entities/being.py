import math

from data_models.entities.entity import Entity
from data_models.entities.stats import *
from data_models.entities.modifiers import ModifiedStatSet
from data_models.entities.status_effects import *


class Being(Entity):
    """
    Base class for any entity with stats.
    """
    def __init__(self, base_stats: StatSet, modified_stats: ModifiedStatSet, status_effects: set = None):
        super(Being, self).__init__(status_effects=status_effects)
        self.base_stats = base_stats
        self.stats = modified_stats
        self.advantages = None
        self.disadvantages = None
        self.description = None
        self.inventory = None
        self.languages = None
        self.character_points = 0

    def add_status_effect(self, a_status_effect: StatusEffect):
        self.status_effects.add(a_status_effect)
        map(self.stats.add_modifier, a_status_effect.modifiers)

    def remove_status_effect(self, a_status_effect: StatusEffect):
        self.status_effects.discard(a_status_effect)
        map(self.stats.remove_modifier, a_status_effect.modifiers)

    @property
    def active_weapons(self):
        # TODO: will be mutated by actions on the character, such as readying, innate attacks, etc.
        return []

    @property
    def dr(self):
        # TODO: total inventory and natural DR, etc
        return 0

    @property
    def dodge(self):
        # TODO: return floor(speed + 3) * encumbrance penalty
        return 0

    @property
    def parry(self):
        # TODO: derive from active equipment
        return 0

    @property
    def block(self):
        # TODO: derive from active equipment
        return 0

    @property
    def bl(self):
        return math.pow(self.stats[StatType.ST.value], 2) / 5

    @property
    def damage_thr(self):
        return 0

    @property
    def damage_sw(self):
        return 0



