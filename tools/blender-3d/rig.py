"""Skeleton + capsule-distance skin weights for the fused Hunyuan mesh."""
import bpy, sys, math
from mathutils import Vector
from mathutils.geometry import intersect_point_line
SRC, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
ob = bpy.data.objects['Brakk']; me = ob.data; hh = bpy.data.objects['HammerHead']
def depth(x, z, r=.06, mode='mean'):
    ys = [v.co.y for v in me.vertices if abs(v.co.x - x) < r and abs(v.co.z - z) < r]
    if not ys: return 0
    return min(ys) if mode == 'front' else (sum(ys) / len(ys) if mode == 'mean' else (min(ys) + max(ys)) / 2)
P = lambda x, z, m='mid': Vector((x, depth(x, z, mode=m), z))
J = {'pelvis': P(-.05, .98), 'spine': P(-.05, 1.22), 'chest': P(-.05, 1.5), 'neck': P(-.01, 1.76), 'top': Vector((.0, -.02, 2.06)),
     'hipR': P(-.2, .95), 'kneeR': P(-.36, .55), 'ankR': P(-.46, .14), 'hipL': P(.12, .93), 'kneeL': P(.34, .5), 'ankL': P(.5, .14),
     'shR': P(-.44, 1.58), 'elR': P(-.52, 1.33), 'haR': P(-.42, 1.22, 'front'), 'shL': P(.3, 1.56), 'elL': P(.41, 1.3), 'haL': P(.27, 1.02, 'front')}
for k, v in J.items(): print('J', k, [round(c, 3) for c in v])
# armature
arm = bpy.data.armatures.new('BrakkRig'); ao = bpy.data.objects.new('BrakkRig', arm); bpy.context.scene.collection.objects.link(ao)
bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode='EDIT'); eb = arm.edit_bones
def bone(name, h, t, parent=None, conn=False):
    b = eb.new(name); b.head = h; b.tail = t; b.roll = 0
    if parent: b.parent = eb[parent]; b.use_connect = conn
    return b
bone('root', Vector((0, 0, 0)), Vector((0, 0, .3)))
bone('hips', J['pelvis'], J['spine'], 'root'); bone('spine', J['spine'], J['chest'], 'hips', True); bone('chest', J['chest'], J['neck'], 'spine', True); bone('head', J['neck'], J['top'], 'chest', True)
piv = (J['shR'] + J['shL']) / 2 + Vector((0, 0, -.06))
bone('arms', piv, piv + Vector((0, 0, .3)), 'chest')
for s in 'RL':
    bone('thigh.' + s, J['hip' + s], J['knee' + s], 'hips'); bone('shin.' + s, J['knee' + s], J['ank' + s], 'thigh.' + s, True)
bpy.ops.object.mode_set(mode='OBJECT')
# capsules: (bone, a, b, radius)
H0, H1 = Vector((-0.495, -0.147, 1.336)), Vector((0.524, -0.084, 0.936))
caps = [('hips', J['pelvis'] + Vector((0, 0, -.12)), J['spine'], .3), ('spine', J['spine'], J['chest'], .3), ('chest', J['chest'], J['neck'] + Vector((0, 0, -.06)), .3), ('head', J['neck'], J['top'], .2),
        ('arms', J['shR'] + Vector((-.04, 0, -.06)), J['elR'], .13), ('arms', J['elR'], J['haR'], .12), ('arms', J['shL'] + Vector((.04, 0, -.06)), J['elL'], .13), ('arms', J['elL'], J['haL'], .12), ('arms', H0, H1, .05)]
for s in 'RL': caps += [('thigh.' + s, J['hip' + s], J['knee' + s], .17), ('shin.' + s, J['knee' + s], J['ank' + s] + Vector((0, 0, -.14)), .16)]
groups = {n: ob.vertex_groups.new(name=n) for n in ['hips', 'spine', 'chest', 'head', 'arms', 'thigh.R', 'shin.R', 'thigh.L', 'shin.L']}
for v in me.vertices:
    sc = {}
    for bn, a, b, r in caps:
        p, t = intersect_point_line(v.co, a, b); t = min(1, max(0, t)); d = (v.co - (a + (b - a) * t)).length - r
        w = math.exp(-max(d, 0) / (.022 if bn == 'arms' else .035))
        sc[bn] = max(sc.get(bn, 0), w)
    tot = sum(sc.values()) or 1; top = sorted(sc.items(), key=lambda kv: -kv[1])[:3]; tt = sum(w for _, w in top) or 1
    for bn, w in top:
        if w / tt > .02: groups[bn].add([v.index], w / tt, 'REPLACE')
mod = ob.modifiers.new('rig', 'ARMATURE'); mod.object = ao; ob.parent = ao
hh.parent = ao; hh.parent_type = 'BONE'; hh.parent_bone = 'arms'
hh.matrix_parent_inverse = (ao.matrix_world @ ao.pose.bones['arms'].matrix @ __import__('mathutils').Matrix.Translation((0, ao.data.bones['arms'].length, 0))).inverted()
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('RIGGED')
