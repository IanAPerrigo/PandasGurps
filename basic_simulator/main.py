import random

from direct.showbase.ShowBase import ShowBase
from direct.fsm import FSM
from direct.directnotify.DirectNotify import DirectNotify
from panda3d.core import AmbientLight, DirectionalLight

from behaviors.actors import HumanPlayerBehavior

from events.component.actors import RefreshStats
from events import Event

from containers.grid import GridNode, GridConfig
from containers.managers import *
from containers.components import *
from containers.managers.simulation_manager import SimulationManagerContainer
from containers.managers.turn_manager import TurnManagerContainer
from containers.managers.action_manager import ActionManagerContainer
from containers.managers.action_resolver import GenericResolverContainer
from containers.managers.action_resolver_locator import ActionResolverLocatorContainer
from containers.managers.gui_manager import InteractionEventManagerContainer
from containers.simulation.turn_manager import TurnManagementFsmContainer
from containers.event_handlers import ConsciousnessHandlerContainer

from kivy_ui import OverlayApp

# TODO: move to module that sets up resolvers
from containers.managers.action_resolver import *
from data_models.actions import MovementAction, MeleeAttack, ActionStatus
from data_models.actions.maneuvers import MoveManeuver, MoveAttackManeuver, YieldTurnManeuver
from managers.character_creation import *

# TODO: inject this logger
fsm_dbg = DirectNotify().newCategory("FSMDebug")
# TODO: Make DirectNotify a singleton?


class GurpsMain(ShowBase, FSM.FSM):
    def __init__(self, config={}):
        ShowBase.__init__(self)

        base.disableMouse()
        self.kivy_app = kivy_app = OverlayApp(self)
        kivy_app.run()

        # TODO: Might change if fsms need to be located by name
        FSM.FSM.__init__(self, 'fsm_%r' % id(self))

        self.set_background_color(.2, .2, .2, 1)

        # TODO: move to a camera control class
        self.camLens.setNearFar(1, 100)
        self.camLens.setFov(75)
        self.scroll = -20
        self.x_offset = 12
        self.z_offset = -6
        self.cam.setPos(self.cam.getX() + self.x_offset, self.scroll, self.cam.getZ() + self.z_offset)

        InteractionEventManagerContainer.config.override({
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
                'm',
                'r',
                'space'
            ]
        })
        self.interaction_event_manager = InteractionEventManagerContainer.interaction_event_manager()

        # TODO: ultimately the showbase will be created from a container.
        #   this will be injected instead
        self.entity_component_manager = EntityComponentManagerContainer.entity_component_manager()
        self.entity_model_manager = EntityModelManagerContainer.entity_model_manager()
        self.being_model_manager = BeingModelManagerContainer.being_model_manager()
        self.entity_fsm_manager = EntityFsmManagerContainer.entity_fsm_manager()

        # Initialize grid.
        # TODO: load from configuration source.
        GridConfig.config.override({
            'x_size': 10,
            'y_size': 10
        })

        self.grid = GridNode.grid(render)
        self.grid_model = self.grid.data_model

        # TODo: Move to its own module
        ActionResolverLocatorContainer.config.override({
            MovementAction: MovementResolverContainer,
            MeleeAttack: MeleeAttackResolverContainer,
            MoveManeuver: MoveManeuverResolverContainer,
            MoveAttackManeuver: MoveAttackManeuverResolverContainer,
            YieldTurnManeuver: YieldTurnManeuverResolverContainer,
        })

        self.action_resolver_locator = ActionResolverLocatorContainer.action_resolver_locator()

        self.action_manager = ActionManagerContainer.action_manager()
        self.turn_manager = TurnManagerContainer.turn_manager()

        self.simulation_manager = SimulationManagerContainer.simulation_manager(grid_model=self.grid_model,
                                                                                entity_model_manager=self.entity_model_manager,
                                                                                being_model_manager=self.being_model_manager,
                                                                                action_manager=self.action_manager)

        self.action_resolver = GenericResolverContainer.resolver()
        self.damage_handler = ConsciousnessHandlerContainer.consciousness_handler()
        self.turn_management_fsm = TurnManagementFsmContainer.turn_management_fsm()

        # TODO: config and singleton
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((1, 1, 1, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection((10, 10, 10))
        directionalLight.setColor((.5, .5, .5, 1))
        directionalLight.setSpecularColor((1, 1, 1, 1))
        # directionalLight.showFrustum()
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

        # Important! Enable the shader generator.
        render.setShaderAuto()

        # TODO: containerize
        self.character_creator = CharacterCreator()

        # TODO: load play area based on an event (menu, etc.)
        self.request('PlayAreaLoad')

    def enterPlayAreaLoad(self, *args):
        fsm_dbg.info("[PlayAreaLoad] entering")

        # TODO: actor setup system (character creation)
        # Initialize all players.
        for _ in range(3):
            character = self.character_creator.generate_character_via_normals(0.5)
            actor = ActorComponentContainer.actor(parent=render, data_model=character)

            # TODO: determine if this should be wired here "self.action_resolver_locator"
            actor_fsm = ActorFsmContainer.actor_fsm(data_model=actor.data_model,
                                                    behavior=HumanPlayerBehavior(),
                                                    action_resolver=self.action_resolver)
            self.entity_component_manager[actor.id] = actor
            self.entity_fsm_manager[actor.id] = actor_fsm

            # Signal a stats change.
            RefreshStats.signal(actor.id)

            actor_fsm.request('WaitForTurn')

            loc = (random.randint(0,9), random.randint(0,9))
            self.grid_model.insert(loc, actor.id)

        Event.signal("notify_grid_update")

        # Trigger the turn management object to bootstrap
        self.turn_management_fsm.request("ManagerSetup")


gurps_main = GurpsMain()
gurps_main.run()
