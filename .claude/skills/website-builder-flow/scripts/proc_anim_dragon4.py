# proc_anim_dragon4.py — 4 sine-based clips: idle, fly, walk, attack.
# Extension of $GAME_SKILL/scripts/proc_anim_dragon.py per the motion-recipe
# table in references/procedural-animation.md:
#   walk   — quadruped diagonal pairs (FL+BR phi=0, FR+BL phi=pi), spine sway
#            at half amplitude, small head bob, tail wave, wings folded.
#   attack — neck/head lunge peaking mid-cycle, wing flare, chest pitch,
#            tail counter-whip (loopable one-shot for the smoke test).
# Usage: blender -b work.blend -P proc_anim_dragon4.py -- out.glb

import math
import struct
import json
import sys

import bpy

FPS = 24
STEP = 2


def get_args():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("usage: blender -b work.blend -P proc_anim_dragon4.py -- out.glb")
    rest = argv[argv.index("--") + 1:]
    if len(rest) != 1:
        raise SystemExit("usage: blender -b work.blend -P proc_anim_dragon4.py -- out.glb")
    return rest[0]


def deg(d):
    return math.radians(d)


# MOVES: bone -> list of (channel, axis, amplitude, phase, constant_offset)
# value(t) = offset + amplitude * sin(2*pi*t + phase), t in [0,1)

FLY_SECONDS = 2.0
FLY = {
    "wing_L_1": [("rot", 0, deg(40), 0.0, 0.0)],
    "wing_R_1": [("rot", 0, deg(40), math.pi, 0.0)],
    "wing_L_2": [("rot", 0, deg(25), -0.2 * 2 * math.pi, 0.0)],
    "wing_R_2": [("rot", 0, deg(25), math.pi - 0.2 * 2 * math.pi, 0.0)],
    "spine":    [("loc", 2, 0.06, math.pi, 0.0)],
    "chest":    [("rot", 0, deg(4), math.pi, 0.0)],
    "tail_1":   [("rot", 0, deg(6), 0.00, 0.0)],
    "tail_2":   [("rot", 0, deg(8), -0.6, 0.0)],
    "tail_3":   [("rot", 0, deg(10), -1.2, 0.0)],
    "tail_4":   [("rot", 0, deg(12), -1.8, 0.0)],
    "leg_FL":   [("rot", 0, 0.0, 0.0, deg(35))],
    "leg_FR":   [("rot", 0, 0.0, 0.0, deg(35))],
    "leg_BL":   [("rot", 0, 0.0, 0.0, deg(40))],
    "leg_BR":   [("rot", 0, 0.0, 0.0, deg(40))],
}

IDLE_SECONDS = 4.0
IDLE = {
    "chest":    [("rot", 0, deg(2.5), 0.0, 0.0)],
    "neck":     [("rot", 2, deg(4), 0.7, 0.0)],
    "head":     [("rot", 2, deg(3), 1.2, 0.0)],
    "tail_1":   [("rot", 2, deg(3), 0.0, 0.0)],
    "tail_2":   [("rot", 2, deg(4), -0.6, 0.0)],
    "tail_3":   [("rot", 2, deg(5), -1.2, 0.0)],
    "tail_4":   [("rot", 2, deg(6), -1.8, 0.0)],
    "wing_L_1": [("rot", 0, deg(2), 0.0, deg(5))],
    "wing_R_1": [("rot", 0, deg(2), math.pi, deg(5))],
}

# walk: diagonal pairs counter-phase (LF+RH phi=0, RF+LH phi=pi),
# spine lateral sway at half amplitude, small head bob, wings folded.
WALK_SECONDS = 1.2
WALK = {
    "leg_FL":   [("rot", 0, deg(25), 0.0, 0.0)],
    "leg_BR":   [("rot", 0, deg(25), 0.0, 0.0)],
    "leg_FR":   [("rot", 0, deg(25), math.pi, 0.0)],
    "leg_BL":   [("rot", 0, deg(25), math.pi, 0.0)],
    "spine":    [("rot", 2, deg(5), 0.0, 0.0),          # lateral sway, half amp
                 ("loc", 2, 0.015, 0.0, 0.0)],          # tiny vertical bob
    "neck":     [("rot", 0, deg(3), math.pi / 2, 0.0)],  # small head bob
    "head":     [("rot", 0, deg(2), math.pi / 2, 0.0)],
    "tail_1":   [("rot", 2, deg(4), 0.0, 0.0)],
    "tail_2":   [("rot", 2, deg(6), -0.6, 0.0)],
    "tail_3":   [("rot", 2, deg(8), -1.2, 0.0)],
    "tail_4":   [("rot", 2, deg(10), -1.8, 0.0)],
    "wing_L_1": [("rot", 0, 0.0, 0.0, deg(8))],          # folded, constant
    "wing_R_1": [("rot", 0, 0.0, 0.0, deg(8))],
}

# attack: neck/head lunge peaking mid-cycle, wing flare, chest pitch,
# tail counter-whip. sin(2*pi*t - pi/2) gives -A..+A..-A: starts pulled
# back, strikes forward at t=0.5, returns — loopable one-shot.
ATTACK_SECONDS = 1.0
ATTACK = {
    "neck":     [("rot", 0, deg(18), -math.pi / 2, deg(-4))],
    "head":     [("rot", 0, deg(14), -math.pi / 2 - 0.4, deg(-3))],  # head lags neck
    "chest":    [("rot", 0, deg(6), -math.pi / 2, 0.0)],
    "spine":    [("loc", 1, 0.05, -math.pi / 2, 0.0)],   # body lunges along axis
    "wing_L_1": [("rot", 0, deg(15), -math.pi / 2, deg(10))],  # flare on strike
    "wing_R_1": [("rot", 0, deg(15), math.pi / 2, deg(10))],
    "tail_1":   [("rot", 0, deg(8), math.pi / 2, 0.0)],  # counter-whip
    "tail_2":   [("rot", 0, deg(10), math.pi / 2 - 0.5, 0.0)],
    "tail_3":   [("rot", 0, deg(12), math.pi / 2 - 1.0, 0.0)],
    "tail_4":   [("rot", 0, deg(14), math.pi / 2 - 1.5, 0.0)],
}


def bake_action(arm, name, moves, seconds):
    frames = int(seconds * FPS)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for bone_name, channels in moves.items():
        pb = arm.pose.bones.get(bone_name)
        if pb is None:
            print(f"  (skip missing bone '{bone_name}')")
            continue
        pb.rotation_mode = "XYZ"
        for f in range(1, frames + 1, STEP):
            t = (f - 1) / frames
            for channel, axis, amp, phase, offset in channels:
                val = offset + amp * math.sin(2 * math.pi * t + phase)
                if channel == "rot":
                    pb.rotation_euler[axis] = val
                    pb.keyframe_insert("rotation_euler", index=axis, frame=f)
                else:
                    pb.location[axis] = val
                    pb.keyframe_insert("location", index=axis, frame=f)
        for channel, axis, amp, phase, offset in channels:
            val = offset + amp * math.sin(phase)
            if channel == "rot":
                pb.rotation_euler[axis] = val
                pb.keyframe_insert("rotation_euler", index=axis, frame=frames + 1)
            else:
                pb.location[axis] = val
                pb.keyframe_insert("location", index=axis, frame=frames + 1)
    arm.animation_data.action = None
    print(f"baked '{name}': {frames} frames ({seconds}s @ {FPS}fps)")
    return act


def main():
    out_path = get_args()
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not armatures:
        raise SystemExit("no armature — run proc_rig + proc_weights first")
    arm = armatures[0]
    if arm.animation_data is None:
        arm.animation_data_create()
    bpy.context.scene.render.fps = FPS

    actions = [
        bake_action(arm, "idle", IDLE, IDLE_SECONDS),
        bake_action(arm, "fly", FLY, FLY_SECONDS),
        bake_action(arm, "walk", WALK, WALK_SECONDS),
        bake_action(arm, "attack", ATTACK, ATTACK_SECONDS),
    ]

    ad = arm.animation_data
    ad.action = None
    for act in actions:
        track = ad.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, max(int(act.frame_range[0]), 0), act)

    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_skins=True,
        export_yup=True,
        export_apply=False,
    )

    # stdlib OPAQUE/doubleSided patch
    MAGIC, CHUNK_JSON = 0x46546C67, 0x4E4F534A
    with open(out_path, "rb") as f:
        data = f.read()
    chunks, off = [], 12
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunks.append((ctype, data[off + 8: off + 8 + clen]))
        off += 8 + clen
    body = b""
    for ctype, payload in chunks:
        if ctype == CHUNK_JSON:
            g = json.loads(payload.decode("utf-8"))
            for m in g.get("materials", []):
                m["alphaMode"] = "OPAQUE"
                m.pop("alphaCutoff", None)
                m["doubleSided"] = True
            payload = json.dumps(g, separators=(",", ":")).encode("utf-8")
        pad = (4 - len(payload) % 4) % 4
        payload += (b" " if ctype == CHUNK_JSON else b"\x00") * pad
        body += struct.pack("<II", len(payload), ctype) + payload
    with open(out_path, "wb") as f:
        f.write(struct.pack("<III", MAGIC, 2, 12 + len(body)) + body)

    print(f"done: {out_path}")


main()
