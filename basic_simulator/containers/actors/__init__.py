from dependency_injector import containers, providers
import logging
import uuid

from containers.stats import StatContainer
from containers.managers.simulation_manager import SimulationManagerContainer
from data_models import actors
import components.actors as actor_components


class ActorConfig(containers.DeclarativeContainer):
    config = providers.Configuration('config')


context = ActorConfig.config.override({
    'model_file': 'models/simple_actor.x'
})


class ActorModel(containers.DeclarativeContainer):
    logger = providers.Singleton(logging.Logger, name="actor")

    entity_id = providers.Factory(uuid.uuid4)
    character_model = providers.Factory(actors.Character, stats=StatContainer.stat_set)
    actor_model = providers.Factory(actors.ActorModel, entity_id=entity_id, character_model=character_model, model_file=ActorConfig.config.model_file)


class ActorFsm(containers.DeclarativeContainer):
    logger = providers.Singleton(logging.Logger, name="actor")

    actor_fsm = providers.Factory(actor_components.ActorFSM, data_model=ActorModel.actor_model,
                                  simulation_manager=SimulationManagerContainer.simulation_manager)


class ActorNode(containers.DeclarativeContainer):
    actor = providers.Factory(actor_components.ActorComponent, data_model=ActorModel.actor_model)


class ActorContainer(containers.DeclarativeContainer):
    actor = providers.FactoryAggregate
