from dependency_injector import containers, providers
import logging

from managers import action_manager


class ActionManagerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="action_manager")

    action_manager = providers.Singleton(action_manager.ActionManager)
