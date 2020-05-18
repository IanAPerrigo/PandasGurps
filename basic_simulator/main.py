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

from containers.grid import GridNode, GridConfig
from containers.managers import EntityComponentManagerContainer, EntityModelManagerContainer, EntityFsmManagerContainer
from containers.actors import ActorNode, ActorConfig, ActorFsm
from containers.managers.simulation_manager import SimulationManagerContainer
from containers.managers.turn_manager import TurnManagerContainer
import config


# TODO: inject this logger
fsm_dbg = DirectNotify().newCategory("FSMDebug")


class GurpsMain(ShowBase, FSM.FSM):
    def __init__(self, config={}):
        ShowBase.__init__(self)
        # TODO: Might change if fsms need to be located by name
        FSM.FSM.__init__(self, 'fsm_%r' % id(self))

        self.set_background_color(.2, .2, .2, 1)

        # TODO: move to a camera control class
        self.camLens.setNearFar(1, 100)
        self.camLens.setFov(75)
        self.scroll = -10
        self.cam.setPos(self.cam.getX(), self.scroll, self.cam.getZ())

        self.keys = {
            "move_right": 0,
            "move_left": 0,
            "move_up": 0,
            "move_down": 0,
            "next_turn": 0,
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 0,
            "6": 0,
        }

        # TODO: ultimately the showbase will be created from a container.
        # this will be injected instead
        self.entity_component_manager = EntityComponentManagerContainer.entity_component_manager()
        self.entity_model_manager = EntityModelManagerContainer.entity_model_manager()
        self.entity_fsm_manager = EntityFsmManagerContainer.entity_fsm_manager()

        self.turn_manager = TurnManagerContainer.turn_manager_manager()
        self.simulation_manager = None
        self.grid_model = None
        self.actor = None
        self.grid = None

        self.accept("arrow_left", self.set_key, ["move_left", 1])
        # self.accept("arrow_left-up",  self.set_key, ["move_left", 0])
        self.accept("arrow_right", self.set_key, ["move_right", 1])
        # self.accept("arrow_right-up", self.set_key, ["move_right", 0])
        self.accept("arrow_up", self.set_key, ["move_up", 1])
        # self.accept("arrow_up-up",    self.set_key, ["move_up", 0])
        self.accept("arrow_down", self.set_key, ["move_down", 1])
        # self.accept("arrow_down-up",    self.set_key, ["move_down", 0])
        self.accept("space", self.set_key, ["next_turn", 1])

        self.accept("1", self.set_key, ["1", 1])
        self.accept("2", self.set_key, ["2", 1])
        self.accept("3", self.set_key, ["3", 1])
        self.accept("4", self.set_key, ["4", 1])
        self.accept("5", self.set_key, ["5", 1])
        self.accept("6", self.set_key, ["6", 1])

        self.accept("enter", self.set_key, ["begin", 1])

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
                                                                                self.entity_model_manager)
        # Initialize all players.
        for _ in range(3):
            # TODO: load from config source.
            ActorConfig.config.override({
                'model_file': 'models/simple_actor.x'
            })

            actor = ActorNode.actor(render)
            actor_fsm = ActorFsm.actor_fsm(data_model=actor.data_model)
            self.entity_component_manager[actor.id] = actor
            self.entity_fsm_manager[actor.id] = actor_fsm
            actor_fsm.request('WaitForTurn')

            # TODO: will be removed when turn infrastructre in place
            if self.actor is None:
                self.actor = actor

            loc = (random.randint(0,10), random.randint(0,10))
            self.grid_model.insert(loc, actor.id)

        # TODO: should be done elsewhere as an update step
        taskMgr.add(self.grid.update_grid, "grid_update")
        self.turn_manager.generate_turn_order()

    def yield_turn(self):
        self.request('TurnLoop')

    def step_complete(self):
        # TODO: assess the actions submitted in the current step.
        #   This requires Pulling actions from the action manager and
        #   applying them to the objective state.
        #   Keeping track of what actions are still available to take, and how many action points
        #   remain are also required.


        # TODO: fill with other things needed to render after a step is complete
        taskMgr.add(self.grid.update_grid, "grid_update")

    def enterTurnLoop(self, *args):
        fsm_dbg.info("[TurnLoop] entering")

        # Advance the turn.
        self.turn_manager.advance_turn()
        curr_actor = self.turn_manager.get_current_actor()

        # Generate a baseline subjective state.
        self.simulation_manager.generate_subjective_state_for(curr_actor)

        # Yield control to the FSM.
        fsm = self.entity_fsm_manager[curr_actor]
        fsm.yield_turn = self.yield_turn
        fsm.keys = self.keys
        fsm.step_complete = self.step_complete
        fsm.request("TakingTurn")

    def filterTurnLoop(self, request, args):
        """
        Accept interactions for control from any FSM.
        :param request:
        :param args:
        :return:
        """
        fsm_dbg.info("[TurnLoop] filtering (%s)" % request)
        if request == 'TurnLoop':
            return 'TurnLoop'

    def exitTurnLoop(self):
        fsm_dbg.info("[TurnLoop] exiting")

    # TODO: input manager
    def set_key(self, key, val):
        self.keys[key] = val

        #  TODO, this will be a button event most likely.
        if key == "begin":
            self.request('TurnLoop')
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
