from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from repositories.data_models import Database
from repositories.data_models.grid import *


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Factory(
        Database,
        conn_str=config.connection_string
    )
