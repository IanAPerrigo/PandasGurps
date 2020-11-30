from managers.status_effect_manager import StatusEffectManager
import time


class TickManager:
    def __init__(self, status_effect_manager: StatusEffectManager, tick_value, tick_rate):
        if tick_rate <= 0:
            raise Exception("tick_rate cannot be zero of less.")

        self.tick_value = tick_value
        self.tick_rate = tick_rate
        self.status_effect_manager = status_effect_manager
        self.start_time = time.perf_counter()
        self.last_time = time.perf_counter()

        self.update_time = time.time()

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

        current_time = time.perf_counter()
        time_elapsed = current_time - self.last_time
        total_time = current_time - self.start_time
        self.last_time = current_time

        c_time = time.time()
        if self.update_time + 5 < c_time:
            tick_rate = 1 / time_elapsed if time_elapsed != 0 else 0
            self.update_time = c_time
            print("%d" % (tick_rate))

        # Tick all status effects
        self.status_effect_manager.tick_status_effects(self.tick_value, self.tick_rate)

