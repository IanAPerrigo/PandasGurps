import enum
from collections import MutableMapping


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


class StatSet(MutableMapping):
    def __init__(self, do_init=True):
        super(StatSet, self).__init__()

        self._mapping = {}

        for stat_type in StatType:
            self._mapping[stat_type] = 0

    def init(self):
        for stat_type in StatType:
            self._mapping[stat_type] = 0

    def __getitem__(self, key):
        return self._mapping[key]

    def __delitem__(self, key):
        self._mapping.pop(key)

    def __setitem__(self, key, value):
        self._mapping[key] = value

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)

    def __repr__(self):
        return f"{type(self).__name__}({self._mapping})"




