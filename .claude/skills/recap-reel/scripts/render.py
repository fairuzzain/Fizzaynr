"""Render a beat-cut recap reel from cleaned clips + music, driven by <run>/edit.json.

Usage: python render.py <run_dir> [--edit edit.json] [--out final.mp4] [--preview] [--from N --to M]
--preview renders at half size, fast preset (for checking the cut).

edit.json (all times in seconds; shot length is counted in BEATS of the music):
{
  "fps": 25,
  "music": "audio/music.mp3", "music_start": 0.0, "beats": "audio/beats.json",
  "end_fade": 0.35, "music_gain_db": 0, "sfx": true, "sfx_gain_db": -14,
  "grade": {"warmth": 0.12, "contrast": 1.08, "saturation": 1.0, "vignette": 0.25, "grain": 0.035},
  "font": "C:/Windows/Fonts/arialbd.ttf",
  "shots": [
    {"clip": "c01", "in": 1.2, "beats": 2, "speed": 1, "zoom": [1.0, 1.06], "fx": ["blur_in"]},
    {"type": "title", "text": "LIVEX 2026", "beats": 1},
    {"type": "title_reveal", "text": "LIVEX 2026", "clip": "c03", "in": 2.0, "beats": 3},
    {"type": "split", "layout": "v3", "panels": [["c02", 3.1], ["c04", 1.0], ["c05", 4.0]], "beats": 2},
    {"clip": "c05", "in": 5.0, "beats": 2, "fx": ["neg_flash", "bw"]},
    {"clip": "c06", "in": 2.0, "beats": 1, "fx": ["flash"]}
  ]
}
Shot keys: clip (name in clean/), in (source start s), beats (int or fraction, e.g. 0.5), speed (0.5-1.5),
zoom [start, end] digital push (1.0 = full frame), pan [dx0, dx1] (-1..1 horizontal drift inside the zoom),
fx list: flash, flash_out, wash (long milky white fade-in), blur_in, blur_out, defocus_in, neg_flash, bw,
         freeze (hold the first frame), shake, strobe (2-frame white blips at each half beat).
Types: clip (default), title (black card + text and/or "logo": "assets/logo.png", "logo_width": 0.25), title_reveal (text over a widening video window);
       both take "width" = text width as a share of the frame (default 0.42 landscape, 0.7 portrait),
       split (layout v2|v3|v4|h3|grid4, panels [[clip, in], ...], "stagger": true pops panels in one by one).
A shot can also use "frames": N instead of beats (exact length).
"""
import os
import argparse, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SR = 48000


# ---------------------------------------------------------------- decoding
def read_frames(path, t0, n, W, H, fps, speed=1.0):
    """n output frames from `path` starting at t0, sampled at `speed`, resized to cover WxH."""
    need = max(1, int(math.ceil(n * speed)) + 2)
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0, t0):.3f}", "-i", str(path), "-frames:v", str(need),
           "-vf", f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase:flags=bicubic,crop={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8)
    got = len(arr) // (W * H * 3)
    if got == 0:
        raise RuntimeError(f"no frames from {path} at {t0}s")
    src = arr[: got * W * H * 3].reshape(got, H, W, 3)
    idx = np.minimum((np.arange(n) * speed).round().astype(int), got - 1)
    return src[idx].astype(np.float32)


# ---------------------------------------------------------------- per-frame tools
def zoom_pan(f, z, dx=0.0):
    if z <= 1.0001 and abs(dx) < 1e-4:
        return f
    H, W = f.shape[:2]
    cw, ch = W / z, H / z
    cx = W / 2 + dx * (W - cw) / 2
    M = np.float32([[z, 0, -(cx - cw / 2) * z], [0, z, -(H / 2 - ch / 2) * z]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def motion_blur(f, k):
    k = int(k)
    if k < 2:
        return f
    ker = np.ones((1, k), np.float32) / k
    return cv2.filter2D(f, -1, ker, borderType=cv2.BORDER_REFLECT)


def gray(f, contrast=1.15):
    g = f @ np.float32([0.299, 0.587, 0.114])
    g = (g - 128) * contrast + 128
    return np.repeat(g[..., None], 3, axis=2)


def to_white(f, a):
    return f + (255 - f) * a


def apply_fx(frames, fx, fps, beat):
    n = len(frames)
    out = frames
    if "freeze" in fx:
        out = np.repeat(out[:1], n, axis=0)
    if "bw" in fx:
        out = np.stack([gray(f) for f in out])
    if "shake" in fx:
        rng = np.random.default_rng(7)
        for i in range(n):
            dx, dy = rng.normal(0, out.shape[2] * 0.004, 2)
            M = np.float32([[1.02, 0, dx - out.shape[2] * 0.01], [0, 1.02, dy - out.shape[1] * 0.01]])
            out[i] = cv2.warpAffine(out[i], M, (out.shape[2], out.shape[1]), borderMode=cv2.BORDER_REFLECT)
    if "blur_in" in fx:
        for i, (k, z) in enumerate([(90, 1.12), (55, 1.07), (28, 1.035), (10, 1.01)][: n]):
            out[i] = motion_blur(zoom_pan(out[i], z), k * out.shape[2] / 1280)
    if "blur_out" in fx:
        for j, k in enumerate([12, 40, 80][-min(3, n):]):
            i = n - min(3, n) + j
            out[i] = motion_blur(out[i], k * out.shape[2] / 1280)
    if "defocus_in" in fx:
        for i, s in enumerate([18, 11, 6, 3, 1][: n]):
            out[i] = cv2.GaussianBlur(out[i], (0, 0), s * out.shape[2] / 1280)
    if "neg_flash" in fx:
        for i in range(min(2, n)):
            out[i] = 255 - gray(out[i], 1.4)
    if "flash" in fx:
        for i, a in enumerate([0.92, 0.6, 0.3, 0.1][: n]):
            out[i] = to_white(out[i], a)
    if "wash" in fx:
        m = min(n, max(4, int(fps * 0.35)))
        for i in range(m):
            out[i] = to_white(out[i], 0.85 * (1 - i / m) ** 1.5)
    if "flash_out" in fx:
        for j, a in enumerate([0.25, 0.6, 0.9][-min(3, n):]):
            out[n - min(3, n) + j] = to_white(out[n - min(3, n) + j], a)
    if "strobe" in fx:
        step = max(2, int(round(beat * fps / 2)))
        for i in range(step, n, step):
            out[i] = to_white(out[i], 0.7)
    return out


# ---------------------------------------------------------------- text
BOLD_FONTS = [*([os.environ["FONT_BOLD"]] if os.environ.get("FONT_BOLD") else []), "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
_fonts = {}


def get_font(path, size):
    key = (path, size)
    if key not in _fonts:
        try:
            _fonts[key] = ImageFont.truetype(path, size)
        except OSError:
            for c in BOLD_FONTS:
                try:
                    _fonts[key] = ImageFont.truetype(c, size); break
                except OSError:
                    pass
            else:
                _fonts[key] = ImageFont.load_default()
    return _fonts[key]


def text_layer(W, H, text, font_path, width=0.42):
    """Float alpha layer (0..1) with centred white text sized to `width` x frame width (capped at 18% of height)."""
    probe = get_font(font_path, 100)
    bb = probe.getbbox(text)
    size = int(100 * min(width * W / max(1, bb[2] - bb[0]), 0.18 * H / max(1, bb[3] - bb[1])))
    f = get_font(font_path, max(12, size))
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((W - tw) / 2 - bb[0], (H - th) / 2 - bb[1]), text, fill=255, font=f)
    return np.asarray(im, np.float32)[..., None] / 255.0


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


# ---------------------------------------------------------------- shots
def render_shot(s, n, run, W, H, fps, beat, font_path):
    typ = s.get("type", "clip")
    clip = lambda name: run / "clean" / f"{name}.mp4"
    speed = float(s.get("speed", 1.0))
    if typ == "title":
        frames = np.zeros((n, H, W, 3), np.float32)
        if s.get("text"):
            frames += text_layer(W, H, s["text"], font_path, s.get("width", 0.42 if W > H else 0.7)) * 255
        if s.get("logo"):  # PNG with alpha, centred (below the text when both are given)
            lg = Image.open(run / s["logo"]).convert("RGBA")
            lw = int(W * s.get("logo_width", 0.25 if W > H else 0.45))
            lg = lg.resize((lw, max(1, round(lg.height * lw / lg.width))), Image.LANCZOS)
            arr = np.asarray(lg, np.float32)
            x0, y0 = (W - lg.width) // 2, (H - lg.height) // 2 + (int(H * 0.14) if s.get("text") else 0)
            y1, x1 = min(H, y0 + lg.height), min(W, x0 + lg.width)
            al = arr[: y1 - y0, : x1 - x0, 3:] / 255
            frames[:, y0:y1, x0:x1] = frames[:, y0:y1, x0:x1] * (1 - al) + arr[: y1 - y0, : x1 - x0, :3] * al
    elif typ == "title_reveal":
        src = read_frames(clip(s["clip"]), s.get("in", 0), n, W, H, fps, speed)
        txt = text_layer(W, H, s["text"], font_path, s.get("width", 0.42 if W > H else 0.7))
        frames = np.zeros_like(src)
        grow = max(1, int(n * s.get("grow", 0.7)))
        for i in range(n):
            w = int(W * ease(i / grow))
            frames[i, :, :w] = src[i, :, :w]
            fade = 1.0 - max(0.0, (i - grow) / max(1, n - grow))  # text fades once the window is full
            frames[i] = frames[i] * (1 - txt * fade) + 255 * txt * fade
    elif typ == "split":
        panels = s["panels"]
        layout = s.get("layout", "v3")
        frames = np.zeros((n, H, W, 3), np.float32)
        if layout == "grid4":
            rects = [(0, 0, W // 2, H // 2), (W // 2, 0, W - W // 2, H // 2), (0, H // 2, W // 2, H - H // 2),
                     (W // 2, H // 2, W - W // 2, H - H // 2)]
        elif layout == "h3":
            rects = [(0, i * H // 3, W, (i + 1) * H // 3 - i * H // 3) for i in range(3)]
        else:
            k = int(layout[1:]) if layout[0] == "v" else 3
            rects = [(i * W // k, 0, (i + 1) * W // k - i * W // k, H) for i in range(k)]
        for pi, ((name, t0), (x, y, w, h)) in enumerate(zip(panels, rects)):
            src = read_frames(clip(name), t0, n, W, H, fps, speed)
            if layout == "grid4":
                src = np.stack([cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA) for f in src])
            else:  # crop the centre of the full frame to the panel shape (keeps subjects full size)
                sx, sy = (W - w) // 2, (H - h) // 2
                src = src[:, sy:sy + h, sx:sx + w]
            start = int(pi * n * 0.5 / len(panels)) if s.get("stagger") else 0
            frames[start:, y:y + h, x:x + w] = src[start:]
            if s.get("stagger") and start < n:  # small flash as each panel pops in
                frames[start, y:y + h, x:x + w] = to_white(frames[start, y:y + h, x:x + w], 0.7)
    else:
        frames = read_frames(clip(s["clip"]), s.get("in", 0), n, W, H, fps, speed)
    z0, z1 = s.get("zoom", [1.0, 1.0])
    p0, p1 = s.get("pan", [0.0, 0.0])
    if (z0, z1, p0, p1) != (1.0, 1.0, 0.0, 0.0):
        for i in range(n):
            t = i / max(1, n - 1)
            frames[i] = zoom_pan(frames[i], z0 + (z1 - z0) * t, p0 + (p1 - p0) * t)
    return apply_fx(frames, s.get("fx", []), fps, beat)


# ---------------------------------------------------------------- grade
class Grade:
    def __init__(self, g, W, H):
        self.warm = g.get("warmth", 0.12)
        self.con = g.get("contrast", 1.08)
        self.sat = g.get("saturation", 1.0)
        self.grain = g.get("grain", 0.035)
        v = g.get("vignette", 0.25)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        self.vig = (1 - v * np.clip(r, 0, 1) ** 2.2)[..., None]
        self.rng = np.random.default_rng(3)
        self.tint = np.float32([1 + self.warm * 0.35, 1 + self.warm * 0.08, 1 - self.warm * 0.3])

    def __call__(self, f):
        x = f / 255.0
        x = x * self.tint
        if self.sat != 1.0:
            lum = x @ np.float32([0.299, 0.587, 0.114])
            x = lum[..., None] + (x - lum[..., None]) * self.sat
        x = 0.5 + (x - 0.5) * self.con
        x = x * self.vig
        if self.grain:
            h, w = x.shape[:2]
            g = self.rng.normal(0, self.grain, (h // 2, w // 2)).astype(np.float32)
            x = x + cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)[..., None]
        return np.clip(x * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- audio
def load_audio(path, start, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur + 0.5:.3f}", "-i", str(path),
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(dur * SR)
    if len(a) < n:
        a = np.pad(a, ((0, n - len(a)), (0, 0)))
    return a[:n]


def whoosh(rng, dur=0.42):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.normal(0, 1, n).astype(np.float32)
    out = np.zeros(n, np.float32)
    # sweep a resonant band-pass upward: cheap one-pole pair with moving cutoff
    lo = hi = 0.0
    for i in range(n):
        fc = 300 + 5000 * t[i] ** 1.7
        a = 1 - math.exp(-2 * math.pi * fc / SR)
        lo += a * (noise[i] - lo)
        hi += (a * 0.35) * (lo - hi)
        out[i] = lo - hi
    env = np.sin(np.pi * t) ** 2 * t ** 0.6
    out = out * env
    return out / (np.abs(out).max() + 1e-9)


def hit(dur=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (48 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 6)
    click = np.random.default_rng(1).normal(0, 1, n) * np.exp(-t * 90) * 0.3
    x = (body + click).astype(np.float32)
    return x / np.abs(x).max()


def mix_sfx(audio, cues, gain_db=-14):
    rng = np.random.default_rng(11)
    g = 10 ** (gain_db / 20)
    w = whoosh(rng)
    h = hit()
    for kind, t in cues:
        snd, lead = (w, len(w) * 0.8 / SR) if kind == "whoosh" else (h, 0.0)
        s0 = int((t - lead) * SR)
        a0, b0 = max(0, s0), min(len(audio), s0 + len(snd))
        if b0 > a0:
            audio[a0:b0] += (snd[a0 - s0:b0 - s0] * g * (0.8 if kind == "hit" else 1.0))[:, None]
    return audio


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("--edit", default="edit.json"); ap.add_argument("--out")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--from", dest="sfrom", type=int, default=0); ap.add_argument("--to", type=int)
    a = ap.parse_args()
    run = Path(a.run)
    E = json.loads((run / a.edit).read_text())
    W, H = json.loads((run / "frames/index.json").read_text())["size"]
    if a.preview:
        W, H = W // 2 // 2 * 2, H // 2 // 2 * 2
    fps = E.get("fps", 25)
    B = json.loads((run / E["beats"]).read_text())
    m0 = E.get("music_start", 0.0)
    grid = [b - m0 for b in B["beats"] if b - m0 > 0.05]
    beat = B["beat"]

    def beat_time(k):  # time of fractional beat index k (k=1 is the first beat after the start)
        if k <= 0: return 0.0
        i = int(math.floor(k))
        frac = k - i
        def bt(j):
            if j <= 0: return 0.0
            return grid[j - 1] if j - 1 < len(grid) else grid[-1] + (j - len(grid)) * beat
        return bt(i) + frac * (bt(i + 1) - bt(i))

    # shot boundaries in frames
    bounds, kpos, fpos = [], 0.0, 0
    for s in E["shots"]:
        if "frames" in s:
            n = int(s["frames"])
            kpos = None
        else:
            if kpos is None:
                raise SystemExit("a beats-shot after a frames-shot: use frames for the rest or none")
            kpos += float(s["beats"])
            n = int(round(beat_time(kpos) * fps)) - fpos
        bounds.append((fpos, max(1, n)))
        fpos += max(1, n)
    total = fpos
    dur = total / fps
    shots = list(enumerate(E["shots"]))[a.sfrom: a.to]
    print(f"{len(E['shots'])} shots · {total} frames · {dur:.2f}s · {B['bpm']} bpm · {W}x{H}", file=sys.stderr)

    out = run / (a.out or ("preview.mp4" if a.preview else "final.mp4"))
    vtmp = out.with_suffix(".video.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if a.preview else "slow",
                            "-crf", "23" if a.preview else "16", "-pix_fmt", "yuv420p", str(vtmp)], stdin=subprocess.PIPE)
    grade = Grade(E.get("grade", {}), W, H)
    font_path = E.get("font", BOLD_FONTS[0])
    cues = []
    for i, s in shots:
        f0, n = bounds[i]
        t0 = f0 / fps
        fx = s.get("fx", [])
        if any(x in fx for x in ("blur_in", "wash")) or s.get("type") == "split" and s.get("stagger"):
            cues.append(("whoosh", t0))
        if "flash" in fx or "neg_flash" in fx or s.get("type") in ("title", "title_reveal"):
            cues.append(("hit", t0))
        frames = render_shot(s, n, run, W, H, fps, beat, font_path)
        for f in frames:
            enc.stdin.write(grade(f).tobytes())
        print(f"  shot {i + 1:2d} {s.get('type', 'clip'):12s} {s.get('clip', s.get('text', '')):>12} "
              f"{t0:6.2f}s +{n:3d}f {','.join(fx)}", file=sys.stderr)
    enc.stdin.close(); enc.wait()

    # audio: music + optional synth sfx + optional clip ambience
    start_t = bounds[shots[0][0]][0] / fps
    end_t = (bounds[shots[-1][0]][0] + bounds[shots[-1][0]][1]) / fps
    seg = end_t - start_t
    audio = load_audio(run / E["music"], m0 + start_t, seg) * (10 ** (E.get("music_gain_db", 0) / 20))
    if E.get("sfx", True):
        audio = mix_sfx(audio, [(k, t - start_t) for k, t in cues], E.get("sfx_gain_db", -14))
    fade = E.get("end_fade", 0.35)
    nf = int(fade * SR)
    if nf and a.to is None:
        audio[-nf:] *= np.linspace(1, 0, nf)[:, None] ** 1.5
    peak = np.abs(audio).max()
    if peak > 0.98:
        audio *= 0.98 / peak
    wav = out.with_suffix(".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(wav)],
                   input=audio.astype(np.float32).tobytes(), check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vtmp), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "256k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-shortest", "-movflags", "+faststart",
                    str(out)], check=True)
    vtmp.unlink(); wav.unlink()
    print(f"wrote {out} ({dur:.2f}s)")


if __name__ == "__main__":
    main()
