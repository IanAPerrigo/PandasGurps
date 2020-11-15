import numpy as np
import math
import copy
from typing import Dict


from repositories.data_models import Database
import repositories.data_models.grid as grid_db_model
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
        # Direction vector, without chunk_size magnitude.
        return [
            np.array([[1, 0, -1], [2, -1, -1]]),
            np.array([[1, -1, 0], [1, -2, 1]]),
            np.array([[0, -1, 1], [-1, -1, 2]]),
            np.array([[-1, 0, 1], [-2, 1, 1]]),
            np.array([[-1, 1, 0], [-1, 2, -1]]),
            np.array([[0, 1, -1], [1, 1, -2]]),
        ]

    def neighbors(self):
        if self._neighbors is None:
            self._neighbors = [self.chunk_center + direction for direction in Chunk.neighbor_directions()]
        return self._neighbors


class ChunkDescriptor:
    def __init__(self, chunk_id, offset):
        self.chunk_id = chunk_id
        self.offset = offset
        self._absolute = None

    @property
    def absolute(self):
        if self._absolute is None:
            self._absolute = np.frombuffer(self.chunk_id, dtype=int) + np.frombuffer(self.offset, dtype=int)
        return self._absolute


class ObjChunkDict(Dict[object, ChunkDescriptor]):
    pass


class GridModel:
    def __init__(self):
        pass

    def _vec2buf(self, v: np.ndarray):
        return v.tobytes()

    def _buf2vec(self, buf: bytes):
        return np.frombuffer(buf, dtype=int)

    def location_exists(self, absolute_position):
        raise NotImplementedError()

    def get_entities_in_radius_absolute(self, absolute_position, radius):
        raise NotImplementedError()

    def at_absolute(self, absolute_position):
        raise NotImplementedError()

    def insert_absolute(self, absolute_position, entity_id):
        raise NotImplementedError()

    def remove(self, entity_id):
        raise NotImplementedError()

    def get_location(self, entity_id):
        raise NotImplementedError()

    def move(self, entity_id, vec: np.ndarray):
        raise NotImplementedError()


class EphemeralGridModel(GridModel):
    def __init__(self):
        super(EphemeralGridModel, self).__init__()

        self._locations = {}
        self._obj_loc = {}

    def location_exists(self, absolute_position):
        return self._vec2buf(absolute_position) in self._locations

    def get_entities_in_radius_absolute(self, absolute_position, radius):
        pass

    def at_absolute(self, absolute_position):
        loc_key = self._vec2buf(absolute_position)
        return self._locations[loc_key]

    def insert_absolute(self, absolute_position, entity_id):
        loc_key = self._vec2buf(absolute_position)
        self._obj_loc[entity_id] = loc_key
        if loc_key not in self._locations:
            self._locations[loc_key] = []
        self._locations[loc_key].append(entity_id)

    def remove(self, entity_id):
        if entity_id not in self._obj_loc:
            return

        loc_key = self._obj_loc.pop(entity_id)
        self._locations[loc_key].remove(loc_key)

    def get_location(self, entity_id):
        return self._obj_loc[entity_id]

    def move(self, entity_id, vec: np.ndarray):
        old_loc_key = self._obj_loc[entity_id]
        new_loc = self._buf2vec(old_loc_key) + vec
        self.remove(entity_id)
        self.insert_absolute(new_loc, entity_id)


class DatabaseBackedGridModel(GridModel):
    def __init__(self, grid_id=None, chunk_radius=None, procedural=False, db: Database = None):
        super(DatabaseBackedGridModel, self).__init__()

        self.grid_id = grid_id
        self.chunk_radius = chunk_radius
        self.procedural = procedural
        self.db_session = db.get_session()

        self.changes_delta = []

        # A dictionary of chunks currently loaded.
        self.chunks = {}

        # A dictionary of what objects are in what chunk. This will contain every entity, regardless if the chunk is
        # loaded or not.
        self._obj_chunk = ObjChunkDict()

        if self.grid_id is None:
            self._db_grid = grid_db_model.Grid()
            self.db_session.add(self._db_grid)
            self.db_session.commit()
        else:
            self._db_grid = self.db_session.query(grid_db_model.Grid).\
                filter_by(grid_id=self.grid_id)

        # Having _obj_chunk always loaded in memory allows chunks to be saved off to disk when they are not needed.
        # The only thing that needs to be done to ensure that _obj_chunk is saved before the application is shut down.

    def _load_chunk(self, chunk_id):
        # Load the chunk based on its ID.
        existing_chunk = self.db_session.query(grid_db_model.Chunk).\
                        filter_by(chunk_id=chunk_id).\
                        join(grid_db_model.Grid.chunks).\
                        one_or_none()

        if self.procedural:
            # If procedural generation is on, just create the new chunk.
            new_chunk = grid_db_model.Chunk(chunk_id=chunk_id)
            self._db_grid.chunks.append(new_chunk)
            self.db_session.add(new_chunk)
            self.db_session.commit()

            existing_chunk = new_chunk
        elif existing_chunk is None:
            raise Exception("Tried to load a chunk that doesn't exist.")

        # Use the data from the database to create the model.
        chunk = Chunk(chunk_id, self.chunk_radius)
        chunk.location_to_data = {}
        chunk.entity_to_location = {}
        for location in existing_chunk.locations:
            entity_ids = list(map(lambda e: e.entity_id, location.entities))
            chunk.location_to_data[location.location_id] = entity_ids
            for entity_id in entity_ids:
                chunk.entity_to_location[entity_id] = location.location_id

        self.chunks[chunk_id] = chunk
        return chunk

    def _unload_chunk(self, chunk_id):
        # Load the chunk based on its ID.
        existing_chunk = self.db_session.query(grid_db_model.Chunk).\
                        filter_by(chunk_id=chunk_id).\
                        join(grid_db_model.Grid.chunks).\
                        one_or_none()

        # TODO: fill in all information relevant to the chunk.


    def _find_chunk_of_location(self, absolute_position, starting_chunk: np.ndarray = None):
        # Default start at the origin (inefficient).
        neighbor_count = 6
        starting_chunk = np.array([0, 0, 0]) if starting_chunk is None else starting_chunk
        starting_distance = cubic_manhattan(starting_chunk, absolute_position)
        destination_repeat = np.repeat([absolute_position], neighbor_count, axis=0)

        chunk_magnitude = np.array([[self.chunk_radius + 1] * 3, [self.chunk_radius] * 3])
        directions = np.array(Chunk.neighbor_directions())
        directions_proper_mag = np.sum(directions * chunk_magnitude, axis=1)

        cur_min = [(starting_chunk, starting_distance)]
        destination_chunk = None

        while len(cur_min) != 0:
            chunk_center, remaining_dist = cur_min.pop(0)
            neighbors_matrix = directions_proper_mag + np.repeat([chunk_center], neighbor_count, axis=0)
            neighbor_distances = list(cubic_manhattan(neighbors_matrix, destination_repeat, axis=1))
            neighbors_and_dist = list(zip(list(neighbors_matrix), neighbor_distances))
            closer_neighbors = list(filter(lambda nd: nd[1] < remaining_dist, neighbors_and_dist))

            # If no neighbors increase the distance, then the current chunk is the closest.
            if len(closer_neighbors) == 0:
                destination_chunk = self._vec2buf(chunk_center)
                break

            min_dist = min(closer_neighbors, key=lambda x: x[1])
            cur_min.append(min_dist)

        return destination_chunk

    def chunk_exists(self, chunk_id):
        existing_chunk = self.db_session.query(grid_db_model.Chunk). \
            filter_by(chunk_id=chunk_id). \
            join(grid_db_model.Grid.chunks). \
            one_or_none()

        return existing_chunk is not None

    def location_exists(self, absolute_position, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        return self.chunk_exists(chunk_id)

    def get_chunk_of_loc(self, absolute_position, hint_chunk=None):
        return self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)

    def get_entities_in_radius_absolute(self, absolute_position, radius, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        offset = self._buf2vec(chunk_id) - absolute_position
        return self.get_entities_in_radius(chunk_id, offset, radius)

    def get_entities_in_radius(self, chunk_id, offset, radius):
        # Determine radius-to-chunk-radius ratio, and grab surrounding chunks of relevance.
        # Use the chunk list to filter the _chunk dictionary, then calculate distances.
        center_chunk = self._buf2vec(chunk_id)
        entity_chunks = list(map(lambda e_cid: (e_cid[0], self._buf2vec(e_cid[1].absolute)), self._obj_chunk.items()))
        entities, chunk_locs = map(list, zip(*entity_chunks))
        center_repeated = np.repeat([center_chunk], repeats=len(chunk_locs), axis=0)
        entity_distances = list(cubic_manhattan(chunk_locs, center_repeated, axis=1))

        # Ignore chunks over a certain distance (no possibility of any parts being in the radius).
        entity_distances = list(zip(entities, entity_distances, chunk_locs))
        return list(filter(lambda ed: ed[1] + self.chunk_radius <= radius, entity_distances))

    def at(self, chunk_id, offset: np.ndarray):
        chunk = self.chunks.get(chunk_id)
        if chunk is None:
            chunk = self._load_chunk(chunk_id)

        offset_key = self._vec2buf(offset)
        return chunk.location_to_data.get(offset_key)

    def at_absolute(self, absolute_position, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        offset = self._buf2vec(chunk_id) - absolute_position
        return self.at(chunk_id, offset)

    def insert(self, chunk_id, offset: np.ndarray, entity_id):
        chunk_center = self._buf2vec(chunk_id)
        chunk = self.chunks.get(chunk_id)
        if chunk is None:
            chunk = self._load_chunk(chunk_id)
            # Check if chunk was not loaded. If so, just return.
            if chunk is None:
                return

        offset_key = self._vec2buf(offset)
        if offset_key not in chunk.location_to_data:
            chunk.location_to_data[offset_key] = []

        data = chunk.location_to_data.get(offset_key)
        data.append(entity_id)
        self._obj_chunk[entity_id] = ChunkDescriptor(chunk_id, offset_key)
        self.changes_delta.append(("insert", entity_id, chunk_center, offset))

    def insert_absolute(self, absolute_position, entity_id, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        offset = self._buf2vec(chunk_id) - absolute_position
        return self.insert(chunk_id, offset, entity_id)

    def remove(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        if chunk_desc is None:
            raise Exception("Attempted query for an object that does not exist.")

        # Load the chunk if it isn't already loaded.
        chunk_id = chunk_desc.chunk_id
        chunk_center = self._buf2vec(chunk_id)
        chunk = self.chunks.get(chunk_id)
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

        offset = self._buf2vec(loc)
        self.changes_delta.append(("remove", entity_id, chunk_center, offset))

    def get_location(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        chunk_center = self._buf2vec(chunk_desc.chunk_id)
        chunk_offset = self._buf2vec(chunk_desc.offset)
        return chunk_center + chunk_offset

    def get_chunk_offset(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        chunk_center = self._buf2vec(chunk_desc.chunk_id)
        chunk_offset = self._buf2vec(chunk_desc.offset)
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
