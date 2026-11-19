#!/usr/bin/env python3
"""VO-first timing: build scenes.json from a draft + the VO lines, so scenes fit the voice exactly.
Usage: python3 split_vo.py vo.mp3 script.txt line > vo.json
       python3 plan_scenes.py draft.json vo.json        -> scenes.json + vo_args.txt (file:start for mix.py)
       python3 plan_scenes.py draft.json none           -> no VO: scenes split evenly over "target"
draft.json = scenes.json without timing: {"target":30, "size":[720,1280], "style":"paper", "caption_look":{...},
  "scenes":[{"bg":..,"fg":..,"chars":[..],"caption":..,"cam":..}], "tagline":{"lines":[..],"cta_word":2,"y":0.76}}
cta_word = index (0-based) of the first CTA word in the LAST VO line; the tagline appears when it is spoken.
Rule: VO line k starts 0.4 s into scene k, scene ends >= 0.5 s after its line, scenes overlap 0.6 s (transition)."""
import sys, json
D = json.load(open(sys.argv[1])); S = D["scenes"]; n = len(S); target = D.get("target", 30); OV = .6
vo = None if sys.argv[2] == "none" else json.load(open(sys.argv[2]))
if vo is not None and len(vo) != n: sys.exit(f"VO has {len(vo)} lines but draft has {n} scenes - fix script.txt or the draft")

def plan(lead, tail, mn):
    st, out, places = 0., [], []
    for k in range(n):
        vs = st+lead; en = max(st+mn, vs+vo[k]["dur"]+tail); out.append((st, en)); places.append((vo[k]["file"], vs)); st = en-OV
    return out, places

if vo is None:
    L = (target+OV*(n-1))/n; times = [(k*(L-OV), k*(L-OV)+L) for k in range(n)]; places = []
else:
    times, places = plan(.4, .5, 3.0)
    if times[-1][1] > target*1.04:
        times, places = plan(.25, .3, 2.6); print("note: VO long, gaps tightened")
    if times[-1][1] > target*1.04:
        need = sum(v["dur"] for v in vo)/(sum(v["dur"] for v in vo)-(times[-1][1]-target))
        print(f"WARNING: VO runs {times[-1][1]:.1f}s vs target {target}s. Options: atempo={min(need, 1.12):.2f} on the VO "
              f"(only if <= 1.12), or keep {times[-1][1]:.1f}s and tell the user.")
for k, sc in enumerate(S):
    sc["start"], sc["end"] = round(times[k][0], 2), round(times[k][1], 2)
D["duration"] = round(times[-1][1], 2)
tg = D.get("tagline")
if tg and "start" not in tg:
    if vo:
        w = vo[-1]["text"].split(); i = min(tg.pop("cta_word", 0), len(w)-1)
        tg["start"] = round(places[-1][1]+vo[-1]["dur"]*i/max(1, len(w)), 2)
    else: tg["start"] = round(S[-1]["start"]+1.0, 2)
D.pop("target", None); json.dump(D, open("scenes.json", "w"), indent=1, ensure_ascii=False)
open("vo_args.txt", "w").write(" ".join(f"{f}:{s:.2f}" for f, s in places))
for k, sc in enumerate(S): print(f"scene {k+1}: {sc['start']:5.2f} - {sc['end']:5.2f}" + (f"  VO @ {places[k][1]:.2f}" if places else ""))
print("duration", D["duration"], "-> scenes.json, vo_args.txt")
