from data_models.actions.maneuvers import Maneuver
from data_models.actions import ActionStatus

class ActionManager:
    """
    Module to contain maneuvers on the current game state (at all stages of resolution).
    TODO: When a turn ends, this manager is purged and the actions are saved in the history.
    TODO: simplification of earlier note. This module should manage maneuvers submitted by actors.
        The only concern with this module is to use an external rule manager to determine if two maneuvers
        can be used in series.
    """
    def __init__(self):
        # Collects actions from an actor
        self.actor_actions = {}
        self.current_order = 0

    def register_actor(self, actor_id):
        self.actor_actions[actor_id] = []

    def submit_maneuver(self, actor_id, actor_maneuver: Maneuver):
        """
        Add or update a maneuver for a given actor.
        :param actor_id:
        :param actor_maneuver: 
        :return: 
        """
        # Ignore empty maneuvers
        if actor_maneuver is None:
            return

        # TODO: verify that the actor submitting the action is the actor contained in the action.

        # Determine if maneuver can be merged with an existing maneuver or added as a separate maneuver.
        matching_types = list(filter(lambda m: type(m) == type(actor_maneuver), self.actor_actions[actor_id]))
        if len(matching_types) == 1:
            # TODO: problem here if a maneuver is of a certain type is issued twice after the first has completed.
            matching_types[0].merge(actor_maneuver)
        else:
            self.actor_actions[actor_id].append(actor_maneuver)

    def clear(self):
        self.actor_actions = {}
        self.current_order = 0

    def remove_all_actions(self):
        for actor, actions in self.actor_actions.items():
            actions.clear()

    def get_submitted_actions(self):
        actions_with_actor = []
        # TODO: NOTE: not sure why a tuple is returned here, could easily jsut return action (action has actor in it)
        for actor, maneuvers in self.actor_actions.items():
            for maneuver in maneuvers:
                actions_with_actor.append(maneuver)
        return actions_with_actor

    def truncate_failure(self, action: Maneuver):
        # TODO: this may not be used in the future depending on how failed actions are treated.
        failure_index = self.actor_actions[action.actor].index(action)
        self.actor_actions[action.actor] = self.actor_actions[action.actor][:failure_index + 1]

        # Trim the point of failure
        sub_failure = next(sub_action for sub_action in action.actions if sub_action.status == ActionStatus.FAILED)
        sub_failure_index = action.actions.index(sub_failure)
        action.actions = action.actions[:sub_failure_index]

        # Default it to unready, since there is no way to know if its a partial or not.
        # The caller will end up setting it to the right status when they issue the new actions.
        action.status = ActionStatus.UNREADY
