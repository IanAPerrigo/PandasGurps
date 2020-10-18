from dependency_injector import containers, providers
import logging
import uuid

from containers.managers.entity_manager import EntityComponentManagerContainer
from data_models import grid
from components.grid import GridComponent


class GridConfig(containers.DeclarativeContainer):
    config = providers.Configuration('config')


class GridModel(containers.DeclarativeContainer):
    logger = providers.Singleton(logging.Logger, name="grid")

    grid_model = providers.Factory(grid.GridModel, x_size=GridConfig.config.x_size, y_size=GridConfig.config.y_size)


class GridNode(containers.DeclarativeContainer):
    grid = providers.Factory(GridComponent,
                             data_model=GridModel.grid_model,
                             entity_component_manager=EntityComponentManagerContainer.entity_component_manager)
