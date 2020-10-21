import random
import enum


from data_models.actions import MovementType, MovementAction, MeleeAttack
from data_models.actions.maneuvers.move import MoveManeuver
from data_models.actions import ActionStatus
from data_models.state.simulation_state import SimulationState
from behaviors import Behavior


class HumanPlayerBehavior(Behavior):
    """
    TODO: include movement interface as dep
    """
    def __init__(self):
        self.keys = None # TODO: should be a dep
        self.mode = None
        self.ready = False

    def act(self, state: SimulationState):
        # TODO: call a renderer to display the view of this player
        #       Big todo here, since there are not separate views for each player. Currently do nothing.
        action = None
        vector = None

        # TODO: Query interface for the moves intended to me made by this player.
        if self.keys['MOVE_NORTH_WEST'] != 0:
            vector = MovementType.NORTH_WEST
            self.keys['MOVE_NORTH_WEST'] = 0
        elif self.keys['MOVE_NORTH_EAST'] != 0:
            vector = MovementType.NORTH_EAST
            self.keys['MOVE_NORTH_EAST'] = 0
        elif self.keys['MOVE_EAST'] != 0:
            vector = MovementType.EAST
            self.keys['MOVE_EAST'] = 0
        elif self.keys['MOVE_SOUTH_EAST'] != 0:
            vector = MovementType.SOUTH_EAST
            self.keys['MOVE_SOUTH_EAST'] = 0
        elif self.keys['MOVE_SOUTH_WEST'] != 0:
            vector = MovementType.SOUTH_WEST
            self.keys['MOVE_SOUTH_WEST'] = 0
        elif self.keys['MOVE_WEST'] != 0:
            vector = MovementType.WEST
            self.keys['MOVE_WEST'] = 0
        elif self.keys["c"] != 0:
            self.mode = "combat" if self.mode != "combat" else None
            self.keys["c"] = 0
        elif self.keys["m"] != 0:
            self.mode = "movement" if self.mode != "movement" else None
            self.keys["m"] = 0
        elif self.keys["r"] != 0:
            self.ready = True
            self.keys["r"] = 0
        else:
            # Nothing handled. Bail out.
            return

        if self.mode == "combat" and vector is not None:
            action = MeleeAttack.in_direction(vector)
            # TODO: convert to maneuvers.
        elif self.mode == "movement":
            moves = [MovementAction(vector)] if vector is not None else []
            action = MoveManeuver(moves)
        else:
            # TODO: add NO-OP
            action = MoveManeuver([MovementAction(MovementType.NONE)])

        if self.ready:
            action.status = ActionStatus.PARTIAL_READY
            self.ready = False

        return action
