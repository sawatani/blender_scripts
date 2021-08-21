import bpy

obj = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')

print(f"Active object: {obj}")

