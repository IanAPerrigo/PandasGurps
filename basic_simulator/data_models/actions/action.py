from enum import Enum


class ActionStatus(Enum):
    # Default status of the action, meaning the action is not ready to be resolved (missing data).
    UNREADY = 0

    # Ready state, meaning the action can be resolved.
    READY = 1

    # Resolved state, cannot be changed from this state.
    RESOLVED = 2

    # Failed state, meaning the action was improper or unable to be executed in the current context.
    # (maybe separate these two)
    FAILED = 3

    # Partially executed state and unready. Similar to regular unready state, but when it is set to PARTIAL_READY,
    # it wont result in the RESOLVED state, it will go back to PARTIAL_UNREADY
    PARTIAL_UNREADY = 4

    # Partially executed state, ready to be partially resolved.
    PARTIAL_READY = 5


class Action:
    def __init__(self):
        self.status = ActionStatus.UNREADY
        self.reason = None
        self.actor = None

    def set_actor(self, actor_id):
        self.actor = actor_id


class CompoundAction(Action):
    def __init__(self, actions: list):
        super(CompoundAction, self).__init__()
        self.actions = actions

    def set_actor(self, actor_id):
        super(CompoundAction, self).set_actor(actor_id)
        for action in self.actions:
            action.set_actor(actor_id)

    def merge(self, a1):
        if self.actor != a1.actor:
            raise Exception("Cannot merge actions from two different actors.")
        if self.status == ActionStatus.RESOLVED or a1.status == ActionStatus.RESOLVED:
            raise Exception("Cannot mutate an already completed action.")

        self.actions += a1.actions

        # Derive the status of the newly added actions.
        if self.status != ActionStatus.FAILED:
            self.status = a1.status
