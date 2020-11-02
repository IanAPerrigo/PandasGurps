from dependency_injector import containers, providers
import uuid

from direct.directnotify.DirectNotify import DirectNotify

from data_models.entities.food import Food


class FoodModelContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("food_model")

    entity_id = providers.Factory(uuid.uuid4)
    model = providers.Factory(Food, entity_id=entity_id)
