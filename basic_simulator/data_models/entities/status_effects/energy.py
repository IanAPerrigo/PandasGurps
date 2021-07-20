from .status_effect import StatusEffect, LeveledStatusEffect, TriggeringStatusEffect, TrackedTrigger

from data_models.triggers.status_effects.energy import *
from data_models.entities.stats.stat_set import StatType
from data_models.entities.modifiers.modifier import Modifier
from utility.time import *


class Fed(LeveledStatusEffect):
    """
    Status representing how many meals have been eaten.
    Each whole meal represents 1 stack of fed.
        Note: until differently valued meals are added, then the meal value will be added to the level (fractional meals).
    """

    def __init__(self, level=0):
        super(Fed, self).__init__(level=level)


class Hydrated(LeveledStatusEffect):
    """
    Status representing how much water as been consumed.
    Each drink of water represents 1 stack of hydrated.
    """
    def __init__(self, level=0):
        super(Hydrated, self).__init__(level=level)


class Starving(TriggeringStatusEffect):
    """
    Status representing a lack of food (can co-exist with Fed).
    Starvation means the actor is at a deficit for food energy.
    A starvation level is gained for every meal missed during the day (triggered by a feeding event 3 times a day)
        Note: increased/decreased food consumption causes the number of periods to change.
    All starvation is lost when the next feeding event is triggered and certain other conditions are met:
        3+ meals, adequate rest, etc
    """
    def __init__(self, level=0, period_length_seconds=SECONDS_PER_DAY):
        super(Starving, self).__init__(modifiers=None)

        self.period_length_seconds = period_length_seconds
        self.last_level = None
        self._level = level

        # Static modifiers to be changed based on
        self.max_fp_reduction = Modifier()
        fp_modifiers = {self.max_fp_reduction}
        self.modifiers[StatType.FP] = fp_modifiers

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self.last_level = self._level
        self._level = value

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
        # Starvation is increased as a trigger condition. Nothing to do except schedule next tick.
        self.next_relevant_tick = tick + self.period_length_seconds


class Dehydrated(TriggeringStatusEffect):
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
        super(Dehydrated, self).__init__(modifiers=None)

        self.period_length_seconds = period_length_seconds
        self.last_level = None
        self._level = level

        self.severe = False

        # Static modifiers to be changed based on
        self.max_fp_reduction = Modifier()
        fp_modifiers = {self.max_fp_reduction}
        self.modifiers[StatType.FP] = fp_modifiers

        self.max_hp_reduction = Modifier()
        hp_modifiers = {self.max_hp_reduction}
        self.modifiers[StatType.HP] = hp_modifiers

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self.last_level = self._level
        self._level = value

    def triggers(self, entity_id):
        trigger_list = []
        for a_t in self._active_triggers:
            trigger_list.append(a_t.trigger_type(entity_id=entity_id, tick_count=a_t.tick_count))
        return trigger_list

    def bootstrap(self, tick, time_scale):
        self.added_at_tick = tick

        daily_trigger = self.added_at_tick + self.period_length_seconds
        eight_hour_trigger = self.added_at_tick + (self.period_length_seconds // 3)
        # TODO: note, integer division could accumulate errors. Better to allow fractional ticks, and allow them to
        #  align when they do so no time is lost (periodic divergence)

        # Queue all relevant triggers.
        # TODO: make a trigger object, add fields like periodicity, period length, etc.
        self._trigger_map[eight_hour_trigger] = [TrackedTrigger(EightHourDehydrationTrigger, self.period_length_seconds // 3)]
        self._trigger_map[daily_trigger] = [TrackedTrigger(DailyDehydrationTrigger, self.period_length_seconds)]

        self.next_relevant_tick = min(self._trigger_map.keys())
        self.active = True

    def update_tick(self, tick, time_scale):
        """
        If the update was called, then a threshold of the status has been met.
        :param tick:
        :param time_scale:
        :return:
        """
        super(Dehydrated, self).update_tick(tick, time_scale)


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
    def __init__(self, level=0, period_length_seconds=SECONDS_PER_DAY):
        super(Resting, self).__init__()

        self.period_length_seconds = period_length_seconds

        # Set tracking the tick that the level was updated at.
        self.increased_on_tick = set()

        self.last_level = None
        self._level = level

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self.last_level = self._level
        self._level = value

        # Save the last relevant tick that the level was updated on.
        if self._level > self.last_level:
            self.increased_on_tick.add(self.last_relevant_tick)


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
