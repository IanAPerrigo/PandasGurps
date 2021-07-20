import numpy as np
from typing import Dict

from utility.coordinates import *
from data_models.terrain.terrain import Terrain, MajorTerrain


class Location:
    def __init__(self):
        self.entities = set()

        self._major_terrain = None
        self._terrain = set()

    @property
    def major_terrain(self):
        return self._major_terrain

    @major_terrain.setter
    def major_terrain(self, val):
        if self._major_terrain in self._terrain:
            self.entities.remove(self._major_terrain)
            self._terrain.remove(self._major_terrain)

        self._major_terrain = val
        self.entities.add(val)
        self._terrain.add(val)

    @property
    def terrain(self):
        return tuple(self._terrain)

    def add_terrain(self, t: Terrain):
        if isinstance(t, MajorTerrain):
            self.major_terrain = t
        else:
            self.entities.add(t)
            self._terrain.add(t)

    def get_elevation(self):
        return self.major_terrain.elevation if self.major_terrain is not None else -1


class LocationDataDict(Dict[bytes, Location]):
    pass


class GridView:
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

    def at_key(self, loc_key):
        raise NotImplementedError()

    def get_location(self, entity_id):
        raise NotImplementedError()

    def watch(self, watcher_id):
        raise NotImplementedError()

    def get_deltas_for(self, watcher_id):
        raise NotImplementedError()

    def all(self):
        raise NotImplementedError()


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

