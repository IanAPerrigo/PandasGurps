import copy
from direct.showbase.DirectObject import DirectObject

from managers.entity_manager import EntityModelManager
from data_models.actors.status_effects.consciousness import *


class TurnManager:
    def __init__(self, entity_model_manager: EntityModelManager):
        self.entity_model_manager = entity_model_manager
        self._turn_order_by_id = []
        self._current_actor_iter = iter(self._turn_order_by_id)
        self._current_actor = None

    def generate_turn_order(self):
        self._turn_order_by_id.clear()
        for entity_id, entity in self.entity_model_manager.items():
            # TODO: determine who goes first based on speed, etc

            # Only add
            char_model = self.entity_model_manager[entity_id].character_model
            if DEAD not in char_model.status_effects:
                self._turn_order_by_id.append(entity_id)

        self._current_actor_iter = iter(self._turn_order_by_id)

    def advance_turn(self):
        self._current_actor = next(self._current_actor_iter, None)
        # TODO: Deprecated, handle the end of the round externally (also re-calling generate turn order)
        # if self._current_actor is None:
        #     self._current_actor_iter = iter(self._turn_order_by_id)
        #     self._current_actor = next(self._current_actor_iter, None)

    def get_turn_order(self):
        return copy.deepcopy(self._turn_order_by_id)

    def get_current_actor(self):
        return self._current_actor
