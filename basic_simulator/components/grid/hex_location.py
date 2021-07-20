from panda3d.core import LVector3, LPoint3, PandaNode, RigidBodyCombiner, NodePath, TextNode
import numpy as np
import math

from data_models.grid import Location
from utility.coordinates import *


class HexLocationComponent(PandaNode):
    # Per hex alignment information.
    RADIUS = 1
    delta_x_center = math.sqrt(3) * RADIUS  # DeltaX of centers = sqrt(3)*(r) / 2 + sqrt(3)*(r) / 2
    delta_y_center = RADIUS + (RADIUS / 2)  # DeltaY = r + r/2

    def __init__(self, parent, data_model: Location, position: np.ndarray, hex_model):
        PandaNode.__init__(self, "location.%s.%s.%s" % (position[0], position[1], position[2]))

        self.parent = parent
        self.path = parent.attachNewNode(self)
        self.position = position
        self.data_model = data_model
        self.hex_model = hex_model

        # Compute the offset cubic coordinate to offset coordinates.
        x, y = cube_to_offset(self.position)
        if y % 2 == 0:
            self.rw_position = LPoint3(self.delta_x_center * x, self.delta_y_center * -y, 0)
        else:
            # Offset of x += sqrt(3)*(r) / 2
            self.rw_position = LPoint3(self.delta_x_center * (x + .5), self.delta_y_center * -y, 0)

    def render(self, rbc_np: RigidBodyCombiner, parent_model):
        """
        Render the model on the RBC for better efficiency.
        :param parent_model:
        :param rbc_np:
        :return:
        """
        # Set the initial position and scale.
        self.path.setPos(self.rw_position.getX(),
                         self.rw_position.getZ(),
                         self.rw_position.getY())
        self.path.setScale(1)

        placeholder = self.hex_model.copy_to(parent_model)
        placeholder.setPos(self.rw_position.getX(),
                           self.rw_position.getZ() + 1,
                           self.rw_position.getY())
        placeholder.setHpr(0, 0, 0)

        # Render the terrain.
        major_terrain = self.data_model.major_terrain
        terrain_color = major_terrain.color
        placeholder.setColorScale(terrain_color[0], terrain_color[1], terrain_color[2], 0.5)
        placeholder.reparentTo(rbc_np)

        # # TODO: DEBUG ONLY
        text_node = TextNode('loc label')
        text_node.setAlign(TextNode.ABoxedCenter)
        #text_node.setText("(%d, %d, %d)" % (self.position[0], self.position[1], self.position[2]))
        text_node.setText("(%.2f)\n(%s, %s, %s)" % (self.data_model.get_elevation(), self.position[0], self.position[1], self.position[2]))
        text_path = self.path.attachNewNode(text_node)
        text_path.setScale(0.25)
        text_path.setPos(0, .1, 0)
