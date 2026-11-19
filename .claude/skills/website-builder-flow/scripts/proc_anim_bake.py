# proc_anim_bake.py — GENERIC procedural animation baker for ANY armature.
# Use when the skeleton is NOT covered by Meshy's biped animation library
# (creatures, quadrupeds, winged things, multi-tail, anything custom).
#
# Workflow (references/procedural-animation.md):
#   1. List the actual bone names of your rig:
#        blender -b work.blend -P proc_anim_bake.py -- --list-bones
#   2. Write a moves config (JSON) against those bone names using the
#      motion-recipe table (diagonal pairs for quadrupeds, wave phases for
#      tails, counter-phase wings...). Example: configs/moves_dragon.json
#   3. Bake + export:
#        blender -b work.blend -P proc_anim_bake.py -- --moves moves.json --out out.glb
#
# Config format — every clip is a set of sine channels per bone:
# {
#   "fps": 24,                  # optional, default 24
#   "step": 2,                  # optional keyframe step, default 2
#   "clips": [
#     { "name": "walk", "seconds": 1.2,
#       "moves": {
#         "<bone name>": [
#           {"channel": "rot", "axis": 0, "amp_deg": 25, "phase": 0.0, "offset_deg": 0},
#           {"channel": "loc", "axis": 2, "amp": 0.02,  "phase": 3.1415, "offset": 0}
#         ]
#       }
#     }
#   ]
# }
# value(t) = offset + amp * sin(2*pi*t + phase), t in [0,1).
# rot uses amp_deg/offset_deg (degrees, converted to radians);
# loc uses amp/offset (object units). Missing bones are skipped with a
# warning, so one config can serve a family of similar rigs.

import json
import math
import struct
import sys

import bpy


def get_args():
    argv = sys.argv
    rest = argv[argv.index("--") + 1:] if "--" in argv else []
    args = {"list_bones": False, "moves": None, "out": None}
    i = 0
    while i < len(rest):
        if rest[i] == "--list-bones":
            args["list_bones"] = True
            i += 1
        elif rest[i] == "--moves":
            args["moves"] = rest[i + 1]
            i += 2
        elif rest[i] == "--out":
            args["out"] = rest[i + 1]
            i += 2
        else:
            raise SystemExit(f"unknown arg: {rest[i]}")
    if not args["list_bones"] and not (args["moves"] and args["out"]):
        raise SystemExit(
            "usage: blender -b work.blend -P proc_anim_bake.py -- "
            "(--list-bones | --moves moves.json --out out.glb)")
    return args


def find_armature():
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not arms:
        raise SystemExit("no armature in the .blend — rig + weights first")
    return arms[0]


def channel_value(spec, t):
    if spec.get("channel", "rot") == "rot":
        amp = math.radians(spec.get("amp_deg", 0.0))
        off = math.radians(spec.get("offset_deg", 0.0))
    else:
        amp = spec.get("amp", 0.0)
        off = spec.get("offset", 0.0)
    return off + amp * math.sin(2 * math.pi * t + spec.get("phase", 0.0))


def bake_clip(arm, clip, fps, step):
    frames = max(int(clip["seconds"] * fps), 2)
    act = bpy.data.actions.new(clip["name"])
    act.use_fake_user = True
    arm.animation_data.action = act
    for bone_name, specs in clip["moves"].items():
        pb = arm.pose.bones.get(bone_name)
        if pb is None:
            print(f"  WARNING: bone '{bone_name}' not in rig — skipped")
            continue
        pb.rotation_mode = "XYZ"
        frame_list = list(range(1, frames + 1, step)) + [frames + 1]
        for f in frame_list:
            t = (f - 1) / frames
            for spec in specs:
                val = channel_value(spec, t)
                axis = spec.get("axis", 0)
                if spec.get("channel", "rot") == "rot":
                    pb.rotation_euler[axis] = val
                    pb.keyframe_insert("rotation_euler", index=axis, frame=f)
                else:
                    pb.location[axis] = val
                    pb.keyframe_insert("location", index=axis, frame=f)
    arm.animation_data.action = None
    print(f"baked '{clip['name']}': {frames} frames ({clip['seconds']}s @ {fps}fps)")
    return act


def export_glb(out_path):
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_skins=True,
        export_yup=True,
        export_apply=False,
    )
    # stdlib patch: force OPAQUE doubleSided (transparent-mesh pitfall)
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


def main():
    args = get_args()
    arm = find_armature()

    if args["list_bones"]:
        print(f"armature '{arm.name}', {len(arm.pose.bones)} bones:")
        for pb in arm.pose.bones:
            parent = pb.parent.name if pb.parent else "-"
            print(f"  {pb.name}  (parent: {parent})")
        return

    with open(args["moves"]) as f:
        cfg = json.load(f)
    fps = cfg.get("fps", 24)
    step = cfg.get("step", 2)
    bpy.context.scene.render.fps = fps
    if arm.animation_data is None:
        arm.animation_data_create()

    actions = [bake_clip(arm, clip, fps, step) for clip in cfg["clips"]]

    ad = arm.animation_data
    ad.action = None
    for act in actions:
        track = ad.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, max(int(act.frame_range[0]), 0), act)

    export_glb(args["out"])
    print(f"done: {args['out']} ({len(actions)} clips)")


main()
