"""Verify keys, assets, guidelines and tools before a run. Exit 1 if anything is missing."""
import shutil
import sys

import importlib.util

from common import (AUDIO_EXTS, CODEX_IMAGE_HINT, GUIDELINES, MUSIC_DIR, PROJECT_ROOT, Nexabot, env,
                    find_style_reference, nexabot_key)

problems = []
if not nexabot_key():
    problems.append("NEXABOT_API_KEY missing in .env")
else:
    try:
        c = Nexabot().credit()
        print(f"Nexabot balance: {c.get('credit')} credits ({c.get('credit_cost')} per request)")
    except Exception as e:
        problems.append(f"Nexabot API not reachable or key rejected: {e}")
if not importlib.util.find_spec("faster_whisper"):
    problems.append("faster-whisper missing (.venv/Scripts/python -m pip install faster-whisper)")
if env("IMAGE_BACKEND", "nexabot") == "codex" and not CODEX_IMAGE_HINT.exists():
    problems.append(f"IMAGE_BACKEND=codex but {CODEX_IMAGE_HINT} is missing")
if not find_style_reference():
    problems.append("assets/style_reference_colored.(png|jpg|jpeg|webp) missing")
for g in ("image-prompts.md", "video-prompts.md"):
    if not (GUIDELINES / g).exists():
        problems.append(f"guidelines/colored/{g} missing")
if not MUSIC_DIR.exists() or not any(p.suffix.lower() in AUDIO_EXTS for p in MUSIC_DIR.iterdir()):
    problems.append("no music in assets/music/")
for tool in ("ffmpeg", "ffprobe"):
    if not shutil.which(tool):
        problems.append(f"{tool} not on PATH (winget install Gyan.FFmpeg)")

if problems:
    print("SETUP INCOMPLETE:\n  - " + "\n  - ".join(problems))
    sys.exit(1)
print(f"Setup OK ({PROJECT_ROOT})")
