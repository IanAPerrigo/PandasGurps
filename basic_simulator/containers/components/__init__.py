from dependency_injector import containers, providers
import logging
import uuid

from direct.directnotify.DirectNotify import DirectNotify

import data_models.entities.entity
from containers.stats import StatContainer
from containers.managers.simulation_manager import SimulationManagerContainer
from containers.managers.action_resolver import GenericResolverContainer
from containers.entity import BeingModelContainer
import components.actors as actor_components


class ActorFsmContainer(containers.DeclarativeContainer):
    logger = providers.Singleton(logging.Logger, name="actor")

    actor_fsm = providers.Factory(actor_components.ActorFSM, data_model=BeingModelContainer.model,
                                  simulation_manager=SimulationManagerContainer.simulation_manager,
                                  action_resolver=GenericResolverContainer.resolver)


class ActorComponentContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')

    actor = providers.Factory(actor_components.ActorComponent, data_model=BeingModelContainer.model, model_file=config.model_file)


ActorComponentContainer.config.override({
    'model_file': 'models/player.obj'
})
