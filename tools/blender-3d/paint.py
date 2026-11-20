"""Project Brakk's art onto the model (front projection), shade parts facing away, add the hammer head."""
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
SRC, ART, EMI, OUT = sys.argv[-4:]
bpy.ops.wm.open_mainfile(filepath=SRC)
ob = bpy.data.objects['Brakk']; me = ob.data
# ortho front render bbox -> world, art alpha bbox -> pixels (measured)
X0, X1, ZT, ZB = (150 - 330) / 275, (512 - 330) / 275, 1.1 - (28 - 330) / 275, 1.1 - (626 - 330) / 275
AW, AH, AX0, AX1, AY0, AY1 = 297, 495, 0, 295, 1, 493
uv = me.uv_layers.new(name='proj')
col = me.color_attributes.new('shade', 'FLOAT_COLOR', 'CORNER')
me.calc_loop_triangles() if hasattr(me, 'calc_loop_triangles') else None
for poly in me.polygons:
    n = poly.normal; facing = -n.y  # model faces -Y
    k = 1.0 if facing > .25 else (.62 + .38 * max(0, (facing + .45) / .7))  # darken faces pointing away from the art
    for li in poly.loop_indices:
        co = me.vertices[me.loops[li].vertex_index].co
        px = AX0 + (co.x - X0) / (X1 - X0) * (AX1 - AX0); py = AY0 + (ZT - co.z) / (ZT - ZB) * (AY1 - AY0)
        uv.data[li].uv = (px / AW, 1 - py / AH)
        col.data[li].color = (k, k, k, 1)
# material: base colour = art x shade, glowing visor from the emissive map
m = bpy.data.materials.new('BrakkArt'); m.use_nodes = True; nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(ART); tex.extension = 'EXTEND'; tex.interpolation = 'Cubic'
etex = nt.nodes.new('ShaderNodeTexImage'); etex.image = bpy.data.images.load(EMI); etex.extension = 'EXTEND'
vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'shade'
mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
nt.links.new(tex.outputs['Color'], mul.inputs['A']); nt.links.new(vc.outputs['Color'], mul.inputs['B']); nt.links.new(mul.outputs['Result'], bsdf.inputs['Base Color'])
nt.links.new(etex.outputs['Color'], bsdf.inputs['Emission Color']); bsdf.inputs['Emission Strength'].default_value = 3.0
bsdf.inputs['Metallic'].default_value = .45; bsdf.inputs['Roughness'].default_value = .42
me.materials.clear(); me.materials.append(m)
# hammer head at the cropped end of the handle
L = Vector((-0.495, 0, 1.336)); Rr = Vector((0.524, 0, 0.936))
def depth(p):  # mean y of mesh vertices near this x,z
    ys = [v.co.y for v in me.vertices if abs(v.co.x - p.x) < .06 and abs(v.co.z - p.z) < .06]
    return sum(ys) / len(ys) if ys else 0
L.y, Rr.y = depth(L), depth(Rr)
d = (L - Rr).normalized(); head_c = L + d * .12
steel = bpy.data.materials.new('HammerSteel'); steel.use_nodes = True; b = steel.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (.32, .35, .4, 1); b.inputs['Metallic'].default_value = .85; b.inputs['Roughness'].default_value = .3
gold = bpy.data.materials.new('HammerGold'); gold.use_nodes = True; g = gold.node_tree.nodes['Principled BSDF']; g.inputs['Base Color'].default_value = (.8, .5, .12, 1); g.inputs['Metallic'].default_value = 1; g.inputs['Roughness'].default_value = .28
wood = bpy.data.materials.new('HammerHandle'); wood.use_nodes = True; w = wood.node_tree.nodes['Principled BSDF']; w.inputs['Base Color'].default_value = (.12, .1, .1, 1); w.inputs['Roughness'].default_value = .6
rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
def add_box(name, size, off, mat, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 2; bpy.ops.object.modifier_apply(modifier='bv')
    o.matrix_world = Matrix.Translation(head_c) @ rot @ Matrix.Translation(off); o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o
parts = [add_box('HHead', (.62, .36, .3), Vector((0, 0, .1)), steel),
         add_box('HBandA', (.08, .41, .35), Vector((-.21, 0, .1)), gold, .015), add_box('HBandB', (.08, .41, .35), Vector((.21, 0, .1)), gold, .015),
         add_box('HFaceA', (.09, .24, .2), Vector((-.35, 0, .1)), steel), add_box('HFaceB', (.09, .24, .2), Vector((.35, 0, .1)), steel)]
bpy.ops.mesh.primitive_cylinder_add(radius=.04, depth=.3, vertices=12); ext = bpy.context.object; ext.matrix_world = Matrix.Translation(head_c - d * .06) @ rot; ext.data.materials.append(wood); parts.append(ext)
bpy.ops.object.select_all(action='DESELECT')
for p in parts: p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); hh = bpy.context.object; hh.name = 'HammerHead'
print('handle ends', [round(v, 3) for v in L], [round(v, 3) for v in Rr], 'head at', [round(v, 3) for v in head_c])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
