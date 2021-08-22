"""
表面にジグザグの折り目を入れる。

X軸を固定した平面として、横と縦に Z, Y 軸とする。
複数の面がY方向に連なっている状態を前提としている。
"""

import bpy
import bmesh


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


def sort_vertices_zy(vts):
    """
    複数の頂点を Z座標とY座標で並べ替える。
    ２次元配列にして、１次元目がY座標、２次元目がZ座標になる。
    """
    grouped = get_grouped_vertices(vts)
    grouped.sort(key=lambda ys: ys[0].co.y)
    return list(map(lambda ys: sorted(ys, key=lambda v: v.co.z), grouped))


def create_verts(bm, ncuts):
    """
    ncuts の数だけZ方向に辺を分割し、全ての頂点を２次元配列にまとめる。
    """
    yss = get_grouped_vertices(bm.verts)
    edges = sorted(map(get_vertices_edge, yss), key=lambda e: e.verts[0].co.y)
    for e in edges:
        bmesh.ops.subdivide_edges(bm, edges=[e], cuts=ncuts)
    return sort_vertices_zy(bm.verts)


def create_triangle_faces(yzs):
    pass

# Start
obj = bpy.context.active_object
print(f"Starting with: {obj}")
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)

yzs = create_verts(bm, 3)
create_triangle_faces(yzs)

# Finish
bpy.context.view_layer.update()
bmesh.update_edit_mesh(obj.data)
