from dependency_injector import containers, providers

from direct.directnotify.DirectNotify import DirectNotify

from managers import action_resolvers
from managers.action_resolvers import movement as movement_resolvers
from managers.action_resolvers import combat as combat_resolvers
from managers.action_resolvers.maneuvers import move as movement_maneuver_resolvers

from containers.managers.simulation_manager import SimulationManagerContainer
from containers.managers.action_resolver_locator import ActionResolverLocatorContainer


class GenericResolverContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("generic_resolver")

    resolver = providers.Singleton(action_resolvers.GenericActionResolver,
                                   action_resolver_locator=ActionResolverLocatorContainer.action_resolver_locator,
                                   simulation_manager=SimulationManagerContainer.simulation_manager)


class MovementResolverContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("movement_resolver")

    resolver = providers.Singleton(movement_resolvers.MovementResolver, logger=logger)


class MeleeAttackResolverContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("melee_attack_resolver")

    resolver = providers.Singleton(combat_resolvers.MeleeAttackResolver, logger=logger)


class MoveManeuverResolverContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = DirectNotify().newCategory("movement_maneuver_resolver")

    resolver = providers.Singleton(movement_maneuver_resolvers.MoveManeuverResolver, logger=logger,
                                   generic_resolver=GenericResolverContainer.resolver)
