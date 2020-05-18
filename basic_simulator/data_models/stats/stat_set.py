import enum


class StatType(enum.Enum):
    ST = "ST"
    IQ = "IQ"
    DX = "DX"
    HT = "HT"
    FP = "FP"
    WILL = "WILL"
    PER = "PER"
    HP = "HP"


class StatSet(dict):
    def __init__(self):
        super(StatSet, self).__init__()

        for stat_type in StatType:
            self[stat_type.value] = None

