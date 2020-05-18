import random
import enum
from data_models.actions import MovementType, MovementAction


class RandomActorBehavior:
    # Real actors would pull in utilities to assist in state evaluation
    def __init__(self):
        self.current_action = 1

    def act(self, state):
        if self.current_action > 6:
            self.current_action = 1
        type = MovementType(self.current_action)
        self.current_action += 1
        return MovementAction(type)


class HumanPlayerBehavior:
    """
    TODO: include movement interface as dep
    """
    def __init__(self):
        self.keys = None # TODO: should be a dep
        pass

    def act(self, state):
        # TODO: call a renderer to display the view of this player
        #       Big todo here, since there are not separate views for each player. Currently do nothing.
        move = None
        # TODO: Query interface for the moves intended to me made by this player.
        if self.keys["1"] != 0:
            move = MovementAction(MovementType.NORTH_WEST)
            self.keys["1"] = 0
        elif self.keys["2"] != 0:
            move = MovementAction(MovementType.NORTH_EAST)
            self.keys["2"] = 0
        elif self.keys["3"] != 0:
            move = MovementAction(MovementType.EAST)
            self.keys["3"] = 0
        elif self.keys["4"] != 0:
            move = MovementAction(MovementType.SOUTH_EAST)
            self.keys["4"] = 0
        elif self.keys["5"] != 0:
            move = MovementAction(MovementType.SOUTH_WEST)
            self.keys["5"] = 0
        elif self.keys["6"] != 0:
            move = MovementAction(MovementType.WEST)
            self.keys["6"] = 0

        return move
