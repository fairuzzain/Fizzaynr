"""Edit the cleaned clips to music at REAL SPEED: beat-snapped cuts, per-world grade, transitions, ambience.

Usage: python cut.py <run_dir> [--edit edit.json] [--out final.mp4] [--preview]
--preview renders at half size with a fast preset (check the cut; free, fast).

edit.json (seconds; every clip plays frame for frame, there is no speed key on purpose):
{
  "fps": 24, "size": [1080, 1920],
  "music": "audio/music.mp3", "beats": "audio/beats.json",
  "music_start": 31.2,          # track time at film t=0; drop on the first cut -> music_start = drop - shots[0].dur
  "music_gain_db": 0, "loop_bars": null,   # [first_beat_idx, last_beat_idx] to repeat if the track is short (auto if null)
  "snap": "half",               # snap cut points to the beat grid: "beat" | "half" | null (exact durations)
  "ambience_gain_db": -11, "jcut": 0.3,    # clip sound under the music; next place is heard 0.3 s before it is seen
  "vignette": 0.22, "end_fade": 1.0, "lufs": -14, "true_peak": -1,
  "worlds": {"dawn": {"warmth": -0.03, "saturation": 0.95, "contrast": 1.04},
             "golden": {"warmth": 0.08, "saturation": 1.06, "contrast": 1.06}},
  "shots": [
    {"clip": "c01", "in": 0.3, "dur": 1.5, "world": "dawn", "to": "whip"},
    {"clip": "c04", "in": 1.0, "dur": 1.0, "world": "dawn", "to": "cut", "amb_db": -4}
  ]
}
Shot keys: clip (name in clean/; sound from videos/<clip>.mp4), in (source start s), dur (s on screen),
world (grade key), to = transition into the NEXT shot:
  cut    hard cut (on the beat)            match  hard cut, frame kept at the joint (a shape/colour match)
  whip   uneven diagonal whip: directional blur + slight rotation/scale + RGB split; "angle" (deg, default 28)
  zoom   radial zoom punch out of A, into B          light  dissolve through warm light/haze
  shake  hard cut with a short shake hit on B
amb_db per-shot ambience trim. A shot whose window runs past its clip is shifted earlier and reported.
Writes <run>/<out>, <run>/audio/mix.wav and <run>/qa_cuts.png (4 frames around every cut).
"""
import os
import argparse, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SR = 48000
TW = {"whip": 3, "zoom": 4, "light": 5, "shake": 6, "cut": 0, "match": 0}


def probe_dur(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True).stdout.strip()
    return float(o or 0)


def frames_of(path, t0, n, W, H, fps):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0, t0):.3f}", "-i", str(path), "-frames:v", str(n),
           "-vf", f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase:flags=bicubic,crop={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    got = len(raw) // (W * H * 3)
    if got == 0: raise RuntimeError(f"no frames from {path} at {t0}s")
    a = np.frombuffer(raw[: got * W * H * 3], np.uint8).reshape(got, H, W, 3)
    if got < n:
        print(f"   ! {Path(path).stem}: only {got}/{n} frames from {t0:.2f}s - last frame held", file=sys.stderr)
        a = np.concatenate([a, np.repeat(a[-1:], n - got, 0)])
    return a


def audio_of(path, t0, dur):
    pad = max(0.0, -t0)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t0):.3f}", "-t", f"{dur - pad:.3f}", "-i", str(path),
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2) if raw else np.zeros((0, 2), np.float32)
    a = np.concatenate([np.zeros((int(pad * SR), 2), np.float32), a])
    n = int(dur * SR)
    return np.pad(a, ((0, max(0, n - len(a))), (0, 0)))[:n]


# ---------------------------------------------------------------- look
def grade(f, g):
    if not g: return f
    w = g.get("warmth", 0)
    if w: f = f * np.float32([1 + w, 1 + w * 0.3, 1 - w])
    c = g.get("contrast", 1)
    if c != 1: f = (f - 118) * c + 118
    s = g.get("saturation", 1)
    if s != 1:
        y = (f @ np.float32([0.299, 0.587, 0.114]))[..., None]
        f = y + (f - y) * s
    lift = g.get("exposure", 0)
    if lift: f = f * (1 + lift)
    return f


def vignette_mask(W, H, v):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) / math.sqrt(2)
    return (1 - v * np.clip((r - 0.35) / 0.65, 0, 1) ** 1.6)[..., None].astype(np.float32)


def affine(f, scale=1.0, rot=0.0, dx=0.0, dy=0.0):
    H, W = f.shape[:2]
    M = cv2.getRotationMatrix2D((W / 2, H / 2), rot, scale); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def dir_blur(f, L, ang):
    L = int(L)
    if L < 3: return f
    k = np.zeros((L, L), np.float32)
    c = (L - 1) / 2; dx, dy = math.cos(math.radians(ang)) * c, -math.sin(math.radians(ang)) * c
    cv2.line(k, (round(c - dx), round(c - dy)), (round(c + dx), round(c + dy)), 1.0, 1)
    return cv2.filter2D(f, -1, k / k.sum(), borderType=cv2.BORDER_REFLECT)


def rgb_split(f, d, ang):
    if d < 0.5: return f
    dx, dy = math.cos(math.radians(ang)) * d, -math.sin(math.radians(ang)) * d
    out = f.copy()
    out[..., 0] = affine(f[..., 0], dx=dx, dy=dy); out[..., 2] = affine(f[..., 2], dx=-dx, dy=-dy)
    return out


def radial(f, scale, amount, n=6):
    acc = np.zeros_like(f)
    for i in range(n):
        acc += affine(f, scale * (1 + amount * i / max(1, n - 1)))
    return acc / n


def trans(f, kind, p, side, ang, W, rng):
    """p in (0,1]: 1 at the joint. side 'out' = end of shot A, 'in' = start of shot B."""
    if kind == "whip":
        sgn = 1 if side == "out" else -1
        f = affine(f, 1 + 0.09 * p, sgn * 2.8 * p)
        f = dir_blur(f, 0.14 * W * p ** 1.6, ang)
        return rgb_split(f, 0.012 * W * p ** 2, ang)
    if kind == "zoom":
        s = 1 + 0.3 * p ** 2 if side == "out" else 1 + 0.22 * p ** 2
        return radial(f, s, 0.07 * p)
    if kind == "light":
        a = 0.92 * p ** 1.4
        f = cv2.GaussianBlur(f, (0, 0), 1 + 5 * p) if p > 0.3 else f
        return f + (np.float32([255, 246, 232]) - f) * a
    if kind == "shake" and side == "in":
        amp = 0.022 * W * p
        f = affine(f, 1.06, rng.uniform(-0.8, 0.8) * p, rng.uniform(-1, 1) * amp, rng.uniform(-1, 1) * amp)
        return dir_blur(f, 0.02 * W * p, 90)
    return f


# ---------------------------------------------------------------- timing
def snap_cuts(shots, beats, music_start, mode, fps):
    T = np.cumsum([s["dur"] for s in shots])
    if mode and beats:
        g = np.array(beats) - music_start
        if mode == "half": g = np.sort(np.concatenate([g, (g[:-1] + g[1:]) / 2]))
        g = g[g > 0.3]
        prev = 0.0
        for i in range(len(T) - 1):  # the film end is not snapped (music fades)
            c = g[(g > prev + 0.4)]
            if len(c): T[i] = c[np.argmin(np.abs(c - T[i]))]
            prev = T[i]
    T = np.round(T * fps) / fps
    starts = np.concatenate([[0], T[:-1]])
    return starts, T


def music_track(path, start, need, beats, loop):
    y = audio_of(path, start, max(0.1, probe_dur(path) - start))
    if len(y) >= need * SR: return y[: int(need * SR)], None
    b = np.array(beats) - start
    if loop: s, e = b[loop[0]], b[loop[1]]
    else:
        ok = np.where(b < len(y) / SR - 0.5)[0]
        e = b[ok[-1]] if len(ok) else len(y) / SR; s = b[max(0, ok[-1] - 16)] if len(ok) else 0
    si, ei = int(s * SR), int(e * SR); seg = y[si:ei]; xf = int(0.008 * SR)
    out = y[:ei]
    while len(out) < need * SR and len(seg) > 2 * xf:
        r = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - r) + seg[:xf] * r, seg[xf:]])
    return out[: int(need * SR)], (round(s + start, 3), round(e + start, 3))


def loudnorm(wav, lufs, tp):
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", f"loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
    return (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
            f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")


def font(size):
    for f in (*([os.environ["FONT_BOLD"]] if os.environ.get("FONT_BOLD") else []), "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("--edit", default="edit.json")
    ap.add_argument("--out"); ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    run = Path(a.run); E = json.loads((run / a.edit).read_text())
    fps = E.get("fps", 24); W, H = E.get("size", [1080, 1920])
    if a.preview: W, H = W // 2 // 2 * 2, H // 2 // 2 * 2
    out = run / (a.out or ("preview.mp4" if a.preview else "final.mp4"))
    beats = json.loads((run / E["beats"]).read_text())["beats"] if E.get("beats") else []
    ms = E.get("music_start", 0.0)
    shots = E["shots"]
    starts, ends = snap_cuts(shots, beats, ms, E.get("snap", "half"), fps)
    film = float(ends[-1]); nfr = int(round(film * fps))
    worlds = E.get("worlds", {}); vig = vignette_mask(W, H, E.get("vignette", 0.22))
    rng = np.random.default_rng(7)
    print(f"{len(shots)} shots, {film:.2f}s at {fps} fps, {W}x{H}")
    # ------------------------------------------------ video
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                            "-i", "-", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
                            "-preset", "ultrafast" if a.preview else "slow", "-crf", "23" if a.preview else "16",
                            str(run / "_video.mp4")], stdin=subprocess.PIPE)
    qa, plan = [], []
    for i, s in enumerate(shots):
        f0, f1 = int(round(starts[i] * fps)), int(round(ends[i] * fps)); n = f1 - f0
        src = run / "clean" / f"{s['clip']}.mp4"; clen = probe_dur(src)
        tin = s["in"]
        if tin + n / fps > clen - 0.05:
            tin = max(0.0, clen - 0.05 - n / fps)
            print(f"   ! shot {i + 1} ({s['clip']}): window ran past the clip, in moved {s['in']:.2f} -> {tin:.2f}", file=sys.stderr)
        s["_in"] = tin
        fr = frames_of(src, tin, n, W, H, fps)
        k_out = TW.get(s.get("to", "cut"), 0) if i < len(shots) - 1 else 0
        prev_to = shots[i - 1].get("to", "cut") if i else "cut"
        k_in = TW.get(prev_to, 0) if i else 0
        ang_out = s.get("angle", 28 if i % 2 == 0 else 180 - 28)
        ang_in = shots[i - 1].get("angle", 28 if (i - 1) % 2 == 0 else 180 - 28) if i else 0
        for j in range(n):
            f = grade(fr[j].astype(np.float32), worlds.get(s.get("world")))
            if k_in and j < k_in: f = trans(f, prev_to, 1 - j / k_in, "in", ang_in, W, rng)
            if k_out and j >= n - k_out: f = trans(f, s["to"], (j - (n - k_out) + 1) / k_out, "out", ang_out, W, rng)
            f = np.clip(f * vig, 0, 255).astype(np.uint8)
            enc.stdin.write(f.tobytes())
            if (i and j < 2) or (i < len(shots) - 1 and j >= n - 2):
                qa.append((i, j, Image.fromarray(f).resize((W * 240 // H, 240))))
        bt = ""
        if i == len(shots) - 1:
            bt = f"end {ends[i]:.2f}s (music fades)"
        elif beats:
            d = np.array(beats) - ms
            half = np.min(np.abs((d[:-1] + d[1:]) / 2 - ends[i])) if len(d) > 1 else 9
            db = np.min(np.abs(d - ends[i]))
            bt = f"cut {ends[i]:.2f}s ({'on beat' if db < 0.03 else 'on half-beat' if half < 0.03 else f'{min(db, half) * 1000:.0f} ms off grid'})"
        plan.append(f"{i + 1:2d} {s['clip']} src {tin:.2f}-{tin + n / fps:.2f} -> film {starts[i]:.2f}-{ends[i]:.2f} "
                    f"({n / fps:.2f}s) {s.get('world', '-')} to {s.get('to', 'cut')}  {bt}")
    enc.stdin.close(); enc.wait()
    print("\n".join(plan))
    # ------------------------------------------------ audio
    need = film
    mus = np.zeros((int(need * SR), 2), np.float32); looped = None
    if E.get("music"):
        mus, looped = music_track(run / E["music"], ms, need, beats, E.get("loop_bars"))
        mus = np.pad(mus, ((0, int(need * SR) - len(mus)), (0, 0)))
        if looped: print(f"   music short: repeated beats {looped[0]}-{looped[1]}s (bar-aligned, 8 ms crossfade)")
    amb = np.zeros_like(mus); jl = E.get("jcut", 0.3); tail = 0.15
    for i, s in enumerate(shots):
        raw = run / "videos" / f"{s['clip']}.mp4"
        if not raw.exists(): continue
        lead = jl if i else 0.0
        seg = audio_of(raw, s["_in"] - lead, (ends[i] - starts[i]) + lead + tail)
        fi, fo = max(1, int((lead or 0.02) * SR)), int(tail * SR)
        seg[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]; seg[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
        seg *= 10 ** (s.get("amb_db", 0) / 20)
        p0 = int((starts[i] - lead) * SR); p1 = min(len(amb), p0 + len(seg))
        amb[max(0, p0):p1] += seg[max(0, -p0):p1 - p0]
    mix = mus * 10 ** (E.get("music_gain_db", 0) / 20) + amb * 10 ** (E.get("ambience_gain_db", -11) / 20)
    fade = int(E.get("end_fade", 1.0) * SR)
    mix[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)[:, None] ** 1.5
    (run / "audio").mkdir(exist_ok=True); wav = run / "audio" / "mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(wav)],
                   input=mix.astype(np.float32).tobytes(), check=True)
    ln = loudnorm(wav, E.get("lufs", -14), E.get("true_peak", -1))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(run / "_video.mp4"), "-i", str(wav), "-af", ln + f",aresample=192000,alimiter=limit={10 ** ((E.get('true_peak', -1) - 0.3) / 20):.4f}:level=false,aresample=48000",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    (run / "_video.mp4").unlink(missing_ok=True)
    # ------------------------------------------------ QA: 4 frames around every cut + measured loudness
    if qa:
        cuts = {}
        for i, j, im in qa:
            key = i if j >= 2 else i - 1
            cuts.setdefault(key, []).append(im)
        tw = qa[0][2].width; rows = sorted(cuts)
        sheet = Image.new("RGB", (4 * tw + 120, len(rows) * 250), (18, 18, 18)); d = ImageDraw.Draw(sheet); f = font(22)
        for r, key in enumerate(rows):
            d.text((8, r * 250 + 110), f"{key + 1}>{key + 2}", fill=(255, 220, 0), font=f)
            for c, im in enumerate(cuts[key][:4]): sheet.paste(im, (120 + c * tw, r * 250 + 5))
        sheet.save(run / "qa_cuts.png")
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    summ = m[m.rfind("Summary:"):]
    I = next((l.split(":")[1].strip() for l in summ.splitlines() if l.strip().startswith("I:")), "?")
    P = next((l.split(":")[1].strip() for l in summ.splitlines() if l.strip().startswith("Peak:")), "?")
    print(f"-> {out}  ({film:.2f}s, {W}x{H}, {fps} fps, {I}, true peak {P}); cut sheet {run / 'qa_cuts.png'}")


if __name__ == "__main__":
    main()
