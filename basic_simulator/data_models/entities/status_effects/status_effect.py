
class StatusEffect:
    """
    Contains an internal representation of the effects on an actor.
    For the time being, status effects are either direct modifiers on stats and skills, or just flags
    to mark conditions handled elsewhere.

    Modifiers: stored in a dictionary mapping of [thing modified] -> Modifier
    e.g. StatType.ST -> Modifier() = Direct modifier to ST and everything that used it.
    e.g. SkillType.Longsword -> Modifier() = Modifier to the skill of Longsword and anything that could default from it.
    e.g. SkillBase.DX -> Modifier() = Modifier to Skills based on DX (a concrete example of this would be "Shock").

    Flags: contains no modifiers, identified by the the status effect's type.
    e.g. Unconsciousness: handled in the logic that delegates who's turn it is / what actions can be taken.
    e.g. Death: Used to flag a dead actor, handled similarly to unconsciousness.
    e.g. Aim / Concentrate: Used to mark actors that are the target of aiming, etc. Or maybe flip this, to have the status
    of "Aiming" on the actor that is aiming (and then giving them modifiers conditionally.

    """

    def __init__(self, modifiers: dict = None):
        self.modifiers = modifiers if modifiers is not None else dict()
        self.added_at_tick = None
        self.removed_at_tick = None
        self.next_relevant_tick = None
        self.active = False

    def bootstrap(self, tick, time_scale):
        """
        Setup all tick information.
        :param tick: The current tick
        :param time_scale: Seconds/tick. Status effects with realtime updates will use this to
        stay invariant to the scale.
        :return:
        """
        raise NotImplementedError()

    def update_tick(self, tick, time_scale):
        raise NotImplementedError()


class MonotonicallyDecreasingStatusEffect(StatusEffect):
    def __init__(self, period_length_seconds, level, modifiers: dict = None):
        super(MonotonicallyDecreasingStatusEffect, self).__init__(modifiers)

        self.period_length_seconds = period_length_seconds
        self.level = level

    def bootstrap(self, tick, time_scale):
        self.added_at_tick = tick
        # Calculate ticks from [seconds / [seconds/tick]]. Drop fractional ticks.
        ticks_per_period = self.period_length_seconds // time_scale
        self.next_relevant_tick = self.added_at_tick + ticks_per_period
        self.active = True

    def update_tick(self, tick, time_scale):
        """
        If the update was called, then a threshold of the status has been met.
        :param tick:
        :param time_scale:
        :return:
        """
        # Decrease the level and set the next update period.
        self.level -= 1
        ticks_per_period = self.period_length_seconds // time_scale
        self.next_relevant_tick = tick + ticks_per_period
