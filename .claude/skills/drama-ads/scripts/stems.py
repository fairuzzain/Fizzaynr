#!/usr/bin/env python3
"""A clip's own music taken out with Demucs (htdemucs: vocals, drums, bass, other). Every clip prompt says "No music and no
score.", yet a clip can come back with a score of its own, which plays against the film's score (references/clips.md, Order
of work, Music). The modes, the room split and the measure are the drama-editor skill's stems.py, tried there on generated
clips.

  voice_room  the lines, the hits and the room: of the other stem only its noise-like part (the room, a street, rain),
              the tonal part (held notes, chords, pads) dropped with the bass; a noisy part of the music (a riser, a
              shaker) stays, a steady hum of the room goes
  voice_fx    the lines and the hits (the drums stem: blows, steps, doors, and a score's beat); the tonal music (bass,
              other) goes, and with it most of the room
  voice       the lines alone: the music, the room and the clip's own effects go
  voice_rest  the lines, everything else 12 dB under: the music buried, the room and the effects still faintly there

Demucs is in the DEV sandbox, its weights cached (it runs offline); the prod sandbox has none: `check` says so, and then a
clip with music is remade. Never pip install it. Run it from the film's folder. A clip is split once; its stems are reused
while its file stays the same.
usage: python3 stems.py check                       {"demucs": true|false}
       python3 stems.py split <clip.mp4> [...]      split the clips that have sound (600 s timeout) and measure what each
                                                    holds under and between its lines -> stems/htdemucs/<clip>/,
                                                    stems/stems.json
       python3 stems.py clean <clip.mp4> <mode>     the clip's picture as it is, its sound as <mode> keeps it, in the
                                                    original's sample rate and channels -> <clip>-clean.mp4"""
import json, os, subprocess, sys

MODEL = "htdemucs"
SR = 44100                      # Demucs's rate: the stems come back at it
STEMS = ("vocals", "drums", "bass", "other")
MODES = {"voice": {"vocals": 0.0},
         "voice_fx": {"vocals": 0.0, "drums": 0.0},
         "voice_room": {"vocals": 0.0, "drums": 0.0, "room": 3.0},   # the split keeps a noise ~5 dB under its level
         "voice_rest": {"vocals": 0.0, "drums": -12.0, "bass": -12.0, "other": -12.0}}
KEEP_UNDER_DB = -20.0           # music further under the lines than this, under them and between them: little to take out
N_FFT, HOP = 2048, 512          # the room split's STFT (46 ms frames at 44.1 kHz)
KERNEL, MARGIN = 17, 2.0        # median filters over 17 frames / bins; a bin is tonal or a hit when twice the other


def available():
    return subprocess.run([sys.executable, "-c", "import demucs, torch"], capture_output=True).returncode == 0


def name(clip):
    return os.path.splitext(os.path.basename(clip))[0]


def stem_path(nm, stem):
    return os.path.join("stems", MODEL, nm, stem + ".wav")


def probe(clip):
    """the clip's first audio stream ({sample_rate, channels, bit_rate}), or None when it has no sound"""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                        "stream=sample_rate,channels,bit_rate", "-of", "json", clip], capture_output=True, text=True, check=True)
    s = json.loads(r.stdout).get("streams") or []
    return s[0] if s else None


def decode(src, sr=SR, ch=2):
    """a file's sound as float32 (n, ch) through ffmpeg"""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def encode(x, out, sr=SR, codec="pcm_f32le"):
    import numpy as np
    x = np.ascontiguousarray(x, np.float32)
    ch = 1 if x.ndim == 1 else x.shape[1]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(ch), "-i", "-", "-c:a", codec, out],
                   input=x.tobytes(), check=True)


def fresh(clip):
    """the clip's four stems exist and are newer than its file"""
    ps = [stem_path(name(clip), s) for s in STEMS]
    return all(os.path.exists(p) for p in ps) and min(os.path.getmtime(p) for p in ps) >= os.path.getmtime(clip)


def _median(M, axis):
    """M median-filtered over KERNEL along axis (0 bins, 1 frames), 512 frames at a time to keep the memory small"""
    import numpy as np
    h, out = KERNEL // 2, np.empty_like(M)
    P = np.pad(M, ((h, h), (0, 0)) if axis == 0 else ((0, 0), (h, h)), mode="edge")
    for a in range(0, M.shape[1], 512):
        b = min(M.shape[1], a + 512)
        if axis == 0:
            out[:, a:b] = np.median(np.lib.stride_tricks.sliding_window_view(P[:, a:b], KERNEL, axis=0), axis=-1)
        else:
            out[:, a:b] = np.median(np.lib.stride_tricks.sliding_window_view(P[:, a:b + 2 * h], KERNEL, axis=1), axis=-1)
    return out


def noise_part(x):
    """the noise-like part of a mono signal: what is neither held in pitch (tonal: steady over time) nor struck (a hit:
    spread over frequency), by harmonic-percussive median filtering with a margin"""
    import numpy as np
    w = np.hanning(N_FFT + 1)[:-1].astype(np.float32)
    xp = np.pad(x.astype(np.float32), (N_FFT // 2, N_FFT))
    S = np.fft.rfft(np.lib.stride_tricks.sliding_window_view(xp, N_FFT)[::HOP] * w, axis=1).T
    M = np.abs(S).astype(np.float32)
    H, P = _median(M, 1), _median(M, 0)
    eps = 1e-10
    tonal = H ** 2 / (H ** 2 + (MARGIN * P) ** 2 + eps)
    hit = P ** 2 / (P ** 2 + (MARGIN * H) ** 2 + eps)
    fr = np.fft.irfft((S * np.clip(1 - tonal - hit, 0, 1)).T, n=N_FFT, axis=1).astype(np.float32) * w
    out, norm = np.zeros(len(fr) * HOP + N_FFT, np.float32), np.zeros(len(fr) * HOP + N_FFT, np.float32)
    for i, f in enumerate(fr):
        out[i * HOP:i * HOP + N_FFT] += f
        norm[i * HOP:i * HOP + N_FFT] += w * w
    return (out / np.maximum(norm, 1e-6))[N_FFT // 2:N_FFT // 2 + len(x)]


def room(nm):
    """the clip's room stem (the other stem's noise-like part), made once beside its stems"""
    import numpy as np
    p, src = stem_path(nm, "room"), stem_path(nm, "other")
    if not os.path.exists(p) or os.path.getmtime(p) < os.path.getmtime(src):
        x = decode(src)
        encode(np.stack([noise_part(x[:, k]) for k in range(2)], 1), p)
    return p


def split(todo):
    inp = os.path.join("stems", "in")
    os.makedirs(inp, exist_ok=True)
    wavs = []
    for clip in todo:
        w = os.path.join(inp, name(clip) + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-vn", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", w],
                       check=True)
        wavs.append(w)
    cmd = [sys.executable, "-m", "demucs", "-n", MODEL, "-j", str(os.cpu_count() or 1), "-o", "stems"] + wavs
    r = subprocess.run(cmd, env=dict(os.environ, HF_HUB_OFFLINE="1"), capture_output=True, text=True)
    if r.returncode:   # the weights are not cached here: fetched once (~80 MB)
        r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("demucs failed:\n" + r.stderr[-2000:])
    for w in wavs:
        os.remove(w)


def db(x):
    import numpy as np
    return round(float(10 * np.log10(np.mean(x.astype(np.float64) ** 2) + 1e-12)), 1) if x.size else None


def measure(nm):
    """what the clip holds, in dB: its lines, and the tonal music (bass + other), the hits (drums) and the room under the
    lines and between them; the lines are the 0.1 s windows where the vocals stem is within 15 dB of its loud end"""
    import numpy as np
    hop = 1600   # 0.1 s at 16 kHz
    x = {s: decode(stem_path(nm, s), 16000, 1)[:, 0] for s in STEMS}
    k = min(len(v) for v in x.values()) // hop
    win = {s: v[:k * hop].reshape(k, hop) for s, v in x.items()}
    music = win["bass"] + win["other"]
    rm = decode(room(nm), 16000, 1)[:, 0][:k * hop].reshape(k, hop)
    lv = 10 * np.log10((win["vocals"].astype(np.float64) ** 2).mean(1) + 1e-12)
    lines = lv > (np.percentile(lv, 90) - 15 if k else 0)
    if lv.size and np.percentile(lv, 90) < -50:   # no voice in the clip
        lines[:] = False
    return {"clip": nm, "voice_db": db(win["vocals"][lines]),
            "music_under_lines_db": db(music[lines]), "music_between_lines_db": db(music[~lines]),
            "hits_between_lines_db": db(win["drums"][~lines]), "room_between_lines_db": db(rm[~lines])}


def against(rows):
    """each row's music, hits and room against its lines, or, in a clip without lines, against the film's (the median of the
    clips that have them); `music` says whether it comes within KEEP_UNDER_DB of them"""
    voices = sorted(r["voice_db"] for r in rows if r["voice_db"] is not None)
    film = voices[len(voices) // 2] if voices else None
    for r in rows:
        ref = r["voice_db"] if r["voice_db"] is not None else film
        r["against"] = "its lines" if r["voice_db"] is not None else ("the film's lines" if film is not None else None)
        for key in ("music_under_lines", "music_between_lines", "hits_between_lines", "room_between_lines"):
            v = r[key + "_db"]
            r[key] = None if v is None or ref is None else round(v - ref, 1)
        r["music"] = any(r[key] is not None and r[key] > KEEP_UNDER_DB for key in ("music_under_lines", "music_between_lines"))
    return rows


def clean(clip, mode):
    import numpy as np
    if mode not in MODES:
        raise SystemExit(f"mode '{mode}' is none of {', '.join(MODES)}")
    nm, a = name(clip), probe(clip)
    if a is None:
        raise SystemExit(f"{clip} has no sound")
    if not fresh(clip):
        raise SystemExit(f"{clip} is not split yet, or changed since: python3 stems.py split {clip}")
    if "room" in MODES[mode]:
        room(nm)
    parts = {s: decode(stem_path(nm, s)) for s in MODES[mode]}
    n = min(len(x) for x in parts.values())
    mix = np.zeros((n, 2), np.float32)
    for stem, gain in MODES[mode].items():
        mix += parts[stem][:n] * np.float32(10 ** (gain / 20))
    wav = stem_path(nm, mode)
    encode(mix, wav)
    out = os.path.join(os.path.dirname(clip), nm + "-clean.mp4")
    rate = ["-b:a", a["bit_rate"]] if a.get("bit_rate", "N/A") != "N/A" else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-ar", str(a["sample_rate"]), "-ac", str(a["channels"])] + rate + ["-movflags", "+faststart", out],
                   check=True)
    print(json.dumps({"clip": nm, "mode": mode, "out": out}))


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip(), file=sys.stdout if len(sys.argv) > 1 else sys.stderr)
        sys.exit(0 if len(sys.argv) > 1 else 2)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "check":
        print(json.dumps({"demucs": available()}))
        return
    if cmd == "clean":
        if len(args) != 2:
            raise SystemExit("usage: python3 stems.py clean <clip.mp4> <mode>")
        clean(*args)
        return
    if cmd != "split" or not args:
        raise SystemExit(__doc__.strip())
    for clip in args:
        if not os.path.exists(clip):
            raise SystemExit(f"no such clip: {clip}")
    chosen = [c for c in args if probe(c)]
    todo = [c for c in chosen if not fresh(c)]
    if todo:
        if not available():
            raise SystemExit("no Demucs in this sandbox (the prod sandbox has none; never pip install it): a clip with music "
                             "is remade, or in a narrated film muted under the track")
        print(f"splitting {len(todo)} clip(s) with {MODEL}...", file=sys.stderr, flush=True)
        split(todo)
    path = os.path.join("stems", "stems.json")
    old = {r["clip"]: r for r in json.load(open(path))} if os.path.exists(path) else {}
    old.update({r["clip"]: r for r in (measure(name(c)) for c in chosen)})
    rows = against(list(old.values()))
    os.makedirs("stems", exist_ok=True)
    json.dump(rows, open(path, "w"), indent=1)
    picked = {name(c) for c in chosen}
    for r in rows:
        if r["clip"] in picked:
            under = f"{r['music_under_lines']} dB while they speak, " if r["music_under_lines"] is not None else ""
            print(f"  {r['clip']}: music against {r['against']}: {under}{r['music_between_lines']} dB between them; hits "
                  f"{r['hits_between_lines']} dB and room {r['room_between_lines']} dB between"
                  + (" -> music to take out" if r["music"] else ""), file=sys.stderr)
    print(json.dumps([r for r in rows if r["clip"] in picked]))


if __name__ == "__main__":
    main()
