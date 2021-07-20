from uuid import uuid4

from .action import Action


class HarvestAction(Action):
    def __init__(self, target_id=None, weapon=None):
        super(HarvestAction, self).__init__()
        self.target_id = target_id
        self.weapon = weapon


class DrinkAction(Action):
    def __init__(self, direction=None, target=None):
        super(DrinkAction, self).__init__()
        self.direction = direction
        self.target = target


class EatAction(Action):
    def __init__(self, target_id=None):
        """
        Given the id of an entity, attempt to eat it.
        Only works on Food, and by default will search the ground, in bags,
        :param target_id:
        """
        super(EatAction, self).__init__()
        self.target_id = target_id
