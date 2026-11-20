"""Bake the 14 s demo timeline into one action and export Brakk as a .glb."""
import bpy, sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Triad-fury/375957ce-c9ac-5e44-a0af-d71998c19d28/scratchpad/hy')
from poses import POSE, BONES
SRC, OUT = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene; ao = bpy.data.objects['BrakkRig']; ob = bpy.data.objects['Brakk']
FPS, T_END = 30, 14.0
sc.render.fps = FPS; sc.frame_start = 0; sc.frame_end = int(T_END * FPS)
K = [(0, 'guard'), (.9, 'guard2'), (1.8, 'guard'), (2.7, 'guard2'), (3.1, 'guard'),
     (3.35, 'sweepW', 'out'), (3.6, 'sweep', 'back'), (3.95, 'sweep'), (4.15, 'sweep2W', 'out'), (4.4, 'sweep2', 'back'), (4.7, 'sweep2'),
     (4.9, 'lift', 'out'), (5.12, 'chop', 'back'), (5.5, 'guard'),
     (6.0, 'lift', 'out'), (6.55, 'lift'), (6.75, 'chop', 'back'), (7.3, 'guard'),
     (7.9, 'charge', 'out'), (9.3, 'charge'), (9.6, 'leap', 'out'), (10.05, 'lift', 'out'), (10.25, 'chop', 'back'), (11.2, 'chop'), (12.2, 'victory', 'out'), (14, 'victory')]
ease = lambda t: 2 * t * t if t < .5 else 1 - (-2 * t + 2) ** 2 / 2
out = lambda t: 1 - (1 - t) ** 3
def back(t): c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def pose_at(t):
    i = 0
    while i < len(K) - 1 and K[i + 1][0] <= t: i += 1
    a, b = K[i], K[min(i + 1, len(K) - 1)]
    if a is b or t <= a[0]: return POSE[a[1]], None, 0
    u = min(1, max(0, (t - a[0]) / (b[0] - a[0]))); kind = b[2] if len(b) > 2 else ''
    f = out(u) if kind == 'out' else back(u) if kind == 'back' else ease(u)
    return POSE[a[1]], POSE[b[1]], f
act = bpy.data.actions.new('Demo'); ao.animation_data_create(); ao.animation_data.action = act
for pb in ao.pose.bones: pb.rotation_mode = 'XYZ'
for fr in range(sc.frame_end + 1):
    t = fr / FPS; A, Bp, f = pose_at(t)
    breathe = math.sin(t * 2.6) * 1.5 if (t < 7.9 or t > 12.2) else 0
    for bn in BONES:
        ra = A.get(bn, (0, 0, 0)); rb = Bp.get(bn, (0, 0, 0)) if Bp else ra
        r = [x + (y - x) * f for x, y in zip(ra, rb)]
        if bn == 'chest': r[0] += breathe
        pb = ao.pose.bones[bn]; pb.rotation_euler = [math.radians(x) for x in r]; pb.keyframe_insert('rotation_euler', frame=fr)
    za = A.get('root_z', 0); zb = Bp.get('root_z', 0) if Bp else za
    rb_ = ao.pose.bones['root']; rb_.location = (0, za + (zb - za) * f + breathe * .004, 0); rb_.keyframe_insert('location', frame=fr)
# simple material for export: art texture + glow; facing shade travels as vertex colour (COLOR_0)
m = ob.data.materials[0]; nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE' and 'emissive' not in n.image.name][0]
for l in list(bsdf.inputs['Base Color'].links): nt.links.remove(l)
nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Metallic'].default_value = .35; bsdf.inputs['Roughness'].default_value = .45
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA') or o.name == 'floor': bpy.data.objects.remove(o)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_force_sampling=True,
                          export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_yup=True, export_apply=False, export_skins=True, export_lights=False, export_cameras=False)
import os; print('EXPORTED', os.path.getsize(OUT))
