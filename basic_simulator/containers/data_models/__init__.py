from dependency_injector import containers, providers
from uuid import uuid4

from data_models.grid import GridModel
from data_models.entities.being import Being


class DataModels(containers.DeclarativeContainer):
    config = providers.Configuration()

    uuid = providers.Factory(uuid4)

    grid_model_objective = providers.Singleton(
        GridModel,
        x_size=config.grid.x_size,
        y_size=config.grid.y_size
    )

    grid_model_subjective = providers.Factory(
        GridModel,
        x_size=config.grid.x_size,
        y_size=config.grid.y_size
    )

    being_model = providers.Factory(
        Being,
        entity_id=uuid
    )
