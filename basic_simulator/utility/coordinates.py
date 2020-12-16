from typing import Iterator
from functools import partial

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, Point3
from panda3d.bullet import BulletWorld, BulletCylinderShape, BulletRigidBodyNode, YUp

from numba import jit, njit, vectorize, prange

import numpy as np
import heapq
import collections


@njit
def cube_to_offset(cubic_coord: np.ndarray):
    result = np.empty(2, dtype=np.int32)
    result[0] = int(cubic_coord[0] + (cubic_coord[2] - (cubic_coord[2] & 1)) / 2)
    result[1] = cubic_coord[2]
    return result


@njit
def cubic_manhattan(c1: np.ndarray, c2: np.ndarray, axis=0):
    return np.absolute(c2 - c1).sum(axis=axis) / 2

cubic_neighbors = np.array([
    np.array([1, 0, -1]),
    np.array([1, -1, 0]),
    np.array([0, -1, 1]),
    np.array([-1, 0, 1]),
    np.array([-1, 1, 0]),
    np.array([0, 1, -1]),
])


# TODO: Incorrect
offset_neighbors = [
    cube_to_offset(np.array([1, 0, -1])),
    cube_to_offset(np.array([1, -1, 0])),
    cube_to_offset(np.array([0, -1, 1])),
    cube_to_offset(np.array([-1, 0, 1])),
    cube_to_offset(np.array([-1, 1, 0])),
    cube_to_offset(np.array([0, 1, -1])),
]


@njit
def cubic_ring(center: np.ndarray, radius):
    current_hex = center + cubic_neighbors[4] * radius

    results = np.empty((radius * 6, 3), dtype=np.int32)
    for i in prange(6):
        for _ in prange(radius):
            results[_ + radius * i] = current_hex
            current_hex = current_hex + cubic_neighbors[i]

    return results


@njit
def cubic_spiral(center: np.ndarray, radius):
    results = np.empty((1, 3), dtype=np.int32)
    results[0] = center
    for i in prange(1, radius):
        results = np.append(results, cubic_ring(center, i), axis=0)
    return results


def in_spiral(vector: np.ndarray, rows: np.ndarray):
    return np.equal(rows, vector).all(1).any()


def offset_spiral(center: np.ndarray, radius):
    c_spiral = cubic_spiral(center, radius)
    return list(map(lambda c: cube_to_offset(c), c_spiral))


def offset_to_cube(offset_coord):
    x = int(offset_coord[0] - (offset_coord[1] - (offset_coord[1] & 1)) / 2)
    z = offset_coord[1]
    y = -x - z
    return np.array((x, y, z))


class AStarNode:
    def __init__(self, pos: np.ndarray):
        self.pos = pos
        self.H = None
        self.parent = None

    def __hash__(self):
        return hash(self.pos.tobytes())

    def __eq__(self, other):
        return (self.pos == other.pos).all()

    def __ne__(self, other):
        return (self.pos != other.pos).any()

    def __lt__(self, other):
        return self.H < other.H

    def __str__(self):
        return str(self.pos)


def a_star(graph, current: AStarNode, end: AStarNode, heuristic):
    open_set = set()
    open_heap = []
    closed_set = set()

    def retrace_path(c):
        path = [c]
        while c.parent is not None:
            c = c.parent
            path.append(c)
        path.reverse()
        return path

    open_set.add(current)
    open_heap.append((0, current))
    while open_set:
        current = heapq.heappop(open_heap)[1]
        if current == end:
            return retrace_path(current)
        open_set.remove(current)
        closed_set.add(current)
        for tile in graph[current.pos]:
            if tile not in closed_set:
                tile.H = heuristic(current.pos, end.pos)
                if tile not in open_set:
                    open_set.add(tile)
                    heapq.heappush(open_heap, (tile.H, tile))
                tile.parent = current
    return []


class NeighborGraph(collections.MutableMapping):
    def __init__(self, neighbor_vectors: np.ndarray):
        self.neighbor_vectors = neighbor_vectors
        self.cached_neighbors = {}
        self.nodes = dict()

    def __setitem__(self, k, v) -> None:
        pass

    def __delitem__(self, v) -> None:
        pass

    def __getitem__(self, pos):
        pos_key = pos.tobytes()
        if pos_key in self.cached_neighbors:
            return self.cached_neighbors[pos_key]

        pos_repeat = np.repeat([pos], self.neighbor_vectors.shape[0], axis=0)
        ns = list(map(lambda n: AStarNode(n), pos_repeat + self.neighbor_vectors))

        new_ns = []
        for n in ns:
            existing_n = self.nodes.get(n, None)
            if existing_n is None:
                existing_n = n
                self.nodes[n] = n
            new_ns.append(existing_n)

        self.cached_neighbors[pos_key] = new_ns
        return new_ns

    def __len__(self) -> int:
        return len(self.cached_neighbors)

    def __iter__(self) -> Iterator:
        return iter(self.cached_neighbors)


# Example of a_star usage
# import timeit
#
# def heuristic(v1, v2):
#     rand = np.random.random()
#     rand = 0
#     l1 = cubic_manhattan(v1, v2) + rand
#     return l1
#
# neighbors = np.array(cubic_neighbors)
# graph = NeighborGraph(neighbors)
#
# start = AStarNode(np.array([0,0,0]))
# end = AStarNode(np.array([200,0,-200]))
#
# number = 1
#
# a = timeit.timeit(lambda: a_star(graph, start, end, heuristic), number=number)
# b = timeit.timeit(lambda: a_star(graph, start, end, heuristic), number=number)
#
# print("done: a %s" % (a / number))
# print("done: b %s" % (b / number))

@njit
def round_vec(vr: np.ndarray, vd: np.ndarray):
    if vd[0] > vd[1] and vd[0] > vd[2]:
        vr[0] = -vr[1]-vr[2]
    elif vd[1] > vd[2]:
        vr[1] = -vr[0]-vr[2]
    else:
        vr[2] = -vr[0]-vr[1]

    return vr


# Ray-casting is much faster than A* for LOS calculations.
@njit
def cube_round(v: np.ndarray):
    vr = np.empty_like(v)
    np.round(v, 0, vr)
    vd = vr - v
    vr_vd_stack = np.dstack((vr, vd))

    r_vr = np.zeros_like(v)
    for ii, vr_vd in enumerate(vr_vd_stack):
        _ = vr_vd.T
        rv = round_vec(_[0], _[1])
        r_vr[ii] = rv

    return r_vr.astype(np.int32)


@njit
def cast_hex_ray(v1: np.ndarray, v2: np.ndarray):
    n = cubic_manhattan(v1, v2)
    if n == 0:
        shortest_path = np.empty((2, 3), dtype=np.int32)
        shortest_path[0] = v1.astype(np.int32)
        shortest_path[1] = v2.astype(np.int32)
        return shortest_path

    v1 = v1 + np.array([1e-6, 2e-6, -3e-6])
    v2 = v2 + np.array([1e-6, 2e-6, -3e-6])

    lerp_count = int(n) + 1
    lerp_intervals = np.empty((lerp_count, 1))
    for ii, _ in enumerate(range(lerp_count)):
        lerp_intervals[ii] = np.array(float(_) / n)

    lerp_shape = (lerp_intervals.shape[0], 3)
    V1 = np.empty(lerp_shape)
    for ii, v in enumerate(lerp_intervals):
        V1[ii] = np.expand_dims(v1, axis=0)

    V21 = np.empty(lerp_shape)
    for ii, v in enumerate(lerp_intervals):
        V21[ii] = np.expand_dims(v2 - v1, axis=0)

    return cube_round(V1 + (V21 * lerp_intervals))


@njit
def elem_dot_matrix_with_vector(mat: np.ndarray, vec: np.ndarray):
    mat_f, vec_f = mat.astype(np.float64), vec.astype(np.float64)
    result = np.empty(mat_f.shape[0])
    for ii, row in enumerate(mat_f):
        result[ii] = np.dot(row, vec_f)
    return result.astype(np.int32)


@njit
def get_new_center_offset_for_dir(mat: np.ndarray, center: np.ndarray, offset: np.ndarray):
    results = np.empty((3, 3), dtype=np.int32)
    dot_prod = elem_dot_matrix_with_vector(mat, offset)

    max_dir = np.argmax(dot_prod)
    new_center = center + mat[max_dir]
    results[2] = np.repeat(max_dir, 3)
    results[1] = (center + offset) - new_center
    results[0] = new_center
    return results


# Initialization of njit functions (required to compile them)
v = np.array([1, 0, -1])
c2 = cube_to_offset(v)

center = np.array([0, 0, 0])
radius = 1
c1 = cubic_ring(center, radius)
s1 = cubic_spiral(center, radius)

u = np.random.randint(0, 100, size=(2, 3))
cubic_manhattan(u[0], u[1])
cast_hex_ray(u[0], u[1])

mat = cubic_neighbors
vec = np.array([0, -2, 2])
center = np.array([0, 0, 0])
get_new_center_offset_for_dir(mat, center, vec)
