import os
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from wx.core import wx, EVT_SHOW, ShowEvent, Panel

from app.panda_app import Panda3dApp
from factory.app_factory import Panda3dAppFactoryState, Panda3dAppFactory


class PandaViewport(Panel):
    """A special Panel which holds a Panda3d window."""

    def __init__(self, gui_pipe: Connection, panda_pipe: Connection, build_panda_app,
                 config: dict, *args, **kwargs):
        # wx.Panel.__init__(self, *args, **kwargs)
        # See __doc__ of initialize() for this callback
        super().__init__(*args, **kwargs)
        self.GetTopLevelParent().Bind(EVT_SHOW, self.onShow)
        self.pipe = gui_pipe
        self.panda_pipe = panda_pipe
        self.panda_process, self.pipe_timer = (None,) * 2
        self.build_panda_app = build_panda_app
        self.config = config

    def onShow(self, event: ShowEvent):
        if event.IsShown() and self.GetHandle():
            # Windows can't get it right from here. Call it after this function.
            if os.name == "nt":
                wx.CallAfter(self.initialize)
            # All other OSes should be okay with instant init.
            else:
                self.initialize()
        event.Skip()

    def initialize(self):
        """This method requires the top most window to be visible, i.e. you called Show()
        on it. Call initialize() after the whole Panel has been laid out and the UI is mostly done.
        It will spawn a new process with a new Panda3D window and this Panel as parent.
        """
        assert self.GetHandle() != 0
        w, h = self.GetClientSize().GetWidth(), self.GetClientSize().GetHeight()
        self.panda_process = Process(target=self.build_panda_app,
                                     args=(self.config, self.GetHandle(), self.panda_pipe))
        self.panda_process.start()

        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(wx.EVT_KILL_FOCUS, self.onDefocus)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy)
        self.SetFocus()

        # We need to check the pipe for requests frequently
        self.pipe_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.checkPipe, self.pipe_timer)
        self.pipe_timer.Start(1000.0 / 60)  # 60 times a second

    def onResize(self, event):
        # when the wx-panel is resized, fit the panda3d window into it
        w, h = event.GetSize().GetWidth(), event.GetSize().GetHeight()
        self.pipe.send(["resize", w, h])

    def onDefocus(self, event):
        f = wx.Window.FindFocus()
        if f:
            # This makes Panda lose keyboard focus
            f.GetTopLevelParent().Raise()

    def onDestroy(self, event):
        self.pipe.send(["close", ])
        # Give Panda a second to close itself and terminate it if it doesn't
        self.panda_process.join(1)
        if self.panda_process.is_alive():
            self.panda_process.terminate()

    def checkPipe(self, event):
        # Panda requested focus (and probably already has keyboard focus), so make wx
        # set it officially. This prevents other widgets from being rendered focused.
        if self.pipe.poll():
            request = self.pipe.recv()
            if request == "focus":
                self.SetFocus()
