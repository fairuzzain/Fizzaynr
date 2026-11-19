#!/usr/bin/env python3
"""
transcribe_words.py — word-level timestamps via faster-whisper.
Extracts mono audio from a video and writes words.json = [[start,end,"word"],...].

Word-level (word_timestamps=True) is MANDATORY for the caption style — phrase-level
timings drift through pauses. Always transcribe the FINISHED (composited) video, not
the script plan: the video model speaks at its own pace.

Requires: python3 -m pip install faster-whisper  (+ ffmpeg on PATH)

Usage:
    python3 transcribe_words.py final.mp4 -o words.json [--model small] [--lang en]
"""
import json, argparse, subprocess, tempfile, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("-o", "--out", default="words.json")
    ap.add_argument("--model", default="small")      # tiny/base/small/medium
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="higgsfield-transcription-") as audio_directory:
        wav = os.path.join(audio_directory, "audio.wav")
        subprocess.run(["ffmpeg", "-y", "-i", a.video, "-vn", "-ac", "1",
                        "-ar", "16000", wav, "-loglevel", "error"], check=True)

        # The sandbox template pre-bakes the "small" model here; other models download to ~/.cache.
        baked = "/opt/whisper-models"
        root = baked if os.path.isdir(f"{baked}/models--Systran--faster-whisper-{a.model}") else None
        if root:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")  # baked cache is read-only; skip HF revision checks
        from faster_whisper import WhisperModel
        model = WhisperModel(a.model, device="cpu", compute_type="int8", download_root=root)
        segs, _ = model.transcribe(wav, word_timestamps=True, language=a.lang)

        words = [[round(w.start, 2), round(w.end, 2), w.word.strip()]
                 for s in segs for w in s.words]
        with open(a.out, "w") as output_file:
            json.dump(words, output_file)
    print(f"wrote {a.out} — {len(words)} words")


if __name__ == "__main__":
    main()
