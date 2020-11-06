import math
import random
import copy

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from panda3d.core import LVector3, LPoint3, PandaNode, RigidBodyCombiner, NodePath, TextNode

from events import Event
from data_models.grid import GridModel
from utility.coordinates import *


class GridComponent(DirectObject, PandaNode):
    def __init__(self, parent, data_model: GridModel, entity_component_manager):

        PandaNode.__init__(self, "grid_%s" % id(self))
        DirectObject.__init__(self)

        self.parent = parent
        self.path = parent.attachNewNode(self)
        self.data_model = data_model
        self.entity_component_manager = entity_component_manager
        self._instantiate_grid_()

        # Register for messages about each location.
        Event.register("notify_grid_update", self, self.update_grid)

    def update_grid(self):
        """
        Update the grid when its contents change.
        :return:
        """
        for change_name, target, location in self.data_model.changes_delta:
            if change_name == "insert":
                # TODO maybe migrate this to a dictionary lookup later for performance
                offset_loc = cube_to_offset(location)
                loc = self.path.find("location.%s.%s" % (offset_loc[0], offset_loc[1]))
                component = self.entity_component_manager.get(target)
                if component is None:
                    continue

                component_path = component.path
                component_path.reparentTo(loc)
            elif change_name == "remove":
                # TODO: find a good place to stick the objects not rendered out of the way.
                component = self.entity_component_manager.get(target)
                if component is None:
                    continue

                component_path = component.path
                component_path.reparentTo(render)

        # Clear all pending changes.
        self.data_model.changes_delta.clear()

    def _instantiate_grid_(self):
        base_hex = loader.loadModel("models/simple_hex.obj")

        # Set the initial position and scale.
        base_hex.setPos(0, 0, 0)
        base_hex.setScale(1)
        base_hex.setHpr(0, 0, 0)
        base_hex.setDepthOffset(1)

        grid = self.path.attachNewNode('model')
        rbc = RigidBodyCombiner('hex_grid')
        rbcnp = NodePath(rbc)
        rbcnp.reparentTo(grid)

        # TODO: testing here for not rendering past 15 items ( off the screen) to see if not loading the models speeds up
        #   loading times.
        too_big = 15

        for y in range(self.data_model.x_size):
            if y > too_big:
                break
            for x in range(self.data_model.y_size):
                if x > too_big:
                    break
                radius = 1
                delta_x_center = math.sqrt(3) * radius  # DeltaX of centers = sqrt(3)*(r) / 2 + sqrt(3)*(r) / 2
                delta_y_center = radius + (radius / 2)  # DeltaY = r + r/2

                if y % 2 == 0:
                    pos = LPoint3(delta_x_center * x, delta_y_center * -y, 0)
                else:
                    # Offset of x += sqrt(3)*(r) / 2
                    pos = LPoint3(delta_x_center * (x + .5), delta_y_center * -y, 0)

                # Set the initial position and scale.
                location = self.path.attachNewNode("location.%s.%s" % (x, y))
                location.setPos(pos.getX(), pos.getZ(), pos.getY())
                location.setScale(1)
                # location.setDepthOffset(1)

                # placeholder = loader.loadModel("models/simple_hex.x")
                placeholder = base_hex.copy_to(grid)

                #placeholder.setPos(pos.getX() - 1, pos.getZ() - 1, pos.getY() + 0.5)
                placeholder.setPos(pos.getX(), pos.getZ() - 1, pos.getY())
                placeholder.setHpr(0, 0, 0)
                major_color = random.choice([0, 1, 2])
                rand_color = [0, 0, 0]
                rand_color[major_color] = 1
                rand_color = tuple(rand_color)
                placeholder.setColorScale(rand_color[0], rand_color[1], rand_color[2], 0.5)
                # base_hex.instanceTo(placeholder)
                placeholder.reparentTo(rbcnp)

                # text_node = TextNode('loc label')
                # text_node.setText("(%d, %d)" % (x, y))
                # text_path = location.attachNewNode(text_node)
                # text_path.setScale(0.5)
                # text_path.setPos(-1.5, -2, 0.5)

                # Add any objects at this location:

        rbc.collect()
        # rbcnp.analyze()
