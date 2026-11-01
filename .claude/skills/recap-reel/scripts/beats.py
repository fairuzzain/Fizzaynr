"""Beat grid for a music track: tempo, beat times and downbeat-ish accents.

Usage: python beats.py <music.mp3|wav> [--out beats.json] [--bpm-min 80 --bpm-max 160]
Writes {"bpm", "beat", "beats": [s...], "first_beat", "duration", "strong": [s...], "suggested_start", "beat_rms"}.
suggested_start = music_start that puts the loudest --span beats (default 28) under the reel.
numpy/scipy only (no librosa): spectral-flux onsets + autocorrelation tempo + phase fit.
"""
import argparse, json, subprocess, sys
import numpy as np
from scipy.signal import find_peaks

SR, HOP, WIN = 22050, 512, 2048


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def onset_env(y):
    n = 1 + (len(y) - WIN) // HOP
    frames = np.lib.stride_tricks.as_strided(y, (n, WIN), (y.strides[0] * HOP, y.strides[0]))
    mag = np.log1p(10 * np.abs(np.fft.rfft(frames * np.hanning(WIN), axis=1)))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(1)
    flux = np.concatenate([[0], flux])
    flux -= np.convolve(flux, np.ones(16) / 16, "same")
    return np.maximum(flux, 0) / (flux.max() + 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("--out")
    ap.add_argument("--bpm-min", type=float, default=80); ap.add_argument("--bpm-max", type=float, default=165)
    ap.add_argument("--span", type=int, default=28, help="beats the reel needs, for suggested_start")
    a = ap.parse_args()
    y = load(a.audio)
    env = onset_env(y)
    fps = SR / HOP
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    lags = np.arange(len(ac))
    ok = (lags >= fps * 60 / a.bpm_max) & (lags <= fps * 60 / a.bpm_min)
    # weight towards ~110 bpm so half/double tempo does not win by accident
    bpm_of = 60 * fps / np.maximum(lags, 1)
    w = np.exp(-0.5 * (np.log2(bpm_of / 110) / 0.9) ** 2)
    period = lags[ok][np.argmax((ac * w)[ok])]
    # refine period with parabolic peak fit
    p = period
    if 1 <= p < len(ac) - 1:
        d = (ac[p - 1] - ac[p + 1]) / (2 * (ac[p - 1] - 2 * ac[p] + ac[p + 1]) + 1e-12)
        p = p + float(np.clip(d, -0.5, 0.5))
    bpm = 60 * fps / p
    # phase: offset that maximises onset energy on the grid
    best, phase = -1, 0
    for off in np.arange(0, p, 0.25):
        idx = np.round(np.arange(off, len(env) - 1, p)).astype(int)
        s = env[idx].sum()
        if s > best: best, phase = s, off
    beats = np.arange(phase, len(env) - 1, p) / fps
    # snap each grid beat to a nearby onset peak (±60 ms) for tight cuts
    peaks, _ = find_peaks(env, height=0.15, distance=int(fps * 0.1))
    pt = peaks / fps
    snapped = []
    for b in beats:
        j = np.argmin(np.abs(pt - b)) if len(pt) else None
        snapped.append(float(pt[j]) if j is not None and abs(pt[j] - b) < 0.06 else float(b))
    strength = [float(env[min(int(b * fps), len(env) - 1)]) for b in snapped]
    thr = np.percentile(strength, 70) if strength else 1
    # loudness per beat and the start beat whose next `--span` beats are loudest (skip quiet intros)
    rms = [float(np.sqrt(np.mean(y[int(b * SR):int((b + 60 / bpm) * SR)] ** 2) + 1e-12)) for b in snapped]
    span = max(1, min(a.span, len(rms)))
    win = [np.mean(rms[i:i + span]) for i in range(max(1, len(rms) - span + 1))]
    sug = int(np.argmax(win)) if win else 0
    sug_t = snapped[sug - 1] if sug > 0 else 0.0  # start one beat early so the first cut lands on beat sug
    out = {"bpm": round(float(bpm), 2), "beat": round(60 / bpm, 4), "first_beat": round(snapped[0], 3),
           "duration": round(len(y) / SR, 3), "beats": [round(b, 3) for b in snapped],
           "strong": [round(b, 3) for b, s in zip(snapped, strength) if s >= thr],
           "suggested_start": round(sug_t, 3), "beat_rms": [round(r, 4) for r in rms]}
    js = json.dumps(out, indent=1)
    if a.out:
        open(a.out, "w").write(js)
    print(f"bpm {out['bpm']} · beat {out['beat']}s · {len(snapped)} beats · first {out['first_beat']}s · "
          f"{len(out['strong'])} strong · duration {out['duration']}s · suggested music_start {out['suggested_start']}s", file=sys.stderr)
    if not a.out:
        print(js)


if __name__ == "__main__":
    main()
