import enum
import numpy as np

from .action import Action


class MovementType(enum.Enum):
    """
    NOTE: for hex movement only
    """
    NONE = 0, 0, 0
    NORTH_WEST = 0, 1, -1
    NORTH_EAST = 1, 0, -1
    EAST = 1, -1, 0
    SOUTH_EAST = 0, -1, 1
    SOUTH_WEST = -1, 0, 1
    WEST = -1, 1, 0


class MovementAction(Action):
    def __init__(self, direction: MovementType, actor=None):
        super(MovementAction, self).__init__()
        self.actor = actor
        self.direction = direction

    def get_vector(self):
        return self.direction.value
