from dependency_injector import containers, providers

from behaviors.actors import HumanPlayerBehavior
from behaviors.actors.ai import AiBehavior


class Behaviors(containers.DeclarativeContainer):
    config = providers.Configuration()

    human = providers.Factory(
        HumanPlayerBehavior
    )

    ai = providers.Factory(
        AiBehavior
    )