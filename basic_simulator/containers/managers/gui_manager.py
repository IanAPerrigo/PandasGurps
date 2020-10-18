from dependency_injector import containers, providers
import logging

from managers import interaction_event_manager


class InteractionEventManagerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="interaction_event_manager")

    interaction_event_manager = providers.Singleton(interaction_event_manager.InteractionEventManager,
                                                    event_types=config.event_types)
