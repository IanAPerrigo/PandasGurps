from dependency_injector import containers, providers

from behaviors.actors import HumanPlayerBehavior


class Behaviors(containers.DeclarativeContainer):
    config = providers.Configuration()

    human = providers.Factory(
        HumanPlayerBehavior
    )
