#!/usr/bin/env python3
"""Checks a song take's words and times every sung line of script.json from them (references/formats.md, Sung story). Standard
library only.

  python3 song_times.py words.json script.json --lines 1-6 --dry-run   (one take of a part: its lines, every word checked)
  python3 song_times.py words.json script.json                          (the joined song: every sung line timed into script.json)

words.json is the take's words as faster-whisper heard them, [{"start", "end", "word"}, …], made in the sandbox with the lyrics it
should hold (the part's lines, or all of them for the joined song) in lyrics.txt:

  python3 -c "import json; from faster_whisper import WhisperModel as W; segs, _ = W('small', device='cpu', compute_type='int8')
  .transcribe('take.mp3', word_timestamps=True, initial_prompt=open('lyrics.txt').read()); json.dump([{'start': w.start,
  'end': w.end, 'word': w.word} for s in segs for w in s.words], open('words.json', 'w'))"

(transcribe returns the segments and an info object, and the segments are a generator: read them once, as above.) Whisper cuts the
song into its own segments, never into the lyric's lines, and glues junk to a word at a segment's edge ("billwaukeeYou"): the
heard words are split at that junk and matched to the lyric's words in order. Each line takes its start from its first heard word
and its end from its last. Every lyric word not heard is listed with its second: cut that line from the take and transcribe it
again alone, without the lyrics (`ffmpeg -ss <a> -to <b> -i take.mp3 line.wav`): a quiet first word missed in the whole take is
often there. A word still missing, or changed, means the take lost it: make that part again.

Whisper also reads the song in 30-second windows, and at a window's edge it can stamp a run of words with no length, or write the
prompt's lines there again: a line timed from them is sung far longer than its timed length. A line timed shorter than 40% of its
words at the take's own pace (the median seconds a word over its lines) is listed as not timed, and gets no times (9 of 13 such
lines in 24 passes, none of 187 clean ones): time it again in a window cut in the gaps around it (references/formats.md).
A line whose first word whisper timed with no length (start = end, stamped at a window's edge) is listed as not timed too: its
line starts later, by up to 3 s in 3 of 3 such lines.
"""
import difflib
import json
import re
import statistics
import sys


def tokens(text):
    return [t.strip("'") for t in re.sub(r"[^a-z0-9' ]", " ", text.lower().replace("’", "'")).split() if t.strip("'")]


def heard_tokens(word, vocabulary):
    """A heard word as lyric words: split where whisper glued junk to it (a capital inside it, "billwaukeeYou" and ".BRUNThree"; a
    non-Latin character), and a piece that begins with a lyric word of three letters or more counts as that word ("stillaves" is
    "still")."""
    out = []
    for piece in re.split(r"(?<=[a-z'])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|[^\x00-\x7F]+", word.strip()):
        for t in tokens(piece):
            if t not in vocabulary:
                t = max((v for v in vocabulary if len(v) >= 3 and t.startswith(v)), key=len, default=t)
            out.append(t)
    return out


def align(lines, heard):
    """lines: the lyric lines in order; heard: [{"start", "end", "word"}, …]. Returns, per line, (start, end, the words not heard
    with the second near which each was due, the length of the heard word its start came from); start and end are None for a line
    none of whose words were heard."""
    lyric, owner = [], []
    for i, line in enumerate(lines):
        for t in tokens(line):
            lyric.append(t)
            owner.append(i)
    vocabulary = set(lyric)
    said, at = [], []
    for w in heard:
        pieces = heard_tokens(w["word"], vocabulary)
        step = (w["end"] - w["start"]) / max(len(pieces), 1)  # a glued word's time is shared out among its pieces
        for p, t in enumerate(pieces):
            said.append(t)
            at.append({"start": w["start"] + p * step, "end": w["start"] + (p + 1) * step, "word_len": w["end"] - w["start"]})
    match = {}
    for block in difflib.SequenceMatcher(None, lyric, said, autojunk=False).get_matching_blocks():
        for k in range(block.size):
            match[block.a + k] = block.b + k
    out = []
    for i in range(len(lines)):
        idx = [j for j, o in enumerate(owner) if o == i]
        hits = [match[j] for j in idx if j in match]
        missing = []
        for j in idx:
            if j in match:
                continue
            before = [match[x] for x in range(j, -1, -1) if x in match]
            near = at[before[0]]["end"] if before else (at[0]["start"] if at else 0)
            missing.append((lyric[j], round(near, 1)))
        if not hits:
            out.append((None, None, missing, None))
            continue
        out.append((round(at[min(hits)]["start"], 2), round(at[max(hits)]["end"], 2), missing, at[min(hits)]["word_len"]))
    return out


def not_timed(lines, times):
    """Per line, why align()'s times for it cannot be used, or None: timed shorter than 40% of its words at the take's pace, or
    started from a heard word timed with no length."""
    pace = [(e - s) / len(tokens(l)) for l, (s, e, *_) in zip(lines, times) if s is not None and tokens(l)]
    if not pace:
        return [None] * len(lines)
    pace = statistics.median(pace)
    out = []
    for line, (start, end, _, first_len) in zip(lines, times):
        due = len(tokens(line)) * pace
        short = start is not None and end - start < 0.4 * due
        if start is not None and first_len < 0.02:
            out.append("its first word was timed with no length")
            continue
        out.append(f"timed {end - start:.1f}s, its words take {due:.1f}s at this take's pace" if short else None)
    return out


def main(argv):
    args = [a for i, a in enumerate(argv[1:], 1) if not a.startswith("--") and argv[i - 1] != "--lines"]
    if len(args) != 2:
        print(__doc__)
        return 2
    with open(args[0]) as f:
        heard = json.load(f)
    with open(args[1]) as f:
        script = json.load(f)
    sung = [l for l in script.get("lines", []) if l.get("kind") == "sung"]
    if "--lines" in argv:
        a, _, b = argv[argv.index("--lines") + 1].partition("-")
        sung = sung[int(a) - 1:int(b or a)]
    if not sung:
        print("script.json has no sung lines here")
        return 1
    times, problems, previous_end = align([l["text"] for l in sung], heard), [], 0
    untimed = not_timed([l["text"] for l in sung], times)
    for line, (start, end, missing, _), why in zip(sung, times, untimed):
        if missing:
            words = ", ".join(f'"{w}" near {s}s' for w, s in missing)
            problems.append(f'not heard: {words} in "{line["text"][:60]}"')
        if why:
            problems.append(f'not timed ({why}; whisper\'s 30-second window): "{line["text"][:60]}"')
        if start is None or why:
            print(f'   ?       ?      {line["text"]}')
            continue
        if start < previous_end:
            problems.append(f'starts at {start}s, before the line before it ends ({previous_end}s): "{line["text"][:50]}"')
        previous_end = end
        line["startSeconds"], line["endSeconds"] = start, end
        print(f"{start:7.2f} {end:7.2f}  {line['text']}")
    if "--dry-run" not in argv:
        with open(args[1], "w") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        timed = sum(t[0] is not None and not why for t, why in zip(times, untimed))
        print(f"wrote startSeconds and endSeconds of {timed} sung lines into {args[1]}")
    for p in problems:
        print(f"- {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
