#!/usr/bin/env python3
"""Procedural SFX (no downloads, no licences). Used by mix.py through events.json from render.py.
Kinds: whoosh (slide/crossfade), paper (torn/page transitions), pop (caption pop/drop/slide), chime (tagline).
Usage alone: python3 sfx.py events.json DURATION out.wav"""
import sys, json, wave, numpy as np
SR = 44100
def _noise(n, seed): return np.random.default_rng(seed).standard_normal(n)
def lowpass(x, a):  # one-pole, a in (0,1): smaller = darker
    y = np.empty_like(x); acc = 0.
    for i, v in enumerate(x): acc += a*(v-acc); y[i] = acc
    return y
def whoosh(seed=0):
    n = int(.55*SR); t = np.arange(n)/SR; x = _noise(n, seed)
    env = np.sin(np.pi*np.clip(t/.55, 0, 1))**2
    a = .02+.25*env  # sweep the filter open in the middle
    y = np.empty(n); acc = 0.
    for i in range(n): acc += a[i]*(x[i]-acc); y[i] = acc
    return .9*y*env/np.abs(y).max()
def paper(seed=0):
    n = int(.6*SR); t = np.arange(n)/SR; r = np.random.default_rng(seed); x = _noise(n, seed+1)
    x = x-lowpass(x, .25)  # crisp highs
    crk = np.zeros(n)
    for _ in range(26):  # crinkles
        p = r.integers(0, n-800); L = r.integers(150, 800); crk[p:p+L] += r.uniform(.3, 1)*np.exp(-np.arange(L)/(L/4))
    env = np.clip(t/.06, 0, 1)*np.clip((.6-t)/.25, 0, 1)
    return .7*x*(.25+crk)*env/np.abs(x*(.25+crk)*env).max()
def pop(seed=0):
    n = int(.12*SR); t = np.arange(n)/SR; f = 900*np.exp(-t*25)+300
    return .6*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*40)
def chime(seed=0):
    n = int(1.4*SR); t = np.arange(n)/SR; y = np.zeros(n)
    for k, (f, d) in enumerate(((1318.5, 0), (1568, .09), (2093, .18))):
        s = int(d*SR); tt = t[:n-s]; y[s:] += np.sin(2*np.pi*f*tt)*np.exp(-tt*3.5)*(.6-.12*k)
    return .5*y
GEN = {"whoosh": whoosh, "paper": paper, "pop": pop, "chime": chime}
VOL = {"whoosh": .55, "paper": .5, "pop": .35, "chime": .4}

def build(events, dur):
    out = np.zeros(int(SR*(dur+2)))
    for k, e in enumerate(events):
        s = GEN[e["kind"]](k)*VOL[e["kind"]]*e.get("vol", 1); st = int(max(0, e["t"]-(.2 if e["kind"] in ("whoosh", "paper") else 0))*SR)
        out[st:st+len(s)] += s[:len(out)-st]
    return out[:int(SR*dur)]
def save(x, f):
    x = np.clip(x, -1, 1); st = np.stack([x, x], 1)
    with wave.open(f, "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
if __name__ == "__main__":
    save(build(json.load(open(sys.argv[1])), float(sys.argv[2])), sys.argv[3]); print("OK", sys.argv[3])
