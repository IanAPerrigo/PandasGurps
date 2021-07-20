from dependency_injector import containers, providers
from direct.directnotify.DirectNotify import DirectNotify

from containers.data_models import DataModels
from containers.data_models.terrain import TerrainDataModels
from containers.behaviors import Behaviors
from containers.utility import Rolls
from containers.trigger_resolvers import TriggerResolvers
from containers.components import Components, CoreComponents, DirectObjects, Fsm, Visual
from containers.managers import Managers
from containers.repositories import Repositories
from containers.action_resolvers import ActionResolvers, ManeuverResolvers
from containers.gui import GUI


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Singleton(
        DirectNotify
    )

    repositories = providers.Container(
        Repositories,
        config=config.repositories
    )

    terrain_data_models = providers.Container(
        TerrainDataModels,
        config=config.terrain_data_models
    )

    data_models = providers.Container(
        DataModels,
        config=config.data_models,
        repositories=repositories,
        terrain=terrain_data_models
    )

    behaviors = providers.Container(
        Behaviors,
        config=config.behaviors
    )

    managers = providers.Container(
        Managers,
        config=config.managers,
        data_models=data_models
    )

    trigger_resolvers = providers.Container(
        TriggerResolvers,
        config=config.trigger_resolvers,
        managers=managers
    )

    rolls = providers.Container(
        Rolls,
        #config=config.rolls
        managers=managers
    )

    action_resolvers = providers.Container(
        ActionResolvers,
        config=config.action_resolvers,
        managers=managers,
        rolls=rolls
    )

    maneuver_resolvers = providers.Container(
        ManeuverResolvers,
        managers=managers,
        action_resolvers=action_resolvers
    )

    # Components
    core = providers.Container(
        CoreComponents,
        config=config.core,
    )

    direct_objects = providers.Container(
        DirectObjects,
        config=config.direct_objects,
        managers=managers
    )

    fsms = providers.Container(
        Fsm,
        config=config.fsms,
        managers=managers,
        action_resolvers=action_resolvers
    )

    visual = providers.Container(
        Visual,
        config=config.visual,
        core=core,
        fsms=fsms,
        data_models=data_models,
        managers=managers
    )

    components = providers.Container(
        Components,
        config=config.components,
        data_models=data_models,
        managers=managers,
        action_resolvers=action_resolvers,
        behaviors=behaviors,
        fsms=fsms,
        visual=visual
    )

    gui = providers.Container(
        GUI,
        config=config.gui,
        core=core
    )
