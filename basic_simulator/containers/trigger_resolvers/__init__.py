from dependency_injector import containers, providers
from direct.directnotify.DirectNotify import DirectNotify

from managers.trigger_resolvers.status_effects.starvation_trigger_resolver import StarvationTriggerResolver
from managers.trigger_resolvers.status_effects.dehydration_trigger_resolver import DehydrationTriggerResolver


def stub_get_resolver():
    raise Exception("This stub needs to be overwritten.")


class TriggerResolvers(containers.DeclarativeContainer):
    config = providers.Configuration()
    managers = providers.DependenciesContainer()

    logger = providers.Singleton(
        DirectNotify
    )

    starvation_trigger_resolver = providers.Singleton(
        StarvationTriggerResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )

    dehydrated_trigger_resolver = providers.Singleton(
        DehydrationTriggerResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )
