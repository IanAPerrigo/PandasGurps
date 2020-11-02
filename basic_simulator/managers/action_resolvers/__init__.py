from .food import *
from .movement import *
from .combat import *

"""
Ideas: 
Resolver returns action as:
Completed:
    Action was successfully applied and state was updated.
Incomplete:
    Returns action that requires the resolution of another action to complete.
    e.g. Original action, MovementAction
    MA -requiring-> RollAction
        Return requested action with a continuation action.
Failed:
    Action failed to execute for a reason (Not the same as a failed roll or negative outcome)

"""