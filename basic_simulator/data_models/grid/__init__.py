import numpy as np
from typing import Dict

from utility.coordinates import *


class Location:
    def __init__(self):
        self.entities = set()

        # TODO: might change form when terrains are implemented
        self.terrain = set()


class LocationDataDict(Dict[bytes, Location]):
    pass


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


