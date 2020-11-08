import numpy as np
import math
import copy
from utility.coordinates import *


class GridModel:
    def __init__(self, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size

        self.changes_delta = []

        # Create flat internal list: loc = (x, y) -> flat((x,y)) = x + y*x_size
        # unflat(n) -> (n % x_size, floor(n / x_size))
        # e.g. grid(10,10) -> flat((1,1)) = 1 + 1*10 = 11
        # grid(10,10) -> unflat(25) = -> (25 % 10, 25/10) = (5, 2) | flat(5, 2) = 5 + 2*10 = 25
        self._grid = [list() for _ in range((x_size * y_size))]
        self._obj_loc = {}

    def duplicate(self):
        g = GridModel(self.x_size, self.y_size)
        g._grid = copy.deepcopy(self._grid)
        g._obj_loc = copy.deepcopy(self._obj_loc)

        return g

    # TODO: this will have a "radius" parameter (L1 norm / manhattan) in the future to support large grids.
    #   The radius will serve as a query parameter for the DB later, as to not pull in more chunks.
    def get_contents(self):
        flat_contents = copy.deepcopy(self._obj_loc)
        contents = {k: self._unflat(v) for k, v in flat_contents.items()}
        return contents

    def _flat(self, loc: np.ndarray):
        offset_coord = loc
        if len(loc) == 3:
            offset_coord = cube_to_offset(loc)

        return offset_coord[0] + offset_coord[1] * self.x_size

    def _unflat(self, unflat_loc: int):
        unflat_offset = unflat_loc % self.x_size, math.floor(unflat_loc / self.x_size)
        return offset_to_cube(unflat_offset)

    def _at_tup(self, loc: np.ndarray) -> list:
        return self._grid[self._flat(loc)]

    def _at_flat(self, flat_loc: int) -> list:
        return self._grid[flat_loc]

    def at(self, loc: np.ndarray):
        return copy.deepcopy(self._at_tup(loc))

    def insert(self, loc: np.ndarray, obj_id):
        cubic_coord = loc
        if len(loc) == 2:
            cubic_coord = offset_to_cube(loc)

        self._at_tup(cubic_coord).append(obj_id)
        self._obj_loc[obj_id] = self._flat(cubic_coord)
        self.changes_delta.append(("insert", obj_id, cubic_coord))

    def remove(self, obj_id):
        flat_loc = self._obj_loc[obj_id]
        self._obj_loc.pop(obj_id)
        self._at_flat(flat_loc).remove(obj_id)
        self.changes_delta.append(("remove", obj_id, flat_loc))

    def move(self, obj_id, vec: np.ndarray):
        """
        Shorthand for remove-insert with a vector.
        """
        loc = self.get_loc_of_obj(obj_id)
        new_loc = loc + vec
        if not self.exists(new_loc):
            return

        self.remove(obj_id)
        self.insert(new_loc, obj_id)

    def get_at_loc(self, loc: np.ndarray):
        return self._at_tup(loc).copy()

    def get_loc_of_obj(self, obj_id):
        return self._unflat(self._obj_loc[obj_id]) if obj_id in self._obj_loc else None

    def get_all(self):
        return copy.deepcopy(self._grid)

    def exists(self, loc: np.ndarray):
        xlated_loc = loc
        if len(loc) == 3:
            xlated_loc = cube_to_offset(loc)

        return 0 <= xlated_loc[0] < self.x_size and 0 <= xlated_loc[1] < self.y_size

