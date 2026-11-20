import bpy, sys, math
from mathutils import Vector
SRC, OUT, ANGS = sys.argv[-3], sys.argv[-2], [float(a) for a in sys.argv[-1].split(',')]
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
def light(name, kind, loc, energy, color, size=1):
    L = bpy.data.lights.new(name, kind); L.energy = energy; L.color = color
    if kind == 'AREA': L.size = size
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1.1)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
if 'key' not in bpy.data.objects:
    light('key', 'AREA', (-2.5, -3.5, 4), 900, (1, .9, .8), 3)
    light('rim', 'AREA', (2.5, 3, 2.5), 700, (1, .45, .15), 2)
    light('fill', 'AREA', (3.5, -2.5, 1.5), 220, (.6, .7, 1), 3)
    bpy.ops.mesh.primitive_plane_add(size=8); fl = bpy.context.object; fl.name = 'floor'
    fm = bpy.data.materials.new('floor'); fm.use_nodes = True; fb = fm.node_tree.nodes['Principled BSDF']; fb.inputs['Base Color'].default_value = (.05, .04, .045, 1); fb.inputs['Roughness'].default_value = .55; fl.data.materials.append(fm)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (.035, .03, .04, 1)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 50
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 40; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 560, 700
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
for i, ang in enumerate(ANGS):
    a = math.radians(ang - 90); d = 6.2
    cam.location = Vector((math.cos(a) * d, math.sin(a) * d, 1.7))
    cam.rotation_euler = (Vector((0, 0, 1.05)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{OUT}_{i}.png'; bpy.ops.render.render(write_still=True)
print('DONE')
