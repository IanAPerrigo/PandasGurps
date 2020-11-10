from dependency_injector import containers, providers

from utility.rolling.advanced import *
from utility.rolling import *


class Rolls(containers.DeclarativeContainer):
    config = providers.Configuration()
    managers = providers.DependenciesContainer()

    roll_versus = providers.Factory(
        RollVersus,
        being_model_manager=managers.being_model_manager
    )