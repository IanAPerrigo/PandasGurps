

class ActionManager:
    """
    TODO: should keep track of what types of actions are still available.
        NOTE: a fair amount of rules could determine which actions are applicable. KISS
    """
    def __init__(self):
        # Collects actions from an actor
        self.actor_actions = {}

    def register_actor(self, actor):
        self.actor_actions[actor.id] = []

    def submit_action(self, actor_action):
        self.actor_actions[actor_action.actor].append(actor_action)

    def clear_actions(self):
        self.actor_actions = {}

    def get_submitted_actions(self):
        return sorted(self.actor_actions.items(), key=lambda kv: kv[1].order)
