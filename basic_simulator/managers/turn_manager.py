import copy
from direct.showbase.DirectObject import DirectObject

from managers.entity_manager import EntityModelManager


class TurnManager:
    def __init__(self, entity_model_manager: EntityModelManager):
        self.entity_model_manager = entity_model_manager
        self._turn_order_by_id = []
        self._current_actor_iter = iter(self._turn_order_by_id)
        self._current_actor = None

    def generate_turn_order(self):
        self._turn_order_by_id.clear()
        for entity_id, entity in self.entity_model_manager.items():
            # TODO: delegate to another service the determination of turn order.
            #  (Service will check Basic Speed, manage ties, etc)
            self._turn_order_by_id.append(entity_id)

    def advance_turn(self):
        self._current_actor = next(self._current_actor_iter, None)
        if self._current_actor is None:
            self._current_actor_iter = iter(self._turn_order_by_id)
            self._current_actor = next(self._current_actor_iter, None)

    def get_turn_order(self):
        return copy.deepcopy(self._turn_order_by_id)

    def get_current_actor(self):
        return self._current_actor
