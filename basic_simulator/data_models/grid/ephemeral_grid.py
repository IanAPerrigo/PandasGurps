import numpy as np

from . import GridModel, GridView, LocationDataDict, Location
from utility.coordinates import cubic_spiral, in_spiral


class SubjectiveLocation(Location):
    def __init__(self, source_location: Location):
        super(SubjectiveLocation, self).__init__()
        self._source_location = source_location

        # Fields are objective, and are inherited from the source location.
        self.terrain = source_location.terrain
        self.major_terrain = source_location.major_terrain


class SubjectiveGridModel(GridModel):

    cache_missed = 0
    cache_hit = 0

    def __init__(self, source_grid: GridModel, fov=10):
        super(SubjectiveGridModel, self).__init__()

        self._source_grid = source_grid
        self._locations = LocationDataDict()
        self._obj_loc_key = {}

        # Spiral vector of all visible areas (centered at zero).
        self.field_of_view = cubic_spiral(np.zeros(3), fov)

        # Vector pointing to the location of the subject.
        self._subject_location = np.empty(3)

        self._cached_fov = {}
        self._fov_keys = set()

    def fov_keys(self):
        return self._fov_keys

    @property
    def subject_location(self):
        return self._subject_location

    @subject_location.setter
    def subject_location(self, value):
        # Do nothing if there is no change.
        if (value == self._subject_location).all():
            return

        self._subject_location = value

        self._cached_fov.clear()

        # Refresh the fov keys
        # TODO: njit repeated add for performance
        self._fov_keys = set((p + value).tobytes() for p in self.field_of_view)

        # Cull entities out of FOV.
        for entity in self._obj_loc_key.keys():
            loc_key = self._obj_loc_key[entity]
            pos = self._buf2vec(loc_key)
            if not self._pos_in_fov(pos):
                self._obj_loc_key.pop(entity)
                self._locations[loc_key].entities.remove(entity)

    # TODO: not exactly streamlined for changing FOV.
    def _pos_in_fov(self, absolute_position: np.ndarray, loc_key=None):
        relative_location = absolute_position - self._subject_location
        loc_key = self._vec2buf(relative_location) if loc_key is None else loc_key
        ce = self._cached_fov.get(loc_key)
        if ce is not None:
            self.cache_hit += 1
            return ce
        else:
            self.cache_missed += 1
            e = in_spiral(relative_location, self.field_of_view)
            self._cached_fov[loc_key] = e
            return e

    def location_exists(self, absolute_position):
        return self._vec2buf(absolute_position) in self._locations

    def remove(self, entity_id):
        if entity_id not in self._obj_loc_key:
            return

        loc_key = self._obj_loc_key.pop(entity_id)
        self._locations[loc_key].entities.remove(entity_id)

    def get_location(self, entity_id):
        location_key = self._obj_loc_key.get(entity_id)
        if location_key is None:
            return None

        return self._buf2vec(location_key)

    def move(self, entity_id, vec: np.ndarray):
        if (vec == np.array([0, 0, 0])).all():
            return

        old_loc_key = self._obj_loc_key[entity_id]
        new_loc = self._buf2vec(old_loc_key) + vec
        self.remove(entity_id)
        self.insert(new_loc, entity_id)

    def get_entities_in_radius(self, absolute_position, radius):
        raise NotImplementedError()

    def at(self, absolute_position):
        loc_key = self._vec2buf(absolute_position)

        # Return nothing if the location is OOB.
        if not self._pos_in_fov(absolute_position, loc_key=loc_key):
            return

        return self._load_loc(absolute_position, loc_key=loc_key)

    def _load_loc(self, absolute_position, loc_key=None):
        # If a subjective location was already loaded, display the loaded location.
        loc_key = self._vec2buf(absolute_position) if loc_key is None else loc_key
        if loc_key not in self._locations:
            # Expensive call to the ground truth.
            gt_loc = self._source_grid.at(absolute_position)
            new_loc = SubjectiveLocation(source_location=gt_loc)
            self._locations[loc_key] = new_loc
            return new_loc

        return self._locations[loc_key]

    def insert(self, absolute_position, entity_id):
        loc_key = self._vec2buf(absolute_position)

        if entity_id in self._obj_loc_key:
            old_loc_key = self._obj_loc_key[entity_id]
            self._locations[old_loc_key].entities.remove(entity_id)

        self._obj_loc_key[entity_id] = loc_key

        loaded_loc = self._load_loc(absolute_position)
        loaded_loc.entities.add(entity_id)


class SubjectiveLocationView:
    def __init__(self, source_location: Location):
        self._source_location = source_location
        self._entities = source_location.entities
        self._terrain = source_location.terrain
        self.major_terrain = source_location.major_terrain

    @property
    def entities(self):
        # Return immutable set
        return tuple(self._entities)

    @entities.setter
    def entities(self, value):
        raise NotImplementedError()

    @property
    def terrain(self):
        # Return immutable set
        return tuple(self._terrain)

    @terrain.setter
    def terrain(self, value):
        raise NotImplementedError()


class SubjectiveGridView(GridView):
    """
    Class that supports non-mutable operations on a grid, and is optimized for only reading operations.
    """
    def __init__(self, source_grid: SubjectiveGridModel):
        self._source_grid = source_grid
        self._subjective_locations = {}

    def _vec2buf(self, v: np.ndarray):
        return v.tobytes()

    def _buf2vec(self, buf: bytes):
        return np.frombuffer(buf, dtype=int)

    def populate(self):
        """
        Refresh the view to be synced up with changes in FOV.
        :return:
        """
        # TODO: currently inefficient, keysets are around 300 entries, might be easier to track the deltas another way.
        #   Costs roughly 150 ticks/s

        # Updates the locations dictionary
        tracked_keys = set(self._subjective_locations.keys())
        current_keys = self._source_grid.fov_keys()
        locs_to_remove = tracked_keys.difference(current_keys)
        locs_to_add = current_keys.difference(tracked_keys)

        for k in locs_to_remove:
            self._subjective_locations.pop(k)

        for k in locs_to_add:
            ab_p = self._buf2vec(k)
            self._load_loc(ab_p, loc_key=k)

        # loc_copy = {}
        #
        # for k in self._source_grid.fov_keys():
        #     if k in self._subjective_locations:
        #         loc_copy[k] = self._subjective_locations[k]
        #     else:
        #         ab_p = self._buf2vec(k)
        #         loc_copy[k] = self._get_not_load_loc(ab_p, loc_key=k)
        #
        # self._subjective_locations = loc_copy

    def location_exists(self, absolute_position):
        return self._source_grid.location_exists(absolute_position)

    def get_location(self, entity_id):
        eph_loc_key = self._source_grid.get_location(entity_id)
        return self._buf2vec(eph_loc_key)

    def get_entities_in_radius(self, absolute_position, radius):
        raise NotImplementedError()

    def at(self, absolute_position):
        """
        Given the absolute position, return the location object for that point.
        Keep an internal cache of loaded locations
        :param absolute_position:
        :return:
        """
        loc_key = self._vec2buf(absolute_position)
        return self._load_loc(absolute_position, loc_key=loc_key)

    def _get_not_load_loc(self, absolute_position, loc_key=None):
        loc_key = self._vec2buf(absolute_position) if loc_key is None else loc_key
        if loc_key in self._subjective_locations:
            return self._subjective_locations[loc_key]

        eph_loc = self._source_grid.at(absolute_position)
        return SubjectiveLocationView(eph_loc)

    def _load_loc(self, absolute_position, loc_key=None):
        loc_key = self._vec2buf(absolute_position) if loc_key is None else loc_key
        if loc_key in self._subjective_locations:
            return self._subjective_locations[loc_key]

        sub_loc = self._get_not_load_loc(absolute_position, loc_key)
        self._subjective_locations[loc_key] = sub_loc
        return sub_loc

    def all(self):
        return self._subjective_locations
