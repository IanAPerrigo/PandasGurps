import numpy as np
import os
import math
import random
from uuid import uuid4

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from direct.fsm import FSM
from direct.directnotify.DirectNotify import DirectNotify
from panda3d.core import TextNode, TransparencyAttrib
from panda3d.core import Filename, AmbientLight, DirectionalLight, PointLight, Spotlight, PerspectiveLens
from panda3d.core import LPoint3, LVector3, VBase4, LVector4

from direct.gui.DirectGui import *

from behaviors.actors import HumanPlayerBehavior

from events.actors import RefreshStats

from containers.grid import GridNode, GridConfig
from containers.managers import EntityComponentManagerContainer, EntityModelManagerContainer, EntityFsmManagerContainer
from containers.actors import *
from containers.managers.simulation_manager import SimulationManagerContainer
from containers.managers.turn_manager import TurnManagerContainer
from containers.managers.action_manager import ActionManagerContainer
from containers.managers.action_resolver import GenericResolverContainer
from containers.managers.action_resolver_locator import ActionResolverLocatorContainer
from containers.managers.gui_manager import InteractionEventManagerContainer

from kivy_ui import OverlayApp

# TODO: move to module that sets up resolvers
from containers.managers.action_resolver import MovementResolverContainer, MeleeAttackResolverContainer, MoveManeuverResolverContainer
from data_models.actions import MovementAction, MeleeAttack, MovementType, ActionStatus
from data_models.actions.maneuvers.move import MoveManeuver
from data_models.stats.stat_set import *
from managers.character_creation import *

import config


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
                'MOVE_NORTH_WEST',
                'MOVE_NORTH_EAST',
                'MOVE_EAST',
                'MOVE_SOUTH_EAST',
                'MOVE_SOUTH_WEST',
                'MOVE_WEST',
                'c',
                'm',
                'r',
                'space'
            ]
        })
        self.interaction_event_manager = InteractionEventManagerContainer.interaction_event_manager()

        # TODO: ultimately the showbase will be created from a container.
        # this will be injected instead
        self.entity_component_manager = EntityComponentManagerContainer.entity_component_manager()
        self.entity_model_manager = EntityModelManagerContainer.entity_model_manager()
        self.entity_fsm_manager = EntityFsmManagerContainer.entity_fsm_manager()

        # TODo: Move to its own module
        ActionResolverLocatorContainer.config.override({
            MovementAction: MovementResolverContainer,
            MeleeAttack: MeleeAttackResolverContainer,
            MoveManeuver: MoveManeuverResolverContainer,
        })

        self.action_resolver_locator = ActionResolverLocatorContainer.action_resolver_locator()

        self.action_manager = ActionManagerContainer.action_manager()
        self.turn_manager = TurnManagerContainer.turn_manager_manager()
        self.simulation_manager = None
        self.action_resolver = None
        self.grid_model = None
        self.grid = None

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

        # Initialize grid.
        # TODO: load from configuration source.
        GridConfig.config.override({
            'x_size': 10,
            'y_size': 10
        })

        self.grid = GridNode.grid(render)
        self.grid_model = self.grid.data_model

        self.simulation_manager = SimulationManagerContainer.simulation_manager(self.grid_model,
                                                                                self.entity_model_manager,
                                                                                self.action_manager)

        self.action_resolver = GenericResolverContainer.resolver()

        # TODO: actor setup system (character creation)
        # Initialize all players.
        for _ in range(3):
            # TODO: load from config source.
            ActorConfig.config.override({
                'model_file': 'models/simple_actor.x'
            })

            character = self.character_creator.generate_character_via_normals(0.5)
            ActorModel.config.override({
                "character_model": character
            })

            actor = ActorNode.actor(render)
            # TODO: determine if this should be wired here "self.action_resolver_locator"
            actor_fsm = ActorFsm.actor_fsm(data_model=actor.data_model,
                                           behavior=HumanPlayerBehavior(),
                                           action_resolver=self.action_resolver)
            self.entity_component_manager[actor.id] = actor
            self.entity_fsm_manager[actor.id] = actor_fsm

            # Signal a stats change.
            RefreshStats.signal(actor.id)

            actor_fsm.request('WaitForTurn')

            loc = (random.randint(0,9), random.randint(0,9))
            self.grid_model.insert(loc, actor.id)

        # TODO: should be done elsewhere as an update step
        taskMgr.add(self.grid.update_grid, "grid_update")
        self.turn_manager.generate_turn_order()
        self.demand("TurnBegin")

    def yield_turn(self):
        # Only directly yield a turn if the state isn't already transitioning.
        if not self.isInTransition():
            self.request('NextTurn')

    def step_complete(self):
        # TODO: move this to a different module
        # TODO: assess the actions submitted in the current step.
        #   This requires Pulling actions from the action manager and
        #   applying them to the objective state.
        #   Keeping track of what actions are still available to take, and how many action points
        #   remain are also required.

        targets = self.simulation_manager.action_manager.get_submitted_actions()

        processed_any_action = False

        # TODO: handle failures and such
        unresolved_actions = filter(lambda maneuver: maneuver.status != ActionStatus.RESOLVED, targets)
        failed_actions = []

        for action in unresolved_actions:
            if action.status == ActionStatus.PARTIAL_UNREADY or \
                    action.status == ActionStatus.UNREADY:
                # TODO: issue an event to draw a planning in-progress maneuver
                break
            elif action.status == ActionStatus.FAILED:
                failed_actions.append(action)
                break
            else:
                processed_any_action = True
                self.action_resolver.resolve(action)

        # TODO: filter through actions that are ready to resolve, and resolve them. If there are no actions
        #   that require resolving, no need to update the grid.
        #   CAVEAT: if a new action was posted, and it needs to be visualized (not ready to execute) do that here too.
        # DEPRECATED
        # for actor, action in targets:
        #     self.action_resolver.resolve(action)

        # TODO: dont purge all actions after each step.
        #self.simulation_manager.action_manager.remove_all_actions()

        # Issue a grid update only if an action was processed.
        if processed_any_action:
            taskMgr.add(self.grid.update_grid, "grid_update")
            # TODO: issue other events (perhaps depending on the effects of the actions)

    def enterTurnBegin(self):
        # Advance the turn.
        self.turn_manager.advance_turn()
        curr_actor = self.turn_manager.get_current_actor()

        # Generate a baseline subjective state.
        self.simulation_manager.generate_subjective_state_for(curr_actor)

        # Clear the action manager of excess actions that were not used.
        self.simulation_manager.action_manager.clear()

        # Register the actor taking the turn.
        self.simulation_manager.action_manager.register_actor(curr_actor)

        # Yield control to the FSM.
        fsm = self.entity_fsm_manager[curr_actor]
        fsm.yield_turn = self.yield_turn
        fsm.keys = self.interaction_event_manager.event_instances
        fsm.step_complete = self.step_complete
        fsm.request("TakingTurn")
        self.demand("TurnLoop")

    def enterTurnLoop(self, *args):
        fsm_dbg.info("[TurnLoop] entering")

    def filterTurnLoop(self, request, args):
        """
        Accept interactions for control from any FSM.
        :param request:
        :param args:
        :return:
        """
        fsm_dbg.info("[TurnLoop] filtering (%s)" % request)

        if request == 'NextTurn':
            return 'NextTurn'

    def exitTurnLoop(self):
        fsm_dbg.info("[TurnLoop] exiting")

    def enterNextTurn(self):
        curr_actor = self.turn_manager.get_current_actor()
        fsm = self.entity_fsm_manager[curr_actor]
        fsm.request("Complete")
        self.demand("TurnBegin")

    # TODO: input manager
    def navigation_button_pressed(self, instance, direction):
        messenger.send("MOVE_%s" % direction)

    # TODO: input manager
    def set_key(self, key, val):
        self.keys[key] = val

        #  TODO, this will be a button event most likely.
        if key == "next_turn":
            self.request('NextTurn')
            return
        #
        # if self.state == 'TurnLoop':
        #     vec = (0, 0)
        #     if key == "move_left":
        #         vec = (-1, 0)
        #     if key == "move_right":
        #         vec = (1, 0)
        #     if key == "move_up":
        #         vec = (0, 1)
        #     if key == "move_down":
        #         vec = (0, -1)
        #
        #     curr_actor = self.turn_manager.get_current_actor()
        #     self.grid_model.move(curr_actor, np.array(vec))
        #     taskMgr.add(self.grid.update_grid, "grid_update")


gurps_main = GurpsMain()
gurps_main.run()
