#!/usr/bin/env python3
"""Rakit audio final: VO + jeda + SFX + musik (opsional) + normalisasi -14 LUFS.

    python3 mix.py <build>            (biasanya dipanggil render_all.py)
    python3 mix.py --list [<build>]   tampilkan sumber tiap jenis SFX tanpa merakit

Membaca dari folder build, jadi selalu sinkron dengan halaman:
  project.json   vo, pauses, tail, audio
  seg/info.json  TOTAL dan daftar SFX [[t, jenis, gain], ...] dari halaman (dibuat render_all.py)
Menulis: mix.wav

Jenis SFX: click pop bubble whoosh swish thud ding tick type riser error
Urutan sumber tiap jenis (yang pertama ada, dipakai):
  1. project.json audio.sfx_files {"whoosh": "aset/sfx/whoosh.mp3"}
  2. project.json audio.sfx_dir   folder SFX user, dipetakan dari nama file (lihat NAME_MAP)
  3. SFX bawaan skill (assets/sfx/, 9 file): click, pop, bubble (bubble-pop), whoosh, swish (swipe), thud (punch),
     ding (notification), type (typing), error; tick dibuat dari click 10x
  4. SFX sintetis numpy
audio.sfx_source = "synth" melewati langkah 3 (semua sintetis kecuali yang diisi user).

project.json -> "audio":
  "sfx": true            false = tanpa SFX
  "sfx_gain": 1.0        pengali semua SFX (0.7 = lebih pelan)
  "music": "aset/musik.mp3", "music_level": "pelan"|"sedang"   (default tanpa musik)
  "lufs": -14
VO dinormalkan dulu ke level bicara yang sama (sekitar -20 dBFS), jadi perbandingan SFX:VO
tetap sama walaupun rekaman VO pelan atau keras.
"""
import json, os, subprocess, sys
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.environ.get("FFMPEG_BIN", "ffmpeg")
rng = np.random.default_rng(7)
db = lambda g: 10 ** (g / 20)
TYPES = ["click", "pop", "bubble", "whoosh", "swish", "thud", "ding", "tick", "type", "riser", "error"]
LEVEL = dict(click=.17, pop=.17, bubble=.15, whoosh=.18, swish=.20, thud=.30, ding=.16, tick=.12, type=.14, riser=.17, error=.16)
EARLY = dict(whoosh=.15, riser=0.0)          # SFX sintetis yang dimulai sedikit sebelum aksinya
BUNDLED = dict(click="click.mp3", pop="pop.mp3", bubble="bubble-pop.mp3", whoosh="whoosh.mp3", swish="swipe.mp3",
               thud="punch.mp3", ding="notification.mp3", type="typing.mp3", error="error.mp3")
PEAK_ALIGN = ("whoosh", "riser")           # file whoosh/riser: puncaknya diletakkan tepat di waktu aksi (maks 0,35 dtk lebih awal)
NAME_MAP = [("whoosh", ("whoosh", "woosh", "transition", "transisi")), ("swish", ("swish", "swipe", "swoosh")),
            ("thud", ("thud", "impact", "boom", "hit", "slam", "punch")), ("riser", ("riser", "rise", "build")),
            ("ding", ("ding", "notif", "chime", "success", "sukses", "bell")), ("click", ("click", "klik", "tap")),
            ("bubble", ("bubble",)), ("pop", ("pop",)), ("type", ("typing", "keyboard", "ketik", "type")),
            ("tick", ("tick", "counter", "hitung")), ("error", ("error", "wrong", "salah", "buzz", "fail"))]


# ---------- SFX sintetis (dari versi lama skill) ----------
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))


def s_click():
    n = int(.06 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * env(n, .0005, .006) * .6 + bp(rng.standard_normal(n), 1500, 9000) * env(n, .0003, .004) * .5
def s_pop():
    n = int(.14 * SR); t = np.arange(n) / SR; f = 500 + 1400 * (t / .14) ** .5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .035) * .7
def s_bubble():
    n = int(.18 * SR); t = np.arange(n) / SR; f = 700 + 900 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .05) * .6
def s_whoosh():
    n = int(.45 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 300, 5000) * np.sin(np.pi * np.clip(t / .45, 0, 1)) ** 2 * .35
def s_swish():
    n = int(.25 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1200, 8000) * np.sin(np.pi * t / .25) ** 3 * .3
def s_thud():
    n = int(.5 * SR); t = np.arange(n) / SR; f = 110 * np.exp(-t * 6) + 45
    body = np.sin(2 * np.pi * np.cumsum(f) / SR); body = np.tanh(1.4 * (body + .25 * np.sin(4 * np.pi * np.cumsum(f) / SR)))
    return body * env(n, .002, .16) + bp(rng.standard_normal(n), 60, 900) * env(n, .001, .03) * .5
def s_ding():
    n = int(.9 * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * a for f, a in [(1320, .5), (1980, .25), (2640, .12)]) * env(n, .003, .25) * .45
def s_type():
    n = int(.05 * SR); return bp(rng.standard_normal(n), 800, 6000) * env(n, .0005, .008) * .5
def s_riser():
    n = int(.8 * SR); t = np.arange(n) / n
    return bp(rng.standard_normal(n), 900, 7000) * t ** 2.4 * (1 - np.clip((t - .95) / .05, 0, 1)) * .3
def s_error():
    n = int(.42 * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for k, f0 in enumerate((220, 175)):
        i = int(k * .17 * SR); m = int(.16 * SR); tt = t[:m]
        out[i:i + m] += np.tanh(3 * np.sin(2 * np.pi * f0 * tt)) * env(m, .004, .09)
    return out * .5
SYNTH = dict(error=s_error, click=s_click, pop=s_pop, bubble=s_bubble, whoosh=s_whoosh, swish=s_swish, thud=s_thud, ding=s_ding,
             type=s_type, riser=s_riser)


def peak_norm(a):
    pk = np.abs(a).max(); return a / pk if pk > 0 else a


def read_audio(path, ch=2):
    r = subprocess.run([FF, "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout: sys.exit(f"Tidak bisa membaca audio: {path}")
    a = np.frombuffer(r.stdout, np.float32).astype(np.float64)
    return a.reshape(-1, ch).copy() if ch > 1 else a.copy()


def load_file(path, long_ok=False):
    a = read_audio(path, 1)
    pk = np.abs(a).max() or 1
    nz = np.flatnonzero(np.abs(a) > pk * .03)
    if len(nz): a = a[max(0, nz[0] - int(.003 * SR)):] if long_ok else a[max(0, nz[0] - int(.003 * SR)):nz[-1] + int(.02 * SR)]
    f = min(len(a) // 4, int(.03 * SR))
    if f > 0: a[-f:] *= np.linspace(1, 0, f)
    return peak_norm(a)


def resolve(B, A):
    """-> {jenis: (sumber_label, array atau None untuk sintetis)}"""
    files = {}
    for typ, rel in (A.get("sfx_files") or {}).items():
        p = os.path.join(B, rel) if B else rel
        if typ in TYPES and os.path.exists(p): files[typ] = (p, "file user")
        else: print("PERINGATAN: sfx_files dilewati:", typ, rel)
    d = A.get("sfx_dir")
    if d and B:
        dp = os.path.join(B, d)
        if os.path.isdir(dp):
            for fn in sorted(os.listdir(dp)):
                if not fn.lower().endswith((".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")): continue
                low = fn.lower()
                for typ, keys in NAME_MAP:
                    if any(k in low for k in keys):
                        if typ not in files: files[typ] = (os.path.join(dp, fn), "folder user")
                        break
        else:
            print("PERINGATAN: folder SFX tidak ditemukan:", d)
    if A.get("sfx_source", "skill") != "synth":
        for typ, fn in BUNDLED.items():
            p = os.path.join(HERE, "sfx", fn)
            if typ not in files and os.path.exists(p): files[typ] = (p, "bawaan skill")
    bank = {}
    for typ in TYPES:
        if typ in files:
            p, lab = files[typ]
            bank[typ] = (f"{lab}: {os.path.basename(p)}", load_file(p, long_ok=(typ == "type")))
        elif typ == "tick" and "click" in bank and bank["click"][1] is not None:
            c = bank["click"][1] * .55; out = np.zeros(int(.66 * SR) + len(c))
            for k in range(10): i = int(k * .06 * SR); out[i:i + len(c)] += c * (1 - k * .04)
            bank[typ] = ("dari click (10x)", peak_norm(out))
        else:
            bank[typ] = ("sintetis", None)
    return bank


def speech_rms_db(x):
    m = x.mean(1) if x.ndim > 1 else x
    hop = int(.05 * SR); n = len(m) // hop
    if n == 0: return -60.0
    e = np.sqrt((m[:n * hop].reshape(n, hop) ** 2).mean(1)); d = 20 * np.log10(e + 1e-9)
    act = d[d > np.percentile(d, 90) - 20]
    return float(20 * np.log10(np.sqrt(np.mean(10 ** (act / 10))) + 1e-12)) if len(act) else -60.0


def speech_env(voice):
    m = np.abs(voice).mean(1); hop = int(.05 * SR); n = len(m) // hop
    e = np.sqrt((m[:n * hop].reshape(n, hop) ** 2).mean(1)); d = 20 * np.log10(e + 1e-9)
    on = (d > np.percentile(d, 90) - 20).astype(float)
    sm = np.zeros(n); a, r = 1 - np.exp(-1 / 1.2), 1 - np.exp(-1 / 7.0)
    for i in range(n):
        prev = sm[i - 1] if i else 0; sm[i] = prev + (a if on[i] > prev else r) * (on[i] - prev)
    full = np.repeat(sm, hop)
    if len(full) < len(voice): full = np.concatenate([full, np.full(len(voice) - len(full), full[-1] if len(full) else 0.)])
    return full[:len(voice)]


def main():
    args = sys.argv[1:]
    if not args: sys.exit(__doc__)
    if args[0] == "--list":
        B = os.path.abspath(args[1]) if len(args) > 1 else None
        A = json.load(open(os.path.join(B, "project.json"))).get("audio", {}) if B else {}
        for typ, (lab, _) in resolve(B, A).items(): print(f"  {typ:7s} {lab}")
        return
    B = os.path.abspath(args[0])
    proj = json.load(open(os.path.join(B, "project.json")))
    info = json.load(open(os.path.join(B, "seg", "info.json")))
    A = proj.get("audio", {})
    total = int(round(float(info["total"]) * SR))

    voice = read_audio(os.path.join(B, proj["vo"]), 2)
    voice *= db(-20 - speech_rms_db(voice))          # level bicara seragam
    f = int(.015 * SR); ramp = np.linspace(0, 1, f)[:, None]
    for at, ln in sorted(proj.get("pauses", []), reverse=True):
        i = int(float(at) * SR); a_, b_ = voice[:i].copy(), voice[i:].copy()
        if len(a_) >= f: a_[-f:] *= ramp[::-1]
        if len(b_) >= f: b_[:f] *= ramp
        voice = np.vstack([a_, np.zeros((int(float(ln) * SR), 2)), b_])
    voice = voice[:total] if len(voice) >= total else np.vstack([voice, np.zeros((total - len(voice), 2))])

    fx = np.zeros(total); used = {}
    if A.get("sfx", True):
        bank = resolve(B, A); g_all = float(A.get("sfx_gain", 1.0))
        ev = sorted(([float(t), ty, float(g)] for t, ty, g in info.get("sfx", [])), key=lambda e: e[0])
        def put(i, s):
            i = max(0, i); e = min(total, i + len(s))
            if e > i: fx[i:e] += s[:e - i]
        # mengetik: event 'type' yang rapat digabung jadi satu potongan suara ketik
        typ_ev = [e for e in ev if e[1] == "type"]; runs = []
        for t, _, g in typ_ev:
            if runs and t - runs[-1][1] <= .25: runs[-1][1] = t; runs[-1][2] = max(runs[-1][2], g)
            else: runs.append([t, t, g])
        src_type = bank["type"][1]; off = 0
        for t0, t1, g in runs:
            dur = t1 - t0 + .12
            if src_type is not None and len(src_type) > int(.5 * SR):
                n = int(dur * SR)
                if off + n > len(src_type): off = 0
                s = src_type[off:off + n].copy(); off += n
                fi, fo = min(len(s) // 3, int(.02 * SR)), min(len(s) // 3, int(.08 * SR))
                if fi: s[:fi] *= np.linspace(0, 1, fi)
                if fo: s[-fo:] *= np.linspace(1, 0, fo)
                put(int(t0 * SR), peak_norm(s) * LEVEL["type"] * g * g_all)
            else:
                for t, _, gg in [e for e in typ_ev if t0 <= e[0] <= t1]:
                    s = peak_norm(s_type()) if src_type is None else src_type
                    put(int(t * SR), s * LEVEL["type"] * gg * g_all)
            used["type"] = used.get("type", 0) + 1
        for t, ty, g in ev:
            if ty == "type": continue
            if ty not in bank: print("SFX tidak dikenal, dilewati:", ty); continue
            arr = bank[ty][1]
            s = peak_norm(SYNTH[ty]()) if arr is None else arr
            if arr is None: early = EARLY.get(ty, 0)
            elif ty in PEAK_ALIGN: early = min(.35, int(np.argmax(np.abs(arr))) / SR)
            else: early = 0
            put(int((t - early) * SR), s * LEVEL[ty] * g * g_all)
            used[ty] = used.get(ty, 0) + 1
        print("SFX:", ", ".join(f"{k} x{v} ({bank[k][0]})" for k, v in sorted(used.items())) or "tidak ada event")
    mix = voice + np.stack([fx, fx], 1)

    note = ""
    if A.get("music"):
        mp = os.path.join(B, A["music"])
        if not os.path.exists(mp): print("PERINGATAN: file musik tidak ditemukan:", A["music"])
        else:
            m = read_audio(mp, 2)
            if len(m) < total: m = np.vstack([m] * (total // max(1, len(m)) + 1))
            m = m[:total]; fi, fo = int(1.0 * SR), int(min(3.0, total / SR / 4) * SR)
            m[:fi] *= np.linspace(0, 1, fi)[:, None]; m[-fo:] *= np.linspace(1, 0, fo)[:, None]
            off = 22 if A.get("music_level", "pelan") == "pelan" else 17
            g0 = db(-20 - off - speech_rms_db(m))
            mix += m * (g0 * db(8 * (1 - speech_env(voice))))[:, None]
            note = f" | musik {A.get('music_level', 'pelan')}, mengecil saat VO bicara"

    rv = speech_rms_db(voice); rf = 20 * np.log10(np.sqrt(np.mean(fx[np.abs(fx) > 1e-4] ** 2)) + 1e-9) if np.any(np.abs(fx) > 1e-4) else -99
    print(f"level bicara VO {rv:.1f} dB | level SFX saat berbunyi {rf:.1f} dB{note}")
    if rf > rv - 4: print("PERINGATAN: SFX terlalu dekat dengan level VO. Turunkan audio.sfx_gain (mis. 0.7).")
    pk = np.abs(mix).max()
    if pk > .95: mix *= .95 / pk
    raw = os.path.join(B, "_mix_raw.f32"); mix.astype(np.float32).tofile(raw)
    lufs = float(A.get("lufs", -14))
    meas = subprocess.run([FF, "-nostdin", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw, "-af",
                           f"loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    af = (f"loudnorm=I={lufs}:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    out = os.path.join(B, "mix.wav")
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
                    "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", out], check=True)
    os.remove(raw)
    y = read_audio(out, 2)
    print(f"mix.wav {len(y)/SR:.3f} dtk (TOTAL {info['total']}) | puncak {np.abs(y).max():.3f} | target {lufs:.0f} LUFS")
    if abs(len(y) / SR - float(info["total"])) > .05: print("PERINGATAN: panjang audio tidak sama dengan TOTAL.")


if __name__ == "__main__":
    main()
