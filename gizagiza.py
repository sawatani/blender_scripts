import bpy
import bmesh
import math

from mathutils import Vector, Matrix


def get_nexts(vertex):
    results = []
    for link in vertex.link_edges:
        other = link.other_vert(vertex)
        if other and other.co:
            results.append(other)
    return results


def calc_distance(vert1, vert2):
    dx = vert1.co[0] - vert2.co[0]
    dy = vert1.co[1] - vert2.co[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def get_vector(vert1, vert2):
    dx = vert1.co[0] - vert2.co[0]
    dy = vert1.co[1] - vert2.co[1]
    t = -dx / dy
    s = calc_distance(vert1, vert2) / math.sqrt(t ** 2 + 1)
    return Vector([s, s * t, 0])


def move_vertex(vert, vector):
    print(f"Moving {vert} at {vert.co} by {vector}")
    vert.co += vector
    print(f"Moved {vert} at {vert.co}")


obj = bpy.context.active_object
bm = bmesh.from_edit_mesh(obj.data)

for active in bm.select_history:
    if active and isinstance(active, bmesh.types.BMVert):
        print(f"Active vertex: {active}")
        others = get_nexts(active)
        print(f"Nexts: {others}")
        v = get_vector(others[0], others[1])
        print(f"Vector: {v}")
        rate = -0.5
        delta = v * rate
        move_vertex(active, delta)

bpy.context.view_layer.update()
bmesh.update_edit_mesh(obj.data)
