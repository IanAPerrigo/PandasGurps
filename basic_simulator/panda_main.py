import logging
from multiprocessing import Pipe

from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.ShowBase import ShowBase
from wx.core import wx, App, FlexGridSizer, Size

from app.panda_app import Panda3dApp
from components.gui.panda_viewport.panda_viewport import PandaViewport

import dependency_injection_config
from data_models.actions import MovementAction, MovementType
from factory import turn_management_fsm
from factory.app_factory import Panda3dAppFactory, Panda3dAppFactoryState
from factory.generic_action_resolver_factory import ActionResolverFactory, ActionResolverFactoryState, \
    GenericActionResolverFactory, GenericActionResolverFactoryState
from factory.gurps_main_fsm import GurpsMainFSMFactory, GurpsMainFSMFactoryState
from factory.turn_management_fsm import TurnManagementFSMFactoryState, TurnManagementFSMFactory
from managers import EntityFsmManager, BeingModelManager, EntityModelManager
from managers.action_resolvers.movement import MovementResolver
from managers.tick_manager import TickManager
from managers.turn_manager import TurnManager


def build_ui(build_panda_app, config: dict) -> App:
    # Threading
    gui_pipe, panda_pipe = Pipe()

    app = wx.App(redirect=False)
    frame = wx.Frame(parent=None, size=wx.Size(1000, 1000))
    p = PandaViewport(parent=frame, build_panda_app=build_panda_app, panda_pipe=panda_pipe, gui_pipe=gui_pipe,
                      config=config)
    t = wx.TextCtrl(parent=frame)
    gap = Size(10, 10)
    sizer = FlexGridSizer(2, 2, gap)  # two rows, one column
    sizer.AddGrowableRow(0)  # make first row growable
    sizer.AddGrowableCol(0)  # make first column growable
    sizer.SetFlexibleDirection(wx.BOTH)
    sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
    sizer.Add(p, flag=wx.EXPAND)
    sizer.Add(t, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Show()
    return app


def build_panda_app(config: dict, window_handle, panda_pipe):
    # Create pure state containers
    being_model_manager = BeingModelManager()
    entity_model_manager = EntityModelManager()
    entity_fsm_manager = EntityFsmManager()

    # Action Resolvers
    movement_resolver_factory_state = ActionResolverFactoryState(resolver_type=MovementResolver,
                                                                 sub_state={"simulation_manager": None, "logger": None})
    movement_resolver_factory = ActionResolverFactory(
        movement_resolver_factory_state)

    # TODO: more resolvers

    generic_resolver_factory_state = GenericActionResolverFactoryState(
        resolvers_for_type={MovementAction: movement_resolver_factory})
    generic_resolver_factory = GenericActionResolverFactory(
        generic_resolver_factory_state)

    generic_resolver = generic_resolver_factory.build()

    # State managers
    turn_manager = TurnManager()
    tick_manager = TickManager(tick_value=config["managers"]["tick_manager"]["tick_value"],
                               tick_rate=config["managers"]["tick_manager"]["tick_rate"])

    # Impure state managers
    # TODO: make pure:

    # Create showbase
    base = ShowBase()
    direct_notify_logger = DirectNotify()

    tm_fsm_state = TurnManagementFSMFactoryState(turn_manager=turn_manager, action_resolver=generic_resolver,
                                                 simulation_manager=None,
                                                 entity_fsm_manager=entity_fsm_manager,
                                                 entity_model_manager=entity_model_manager,
                                                 interaction_event_manager=None,
                                                 tick_manager=tick_manager,
                                                 logger=direct_notify_logger)
    tm_fsm = TurnManagementFSMFactory(tm_fsm_state).build()

    gurps_main_state = GurpsMainFSMFactoryState(turn_management_fsm=tm_fsm, character_creator=None,
                                                logger=direct_notify_logger)
    gurps_main = GurpsMainFSMFactory(gurps_main_state).build()

    panda_app_state = Panda3dAppFactoryState(base=base, turn_management_fsm=tm_fsm, gurps_main_fsm=gurps_main,
                                             panda_pipe=panda_pipe,
                                             config=config['core']['app'])

    panda_app = Panda3dAppFactory(panda_app_state).build()
    panda_app.run(window_handle)


def run_app():
    # Config
    config = dependency_injection_config.config_dict

    # Build the GUI and start the application
    ui_app = build_ui(config=config, build_panda_app=build_panda_app)
    ui_app.MainLoop()
