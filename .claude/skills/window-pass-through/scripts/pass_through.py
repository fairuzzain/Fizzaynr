"""Window pass-through finishing tool.

  python pass_through.py analyse <clip.mp4>
      -> <clip>_clean.mp4 (Gemini watermark removed), <clip>_sheet.png (1 fps),
         <clip>_strip.png (4 fps around the top crossing), prints crossing candidates.
  python pass_through.py render <clip.mp4> --cross S --in S --len S [--veo-gain 0.35] [--sfx-gain 1.0] [--sfx path]
      -> <clip>_final.mp4: trimmed clean clip, SFX peak placed on --cross, Veo audio ducked.
"""
import argparse, json, subprocess, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SFX = Path(__file__).resolve().parent.parent / "assets" / "pass_through_sfx.mp3"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"command failed: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r.stdout


def probe(path):
    out = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    v = next(s for s in out["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in out["streams"])
    return int(v["width"]), int(v["height"]), float(out["format"]["duration"]), has_audio


def delogo_box(w, h):
    # Measured: 1080x1920 -> x855 y1695 95x95; 1280x720 -> x1130 y570 63x63. Scale for other sizes.
    if h > w:
        k = w / 1080
        x, y, s = 855, 1695, 95
    else:
        k = w / 1280
        x, y, s = 1130, 570, 63
    return round(x * k), round(y * k), round(s * k), round(s * k)


def font(size):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def grab(cap, t):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, fr = cap.read()
    return cv2.cvtColor(fr, cv2.COLOR_BGR2RGB) if ok else None


def sheet(cap, times, out, thumb_w=270, cols=5):
    tiles = []
    for t in times:
        fr = grab(cap, t)
        if fr is None:
            continue
        im = Image.fromarray(fr)
        im = im.resize((thumb_w, round(im.height * thumb_w / im.width)))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 78, 30], fill=(0, 0, 0))
        d.text((6, 4), f"{t:.2f}s", fill=(255, 220, 0), font=font(20))
        tiles.append(im)
    if not tiles:
        return
    tw, th = tiles[0].size
    rows = -(-len(tiles) // cols)
    canvas = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
    for i, im in enumerate(tiles):
        canvas.paste(im, ((i % cols) * tw, (i // cols) * th))
    canvas.save(out)


def crossing_candidates(path, dur):
    """Frame-to-frame change curve; the pass through the glass is usually its biggest burst."""
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    prev, diffs = None, []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(fr, (160, round(160 * fr.shape[0] / fr.shape[1]))), cv2.COLOR_BGR2GRAY).astype(np.float32)
        diffs.append(0.0 if prev is None else float(np.mean(np.abs(g - prev))))
        prev = g
    cap.release()
    d = np.convolve(np.array(diffs), np.ones(5) / 5, mode="same")
    t = np.arange(len(d)) / fps
    d[(t < 1.0) | (t > dur - 0.5)] = 0
    picks = []
    for i in np.argsort(d)[::-1]:
        if d[i] <= 0 or len(picks) == 3:
            break
        if all(abs(t[i] - p[0]) >= 0.7 for p in picks):
            picks.append((round(float(t[i]), 2), round(float(d[i]), 2)))
    return picks


def sfx_peak(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    env = np.sqrt(np.convolve(a * a, np.ones(400) / 400, mode="same"))  # 50 ms RMS
    return float(np.argmax(env) / 8000)


def analyse(clip):
    clip = Path(clip)
    w, h, dur, _ = probe(clip)
    x, y, bw, bh = delogo_box(w, h)
    clean = clip.with_name(clip.stem + "_clean.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-vf", f"delogo=x={x}:y={y}:w={bw}:h={bh}",
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", str(clean)])
    picks = crossing_candidates(clean, dur)
    cap = cv2.VideoCapture(str(clean))
    sheet(cap, [i + 0.5 for i in range(int(dur))], clip.with_name(clip.stem + "_sheet.png"))
    if picks:
        c = picks[0][0]
        ts = [round(c + k * 0.25, 2) for k in range(-6, 7) if 0 <= c + k * 0.25 < dur]
        sheet(cap, ts, clip.with_name(clip.stem + "_strip.png"), cols=len(ts) if len(ts) <= 7 else 7)
    cap.release()
    print(json.dumps({"clean": str(clean), "size": [w, h], "duration": round(dur, 2),
                      "delogo": [x, y, bw, bh], "crossing_candidates_s": [p[0] for p in picks],
                      "sheet": str(clip.with_name(clip.stem + "_sheet.png")),
                      "strip": str(clip.with_name(clip.stem + "_strip.png"))}, indent=2))


def render(a):
    clip = Path(a.clip)
    clean = clip.with_name(clip.stem + "_clean.mp4")
    if not clean.exists():
        sys.exit(f"{clean} missing - run analyse first")
    _, _, dur, has_audio = probe(clean)
    length = min(a.len, dur - a.in_)
    peak = sfx_peak(a.sfx)
    offset = a.cross - a.in_ - peak          # where the SFX starts on the output timeline
    if offset >= 0:
        sfx_chain = f"[1:a]volume={a.sfx_gain},adelay={int(offset * 1000)}:all=1"
    else:
        sfx_chain = f"[1:a]atrim=start={-offset},asetpts=PTS-STARTPTS,volume={a.sfx_gain}"
    fade = f"afade=t=out:st={max(0, length - 0.6):.2f}:d=0.6"
    if has_audio and a.veo_gain > 0:
        fc = (f"{sfx_chain}[s];[0:a]volume={a.veo_gain}[v];"
              f"[v][s]amix=inputs=2:duration=first:normalize=0,{fade}[a]")
    else:
        fc = f"{sfx_chain},apad,atrim=0:{length:.3f},{fade}[a]"
    out = clip.with_name(clip.stem + "_final.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a.in_:.3f}", "-t", f"{length:.3f}", "-i", str(clean),
         "-i", str(a.sfx), "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
         "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    print(json.dumps({"final": str(out), "length": round(length, 2), "sfx_peak_in_asset_s": round(peak, 2),
                      "crossing_in_output_s": round(a.cross - a.in_, 2)}, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("analyse")
    s1.add_argument("clip")
    s2 = sub.add_parser("render")
    s2.add_argument("clip")
    s2.add_argument("--cross", type=float, required=True, help="crossing time in the source clip (s)")
    s2.add_argument("--in", dest="in_", type=float, default=0.0)
    s2.add_argument("--len", type=float, default=6.0)
    s2.add_argument("--veo-gain", type=float, default=0.35)
    s2.add_argument("--sfx-gain", type=float, default=1.0)
    s2.add_argument("--sfx", default=str(SFX))
    a = p.parse_args()
    analyse(a.clip) if a.cmd == "analyse" else render(a)
