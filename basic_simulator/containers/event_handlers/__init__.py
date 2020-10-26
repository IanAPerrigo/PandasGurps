from dependency_injector import containers, providers
import logging
import uuid

from direct.directnotify.DirectNotify import DirectNotify

from containers.managers.entity_manager import EntityModelManagerContainer
from event_handlers import status_effects
import components.actors as actor_components


class FatalDamageHandlerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("fatal_damage_handler")

    fatal_damage_handler = providers.Singleton(
        status_effects.FatalDamageHandler,
        entity_model_manager=EntityModelManagerContainer.entity_model_manager, logger=logger)
