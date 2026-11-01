#!/usr/bin/env python3
"""Generate or edit one image through the OpenAI-compatible Images API (repo provider) and save a verified PNG.

Usage:
  python openai_image.py --prompt "<prompt>" --out <path>.png [--aspect 16:9] [--width 1920]
                         [--reference img1.png img2.png] [--pad auto|#RRGGBB] [--model gpt-image-1.5]
                         [--quality low|medium|high|auto] [--overwrite]

Config (repo .env or environment): OPENAI_API_KEY (required),
OPENAI_BASE_URL (default https://space.stationine.com/v1), IMAGE_MODEL (default gpt-image-1.5).
Prints JSON {Path, Width, Height, Bytes, Source} on success; exits non-zero with the API error on failure.
"""
import argparse, base64, io, json, mimetypes, os, subprocess, sys, urllib.error, urllib.request, uuid
from pathlib import Path

from PIL import Image


def repo_root():
    try:
        return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True,
                                            cwd=Path(__file__).resolve().parent).strip())
    except Exception:
        return Path(__file__).resolve().parents[3]


def load_env(path):
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def ratio(s):
    a, b = s.split(":")
    return float(a) / float(b)


def api_size(r):
    # Sizes every gpt-image model accepts; pick the closest shape, then crop/pad locally.
    if r > 1.15:
        return "1536x1024"
    if r < 0.87:
        return "1024x1536"
    return "1024x1024"


UA = "curl/8.5.0 fizzaynr-image/1.0"  # provider is behind Cloudflare: Python's default UA gets 403 (1010)


def post(url, key, body=None, files=None):
    headers = {"Authorization": f"Bearer {key}", "User-Agent": UA}
    if files is None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    else:
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in body.items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for p in files:
            mime = mimetypes.guess_type(p)[0] or "image/png"
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="{Path(p).name}"\r\n'
                         f"Content-Type: {mime}\r\n\r\n".encode() + Path(p).read_bytes() + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        data = b"".join(parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code}: {e.read().decode(errors='replace')[:800]}")


def fetch_image(item):
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        with urllib.request.urlopen(urllib.request.Request(item["url"], headers={"User-Agent": UA}), timeout=300) as r:
            return r.read()
    sys.exit(f"API returned no image: {json.dumps(item)[:400]}")


def fit(img, r, pad):
    w, h = img.size
    if pad:
        color = img.getpixel((0, 0)) if pad == "auto" else pad
        if w / h > r:
            nw, nh = w, round(w / r)
        else:
            nw, nh = round(h * r), h
        canvas = Image.new("RGB", (nw, nh), color)
        canvas.paste(img, ((nw - w) // 2, (nh - h) // 2))
        return canvas
    if w / h > r:
        nw = round(h * r); x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    nh = round(w / r); y = (h - nh) // 2
    return img.crop((0, y, w, y + nh))


def free_path(p, overwrite):
    if overwrite or not p.exists():
        return p
    i = 2
    while (q := p.with_name(f"{p.stem}-{i}{p.suffix}")).exists():
        i += 1
    return q


def main():
    root = repo_root()
    load_env(root / ".env")
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--aspect", default="1:1")
    ap.add_argument("--width", type=int)
    ap.add_argument("--reference", nargs="*", default=[])
    ap.add_argument("--pad")
    ap.add_argument("--model", default=os.environ.get("IMAGE_MODEL", "gpt-image-1.5"))
    ap.add_argument("--quality", default=os.environ.get("IMAGE_QUALITY", "high"))
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit(f"OPENAI_API_KEY is not set. Add it to {root / '.env'}")
    base = os.environ.get("OPENAI_BASE_URL", "https://space.stationine.com/v1").rstrip("/")
    r = ratio(a.aspect)
    body = {"model": a.model, "prompt": a.prompt, "size": api_size(r), "quality": a.quality, "n": 1}
    for p in a.reference:
        if not Path(p).is_file():
            sys.exit(f"Reference not found: {p}")
    if a.reference:
        res = post(f"{base}/images/edits", key, body, files=a.reference)
    else:
        res = post(f"{base}/images/generations", key, body)
    data = res.get("data") or []
    if not data:
        sys.exit(f"API returned no data: {json.dumps(res)[:600]}")

    img = Image.open(io.BytesIO(fetch_image(data[0]))).convert("RGB")
    raw_w, raw_h = img.size
    img = fit(img, r, a.pad)
    if a.width:
        img = img.resize((a.width, round(a.width / r)), Image.LANCZOS)
    out = free_path(Path(a.out).expanduser().resolve(), a.overwrite)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    Image.open(out).verify()
    print(json.dumps({"Path": str(out), "Width": img.width, "Height": img.height,
                      "Bytes": out.stat().st_size, "RawWidth": raw_w, "RawHeight": raw_h, "Source": f"{a.model} via {base}"}))


if __name__ == "__main__":
    main()
