from . import SimulationStateManager, ActionResolver, np

from utility.rolling import *
from events.component.actors import RefreshStats
from events import Event


class MeleeAttackResolver(ActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(MeleeAttackResolver, self).__init__(simulation_manager)

        self.logger = logger

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
        if action.direction is not None:
            actor_loc = self.simulation_manager.grid_model.get_loc_of_obj(action.actor)
            dst_loc = np.add(action.direction.value, actor_loc)
            dst_entities = self.simulation_manager.grid_model.get_at_loc(dst_loc)
        elif action.location is not None:
            dst_entities = self.simulation_manager.grid_model.get_at_loc(action.location)
        else:
            # TODO: resolving error. Cant specify just a target (maybe?)
            #  Log?
            self.logger.warn("No target found.")
            return

        """
        Targeting Phase
        """
        selected_target = None
        # If the target was specified, determine if it is in the location specified.
        if action.target_id is not None and dst_entities is not None and len(dst_entities) != 0:
            valid_target = action.target_id in dst_entities

            if valid_target:
                # TODO: determine if target is in sight.
                """"""

            selected_target = valid_target
        # No target specified, pick any of the targets in the destination.
        elif action.target_id is None and dst_entities is not None and len(dst_entities) != 0:
            selected_target = random.choice(dst_entities)

        self.logger.info("%s targeted %s." % (action.actor, selected_target))

        if selected_target is not None:
            """
            Tooling Phase
            """
            # TODO: use explicitly defined tool for combat
            #  determine validity of the selection
            #  OR use default tool currently usable
            #  OR if ambiguous, fail

            attacker_model = self.simulation_manager.entity_model_manager.get(action.actor)
            defender_model = self.simulation_manager.entity_model_manager.get(selected_target)
            attacker_char_model = attacker_model.character_model
            defender_char_model = defender_model.character_model

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
                # TODO: Attack misses. event?
                return
            elif hit_result == ContestResults.Critical_Failure:
                # TODO: critical miss table
                return
            elif hit_result == ContestResults.Critical_Success:
                # TODO: perform critical hit
                return
            else:
                defense_roll = ContestRoll(defender_defense_score)
                defense_result = defense_roll.contest()

                self.logger.info("Defender rolling to defend (3d6): [%s] | %d" % (defense_result.value, defense_roll.last_result))
                if defense_result == ContestResults.Critical_Success:
                    # TODO: cause attacker to critical miss
                    return
                elif defense_result == ContestResults.Success:
                    # Attack misses.
                    return

                # Attack connects, calculate damage.
                attack_damage = attacker_damage_descriptor.roll()

                self.logger.info(
                    "Attacker dealing damage (%s): %d" % (attacker_damage_descriptor.get_description(), attack_damage))

                defender_char_model.stats['CURR_HP'] -= attack_damage # TODO: brittle, replace with StatType ref

                Event.signal("actor_damaged", selected_target, attack_damage)

                # TODO: apply damage ( as an event?)
                # TODO: emit an event (to update display and determine if anything died


                # todo: replace with a more proper event that doesnt reference the stats update directly (more like a "deal damage" event)
                RefreshStats.signal(defender_model.entity_id)

            return
        else:
            # TODO: log?
            return

