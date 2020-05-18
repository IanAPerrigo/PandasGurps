


# import pyglet
# from pyglet.gl import *
# from pyglet.graphics import Batch
# from pyglet.window import key
# import random

# from math import *

# from components import Vector, Behavior


# class HumanActor(Behavior):

#     # TODO: current game state provided by injected object.

#     def __init__(self, id, key_map):
#         super(HumanActor, self).__init__()
#         self.id = id
#         self.key_map = key_map

#     def update(self):
#         # TODO:  grab the game state.
#         if self.key_map.get(key.UP):
#             self.key_map.pop(key.UP)
#             return [1]
#         elif self.key_map.get(key.DOWN):
#             self.key_map.pop(key.DOWN)
#             return [2]
#         elif self.key_map.get(key.RIGHT):
#             self.key_map.pop(key.RIGHT)
#             return [3]
#         elif self.key_map.get(key.LEFT):
#             self.key_map.pop(key.LEFT)
#             return [4]
#         elif self.key_map.get(key.N):
#             self.key_map.pop(key.N)
#             return [-1]

#         return None


# class SimpleActor(Behavior):
#     def __init__(self, id):
#         super(SimpleActor, self).__init__()
#         self.id = id

#     def update(self):
#         moves = [random.randint(0, 4) for _ in range(4)] + [-1]
#         return moves


# class ActorComponent(Vector):
#     def __init__(self, position, scale, color):
#         super(ActorComponent, self).__init__(position, scale)
#         self.color = color
#         self.batch = Batch()
#         self.group = None
#         self.icon = None
#         self.update_graphics()

#     def clear(self):
#         if self.icon is not None:
#             self.icon.delete()
#             self.icon = None

#     def update_graphics(self):
#         self.clear()

#         circle, indices = self.create_indexed_vertices(sides=100)
#         vertex_count = len(circle) // 2
#         self.icon = self.batch.add_indexed(vertex_count, pyglet.gl.GL_TRIANGLES, self.group,
#                                         indices,
#                                         ('v2f', circle),
#                                         ('c4f', (self.color[0], self.color[1], self.color[2], 0.9) * vertex_count))

#     def create_indexed_vertices(self, sides=24):
#         vertices = [self.position[0], self.position[1]]
#         for side in range(sides):
#             angle = side * 2.0 * pi / sides
#             vertices.append(self.position[0] + cos(angle) * (self.scale / 2))
#             vertices.append(self.position[1] + sin(angle) * (self.scale / 2))
#         # Add a degenerated vertex
#         vertices.append(self.position[0] + cos(0) * (self.scale / 2))
#         vertices.append(self.position[1] + sin(0) * (self.scale / 2))

#         indices = []
#         for side in range(1, sides + 1):
#             indices.append(0)
#             indices.append(side)
#             indices.append(side + 1)
#         return vertices, indices

#     def draw(self):
#         glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
#         glColor3f(self.color[0], self.color[1], self.color[2])
#         self.batch.draw()
