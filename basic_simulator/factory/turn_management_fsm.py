from typing import NamedTuple

from direct.showbase.ShowBase import ShowBase

from components.camera.camera import Camera
from components.simulation.turn_management import TurnManagementFSM
from managers import SimulationStateManager, EntityFsmManager
from managers.action_resolvers.generic import GenericActionResolver
from managers.entity_manager import EntityModelManager
from managers.interaction_event_manager import InteractionEventManager
from managers.tick_manager import TickManager
from managers.turn_manager import TurnManager


class TurnManagementFSMFactoryState(NamedTuple):
    turn_manager: TurnManager
    action_resolver: GenericActionResolver
    simulation_manager: SimulationStateManager
    entity_fsm_manager: EntityFsmManager
    entity_model_manager: EntityModelManager
    interaction_event_manager: InteractionEventManager
    tick_manager: TickManager
    logger: object


class TurnManagementFSMFactory:
    def __init__(self, state):
        self.state = state

    def build(self) -> TurnManagementFSM:
        return TurnManagementFSM(
            turn_manager=self.state.turn_manager,
            action_resolver=self.state.action_resolver,
            simulation_manager=self.state.simulation_manager,
            entity_fsm_manager=self.state.entity_fsm_manager,
            entity_model_manager=self.state.entity_model_manager,
            interaction_event_manager=self.state.interaction_event_manager,
            tick_manager=self.state.tick_manager,
            logger=self.state.logger
        )
