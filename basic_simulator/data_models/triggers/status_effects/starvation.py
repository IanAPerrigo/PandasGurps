from ..trigger import Trigger


class StarvationTrigger(Trigger):
    def __init__(self, entity_id):
        self.entity_id = entity_id
