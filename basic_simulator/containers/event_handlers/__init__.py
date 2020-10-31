from dependency_injector import containers, providers
import logging
import uuid

from direct.directnotify.DirectNotify import DirectNotify

from containers.managers.entity_manager import BeingModelManagerContainer
from event_handlers import consciousness
import components.actors as actor_components


class ConsciousnessHandlerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("consciousness_handler")

    consciousness_handler = providers.Singleton(
        consciousness.ConsciousnessHandler,
        being_model_manager=BeingModelManagerContainer.being_model_manager, logger=logger)
