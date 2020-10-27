from dependency_injector import containers, providers

from direct.directnotify.DirectNotify import DirectNotify

import components.simulation.turn_management as turn_management
from containers.managers import TurnManagerContainer, SimulationManagerContainer, GenericResolverContainer, \
    EntityFsmManagerContainer, InteractionEventManagerContainer


class TurnManagementFsmContainer(containers.DeclarativeContainer):
    logger= DirectNotify().newCategory("turn_management_fsm")

    turn_management_fsm = providers.Singleton(turn_management.TurnManagementFSM,
                                              turn_manager=TurnManagerContainer.turn_manager,
                                              action_resolver=GenericResolverContainer.resolver,
                                              simulation_manager=SimulationManagerContainer.simulation_manager,
                                              entity_fsm_manager=EntityFsmManagerContainer.entity_fsm_manager,
                                              interaction_event_manager=InteractionEventManagerContainer.interaction_event_manager,
                                              logger=logger)
