import numpy as np
from typing import Dict

from utility.coordinates import *


class Location:
    def __init__(self):
        self.entities = set()

        self.major_terrain = None

        # TODO: might change form when terrains are implemented
        self.terrain = set()

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

