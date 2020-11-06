from dependency_injector import containers, providers

from managers.simulation_manager import SimulationStateManager
from managers.entity_manager import EntityComponentManager, EntityModelManager, EntityFsmManager, BeingModelManager
from managers.action_manager import ActionManager
from managers.turn_manager import TurnManager
from managers.interaction_event_manager import InteractionEventManager
from managers.tick_manager import TickManager
from managers.status_effect_manager import StatusEffectManager


class Managers(containers.DeclarativeContainer):
    config = providers.Configuration()
    data_models = providers.DependenciesContainer()

    interaction_event_manager = providers.Singleton(
        InteractionEventManager,
        event_types=config.interaction.event_types
    )

    entity_model_manager = providers.Singleton(EntityModelManager)
    entity_fsm_manager = providers.Singleton(EntityFsmManager)
    being_model_manager = providers.Singleton(BeingModelManager)
    entity_component_manager = providers.Singleton(
        EntityComponentManager,
        entity_model_manager=entity_model_manager,
        entity_fsm_manager=entity_fsm_manager,
        being_model_manager=being_model_manager
    )

    turn_manager = providers.Singleton(
        TurnManager,
        entity_model_manager=entity_model_manager
    )

    action_manager = providers.Singleton(ActionManager)

    simulation_manager = providers.Singleton(
        SimulationStateManager,
        grid_model=data_models.grid_model_objective,
        entity_component_manager=entity_component_manager,
        action_manager=action_manager,
        grid_factory=data_models.grid_model_subjective.provider
    )

    status_effect_manager = providers.Singleton(
        StatusEffectManager,
        simulation_manager=simulation_manager
    )

    tick_manager = providers.Singleton(
        TickManager,
        status_effect_manager=status_effect_manager,
        tick_value=config.tick_manager.tick_value,
        tick_rate=config.tick_manager.tick_rate
    )
