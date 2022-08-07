from typing import Dict

from dependency_injector import containers, providers

from data_models.actions import *
from data_models.actions.maneuvers import *
from data_models.entities.status_effects import *
from data_models.triggers.status_effects.energy import *
from data_models.terrain.basic_terrain import *


config_dict = {
        "repositories": {
            'connection_string': 'sqlite:///:memory:',
            'echo': True
        },
        "terrain_data_models": {

        },
        "data_models": {
            'grid': {
                "chunk_radius": 2,
                "procedural": True
            },

        },
        "behaviors": {},
        'managers': {
            'interaction': {
                "event_types": [
                    '1',  # "MOVE_MANEUVER",
                    '2',  # "MOVE_ATTACK_MANEUVER",
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
                'tick_rate': 100
            },
        },
        "action_resolvers": {},
        "trigger_resolvers": {},
        "core": {
            'app': {
                'width': 1000,
                'height': 1000
            },
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

    }

# Config file for the dependency injector
def apply(root: containers.Container):
    # Main config passed to containers.
    root.config.from_dict()

    """ Binding of action resolvers """
    action_resolvers_for_type = {
        MovementAction: root.action_resolvers.movement_resolver,
        MeleeAttack: root.action_resolvers.melee_attack_resolver,
        HarvestAction: root.action_resolvers.harvest_resolver,
        DrinkAction: root.action_resolvers.drink_resolver,
        EatAction: root.action_resolvers.eat_resolver,
        ObservationAction: root.action_resolvers.observation_resolver,

        PassiveObservationManeuver: root.maneuver_resolvers.passive_observation_resolver,
        MoveManeuver: root.maneuver_resolvers.movement_resolver,
        MoveAttackManeuver: root.maneuver_resolvers.move_attack_resolver,
        YieldTurnManeuver: root.maneuver_resolvers.yield_turn_resolver,
    }

    def get_action_resolver(action_type: type):
        return action_resolvers_for_type[action_type]

    """ Binding of trigger resolvers """
    trigger_resolvers_for_type = {
        StarvationTrigger: root.trigger_resolvers.starvation_trigger_resolver,
        DailyDehydrationTrigger: root.trigger_resolvers.daily_dehydrated_trigger_resolver,
        EightHourDehydrationTrigger: root.trigger_resolvers.eight_hour_dehydrated_trigger_resolver
    }

    def get_trigger_resolver(trigger_type: type):
        return trigger_resolvers_for_type[trigger_type]

    """ Binding of terrain generators """
    terrain_types = {
        WaterTerrain: root.data_models.terrain.water_terrain,
        GrassTerrain: root.data_models.terrain.grass_terrain,
        CliffTerrain: root.data_models.terrain.cliff_terrain,
    }

    """
    Container overrides with configured functions.
    """
    root.action_resolvers.get_resolver.override(get_action_resolver)
    root.managers.get_trigger_resolver.override(get_trigger_resolver)
    root.data_models.get_terrain_types.override(terrain_types)
