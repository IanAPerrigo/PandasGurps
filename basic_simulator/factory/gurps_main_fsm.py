from typing import NamedTuple

from components.main import GurpsMainFSM
from components.simulation.turn_management import TurnManagementFSM
from components.event_handlers.character_creation import CharacterCreator


class GurpsMainFSMFactoryState(NamedTuple):
    turn_management_fsm: TurnManagementFSM
    character_creator: CharacterCreator
    logger: object


class GurpsMainFSMFactory:
    def __init__(self, state: GurpsMainFSMFactoryState):
        self.state = state

    def build(self) -> GurpsMainFSM:
        return GurpsMainFSM(**self.state._asdict())
