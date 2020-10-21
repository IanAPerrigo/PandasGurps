from direct.showbase.DirectObject import DirectObject

from events import Event
from managers.entity_manager import EntityModelManager
from data_models.actors.stats.stat_set import StatType


class FatalDamageHandler(DirectObject):
    def __init__(self, entity_model_manager: EntityModelManager):
        super(FatalDamageHandler, self).__init__()

        self.entity_model_manager = entity_model_manager

        # Register event that watches for damage to occur.
        Event.register("actor_damaged", self, self.assess_damage)

    def assess_damage(self, actor_id, damage_taken):
        actor = self.entity_model_manager[actor_id].character_model

        curr_hp = actor.stats[StatType.CURR_HP.value]
        total_hp = actor.stats[StatType.HP.value]

        # Has the damage taken changed the actors health to below zero.
        if 0 >= curr_hp > -damage_taken:

            # TODO: roll vs HT:
            #  success: remain conscious.
            #  Applies debuff for "Hanging on to consciousness": roll each turn that you dont "Do Nothing" action
            #  to retain consciousness.
            #  failure: fall unconscious. Applies the "Unconscious" debuff.

            pass
        # Has the damage taken changed the actors health to below the first multiple.
        elif (-1 * total_hp) >= curr_hp > (-1 * total_hp)-damage_taken:
            # TODO: roll vs HT:
            #  success: Nothing.
            #  failure by 1 or 2: mortal wounds (for simplicity at the beginning, this is death)
            #  failure: death
            pass
        # Has the damage taken changed the actors health to below the second multiple.
        elif (-2 * total_hp) >= curr_hp > (-2 * total_hp)-damage_taken:
            # TODO: roll vs HT:
            #  success: Nothing.
            #  failure by 1 or 2: mortal wounds (for simplicity at the beginning, this is death)
            #  failure: death
            pass
        # Has the damage taken changed the actors health to below the third multiple.
        elif (-3 * total_hp) >= curr_hp > (-3 * total_hp)-damage_taken:
            # TODO: roll vs HT:
            #  success: Nothing.
            #  failure by 1 or 2: mortal wounds (for simplicity at the beginning, this is death)
            #  failure: death
            pass
        # Has the damage taken changed the actors health to below the fifth multiple.
        elif (-5 * total_hp) >= curr_hp:
            # TODO: instant death
            pass

