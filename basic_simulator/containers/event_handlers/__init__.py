from dependency_injector import containers, providers
import logging
import uuid

from direct.directnotify.DirectNotify import DirectNotify

from containers.managers.entity_manager import EntityModelManagerContainer
from event_handlers import status_effects
import components.actors as actor_components


class ConsciousnessHandlerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("consciousness_handler")

    consciousness_handler = providers.Singleton(
        status_effects.ConsciousnessHandler,
        entity_model_manager=EntityModelManagerContainer.entity_model_manager, logger=logger)
