import math
import random
import copy

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from panda3d.core import LVector3, LPoint3, PandaNode, RigidBodyCombiner, NodePath, TextNode

from data_models.actions.movement import MovementType
from data_models.grid import GridModel
from utility.coordinates import *


class ArrowPathComponent(DirectObject, PandaNode):
    def __init__(self, parent, direction: MovementType):

        PandaNode.__init__(self, "arrow_path_%s" % id(self))
        DirectObject.__init__(self)

        self.parent = parent
        self.path = parent.attachNewNode(self)
        self.direction = direction
        self._instantiate_arrow()

    def _instantiate_arrow(self):
        arrow = loader.loadModel("models/arrow.obj")

        # Set the initial position and scale.
        arrow.setScale(0.5)

        # TODO: Get an angle based off of self.direction
        if self.direction == MovementType.EAST:
            arrow.setHpr(0, 0, 90)
            arrow.setPos(.5, 0, 0)
        elif self.direction == MovementType.SOUTH_EAST:
            arrow.setHpr(0, 0, 150)
            arrow.setPos(.5, 0, -.5)
        elif self.direction == MovementType.SOUTH_WEST:
            arrow.setHpr(0, 0, 210)
            arrow.setPos(.5, 0, 0)
        elif self.direction == MovementType.WEST:
            arrow.setHpr(0, 0, 270)
            arrow.setPos(-.5, 0, 0)
        elif self.direction == MovementType.NORTH_WEST:
            arrow.setHpr(0, 0, 330)
            arrow.setPos(.5, 0, 0)
        elif self.direction == MovementType.NORTH_EAST:
            arrow.setHpr(0, 0, 30)
            arrow.setPos(.5, 0, .5)

        arrow.setDepthOffset(1)
        arrow.reparentTo(self.path)


