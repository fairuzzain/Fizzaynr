#!/usr/bin/env python3
"""
group_captions.py — turn word-level timestamps into dynamic 1-2 word caption
segments that BLANK OUT during pauses. Feeds scripts/make_captions.py.

Input  words.json    : [[start, end, "word"], ...]  (faster-whisper word_timestamps)
Output segments.json : {"video": ..., "style": {"margin_v": ...}, "segments":[{start,end,text}]}

Correctness: pass --script with the AUTHORED monologue text. The caption TEXT is then
taken from the script (correct brand / product spelling), timed by whisper — whisper is
only the clock. This removes transcription typos generically, with no per-brand hardcoding.

Usage:
    python3 group_captions.py words.json -o segments.json --video final.mp4 --script script.txt
"""
import json, argparse, re, difflib, sys

# --- defaults (tune here) ---
MAX_PAIR_CHARS = 11    # pair two words only if together <= this many chars
MAX_JOIN_GAP   = 0.35  # ...and the gap between them is < this (seconds)
TAIL           = 0.15  # caption lingers this long after its last word (this IS the pause-blanking)
MIN_HOLD       = 0.20  # minimum on-screen time
MARGIN_V       = 1380  # written into style.margin_v; the pipeline post-processes the .ass anyway

SENT_END_PUNCT = (".", "!", "?", ":", ";")  # never pair across a sentence boundary
# Optional manual transcription overrides, applied case-insensitively per word. Default EMPTY —
# correctness comes from --script alignment, NOT from a per-brand hardcode. Only add an entry for a
# rare case the alignment cannot resolve, and clear it for other sites.
FIX = {}


def _norm(t):
    """Normalise a token for matching: lowercase, strip non-alphanumerics."""
    return re.sub(r"[^a-z0-9]", "", t.lower())


def load_words(path):
    raw = json.load(open(path))
    words = [(float(s), float(e), FIX.get(w.strip().lower(), w.strip())) for s, e, w in raw]
    # glue split tokens like "adidas" + ".com", "two" + "-day"
    merged = []
    for s, e, w in words:
        if merged and w.startswith((".", "-", "'")):
            ps, pe, pw = merged[-1]; merged[-1] = (ps, e, pw + w); continue
        merged.append((s, e, w))
    return merged


SPAN_SIMILARITY = 0.6   # normalized-text ratio above which a span is "the same words, mis-heard"


def _span_ratio(a_tokens, b_tokens):
    """Similarity of two token spans as flat normalized strings."""
    return difflib.SequenceMatcher(a="".join(a_tokens), b="".join(b_tokens), autojunk=False).ratio()


def align_to_script(words, script_text):
    """Replace whisper word TEXT with the authored script's exact words (keeping whisper
    timings), by aligning the two token sequences. Whisper only supplies the clock, so
    brand / product names are always spelled as authored.

    Mis-hears are routinely N<->M, not 1:1 — the transcript collapses a multi-word name
    into one token, splits one across two, or drops a word. Equal-length spans map straight
    across; unequal spans are distributed across the whisper words of the span (so every
    authored word survives, in order, on real timings) whenever the two spans read as the
    same words. On a genuinely different span the whisper text stays and the QA check
    flags it — the alignment never invents text, and it never prefers ASR spelling for a
    word the author actually wrote."""
    script_tokens = script_text.split()
    a = [_norm(w) for _, _, w in words]
    b = [_norm(t) for t in script_tokens]
    out = [[s, e, w] for s, e, w in words]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        n, m = i2 - i1, j2 - j1
        if tag == "equal" or (tag == "replace" and n == m):
            for k in range(n):
                if _norm(script_tokens[j1 + k]):        # don't overwrite with a punctuation-only token
                    out[i1 + k][2] = script_tokens[j1 + k]
        elif tag == "replace" and n > 0 and m > 0:
            # Unequal span: only substitute when it is clearly the same words mis-heard,
            # never when the transcript heard something else.
            if _span_ratio(a[i1:i2], b[j1:j2]) < SPAN_SIMILARITY:
                continue
            # Spread the m authored tokens over the n whisper words, in order; the last
            # whisper word absorbs the remainder so nothing authored is lost.
            base, extra = divmod(m, n)
            cursor = j1
            for k in range(n):
                width = base + (1 if k < extra else 0)
                take = script_tokens[cursor:j2] if k == n - 1 else script_tokens[cursor:cursor + width]
                cursor += len(take)
                text = " ".join(t for t in take if _norm(t))
                if text:
                    out[i1 + k][2] = text
        # delete / insert: keep the whisper words as-is
    return [(s, e, w) for s, e, w in out]


def group(words):
    segs, i = [], 0
    while i < len(words):
        s, e, w = words[i]
        pair = (i + 1 < len(words)
                and len(w) + len(words[i + 1][2]) <= MAX_PAIR_CHARS
                and (words[i + 1][0] - e) < MAX_JOIN_GAP
                and not w.rstrip().endswith(SENT_END_PUNCT))  # generic sentence-boundary test
        if pair:
            ns, ne, nw = words[i + 1]
            segs.append({"start": round(s, 2), "end": round(ne, 2), "text": f"{w} {nw}"}); i += 2
        else:
            segs.append({"start": round(s, 2), "end": round(e, 2), "text": w}); i += 1
    # blank during pauses: end = word_end + small tail, never bridge to the next caption
    for j, seg in enumerate(segs):
        nxt = segs[j + 1]["start"] if j + 1 < len(segs) else seg["end"] + TAIL
        seg["end"] = round(min(seg["end"] + TAIL, nxt - 0.02), 2)
        if seg["end"] < seg["start"] + MIN_HOLD:
            seg["end"] = round(seg["start"] + MIN_HOLD, 2)
    # never let two captions overlap in time — ASS stacks overlapping events, which makes the
    # text jump vertically. Trim each segment's end to before the next one's start.
    GAP = 0.02
    for i in range(len(segs) - 1):
        if segs[i]["end"] > segs[i + 1]["start"] - GAP:
            segs[i]["end"] = round(
                max(segs[i]["start"] + 0.05, segs[i + 1]["start"] - GAP), 2
            )
    return segs


def qa_check(segs, script_text):
    """Flag caption words that are not in the authored script (mis-hears the alignment
    could not fix). Returns the offending words so the caller can BLOCK the burn."""
    vocab = {_norm(t) for t in script_text.split() if _norm(t)}
    unknown = sorted({w for seg in segs for w in seg["text"].split()
                      if _norm(w) and _norm(w) not in vocab})
    if unknown:
        print(f"[QA] {len(unknown)} caption word(s) not in the script: {unknown}")
    else:
        print("[QA] ok — every caption word is in the script")
    return unknown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words_json")
    ap.add_argument("-o", "--out", default="segments.json")
    ap.add_argument("--video", default="final.mp4")
    ap.add_argument("--script", default=None, help="authored monologue text — captions take spelling from it")
    ap.add_argument("--margin-v", type=int, default=MARGIN_V)
    ap.add_argument("--allow-qa-misses", action="store_true",
                    help="write segments even when caption words are missing from the script "
                         "(default: exit 3 so a chained burn never ships mis-heard text)")
    a = ap.parse_args()

    words = load_words(a.words_json)
    script_text = None
    if a.script:
        script_text = open(a.script, encoding="utf-8").read()
        words = align_to_script(words, script_text)

    segs = group(words)
    unknown = []
    if script_text is not None:
        unknown = qa_check(segs, script_text)
    else:
        print("[QA] no --script given — captions use raw transcription (brand/product typos possible)")

    json.dump({"video": a.video, "style": {"margin_v": a.margin_v}, "segments": segs},
              open(a.out, "w"))
    print(f"wrote {a.out} — {len(segs)} segments")

    # A non-empty QA list means the burn would put ASR spelling on screen. Fail loudly
    # instead: fix the script's display forms, or re-run with --allow-qa-misses if the
    # flagged words really are correct.
    if unknown and not a.allow_qa_misses:
        print("[QA] BLOCKED — not safe to burn. Author every brand and number in the script "
              "exactly as it must read on screen, then re-run; pass --allow-qa-misses to override.")
        sys.exit(3)


if __name__ == "__main__":
    main()
