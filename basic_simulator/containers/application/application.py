from dependency_injector import containers, providers

from containers.data_models import DataModels
from containers.components import Components
from containers.managers import Managers
from containers.action_resolvers import ActionResolvers
from containers.gui import GUI


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    data_models = providers.Container(
        DataModels,
        config=config.data_models
    )

    managers = providers.Container(
        Managers,
        config=config.managers,
        data_models=data_models
    )

    action_resolvers = providers.Container(
        ActionResolvers,
        config=config.managers,
        managers=managers
    )

    components = providers.Container(
        Components,
        config=config.components,
        managers=managers,
        action_resolvers=action_resolvers,
        data_models=data_models
    )

    gui = providers.Container(
        GUI,
        config=config.gui,
        components=components
    )
