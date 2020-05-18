import numpy as np


def cube_to_offset(cubic_coord: np.ndarray):
    col = int(cubic_coord[0] + (cubic_coord[2] - (cubic_coord[2] & 1)) / 2)
    row = cubic_coord[2]
    return col, row


def offset_to_cube(offset_coord):
    x = int(offset_coord[0] - (offset_coord[1] - (offset_coord[1] & 1)) / 2)
    z = offset_coord[1]
    y = -x - z
    return x, y, z
