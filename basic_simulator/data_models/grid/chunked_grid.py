import numpy as np
from typing import Dict
from numba import njit

from . import GridModel, Location, LocationDataDict
from utility.coordinates import cubic_manhattan, get_new_center_offset_for_dir, cubic_ring


class Chunk:
    chunk_neighbor_dirs = [
        np.array([[1, 0, -1], [1, -1, 0]]),
        np.array([[1, -1, 0], [0, -1, 1]]),
        np.array([[0, -1, 1], [-1, 0, 1]]),
        np.array([[-1, 0, 1], [-1, 1, 0]]),
        np.array([[-1, 1, 0], [0, 1, -1]]),
        np.array([[0, 1, -1], [1, 0, -1]]),
    ]

    offset_vec_neighbors = None
    neighbor_by_offset = None

    def __init__(self, chunk_id, chunk_radius):
        self.chunk_id = chunk_id
        self.chunk_radius = chunk_radius
        self.chunk_center = np.frombuffer(chunk_id, dtype=int)

        self.entity_to_pos = {}
        self.pos_to_location = LocationDataDict()

        # List of neighbors, with none representing the neighbor as unloaded / inaccessible.
        # The index corresponds to the direction in the neighbor_directions array as it was derived.
        # Since they are the absolute vector (buffers) when one direction is determined, the other can be determined
        # by conjugating ((i + 3) % 6)
        self.neighbors = [None] * 6

        if Chunk.offset_vec_neighbors is None:
            # Create offset vector neighbors.
            self._neighbor_directions = Chunk.chunk_neighbor_dirs
            chunk_magnitude = np.array([[self.chunk_radius + 1] * 3, [self.chunk_radius] * 3])
            directions = np.array(self._neighbor_directions)
            Chunk.offset_vec_neighbors = np.sum(directions * chunk_magnitude, axis=1)

            # Use the neighbors to generate links to other chunks (in local coordinates to it can be reused).
            local_center = np.array([0, 0, 0])
            periphary_ring = cubic_ring(local_center, self.chunk_radius + 1)
            Chunk.neighbor_by_offset = {}

            for local_offset in periphary_ring:
                center, offset, neighbor_indexes = get_new_center_offset_for_dir(Chunk.offset_vec_neighbors,
                                                                               local_center, local_offset)
                # Neighbor indexes was packed in an array for optimal performance.
                neighbor_index = neighbor_indexes[0]
                offset_key = local_offset.tobytes()
                Chunk.neighbor_by_offset[offset_key] = (center, offset, neighbor_index)

        center_repeat = np.repeat([self.chunk_center], Chunk.offset_vec_neighbors.shape[0], axis=0)
        self.neighbor_chunk_vec = center_repeat + Chunk.offset_vec_neighbors

    def __str__(self):
        return str(self.chunk_center)

    @staticmethod
    def conjugate_direction_index(index):
        return (index + 3) % 6


class ChunkDescriptor:
    def __init__(self, chunk_id, offset):
        self.chunk_id = chunk_id
        self.offset = offset

        self.chunk_vec = np.frombuffer(self.chunk_id, dtype=int)
        self.offset_vec = np.frombuffer(self.offset, dtype=int)
        self.absolute = self.chunk_vec + self.offset_vec


class ObjChunkDict(Dict[object, ChunkDescriptor]):
    pass


class ChunkedGrid(GridModel):
    def __init__(self, chunk_radius=None):
        super(ChunkedGrid, self).__init__()

        self.chunk_radius = chunk_radius

        # Dictionary to locate object's locations.
        self._obj_chunk = ObjChunkDict()

        # Dictionary of loaded chunks.
        self.chunks = {}

        # Create the vectors for determining neighbors.
        chunk_magnitude = np.array([[self.chunk_radius + 1] * 3, [self.chunk_radius] * 3])
        directions = np.array(Chunk.chunk_neighbor_dirs)
        self.neighbor_chunk_vec = np.sum(directions * chunk_magnitude, axis=1)

    def _load_chunk(self, chunk_id):
        chunk = Chunk(chunk_id, self.chunk_radius)

        # Populate the neighbors field of the chunk.
        for i, neighbor_vec in enumerate(chunk.neighbor_chunk_vec):
            # Translate vector to ID, and lookup for loaded chunks.
            neighbor_id = self._vec2buf(neighbor_vec)
            neighbor_chunk = self.chunks.get(neighbor_id, None)

            # If a neighboring chunk exists, link the two chunks.
            if neighbor_chunk is not None:
                chunk.neighbors[i] = neighbor_chunk
                i_con = Chunk.conjugate_direction_index(i)
                neighbor_chunk.neighbors[i_con] = chunk

        self.chunks[chunk_id] = chunk
        # TODO: add a "loaded chunk" event to the deltas list
        return chunk

    def load_chunk(self, chunk_id):
        if chunk_id not in self.chunks:
            chunk = self._load_chunk(chunk_id)
        else:
            chunk = self.chunks[chunk_id]

        return chunk

    def load_chunk_v(self, chunk_vec: np.ndarray):
        return self.load_chunk(self._vec2buf(chunk_vec))

    def _unload_chunk(self, chunk_id):
        # Delete the chunk and remove all
        chunk = self.chunks.pop(chunk_id, None)
        for entity_id in chunk.entity_to_pos.keys():
            self._obj_chunk.pop(entity_id, None)

        # TODO: add a "unloaded chunk" event to the deltas list

    def unload_chunk(self, chunk_id):
        if chunk_id in self.chunks:
            self._unload_chunk(chunk_id)

    def _find_chunk_of_location(self, absolute_position, starting_chunk: np.ndarray = None):
        # Default start at the origin (inefficient).
        neighbor_count = 6
        starting_chunk = np.array([0, 0, 0]) if starting_chunk is None else starting_chunk
        starting_distance = cubic_manhattan(starting_chunk, absolute_position)
        destination_repeat = np.repeat([absolute_position], neighbor_count, axis=0)

        cur_min = [(starting_chunk, starting_distance)]
        destination_chunk = None
        # TODO: move chunk searching to chunk class? or split since this may be needed for finding unloaded chunks
        # Also maybe use dot product to determine direction

        while len(cur_min) != 0:
            chunk_center, remaining_dist = cur_min.pop(0)
            neighbors_matrix = self.neighbor_chunk_vec + np.repeat([chunk_center], neighbor_count, axis=0)
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

    def get_locations_of_path(self, path: np.ndarray, starting_chunk: np.ndarray = None):
        if starting_chunk is None:
            # determine starting chunk. Worst case performance
            pass

        locations = []
        chunk_id = self._vec2buf(starting_chunk)
        current_chunk = self.chunks.get(chunk_id)
        direction_list = [j - i for i, j in zip(path[:-1], path[1:])]
        offset_vec_neighbors = current_chunk.offset_vec_neighbors
        center, offset = starting_chunk, path[0] - starting_chunk
        locations.append(self.at_chunked(chunk_id, offset))

        # TODO: not as performant as possible. Maybe numba-fy this function
        for direction in direction_list:
            # Calculate new offset
            offset = offset + direction
            dist = cubic_manhattan(np.array([0,0,0]), offset)
            if dist > self.chunk_radius:
                # Determine which chunk comes from moving in a particular direction.
                offset_key = self._vec2buf(offset)
                chunk_vec, new_offset, neighbor_idx = Chunk.neighbor_by_offset.get(offset_key)
                # Translate the new center and set the new offset.
                center = center + chunk_vec
                offset = new_offset
                chunk_id = self._vec2buf(center)
                current_chunk = current_chunk.neighbors[neighbor_idx]
                if current_chunk is None:
                    current_chunk = self.load_chunk_v(chunk_id)

            locations.append(self.at_chunked(chunk_id, offset))

        return locations

    def chunk_exists(self, chunk_id):
        # Note: regular chunked grid has no bounds, so any chunk will exist.
        return True

    def get_chunk_of_loc(self, absolute_position, hint_chunk=None):
        return self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)

    def chunk_vec_to_buf(self, chunk_vec: np.ndarray):
        return self._vec2buf(chunk_vec)

    def get_entities_in_radius_chunked(self, chunk_id, offset, radius):
        # TODO: make this more performant
        # Determine radius-to-chunk-radius ratio, and grab surrounding chunks of relevance.
        # Use the chunk list to filter the _chunk dictionary, then calculate distances.
        center_chunk = self._buf2vec(chunk_id)
        entity_chunks = list(map(lambda e_cid: (e_cid[0], e_cid[1].absolute), self._obj_chunk.items()))
        entities, chunk_locs = map(np.array, zip(*entity_chunks))
        center_repeated = np.repeat([center_chunk], repeats=len(chunk_locs), axis=0)
        entity_distances = list(cubic_manhattan(chunk_locs, center_repeated, axis=1))

        # Ignore chunks over a certain distance (no possibility of any parts being in the radius).
        entity_distances = list(zip(entities, entity_distances, chunk_locs))
        return list(filter(lambda ed: ed[1] + self.chunk_radius <= radius, entity_distances))

    def at_chunked(self, chunk_id, offset: np.ndarray):
        chunk = self.chunks.get(chunk_id)
        if chunk is None:
            chunk = self._load_chunk(chunk_id)

        offset_key = self._vec2buf(offset)
        if offset_key not in chunk.pos_to_location:
            chunk.pos_to_location[offset_key] = Location()

        return chunk.pos_to_location.get(offset_key)

    def insert_chunked(self, chunk_id, offset: np.ndarray, entity_id):
        chunk_center = self._buf2vec(chunk_id)
        chunk = self.chunks.get(chunk_id)
        if chunk is None:
            chunk = self._load_chunk(chunk_id)

            # Check if chunk was not loaded. If so, just return.
            if chunk is None:
                return

        offset_key = self._vec2buf(offset)
        if offset_key not in chunk.pos_to_location:
            chunk.pos_to_location[offset_key] = Location()

        location = chunk.pos_to_location.get(offset_key)
        location.entities.add(entity_id)
        chunk.entity_to_pos[entity_id] = offset_key
        self._obj_chunk[entity_id] = ChunkDescriptor(chunk_id, offset_key)
        self.changes_delta.append(("insert", entity_id, chunk_center, offset))

    def get_chunk_offset(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        chunk_center = self._buf2vec(chunk_desc.chunk_id)
        chunk_offset = self._buf2vec(chunk_desc.offset)
        return chunk_center, chunk_offset

    # GridModel Implementation
    def location_exists(self, absolute_position, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        return self.chunk_exists(chunk_id)

    def get_entities_in_radius(self, absolute_position, radius, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        offset = self._buf2vec(chunk_id) - absolute_position
        return self.get_entities_in_radius_chunked(chunk_id, offset, radius)

    def at(self, absolute_position, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        offset = absolute_position - self._buf2vec(chunk_id)
        return self.at_chunked(chunk_id, offset)

    def insert(self, absolute_position, entity_id, hint_chunk=None):
        chunk_id = self._find_chunk_of_location(absolute_position, starting_chunk=hint_chunk)
        offset = self._buf2vec(chunk_id) - absolute_position
        return self.insert_chunked(chunk_id, offset, entity_id)

    def remove(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        if chunk_desc is None:
            raise Exception("Attempted query for an object that does not exist.")

        # Load the chunk if it isn't already loaded.
        chunk_id = chunk_desc.chunk_id
        chunk_center = chunk_desc.chunk_vec
        chunk = self.chunks.get(chunk_id)
        if chunk is None:
            chunk = self._load_chunk(chunk_id)

        loc = chunk.entity_to_pos.pop(entity_id, None)
        if loc is None:
            raise Exception("Entity exists in chunk map but not in the chunk.")

        loc_contents = chunk.pos_to_location.get(loc)
        if loc_contents is None:
            raise Exception("Location is empty.")

        # Remove the entity.
        offset = chunk_desc.offset_vec
        self._obj_chunk.pop(entity_id, None)
        loc_contents.entities.remove(entity_id)

        self.changes_delta.append(("remove", entity_id, chunk_center, offset))

    def get_location(self, entity_id):
        chunk_desc = self._obj_chunk.get(entity_id)
        chunk_center = self._buf2vec(chunk_desc.chunk_id)
        chunk_offset = self._buf2vec(chunk_desc.offset)
        return chunk_center + chunk_offset

    def move(self, entity_id, vec: np.ndarray):
        """
        Shorthand for remove-insert with a vector.
        """
        # Skip empty moves.
        if (vec == np.array([0, 0, 0])).all():
            return

        curr_chunk = self._obj_chunk.get(entity_id)
        dest_chunk_id = curr_chunk.chunk_id
        new_offset = curr_chunk.offset_vec + vec

        # Determine the destination chunk
        if self.chunk_radius < cubic_manhattan(curr_chunk.chunk_vec, new_offset):
            # Compute offset and chunk from absolute.
            absolute = curr_chunk.chunk_vec + new_offset
            dest_chunk_id = self.get_chunk_of_loc(absolute, hint_chunk=curr_chunk.chunk_vec)
            dest_chunk_vec = self._buf2vec(dest_chunk_id)
            new_offset = absolute - dest_chunk_vec

        # Remove the entity from the original location.
        self.remove(entity_id)

        # Add it to the new location.
        self.insert_chunked(dest_chunk_id, new_offset, entity_id)
