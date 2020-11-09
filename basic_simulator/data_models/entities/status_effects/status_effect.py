
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
        self.last_relevant_tick = None
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
        self.last_relevant_tick = self.added_at_tick
        self.next_relevant_tick = self.added_at_tick + self.period_length_seconds
        self.active = True

    def update_tick(self, tick, time_scale):
        """
        If the update was called, then a threshold of the status has been met.
        :param tick:
        :param time_scale:
        :return:
        """
        # Determine how many periods have passed (timescale could trigger multiple times).
        ticks_elapsed = int((tick - self.last_relevant_tick) // self.period_length_seconds)
        ticks_truncated = int((tick - self.last_relevant_tick) % self.period_length_seconds)

        # Decrease the level by the number of ticks elapsed and set the next update period.
        self.level -= ticks_elapsed
        # Next period if the current time, minus the number of ticks since the last update should have been.
        self.next_relevant_tick = (tick - ticks_truncated) + self.period_length_seconds
        self.last_relevant_tick = (tick - ticks_truncated)


class ScaleInvariantStatusEffect(StatusEffect):
    """
    A status effect that isnt tied to the amount of physical time passes (time scale is measured in seconds / tick).
    A scale invariant status effect with period / trigger time of 5 means it will be 5 ticks from the last period
    elapsed. If the game clock scale is extended (more seconds per tick), the status invariant will still be the same
    amount of tick before and after. Regular status effects depend on the time elapsed; 5 ticks in the future is
    actually 5 seconds in the future with a time scale of 1, but is 1 tick with a time scale of 5.
    """
