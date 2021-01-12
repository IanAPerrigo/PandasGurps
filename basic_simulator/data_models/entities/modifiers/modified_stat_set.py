from operator import attrgetter
from functools import reduce
from collections import MutableMapping

from data_models.entities.modifiers.modifier_set import ModifierSet
from data_models.entities.stats import StatSet
from data_models.entities.modifiers.modifier import Modifier


class ModifiedStatSet(StatSet, MutableMapping):
    def __init__(self, base_stat_set: StatSet, modifier_set: ModifierSet):
        super(ModifiedStatSet, self).__init__(do_init=False)
        self._base_set = base_stat_set
        self.modifiers = set()

        self.modifier_stat_type = {}

        self.modifier_set = modifier_set

        # Inject relevant keys into the modifier set.
        for k in self.keys():
            self.modifier_set[k] = set()

    def add_modifier(self, modifier: Modifier, stat_type):
        self.modifiers.add(modifier)
        self.modifier_stat_type[modifier] = stat_type
        self.modifier_set[stat_type].add(modifier)

    def remove_modifier(self, modifier: Modifier):
        self.modifiers.discard(modifier)
        stat_type = self.modifier_stat_type[modifier]
        self.modifier_stat_type.pop(modifier, None)
        self.modifier_set[stat_type].discard(modifier)

    def __getitem__(self, item):
        base_stat = self._base_set[item]

        # TODO: total all modifiers for the given stat
        # TODO: enforce ordering (some modifiers should have higher precedence than others)
        #   e.g. order 0 is a "dont care" priority, and anything larger will take precedence.
        #   this is important for modifiers like "Reeling" that have a multiplicative modifier.

        modifiers_for_stat = self.modifier_set[item]
        modifiers_in_order = sorted(modifiers_for_stat, key=attrgetter('order'), reverse=True)
        modified_value = reduce(lambda val, mod: mod.modify(val), modifiers_in_order, base_stat)

        return modified_value

    def __setitem__(self, key, value):
        raise Exception("Modified stat sets cannot be mutated.")
