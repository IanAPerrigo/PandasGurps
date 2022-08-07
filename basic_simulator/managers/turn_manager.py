import copy

from data_models.entities.stats import SecondaryStats
from managers.entity_manager import EntityModelManager
from data_models.entities.being import Being
from data_models.entities.status_effects.consciousness import *


class TurnManager:
    def generate_order_from_model(self, actor: Being):
        # TODO: can make this more complex later
        return actor.stats.get(SecondaryStats.SPD), actor

    def generate_turn_order(self, entity_model_manager: EntityModelManager):
        alive_actors = filter(lambda e: isinstance(e[1], Being) and not e[1].status_effects.is_affected_by(Dead),
                              entity_model_manager.items())

        turn_score = map(self.generate_order_from_model, alive_actors)
        return tuple(map(lambda score_actor: score_actor[1], sorted(turn_score, key=lambda tup: tup[0])))

    def advance_turn(self, turn_state: tuple):
        return turn_state[1:]

# DEPRECATED turn manager
# class TurnManager:
#     def __init__(self, entity_model_manager: EntityModelManager):
#         self.entity_model_manager = entity_model_manager
#         self._turn_order_by_id = []
#         self._current_actor_iter = iter(self._turn_order_by_id)
#         self._current_actor = None
#
#     def generate_turn_order(self):
#         self._turn_order_by_id.clear()
#
#         actors = filter(lambda e: isinstance(e[1], Being), self.entity_model_manager.items())
#         for entity_id, model in actors:
#
#             # TODO: determine who goes first based on speed, etc
#
#             # Only add
#             if not model.status_effects.is_affected_by(Dead):
#                 self._turn_order_by_id.append(entity_id)
#
#         self._current_actor_iter = iter(self._turn_order_by_id)
#
#     def advance_turn(self):
#         self._current_actor = next(self._current_actor_iter, None)
#         # TODO: Deprecated, handle the end of the round externally (also re-calling generate turn order)
#         # if self._current_actor is None:
#         #     self._current_actor_iter = iter(self._turn_order_by_id)
#         #     self._current_actor = next(self._current_actor_iter, None)
#
#     def get_turn_order(self):
#         return copy.deepcopy(self._turn_order_by_id)
#
#     def get_current_actor(self):
#         return self._current_actor
