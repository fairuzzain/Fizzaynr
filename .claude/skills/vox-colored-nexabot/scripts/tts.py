"""Generate narration per chapter with Nexabot TTS and derive word-level timestamps.

Usage: python tts.py <run_dir> [--chapter N] [--align-only]

Reads   <run_dir>/script.json   {"chapters": [{"index": 1, "narration": "..."}, ...]}
Writes  <run_dir>/audio/chapter_NN.wav
        <run_dir>/audio/chapter_NN.words.json   [{"i", "word", "start", "end"}, ...]

Nexabot TTS returns audio only, so timestamps come from a local faster-whisper pass whose
words are matched back onto the script's own words (punctuation kept for segment.py).
--align-only re-runs the alignment on existing audio without a new (paid) TTS request.
"""
import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

from common import Nexabot, env, load_json, save_json

_model = None


def audio_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return float(out.stdout.strip())


def norm(w):
    return re.sub(r"[^\w]", "", w.lower())


def whisper_words(audio, narration):
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel(env("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
    # decode with ffmpeg (16 kHz mono float) instead of faster-whisper's PyAV loader
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    def run(prompt):
        segs, _ = _model.transcribe(np.frombuffer(pcm, np.float32), word_timestamps=True, language=env("TTS_LANGUAGE") or None,
                                    initial_prompt=prompt, vad_filter=False)
        return [(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or []) if w.word.strip()]
    words = run(narration[:800])
    # a full-script prompt can make whisper skip speech it thinks was "already said"; retry without it
    if len(words) < 0.5 * len(narration.split()):
        words = run(None)
    return words


def align(script_words, heard, total):
    """Map whisper timings onto the script words; unmatched words are interpolated."""
    a = [norm(w) for w in script_words]
    b = [norm(w) for w, _, _ in heard]
    times = [None] * len(script_words)
    blocks = difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks()
    for blk in blocks:
        for k in range(blk.size):
            _, s, e = heard[blk.b + k]
            times[blk.a + k] = (s, e)
    # fill gaps: spread unmatched runs evenly between the surrounding matched words
    i, n = 0, len(times)
    while i < n:
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < n and times[j] is None:
            j += 1
        t0 = times[i - 1][1] if i > 0 else 0.0
        t1 = times[j][0] if j < n else total
        step = max(t1 - t0, 0.05 * (j - i)) / (j - i)
        for k in range(i, j):
            times[k] = (t0 + (k - i) * step, t0 + (k - i + 1) * step)
        i = j
    matched = sum(blk.size for blk in blocks)
    words = [{"i": i, "word": w, "start": round(s, 3), "end": round(e, 3)}
             for i, (w, (s, e)) in enumerate(zip(script_words, times))]
    return words, matched / max(len(a), 1)


def add_pauses(wav, words, pause):
    """Insert `pause` s of silence after every sentence end (plus HEAD_PAUSE before the first word
    and TAIL_PAUSE after the last, so the opening and closing shots breathe). The untouched TTS audio is kept as
    chapter_NN.raw.wav so re-running never stacks pauses. Returns the new duration."""
    raw = wav.with_name(wav.stem + ".raw.wav")
    if not raw.exists():
        wav.replace(raw)
    cuts = [round((w["end"] + words[i + 1]["start"]) / 2, 3) for i, w in enumerate(words[:-1])
            if re.search(r"[.!?…][\"')\]]*$", w["word"])]
    edges = [0.0] + cuts + [None]
    head, tail = float(env("HEAD_PAUSE", "0.4")), float(env("TAIL_PAUSE", "1.5"))
    parts, labels = [f"aevalsrc=0:d={head}:s=24000[zh];"], ["[zh]"]
    for k in range(len(edges) - 1):
        end = f":end={edges[k + 1]}" if edges[k + 1] is not None else ""
        parts.append(f"[0:a]atrim=start={edges[k]}{end},asetpts=PTS-STARTPTS[s{k}];")
        labels.append(f"[s{k}]")
        if edges[k + 1] is not None:
            parts.append(f"aevalsrc=0:d={pause}:s=24000[z{k}];")
            labels.append(f"[z{k}]")
    parts.append(f"aevalsrc=0:d={tail}:s=24000[zt];")
    labels.append("[zt]")
    fc ="".join(parts) + "".join(f"{l}aresample=24000,aformat=channel_layouts=mono" + f"[n{i}];"
                                  for i, l in enumerate(labels))
    fc += "".join(f"[n{i}]" for i in range(len(labels))) + f"concat=n={len(labels)}:v=0:a=1[out]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-filter_complex", fc, "-map", "[out]",
                    str(wav)], check=True)
    return audio_duration(wav)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--chapter", type=int, help="only (re)generate this chapter")
    ap.add_argument("--align-only", action="store_true", help="skip TTS, re-align existing audio")
    ap.add_argument("--pause", type=float, default=float(env("SENTENCE_PAUSE", "0")),
                    help="seconds of silence added after each sentence (default SENTENCE_PAUSE, 0 = off)")
    a = ap.parse_args()
    run = Path(a.run_dir)
    chapters = load_json(run / "script.json")["chapters"]
    nb = None if a.align_only else Nexabot()
    voice = env("NEXABOT_VOICE", "Charon")

    for ch in chapters:
        n = ch["index"]
        if a.chapter and n != a.chapter:
            continue
        wav = run / "audio" / f"chapter_{n:02d}.wav"
        if not a.align_only:
            path, err = nb.run({"mode": "tts", "prompt": ch["narration"], "voice": voice}, wav, timeout=600)
            if err:
                sys.exit(f"chapter {n}: TTS {err}")
        elif not wav.exists():
            sys.exit(f"chapter {n}: {wav} missing - run without --align-only")
        raw = wav.with_name(wav.stem + ".raw.wav")
        if not a.align_only:
            raw.unlink(missing_ok=True)       # fresh TTS: the new audio is the raw take
        if a.pause > 0:
            src = raw if raw.exists() else wav
            tmp_words, _ = align(ch["narration"].split(), whisper_words(src, ch["narration"]), audio_duration(src))
            add_pauses(wav, tmp_words, a.pause)
        elif raw.exists():
            raw.replace(wav)                  # --pause 0 restores the untouched take
        dur = audio_duration(wav)
        words, ratio = align(ch["narration"].split(), whisper_words(wav, ch["narration"]), dur)
        save_json(run / "audio" / f"chapter_{n:02d}.words.json", words)
        flag = "" if 26 <= dur <= 36 else "   <-- outside 26-36s target, adjust narration length"
        warn = "" if ratio >= 0.85 else f"   <-- only {ratio:.0%} of words matched, listen and check"
        print(f"chapter {n}: {dur:.2f}s, {len(words)} words, {ratio:.0%} aligned{flag}{warn}")


if __name__ == "__main__":
    main()
