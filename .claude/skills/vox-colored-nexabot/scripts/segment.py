"""Split each chapter's narration into clips and compute exact on-screen timing.

Usage:
  python segment.py <run_dir> --auto       propose boundaries -> writes segments.json, then plans
  python segment.py <run_dir>              use existing <run_dir>/segments.json

segments.json:  {"1": [0, 14, 27, 41, 55], "2": [...]}
  For each chapter, the index of the FIRST word of every clip (must start with 0).

Writes <run_dir>/plan.json with per-clip timing. Prompt fields already filled in an
existing plan.json are kept for any clip whose word span is unchanged.

Timing model
  - Clip k is on screen from cut[k] to cut[k+1]; cuts sit midway in the gap before the
    clip's first word; the first clip starts at 0, the last ends at the end of the audio.
  - Every generated video loses its first TRIM_START seconds, so a clip's local time
    (what the video prompt must use) = narration time - clip start + TRIM_START.
  - gen_duration is 4 if the clip fits in 4 - TRIM_START seconds, else 6. Clips longer
    than 6 - TRIM_START are rejected: split them.
"""
import argparse
import re
import sys
from pathlib import Path

from common import GEN_DURATIONS, TRIM_START, env, load_json, save_json
from tts import audio_duration

MAX_SHOW = max(GEN_DURATIONS) - TRIM_START   # 5.75
SHORT_SHOW = min(GEN_DURATIONS) - TRIM_START  # 3.75
MIN_SHOW = 1.5
SENTENCE_END = re.compile(r"[.!?…][\"')\]]*$")
CLAUSE_END = re.compile(r"[,;:—–-][\"')\]]*$")


def cut_before(words, i):
    if i == 0:
        return 0.0
    return round((words[i - 1]["end"] + words[i]["start"]) / 2, 3)


def auto_boundaries(words, total, target=4.5):
    """Optimal split (DP): every clip 1.8s..MAX_SHOW, cuts preferably after sentence ends,
    then clause ends; clip lengths close to `target`; 8 clips max per chapter."""
    n = len(words)
    times = [cut_before(words, j) for j in range(n)] + [total]   # index n == end of audio

    def boundary_cost(j):
        if j == n:
            return 0.0
        w = words[j - 1]["word"]
        return 0.0 if SENTENCE_END.search(w) else 1.0 if CLAUSE_END.search(w) else 4.0

    INF = float("inf")
    # best[k][j] = min cost to cover words[0:j] with k clips
    best = [[INF] * (n + 1) for _ in range(9)]
    back = [[None] * (n + 1) for _ in range(9)]
    best[0][0] = 0.0
    for k in range(1, 9):
        for j in range(1, n + 1):
            for i in range(j):
                if best[k - 1][i] == INF:
                    continue
                length = times[j] - times[i]
                if length > MAX_SHOW:
                    continue
                if length < 1.8:
                    break
                c = best[k - 1][i] + boundary_cost(j) + 0.3 * (length - target) ** 2
                if c < best[k][j]:
                    best[k][j], back[k][j] = c, i
    ks = [k for k in range(4, 9) if best[k][n] < INF] or [k for k in range(1, 9) if best[k][n] < INF]
    if not ks:
        sys.exit("auto split impossible (a single pause is longer than a clip) - write segments.json by hand")
    k = min(ks, key=lambda k: best[k][n])
    firsts, j = [], n
    while k > 0:
        i = back[k][j]
        firsts.append(i)
        j, k = i, k - 1
    return sorted(firsts)


def build_chapter(run, ch_index, words, firsts, old_clips):
    wav = run / "audio" / f"chapter_{ch_index:02d}.wav"
    total = round(audio_duration(wav), 3)
    if not firsts or firsts[0] != 0 or sorted(set(firsts)) != firsts or firsts[-1] >= len(words):
        sys.exit(f"chapter {ch_index}: boundaries must be increasing word indices starting at 0, "
                 f"each < {len(words)}")
    clips, problems = [], []
    for k, fw in enumerate(firsts):
        lw = (firsts[k + 1] - 1) if k + 1 < len(firsts) else len(words) - 1
        start = cut_before(words, fw)
        end = cut_before(words, firsts[k + 1]) if k + 1 < len(firsts) else total
        show = round(end - start, 3)
        cid = f"ch{ch_index}_c{k + 1:02d}"
        if show > MAX_SHOW:
            problems.append(f"{cid} is {show:.2f}s on screen (> {MAX_SHOW}s) - split it")
        if show < MIN_SHOW:
            problems.append(f"{cid} is only {show:.2f}s on screen (< {MIN_SHOW}s) - merge it")
        clip = {
            "id": cid,
            "first_word": fw,
            "last_word": lw,
            "start": start,
            "end": end,
            "display_duration": show,
            "gen_duration": 4 if show <= SHORT_SHOW else 6,
            "narration": " ".join(w["word"] for w in words[fw:lw + 1]),
            "word_times": [{"word": w["word"], "t": round(w["start"] - start + TRIM_START, 2)}
                           for w in words[fw:lw + 1]],
            "public_figures": [],
            "image_prompt": "",
            "video_prompt": "",
        }
        old = old_clips.get(cid)
        if old and old.get("first_word") == fw and old.get("last_word") == lw:
            for key in ("public_figures", "image_prompt", "video_prompt"):
                clip[key] = old.get(key, clip[key])
        clips.append(clip)
    if not 4 <= len(clips) <= 8:
        problems.append(f"chapter {ch_index} has {len(clips)} clips (target 4-8)")
    return {"index": ch_index, "audio": f"audio/{wav.name}", "duration": total, "clips": clips}, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--auto", action="store_true")
    a = ap.parse_args()
    run = Path(a.run_dir)
    script = load_json(run / "script.json")
    seg_path = run / "segments.json"
    plan_path = run / "plan.json"

    old_clips = {}
    if plan_path.exists():
        for ch in load_json(plan_path).get("chapters", []):
            for c in ch["clips"]:
                old_clips[c["id"]] = c

    segments = {} if a.auto else load_json(seg_path)
    chapters, problems = [], []
    for ch in script["chapters"]:
        n = ch["index"]
        words = load_json(run / "audio" / f"chapter_{n:02d}.words.json")
        if a.auto:
            total = audio_duration(run / "audio" / f"chapter_{n:02d}.wav")
            segments[str(n)] = auto_boundaries(words, total)
        chap, probs = build_chapter(run, n, words, segments[str(n)], old_clips)
        chapters.append(chap)
        problems += probs
    if a.auto:
        save_json(seg_path, segments)

    plan = {"title": script.get("title", ""), "aspect_ratio": env("ASPECT_RATIO", "16:9"),
            "chapters": chapters}
    save_json(plan_path, plan)

    for chap in chapters:
        print(f"\n=== Chapter {chap['index']}  ({chap['duration']:.2f}s, {len(chap['clips'])} clips)")
        for c in chap["clips"]:
            timed = " ".join(f"[{w['t']:.2f}]{w['word']}" for w in c["word_times"])
            print(f"{c['id']}  {c['start']:6.2f}-{c['end']:6.2f}  show {c['display_duration']:.2f}s"
                  f"  gen {c['gen_duration']}s\n    {timed}")
    if problems:
        print("\nPROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print(f"\nOK -> {plan_path}")


if __name__ == "__main__":
    main()
