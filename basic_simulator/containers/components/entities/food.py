import logging

from dependency_injector import containers, providers

from containers.components.entities.generic import GenericComponentContainer
from containers.entity.food import FoodModelContainer
from components.entities.food import simple_meal as food_components


class BasicMealComponentContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')

    component = providers.Factory(food_components.BasicMealComponent,
                                  parent=GenericComponentContainer.entity_component_config.parent,
                                  data_model=FoodModelContainer.model)
