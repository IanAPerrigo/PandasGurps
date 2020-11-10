import random
import enum


class Roll:
    def __init__(self, num_dice, num_sides, modifiers=None):
        self.num_dice = num_dice
        self.num_sides = num_sides # TODO: zero sides validation
        self.modifiers = modifiers if modifiers else []
        self.last_result = None
        self.last_dice = None
        self.last_raw_result = None

    def roll(self):
        roll = [random.randint(1, self.num_sides) for _ in range(self.num_dice)]
        self.last_dice = roll
        roll_value = sum(roll)
        self.last_raw_result = roll_value
        # TODO: logging / eventing
        # TODO: make modifiers objects to allow for string descriptions.
        for modifier in self.modifiers:
            roll_value = modifier(roll_value)

        self.last_result = roll_value
        return roll_value

    def get_description(self):
        return "%dd%d + %d" % (self.num_dice, self.num_sides, 0)


class RollResult(enum.Enum):
    Success = "Success"
    Failure = "Failure"
    Critical_Success = "Critical Success"
    Critical_Failure = "Critical Failure"


class SuccessRoll:
    def __init__(self, value, modifiers=None):
        self._roll_descriptor = Roll(3, 6, modifiers)
        self.value = value
        self.last_result = None

    def get_latest_margin(self):
        return self.value - self._roll_descriptor.last_result

    def roll(self) -> RollResult:
        self._roll_descriptor.roll()
        self.last_result = self._roll_descriptor.last_result

        if self._roll_descriptor.last_raw_result <= 4 \
                or self._roll_descriptor.last_raw_result <= 5 and self.value >= 15 \
                or self._roll_descriptor.last_raw_result <= 6 and self.value >= 16:
            return RollResult.Critical_Success
        elif self._roll_descriptor.last_raw_result == 18 \
                or self._roll_descriptor.last_raw_result == 17 and self.value <= 15 \
                or self._roll_descriptor.last_raw_result >= self.value + 10:
            return RollResult.Critical_Failure
        else:
            return RollResult.Success if self._roll_descriptor.last_result <= self.value else RollResult.Failure


class ContestResult(enum.Enum):
    Success = "Success"
    Failure = "Failure"
    Tie = "Tie"


class ContestRoll:
    def __init__(self, subject_sroll: SuccessRoll, target_sroll: SuccessRoll):
        self.subject_sroll = subject_sroll
        self.target_sroll = target_sroll
        self.last_margin_difference = None

    def contest(self) -> ContestResult:
        """
        Return if the subject won or lost the contest.
        :return:
        """
        self.subject_sroll.roll()
        self.target_sroll.roll()
        s_margin = self.subject_sroll.get_latest_margin()
        t_margin = self.target_sroll.get_latest_margin()
        self.last_margin_difference = s_margin - t_margin

        if s_margin >= 0 > t_margin:
            return ContestResult.Success
        elif s_margin > t_margin:
            return ContestResult.Success
        elif s_margin < t_margin:
            return ContestResult.Failure
        elif s_margin == t_margin:
            return ContestResult.Tie
        else:
            return ContestResult.Failure


class ResistRoll(ContestRoll):
    def __init__(self, subject_sroll: SuccessRoll, target_sroll: SuccessRoll):
        super(ResistRoll, self).__init__(subject_sroll, target_sroll)

    def contest(self) -> ContestResult:
        """
        Return if the subject won or lost the contest.
        :return:
        """
        self.subject_sroll.roll()
        self.target_sroll.roll()
        s_margin = self.subject_sroll.get_latest_margin()
        t_margin = self.target_sroll.get_latest_margin()
        self.last_margin_difference = s_margin - t_margin

        if s_margin >= 0 > t_margin:
            return ContestResult.Success
        elif s_margin >= 0 and s_margin > t_margin:
            return ContestResult.Success
        elif s_margin < t_margin:
            return ContestResult.Failure
        else:
            return ContestResult.Failure
