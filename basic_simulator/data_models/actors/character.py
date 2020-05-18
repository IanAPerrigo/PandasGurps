from data_models.stats import *


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
