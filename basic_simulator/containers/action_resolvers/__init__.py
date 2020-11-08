from dependency_injector import containers, providers
from direct.directnotify.DirectNotify import DirectNotify

from managers.action_resolvers.generic import GenericActionResolver
from managers.action_resolvers.movement import MovementResolver
from managers.action_resolvers.combat import MeleeAttackResolver
from managers.action_resolvers.food import HarvestResolver, EatResolver
from managers.action_resolvers.maneuvers.move import MoveManeuverResolver
from managers.action_resolvers.maneuvers.move_attack import MoveAttackManeuverResolver
from managers.action_resolvers.maneuvers.yield_turn import YieldTurnManeuverResolver

from data_models.actions import *
from data_models.actions.maneuvers import *


def stub_get_resolver():
    raise Exception("This stub needs to be overwritten.")


class ActionResolvers(containers.DeclarativeContainer):
    config = providers.Configuration()
    managers = providers.DependenciesContainer()

    logger = providers.Singleton(
        DirectNotify
    )

    get_resolver = providers.Callable(stub_get_resolver)

    generic_action_resolver = providers.Singleton(
        GenericActionResolver,
        resolvers_for_type=get_resolver,
        simulation_manager=managers.simulation_manager
    )

    movement_resolver = providers.Singleton(
        MovementResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )

    melee_attack_resolver = providers.Singleton(
        MeleeAttackResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )

    harvest_resolver = providers.Singleton(
        HarvestResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )

    eat_resolver = providers.Singleton(
        EatResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )


class ManeuverResolvers(containers.DeclarativeContainer):
    config = providers.Configuration()
    managers = providers.DependenciesContainer()
    action_resolvers = providers.DependenciesContainer()
    logger = providers.Singleton(
        DirectNotify
    )

    movement_resolver = providers.Singleton(
        MoveManeuverResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger,
        generic_resolver=action_resolvers.generic_action_resolver
    )

    move_attack_resolver = providers.Singleton(
        MoveAttackManeuverResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger,
        generic_resolver=action_resolvers.generic_action_resolver
    )

    yield_turn_resolver = providers.Singleton(
        YieldTurnManeuverResolver,
        simulation_manager=managers.simulation_manager,
        logger=logger,
        generic_resolver=action_resolvers.generic_action_resolver
    )