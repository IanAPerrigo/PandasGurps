import enum


class PrimaryStats(enum.Enum):
    # Primary Stats
    ST = "ST"
    IQ = "IQ"
    DX = "DX"
    HT = "HT"


class SecondaryStats(enum.Enum):
    # Secondary Characteristics
    FP = "FP"
    WILL = "WILL"
    PER = "PER"
    HP = "HP"
    SPD = "SPD"


class TertiaryStats(enum.Enum):
    # Tertiary stats
    BM = "BM"


class StatType(enum.Enum):
    # Primary Stats
    ST = "ST"
    IQ = "IQ"
    DX = "DX"
    HT = "HT"

    # Secondary Characteristics
    FP = "FP"
    WILL = "WILL"
    PER = "PER"
    HP = "HP"
    SPD = "SPD"

    # Tertiary stats
    BM = "BM"

    CURR_HP = "CURR_HP"
    CURR_FP = "CURR_FP"
    CURR_BM = "CURR_BM"


def get_derived(stat):
    stat_map = {PrimaryStats.ST: [SecondaryStats.HP],
                PrimaryStats.DX: [SecondaryStats.SPD],
                PrimaryStats.IQ: [SecondaryStats.PER, SecondaryStats.WILL],
                PrimaryStats.HT: [SecondaryStats.FP],
                SecondaryStats.SPD: [TertiaryStats.BM]}
    derived = stat_map.get(stat)

    return map(lambda x: x.value, derived if derived is not None else [])


class StatSet(dict):
    def __init__(self):
        super(StatSet, self).__init__()

        for stat_type in StatType:
            self[stat_type.value] = 0



