from dependency_injector import containers, providers
import logging

from managers import turn_manager
from containers import managers


class TurnManagerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="entity_component_manager")

    turn_manager_manager = providers.Singleton(turn_manager.TurnManager,
                                               entity_model_manager=managers.EntityModelManagerContainer.entity_model_manager)
