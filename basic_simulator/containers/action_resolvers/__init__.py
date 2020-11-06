from dependency_injector import containers, providers

from managers.action_resolvers.generic import GenericActionResolver
from managers.action_resolvers.movement import MovementResolver


class ActionResolvers(containers.DeclarativeContainer):
    config = providers.Configuration()
    managers = providers.DependenciesContainer()

    generic_action_resolver = providers.Singleton(
        GenericActionResolver,
        resolvers_for_type=config.resolver_locator.resolvers_for_type,
        simulation_manager=managers.simulation_manager
    )

    movement_action_resolver = providers.Singleton(
        MovementResolver,
        simulation_manager=managers.simulation_manager
    )
