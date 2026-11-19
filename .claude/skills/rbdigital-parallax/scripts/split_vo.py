#!/usr/bin/env python3
"""Split one voice-over recording into script lines by pauses.
Usage: python3 split_vo.py input.(m4a|mp3|wav) script.txt [outprefix]
script.txt = one spoken line per scene (blank lines ignored). Word counts give the expected
split points; the nearest real pause (>=0.2 s) to each expected point is used.
Writes <prefix>1.wav.. and prints JSON [{file, src_start, dur, text}] -> save as vo.json for plan_scenes.py.
Input seek (-ss before -i) so the fades apply to each clip, not to the whole file."""
import sys, subprocess, json, wave, numpy as np
src, scr = sys.argv[1], sys.argv[2]; pre = sys.argv[3] if len(sys.argv) > 3 else "line"
lines = [l.strip() for l in open(scr, encoding="utf-8") if l.strip()]; n = len(lines)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "16000", "_mono.wav"], check=True)
w = wave.open("_mono.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
hop = 800; T = hop/16000
db = np.array([20*np.log10(np.sqrt((a[i:i+hop]**2).mean())+1e-9) for i in range(0, len(a)-hop, hop)])
sp = db > max(db.max()-22, -36)
# remove tiny speech blips (<0.15 s) inside pauses
i = 0
while i < len(sp):
    if sp[i]:
        j = i
        while j < len(sp) and sp[j]: j += 1
        if j-i < 3 and i > 0 and j < len(sp): sp[i:j] = False
        i = j
    else: i += 1
idx = np.where(sp)[0]; st, en = idx[0], idx[-1]+1
gaps = []; g = None
for k in range(st, en):
    if not sp[k] and g is None: g = k
    if sp[k] and g is not None:
        if (k-g)*T >= 0.2: gaps.append((g, k))
        g = None
wc = np.array([len(l.split()) for l in lines], float); cum = np.cumsum(wc)[:-1]/wc.sum()
speech_len = en-st; chosen = []
for c in cum:
    target = st + c*speech_len
    cand = [x for x in gaps if x not in chosen]
    best = min(cand, key=lambda x: abs((x[0]+x[1])/2-target) - 0.5*(x[1]-x[0]))  # prefer near + longer
    chosen.append(best)
chosen.sort(); b = [st] + [v for gg in chosen for v in gg] + [en]; res = []
for k in range(n):
    s0, e0 = max(0, b[2*k]*T-0.08), b[2*k+1]*T+0.1; o = f"{pre}{k+1}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{s0:.2f}", "-to", f"{e0:.2f}", "-i", src, "-ac", "1", "-ar", "44100",
                    "-af", "afftdn=nf=-30,highpass=f=80,afade=t=in:d=0.04,areverse,afade=t=in:d=0.08,areverse", o], check=True)
    res.append({"file": o, "src_start": round(s0, 2), "dur": round(e0-s0, 2), "text": lines[k]})
for r in res:  # loudness check: every clip must actually contain voice
    m = subprocess.run(["ffmpeg", "-i", r["file"], "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    r["mean_db"] = float(m.split("mean_volume:")[1].split("dB")[0]) if "mean_volume:" in m else -99
    if r["mean_db"] < -30 or r["dur"] < 1.2: print(f"CHECK {r['file']}: mean {r['mean_db']} dB, {r['dur']} s - fix cut points by hand", file=sys.stderr)
print(json.dumps(res, indent=1, ensure_ascii=False))
