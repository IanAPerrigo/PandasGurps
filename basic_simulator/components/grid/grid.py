import math
import random
import copy

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from panda3d.core import LVector3, LPoint3, PandaNode, RigidBodyCombiner, NodePath, TextNode

from events import Event
from data_models.grid import DatabaseBackedGridModel, Chunk
from utility.coordinates import *


class GridComponent(DirectObject, PandaNode):
    def __init__(self, parent, data_model: DatabaseBackedGridModel, entity_component_manager):

        PandaNode.__init__(self, "grid_%s" % id(self))
        DirectObject.__init__(self)

        self.parent = parent
        self.path = parent.attachNewNode(self)
        self.data_model = data_model
        self.entity_component_manager = entity_component_manager

        self._hex_model = None
        self.cubic_spiral = cubic_spiral(np.array([0, 0, 0]), radius=data_model.chunk_radius + 1)
        self._instantiate_grid_()

        # Register for messages about each location.
        Event.register("notify_grid_update", self, self.update_grid)

    def update_grid(self):
        """
        Update the grid when its contents change.
        :return:
        """
        for change_name, target, chunk_center, offset in self.data_model.changes_delta:
            if change_name == "insert":
                absolute_loc = chunk_center + offset
                chunk_comp = self.path.find("chunk.%s.%s.%s" % (chunk_center[0], chunk_center[1], chunk_center[2]))

                # If the chunk is not loaded, load it.
                if chunk_comp.getErrorType() == NodePath.ET_not_found:
                    chunk = self.data_model.load_chunk_v(chunk_center)
                    chunk_comp = self._render_chunk(chunk)

                loc = chunk_comp.find("location.%s.%s.%s" % (absolute_loc[0], absolute_loc[1], absolute_loc[2]))
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
                # TODO: hide the node in the render tree

        # Clear all pending changes.
        self.data_model.changes_delta.clear()

    def _render_chunk(self, chunk: Chunk):
        # Create the chunk hierarchy in the scene graph.
        c_new_chunk = chunk.chunk_center
        chunk_path = self.path.attachNewNode("chunk.%s.%s.%s" % (c_new_chunk[0], c_new_chunk[1], c_new_chunk[2]))
        chunk_model = chunk_path.attachNewNode('model')
        rbc = RigidBodyCombiner('chunk')
        rbcnp = NodePath(rbc)
        rbcnp.reparentTo(chunk_model)

        rand_color = np.random.random(3)

        # Per hex alignment information.
        radius = 1
        delta_x_center = math.sqrt(3) * radius  # DeltaX of centers = sqrt(3)*(r) / 2 + sqrt(3)*(r) / 2
        delta_y_center = radius + (radius / 2)  # DeltaY = r + r/2

        # Offset the matrix from the origin to the center of the new relative chunk.
        relative_spiral_matrix = np.array(self.cubic_spiral)
        spiral_matrix = relative_spiral_matrix + np.repeat([c_new_chunk], repeats=relative_spiral_matrix.shape[0], axis=0)

        for c_sp in spiral_matrix:
            c_x, c_y, c_z = c_sp

            # Compute the offset cubic coordinate to offset coordinates.
            o_sp = cube_to_offset(c_sp)
            x, y = o_sp

            if y % 2 == 0:
                pos = LPoint3(delta_x_center * x, delta_y_center * -y, 0)
            else:
                # Offset of x += sqrt(3)*(r) / 2
                pos = LPoint3(delta_x_center * (x + .5), delta_y_center * -y, 0)

            # Set the initial position and scale.
            location = chunk_path.attachNewNode("location.%s.%s.%s" % (c_x, c_y, c_z))
            location.setPos(pos.getX(), pos.getZ(), pos.getY())
            location.setScale(1)

            placeholder = self._hex_model.copy_to(chunk_model)
            placeholder.setPos(pos.getX(), pos.getZ() - 1, pos.getY())
            placeholder.setHpr(0, 0, 0)
            # major_color = random.choice([0, 1, 2])
            # rand_color = [0, 0, 0]
            # rand_color[major_color] = 1
            # rand_color = tuple(rand_color)
            placeholder.setColorScale(rand_color[0], rand_color[1], rand_color[2], 0.5)
            placeholder.reparentTo(rbcnp)

            # # TODO: DEBUG ONLY
            text_node = TextNode('loc label')
            text_node.setAlign(TextNode.ABoxedCenter)
            text_node.setText("(%d, %d, %d)" % (c_x, c_y, c_z))
            text_path = location.attachNewNode(text_node)
            text_path.setScale(0.25)
            text_path.setPos(0, -.1, 0)

        rbc.collect()
        return chunk_path

    def _instantiate_grid_(self):
        self._hex_model = loader.loadModel("models/simple_hex.obj")

        # Set the initial position and scale.
        self._hex_model.setPos(0, 0, 0)
        self._hex_model.setScale(1)
        self._hex_model.setHpr(0, 0, 0)
        self._hex_model.setDepthOffset(1)

        center_chunk = np.array((0, 0, 0))
        chunk_id = self.data_model.chunk_vec_to_buf(center_chunk)
        starting_chunk = self.data_model.load_chunk(chunk_id)

        chunk_radius_to_render = 1
        radius_to_render = (self.data_model.chunk_radius * 3 + 1) * chunk_radius_to_render

        # BFS Queue
        neighbors_to_explore = [starting_chunk]
        seen_neighbors = set()

        while len(neighbors_to_explore) != 0:
            chunk = neighbors_to_explore.pop(0)
            if chunk in seen_neighbors:
                continue

            seen_neighbors.add(chunk)

            # Only render chunk if the chunk's radius is less than or equal to R away
            origin_d = cubic_manhattan(starting_chunk.chunk_center, chunk.chunk_center)
            if origin_d > radius_to_render:
                continue

            # Convert the list of neighbor positions to ids, then load the neighbors.
            for neighbor_vector in chunk.neighbor_chunk_vec:
                neighbor_id = self.data_model.chunk_vec_to_buf(neighbor_vector)
                self.data_model.load_chunk(neighbor_id)

            self._render_chunk(chunk)
            neighbors_to_explore.extend(filter(lambda n: n is not None and n not in neighbors_to_explore, chunk.neighbors))


        # # TODO: batch and filter more efficiently.
        # for chunk_id, chunk in self.data_model.chunks.items():
        #     if cubic_manhattan(center_chunk, chunk.chunk_center) >= chunk_render_radius:
        #         continue


        #
        # for y in range(self.data_model.x_size):
        #     if y > too_big:
        #         break
        #     for x in range(self.data_model.y_size):
        #         if x > too_big:
        #             break
        #         radius = 1
        #         delta_x_center = math.sqrt(3) * radius  # DeltaX of centers = sqrt(3)*(r) / 2 + sqrt(3)*(r) / 2
        #         delta_y_center = radius + (radius / 2)  # DeltaY = r + r/2
        #
        #         if y % 2 == 0:
        #             pos = LPoint3(delta_x_center * x, delta_y_center * -y, 0)
        #         else:
        #             # Offset of x += sqrt(3)*(r) / 2
        #             pos = LPoint3(delta_x_center * (x + .5), delta_y_center * -y, 0)
        #
        #         # Set the initial position and scale.
        #         location = self.path.attachNewNode("location.%s.%s" % (x, y))
        #         location.setPos(pos.getX(), pos.getZ(), pos.getY())
        #         location.setScale(1)
        #         # location.setDepthOffset(1)
        #
        #         # placeholder = loader.loadModel("data_models/simple_hex.x")
        #         placeholder = base_hex.copy_to(grid)
        #
        #         #placeholder.setPos(pos.getX() - 1, pos.getZ() - 1, pos.getY() + 0.5)
        #         placeholder.setPos(pos.getX(), pos.getZ() - 1, pos.getY())
        #         placeholder.setHpr(0, 0, 0)
        #         major_color = random.choice([0, 1, 2])
        #         rand_color = [0, 0, 0]
        #         rand_color[major_color] = 1
        #         rand_color = tuple(rand_color)
        #         placeholder.setColorScale(rand_color[0], rand_color[1], rand_color[2], 0.5)
        #         # base_hex.instanceTo(placeholder)
        #         placeholder.reparentTo(rbcnp)
        #
        #         # text_node = TextNode('loc label')
        #         # text_node.setText("(%d, %d)" % (x, y))
        #         # text_path = location.attachNewNode(text_node)
        #         # text_path.setScale(0.5)
        #         # text_path.setPos(-1.5, -2, 0.5)
        #
        #         # Add any objects at this location:

        # rbcnp.analyze()
