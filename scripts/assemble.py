#!/usr/bin/env python3
"""Composite live-action plates into the UI render.

  out/ui.mp4          full picture (slates in live slots)          <- npm run render
  out/captions.mov    captions/supers for live slots, with alpha   <- npm run render:captions
  plates/<SHOT>.mp4   your Higgsfield clip for that live slot (optional, any length/size)

Each plate is scaled/cropped to 1920x1080, conformed to 24 fps, trimmed (or last-frame held)
to the slot length and laid over its absolute frame range. Missing plates leave the slate.
Optional: plates/<SHOT>.json  {"offset": 12}  skips 12 frames into the plate before the slot starts.
Optional: audio/mix.wav is muxed if present.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tl = json.loads((ROOT / "timeline/timeline.json").read_text())
fps = tl["fps"]
ui = ROOT / "out/ui.mp4"
caps = ROOT / "out/captions.mov"
out = ROOT / "out/final.mp4"

if not ui.exists():
    sys.exit("out/ui.mp4 missing: run `npm run render` first")

inputs = ["-i", str(ui)]
chain = []
last = "[0:v]"
idx = 1
used = []
for s in tl["shots"]:
    if s["kind"] != "live":
        continue
    plate = next((p for p in [ROOT / f"plates/{s['id']}.mp4", ROOT / f"plates/{s['id']}.mov"] if p.exists()), None)
    if not plate:
        continue
    meta = ROOT / f"plates/{s['id']}.json"
    offset = json.loads(meta.read_text()).get("offset", 0) if meta.exists() else 0
    n = s["end"] - s["start"]
    inputs += ["-i", str(plate)]
    chain.append(
        f"[{idx}:v]fps={fps},scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,"
        f"trim=start_frame={offset}:end_frame={offset + n},setpts=PTS-STARTPTS,"
        f"tpad=stop_mode=clone:stop={n},trim=end_frame={n},"
        f"setpts=PTS+{s['start']}/({fps}*TB)[p{idx}]"
    )
    chain.append(f"{last}[p{idx}]overlay=eof_action=pass:enable='between(n,{s['start']},{s['end'] - 1})'[v{idx}]")
    last = f"[v{idx}]"
    used.append(s["id"])
    idx += 1

if used and caps.exists():
    inputs += ["-i", str(caps)]
    chain.append(f"{last}[{idx}:v]overlay=eof_action=pass[vc]")
    last = "[vc]"
    idx += 1

audio = ROOT / "audio/mix.wav"
amap = []
if audio.exists():
    inputs += ["-i", str(audio)]
    amap = ["-map", f"{idx}:a", "-c:a", "aac", "-b:a", "256k", "-shortest"]

cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs]
if chain:
    cmd += ["-filter_complex", ";".join(chain), "-map", last]
else:
    cmd += ["-map", "0:v"]
cmd += [*amap, "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(fps),
        "-frames:v", str(tl["durationFrames"]), str(out)]
subprocess.run(cmd, check=True)
print(f"wrote {out.relative_to(ROOT)}; plates used: {', '.join(used) or 'none (slates kept)'}")
