import enum
import numpy as np


class MovementType(enum.Enum):
    """
    NOTE: for hex movement only
    """
    NONE = 0
    NORTH_WEST = 1
    NORTH_EAST = 2
    EAST = 3
    SOUTH_EAST = 4
    SOUTH_WEST = 5
    WEST = 6


class MovementAction:
    def __init__(self, direction: MovementType):
        self.direction = direction

    def get_vector(self):
        if self.direction == MovementType.NONE:
            return 0, 0, 0
        elif self.direction == MovementType.NORTH_WEST:
            return 0, 1, -1
        elif self.direction == MovementType.NORTH_EAST:
            return 1, 0, -1
        elif self.direction == MovementType.EAST:
            return 1, -1, 0
        elif self.direction == MovementType.SOUTH_EAST:
            return 0, -1, 1
        elif self.direction == MovementType.SOUTH_WEST:
            return -1, 0, 1
        elif self.direction == MovementType.WEST:
            return -1, 1, 0
