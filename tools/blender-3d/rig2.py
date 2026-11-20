"""Rig v2: split the arms + hammer off the fused body so they swing freely about the shoulder axis.
Body keeps capsule skin weights; the arms piece rides the 'arms' bone (hinge along the shoulder line)."""
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_point_line
SRC, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
ob = bpy.data.objects['Brakk']; me = ob.data; hh = bpy.data.objects['HammerHead']
def depth(x, z, r=.06, mode='mid'):
    ys = [v.co.y for v in me.vertices if abs(v.co.x - x) < r and abs(v.co.z - z) < r]
    if not ys: return 0
    return min(ys) if mode == 'front' else (min(ys) + max(ys)) / 2
P = lambda x, z, m='mid': Vector((x, depth(x, z, mode=m), z))
J = {'pelvis': P(-.05, .98), 'spine': P(-.05, 1.22), 'chest': P(-.05, 1.5), 'neck': P(-.01, 1.76), 'top': Vector((.0, -.02, 2.06)),
     'hipR': P(-.2, .95), 'kneeR': P(-.36, .55), 'ankR': P(-.46, .14), 'hipL': P(.12, .93), 'kneeL': P(.34, .5), 'ankL': P(.5, .14),
     'shR': P(-.44, 1.58), 'elR': P(-.52, 1.33), 'haR': P(-.42, 1.22, 'front'), 'shL': P(.3, 1.56), 'elL': P(.41, 1.3), 'haL': P(.27, 1.02, 'front')}
H0, H1 = Vector((-0.495, -0.147, 1.336)), Vector((0.524, -0.084, 0.936))
caps = [('hips', J['pelvis'] + Vector((0, 0, -.12)), J['spine'], .3), ('spine', J['spine'], J['chest'], .3), ('chest', J['chest'], J['neck'] + Vector((0, 0, -.06)), .32), ('head', J['neck'], J['top'], .2),
        ('arms', J['shR'] + Vector((-.06, -.02, -.16)), J['elR'], .12), ('arms', J['elR'], J['haR'], .12), ('arms', J['shL'] + Vector((.06, -.02, -.16)), J['elL'], .12), ('arms', J['elL'], J['haL'], .12), ('arms', H0, H1, .055)]
for s in 'RL': caps += [('thigh.' + s, J['hip' + s], J['knee' + s], .17), ('shin.' + s, J['knee' + s], J['ank' + s] + Vector((0, 0, -.14)), .16)]
def scores(co):
    sc = {}
    for bn, a, b, r in caps:
        p, t = intersect_point_line(co, a, b); t = min(1, max(0, t)); d = (co - (a + (b - a) * t)).length - r
        sc[bn] = max(sc.get(bn, 0), math.exp(-max(d, 0) / .03))
    return sc
# 1) split: faces whose vertices belong mostly to the arms
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
armv = set()
for v in bm.verts:
    sc = scores(v.co); tot = sum(sc.values()) or 1
    if sc.get('arms', 0) / tot > .5 and v.co.z < 1.52: armv.add(v.index)
for v in bm.verts: v.select = False
for e in bm.edges: e.select = False
for f in bm.faces:
    f.select = sum(1 for v in f.verts if v.index in armv) >= 2
    if f.select:
        for v in f.verts: v.select = True
        for e in f.edges: e.select = True
bm.select_mode = {'FACE'}
bm.to_mesh(me); bm.free()
bpy.ops.object.select_all(action='DESELECT'); before = set(bpy.data.objects)
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.context.tool_settings.mesh_select_mode = (False, False, True); bpy.ops.mesh.separate(type='SELECTED'); bpy.ops.object.mode_set(mode='OBJECT')
arms = [o for o in bpy.data.objects if o not in before][0]; arms.name = 'BrakkArms'
for o in (ob, arms):  # seal the cut edges
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.context.tool_settings.mesh_select_mode = (True, False, False); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
    bpy.ops.mesh.fill_holes(sides=0); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
print('arms faces', len(arms.data.polygons), 'body faces', len(ob.data.polygons))
# keep the hammer with the arms
bpy.ops.object.select_all(action='DESELECT'); hh.select_set(True); arms.select_set(True); bpy.context.view_layer.objects.active = arms; bpy.ops.object.join()
# 2) armature: the arms bone hinges along the shoulder line (rotate about its Y to swing)
arm = bpy.data.armatures.new('BrakkRig'); ao = bpy.data.objects.new('BrakkRig', arm); bpy.context.scene.collection.objects.link(ao)
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode='EDIT'); eb = arm.edit_bones
def bone(name, h, t, parent=None, conn=False):
    b = eb.new(name); b.head = h; b.tail = t; b.roll = 0
    if parent: b.parent = eb[parent]; b.use_connect = conn
bone('root', Vector((0, 0, 0)), Vector((0, 0, .3)))
bone('hips', J['pelvis'], J['spine'], 'root'); bone('spine', J['spine'], J['chest'], 'hips', True); bone('chest', J['chest'], J['neck'], 'spine', True); bone('head', J['neck'], J['top'], 'chest', True)
SR, SL = J['shR'] + Vector((0, 0, -.04)), J['shL'] + Vector((0, 0, -.04))
MID = (SR + SL) / 2; bone('arms', MID, MID + (SL - SR) / 2, 'chest')
for s in 'RL': bone('thigh.' + s, J['hip' + s], J['knee' + s], 'hips'); bone('shin.' + s, J['knee' + s], J['ank' + s], 'thigh.' + s, True)
bpy.ops.object.mode_set(mode='OBJECT')
# 3) body skin weights (no arms group); arms piece is bone-parented (rigid)
me = ob.data
for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
groups = {n: ob.vertex_groups.new(name=n) for n in ['hips', 'spine', 'chest', 'head', 'thigh.R', 'shin.R', 'thigh.L', 'shin.L']}
for v in me.vertices:
    sc = scores(v.co); sc.pop('arms', None)
    top = sorted(sc.items(), key=lambda kv: -kv[1])[:3]; tt = sum(w for _, w in top) or 1
    for bn, w in top:
        if w / tt > .02: groups[bn].add([v.index], w / tt, 'REPLACE')
for m in list(ob.modifiers): ob.modifiers.remove(m)
mod = ob.modifiers.new('rig', 'ARMATURE'); mod.object = ao
mw = ob.matrix_world.copy(); ob.parent = ao; ob.matrix_world = mw
for g in list(arms.vertex_groups): arms.vertex_groups.remove(g)
for m in list(arms.modifiers): arms.modifiers.remove(m)
bpy.context.view_layer.update()
mw = arms.matrix_world.copy(); arms.parent = ao; arms.parent_type = 'BONE'; arms.parent_bone = 'arms'; bpy.context.view_layer.update(); arms.matrix_world = mw
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('RIGGED2', [round(c, 3) for c in SR], [round(c, 3) for c in SL])
