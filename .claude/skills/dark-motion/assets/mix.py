#!/usr/bin/env python3
"""Rakit audio final: suara + jeda + SFX modern + musik latar (opsional) + normalisasi -14 LUFS.

    python3 mix.py <build>

Membaca semuanya dari folder build, jadi selalu sinkron dengan halaman:
  src/main.mp4        suara (sudah disambung, dibersihkan, dipotong jedanya)
  project.json        jeda (pauses), ekor (tail), pengaturan audio
  seg/info.json       TOTAL dan daftar SFX dari halaman (dibuat render_all.py)
Menulis: mix.wav

project.json -> "audio":
  "sfx": true/false            sound effect aktif
  "sfx_source": "skill"|"synth" "skill" (default) = 9 SFX bawaan di assets/sfx/; "synth" = SFX halus sintetis
  "ambience": true/false       pad sangat pelan di bagian ekor/penutup
  "music": "aset/musik.mp3"    musik dari user (opsional). Otomatis diulang, fade, dan mengecil saat ada suara
  "sfx_dir": "aset/sfx"        folder SFX milik user (opsional). File dipetakan ke jenis SFX menurut namanya:
                               click/klik/tick -> tick, pop -> air, swipe/whoosh/swoosh -> sweep,
                               typing/keyboard/ketik -> key, notif/ding/chime -> conf, boom/impact/hit -> sub,
                               glitch -> glitch, rise/riser -> rise, error/wrong -> error, bubble -> bubble.
                               Jenis tanpa file user memakai SFX bawaan skill, lalu sintetis.
Jenis SFX untuk sfx(t, jenis): sub air tick glitch key conf rise sweep (jenis lama, dipakai autocap/template)
  + pop bubble whoosh swish click error thud ding type (jenis baru / nama sama dengan skill lain, untuk scene buatan sendiri).
SFX bawaan (assets/sfx/): tick=click, air=pop, sweep=whoosh, key=typing, conf=notification, sub=punch,
  pop=pop, bubble=bubble-pop, whoosh=whoosh, swish=swipe, click=click, error=error. glitch dan rise tetap sintetis.
  "sfx_files": {"tick": "aset/sfx/klik.mp3"}   pemetaan manual (menang atas sfx_dir)
  "music_level": "pelan"|"sedang"
  "lufs": -14                  target kenyaringan (Instagram/TikTok/YouTube Shorts sekitar -14)
Tidak butuh paket selain numpy; baca-tulis audio lewat ffmpeg.
"""
import json, os, subprocess, sys
import numpy as np

SR = 48000
rng = np.random.default_rng(11)
db = lambda g: 10 ** (g / 20)
FF = os.environ.get("FFMPEG_BIN", "ffmpeg")


# ---------- bank SFX modern ----------
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


def bp(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= np.clip((f - lo * .7) / (lo * .3 + 1), 0, 1) * np.clip((hi * 1.3 - f) / (hi * .3), 0, 1)
    return np.fft.irfft(X, len(x))


def sub():
    """Hentakan rendah. Harmonik tipis wajib: tanpa itu hilang di speaker HP."""
    n = int(.55 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(58 + 95 * np.exp(-t * 24)) / SR
    return np.tanh(1.5 * (np.sin(ph) + .28 * np.sin(2 * ph) + .12 * np.sin(3 * ph))) * env(n, .003, .15) * .8


def air():
    n = int(.42 * SR); t = np.arange(n) / n
    return bp(rng.standard_normal(n), 500, 5200) * (np.sin(np.pi * t ** .72) ** 2) * .3


def tick():
    n = int(.03 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2300 * t) * env(n, .0003, .0035) * .55
            + bp(rng.standard_normal(n), 2500, 9000) * env(n, .0002, .002) * .35)


def glitch():
    n = int(.18 * SR); out = np.zeros(n); i = 0
    while i < n:
        L = int(rng.uniform(.006, .02) * SR)
        if rng.random() < .7:
            c = bp(rng.standard_normal(L), 1400, 7000) * rng.uniform(.25, .7)
            out[i:i + L] = c[:len(out[i:i + L])]
        i += L + int(rng.uniform(.002, .012) * SR)
    return out * env(n, .001, .09) * .75


def key():
    n = int(.028 * SR)
    return bp(rng.standard_normal(n), 900, 4500) * env(n, .0005, .005) * .55


def conf():
    """Dua nada sinus lembut. Bukan bel, bukan ding kartun."""
    n = int(.65 * SR); t = np.arange(n) / SR
    a = np.sin(2 * np.pi * 523 * t) * env(n, .006, .16)
    b = np.zeros(n); k = int(.085 * SR)
    b[k:] = np.sin(2 * np.pi * 784 * t[:n - k]) * env(n - k, .006, .2)
    return (a + .85 * b) * .2


def rise():
    n = int(.68 * SR); t = np.arange(n) / n
    return bp(rng.standard_normal(n), 900, 7000) * t ** 2.4 * (1 - np.clip((t - .95) / .05, 0, 1)) * .3


def sweep():
    n = int(.55 * SR); t = np.arange(n) / n
    return bp(rng.standard_normal(n), 3000, 11000) * np.sin(np.pi * t) ** 1.6 * .13


def error():
    n = int(.42 * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for k, f0 in enumerate((220, 175)):
        i = int(k * .17 * SR); m = int(.16 * SR)
        out[i:i + m] += np.tanh(3 * np.sin(2 * np.pi * f0 * t[:m])) * env(m, .004, .09)
    return out * .35


BANK = dict(sub=sub, air=air, tick=tick, glitch=glitch, key=key, conf=conf, rise=rise, sweep=sweep,
            pop=air, bubble=air, whoosh=sweep, swish=sweep, click=tick, error=error, thud=sub, ding=conf, type=key)
LEVEL = dict(sub=.55, air=.42, tick=.42, glitch=.42, key=.3, conf=.55, rise=.42, sweep=.5,
             pop=.42, bubble=.42, whoosh=.5, swish=.5, click=.42, error=.5, thud=.55, ding=.55, type=.3)
BUNDLED = dict(tick="click.mp3", air="pop.mp3", sweep="whoosh.mp3", key="typing.mp3", conf="notification.mp3",
               sub="punch.mp3", pop="pop.mp3", bubble="bubble-pop.mp3", whoosh="whoosh.mp3", swish="swipe.mp3",
               click="click.mp3", error="error.mp3", thud="punch.mp3", ding="notification.mp3", type="typing.mp3")
PEAK_ALIGN = ("sweep", "whoosh", "rise")   # file transisi: puncaknya diletakkan tepat di waktu aksi
EARLY = dict(air=.14, rise=0.0, sweep=.05)   # SFX yang dimulai sedikit lebih awal dari aksinya


def read_audio(path):
    r = subprocess.run([FF, "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"Tidak bisa membaca audio dari {path}")
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-9)


def speech_env(voice):
    """0..1, seberapa 'ada suara orang' di tiap sampel. Untuk mengecilkan musik saat ada suara."""
    m = np.abs(voice).mean(1)
    hop = int(.05 * SR); n = len(m) // hop
    e = np.sqrt((m[:n * hop].reshape(n, hop) ** 2).mean(1))
    d = 20 * np.log10(e + 1e-9)
    thr = np.percentile(d, 90) - 20
    on = (d > thr).astype(float)
    sm = np.zeros(n); a, r = 1 - np.exp(-1 / 1.2), 1 - np.exp(-1 / 7.0)   # attack ~60 ms, release ~350 ms
    for i in range(n):
        prev = sm[i - 1] if i else 0
        sm[i] = prev + (a if on[i] > prev else r) * (on[i] - prev)
    full = np.repeat(sm, hop) if n else np.zeros(0)
    if len(full) < len(voice): full = np.concatenate([full, np.full(len(voice) - len(full), full[-1] if len(full) else 0.0)])
    return full[:len(voice)], d[on > 0]


# ---------- SFX milik user ----------
NAME_MAP = [("bubble", ("bubble",)), ("tick", ("click", "klik", "tick", "tap")), ("air", ("pop",)), ("sweep", ("swipe", "whoosh", "swoosh", "swish")),
            ("key", ("typing", "keyboard", "ketik", "type")), ("conf", ("notif", "ding", "chime", "bell")),
            ("sub", ("boom", "impact", "hit", "bass", "punch")), ("glitch", ("glitch",)), ("rise", ("rise", "riser")),
            ("error", ("error", "wrong", "salah", "buzz", "fail"))]
USER_LEVEL = dict(tick=.32, air=.34, sweep=.36, key=.28, conf=.40, sub=.5, glitch=.4, rise=.4,
                  pop=.34, bubble=.3, whoosh=.36, swish=.36, click=.32, error=.34, thud=.5, ding=.4, type=.28)
USER_MAXDUR = dict(key=1.1, type=1.1)   # file mengetik biasanya panjang; cukup ~1 dtk per pemicu


def load_user_sfx(path, maxdur=None, fade=.08):
    a = read_audio(path).mean(1)
    nz = np.flatnonzero(np.abs(a) > max(1e-3, np.abs(a).max() * .03))
    if len(nz): a = a[nz[0]:]                     # buang hening di depan supaya tepat waktunya
    if maxdur: a = a[:int(maxdur * SR)]
    f = min(len(a), int((.25 if maxdur else fade) * SR))
    if f: a[-f:] *= np.linspace(1, 0, f)
    pk = np.abs(a).max() or 1
    return (a / pk).astype(np.float64)


def apply_user_sfx(B, A):
    """Ganti SFX sintetis dengan file milik user (audio.sfx_dir dan/atau audio.sfx_files)."""
    files = {}
    d = A.get("sfx_dir")
    if d:
        dp = os.path.join(B, d)
        if not os.path.isdir(dp):
            print("PERINGATAN: folder SFX tidak ditemukan:", d)
        else:
            for fn in sorted(os.listdir(dp)):
                if not fn.lower().endswith((".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")): continue
                low = fn.lower()
                for typ, keys in NAME_MAP:
                    if typ not in files and any(k in low for k in keys):
                        files[typ] = os.path.join(dp, fn); break
    for typ, rel in (A.get("sfx_files") or {}).items():
        files[typ] = os.path.join(B, rel)
    label = {t: "user" for t in files}
    if A.get("sfx_source", "skill") != "synth":
        sd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")
        for typ, fn in BUNDLED.items():
            if typ not in files and os.path.exists(os.path.join(sd, fn)):
                files[typ] = os.path.join(sd, fn); label[typ] = "bawaan"
    used = []
    for typ, path in files.items():
        if typ not in BANK or not os.path.exists(path):
            print("PERINGATAN: SFX user dilewati:", typ, path); continue
        arr = load_user_sfx(path, USER_MAXDUR.get(typ))
        BANK[typ] = (lambda a=arr: a.copy())
        LEVEL[typ] = USER_LEVEL.get(typ, .35)
        EARLY[typ] = min(.35, int(np.argmax(np.abs(arr))) / SR) if typ in PEAK_ALIGN else 0.0
        used.append(f"{typ}={os.path.basename(path)}" + (" (bawaan)" if label.get(typ) == "bawaan" else ""))
    if used:
        print("SFX dipakai:", ", ".join(used))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    B = sys.argv[1].rstrip("/")
    proj = json.load(open(os.path.join(B, "project.json")))
    info = json.load(open(os.path.join(B, "seg", "info.json")))
    A = proj.get("audio", {})
    total = int(round(info["total"] * SR))

    voice = read_audio(os.path.join(B, "src", "main.mp4"))
    # jeda dari project.json, cermin persis dari srcT() di halaman
    f = int(.01 * SR); ramp = np.linspace(0, 1, f)[:, None]
    for at, ln in sorted(proj.get("pauses", []), reverse=True):
        i = int(float(at) * SR)
        a_, b_ = voice[:i].copy(), voice[i:].copy()
        if len(a_) >= f: a_[-f:] *= ramp[::-1]
        if len(b_) >= f: b_[:f] *= ramp
        voice = np.vstack([a_, np.zeros((int(float(ln) * SR), 2), np.float32), b_])
    voice = voice[:total] if len(voice) >= total else np.vstack([voice, np.zeros((total - len(voice), 2), np.float32)])

    fx = np.zeros(total)
    if A.get("sfx", True):
        apply_user_sfx(B, A)
        for t, typ, g in info.get("sfx", []):
            if typ not in BANK:
                print("SFX tidak dikenal, dilewati:", typ); continue
            s = BANK[typ]() * LEVEL[typ] * g
            i = max(0, int((t - EARLY.get(typ, 0)) * SR)); e = min(total, i + len(s))
            if e > i: fx[i:e] += s[:e - i]
    tail = float(proj.get("tail", 0))
    if A.get("ambience"):
        dur = tail if tail > 1 else 4.0
        n = min(total, int(dur * SR)); t = np.arange(n) / SR
        pad = sum(amp * np.sin(2 * np.pi * fr * t + ph) for fr, amp, ph in
                  [(110, .5, 0), (164.8, .32, 1), (220, .26, 2), (329.6, .12, 3)])
        pad *= np.minimum(1, t / .7) * np.minimum(1, (dur - t) / 1.0) * (1 + .12 * np.sin(2 * np.pi * .35 * t))
        fx[-n:] += pad * .055

    mix = voice + np.stack([fx, np.concatenate([np.zeros(29), fx[:-29]])], 1)
    music_note = ""
    if A.get("music"):
        mp = os.path.join(B, A["music"])
        if not os.path.exists(mp):
            print("PERINGATAN: file musik tidak ditemukan:", A["music"])
        else:
            m = read_audio(mp)
            if len(m) < total:
                m = np.vstack([m] * (total // max(1, len(m)) + 1))
            m = m[:total]
            fi, fo = int(.6 * SR), int(min(2.5, total / SR / 4) * SR)
            m[:fi] *= np.linspace(0, 1, fi)[:, None]; m[-fo:] *= np.linspace(1, 0, fo)[:, None]
            envv, sp_db = speech_env(voice)
            vlev = float(np.percentile(sp_db, 70)) if len(sp_db) else rms_db(voice) + 6
            off = 20 if A.get("music_level", "pelan") == "pelan" else 15
            # musik di bawah suara sejauh `off` dB saat ada suara, naik 9 dB saat hening
            g0 = db(vlev - off - rms_db(m[m.any(1)] if m.any() else m))
            gain = g0 * db(9 * (1 - envv))[:, None]
            mix += m * gain
            music_note = f"| musik {A['music_level'] if A.get('music_level') else 'pelan'}, mengecil saat ada suara"

    print("rms suara", round(rms_db(voice.mean(1)), 1), "| rms sfx", round(rms_db(fx), 1), music_note)
    pk = np.abs(mix).max()
    if pk > .95: mix *= .95 / pk
    raw = os.path.join(B, "_mix_raw.f32")
    mix.astype(np.float32).tofile(raw)
    lufs = float(A.get("lufs", -14))
    meas = subprocess.run([FF, "-nostdin", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw, "-af",
                           f"loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    af = (f"loudnorm=I={lufs}:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    out = os.path.join(B, "mix.wav")
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
                    "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", out], check=True)
    os.remove(raw)
    y = read_audio(out)
    print("mix.wav", round(len(y) / SR, 3), "dtk (TOTAL", info["total"], ") | puncak", round(float(np.abs(y).max()), 3))
    if abs(len(y) / SR - info["total"]) > .05:
        print("PERINGATAN: panjang audio tidak sama dengan TOTAL.")
    if not A.get("sfx", True):
        sil = speech_env(y)[0] < 0.05
        secs = sil.sum() / SR
        if secs > 2:
            print(f"Catatan: tanpa SFX, ada sekitar {secs:.1f} dtk hening total. Sebutkan ke user.")


if __name__ == "__main__":
    main()
