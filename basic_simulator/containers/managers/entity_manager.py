from dependency_injector import containers, providers
import logging

from managers import entity_manager


class EntityModelManagerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="entity_model_manager")

    entity_model_manager = providers.Singleton(entity_manager.EntityModelManager)


class EntityFsmManagerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="entity_fsm_manager")

    entity_fsm_manager = providers.Singleton(entity_manager.EntityFsmManager)


class EntityComponentManagerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="entity_component_manager")

    entity_component_manager = providers.Singleton(entity_manager.EntityComponentManager,
                                                   entity_model_manager=EntityModelManagerContainer.entity_model_manager)
