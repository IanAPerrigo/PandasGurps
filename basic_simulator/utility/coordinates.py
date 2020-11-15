import numpy as np


def cube_to_offset(cubic_coord: np.array):
    col = int(cubic_coord[0] + (cubic_coord[2] - (cubic_coord[2] & 1)) / 2)
    row = cubic_coord[2]
    return np.array((col, row))


def slow_cubic_manhattan(c1: np.ndarray, c2: np.ndarray, axis=0):
    return np.linalg.norm(c2 - c1, ord=1, axis=axis) / 2


def cubic_manhattan(c1: np.ndarray, c2: np.ndarray, axis=0):
    return np.absolute(c2 - c1).sum(axis=axis) / 2


cubic_neighbors = [
    np.array([1, 0, -1]),
    np.array([1, -1, 0]),
    np.array([0, -1, 1]),
    np.array([-1, 0, 1]),
    np.array([-1, 1, 0]),
    np.array([0, 1, -1]),
]


# TODO: Incorrect
offset_neighbors = [
    cube_to_offset(np.array([1, 0, -1])),
    cube_to_offset(np.array([1, -1, 0])),
    cube_to_offset(np.array([0, -1, 1])),
    cube_to_offset(np.array([-1, 0, 1])),
    cube_to_offset(np.array([-1, 1, 0])),
    cube_to_offset(np.array([0, 1, -1])),
]


def cubic_ring(center: np.ndarray, radius):
    results = []
    current_hex = center + cubic_neighbors[4] * radius

    for i in range(6):
        for _ in range(radius):
            results.append(current_hex)
            current_hex = current_hex + cubic_neighbors[i]

    return results


def cubic_spiral(center: np.ndarray, radius):
    results = [center]
    for i in range(1, radius):
        results.extend(cubic_ring(center, i))
    return results


def offset_spiral(center: np.ndarray, radius):
    c_spiral = cubic_spiral(center, radius)
    return list(map(lambda c: cube_to_offset(c), c_spiral))


def offset_to_cube(offset_coord):
    x = int(offset_coord[0] - (offset_coord[1] - (offset_coord[1] & 1)) / 2)
    z = offset_coord[1]
    y = -x - z
    return np.array((x, y, z))
