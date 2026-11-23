#!/usr/bin/env python3
"""Rakit audio final: sisip jeda + sintesis SFX + mix.

  python3 audio.py sfx.json src_video.mp4 mix.wav \
      --ins 45.3 --dur 6.5 --mute 45.3:51.8 \
      --clip klip.wav --clip-at 46.0 --clip-len 4.95 --clip-gain -0.5

  sfx.json  : hasil page.evaluate(()=>({sfx:window.SFX,total:window.TOTAL}))
  --ins/--dur: sisipkan DUR detik hening di detik INS pada VO
  --mute    : rentang final yang wajib sunyi dari SFX (scene tambahan)
  --clip*   : audio klip tambahan yang ikut dinyalakan, dengan fade

SFX: 9 file bawaan di assets/sfx/ dipakai default (click, pop, bubble-pop, whoosh, swipe, punch,
notification, typing, error). Jenis tanpa file disintesis numpy (tick dibuat dari click 10x).
  --sfx-source synth     pakai SFX sintetis saja
  --sfx-dir <folder>     folder SFX milik user (dipetakan dari nama file), menang atas bawaan
Jenis: click pop bubble whoosh swish thud ding tick type error
"""
import os, sys, json, argparse, subprocess
import numpy as np, soundfile as sf

SR = 48000
rng = np.random.default_rng(7)

def env(n, a, d):
    t = np.arange(n)/SR
    return np.minimum(1, t/max(a, 1e-4)) * np.exp(-np.maximum(0, t-a)/d)
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR); X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def click():
    n = int(.06*SR); t = np.arange(n)/SR
    return np.sin(2*np.pi*3200*t)*env(n, .0005, .006)*.6 + bp(rng.standard_normal(n), 1500, 9000)*env(n, .0003, .004)*.5
def pop():
    n = int(.14*SR); t = np.arange(n)/SR; f = 500 + 1400*(t/.14)**.5
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n, .002, .035)*.7
def whoosh():
    n = int(.45*SR); t = np.arange(n)/SR
    return bp(rng.standard_normal(n), 300, 5000)*np.sin(np.pi*np.clip(t/.45, 0, 1))**2*.35
def swish():
    n = int(.25*SR); t = np.arange(n)/SR
    return bp(rng.standard_normal(n), 1200, 8000)*np.sin(np.pi*t/.25)**3*.3
def thud():
    n = int(.5*SR); t = np.arange(n)/SR; f = 110*np.exp(-t*6) + 45
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n, .002, .16) + bp(rng.standard_normal(n), 60, 900)*env(n, .001, .03)*.5
def ding():
    n = int(.9*SR); t = np.arange(n)/SR
    return sum(np.sin(2*np.pi*f*t)*a for f, a in [(1320, .5), (1980, .25), (2640, .12)])*env(n, .003, .25)*.45
def tick():
    out = np.zeros(int(.6*SR))
    for k in range(10):
        c = click()*.5; i = int(k*.06*SR); out[i:i+len(c)] += c[:len(out)-i]
    return out
def typ():
    n = int(.05*SR)
    return bp(rng.standard_normal(n), 800, 6000)*env(n, .0005, .008)*.5

def bubble():
    n = int(.18*SR); t = np.arange(n)/SR; f = 700 + 900*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n, .002, .05)*.6
def error():
    n = int(.42*SR); t = np.arange(n)/SR; out = np.zeros(n)
    for k, f0 in enumerate((220, 175)):
        i = int(k*.17*SR); m = int(.16*SR)
        out[i:i+m] += np.tanh(3*np.sin(2*np.pi*f0*t[:m]))*env(m, .004, .09)
    return out*.5

BANK = dict(click=click, pop=pop, bubble=bubble, whoosh=whoosh, swish=swish, thud=thud, ding=ding, tick=tick, type=typ, error=error)
EARLY = dict(whoosh=.15)
# ---------- SFX dari file (bawaan skill / milik user) ----------
HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED = dict(click="click.mp3", pop="pop.mp3", bubble="bubble-pop.mp3", whoosh="whoosh.mp3", swish="swipe.mp3",
               thud="punch.mp3", ding="notification.mp3", type="typing.mp3", error="error.mp3")
NAME_MAP = [("whoosh", ("whoosh", "woosh", "transition", "transisi")), ("swish", ("swish", "swipe", "swoosh")),
            ("thud", ("thud", "impact", "boom", "hit", "slam", "punch")), ("ding", ("ding", "notif", "chime", "success", "bell")),
            ("click", ("click", "klik", "tap")), ("bubble", ("bubble",)), ("pop", ("pop",)),
            ("type", ("typing", "keyboard", "ketik", "type")), ("tick", ("tick", "counter")),
            ("error", ("error", "wrong", "salah", "buzz", "fail"))]
# file dinormalkan ke puncak 1, lalu dikali level ini (setara level SFX sintetis sebelum --sfx-level)
FILE_LEVEL = dict(click=.53, pop=.53, bubble=.47, whoosh=.56, swish=.62, thud=.94, ding=.5, tick=.38, type=.44, error=.5)

def read_mono(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout: sys.exit(f"Tidak bisa membaca audio: {path}")
    return np.frombuffer(r.stdout, np.float32).astype(np.float64).copy()

def load_file(path, long_ok=False):
    a = read_mono(path); pk = np.abs(a).max() or 1
    nz = np.flatnonzero(np.abs(a) > pk*.03)
    if len(nz): a = a[max(0, nz[0]-int(.003*SR)):] if long_ok else a[max(0, nz[0]-int(.003*SR)):nz[-1]+int(.02*SR)]
    f = min(len(a)//4, int(.03*SR))
    if f > 0: a[-f:] *= np.linspace(1, 0, f)
    return a/(np.abs(a).max() or 1)

def resolve(source, sfx_dir):
    files = {}
    if sfx_dir and os.path.isdir(sfx_dir):
        for fn in sorted(os.listdir(sfx_dir)):
            if not fn.lower().endswith((".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")): continue
            for typ, keys in NAME_MAP:
                if any(k in fn.lower() for k in keys):
                    files.setdefault(typ, (os.path.join(sfx_dir, fn), "user")); break
    elif sfx_dir:
        print("PERINGATAN: folder SFX tidak ditemukan:", sfx_dir)
    if source != "synth":
        for typ, fn in BUNDLED.items():
            p = os.path.join(HERE, "sfx", fn)
            if typ not in files and os.path.exists(p): files[typ] = (p, "bawaan")
    bank = {}
    for typ, (p, lab) in files.items():
        bank[typ] = (load_file(p, long_ok=(typ == "type"))*FILE_LEVEL[typ], f"{lab}:{os.path.basename(p)}")
    if "tick" not in bank and "click" in bank:
        c = bank["click"][0]/FILE_LEVEL["click"]*.55; out = np.zeros(int(.66*SR)+len(c))
        for k in range(10): i = int(k*.06*SR); out[i:i+len(c)] += c*(1-k*.04)
        bank["tick"] = (out/np.abs(out).max()*FILE_LEVEL["tick"], "dari click 10x")
    return bank
rms = lambda x: 20*np.log10(np.sqrt(np.mean(x**2)) + 1e-9)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sfx"); ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--ins", type=float, default=0.0)
    ap.add_argument("--dur", type=float, default=0.0)
    ap.add_argument("--tail", type=float, default=0.8)
    ap.add_argument("--sfx-level", type=float, default=0.32)
    ap.add_argument("--mute", default=None, help="a:b rentang final yang sunyi dari SFX")
    ap.add_argument("--clip", default=None); ap.add_argument("--clip-at", type=float, default=0.0)
    ap.add_argument("--clip-len", type=float, default=0.0)
    ap.add_argument("--clip-gain", type=float, default=0.0, help="dB relatif")
    ap.add_argument("--clip-fade", default="0.25,0.35")
    ap.add_argument("--sfx-source", default="skill", choices=["skill", "synth"])
    ap.add_argument("--sfx-dir", default=None)
    args = ap.parse_args()

    d = json.load(open(args.sfx))
    events = d["sfx"] if isinstance(d, dict) else d
    TOTAL = d.get("total") if isinstance(d, dict) else None

    vo48 = "/tmp/_vo48.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", args.src,
                    "-ar", str(SR), "-ac", "2", vo48], check=True)
    vo, sr = sf.read(vo48); assert sr == SR
    if vo.ndim == 1: vo = np.stack([vo, vo], 1)

    if args.dur > 0:
        p = int(args.ins*SR); f = int(.015*SR)
        a = vo[:p].copy(); a[-f:] *= np.linspace(1, 0, f)[:, None]
        b = vo[p:].copy(); b[:f] *= np.linspace(0, 1, f)[:, None]
        voF = np.concatenate([a, np.zeros((int(args.dur*SR), 2)), b])
    else:
        voF = vo.copy()

    L = int(round(TOTAL*SR)) if TOTAL else len(voF) + int(args.tail*SR)
    voF = np.concatenate([voF, np.zeros((max(0, L-len(voF)), 2))])[:L]

    fx = np.zeros(L)
    files = resolve(args.sfx_source, args.sfx_dir)
    used = {}
    def put(i, s):
        i = max(0, i)
        if i < L: fx[i:i+len(s)] += s[:L-i]
    ev = sorted(events, key=lambda e: e[0])
    # mengetik: event 'type' yang rapat digabung jadi satu potongan suara ketik dari file
    if "type" in files and len(files["type"][0]) > int(.5*SR):
        src, off, runs = files["type"][0], 0, []
        for t, ty, g in ev:
            if ty != "type": continue
            if runs and t - runs[-1][1] <= .25: runs[-1][1] = t
            else: runs.append([t, t, g])
        for t0, t1, g in runs:
            n = int((t1 - t0 + .12)*SR)
            if off + n > len(src): off = 0
            seg = src[off:off+n].copy(); off += n
            fi, fo = min(n//3, int(.02*SR)), min(n//3, int(.08*SR))
            seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
            put(int(t0*SR), seg*g); used["type"] = used.get("type", 0) + 1
        ev = [e for e in ev if e[1] != "type"]
    for t, ty, g in ev:
        if ty not in BANK: print("SFX tidak dikenal:", ty); continue
        if ty in files:
            s = files[ty][0]*g
            early = min(.35, int(np.argmax(np.abs(s)))/SR) if ty == "whoosh" else 0
        else:
            s = BANK[ty]()*g; early = EARLY.get(ty, 0)
        put(int((t - early)*SR), s); used[ty] = used.get(ty, 0) + 1
    print("SFX dipakai:", ", ".join(f"{k} x{v} ({files[k][1] if k in files else 'sintetis'})" for k, v in sorted(used.items())))

    if args.mute:
        a0, b0 = (float(x) for x in args.mute.split(":"))
        fx[int(a0*SR):int(b0*SR)] *= 0

    mix = voF + fx[:, None]*args.sfx_level

    if args.clip:
        c, csr = sf.read(args.clip)
        if csr != SR:
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", args.clip,
                            "-ar", str(SR), "-ac", "2", "/tmp/_clip48.wav"], check=True)
            c, _ = sf.read("/tmp/_clip48.wav")
        if c.ndim == 1: c = np.stack([c, c], 1)
        n = int(args.clip_len*SR) if args.clip_len else len(c)
        seg = c[:n].copy(); n = len(seg)
        fi, fo = (int(float(x)*SR) for x in args.clip_fade.split(","))
        e = np.ones(n); e[:fi] = np.linspace(0, 1, fi); e[-fo:] = np.linspace(1, 0, fo)**1.5
        seg = seg*e[:, None]*(10**(args.clip_gain/20))
        i0 = int(args.clip_at*SR)
        if i0 + n <= L:
            overlap = np.abs(voF[i0:i0+n]).max()
            if overlap > 1e-3:
                print(f"PERINGATAN: klip tumpang tindih dengan VO (peak {overlap:.3f}). Geser clip-at atau perpendek.")
            mix[i0:i0+n] += seg
            print(f"klip: rms {rms(seg.mean(1)):.1f} dB, selesai di {(i0+n)/SR:.2f} dtk")

    pk = np.abs(mix).max()
    if pk > .98: mix *= .98/pk; print(f"dinormalisasi dari peak {pk:.3f}")
    sf.write(args.out, mix, SR, subtype="FLOAT")

    act = fx[np.abs(fx) > 1e-4]
    print(f"durasi {len(mix)/SR:.3f} dtk | peak {np.abs(mix).max():.3f}")
    print(f"VO rms {rms(voF[np.abs(voF).sum(1) > 1e-5]):.1f} dB | SFX rms {rms(act*args.sfx_level) if len(act) else 0:.1f} dB")
    if args.mute:
        a0, b0 = (float(x) for x in args.mute.split(":"))
        print(f"window sunyi {a0}-{b0}: peak VO {np.abs(voF[int(a0*SR):int(b0*SR)]).max():.4f}")

if __name__ == "__main__":
    main()
