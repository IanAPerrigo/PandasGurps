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


class SuccessRoll(Roll):
    def __init__(self, modifiers=None):
        super(SuccessRoll, self).__init__(3, 6, modifiers)


class ContestResults(enum.Enum):
    Success = "Success"
    Failure = "Failure"
    Critical_Success = "Critical Success"
    Critical_Failure = "Critical Failure"


class ContestRoll(SuccessRoll):
    def __init__(self, value, modifiers=None):
        super(ContestRoll, self).__init__(modifiers)
        self.value = value

    def contest(self):
        super(ContestRoll, self).roll()

        if self.last_raw_result <= 4 \
                or self.last_raw_result <= 5 and self.value >= 15 \
                or self.last_raw_result <= 6 and self.value >= 16:
            return ContestResults.Critical_Success
        elif self.last_raw_result == 18 \
                or self.last_raw_result == 17 and self.value <= 15 \
                or self.last_raw_result >= self.value + 10:
            return ContestResults.Critical_Failure
        else:
            return ContestResults.Success if self.last_result <= self.value else ContestResults.Failure
