import bpy, sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Triad-fury/375957ce-c9ac-5e44-a0af-d71998c19d28/scratchpad/hy')
from mathutils import Vector
from poses import POSE, apply
SRC, OUT, NAMES = sys.argv[-3], sys.argv[-2], sys.argv[-1].split(',')
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene; ao = bpy.data.objects['BrakkRig']
for nm, loc, e, col in [('key', (-2.5, -3.5, 4), 900, (1, .9, .8)), ('rim', (2.5, 3, 2.5), 600, (1, .45, .15)), ('fill', (3.5, -2.5, 1.5), 250, (.6, .7, 1))]:
    L = bpy.data.lights.new(nm, 'AREA'); L.energy = e; L.color = col; L.size = 3; o = bpy.data.objects.new(nm, L); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1.1)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (.05, .05, .06, 1)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 85
cam.location = Vector((.6, -6.5, 1.5)); cam.rotation_euler = (Vector((.2, 0, 1.25)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 10; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 420, 520
for i, n in enumerate(NAMES):
    apply(ao, POSE[n]); bpy.context.view_layer.update()
    sc.render.filepath = f'{OUT}_{i}_{n}.png'; bpy.ops.render.render(write_still=True)
print('DONE')
