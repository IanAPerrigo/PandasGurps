import logging

from dependency_injector import containers, providers

from containers.components.entities.generic import GenericComponentContainer
from containers.managers.action_resolver import GenericResolverContainer
from containers.managers.simulation_manager import SimulationManagerContainer
from containers.entity.being import BeingModelContainer
from components.entities import actors as actor_components


class ActorFsmContainer(containers.DeclarativeContainer):
    logger = providers.Singleton(logging.Logger, name="actor")

    fsm = providers.Factory(actor_components.ActorFSM,
                            data_model=BeingModelContainer.model,
                            simulation_manager=SimulationManagerContainer.simulation_manager,
                            action_resolver=GenericResolverContainer.resolver)


class ActorComponentContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')

    component = providers.Factory(actor_components.ActorComponent,
                                  parent=GenericComponentContainer.entity_component_config.parent,
                                  data_model=BeingModelContainer.model,
                                  model_file=config.model_file)


# Set the default model to something simple.
ActorComponentContainer.config.override({
    'model_file': 'models/player.obj'
})
