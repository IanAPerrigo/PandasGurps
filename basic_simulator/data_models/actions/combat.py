import enum
from uuid import uuid4
import numpy as np

from .action import Action


class MeleeAttack(Action):
    def __init__(self, target_id: uuid4 = None, location: np.array = None, direction: np.array = None):
        super(MeleeAttack, self).__init__()
        self.target_id = target_id
        self.location = location
        self.direction = direction

    @classmethod
    def at_location(cls, location: np.array):
        return cls(location=location)

    @classmethod
    def in_direction(cls, direction: np.array):
        return cls(direction=direction)

    @classmethod
    def target(cls, target_id: uuid4):
        return cls(target_id=target_id)
