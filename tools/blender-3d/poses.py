"""Brakk's key poses (degrees, bone-local XYZ euler) shared by the pose test and the animation build.
Arms bone: z<0 swings the hammer head up and over toward the enemy (+x), x>0 tips it forward.
Spine/chest: x>0 leans forward, y twists. Thighs/shins: x bends."""
import math
POSE = {
 'rest':   {},
 'guard':  {'spine': (4, 0, 0), 'chest': (3, 0, 0), 'thigh.R': (-4, 0, 0), 'thigh.L': (-4, 0, 0), 'shin.R': (8, 0, 0), 'shin.L': (8, 0, 0), 'root_z': -.03},
 'guard2': {'spine': (6, 0, 0), 'chest': (5, 0, 0), 'arms': (0, 0, -3), 'thigh.R': (-8, 0, 0), 'thigh.L': (-8, 0, 0), 'shin.R': (14, 0, 0), 'shin.L': (14, 0, 0), 'root_z': -.06},
 # horizontal sweeps: twist hips/spine/chest/arms together about the vertical axis
 'sweepW': {'hips': (0, -12, 0), 'spine': (0, -16, 0), 'chest': (-4, -16, 0), 'arms': (0, -14, -18), 'head': (0, 20, 0), 'thigh.R': (-6, 0, 0), 'shin.R': (10, 0, 0), 'thigh.L': (-6, 0, 0), 'shin.L': (10, 0, 0), 'root_z': -.05},
 'sweep':  {'hips': (0, 14, 0), 'spine': (8, 20, 0), 'chest': (8, 20, 0), 'arms': (0, 22, 6), 'head': (4, -24, 0), 'thigh.R': (-12, 0, 0), 'shin.R': (20, 0, 0), 'thigh.L': (-12, 0, 0), 'shin.L': (20, 0, 0), 'root_z': -.1},
 'sweep2W':{'hips': (0, 12, 0), 'spine': (4, 18, 0), 'chest': (4, 18, 0), 'arms': (0, 18, -10), 'head': (0, -18, 0), 'thigh.R': (-8, 0, 0), 'shin.R': (14, 0, 0), 'thigh.L': (-8, 0, 0), 'shin.L': (14, 0, 0), 'root_z': -.07},
 'sweep2': {'hips': (0, -14, 0), 'spine': (6, -20, 0), 'chest': (6, -20, 0), 'arms': (0, -24, 4), 'head': (2, 22, 0), 'thigh.R': (-12, 0, 0), 'shin.R': (20, 0, 0), 'thigh.L': (-12, 0, 0), 'shin.L': (20, 0, 0), 'root_z': -.1},
 # rising swing and chop: lift the hammer with the arms, lean back, then drive it down
 'lift':   {'hips': (0, -6, 0), 'spine': (-10, -8, 0), 'chest': (-10, -8, 0), 'arms': (0, 0, -55), 'head': (-10, 6, 0), 'thigh.R': (-4, 0, 0), 'shin.R': (6, 0, 0), 'thigh.L': (-4, 0, 0), 'shin.L': (6, 0, 0), 'root_z': .02},
 'chop':   {'hips': (0, 8, 0), 'spine': (16, 10, 0), 'chest': (14, 8, 0), 'arms': (0, 6, 22), 'head': (-12, -6, 0), 'thigh.R': (-18, 0, 0), 'shin.R': (30, 0, 0), 'thigh.L': (-18, 0, 0), 'shin.L': (30, 0, 0), 'root_z': -.18},
 'charge': {'spine': (-8, 0, 0), 'chest': (-8, 0, 0), 'arms': (0, 0, -52), 'head': (-16, 0, 0), 'thigh.R': (-24, 0, 0), 'shin.R': (44, 0, 0), 'thigh.L': (-24, 0, 0), 'shin.L': (44, 0, 0), 'root_z': -.24},
 'leap':   {'spine': (-8, 0, 0), 'chest': (-8, 0, 0), 'arms': (0, 0, -55), 'head': (-10, 0, 0), 'thigh.R': (-40, 0, 0), 'shin.R': (70, 0, 0), 'thigh.L': (-20, 0, 0), 'shin.L': (50, 0, 0), 'root_z': 0},
 'victory':{'spine': (-8, -10, 0), 'chest': (-10, -10, 0), 'arms': (0, -8, -50), 'head': (-14, 14, 0), 'thigh.R': (-2, 0, 0), 'shin.R': (3, 0, 0), 'thigh.L': (-2, 0, 0), 'shin.L': (3, 0, 0), 'root_z': .02},
 'hit':    {'spine': (-16, 8, 0), 'chest': (-12, 6, 0), 'arms': (0, 0, 8), 'head': (-18, 0, 0), 'thigh.R': (6, 0, 0), 'shin.R': (6, 0, 0), 'thigh.L': (-10, 0, 0), 'shin.L': (18, 0, 0), 'root_z': -.06},
}
BONES = ['hips', 'spine', 'chest', 'head', 'arms', 'thigh.R', 'shin.R', 'thigh.L', 'shin.L']
def apply(ao, p, blend=None, u=0):
    for b in BONES:
        r = p.get(b, (0, 0, 0))
        if blend is not None:
            r2 = blend.get(b, (0, 0, 0)); r = tuple(a + (c - a) * u for a, c in zip(r, r2))
        ao.pose.bones[b].rotation_mode = 'XYZ'; ao.pose.bones[b].rotation_euler = tuple(math.radians(x) for x in r)
    z = p.get('root_z', 0)
    if blend is not None: z += (blend.get('root_z', 0) - z) * u
    ao.pose.bones['root'].location = (0, z, 0)  # root bone points +Z: its local y is world z
