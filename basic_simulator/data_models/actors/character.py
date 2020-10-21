import math

from data_models.actors.stats import *


class Character:
    """
    Base class for any playable character.
    """
    def __init__(self, stats: StatSet):
        self.stats = stats
        self.advantages = None
        self.disadvantages = None
        self.description = None
        self.inventory = None
        self.languages = None
        self.character_points = 0

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



