import math

from data_models.actors.stats import *
from data_models.actors.modifiers import ModifiedStatSet
from data_models.actors.status_effects import *


class Character:
    """
    Base class for any playable character.
    """
    def __init__(self, base_stats: StatSet, modified_stats: ModifiedStatSet, status_effects=None):
        self.base_stats = base_stats
        self.stats = modified_stats
        self.status_effects = status_effects if status_effects is not None else set()
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



