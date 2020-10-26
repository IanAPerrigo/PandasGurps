import numpy as np

from data_models.actors.character import Character
from data_models.actors.stats.stat_set import StatType, StatSet, SecondaryStats, PrimaryStats, get_derived
from data_models.actors.modifiers import ModifiedStatSet

class CharacterCreator:
    def __init__(self):
        # TODO: configuration for different aspects of the character creator.
        #   e.g.
        #   - rules on what skills, advantages, items, etc are allowed.
        #   - contextual rules on what selections can be made together (exclusivity, etc)
        #   - costs for different stats, skills, adv/dis, etc.
        pass

    def calculate_total(self, character: Character):
        # TODO: assume standard costs for stats (only thing that costs points at the moment)
        # Total primary stat costs.
        primary_stats = {
            StatType.ST: 10,
            StatType.DX: 20,
            StatType.IQ: 20,
            StatType.HT: 10
        }

        point_total = 0

        for stat in primary_stats.keys():
            # assume 10 is default.
            stat_difference = character.stats[stat.value] - 10
            stat_cost = stat_difference * primary_stats[stat]
            point_total += stat_cost

        return point_total

    def validate_character(self, character: Character):
        """
        Total up the points for the character and enforce other rules on different aspects of the character.
        :param character:
        :return:
        """
        return True

    # TODO: nto sure where to put a character generator. Definitely separate from the logic that validates them.
    def generate_character_via_normals(self, rho, defaults=None):
        defaults = {StatType.ST: 10,
                    StatType.IQ: 10,
                    StatType.DX: 10,
                    StatType.HT: 10,
                    StatType.WILL: 10,
                    StatType.PER: 10,
                    StatType.FP: 10,
                    StatType.HP: 10,
                    StatType.SPD: 100,
                    # TODO: switch back to 5 SPD
                    StatType.BM: 5} if not defaults else defaults
        keys, values = zip(*defaults.items())
        stats = np.round(np.random.normal(np.zeros(shape=(len(defaults))), scale=rho)).astype(int)
        generated_stats = dict(zip(keys, stats))

        combined_stats = dict()
        for pstype in PrimaryStats:
            stype = StatType(pstype.value)

            # Set the value of the default + generated change
            combined_stats[stype] = defaults[stype] + generated_stats[stype]

            # Set the secondary stat value
            for secondary in get_derived(pstype):
                sec_type = StatType(secondary)
                combined_stats[sec_type] = combined_stats[stype] + generated_stats[sec_type]

        for sstype in SecondaryStats:
            stype = StatType(sstype.value)

            # Set the value of the default + generated change
            combined_stats[stype] = defaults[stype] + generated_stats[stype]

            # Set the tertiary stat value
            for tertiary in get_derived(sstype):
                ter_type = StatType(tertiary)
                combined_stats[ter_type] = combined_stats[stype] + generated_stats[ter_type]

        stat_set = StatSet()
        for stype, value in combined_stats.items():
            stat_set[stype.value] = value

        stat_set[StatType.CURR_HP.value] = stat_set[StatType.HP.value]
        stat_set[StatType.CURR_FP.value] = stat_set[StatType.FP.value]
        stat_set[StatType.CURR_BM.value] = stat_set[StatType.BM.value]

        modified_stat_set = ModifiedStatSet(stat_set)

        character = Character(base_stats=stat_set, modified_stats=modified_stat_set)
        character.character_points = self.calculate_total(character)
        return character
