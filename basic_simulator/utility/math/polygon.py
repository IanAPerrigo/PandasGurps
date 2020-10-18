from math import cos, sin, pi
from kivy.graphics import Mesh


# def get_hexagon_points_for_size(size, center=(0, 0)):
#     points = []
#     for i in range(7):
#         angle_deg = 60 * i - 30
#         angle_rad = math.pi / 180 * angle_deg
#         points.append(int(center[0] + size * math.cos(angle_rad)))
#         points.append(int(center[1] + size * math.sin(angle_rad)))
#
#     return points

def regular_polygon_vertices(radius, sides, x, y):
    r = radius
    a = 2 * pi / sides
    offset_rad = pi / 180 * 30
    vertices = []
    for i in range(sides):
        vertices += [
            x + cos(i * a - offset_rad) * r,
            y + sin(i * a - offset_rad) * r,
            cos(i * a - offset_rad),
            sin(i * a - offset_rad),
        ]
    return vertices


def regular_polygon_indices(sides):
    return range(sides)