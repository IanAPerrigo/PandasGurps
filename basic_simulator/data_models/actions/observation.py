from uuid import UUID

from .action import Action, ActionStatus


class ObservationAction(Action):
    def __init__(self, target_id: UUID = None):
        super(ObservationAction, self).__init__()
        self.target_id = target_id
