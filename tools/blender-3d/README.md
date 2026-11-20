# AI model to animated Babylon fighter (Blender)

How `prototypes/brakk-3d/brakk.glb` was made. Needs `pip install bpy` (Blender 5.3 as a Python module) and `gradio_client`.

1. **Shape:** Hunyuan3D-2 on Hugging Face (`tencent/Hunyuan3D-2`, `/shape_generation`) from `art/brakk-stance.png`
   (needs a free Hugging Face token for GPU quota; the texture step on the Space was broken at the time).
2. `python3 clean.py -- shape.glb clean.blend`: stand on the floor, 2.2 m tall, voxel remesh, decimate to ~60k faces.
3. `python3 paint.py -- clean.blend art_padded.png art_emissive.png painted.blend`: project the art from the front
   (bbox numbers are measured for Brakk), darken faces pointing away, add the hammer head.
4. `python3 rig.py -- painted.blend rigged.blend`: skeleton + capsule-distance skin weights (one "arms" bone moves both arms and the hammer).
5. `python3 posetest.py -- rigged.blend out guard,lift,chop`: check poses (defined in `poses.py`).
6. `python3 bake.py -- rigged.blend brakk.glb`: bake the 14 s demo timeline and export .glb.

## In-game version (models/brakk.glb)
7. `python3 rig2.py -- painted.blend rig2.blend`: split the fused arms + hammer off the body (sealed cuts) so they swing
   freely from the shoulders; the body keeps skin weights.
8. `python3 lib_preview.py -- rig2.blend lib`: preview the pose library in `poses3.py`.
9. `python3 export_lib.py -- rig2.blend brakk.glb 26000 6000`: lighter mesh + a "Poses" action (frame i = `ORDER[i]`).
   The game (`R3` in index.html) reads each pose from that action and blends between them by fight state.
