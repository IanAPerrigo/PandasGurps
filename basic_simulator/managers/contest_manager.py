from uuid import UUID

from utility.rolling import SuccessRoll, RollResult
from managers.simulation_manager import SimulationStateManager
from data_models.entities.stats.stat_set import StatType


class AttributeContestResult:
    def __init__(self, subject_contest_result: RollResult, subject_margin,
                 target_contest_result: RollResult, target_margin):
        self.subject_contest_result = subject_contest_result
        self.subject_margin = subject_margin
        self.target_contest_result = target_contest_result
        self.target_margin = target_margin


class ContestManager:
    def __init__(self, simulation_manager: SimulationStateManager):
        self.simulation_manager = simulation_manager

    def contest(self, subject_id: UUID, target_id: UUID,
                subject_contest_type, target_contest_type,
                subject_modifiers, target_modifiers,
                allow_defaults=False):
        subject_model = self.simulation_manager.being_model_manager.get(subject_id)
        target_model = self.simulation_manager.being_model_manager.get(target_id)

        result = None
        sub_result, sub_margin, tar_result, tar_margin = None, None, None, None

        # Separate different contests based on the type.
        if isinstance(subject_contest_type, StatType):
            contest_value = subject_model.stats[subject_contest_type]
            sub_roll = SuccessRoll(contest_value, subject_modifiers)
            sub_result = sub_roll.roll()
            sub_margin = contest_value - sub_roll.last_result
        # elif isinstance(subject_contest_type, SkillType):
        #     contest_value = subject_model.skills[subject_contest_type]
        #     sub_roll = ContestRoll(contest_value, subject_modifiers)
        #     sub_result = sub_roll.contest()
        #     sub_margin = contest_value - sub_roll.last_result

        # TODO: active defenses

        if isinstance(target_contest_type, StatType):
            contest_value = target_model.stats[target_contest_type]
            tar_roll = SuccessRoll(contest_value, target_modifiers)
            tar_result = tar_roll.roll()
            tar_margin = contest_value - tar_roll.last_result

        return AttributeContestResult(sub_result, sub_margin, tar_result, tar_margin)
