from .status_effect import StatusEffect, MonotonicallyDecreasingStatusEffect
from utility.time import *


class Fed(MonotonicallyDecreasingStatusEffect):
    """
    Status representing how many meals have been eaten.
    Each whole meal represents 1 stack of fed.
        Note: until differently valued meals are added, then the meal value will be added to the level (fractional meals).
    """

    def __init__(self, level=0, period_length_seconds=SECONDS_PER_DAY / 3):
        super(Fed, self).__init__(period_length_seconds=period_length_seconds, level=level)


class Hydrated(MonotonicallyDecreasingStatusEffect):
    """
    Status representing how much water as been consumed.
    Each drink of water represents 1 stack of hydrated.
    """
    def __init__(self, level=0, period_length_seconds=SECONDS_PER_DAY / 8):
        super(Hydrated, self).__init__(period_length_seconds=period_length_seconds, level=level)


class Starving(StatusEffect):
    """
    Status representing a lack of food (can co-exist with Fed).
    Starvation means the actor is at a deficit for food energy.
    A starvation level is gained for every meal missed during the day (triggered by a feeding event 3 times a day)
        Note: increased/decreased food consumption causes the number of periods to change.
    All starvation is lost when the next feeding event is triggered and certain other conditions are met:
        3+ meals, adequate rest, etc
    """
    def __init__(self, level=0, period_length_seconds=SECONDS_PER_DAY):
        super(Starving, self).__init__()

        self.period_length_seconds = period_length_seconds
        self.level = level

    def bootstrap(self, tick, time_scale):
        self.added_at_tick = tick
        #ticks_per_period = self.period_length_seconds // time_scale
        self.next_relevant_tick = self.added_at_tick + self.period_length_seconds

        # In this case, active will be set to false externally when the conditions for hunger and
        # rest have been satisfied.
        self.active = True

    def update_tick(self, tick, time_scale):
        """
        If the update was called, then a threshold of the status has been met.
        :param tick:
        :param time_scale:
        :return:
        """
        # Starvation increases by one per period.
        self.level += 1
        #ticks_per_period = self.period_length_seconds // time_scale
        self.next_relevant_tick = tick + self.period_length_seconds


class Dehydrated(StatusEffect):
    """
    Status representing lack of water (can co-exist with hydrated).
    Dehydrated means the actor is at a deficit of water.
    A dehydration level is gained per level of missing water intake (hydrated =8 is a full amount, counted TODO: how often????)
        Note: increased/decreased water consumption causes the number of periods to change.
    A severe dehydration stack is gained daily by drinking less than 1 quart of water.
    All dehydration (also severe) is lost when the next drinking event is triggered and certain other conditions are met:
        8+ drinks, adequate rest, etc

    """
    def __init__(self, level=0, period_length_seconds=SECONDS_PER_DAY):
        super(Dehydrated, self).__init__()

        self.period_length_seconds = period_length_seconds
        self.level = level
        self.severe = False

    def bootstrap(self, tick, time_scale):
        self.added_at_tick = tick
        #ticks_per_period = self.period_length_seconds // time_scale
        self.next_relevant_tick = self.added_at_tick + self.period_length_seconds

        # In this case, active will be set to false externally when the conditions for hunger and
        # rest have been satisfied.
        self.active = True

    def update_tick(self, tick, time_scale):
        """
        If the update was called, then a threshold of the status has been met.
        :param tick:
        :param time_scale:
        :return:
        """
        # Starvation increases by one per period.
        self.level += 1
        #ticks_per_period = self.period_length_seconds // time_scale
        self.next_relevant_tick = tick + self.period_length_seconds


class Resting(StatusEffect):
    """
    Status representing active conscious resting (a lack of strenuous activity).
    Resting is gained after 10 minutes of a lack of overly strenuous activity.
    During resting, every 10 minutes will yield 1 FP recovery, with a bonus of 1 FP if food was consumed during the rest cycle.
    Resting is lost if any strenuous activity is performed:
        Movement > 40% of BasicSpeed (subject to change)
        Any combat (including harvesting)
        Lifting extra heavy loads (overexertion)
    Resting is also lost if any stacks of dehydration / starvation are gained.

    """
    def __init__(self):
        super(Resting, self).__init__()


class Sleeping(StatusEffect):
    """
    Status representing active sleep.
    A level of sleep is gained for every hour of un-interrupted sleep.
    By default, 6 levels of sleep are required in every 24 hour cycle.
        Note: this value is changed by more/less sleep adv/dis.
    During sleep, each hour of sleep will yield 1 FP recovery.
    After a 24 hour period (right after waking up perhaps), every level of missed sleep will be turned into a separate
    missed sleep status.
    """
    def __init__(self, level=0):
        super(Sleeping, self).__init__()
        self.level = level
