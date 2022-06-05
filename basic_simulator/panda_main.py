from dependency_injector import providers
from dependency_injector.wiring import Provide

from direct.showbase.ShowBase import ShowBase
from direct.showbase.MessengerGlobal import messenger

import containers.application.application as app_containers
from components.camera.camera import Lighting, Camera
from components.simulation.turn_management import TurnManagementFSM
from components.event_handlers.consciousness import ConsciousnessHandler
from components.grid.grid import GridComponent
from components.main import GurpsMain

from events import Event
from managers.simulation_manager import SimulationStateManager
import dependency_injection_config
from kivy_ui import OverlayApp

def run_app(
        show_base: ShowBase = Provide[app_containers.Application.core.show_base],
        render: ShowBase = Provide[app_containers.Application.core.render],
        camera: Camera = Provide[app_containers.Application.core.camera],
        lighting: Lighting = Provide[app_containers.Application.core.lighting],
        kivy_app: OverlayApp = Provide[app_containers.Application.gui.overlay_panel],
        simulation_manager: SimulationStateManager = Provide[
            app_containers.Application.managers.simulation_manager],
        consciousness_handler: ConsciousnessHandler = Provide[
            app_containers.Application.direct_objects.consciousness_handler],
        turn_management_fsm: TurnManagementFSM = Provide[app_containers.Application.fsms.turn_management_fsm],
        main_fsm: GurpsMain = Provide[app_containers.Application.components.main_fsm],
        grid_component: GridComponent = Provide[app_containers.Application.visual.grid]
):
    # Setup camera and lighting
    camera.setup()
    lighting.setup()

    # GUI initialization.
    # show_base.disableMouse()
    kivy_app.run()

    # Request the main FSM to take over.
    main_fsm.request('PlayAreaLoad')

    # App start
    show_base.run()


# Bind the panda messenger to the messenger static
Event.messenger = messenger

application = app_containers.Application()
dependency_injection_config.apply(application)

# Wire all dependencies and start the app.
application.wire(modules=[sys.modules[__name__]])

# for provider in application.traverse():
#     print(provider)

run_app()