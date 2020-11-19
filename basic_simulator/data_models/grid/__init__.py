import numpy as np
import math
import copy
from typing import Dict


from repositories.data_models import Database
import repositories.data_models.grid as grid_db_model
from utility.coordinates import *


class Location:
    def __init__(self):
        self.entities = set()

        # TODO: might change form when terrains are implemented
        self.terrain = set()


class GridModel:
    def __init__(self):
        self.changes_delta = []

    def _vec2buf(self, v: np.ndarray):
        return v.tobytes()

    def _buf2vec(self, buf: bytes):
        return np.frombuffer(buf, dtype=int)

    def location_exists(self, absolute_position):
        raise NotImplementedError()

    def get_entities_in_radius(self, absolute_position, radius):
        raise NotImplementedError()

    def at(self, absolute_position):
        raise NotImplementedError()

    def insert(self, absolute_position, entity_id):
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


