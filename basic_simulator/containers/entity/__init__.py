from dependency_injector import containers, providers
import uuid

from direct.directnotify.DirectNotify import DirectNotify

from data_models.entities.being import Being


class BeingModelContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("actor_model")

    entity_id = providers.Factory(uuid.uuid4)
    model = providers.Factory(Being, entity_id=entity_id)
