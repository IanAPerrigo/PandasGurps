import numpy as np
import math
import copy
from typing import Dict

from utility.coordinates import *


class Chunk:
    def __init__(self, chunk_id, chunk_radius):
        self.chunk_id = chunk_id
        self.chunk_radius = chunk_radius
        self.chunk_center = np.frombuffer(chunk_id, dtype=int)

        self.entity_to_location = {}
        self.location_to_data = {}
        self._neighbors = None

    @staticmethod
    def neighbor_directions():
        return [np.array([1, 1, -2]),
                np.array([2, -1, -1]),
                np.array([1, -2, 1]),
                np.array([-1, -1, 2]),
                np.array([-2, 1, 1]),
                np.array([-1, 2 ,-1])]

    def neighbors(self):
        if self._neighbors is None:
            self._neighbors = [self.chunk_center + direction for direction in Chunk.neighbor_directions()]
        return self._neighbors


class ChunkDescriptor:
    def __init__(self, chunk_id, offset):
        self.chunk_id = chunk_id
        self.offset = offset


class ObjChunkDict(Dict[object, ChunkDescriptor]):
    pass


class GridModel:
    def __init__(self, grid_id=None, chunk_radius=None, procedural=False):
        # TODO: two different uses for a grid.
        #   1. be the objective source of data for a grid. Load defined grid state from disk, or create it if it doenst
        #   exist.
        #   2. Be a subjective grid storage, and act as a facade for the real data.

        # TODO: if the grid_id is missing, allocate new data on disk for the grid.
        self.grid_id = grid_id
        self.chunk_radius = chunk_radius
        self.procedural = procedural

        self.changes_delta = []

        # A dictionary of chunks currently loaded.
        self._chunks = {}

        # A dictionary of what objects are in what chunk. This will contain every entity, regardless if the chunk is
        # loaded or not.
        # TODO: load the grid_descriptor that describes the state of every entity and their assigned chunks on save.
        self._obj_chunk = ObjChunkDict()

        # Having _obj_chunk always loaded in memory allows chunks to be saved off to disk when they are not needed.
        # The only thing that needs to be done to ensure that _obj_chunk is saved before the application is shut down.

    def _load_chunk(self, chunk_id):
        # Load the chunk based on its ID.
        # TODO: read from disk
        data = object()

        if self.procedural:
            # If procedural generation is on, just create the new chunk.
            pass

        # Use the data from the database to create the model.
        chunk = Chunk(chunk_id, self.chunk_radius)
        chunk.location_to_data = {} # TODO: STUB
        chunk.entity_to_location = {} # TODO: STUB

        self._chunks[chunk_id] = chunk
        return chunk

    def _find_chunk_of_location(self, absolute_position, starting_chunk: np.ndarray = None):
        # Default start at the origin (inefficient).
        starting_chunk = np.array([0, 0, 0]) if starting_chunk is None else starting_chunk
        #starting_chunk_id = starting_chunk.tobytes()
        starting_distance = cubic_manhattan(starting_chunk, absolute_position)

        directions = Chunk.neighbor_directions()
        destination_repeat = np.repeat([absolute_position], len(directions), axis=0)
        open_n, closed_n = [(starting_chunk, starting_distance)], []

        while len(open_n) != 0:
            chunk_center, remaining_dist = open_n.pop(0)
            directions = Chunk.neighbor_directions()
            neighbors_matrix = np.array(directions) * 2 + np.repeat([chunk_center], len(directions), axis=0)
            neighbor_distances = list(cubic_manhattan(neighbors_matrix, destination_repeat, axis=1))
            neighbors_and_dist = list(zip(list(neighbors_matrix), neighbor_distances))
            min_dist = min(filter(lambda nd: nd[1] < remaining_dist, neighbors_and_dist), key=lambda x: x[1])
            open_n.append(min)


    def chunk_exists(self, chunk_id):
        # TODO: query the chunk storage for the key.
        pass

    def location_exists(self, absolute_position):
        # TODO: perform A* to find the chunk,
        # then call self.chunk_exists(chunk_id, offset)
        pass

    def get_chunk_of_loc(self, absolute_position, hint_chunk=None):
        # TODO: perform A* to find the chunk that minimizes the distance.

        pass

    def get_entities_in_radius_absolute(self, absolute_position, radius, hint_chunk=None):
        # Perform A* from the origin (could be very inefficient for long distances, maybe some way of inferring an okay
        # starting chunk) to find the related chunk, offset.

        # Call self.get_entities_in_radius()
        pass

    def get_entities_in_radius(self, chunk_id, offset, radius):
        # Determine radius-to-chunk-radius ratio, and grab surrounding chunks of relevance.
        # Use the chunk list to filter the _chunk dictionary, then calculate distances.

        pass

    def at(self, chunk_id, offset: np.ndarray):
        chunk = self._chunks.get(chunk_id)
        if chunk is None:
            chunk = self._load_chunk(chunk_id)

        offset_key = offset.tobytes()
        return chunk.location_to_data.get(offset_key)

    def at_absolute(self, absolute_position, hint_chunk=None):
        # TODO: perform A* from a close loaded chunk, and locate the position.
        # then call self.at(chunk_id, offset)
        pass

    def insert(self, chunk_id, offset: np.ndarray, entity_id):
        chunk = self._chunks.get(chunk_id)
        if chunk is None:
            chunk = self._load_chunk(chunk_id)

        offset_key = offset.tobytes()
        if offset_key not in chunk.location_to_data:
            chunk.location_to_data[offset_key] = []

        data = chunk.location_to_data.get(offset_key)
        data.append(entity_id)
        self._obj_chunk[entity_id] = ChunkDescriptor(chunk_id, offset_key)
        self.changes_delta.append(("insert", entity_id, chunk_id, offset))

    def insert_absolute(self, absolute_position, entity_id, hint_chunk=None):
        # TODO: perform A* from the closest loaded chunk.
        # Call self.insert(chunk_id, offset, entity_id)
        pass

    def remove(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        if chunk_desc is None:
            raise Exception("Attempted query for an object that does not exist.")

        # Load the chunk if it isn't already loaded.
        chunk_id = chunk_desc.chunk_id
        chunk = self._chunks.get(chunk_id)
        if chunk is not None:
            chunk = self._load_chunk(chunk_id)

        loc = chunk.entity_to_location.pop(entity_id, None)
        if loc is None:
            raise Exception("Entity exists in chunk map but not in the chunk.")

        loc_contents = chunk.entity_to_location.get(loc)
        if loc_contents is None:
            raise Exception("Location is empty.")

        # Remove the entity.
        self._obj_chunk.pop(entity_id, None)
        loc_contents.remove(entity_id)

        offset = np.frombuffer(loc, dtype=int)
        self.changes_delta.append(("remove", entity_id, chunk_id, offset))

    def get_location(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        chunk_center = np.frombuffer(chunk_desc.chunk_id, dtype=int)
        chunk_offset = np.frombuffer(chunk_desc.offset, dtype=int)
        return chunk_center + chunk_offset

    def get_chunk_offset(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        chunk_center = np.frombuffer(chunk_desc.chunk_id, dtype=int)
        chunk_offset = np.frombuffer(chunk_desc.offset, dtype=int)
        return chunk_center, chunk_offset

    def move(self, entity_id, vec: np.ndarray):
        """
        Shorthand for remove-insert with a vector.
        """
        chunk_center, offset = self.get_chunk_offset(entity_id)
        new_offset = offset + vec

        # Determine the destination chunk
        dest_chunk = self._obj_chunk.get(entity_id)
        if self.chunk_radius < cubic_manhattan(chunk_center, new_offset):
            # Compute absolute coordinates,
            absolute = chunk_center + new_offset
            dest_chunk = self.get_chunk_of_loc(absolute, hint_chunk=chunk_center)

        # Remove the entity from the original location.
        self.remove(entity_id)

        # Add it to the new location.
        self.insert(dest_chunk.chunk_id, dest_chunk.offset, entity_id)

a = GridModel(chunk_radius=2)

to_find = np.array([1,0,-1]) * 4
a._find_chunk_of_location(to_find)