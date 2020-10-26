from data_models.actions import MovementType, MovementAction, MeleeAttack
from data_models.actions.maneuvers import MoveManeuver, MoveAttackManeuver, YieldTurnManeuver
from data_models.actions import ActionStatus
from data_models.state.simulation_state import SimulationState
from behaviors import Behavior


class HumanPlayerBehavior(Behavior):
    """
    TODO: include movement interface as dep
    """
    def __init__(self):
        self.keys = None # TODO: should be a dep
        self.action_type = None
        self.maneuver_type = None
        self.ready = False

    def act(self, state: SimulationState):
        # TODO: call a renderer to display the view of this player
        #       Big todo here, since there are not separate views for each player. Currently do nothing.
        action = []
        maneuver = None
        vector = None

        # If a new maneuver event is signaled, change the active maneuver type.
        # Return here so that empty maneuvers aren't submitted.
        if self.keys['1'] != 0: # MOVE_MANEUVER
            self.maneuver_type = MoveManeuver
            self.keys['1'] = 0
            return
        elif self.keys['2'] != 0: # MOVE_ATTACK_MANEUVER
            self.maneuver_type = MoveAttackManeuver
            self.keys['2'] = 0
            return
        elif self.keys['space'] != 0: # YIELD_TURN_MANEUVER
            # The exception to the rule above is because we are yielding. There is no plan to yield.
            self.keys['space'] = 0
            maneuver = YieldTurnManeuver()
            maneuver.status = ActionStatus.READY
            return maneuver

        # Set the action type
        if self.keys["c"] != 0:
            self.action_type = "combat" if self.action_type != "combat" else None
            self.keys["c"] = 0
        elif self.keys["m"] != 0:
            self.action_type = "movement" if self.action_type != "movement" else None
            self.keys["m"] = 0
        elif self.keys["r"] != 0:
            self.ready = True
            self.keys["r"] = 0

        # Extract vector events.
        if self.keys['VECTOR_NORTH_WEST'] != 0:
            vector = MovementType.NORTH_WEST
            self.keys['VECTOR_NORTH_WEST'] = 0
        elif self.keys['VECTOR_NORTH_EAST'] != 0:
            vector = MovementType.NORTH_EAST
            self.keys['VECTOR_NORTH_EAST'] = 0
        elif self.keys['VECTOR_EAST'] != 0:
            vector = MovementType.EAST
            self.keys['VECTOR_EAST'] = 0
        elif self.keys['VECTOR_SOUTH_EAST'] != 0:
            vector = MovementType.SOUTH_EAST
            self.keys['VECTOR_SOUTH_EAST'] = 0
        elif self.keys['VECTOR_SOUTH_WEST'] != 0:
            vector = MovementType.SOUTH_WEST
            self.keys['VECTOR_SOUTH_WEST'] = 0
        elif self.keys['VECTOR_WEST'] != 0:
            vector = MovementType.WEST
            self.keys['VECTOR_WEST'] = 0

        # Skip making a maneuver if nothing is going to be done.
        if (vector is None and not self.ready) or self.maneuver_type is None:
            return

        if self.action_type == "combat" and vector is not None:
            action = [MeleeAttack.in_direction(vector)]
        elif self.action_type == "movement" and vector is not None:
            action = [MovementAction(vector)]
        else:
            # TODO: add NO-OP
            action = [MovementAction(MovementType.NONE)]

        maneuver = self.maneuver_type(action)

        if self.ready:
            maneuver.status = ActionStatus.PARTIAL_READY
            self.ready = False

        return maneuver
