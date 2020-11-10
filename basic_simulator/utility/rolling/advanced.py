from uuid import UUID

from . import SuccessRoll, RollResult
from data_models.entities.stats.stat_set import StatType
from managers.entity_manager import BeingModelManager


class RollVersus(SuccessRoll):
    def __init__(self, being_id: UUID, versus, modifiers=None, being_model_manager: BeingModelManager = None):
        self.being_model_manager = being_model_manager
        self.being_id = being_id

        if isinstance(versus, StatType):
            value = self._versus_stat(versus)
        #elif isinstance(versus, SkillType):
        # TODO: add hit_active_weapon to gather the relevant weapon and skill associated
        else:
            raise Exception('Cannot find the type of object to roll versus.')

        super(RollVersus, self).__init__(value, modifiers)

    def _versus_stat(self, stat_type: StatType):
        model = self.being_model_manager[self.being_id]
        return model.stats.get(stat_type)
