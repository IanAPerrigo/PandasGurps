from dependency_injector import containers, providers
from uuid import uuid4, uuid1

from data_models.grid import GridModel
from data_models.entities.being import Being

id_num = 0
def get_id():
    global id_num
    if id_num is None:
        id_num = 0
    i = id_num
    id_num += 1
    return i


class DataModels(containers.DeclarativeContainer):
    config = providers.Configuration()

    #uuid = providers.Factory(uuid1)
    uuid = providers.Callable(get_id)

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
