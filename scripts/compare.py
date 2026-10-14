#!/usr/bin/env python3
"""Compare our render against the reference at identical absolute timecodes.

Outputs (out/compare/):
  side_by_side.mp4   reference | ours, same frame index, timecode + frame + shot id burned in
  sheet.jpg          per shot: first / middle / last frame, reference above ours
  cuts.md            cut-point alignment (frame deltas) + per-shot timing table

Usage: python3 scripts/compare.py [ours.mp4]   (default: out/final.mp4, else out/ui.mp4)
The reference is read from reference/ref.mp4 (fetch with scripts/fetch_reference.sh).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
tl = json.loads((ROOT / "timeline/timeline.json").read_text())
FPS, N = tl["fps"], tl["durationFrames"]
REF = ROOT / "reference/ref.mp4"
ours = Path(sys.argv[1]) if len(sys.argv) > 1 else next(p for p in [ROOT / "out/final.mp4", ROOT / "out/ui.mp4"] if p.exists())
OUT = ROOT / "out/compare"
OUT.mkdir(parents=True, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
if not REF.exists():
    sys.exit("reference/ref.mp4 missing: run scripts/fetch_reference.sh")


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def gray_frames(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf", f"fps={FPS},scale=64:36,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(float)


def detect_cuts(a):
    d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    med = np.convolve(d, np.ones(9) / 9, "same")
    return [i + 1 for i, v in enumerate(d) if v > 12 and v > 2.5 * med[i]]


def tc(f):
    s = f // FPS
    return f"{s // 60:02d}:{s % 60:02d}:{f % FPS:02d}"


# 1) side-by-side at the same absolute frame index
labels = ",".join(
    f"drawtext=fontfile={FONT}:text='{s['id']} {s['scene']}':x=980:y=548:fontsize=22:fontcolor=white:box=1:boxcolor=0x000000AA:enable='between(n,{s['start']},{s['end'] - 1})'"
    for s in tl["shots"])
ff("-i", str(REF), "-i", str(ours), "-filter_complex",
   f"[0:v]fps={FPS},scale=960:540,setsar=1,trim=end_frame={N},setpts=N/({FPS}*TB)[a];"
   f"[1:v]fps={FPS},scale=960:540,setsar=1,trim=end_frame={N},setpts=N/({FPS}*TB)[b];"
   f"[a][b]hstack,pad=1920:600:0:0:black,"
   f"drawtext=fontfile={FONT}:text='REFERENCE':x=12:y=548:fontsize=22:fontcolor=white,"
   f"drawtext=fontfile={FONT}:text='%{{pts\\:hms}}  f%{{n}}':x=330:y=566:fontsize=26:fontcolor=0xFF6A2B,"
   f"{labels}[v]",
   "-map", "[v]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
   str(OUT / "side_by_side.mp4"))

# 2) per-shot sheet: first+2, middle, last-2 frames
picks = []
for s in tl["shots"]:
    picks += [min(s["start"] + 2, s["end"] - 1), (s["start"] + s["end"]) // 2, max(s["end"] - 3, s["start"])]


def grab(path, frames, tag):
    sel = "+".join(f"eq(n\\,{f})" for f in sorted(set(frames)))
    d = OUT / f"_{tag}"
    d.mkdir(exist_ok=True)
    for old in d.glob("*.png"):
        old.unlink()
    ff("-i", str(path), "-vf", f"fps={FPS},select='{sel}',scale=320:180,setsar=1", "-fps_mode", "passthrough", str(d / "%04d.png"))
    files = sorted(d.glob("*.png"))
    return dict(zip(sorted(set(frames)), files))


ra, oa = grab(REF, picks, "ref"), grab(ours, picks, "ours")
W, H, LBL = 320, 180, 26
rows = len(tl["shots"])
sheet = Image.new("RGB", (W * 3 + 160, rows * (2 * H + LBL + 10)), (12, 12, 14))
dr = ImageDraw.Draw(sheet)
font = ImageFont.truetype(FONT, 16)
for r, s in enumerate(tl["shots"]):
    y = r * (2 * H + LBL + 10)
    dr.text((8, y + 6), f"{s['id']}  [{tc(s['start'])} → {tc(s['end'])}]  {s['end'] - s['start']}f  {s['kind']}:{s['scene']}", fill=(255, 106, 43), font=font)
    for c, f in enumerate(picks[r * 3:r * 3 + 3]):
        x = 160 + c * W
        if f in ra:
            sheet.paste(Image.open(ra[f]), (x, y + LBL))
        if f in oa:
            sheet.paste(Image.open(oa[f]), (x, y + LBL + H))
        dr.text((x + 6, y + LBL + 4), f"f{f}", fill=(255, 255, 0), font=font)
    dr.text((8, y + LBL + 80), "REF", fill=(200, 200, 200), font=font)
    dr.text((8, y + LBL + H + 80), "OURS", fill=(200, 200, 200), font=font)
sheet.save(OUT / "sheet.jpg", quality=88)

# 3) cut alignment
ref_cuts = detect_cuts(gray_frames(REF))
our_cuts = detect_cuts(gray_frames(ours))
tl_cuts = [s["start"] for s in tl["shots"][1:]]
# in-shot beats (camera snaps, cursor morphs, text hits) that read as cuts in the reference
tl_marks = sorted(tl_cuts + [s["start"] + b for s in tl["shots"] for b in s.get("beats", [])])
lines = ["# Cut alignment", "", f"reference: `{REF.relative_to(ROOT)}` · ours: `{ours.relative_to(ROOT) if ours.is_relative_to(ROOT) else ours}` · {FPS} fps", "",
         "| ref cut | timecode | nearest timeline cut/beat | Δ frames | detected in ours | Δ frames |", "|---|---|---|---|---|---|"]
worst = 0
for c in ref_cuts:
    t = min(tl_marks, key=lambda x: abs(x - c))
    o = min(our_cuts, key=lambda x: abs(x - c)) if our_cuts else None
    worst = max(worst, abs(t - c))
    lines.append(f"| {c} | {tc(c)} | {t} | {t - c:+d} | {o if o is not None else '–'} | {(o - c) if o is not None else 0:+d} |")
lines += ["", f"Max |Δ| between reference cuts and timeline cuts/beats: **{worst} frames**.", "",
          "Ours-detected misses on live slots are expected while slates are in place: consecutive slates look alike to the detector.", "",
          "Timeline cuts not detected in the reference (soft transitions such as the burst or blur wipes): " + (", ".join(str(t) for t in tl_cuts if min(abs(t - c) for c in ref_cuts) > 1) or "none"),
          "", "## Shots", "", "| shot | in | out | frames | seconds | kind | reference beat |", "|---|---|---|---|---|---|---|"]
for s in tl["shots"]:
    lines.append(f"| {s['id']} | {tc(s['start'])} | {tc(s['end'])} | {s['end'] - s['start']} | {(s['end'] - s['start']) / FPS:.2f} | {s['kind']} | {s['ref']} |")
(OUT / "cuts.md").write_text("\n".join(lines) + "\n")
print(f"wrote {OUT.relative_to(ROOT)}/side_by_side.mp4, sheet.jpg, cuts.md (max cut Δ {worst}f)")
