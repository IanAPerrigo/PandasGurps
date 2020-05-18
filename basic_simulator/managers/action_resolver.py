

class ActionResolver:
    """ The gist of this class is to extend it and have dependencies related to
    resolving the action be injected
    """
    def __init__(self):
        """"""

    def resolve(self, state, action):
        raise NotImplementedError()


class MovementResolver(ActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self):
        super(MovementResolver, self).__init__()
        """"""

    def resolve(self, state, action):
        """"""


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