#!/usr/bin/env python3
"""motion_check.py — find the motion defects that stills can't show, in a rendered video.

    python motion_check.py out/video.mp4 --out out/check/motion [--from 0 --to 30]

Looks at every frame (downscaled) and flags:
  freeze  a stretch where nothing moves for longer than --freeze seconds (default 1.0) outside title cards.
  black   frames that are (almost) black inside the film, and a hard cut to black at the end (no fade).
  flash   (almost) white frames — fine when designed, but they must not hide the moment they cover.
Writes <out>/motion.json and one strip per flag (<out>/<kind>_<time>.jpg, the frames around it) — open the strips.
It also lists the hard cuts, to check against the plan's shot list.
Pops (a pose, expression or prop swapped with no in-between) are NOT detected here: frame differences can't tell them
from wipes and caption changes (tested on real runs). Find them by looking: clip_strip.py at 12 fps over every action.
"""
import argparse, json, os, shutil, subprocess

FFMPEG_FALLBACK = os.environ.get("FFMPEG_DIR", "")
if not shutil.which("ffmpeg") and FFMPEG_FALLBACK and os.path.isdir(FFMPEG_FALLBACK):
    os.environ["PATH"] += os.pathsep + FFMPEG_FALLBACK

import numpy as np

W, H, G = 160, 96, 8   # analysis size; G×G grid of cells for "how much of the frame changed"


def probe_fps(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    n, d = (r.stdout.strip().splitlines() or ["24/1"])[0].strip(",").split("/")
    return float(n) / float(d)


def frames(path, a, b):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(a)] if a else []) + ["-i", path] + (["-t", str(b - a)] if b else []) + \
          ["-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    arr = np.frombuffer(raw, np.uint8)
    return arr[: len(arr) // (W * H) * W * H].reshape(-1, H, W).astype(np.float32) / 255


def strip(path, t, fps, out, n=10):
    a = max(0.0, t - (n // 2) / fps)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", path, "-frames:v", str(n),
                    "-vf", f"scale=320:-2,drawtext=text='%{{pts\\:hms\\:{a:.3f}}}':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.5,tile={n}x1",
                    "-update", "1", out], capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--out", required=True)
    ap.add_argument("--from", dest="a", type=float, default=0); ap.add_argument("--to", dest="b", type=float, default=0)
    ap.add_argument("--freeze", type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fps = probe_fps(a.video)
    F = frames(a.video, a.a, a.b)
    if len(F) < 3: raise SystemExit("no frames")
    t = lambda i: round(a.a + i / fps, 3)
    lum = F.mean((1, 2))
    d = np.abs(np.diff(F, axis=0))                                    # d[i] = change from frame i to i+1
    whole = d.mean((1, 2))
    cells = d.reshape(len(d), G, H // G, G, W // G).mean((2, 4))      # (n, G, G)
    # cuts: most of the frame changes a lot at once (line boil / grain change everything a little, not a lot)
    big = (cells > 0.1).mean((1, 2))
    cut_at = {i for i in range(len(d)) if big[i] > 0.5 and whole[i] > 0.1}
    cuts = [t(i + 1) for i in sorted(cut_at)]
    freezes, run = [], 0
    for i in range(len(d) + 1):
        still = i < len(d) and whole[i] < 0.0015
        if still: run += 1
        else:
            if run / fps >= a.freeze: freezes.append({"from": t(i - run), "to": t(i), "s": round(run / fps, 2)})
            run = 0
    black, white = [], []
    for i, v in enumerate(lum):
        if v < 0.04 and (not black or t(i) - black[-1]["to"] > 1.5 / fps): black.append({"from": t(i), "to": t(i)})
        elif v < 0.04: black[-1]["to"] = t(i)
        if v > 0.92 and (not white or t(i) - white[-1] > 0.5): white.append(t(i))
    tail = lum[-int(fps * 0.5):] if len(lum) > fps else lum
    end_hard_black = bool(lum[-1] < 0.04 and len(tail) > 3 and tail[0] > 0.12 and np.min(np.diff(tail)) < -0.1)
    rep = {"video": a.video, "fps": fps, "frames": len(F), "cuts": cuts, "freezes": freezes,
           "black": [b for b in black if b["from"] > a.a + 0.2], "white_flash": white, "end_hard_cut_to_black": end_hard_black,
           "note": "open each strip. Pops are not detected here: check every action with clip_strip.py at 12 fps."}
    for z in freezes: strip(a.video, (z["from"] + z["to"]) / 2, fps, os.path.join(a.out, f"freeze_{z['from']:.2f}.jpg"))
    for b in rep["black"]: strip(a.video, b["from"], fps, os.path.join(a.out, f"black_{b['from']:.2f}.jpg"))
    with open(os.path.join(a.out, "motion.json"), "w", encoding="utf-8") as f: json.dump(rep, f, indent=1)
    print(f"cuts {len(cuts)}  freezes {len(freezes)}  black {len(rep['black'])}  white {len(white)}  end_hard_black {end_hard_black}")
    for z in freezes: print(f"  freeze {z['from']:.2f}–{z['to']:.2f}s ({z['s']}s)")
    print("wrote", os.path.join(a.out, "motion.json"))


if __name__ == "__main__":
    main()
