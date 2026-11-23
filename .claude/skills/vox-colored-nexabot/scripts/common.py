"""Shared helpers: project paths, .env loading, Nexabot client, JSON IO."""
import base64
import json
import mimetypes
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(os.getenv("VOX_PROJECT_ROOT") or Path(__file__).resolve().parents[4])
load_dotenv(PROJECT_ROOT / ".env")

ASSETS = PROJECT_ROOT / "assets"
MUSIC_DIR = Path(os.getenv("MUSIC_DIR") or ASSETS / "music")
GUIDELINES = PROJECT_ROOT / "guidelines" / "colored"   # vox-colored: own prompt system
RUNS = Path(os.getenv("RUNS_DIR") or PROJECT_ROOT / "runs")

NEXABOT_BASE = "https://nexabot.id"
# Fallback key file shared with the Motion_as_kit nexabot.ts client
NEXABOT_KEY_FILE = Path(os.getenv("NEXABOT_KEY_FILE") or
                        Path(os.getenv("MOTION_KIT") or PROJECT_ROOT / "vendor" / "Motion_as_kit") / ".env.nexabot")
CODEX_IMAGE_HINT = Path(os.getenv("CODEX_IMAGE_PS1") or PROJECT_ROOT / ".claude" / "skills" / "codex-image" / "codex-image.ps1")
OPENAI_IMAGE = PROJECT_ROOT / ".claude" / "skills" / "codex-image" / "openai_image.py"
# Nexabot API (https://nexabot.id/developers, checked 2026-11-23). Failed jobs are refunded.
CREDIT_COST = 0.15        # img / music / tts on /api/v1/api, without the API Unlimited plan
VIDEO_COST = 0.3          # any video mode (t2v/sfv/i2v/r2v/extend) on omni_flash; 0 on API Unlimited
IMAGE_COST = 0.1          # sync premium image models, POST /api/v1/image (always charged)
VOICE_COST = 0.02         # sync ElevenLabs voice, POST /api/v1/voice (always charged)
VIDEO_MODEL = "omni_flash"  # Omni Flash 1.2, the only video model since 2026-11-11 (omni/veo -> 400)
VIDEO_MODES = ("t2v", "sfv", "i2v", "r2v", "extend")
RESULT_TTL_MIN = 30       # result files are deleted 30 min after a job finishes (then 410)

TRIM_START = 0.25          # seconds cut from the head of every generated clip
GEN_DURATIONS = (4, 8)     # clip length classes used by segment.py
CLIP_SECONDS = int(os.getenv("VIDEO_DURATION") or 10)  # omni_flash `duration` sent per clip (API allows 1-60, default 15)
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")
NEXABOT_RATIO = {"16:9": 1, "9:16": 2}      # video `ratio`
NEXABOT_ASPECT = {"16:9": 2, "9:16": 5}     # image `aspect`


def env(name, default=None, required=False):
    val = os.getenv(name, default)
    if required and not val:
        sys.exit(f"ERROR: {name} is not set. Add it to {PROJECT_ROOT / '.env'}")
    return val


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_style_reference():
    for ext in IMAGE_EXTS:
        p = ASSETS / f"style_reference_colored{ext}"   # vox-colored style sheet
        if p.exists():
            return p
    return None


def data_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def nexabot_key():
    key = os.getenv("NEXABOT_API_KEY")
    if key and not key.startswith("your_"):
        return key.strip()
    if NEXABOT_KEY_FILE.exists():
        for line in NEXABOT_KEY_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("NEXABOT_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


class Nexabot:
    """Async: POST /api/v1/api -> poll GET /api/v1/jobs/<id> -> GET /api/v1/jobs/<id>/download.
    Sync (final file `url` in the reply): POST /api/v1/image, POST /api/v1/voice."""

    def __init__(self):
        key = nexabot_key()
        if not key:
            sys.exit(f"ERROR: NEXABOT_API_KEY not set in .env (or {NEXABOT_KEY_FILE})")
        self.s = requests.Session()
        self.s.headers["x-api-key"] = key

    def _get(self, path):
        r = self.s.get(NEXABOT_BASE + path, timeout=60)
        r.raise_for_status()
        return r.json()

    def credit(self):
        return self._get("/api/v1/api/credit")

    def modes(self):
        """Modes, video models and the `tts` voice names."""
        return self._get("/api/v1/modes")

    def image_models(self):
        return self._get("/api/v1/image")

    def voices(self):
        """ElevenLabs voices for POST /api/v1/voice (voice_id, name, gender, languages, features)."""
        return self._get("/api/v1/voices")

    @staticmethod
    def _json(r):
        return r.json() if r.headers.get("content-type", "").startswith("application/json") else {}

    def _post(self, path, body, label, timeout=300):
        for attempt in range(5):
            r = self.s.post(NEXABOT_BASE + path, json=body, timeout=timeout)
            if r.status_code in (429, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            d = self._json(r)
            if r.status_code >= 400 or not d.get("ok"):
                raise RuntimeError(f"{label} -> {r.status_code}: {d.get('error') or r.text[:300]}")
            return d
        raise RuntimeError(f"{label} -> still {r.status_code} after retries")

    def submit(self, body):
        body = dict(body)
        if body.get("mode") in VIDEO_MODES:
            body.setdefault("model", VIDEO_MODEL)
        return self._post("/api/v1/api", body, f"{body.get('mode')} submit")["job_id"]

    def wait(self, job_id, timeout=1200, interval=3):
        """Poll every 2-5 s (the docs: faster gives nothing) until done/failed.
        Returns (job, None) or (None, error)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(interval)
            r = self.s.get(f"{NEXABOT_BASE}/api/v1/jobs/{job_id}", timeout=60)
            if r.status_code in (429, 502, 503, 504):
                continue
            r.raise_for_status()
            d = r.json()
            job = d.get("job") or d
            if job.get("status") == "done":
                return job, None
            if job.get("status") == "failed":
                return None, f"job failed: {job.get('error')}"
            interval = min(interval * 1.2, 5)
        return None, f"timed out; job {job_id} may still finish - download within {RESULT_TTL_MIN} min of completion"

    def download(self, job_id, dest):
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self.s.get(f"{NEXABOT_BASE}/api/v1/jobs/{job_id}/download", stream=True, timeout=600) as r:
            if r.status_code == 410:
                raise RuntimeError(f"job {job_id}: file expired ({RESULT_TTL_MIN} min after completion)")
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 16):
                    f.write(chunk)
        return dest

    def run(self, body, dest, timeout=1200):
        """Submit, wait and download in one go. Returns (path, None) or (None, error)."""
        job_id = self.submit(body)
        job, err = self.wait(job_id, timeout=timeout)
        if err:
            return None, err
        return self.download(job_id, dest), None

    def _fetch(self, url, dest):
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = url if url.startswith("http") else NEXABOT_BASE + url
        with self.s.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 16):
                    f.write(chunk)
        return dest

    def image(self, prompt, dest, model="nano_banana_2", **opts):
        """Sync premium image (0.1 credit). opts: aspect="16:9", resolution="2K" for nano_banana*,
        image_size="landscape_16_9" for gpt_image_* / mai_image_*. See image_models()."""
        d = self._post("/api/v1/image", {"model": model, "prompt": prompt, **opts}, f"image {model}", timeout=300)
        return self._fetch(d["url"], dest), d

    def voice(self, text, voice_id, dest, language_code="id-ID", **opts):
        """Sync ElevenLabs voice (0.02 credit, text <= 5000 chars). opts: speed 0.5-2, and
        stability / similarity_boost / style 0-1 where the voice's features allow them.
        Returns (path, reply); reply["timestamps"] = [{text, start}]."""
        body = {"text": text, "voice_id": voice_id, "language_code": language_code, **opts}
        d = self._post("/api/v1/voice", body, "voice", timeout=300)
        return self._fetch(d["url"], dest), d
