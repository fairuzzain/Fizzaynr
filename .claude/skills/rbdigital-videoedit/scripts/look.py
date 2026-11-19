#!/usr/bin/env python3
"""QA gates for a rendered MP4 (RB Digital video skills).

Checks the REAL render, not the HTML:
  G0  decodes, has a picture, picture moves, size / duration / audio as planned
  G2  no dead frames: no still run longer than --max-still seconds mid-video
  G3  end hold short: the final still run is at most --max-end seconds
  info  hard-cut count, longest still, % moving frames, loudness (optional)

Usage:
  python look.py video.mp4 [--expect-duration 45] [--audio] [--size 1080x1920]
                 [--max-still 0.4] [--max-end 1.4] [--allow-still 12.3,30.1]
                 [--lufs -14] [--sheet qa.jpg] [--json]
Exit code 1 if any gate FAILs. Needs ffmpeg/ffprobe + numpy.
"""
import argparse, json, re, subprocess, sys

import numpy as np


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = sh(["ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_type,width,height,r_frame_rate",
            "-of", "json", path])
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser(description="QA gates for a rendered video")
    ap.add_argument("video")
    ap.add_argument("--expect-duration", type=float, help="planned length in seconds (±0.5 s)")
    ap.add_argument("--audio", action="store_true", help="audio track is required")
    ap.add_argument("--size", help="expected WxH, e.g. 1080x1920")
    ap.add_argument("--max-still", type=float, default=0.4, help="longest allowed still run mid-video (s)")
    ap.add_argument("--max-end", type=float, default=1.4, help="longest allowed end hold (s)")
    ap.add_argument("--allow-still", default="", help="comma list of times (s) of deliberate pauses (each ≤ 1.0 s)")
    ap.add_argument("--still-thresh", type=float, default=0.05,
                    help="%% of pixels that must change (by >2 levels) for a frame to count as moving; "
                         "slow camera drift scores ~0.8%%, a lone progress bar ~0.003%%")
    ap.add_argument("--cut-thresh", type=float, default=28.0, help="mean abs diff above which a frame change counts as a hard cut")
    ap.add_argument("--lufs", type=float, help="target integrated loudness, checked ±1 LU")
    ap.add_argument("--sheet", help="write a contact sheet of the real render to this path")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    a = ap.parse_args()

    res = {"gates": {}, "info": {}}
    fails = []

    def gate(name, ok, detail):
        res["gates"][name] = {"pass": bool(ok), "detail": detail}
        if not ok:
            fails.append(name)

    meta = probe(a.video)
    if not meta or "format" not in meta:
        gate("G0_decode", False, "ffprobe cannot read the file")
        return finish(res, fails, a)
    streams = meta.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    if not v:
        gate("G0_decode", False, "no video stream")
        return finish(res, fails, a)
    W, H = int(v["width"]), int(v["height"])
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1) if float(num) else 30.0
    dur = float(meta["format"].get("duration", 0))
    res["info"].update(width=W, height=H, fps=round(fps, 3), duration=round(dur, 3), audio=has_audio)

    if a.size:
        ew, eh = (int(x) for x in a.size.lower().split("x"))
        gate("G0_size", (W, H) == (ew, eh), f"{W}x{H} (expected {ew}x{eh})")
    if a.expect_duration is not None:
        gate("G0_duration", abs(dur - a.expect_duration) <= 0.5,
             f"{dur:.2f} s (planned {a.expect_duration:.2f} s, ±0.5)")
    if a.audio:
        gate("G0_audio", has_audio, "audio track present" if has_audio else "NO audio track")

    # decode small grey frames
    sw = 360
    shh = max(2, int(round(sw * H / W / 2)) * 2)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-vf",
                        f"scale={sw}:{shh}:flags=area,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = buf.size // (sw * shh)
    if n < 2:
        gate("G0_decode", False, "could not decode frames")
        return finish(res, fails, a)
    fr = buf[: n * sw * shh].reshape(n, shh, sw).astype(np.int16)
    gate("G0_decode", True, f"{n} frames decoded")

    stds = fr.reshape(n, -1).std(axis=1)
    blank = float((stds < 3).mean())
    gate("G0_not_blank", blank < 0.5, f"{blank*100:.0f}% of frames are flat/blank")

    ad = np.abs(np.diff(fr, axis=0)).reshape(n - 1, -1)
    d = ad.mean(axis=1)                         # mean change frame i -> i+1 (for cuts)
    changed = (ad > 2).mean(axis=1) * 100       # % pixels that changed (for stills)
    still = changed < a.still_thresh
    moving_pct = float((~still).mean() * 100)
    gate("G0_moves", moving_pct > 20, f"{moving_pct:.0f}% of frames have motion")
    cuts = [round((i + 1) / fps, 2) for i in np.where(d > a.cut_thresh)[0]]
    res["info"].update(moving_pct=round(moving_pct, 1), hard_cuts=len(cuts), cut_times=cuts[:60])

    # still runs: consecutive still diffs -> a held picture of (k+1) frames
    runs, i = [], 0
    while i < len(still):
        if still[i]:
            j = i
            while j < len(still) and still[j]:
                j += 1
            runs.append((i, j))  # frames i..j identical
            i = j
        else:
            i += 1
    end_hold = 0.0
    if runs and runs[-1][1] == len(still):
        s, e = runs.pop()
        end_hold = (e - s + 1) / fps
    allow = [float(t) for t in a.allow_still.split(",") if t.strip()]
    worst, worst_at, offenders = 0.0, None, []
    for s, e in runs:
        length = (e - s + 1) / fps
        t0, t1 = s / fps, (e + 1) / fps
        excused = any(t0 - 0.2 <= t <= t1 + 0.2 for t in allow) and length <= 1.0
        if not excused and length > worst:
            worst, worst_at = length, round(t0, 2)
        if not excused and length > a.max_still:
            offenders.append(f"{t0:.2f}-{t1:.2f}s ({length:.2f}s)")
    res["info"].update(longest_still=round(worst, 3), longest_still_at=worst_at)
    gate("G2_no_dead_frames", not offenders,
         f"longest still {worst:.2f}s (max {a.max_still}s)" +
         ("" if not offenders else "; still runs: " + ", ".join(offenders[:8])))
    gate("G3_end_hold", end_hold <= a.max_end, f"end hold {end_hold:.2f}s (max {a.max_end}s)")

    if has_audio:
        r = sh(["ffmpeg", "-nostats", "-i", a.video, "-af", "ebur128=peak=true", "-f", "null", "-"])
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
        p = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", r.stderr)
        if m:
            lufs = float(m[-1])
            res["info"]["lufs"] = lufs
            if p and p[-1] != "-inf":
                res["info"]["true_peak_dbfs"] = float(p[-1])
            if lufs < -45:
                gate("G0_audio_not_silent", False, f"audio is silent ({lufs} LUFS)")
            if a.lufs is not None:
                gate("G0_loudness", abs(lufs - a.lufs) <= 1.0, f"{lufs:.1f} LUFS (target {a.lufs}, ±1)")

    if a.sheet:
        cols, rows = (6, 2) if H >= W else (4, 3)
        count = cols * rows
        rate = count / max(dur, 0.1)
        tw = 270 if H >= W else 400
        sh(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf",
            f"fps={rate:.5f},scale={tw}:-2,tile={cols}x{rows}:padding=6:color=white",
            "-frames:v", "1", "-q:v", "3", a.sheet])
        res["info"]["sheet"] = a.sheet

    return finish(res, fails, a)


def finish(res, fails, a):
    res["verdict"] = "FAIL" if fails else "PASS"
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for k, g in res["gates"].items():
            print(f"{'PASS' if g['pass'] else 'FAIL'}  {k:22s} {g['detail']}")
        inf = res["info"]
        bits = []
        if "hard_cuts" in inf:
            bits.append(f"{inf['hard_cuts']} hard cuts")
        if "moving_pct" in inf:
            bits.append(f"{inf['moving_pct']}% moving frames")
        if "lufs" in inf:
            bits.append(f"{inf['lufs']} LUFS")
        if bits:
            print("info  " + ", ".join(bits))
        print(f"VERDICT: {res['verdict']}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
