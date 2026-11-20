import bpy, sys
from mathutils import Vector
SRC, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
ob = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
for o in list(bpy.context.scene.objects):
    if o is not ob: bpy.data.objects.remove(o)
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
ob.parent = None; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
ws = [Vector(v.co) for v in ob.data.vertices]
lo = Vector([min(v[i] for v in ws) for i in range(3)]); hi = Vector([max(v[i] for v in ws) for i in range(3)])
H = hi.z - lo.z; k = 2.2 / H  # 2.2 m tall, feet on the floor, centred
for v in ob.data.vertices: v.co = Vector(((v.co.x - (lo.x + hi.x) / 2) * k, (v.co.y - (lo.y + hi.y) / 2) * k, (v.co.z - lo.z) * k))
ob.data.update()
r = ob.modifiers.new('remesh', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = .011; r.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier='remesh')
print('after remesh', len(ob.data.polygons))
d = ob.modifiers.new('dec', 'DECIMATE'); d.ratio = min(1, 60000 / len(ob.data.polygons))
bpy.ops.object.modifier_apply(modifier='dec')
bpy.ops.object.shade_smooth()
ob.name = 'Brakk'; ob.data.name = 'BrakkMesh'
print('faces', len(ob.data.polygons), 'verts', len(ob.data.vertices))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
