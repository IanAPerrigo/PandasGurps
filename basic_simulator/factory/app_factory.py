from multiprocessing.connection import Connection
from typing import NamedTuple

from direct.showbase.ShowBase import ShowBase

from app.panda_app import Panda3dApp
from components.main import GurpsMainFSM
from components.simulation.turn_management import TurnManagementFSM


class Panda3dAppFactoryState(NamedTuple):
    base: ShowBase
    panda_pipe: Connection
    turn_management_fsm: TurnManagementFSM
    gurps_main_fsm: GurpsMainFSM
    config: dict


class Panda3dAppFactory:
    def __init__(self, state: Panda3dAppFactoryState):
        self.state = state

    def build(self) -> Panda3dApp:
        return Panda3dApp(**self.state._asdict())
