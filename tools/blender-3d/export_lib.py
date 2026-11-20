"""Export the in-game Brakk: lighter mesh + a pose library action (frame i = pose ORDER[i])."""
import bpy, sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-Triad-fury/375957ce-c9ac-5e44-a0af-d71998c19d28/scratchpad/hy')
from poses3 import POSES, ORDER, BONES, apply
SRC, OUT, BODY, ARMS = sys.argv[-4], sys.argv[-3], int(sys.argv[-2]), int(sys.argv[-1])
bpy.ops.wm.open_mainfile(filepath=SRC)
ao = bpy.data.objects['BrakkRig']
for name, target in (('Brakk', BODY), ('BrakkArms', ARMS)):
    o = bpy.data.objects[name]; bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    d = o.modifiers.new('dec', 'DECIMATE'); d.ratio = min(1, target / len(o.data.polygons))
    bpy.ops.object.modifier_move_to_index(modifier='dec', index=0); bpy.ops.object.modifier_apply(modifier='dec')
    print(name, 'faces', len(o.data.polygons))
# material for export: art texture + glow; facing shade travels as COLOR_0
for o in (bpy.data.objects['Brakk'], bpy.data.objects['BrakkArms']):
    for m in o.data.materials:
        if not m or not m.use_nodes or m.name != 'BrakkArt': continue
        nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']; tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE' and 'emissive' not in n.image.name][0]
        for l in list(bsdf.inputs['Base Color'].links): nt.links.remove(l)
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color']); bsdf.inputs['Metallic'].default_value = .35; bsdf.inputs['Roughness'].default_value = .45
sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start = 0; sc.frame_end = len(ORDER) - 1
act = bpy.data.actions.new('Poses'); ao.animation_data_create(); ao.animation_data.action = act
for i, n in enumerate(ORDER):
    apply(ao, POSES[n])
    for b in BONES + ['root']:
        pb = ao.pose.bones[b]; pb.keyframe_insert('rotation_euler', frame=i)
        if b == 'root': pb.keyframe_insert('location', frame=i)
for fc in (act.fcurves if hasattr(act, 'fcurves') else []):
    for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA'): bpy.data.objects.remove(o)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_force_sampling=False,
                          export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_yup=True, export_skins=True, export_lights=False, export_cameras=False)
print('EXPORTED', os.path.getsize(OUT), 'poses', ORDER)
