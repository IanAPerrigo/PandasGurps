import sys
from multiprocessing.connection import Connection

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import loadPrcFileData, WindowProperties

from components.main import GurpsMainFSM
from components.simulation.turn_management import TurnManagementFSM


class Panda3dApp(object):
    def __init__(self, base: ShowBase, panda_pipe: Connection, turn_management_fsm: TurnManagementFSM,
                 gurps_main_fsm: GurpsMainFSM, config: dict):
        self.pipe = panda_pipe
        self.base = base

        # Configure window size inside the GUI
        loadPrcFileData("", "window-type none")
        loadPrcFileData("", "audio-library-name null")

        height, width = config.get("width"), config.get("height")

        self.wp = WindowProperties()
        self.wp.setOrigin(0, 0)
        self.wp.setSize(width, height)


        self.turn_fsm = turn_management_fsm

        # Request the main FSM to take over.
        self.gurps_main_fsm = gurps_main_fsm
        self.gurps_main_fsm.request('PlayAreaLoad')

    def run(self, window_handle):
        self.wp.setParentWindow(window_handle)
        self.base.openDefaultWindow(props=self.wp, gsg=None)

        # Schedule a task to query the GUI event pipe
        self.base.taskMgr.add(self.checkPipe, "check pipe")

        self.base.accept("mouse1-up", self.getFocus)
        self.base.run()

    def getFocus(self):
        """Bring Panda3d to foreground, so that it gets keyboard focus.
        Also send a message to wx, so that it doesn't render a widget focused.
        We also need to say wx that Panda now has focus, so that it can notice when
        to take focus back.
        """
        wp = WindowProperties()
        # This causes warnings on Windows
        # wp.setForeground(True)
        self.base.win.requestProperties(wp)
        self.pipe.send("focus")

    def resizeWindow(self, width, height):
        old_wp = self.base.win.getProperties()
        if old_wp.getXSize() == width and old_wp.getYSize() == height:
            return
        wp = WindowProperties()
        wp.setOrigin(0, 0)
        wp.setSize(width, height)
        self.base.win.requestProperties(wp)

    def checkPipe(self, task):
        """This task is responsible for executing actions requested by wxWidgets.
        Currently supported requests with params:
        resize, width, height
        close
        """
        # TODO: only use the last request of a type
        #       e.g. from multiple resize requests take only the latest into account
        while self.pipe.poll():
            request = self.pipe.recv()
            if request[0] == "resize":
                self.resizeWindow(request[1], request[2])
            elif request[0] == "close":
                sys.exit()
        return Task.cont
