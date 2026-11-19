#!/usr/bin/env python3
"""Royalty-free background track generated in code, one mood per video.
Usage: python3 music.py DURATION_SEC out.wav [MOOD] [BPM]
Moods: ceria (upbeat, default) | hopeful (warm build) | sedih (slow, sad) | epic (big, driving)
       | chill (lofi, relaxed) | kids (bouncy, playful)
Pick the mood from the story; don't reuse the previous video's mood if another one fits.
Their own music file (mp3/wav) also works: pass it straight to mix.py instead (it loops if too short)."""
import sys, numpy as np, wave
dur = float(sys.argv[1]); outf = sys.argv[2]; mood = sys.argv[3] if len(sys.argv) > 3 else "ceria"
M = {  # chords (midi), bpm, arp pattern (chord index, +octave), drums, timbre
    "ceria":   dict(ch=[[60, 64, 67], [67, 71, 74], [69, 72, 76], [65, 69, 72]], bpm=112, arp=[0, 1, 2, 13, 2, 1, 12, 2], kick="2-4", hat=True, tone="pluck"),
    "hopeful": dict(ch=[[65, 69, 72], [60, 64, 67], [67, 71, 74], [69, 72, 76]], bpm=92, arp=[0, 2, 1, 2, 12, 2, 1, 2], kick="late", hat=False, tone="bell"),
    "sedih":   dict(ch=[[57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]], bpm=70, arp=[0, 1, 2, 1], kick=None, hat=False, tone="piano"),
    "epic":    dict(ch=[[62, 65, 69], [58, 62, 65], [65, 69, 72], [60, 64, 67]], bpm=96, arp=[0, 12, 1, 12, 2, 12, 1, 12], kick="all", hat=True, tone="saw"),
    "chill":   dict(ch=[[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]], bpm=82, arp=[0, 2, 3, 1], kick="13", hat="swing", tone="piano"),
    "kids":    dict(ch=[[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]], bpm=128, arp=[0, 1, 2, 1, 12, 2, 1, 2], kick="2-4", hat=True, tone="square")}[mood]
bpm = float(sys.argv[4]) if len(sys.argv) > 4 else M["bpm"]
sr = 44100; beat = 60/bpm; N = int(sr*(dur+3)); out = np.zeros(N); rng = np.random.default_rng(1)
note = lambda m: 440*2**((m-69)/12)
def add(sig, start):
    s = int(start*sr)
    if s >= N: return
    e = min(N, s+len(sig)); out[s:e] += sig[:e-s]
def voice(f, st, ln, amp, tone):
    t = np.arange(int(ln*sr))/sr; att = np.minimum(1, t*200)
    if tone == "pluck": w = (np.sin(2*np.pi*f*t)+.35*np.sin(4*np.pi*f*t)+.12*np.sin(6*np.pi*f*t))*np.exp(-t*5)
    elif tone == "bell": w = (np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*2.01*t)*np.exp(-t*6)+.2*np.sin(2*np.pi*f*3*t))*np.exp(-t*2.5)
    elif tone == "piano": w = (np.sin(2*np.pi*f*t)+.45*np.sin(4*np.pi*f*t)*np.exp(-t*3)+.15*np.sin(6*np.pi*f*t))*np.exp(-t*2.2)
    elif tone == "saw": w = sum(np.sin(2*np.pi*f*k*t)/k for k in range(1, 7))*.6*np.exp(-t*3)
    else: w = sum(np.sin(2*np.pi*f*k*t)/k for k in (1, 3, 5, 7))*.7*np.exp(-t*7)  # square-ish, staccato
    add(amp*w*att, st)
def pad(fs, st, ln, amp, bright=.3):
    t = np.arange(int(ln*sr))/sr
    add(amp*sum(np.sin(2*np.pi*f*t)+bright*np.sin(2*np.pi*f*1.003*t)+.15*bright*np.sin(4*np.pi*f*t) for f in fs)*np.minimum(1, t/.4)*np.minimum(1, (ln-t)/.5), st)
def kick(st, amp=.5):
    t = np.arange(int(.25*sr))/sr; f = 60+90*np.exp(-t*30); add(amp*np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t*14), st)
def hat(st, amp=.06):
    n = int(.05*sr); add(amp*rng.standard_normal(n)*np.exp(-np.arange(n)/sr*80), st)
def clap(st):
    n = int(.12*sr); add(.12*rng.standard_normal(n)*np.exp(-np.arange(n)/sr*30), st)
def tom(st, f0):
    t = np.arange(int(.3*sr))/sr; add(.3*np.sin(2*np.pi*np.cumsum(f0+40*np.exp(-t*20))/sr)*np.exp(-t*9), st)

ch = M["ch"]; bar = 4*beat; i = 0; st = 0; step = bar/len(M["arp"])
while st < dur:
    c = ch[i % 4]; lead = M["tone"]
    pad([note(n-12) for n in c], st, bar, .05 if mood not in ("sedih", "chill") else .07, .15 if mood == "chill" else .3)
    voice(note(c[0]-24), st, bar, .22 if mood != "epic" else .3, "pluck" if mood != "epic" else "saw")
    for k, a in enumerate(M["arp"]):
        n = c[a % 12 % len(c)]+(12 if a >= 12 else 0)
        voice(note(n+12), st+k*step, max(.6, step*1.5), .11 if mood != "sedih" else .14, lead)
    kk = M["kick"]
    for b in range(4):
        if kk == "all" or (kk == "2-4" and st >= bar-.01) or (kk == "late" and i >= 2) or (kk == "13" and b in (0, 2)): kick(st+b*beat, .5 if kk != "13" else .35)
        if M["hat"] is True: hat(st+b*beat+beat/2)
        elif M["hat"] == "swing": hat(st+b*beat+beat*.62, .04)
        if mood == "kids" and b in (1, 3): clap(st+b*beat)
    if mood == "epic" and i % 2 == 1:
        for k, f0 in enumerate((140, 110, 85)): tom(st+bar-beat+k*beat/3, f0)
    st += bar; i += 1
out = out[:int(sr*dur)]; f = int(1.2*sr); out[-f:] *= np.linspace(1, 0, f); out[:int(.3*sr)] *= np.linspace(0, 1, int(.3*sr))
out = out/np.abs(out).max()*.85; stv = np.stack([out, np.roll(out, int(.012*sr))*.9], 1)
with wave.open(outf, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((stv*32767).astype(np.int16).tobytes())
print("OK", outf, "mood:", mood, "bpm:", bpm)
