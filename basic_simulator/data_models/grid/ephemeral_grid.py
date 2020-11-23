import numpy as np

from . import GridModel, LocationDataDict, Location


class EphemeralGridModel(GridModel):
    def __init__(self):
        super(EphemeralGridModel, self).__init__()

        self._locations = LocationDataDict()
        self._obj_loc = {}

    def location_exists(self, absolute_position):
        return self._vec2buf(absolute_position) in self._locations

    def remove(self, entity_id):
        if entity_id not in self._obj_loc:
            return

        loc_key = self._obj_loc.pop(entity_id)
        self._locations[loc_key].entities.remove(loc_key)

    def get_location(self, entity_id):
        return self._obj_loc[entity_id]

    def move(self, entity_id, vec: np.ndarray):
        if (vec == np.array([0, 0, 0])).all():
            return

        old_loc_key = self._obj_loc[entity_id]
        new_loc = self._buf2vec(old_loc_key) + vec
        self.remove(entity_id)
        self.insert(new_loc, entity_id)

    def get_entities_in_radius(self, absolute_position, radius):
        raise NotImplementedError()

    def at(self, absolute_position):
        loc_key = self._vec2buf(absolute_position)
        return self._locations[loc_key]

    def insert(self, absolute_position, entity_id):
        loc_key = self._vec2buf(absolute_position)
        self._obj_loc[entity_id] = loc_key
        if loc_key not in self._locations:
            self._locations[loc_key] = Location()
        self._locations[loc_key].entities.add(entity_id)

