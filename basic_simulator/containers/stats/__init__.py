from dependency_injector import containers, providers
import logging

from data_models import stats


class StatContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="stat")

    stat_set = providers.Factory(stats.StatSet)
