from uuid import uuid4

from .action import Action


class Harvest(Action):
    def __init__(self, target_id: uuid4 = None, weapon=None):
        super(Harvest, self).__init__()
        self.target_id = target_id
        self.weapon = weapon


class Eat(Action):
    def __init__(self, target_id: uuid4 = None):
        """
        Given the id of an entity, attempt to eat it.
        Only works on Food, and by default will search the ground, in bags,
        :param target_id:
        """
        super(Eat, self).__init__()
        self.target_id = target_id
