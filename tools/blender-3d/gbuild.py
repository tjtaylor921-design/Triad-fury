"""Generic fighter build: paint (front projection), split arms+weapon, rig, export the 18-pose library.
Usage: python3 gbuild.py -- CID CLEAN.blend ORTHO_FRONT.png ART.png OUT.glb"""
import bpy, bmesh, sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/tmp/claude-0/-home-user-Triad-fury/375957ce-c9ac-5e44-a0af-d71998c19d28/scratchpad/hy')
from mathutils import Vector
from mathutils.geometry import intersect_point_line
from PIL import Image
import numpy as np
from fighters import CFG
from poses3 import POSES, ORDER, BONES, apply
CID, SRC, ORTHO, ART, OUT = sys.argv[-5:]
C = CFG[CID]
bpy.ops.wm.open_mainfile(filepath=SRC)
ob = bpy.data.objects['Brakk']; ob.name = 'Body'; me = ob.data
# ---- paint: map the art's alpha box onto the model's front silhouette box
fr = np.array(Image.open(ORTHO).convert('RGB')).astype(int); m = np.abs(fr - fr[5, 5]).sum(2) > 30; ys, xs = np.nonzero(m)
X0, X1, ZT, ZB = (xs.min() - 330) / 275, (xs.max() - 330) / 275, 1.1 - (ys.min() - 330) / 275, 1.1 - (ys.max() - 330) / 275
art = Image.open(ART); aa = np.array(art.convert('RGBA'))[..., 3]; ay, ax = np.nonzero(aa > 40); AW, AH = art.size
AX0, AX1, AY0, AY1 = ax.min(), ax.max(), ay.min(), ay.max()
uv = me.uv_layers.new(name='proj')
for poly in me.polygons:
    for li in poly.loop_indices:
        co = me.vertices[me.loops[li].vertex_index].co
        px = AX0 + (co.x - X0) / (X1 - X0) * (AX1 - AX0); py = AY0 + (ZT - co.z) / (ZT - ZB) * (AY1 - AY0)
        uv.data[li].uv = (px / AW, 1 - py / AH)
mat = bpy.data.materials.new(CID + 'Art'); mat.use_nodes = True; nt = mat.node_tree; bsdf = nt.nodes['Principled BSDF']
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(ART); tex.extension = 'EXTEND'
nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color']); bsdf.inputs['Metallic'].default_value = .3; bsdf.inputs['Roughness'].default_value = .5
me.materials.clear(); me.materials.append(mat)
# ---- joints (y from the mesh depth at that spot)
def depth(x, z, r=.06):
    q = [v.co.y for v in me.vertices if abs(v.co.x - x) < r and abs(v.co.z - z) < r]
    return (min(q) + max(q)) / 2 if q else 0
J = {k: Vector((v[0], depth(*v), v[1])) for k, v in C.items() if k != 'weapon'}
W = [(Vector((a[0], depth(*a, r=.09), a[1])), Vector((b[0], depth(*b, r=.09), b[1])), r) for a, b, r in C['weapon']]
caps = [('hips', J['pelvis'] + Vector((0, 0, -.12)), J['spine'], .28), ('spine', J['spine'], J['chest'], .28), ('chest', J['chest'], J['neck'] + Vector((0, 0, -.06)), .3), ('head', J['neck'], J['top'], .2)]
for s in 'BF':
    caps += [('arms', J['sh' + s] + Vector((0, 0, -.1)), J['el' + s], .11), ('arms', J['el' + s], J['ha' + s], .11)]
    caps += [('thigh.' + ('R' if s == 'B' else 'L'), J['hip' + s], J['knee' + s], .16), ('shin.' + ('R' if s == 'B' else 'L'), J['knee' + s], J['ank' + s] + Vector((0, 0, -.14)), .15)]
caps += [('arms', a, b, r) for a, b, r in W]
def scores(co):
    sc = {}
    for bn, a, b, r in caps:
        p, t = intersect_point_line(co, a, b); t = min(1, max(0, t)); d = (co - (a + (b - a) * t)).length - r
        sc[bn] = max(sc.get(bn, 0), math.exp(-max(d, 0) / .03))
    return sc
# ---- split the arms + weapon off the body
shz = min(J['shB'].z, J['shF'].z) - .04
bm = bmesh.new(); bm.from_mesh(me); armv = set()
for v in bm.verts:
    sc = scores(v.co); tot = sum(sc.values()) or 1
    if sc.get('arms', 0) / tot > .5 and (v.co.z < shz or any(intersect_point_line(v.co, a, b)[0].__sub__(v.co).length < r + .03 for a, b, r in W)): armv.add(v.index)
for v in bm.verts: v.select = False
for e in bm.edges: e.select = False
for f in bm.faces:
    f.select = sum(1 for v in f.verts if v.index in armv) >= 2
    if f.select:
        for v in f.verts: v.select = True
        for e in f.edges: e.select = True
bm.to_mesh(me); bm.free()
bpy.ops.object.select_all(action='DESELECT'); before = set(bpy.data.objects); bpy.context.view_layer.objects.active = ob; ob.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.context.tool_settings.mesh_select_mode = (False, False, True); bpy.ops.mesh.separate(type='SELECTED'); bpy.ops.object.mode_set(mode='OBJECT')
arms = [o for o in bpy.data.objects if o not in before][0]; arms.name = 'Arms'
for o in (ob, arms):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.context.tool_settings.mesh_select_mode = (True, False, False); bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
    bpy.ops.mesh.fill_holes(sides=0); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
print('split arms', len(arms.data.polygons), 'body', len(ob.data.polygons))
# ---- armature (same bone names as Brakk so the game's pose code is shared)
arm = bpy.data.armatures.new('Rig'); ao = bpy.data.objects.new('Rig', arm); bpy.context.scene.collection.objects.link(ao)
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode='EDIT'); eb = arm.edit_bones
def bone(name, h, t, parent=None, conn=False):
    b = eb.new(name); b.head = h; b.tail = t; b.roll = 0
    if parent: b.parent = eb[parent]; b.use_connect = conn
bone('root', Vector((0, 0, 0)), Vector((0, 0, .3)))
bone('hips', J['pelvis'], J['spine'], 'root'); bone('spine', J['spine'], J['chest'], 'hips', True); bone('chest', J['chest'], J['neck'], 'spine', True); bone('head', J['neck'], J['top'], 'chest', True)
SB, SF = J['shB'] + Vector((0, 0, -.04)), J['shF'] + Vector((0, 0, -.04)); MID = (SB + SF) / 2
axis = SF - SB
if axis.length < .2: axis = Vector((.4, 0, 0))
bone('arms', MID, MID + axis.normalized() * .35, 'chest')
bone('thigh.R', J['hipB'], J['kneeB'], 'hips'); bone('shin.R', J['kneeB'], J['ankB'], 'thigh.R', True)
bone('thigh.L', J['hipF'], J['kneeF'], 'hips'); bone('shin.L', J['kneeF'], J['ankF'], 'thigh.L', True)
bpy.ops.object.mode_set(mode='OBJECT')
groups = {n: ob.vertex_groups.new(name=n) for n in ['hips', 'spine', 'chest', 'head', 'thigh.R', 'shin.R', 'thigh.L', 'shin.L']}
for v in ob.data.vertices:
    sc = scores(v.co); sc.pop('arms', None); top = sorted(sc.items(), key=lambda kv: -kv[1])[:3]; tt = sum(w for _, w in top) or 1
    for bn, w in top:
        if w / tt > .02: groups[bn].add([v.index], w / tt, 'REPLACE')
mod = ob.modifiers.new('rig', 'ARMATURE'); mod.object = ao; mw = ob.matrix_world.copy(); ob.parent = ao; ob.matrix_world = mw
bpy.context.view_layer.update(); mw = arms.matrix_world.copy(); arms.parent = ao; arms.parent_type = 'BONE'; arms.parent_bone = 'arms'; bpy.context.view_layer.update(); arms.matrix_world = mw
# ---- lighter meshes
for o, target in ((ob, 26000), (arms, 6000)):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    d = o.modifiers.new('dec', 'DECIMATE'); d.ratio = min(1, target / max(1, len(o.data.polygons))); bpy.ops.object.modifier_move_to_index(modifier='dec', index=0); bpy.ops.object.modifier_apply(modifier='dec')
    bpy.ops.object.shade_smooth()
bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.glb', '.blend'))
# ---- pose library
sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start = 0; sc.frame_end = len(ORDER) - 1
ao.animation_data_create(); ao.animation_data.action = bpy.data.actions.new('Poses')
for i, n in enumerate(ORDER):
    apply(ao, POSES[n])
    for b in BONES + ['root']:
        pb = ao.pose.bones[b]; pb.keyframe_insert('rotation_euler', frame=i)
        if b == 'root': pb.keyframe_insert('location', frame=i)
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA'): bpy.data.objects.remove(o)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_force_sampling=False,
                          export_yup=True, export_skins=True, export_lights=False, export_cameras=False, export_image_format='JPEG', export_image_quality=60)
print('EXPORTED', CID, os.path.getsize(OUT))
