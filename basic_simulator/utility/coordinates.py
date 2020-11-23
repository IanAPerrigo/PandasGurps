from typing import Iterator
from functools import partial

import numpy as np
import heapq
import collections


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


# Ray-casting is much faster than A* for LOS calculations.
def cube_round(v: np.ndarray):
    vr = np.round(v)
    vd = vr - v
    if vd[0] > vd[1] and vd[0] > vd[2]:
        vr[0] = -vr[1]-vr[2]
    elif vd[1] > vd[2]:
        vr[1] = -vr[0]-vr[2]
    else:
        vr[2] = -vr[0]-vr[1]
    return vr.astype(int)


def lerp(v1: np.ndarray, v2: np.ndarray, t: float):
    return cube_round(v1 + (v2 - v1) * t)
    #return v1 + (v2 - v1) * t


def cast_hex_ray(v1: np.ndarray, v2: np.ndarray):
    n = cubic_manhattan(v1, v2)
    partial_lerp = partial(lerp, v1, v2)
    lerp_intervals = np.array([float(i) / n for i in range(int(n) + 1)])

    return np.array(list(map(partial_lerp, lerp_intervals)))

import timeit
v1 = np.array([0,0,0])
v2 = np.array([1,-3,2]) * 1
results = timeit.timeit(lambda: cast_hex_ray(v1, v2), number=100)
print(results / 100)