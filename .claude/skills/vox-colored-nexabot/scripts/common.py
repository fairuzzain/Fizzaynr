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
CREDIT_COST = 0.15        # per request without the API Unlimited plan (refunded on failure)
SEEDANCE_COST = 0.2       # Seedance 2.5 (own endpoint), always charged, refunded on failure

TRIM_START = 0.25          # seconds cut from the head of every generated clip
GEN_DURATIONS = (4, 8)     # clip length classes used by segment.py (Nexabot Veo clips run 10 s)
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
    """POST /api/v1/api -> poll /api/v1/jobs/<id> -> GET /api/v1/jobs/<id>/download.
    A body with mode "seedance" goes to /api/v1/seedance (and /api/v1/seedance/<id>) instead."""

    def __init__(self):
        key = nexabot_key()
        if not key:
            sys.exit(f"ERROR: NEXABOT_API_KEY not set in .env (or {NEXABOT_KEY_FILE})")
        self.s = requests.Session()
        self.s.headers["x-api-key"] = key

    def credit(self):
        r = self.s.get(NEXABOT_BASE + "/api/v1/api/credit", timeout=60)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _paths(body):
        """(submit path, job path prefix): Seedance 2.5 has its own endpoint, not listed in /modes."""
        if body.get("mode") == "seedance":
            return "/api/v1/seedance", "/api/v1/seedance"
        return "/api/v1/api", "/api/v1/jobs"

    def submit(self, body):
        submit_path, _ = self._paths(body)
        if body.get("mode") == "seedance":
            body = {k: v for k, v in body.items() if k != "mode"}
        for attempt in range(5):
            r = self.s.post(NEXABOT_BASE + submit_path, json=body, timeout=300)
            if r.status_code in (429, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            if r.status_code >= 400 or not d.get("ok"):
                raise RuntimeError(f"{body.get('mode', 'seedance')} submit -> {r.status_code}: {d.get('error') or r.text[:300]}")
            return d["job_id"]
        raise RuntimeError(f"{body.get('mode', 'seedance')} submit -> still {r.status_code} after retries")

    def wait(self, job_id, timeout=1200, interval=4, jobs="/api/v1/jobs"):
        """Poll until done/failed. Returns (job, None) or (None, error)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(interval)
            r = self.s.get(f"{NEXABOT_BASE}{jobs}/{job_id}", timeout=60)
            if r.status_code in (429, 502, 503, 504):
                continue
            r.raise_for_status()
            d = r.json()
            job = d.get("job") or d
            if job.get("status") == "done":
                return job, None
            if job.get("status") == "failed":
                return None, f"job failed: {job.get('error')}"
            interval = min(interval * 1.2, 10)
        return None, f"timed out; job {job_id} can still be downloaded within 60 min"

    def download(self, job_id, dest, jobs="/api/v1/jobs"):
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self.s.get(f"{NEXABOT_BASE}{jobs}/{job_id}/download", stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 16):
                    f.write(chunk)
        return dest

    def run(self, body, dest, timeout=1200):
        """Submit, wait and download in one go. Returns (path, None) or (None, error)."""
        _, jobs = self._paths(body)
        job_id = self.submit(body)
        job, err = self.wait(job_id, timeout=timeout, jobs=jobs, interval=10 if "seedance" in jobs else 4)
        if err:
            return None, err
        return self.download(job_id, dest, jobs=jobs), None
