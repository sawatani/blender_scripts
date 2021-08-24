"""
表面にジグザグの折り目を入れて、頂点を交互に持ち上げてトゲトゲにする。

X軸を固定した平面として、横と縦に Z, Y 軸とする。
複数の面がY方向に連なっている状態を前提としている。
"""
import math

import bmesh
import bpy
from mathutils import Vector


def get_grouped_vertices(vts):
    """
    Y座標が同じ頂点をグループにする。
    """
    grp = {}
    for vt in vts:
        if vt.co.y in grp:
            grp[vt.co.y].append(vt)
        else:
            grp[vt.co.y] = [vt]
    return list(grp.values())


def get_vertices_edge(vts):
    """
    与えられた頂点がなす辺を返す。
    """
    origin, other = vts
    for e in origin.link_edges:
        v = e.other_vert(origin)
        if v == other:
            return e
    raise ValueError(f"No connection found: {vts}")


class VertYZ:
    """
    複数の頂点を Z座標とY座標で並べ替えた配列。
    ２次元配列にして、１次元目がY座標、２次元目がZ座標になる。
    """

    def __init__(self, lists_by_yz):
        self.lists = lists_by_yz

    def get_size_y(self):
        return len(self.lists)

    def get_size_z(self):
        return len(self.lists[0])

    def get(self, y, z):
        return self.lists[y][z]

    def get_next_y(self, y, z):
        if 0 < y < len(self.lists) - 1:
            return [self.lists[y - 1][z], self.lists[y + 1][z]]
        else:
            return None

    def get_left_bottom(self, face_y, face_z):
        return self.lists[face_y][face_z]

    def get_left_top(self, face_y, face_z):
        return self.lists[face_y][face_z + 1]

    def get_right_bottom(self, face_y, face_z):
        return self.lists[face_y + 1][face_z]

    def get_right_top(self, face_y, face_z):
        return self.lists[face_y + 1][face_z + 1]


def sort_vertices_zy(vts):
    """
    複数の頂点を Z座標とY座標で並べ替え VertYZ として返す。
    """
    grouped = get_grouped_vertices(vts)
    grouped.sort(key=lambda ys: ys[0].co.y)
    lists = list(map(lambda ys: sorted(ys, key=lambda v: v.co.z), grouped))
    return VertYZ(lists)


def create_verts(bm, ncuts):
    """
    ncuts の数だけZ方向に辺を分割し、全ての頂点を VertYZ にまとめる。
    """
    yss = get_grouped_vertices(bm.verts)
    edges = sorted(map(get_vertices_edge, yss), key=lambda e: e.verts[0].co.y)
    for e in edges:
        bmesh.ops.subdivide_edges(bm, edges=[e], cuts=ncuts)
    return sort_vertices_zy(bm.verts)


def create_triangle_faces(yzs: VertYZ):
    """
    VertYZ の頂点でジグザグに面を作成する。
    """
    bpy.ops.mesh.select_mode(type="VERT")

    def mk_face(*verts):
        bpy.ops.mesh.select_all(action="DESELECT")
        for v in verts:
            v.select = True
        bpy.ops.mesh.vert_connect()

    for iy in range(yzs.get_size_y() - 1):
        for iz in range(yzs.get_size_z() - 1):
            if (iy + iz) % 2 == 0:
                base = [
                    yzs.get_left_top(iy, iz),
                    yzs.get_right_bottom(iy, iz),
                ]
                mk_face(yzs.get_left_bottom(iy, iz), *base)
                mk_face(yzs.get_right_top(iy, iz), *base)
            else:
                base = [
                    yzs.get_right_top(iy, iz),
                    yzs.get_left_bottom(iy, iz),
                ]
                mk_face(yzs.get_right_bottom(iy, iz), *base)
                mk_face(yzs.get_left_top(iy, iz), *base)


def make_togetoge(yzs: VertYZ, rate):
    """
    VertYZ の頂点をトゲトゲになるようにX,Y軸の法線方向に動かす。
    動かす大きさは {両隣の頂点の距離} * rate で指定される。
    """

    def get_vector(vert1, vert2):
        dx = vert1.co[0] - vert2.co[0]
        dy = vert1.co[1] - vert2.co[1]
        t = -dx / dy
        s = math.sqrt((dx ** 2 + dy ** 2) / (t ** 2 + 1))
        return Vector([s, s * t, 0]) * rate

    def move_vertex(y, z):
        vert = yzs.get(y, z)
        nexts = yzs.get_next_y(y, z)
        if nexts:
            vert.co += get_vector(*nexts)

    for start in [0, 1]:
        for iy in range(start, yzs.get_size_y(), 2):
            for iz in range(start, yzs.get_size_z(), 2):
                move_vertex(iy, iz)


obj = bpy.context.active_object
print(f"Starting with: {obj}")
try:
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)

    yzs = create_verts(bm, 3)
    create_triangle_faces(yzs)
    make_togetoge(yzs, -0.5)
finally:
    bpy.context.view_layer.update()
    bmesh.update_edit_mesh(obj.data)
