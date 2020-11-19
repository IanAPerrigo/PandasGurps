import sys
from dependency_injector import providers
from dependency_injector.wiring import Provide

from direct.showbase.ShowBase import ShowBase


from kivy_ui import OverlayApp
import containers.application.application as app_containers
from components.camera.camera import Lighting, Camera
from components.simulation.turn_management import TurnManagementFSM
from components.event_handlers.consciousness import ConsciousnessHandler
from components.grid.grid import GridComponent
from components.main import GurpsMain

from managers.simulation_manager import SimulationStateManager
from data_models.actions import *
from data_models.actions.maneuvers import *


def run_app(
        show_base: ShowBase = Provide[app_containers.Application.core.show_base],
        render: ShowBase = Provide[app_containers.Application.core.render],
        camera: Camera = Provide[app_containers.Application.core.camera],
        lighting: Lighting = Provide[app_containers.Application.core.lighting],
        kivy_app: OverlayApp = Provide[app_containers.Application.gui.overlay_panel],
        simulation_manager: SimulationStateManager = Provide[app_containers.Application.managers.simulation_manager],
        consciousness_handler: ConsciousnessHandler = Provide[app_containers.Application.direct_objects.consciousness_handler],
        turn_management_fsm: TurnManagementFSM = Provide[app_containers.Application.fsms.turn_management_fsm],
        main_fsm: GurpsMain = Provide[app_containers.Application.components.main_fsm],
        grid_component: GridComponent = Provide[app_containers.Application.visual.grid]
):
    # Setup camera and lighting
    camera.setup()
    lighting.setup()

    # GUI initialization.
    #show_base.disableMouse()
    kivy_app.run()

    # Request the main FSM to take over.
    main_fsm.request('PlayAreaLoad')

    # App start
    show_base.run()


application = app_containers.Application()

application.config.from_dict({
    "repositories": {
        'connection_string': 'sqlite:///:memory:',
        'echo': True
    },
    "data_models": {
        'grid': {
            "chunk_radius": 5,
            "procedural": True
        },

    },
    "behaviors": {},
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
    },
    "action_resolvers": {},
    "core": {
        "camera": {
            'background_color': (.2, .2, .2, 1),
            'fov': 75,
            'x_offset': 5,
            'z_offset': 0,
            'scroll': -30
        },
        'lighting': {
            'ambient_color': (1, 1, 1, 1),
            'direction': (10, 10, 10),
            'directional_color': (.5, .5, .5, 1),
            'directional_specular_color': (1, 1, 1, 1)
        }
    },
    "direct_objects": {},
    "fsms": {},
    "visual": {
        'being': {
            'model_file': 'models/player.obj'
        }
    },
    "gui": {},

})

resolvers_for_type = {
    MovementAction: application.action_resolvers.movement_resolver,
    MeleeAttack: application.action_resolvers.melee_attack_resolver,
    HarvestAction: application.action_resolvers.harvest_resolver,
    EatAction: application.action_resolvers.eat_resolver,
    ObservationAction: application.action_resolvers.observation_resolver,

    PassiveObservationManeuver: application.maneuver_resolvers.passive_observation_resolver,
    MoveManeuver: application.maneuver_resolvers.movement_resolver,
    MoveAttackManeuver: application.maneuver_resolvers.move_attack_resolver,
    YieldTurnManeuver: application.maneuver_resolvers.yield_turn_resolver,
}


def get_resolver(action_type: type):
    return resolvers_for_type[action_type]


# Janky, but it works. Relies on the main container context to perform the resolution.
application.action_resolvers.get_resolver.override(get_resolver)

application.wire(modules=[sys.modules[__name__]])

run_app()
