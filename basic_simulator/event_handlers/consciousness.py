from direct.showbase.DirectObject import DirectObject

from events import Event
from managers.entity_manager import EntityModelManager
from utility.rolling import *
from data_models.entities.stats import StatType
from data_models.entities.status_effects.consciousness import *


class ConsciousnessHandler(DirectObject):
    def __init__(self, entity_model_manager: EntityModelManager, logger):
        super(ConsciousnessHandler, self).__init__()

        self.entity_model_manager = entity_model_manager
        self.logger = logger

        # Register event that watches for damage to occur.
        Event.register("actor_damaged", self, self.assess_damage)
        Event.register("actor_retain_consciousness", self, self.maintain_consciousness)
        Event.register("actor_regain_consciousness", self, self.regain_consciousness)

    def apply_death(self, actor):
        # Death is absolute, and negates any other form of consciousness.
        actor.add_status_effect(DEAD)
        actor.remove_status_effect(HANGING_ONTO_CONSCIOUSNESS)
        actor.remove_status_effect(UNCONSCIOUS)

    def apply_unconscious(self, actor):
        # Consciousness is mutually exclusive with hanging on.
        actor.add_status_effect(UNCONSCIOUS)
        actor.remove_status_effect(HANGING_ONTO_CONSCIOUSNESS)

    def apply_hanging_on(self, actor):
        # Hanging on is mutually exclusive with unconscious.
        actor.add_status_effect(HANGING_ONTO_CONSCIOUSNESS)
        actor.remove_status_effect(UNCONSCIOUS)

    def below_zero(self, actor):
        ht = actor.stats[StatType.HT.value]
        curr_hp = actor.stats[StatType.CURR_HP.value]

        ht_roll = ContestRoll(ht)
        ht_result = ht_roll.contest()

        self.logger.info("Fell below 0 HP (HP = %d). Rolled HT to stay conscious: %s | [%d vs HT of %d]" %
                         (curr_hp, ht_result.value, ht_roll.last_result, ht))

        if ht_result == ContestResults.Failure:
            self.apply_unconscious(actor)
        elif ht_result == ContestResults.Critical_Failure:
            self.apply_death(actor)
        elif ht_result == ContestResults.Critical_Success:
            self.apply_hanging_on(actor)
        else:
            self.apply_hanging_on(actor)

    def negative_multiple(self, actor):
        ht = actor.stats[StatType.HT.value]
        curr_hp = actor.stats[StatType.CURR_HP.value]

        ht_roll = ContestRoll(ht)
        ht_result = ht_roll.contest()

        self.logger.info("Fell below a negative multiple of HP (HP = %d). Rolled HT to stay conscious: %s | [%d vs HT of %d]" %
                         (curr_hp, ht_result.value, ht_roll.last_result, ht))

        # TODO: clear out old status like if unconscious -> death, remove unconscious.

        if ht_result == ContestResults.Failure:
            self.apply_death(actor) # TODO: Technically dying, but for simplicity.
        elif ht_result == ContestResults.Critical_Failure:
            self.apply_death(actor)
        elif ht_result == ContestResults.Critical_Success:
            self.apply_hanging_on(actor)
            # TODO: maybe another status that helps recovery.
        else:
            self.apply_hanging_on(actor)

    def assess_damage(self, actor_id, damage_taken):
        actor = self.entity_model_manager[actor_id].character_model

        curr_hp = actor.stats[StatType.CURR_HP.value]
        total_hp = actor.stats[StatType.HP.value]

        # If the actor is non-existent, no reason to track status changes.
        if NON_EXISTENT in actor.status_effects:
            return

        # Has the damage taken changed the actors health to below zero.
        if 0 >= curr_hp > -damage_taken:
            self.below_zero(actor)
        # Has the damage taken changed the actors health to below the first multiple.
        elif (-1 * total_hp) >= curr_hp > (-1 * total_hp)-damage_taken:
            self.negative_multiple(actor)
        # Has the damage taken changed the actors health to below the second multiple.
        elif (-2 * total_hp) >= curr_hp > (-2 * total_hp)-damage_taken:
            self.negative_multiple(actor)
        # Has the damage taken changed the actors health to below the third multiple.
        elif (-3 * total_hp) >= curr_hp > (-3 * total_hp)-damage_taken:
            self.negative_multiple(actor)
        # Has the damage taken changed the actors health to below the fifth multiple.
        elif (-5 * total_hp) >= curr_hp > (-10 * total_hp):
            # Actor instantly dies.
            self.apply_death(actor)
            self.logger.info("%s passed threshold of death." % actor_id)
        elif (-10 * total_hp) >= curr_hp:
            actor.add_status_effect(NON_EXISTENT)
            self.logger.info("%s is unrecognizable." % actor_id)

    def maintain_consciousness(self, actor_id):
        pass

    def regain_consciousness(self, actor_id):
        pass
