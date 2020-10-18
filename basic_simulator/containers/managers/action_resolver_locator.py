from dependency_injector import containers, providers
import logging

from managers import action_resolver_locator


class ActionResolverLocatorContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="action_resolver_locator")

    action_resolver_locator = providers.Singleton(action_resolver_locator.ActionResolverLocator,
                                                  resolvers_for_type=config)
