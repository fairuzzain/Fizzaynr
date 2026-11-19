#!/usr/bin/env python3
"""Prepare the VO: lip-sync cues (Rhubarb) + scene timing from pauses.

  python vo_prep.py vo.mp3 <n_scenes> [--out .] [--noise -32] [--min-pause 0.18]

Writes into --out:
  vo.wav       16 kHz mono copy (Rhubarb input)
  cues.json    Rhubarb mouth cues (phonetic recognizer: works for Malay)
  timing.json  {"duration": s, "scenes": [{"start","end"}...], "phrases": [{"start","end"}...]}
Scene boundaries = the n-1 longest pauses, kept in time order. The VO script must have
one paragraph per scene (blank line between them) so ElevenLabs leaves a clear pause.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vo")
    ap.add_argument("scenes", type=int)
    ap.add_argument("--out", default=".")
    ap.add_argument("--noise", default="-32")
    ap.add_argument("--min-pause", type=float, default=0.18)
    ap.add_argument("--script", help="vo.txt (one paragraph per scene): place cuts by word count, snapped to the nearest pause")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    wav = os.path.join(a.out, "vo.wav")
    r = run(["ffmpeg", "-v", "error", "-y", "-i", a.vo, "-ar", "16000", "-ac", "1", wav])
    if r.returncode:
        sys.exit(r.stderr)
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.vo]).stdout)

    # --- pauses ---
    r = run(["ffmpeg", "-i", a.vo, "-af", f"silencedetect=n={a.noise}dB:d={a.min_pause}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    gaps = [(s, e) for s, e in zip(starts, ends) if s > 0.15 and e < dur - 0.15]
    # speech phrases
    phrases, cur = [], 0.0
    for s, e in gaps:
        phrases.append({"start": round(cur, 2), "end": round(s, 2)})
        cur = e
    phrases.append({"start": round(cur, 2), "end": round(dur, 2)})
    # scene cuts = n-1 longest gaps, cut placed just before the next phrase starts
    n = max(1, a.scenes)
    if a.script:
        paras = [p for p in re.split(r"\n\s*\n", open(a.script, encoding="utf-8").read()) if p.strip()]
        words = [len(re.sub(r"\[[^\]]*\]", "", p).split()) for p in paras]
        if len(paras) != n:
            print(f"WARN script has {len(paras)} paragraphs, expected {n}", file=sys.stderr)
        tot, acc, longest, used = sum(words), 0, [], -1
        for w in words[:-1]:
            acc += w
            exp = dur * acc / tot
            best = None
            for gi, (s, e) in enumerate(gaps):
                if gi <= used:
                    continue
                score = abs((s + e) / 2 - exp) - 1.5 * (e - s)
                if best is None or score < best[0]:
                    best = (score, gi)
            if best:
                used = best[1]
                longest.append(gaps[used])
    else:
        longest = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[: n - 1])
    if len(longest) < n - 1:
        print(f"WARN only {len(longest)} pauses found for {n} scenes: lower --min-pause or --noise", file=sys.stderr)
    bounds = [0.0] + [round(e - 0.12, 2) for s, e in longest] + [round(dur, 2)]
    scenes = [{"start": bounds[i], "end": bounds[i + 1]} for i in range(len(bounds) - 1)]
    json.dump({"duration": round(dur, 2), "scenes": scenes, "phrases": phrases},
              open(os.path.join(a.out, "timing.json"), "w"), indent=1)

    # --- lip-sync ---
    rh = run([sys.executable, os.path.join(HERE, "setup_rhubarb.py")])
    if rh.returncode:
        sys.exit("Rhubarb not available: " + rh.stderr)
    rhubarb = rh.stdout.strip().splitlines()[-1]
    cues = os.path.join(a.out, "cues.json")
    r = run([rhubarb, "-q", "-r", "phonetic", "-f", "json", wav, "-o", cues])
    if r.returncode:
        sys.exit("rhubarb failed: " + r.stderr)
    nc = len(json.load(open(cues))["mouthCues"])
    print(f"OK duration {dur:.2f}s, {len(scenes)} scenes, {len(phrases)} phrases, {nc} mouth cues")
    for i, s in enumerate(scenes, 1):
        print(f"  scene {i}: {s['start']:.2f} - {s['end']:.2f}")


if __name__ == "__main__":
    main()
