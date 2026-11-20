"""Brakk's in-game pose library (rig v2). Degrees, bone-local XYZ euler.
arms: x<0 raises the hammer up beside his head, x>0 brings it down to his side (the strike side); z>0 pushes it forward.
spine/chest/head: x>0 leans forward, y twists. thighs/shins: x bends. root_z: crouch/lift, root_rot: whole-body tilt (KO)."""
import math
L = lambda **k: k
def legs(t, s, t2=None, s2=None): return {'thigh.R': (t, 0, 0), 'shin.R': (s, 0, 0), 'thigh.L': (t2 if t2 is not None else t, 0, 0), 'shin.L': (s2 if s2 is not None else s, 0, 0)}
def P(base, **k): d = dict(base); d.update(k); return d
POSES = {
 'idle':   P(legs(-4, 8), spine=(4, 0, 0), chest=(3, 0, 0), arms=(10, 0, 0), root_z=-.03),
 'a1w':    P(legs(-6, 10), hips=(0, -10, 0), spine=(0, -10, 0), chest=(-4, -14, 0), arms=(-35, 0, -20), head=(0, 12, 0), root_z=-.05),
 'a1':     P(legs(-12, 20), hips=(0, 10, 0), spine=(8, 14, 0), chest=(8, 12, 0), arms=(40, 0, 25), head=(4, -12, 0), root_z=-.1),
 'a2w':    P(legs(-10, 18), hips=(0, 8, 0), spine=(8, 10, 0), chest=(6, 10, 0), arms=(55, 0, 10), root_z=-.09),
 'a2':     P(legs(-6, 10), hips=(0, -8, 0), spine=(-4, -10, 0), chest=(-6, -16, 0), arms=(-70, 0, 20), head=(-8, 10, 0), root_z=-.02),
 'a3w':    P(legs(-4, 6), spine=(-10, 0, 0), chest=(-10, 0, 0), arms=(-115, 0, 0), head=(-10, 0, 0), root_z=.02),
 'a3':     P(legs(-18, 30), hips=(0, 8, 0), spine=(18, 8, 0), chest=(14, 6, 0), arms=(30, 0, 15), head=(-12, -6, 0), root_z=-.18),
 'heavyW': P(legs(-6, 10), spine=(-14, -8, 0), chest=(-12, -8, 0), arms=(-130, 0, -10), head=(-14, 6, 0), root_z=.02),
 'heavy':  P(legs(-24, 40), hips=(0, 10, 0), spine=(22, 10, 0), chest=(16, 8, 0), arms=(38, 0, 22), head=(-14, -6, 0), root_z=-.24),
 'block':  P(legs(-12, 22), spine=(10, 0, 0), chest=(6, 0, 0), arms=(-35, 0, 40), head=(8, 0, 0), root_z=-.1),
 'hit':    P(legs(6, 6, -10, 18), spine=(-18, 8, 0), chest=(-14, 6, 0), arms=(25, 0, -20), head=(-20, 0, 0), root_z=-.06),
 'stun':   P(legs(-10, 18), spine=(10, -10, 0), chest=(8, -8, 0), arms=(30, 0, -10), head=(20, 0, 0), root_z=-.1),
 'cast':   P(legs(-24, 44), spine=(-8, 0, 0), chest=(-8, 0, 0), arms=(-100, 0, 0), head=(-16, 0, 0), root_z=-.24),
 'air':    P(legs(-40, 70, -20, 50), spine=(-8, 0, 0), chest=(-8, 0, 0), arms=(-125, 0, -10), head=(-10, 0, 0)),
 'slam':   P(legs(-28, 48), hips=(0, 10, 0), spine=(26, 10, 0), chest=(18, 8, 0), arms=(42, 0, 26), head=(-16, -6, 0), root_z=-.3),
 'dash':   P(legs(-20, 30, -6, 10), spine=(18, 0, 0), chest=(10, 0, 0), arms=(10, 0, 30), head=(-10, 0, 0), root_z=-.08),
 'win':    P(legs(-2, 3), spine=(-8, -10, 0), chest=(-10, -10, 0), arms=(-110, 0, 0), head=(-14, 14, 0), root_z=.02),
 'ko':     P(legs(20, 30, 10, 40), spine=(-20, 0, 0), chest=(-10, 0, 0), arms=(40, 0, -30), head=(-20, 0, 0), root_rot=(0, 0, -82), root_z=.25),
}
ORDER = list(POSES)
BONES = ['hips', 'spine', 'chest', 'head', 'arms', 'thigh.R', 'shin.R', 'thigh.L', 'shin.L']
def apply(ao, p):
    for b in BONES:
        pb = ao.pose.bones[b]; pb.rotation_mode = 'XYZ'; pb.rotation_euler = [math.radians(x) for x in p.get(b, (0, 0, 0))]
    rb = ao.pose.bones['root']; rb.rotation_mode = 'XYZ'; rb.rotation_euler = [math.radians(x) for x in p.get('root_rot', (0, 0, 0))]; rb.location = (0, p.get('root_z', 0), 0)
