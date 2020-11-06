import sys
from dependency_injector.wiring import Provide

from direct.showbase.ShowBase import ShowBase


from kivy_ui import OverlayApp
import containers.application.application as app_containers
from components.camera.camera import Lighting, Camera
from components.simulation.turn_management import TurnManagementFSM
from components.event_handlers.consciousness import ConsciousnessHandler
from components.grid.grid import GridComponent
from components.main import GurpsMain

from data_models.actions import *


def run_app(
        show_base: ShowBase = Provide[app_containers.Application.components.show_base],
        render: ShowBase = Provide[app_containers.Application.components.render],
        camera: Camera = Provide[app_containers.Application.components.camera],
        lighting: Lighting = Provide[app_containers.Application.components.lighting],
        kivy_app: OverlayApp = Provide[app_containers.Application.gui.overlay_panel],
        consciousness_handler: ConsciousnessHandler = Provide[app_containers.Application.components.consciousness_handler],
        turn_management_fsm: TurnManagementFSM = Provide[app_containers.Application.components.turn_management_fsm],
        main_fsm: GurpsMain = Provide[app_containers.Application.components.main_fsm],
        grid_component: GridComponent = Provide[app_containers.Application.components.grid]
):
    # Setup camera and lighting
    camera.setup()
    lighting.setup()

    # GUI initialization.
    show_base.disableMouse()
    kivy_app.run()

    # Request the main FSM to take over.
    main_fsm.request('PlayAreaLoad')

    # App start
    show_base.run()



application = app_containers.Application()

application.config.from_dict({
    "data_models": {
        'grid': {
            "x_size": 10,
            "y_size": 10
        },

    },
    'managers': {
        'interaction': {
            "event_types": [
                '1', #"MOVE_MANEUVER",
                '2', #"MOVE_ATTACK_MANEUVER",
                'VECTOR_NORTH_WEST',
                'VECTOR_NORTH_EAST',
                'VECTOR_EAST',
                'VECTOR_SOUTH_EAST',
                'VECTOR_SOUTH_WEST',
                'VECTOR_WEST',
                'c',
                'h',
                'e',
                'm',
                'r',
                'space'
            ]
        },
        'tick_manager': {
            'tick_value': 0,
            'tick_rate': 1
        },
        'resolver_locator': {
            'resolvers_for_type': {
                MovementAction: app_containers.Application.action_resolvers.movement_action_resolver,
                # MeleeAttack: MeleeAttackResolverContainer,
                # HarvestAction: HarvestResolverContainer,
                # MoveManeuver: MoveManeuverResolverContainer,
                # MoveAttackManeuver: MoveAttackManeuverResolverContainer,
                # YieldTurnManeuver: YieldTurnManeuverResolverContainer,
            }
        }
    },
    "components": {
        "camera": {
            'background_color': (.2, .2, .2, 1),
            'fov': 75,
            'x_offset': 12,
            'z_offset': -6,
            'scroll': -20
        },
        'lighting': {
            'ambient_color': (1, 1, 1, 1),
            'direction': (10, 10, 10),
            'directional_color': (.5, .5, .5, 1),
            'directional_specular_color': (1, 1, 1, 1)
        }
    },

})

application.wire(modules=[sys.modules[__name__]])
run_app()
