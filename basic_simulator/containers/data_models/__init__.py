from dependency_injector import containers, providers
from uuid import uuid4, uuid1

from data_models.grid.persistent_grid import DatabaseBackedGridModel
from data_models.grid.ephemeral_grid import SubjectiveGridModel
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
    repositories = providers.DependenciesContainer()

    #uuid = providers.Factory(uuid1)
    uuid = providers.Callable(get_id)

    grid_model_objective = providers.Singleton(
        DatabaseBackedGridModel,
        chunk_radius=config.grid.chunk_radius,
        procedural=config.grid.procedural,
        db=repositories.db
    )

    grid_model_subjective = providers.Factory(
        SubjectiveGridModel
    )

    being_model = providers.Factory(
        Being,
        entity_id=uuid
    )
