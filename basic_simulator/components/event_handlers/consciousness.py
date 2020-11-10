from direct.showbase.DirectObject import DirectObject

from events import Event
from managers.entity_manager import BeingModelManager
from managers.status_effect_manager import StatusEffectManager
from utility.rolling import *
from data_models.entities.stats import StatType
from data_models.entities.status_effects.consciousness import *


class ConsciousnessHandler(DirectObject):
    def __init__(self, being_model_manager: BeingModelManager,
                 status_effect_manager: StatusEffectManager,
                 logger):
        super(ConsciousnessHandler, self).__init__()

        self.being_model_manager = being_model_manager
        self.status_effect_manager = status_effect_manager
        self.logger = logger.newCategory(__name__)


        # Register event that watches for damage to occur.
        Event.register("actor_damaged", self, self.assess_damage)
        Event.register("actor_retain_consciousness", self, self.maintain_consciousness)
        Event.register("actor_regain_consciousness", self, self.regain_consciousness)

    def apply_death(self, actor):
        # Death is absolute, and negates any other form of consciousness.
        if not actor.status_effects.is_affected_by(Dead):
            self.status_effect_manager.add_status_effect_to_entity(actor.entity_id, Dead())
            self.logger.info("%s passed threshold of death." % actor.entity_id)
        self.status_effect_manager.remove_all_status_effects_from_entity(actor.entity_id, HangingOnToConsciousness)
        self.status_effect_manager.remove_all_status_effects_from_entity(actor.entity_id, Unconscious)

    def apply_non_existent(self, actor):
        # Death is absolute, and negates any other form of consciousness.
        if not actor.status_effects.is_affected_by(NonExistent):
            self.status_effect_manager.add_status_effect_to_entity(actor.entity_id, NonExistent())
            self.logger.info("%s is unrecognizable." % actor.entity_id)
        self.status_effect_manager.remove_all_status_effects_from_entity(actor.entity_id, HangingOnToConsciousness)
        self.status_effect_manager.remove_all_status_effects_from_entity(actor.entity_id, Unconscious)

    def apply_unconscious(self, actor):
        # Consciousness is mutually exclusive with hanging on.
        if not actor.status_effects.is_affected_by(Unconscious):
            self.status_effect_manager.add_status_effect_to_entity(actor.entity_id, Unconscious())
            self.logger.info("%s fell unconscious." % actor.entity_id)
        self.status_effect_manager.remove_all_status_effects_from_entity(actor.entity_id, HangingOnToConsciousness)

    def apply_hanging_on(self, actor):
        # Hanging on is mutually exclusive with unconscious.
        if not actor.status_effects.is_affected_by(HangingOnToConsciousness):
            self.status_effect_manager.add_status_effect_to_entity(actor.entity_id, HangingOnToConsciousness())
            self.logger.info("%s is hanging onto consciousness." % actor.entity_id)
        self.status_effect_manager.remove_all_status_effects_from_entity(actor.entity_id, Unconscious)

    def below_zero(self, actor):
        ht = actor.stats[StatType.HT.value]
        curr_hp = actor.stats[StatType.CURR_HP.value]

        ht_roll = SuccessRoll(ht)
        ht_result = ht_roll.roll()

        self.logger.info("Fell below 0 HP (HP = %d). Rolled HT to stay conscious: %s | [%d vs HT of %d]" %
                         (curr_hp, ht_result.value, ht_roll.last_result, ht))

        if ht_result == RollResult.Failure:
            self.apply_unconscious(actor)
        elif ht_result == RollResult.Critical_Failure:
            self.apply_death(actor)
        elif ht_result == RollResult.Critical_Success:
            self.apply_hanging_on(actor)
        else:
            self.apply_hanging_on(actor)

    def negative_multiple(self, actor):
        ht = actor.stats[StatType.HT.value]
        curr_hp = actor.stats[StatType.CURR_HP.value]

        ht_roll = SuccessRoll(ht)
        ht_result = ht_roll.roll()

        self.logger.info("Fell below a negative multiple of HP (HP = %d). Rolled HT to stay conscious: %s | [%d vs HT of %d]" %
                         (curr_hp, ht_result.value, ht_roll.last_result, ht))

        # TODO: clear out old status like if unconscious -> death, remove unconscious.

        if ht_result == RollResult.Failure:
            self.apply_death(actor) # TODO: Technically dying, but for simplicity.
        elif ht_result == RollResult.Critical_Failure:
            self.apply_death(actor)
        elif ht_result == RollResult.Critical_Success:
            self.apply_hanging_on(actor)
        else:
            if not actor.status_effects.is_affected_by(Unconscious):
                self.apply_hanging_on(actor)

    def assess_damage(self, actor_id, damage_taken):
        actor = self.being_model_manager[actor_id]

        curr_hp = actor.stats[StatType.CURR_HP.value]
        total_hp = actor.stats[StatType.HP.value]

        # If the actor is non-existent, no reason to track status changes.
        if actor.status_effects.is_affected_by(NonExistent):
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
        elif (-10 * total_hp) >= curr_hp:
            self.apply_non_existent(actor)

    def maintain_consciousness(self, actor_id):
        pass

    def regain_consciousness(self, actor_id):
        pass
