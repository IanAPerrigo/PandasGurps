from . import *

from utility.rolling import *
from data_models.actions.action import ActionStatus
from events.component.actors import RefreshStats
from events import Event
from .decorators import require_consciousness, required_target
from .generic import ActionResolver


class MeleeAttackResolver(ActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(MeleeAttackResolver, self).__init__(simulation_manager)

        self.logger = logger

    @require_consciousness
    @required_target(explicit=False)
    # TODO: make proximity able to derive from active weapon.
    #@require_proximity(from_active_weapon=True)
    def resolve(self, action):
        # TODO: different specifications for the action will have different outcomes.
        #  e.g.
        #  - target with no location requires sight of the target
        #  - location / direction with no target will hit anything in that area (randomly or depending on Size modifier maybe)
        #  - location + target requires the actor to know the location of the target. this should be the most accurate
        #       (assuming the target is actually at that location)
        #
        dst_entities = None
        self.logger.info("Resolving combat:")

        """
        Targeting Phase
        NOTE: already handled by decorators.
        """
        selected_target = action.target_id
        self.logger.info("%s targeted %s." % (action.actor, selected_target))

        """
        Tooling Phase
        """
        # TODO: use explicitly defined tool for combat
        #  determine validity of the selection
        #  OR use default tool currently usable
        #  OR if ambiguous, fail

        attacker_model = self.simulation_manager.being_model_manager.get(action.actor)
        defender_model = self.simulation_manager.being_model_manager.get(selected_target)
        attacker_char_model = attacker_model
        defender_char_model = defender_model

        # TODO: STUB: ignore existing tooling and use hardcoded values
        attacker_hit_score = 10
        defender_defense_score = 8

        self.logger.info("Attacker hit score: %d" % attacker_hit_score)
        self.logger.info("Defender defense score: %d" % defender_defense_score)

        attacker_damage_descriptor = Roll(1, 6)

        """
        Combat Phase
        """
        # TODO: use tooling to build an attack roll
        #  query defender (blocking action) for defense type (start with dodge only to simplify)

        # TODO: Query module for different bonuses

        hit_roll = ContestRoll(attacker_hit_score)
        hit_result = hit_roll.contest()
        self.logger.info("Attacker rolling to hit (3d6): [%s] | %d" % (hit_result.value, hit_roll.last_result))

        if hit_result == ContestResults.Failure:
            """ TODO: Attack misses. event? """
        elif hit_result == ContestResults.Critical_Failure:
            """ TODO: critical miss table """
        elif hit_result == ContestResults.Critical_Success:
            """ TODO: perform critical hit """
        else:
            defense_roll = ContestRoll(defender_defense_score)
            defense_result = defense_roll.contest()

            self.logger.info("Defender rolling to defend (3d6): [%s] | %d" % (defense_result.value, defense_roll.last_result))
            if defense_result == ContestResults.Critical_Success:
                # TODO: cause attacker to critical miss
                action.status = ActionStatus.RESOLVED
                return
            elif defense_result == ContestResults.Success:
                # Attack misses.
                action.status = ActionStatus.RESOLVED
                return

            # Attack connects, calculate damage.
            attack_damage = attacker_damage_descriptor.roll()

            self.logger.info(
                "Attacker dealing damage (%s): %d" % (attacker_damage_descriptor.get_description(), attack_damage))

            defender_char_model.base_stats['CURR_HP'] -= attack_damage # TODO: brittle, replace with StatType ref

            Event.signal("actor_damaged", selected_target, attack_damage)
            RefreshStats.signal(defender_model.entity_id)

        action.status = ActionStatus.RESOLVED
