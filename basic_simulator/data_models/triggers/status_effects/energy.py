from ..trigger import Trigger


class StarvationTrigger(Trigger):
    def __init__(self, entity_id, tick_count=0):
        self.entity_id = entity_id
        self.tick_count = tick_count


class DailyDehydrationTrigger(Trigger):
    def __init__(self, entity_id, tick_count=0):
        self.entity_id = entity_id
        self.tick_count = tick_count


class EightHourDehydrationTrigger(Trigger):
    def __init__(self, entity_id, tick_count=0):
        self.entity_id = entity_id
        self.tick_count = tick_count

