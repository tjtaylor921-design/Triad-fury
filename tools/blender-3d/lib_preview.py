import bpy, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Triad-fury/375957ce-c9ac-5e44-a0af-d71998c19d28/scratchpad/hy')
from mathutils import Vector
from poses3 import POSES, ORDER, apply
SRC, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene; ao = bpy.data.objects['BrakkRig']
for nm, loc, e, col in [('key', (-2.5, -3.5, 4), 900, (1, .9, .8)), ('rim', (2.5, 3, 2.5), 600, (1, .45, .15)), ('fill', (3.5, -2.5, 1.5), 250, (.6, .7, 1))]:
    Lg = bpy.data.lights.new(nm, 'AREA'); Lg.energy = e; Lg.color = col; Lg.size = 3; o = bpy.data.objects.new(nm, Lg); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1.1)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (.05, .05, .06, 1)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = 'ORTHO'; cam.data.ortho_scale = 4.0
cam.location = Vector((0, -8, 1.3)); cam.rotation_euler = (1.5708, 0, 0)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 6; sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 300
for i, n in enumerate(ORDER):
    apply(ao, POSES[n]); bpy.context.view_layer.update(); sc.render.filepath = f'{OUT}_{i:02d}_{n}.png'; bpy.ops.render.render(write_still=True)
print('DONE')
