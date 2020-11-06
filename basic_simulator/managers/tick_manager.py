from managers.status_effect_manager import StatusEffectManager


class TickManager:
    def __init__(self, status_effect_manager: StatusEffectManager, tick_value, tick_rate):
        if tick_rate <= 0:
            raise Exception("tick_rate cannot be zero of less.")

        self.tick_value = tick_value
        self.tick_rate = tick_rate
        self.status_effect_manager = status_effect_manager

    def tick(self):
        """
        Handle all the events that the tick manager knows about.
        Order matters, certain tick events are prioritized over others.
        :return:
        """

        # Bootstrap all new status effects.
        self.status_effect_manager.bootstrap_status_effects(self.tick_value, self.tick_rate)

        # Update the tick count.
        self.tick_value += self.tick_rate

        # Tick all status effects
        self.status_effect_manager.tick_status_effects(self.tick_value, self.tick_rate)

