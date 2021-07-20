from dependency_injector import containers, providers
from direct.directnotify.DirectNotify import DirectNotify

from data_models.triggers.status_effects.energy import *

from managers.trigger_resolvers.status_effects.starvation_trigger_resolver import StarvationTriggerResolver
from managers.trigger_resolvers.status_effects.dehydration import *


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

    daily_dehydrated_trigger_resolver = providers.Singleton(
        DailyDehydrationTriggerResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )

    eight_hour_dehydrated_trigger_resolver = providers.Singleton(
        EightHourDehydrationTriggerResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )
