import numpy as np


def cube_to_offset(cubic_coord: np.array):
    col = int(cubic_coord[0] + (cubic_coord[2] - (cubic_coord[2] & 1)) / 2)
    row = cubic_coord[2]
    return np.array((col, row))


def cubic_manhattan(c1: np.ndarray, c2: np.ndarray, axis=0):
    return np.linalg.norm(c2 - c1, ord=1, axis=axis) / 2


def offset_to_cube(offset_coord):
    x = int(offset_coord[0] - (offset_coord[1] - (offset_coord[1] & 1)) / 2)
    z = offset_coord[1]
    y = -x - z
    return np.array((x, y, z))
