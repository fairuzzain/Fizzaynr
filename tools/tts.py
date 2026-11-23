#!/usr/bin/env python3
"""VO / TTS untuk semua skill: Gemini TTS dahulu, Nexabot /api/v1/voice sebagai sandaran.

  python tools/tts.py --text-file skrip.txt --out runs/<skill>/<slug>/vo.mp3 [--words words.json]
                      [--voice Puck] [--provider auto|gemini|nexabot]

- Gemini (pilihan 1): GEMINI_API_KEY, model GEMINI_TTS_MODEL (default gemini-3.8-flash-tts),
  suara GEMINI_VOICE (default Puck). Hantar TEKS SKRIP SAHAJA: arahan gaya dalam teks akan dibaca kuat.
  Gemini tiada timestamp perkataan -> jalankan wordtime.py --lang ms selepas ini.
- Nexabot (pilihan 2): POST /api/v1/voice, suara NEXABOT_VOICE_ID (default Adrian, eleven_v4,
  menyokong ms). Menulis --words terus dari timestamp Nexabot.
Teks mesti Bahasa Melayu Malaysia (lihat CLAUDE.md -> Bahasa). Kunci tidak pernah dicetak.
"""
import argparse, base64, json, os, subprocess, sys, tempfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def load_env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def to_mp3(src, out, raw_pcm=False):
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y"]
    if raw_pcm:
        cmd += ["-f", "s16le", "-ar", "24000", "-ac", "1"]
    cmd += ["-i", str(src), "-ar", "44100", "-b:a", "192k", str(out)]
    subprocess.run(cmd, check=True)


def gemini(text, out, voice):
    key = os.getenv("GEMINI_API_KEY")
    if not key or key.startswith("your_"):
        raise RuntimeError("GEMINI_API_KEY tiada dalam .env")
    model = os.getenv("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                      headers={"x-goog-api-key": key}, json=body, timeout=600)
    d = r.json()
    if "error" in d:
        raise RuntimeError(f"Gemini {r.status_code}: {d['error'].get('message', '')[:200]}")
    data = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as f:
        f.write(data)
    try:
        to_mp3(f.name, out, raw_pcm=not data[:4] == b"RIFF")
    finally:
        os.unlink(f.name)
    return None


def nexabot(text, out, voice_id):
    headers = {}
    if os.getenv("NEXABOT_API_KEY") and not os.getenv("NEXABOT_API_KEY").startswith("your_"):
        headers["x-api-key"] = os.environ["NEXABOT_API_KEY"]
    r = requests.post("https://nexabot.id/api/v1/voice", json={"text": text, "voice_id": voice_id},
                      headers=headers, timeout=600).json()
    if not r.get("ok"):
        raise RuntimeError(f"Nexabot: {r.get('error')}")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(requests.get(r["url"], timeout=600).content)
    try:
        to_mp3(f.name, out)
    finally:
        os.unlink(f.name)
    return [[round(x["start"], 3), x["text"]] for x in r.get("timestamps", [])]


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", help="tulis [[detik, kata], ...] (Nexabot sahaja)")
    ap.add_argument("--voice", help="suara Gemini (default GEMINI_VOICE / Puck)")
    ap.add_argument("--nexabot-voice", help="voice_id Nexabot (default NEXABOT_VOICE_ID / Adrian)")
    ap.add_argument("--provider", default="auto", choices=["auto", "gemini", "nexabot"])
    a = ap.parse_args()
    text = Path(a.text_file).read_text(encoding="utf-8").strip()
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    order = {"auto": ["gemini", "nexabot"], "gemini": ["gemini"], "nexabot": ["nexabot"]}[a.provider]
    errors = []
    for p in order:
        try:
            if p == "gemini":
                words = gemini(text, out, a.voice or os.getenv("GEMINI_VOICE", "Puck"))
            else:
                words = nexabot(text, out, a.nexabot_voice or os.getenv("NEXABOT_VOICE_ID", "7MkLnPXETw81c6o9Z5yj"))
            if a.words and words:
                Path(a.words).write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
            print(f"OK {p}: {out}" + (f" + {a.words}" if a.words and words else
                                       ("  (tiada timestamp: jalankan wordtime.py --lang ms)" if a.words else "")))
            return
        except Exception as e:
            errors.append(f"{p}: {e}")
            print(f"GAGAL {p}: {e}", file=sys.stderr)
    sys.exit("Semua penyedia TTS gagal:\n  " + "\n  ".join(errors))


if __name__ == "__main__":
    main()
