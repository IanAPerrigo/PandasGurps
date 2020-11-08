from uuid import UUID
from managers.simulation_manager import SimulationStateManager
from data_models.entities.status_effects.status_effect import StatusEffect


class StatusEffectManager:
    def __init__(self, simulation_manager: SimulationStateManager):
        self.simulation_manager = simulation_manager

        # UUID to list mapping of
        self.new_status_effects = {}

    def add_status_effect_to_entity(self, entity_id: UUID, status_effect: StatusEffect):
        if entity_id not in self.new_status_effects:
            self.new_status_effects[entity_id] = list()

        entity = self.simulation_manager.entity_model_manager.get(entity_id)
        entity.add_status_effect(status_effect)
        self.new_status_effects[entity_id].append(status_effect)

    def remove_status_effect_from_entity(self, entity_id: UUID, status_effect: StatusEffect):
        entity = self.simulation_manager.entity_model_manager.get(entity_id)
        entity.remove_status_effect(status_effect)
        if entity_id in self.new_status_effects and status_effect in self.new_status_effects[entity_id]:
            self.new_status_effects[entity_id].remove(status_effect)

    def remove_all_status_effects_from_entity(self, entity_id, status_type: type):
        entity = self.simulation_manager.entity_model_manager.get(entity_id)
        for status_effect in filter(lambda se: isinstance(se, status_type), entity.status_effects):
            if entity_id in self.new_status_effects and status_effect in self.new_status_effects[entity_id]:
                self.new_status_effects[entity_id].remove(status_effect)

    def bootstrap_status_effects(self, tick, time_scale):
        # Bootstrap all new status effects
        for entity_id, status_effects in self.new_status_effects.items():
            for status_effect in status_effects:
                status_effect.bootstrap(tick, time_scale)

        self.new_status_effects.clear()

    def tick_status_effects(self, tick, time_scale):
        for entity_id, model in self.simulation_manager.entity_model_manager.items():
            # Filter status effects requiring tick, and apply the tick.
            statuses_requiring_tick = list(filter(lambda se: se.active and se.next_relevant_tick <= tick,
                                                  model.status_effects.items()))
            for se in statuses_requiring_tick:
                se.update_tick(tick, time_scale)

            # Gather and cleanup the deactivated statuses.
            deactivated_statuses = filter(lambda se: not se.active, model.status_effects.items())
            for se in deactivated_statuses:
                self.remove_status_effect_from_entity(entity_id, se)
