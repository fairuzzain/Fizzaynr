#!/usr/bin/env python3
"""Nexabot fallback for the magi-2 skill: submit one clip, wait, download, optionally trim.

Usage:
  python nexabot_run.py <body.json> <out.mp4> [--trim SECONDS]

body.json is a Nexabot request, e.g.
  {"mode":"t2v","ratio":2,"resolution":1080,"prompt":"..."}
  {"mode":"sfv","ratio":1,"resolution":1080,"prompt":"...","media":["start.png"]}
Local paths in "media" are sent as data URIs. Modes and limits: GET https://nexabot.id/api/v1/modes
Key: NEXABOT_API_KEY from the environment or <repo>/.env (never printed).
"""
import argparse, base64, json, mimetypes, os, subprocess, sys, time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

BASE = os.getenv("NEXABOT_BASE", "https://nexabot.id")


def repo_root():
    try:
        return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    except Exception:
        return Path(__file__).resolve().parents[4]


def api_key():
    key = os.getenv("NEXABOT_API_KEY")
    if key:
        return key
    env = repo_root() / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("NEXABOT_API_KEY="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    # Some environments inject the key at a proxy; the header just needs a value.
    return "set-by-proxy"


def data_uri(path, base_dir):
    p = Path(path)
    if not p.is_absolute():
        p = base_dir / p
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("body")
    ap.add_argument("out")
    ap.add_argument("--trim", type=float, help="cut the result to this many seconds (Nexabot clips are ~15 s)")
    ap.add_argument("--timeout", type=int, default=1500)
    a = ap.parse_args()

    body_path = Path(a.body)
    body = json.loads(body_path.read_text(encoding="utf-8"))
    if body.get("media"):
        body["media"] = [m if str(m).startswith(("data:", "http")) else data_uri(m, body_path.parent)
                         for m in body["media"]]

    s = requests.Session()
    s.headers["x-api-key"] = api_key()

    for attempt in range(5):
        r = s.post(BASE + "/api/v1/api", json=body, timeout=300)
        if r.status_code in (429, 502, 503, 504):
            time.sleep(5 * (attempt + 1))
            continue
        d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if r.status_code >= 400 or not d.get("ok"):
            sys.exit(f"submit failed {r.status_code}: {d.get('error') or r.text[:300]}")
        break
    else:
        sys.exit("submit failed after retries")
    job = d["job_id"]
    print(f"job {job}  model {d.get('model_label')}  cost {d.get('credit_cost')}  balance {d.get('credit_balance')}", flush=True)

    t0, interval = time.time(), 5
    while True:
        if time.time() - t0 > a.timeout:
            sys.exit(f"timed out; job {job} can still be downloaded within 60 min")
        time.sleep(interval)
        g = s.get(f"{BASE}/api/v1/jobs/{job}", timeout=60)
        if g.status_code in (429, 502, 503, 504):
            continue
        g.raise_for_status()
        j = g.json()
        j = j.get("job") or j
        if j.get("status") == "done":
            break
        if j.get("status") == "failed":
            sys.exit(f"job failed: {j.get('error')}")
        interval = min(interval * 1.2, 10)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = out.with_suffix(".raw.mp4") if a.trim else out
    with s.get(f"{BASE}/api/v1/jobs/{job}/download", stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(raw, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
    if a.trim:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-t", str(a.trim),
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out)], check=True)
    print(f"saved {out} after {int(time.time() - t0)} s")


if __name__ == "__main__":
    main()
