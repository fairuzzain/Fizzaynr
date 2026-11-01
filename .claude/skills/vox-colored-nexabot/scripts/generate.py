"""Generate clip keyframe images and clip videos via Nexabot (or Codex for images).

Usage:
  python generate.py images <run_dir> [--only ch1_c02,ch1_c05] [--force] [--dry]
  python generate.py videos <run_dir> [--only ...] [--force] [--dry]

Images (IMAGE_BACKEND in .env):
  "nexabot" -> Nexabot `img` (text only: the style sheet cannot be attached), 0.15 credit each
  "codex"   -> Codex CLI on the ChatGPT login with assets/style_reference_colored.png as reference,
               free, one image at a time (parallel Codex runs collide on temp files)
Videos (VIDEO_ENGINE in .env, or --engine):
  "veo"      -> Nexabot `sfv` (Veo, ~10 s, the keyframe is the first frame), 0.15 credit each
  "seedance" -> Nexabot Seedance 2.5 (15 s, keyframe as start frame), 0.2 credit each, always charged

Reads prompts from <run_dir>/plan.json, writes <run_dir>/images/<id>.png and
<run_dir>/clips/<id>.mp4. Existing outputs are skipped unless --force or listed in --only.
--dry only prints what would run and what it costs.
"""
import argparse
import re
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import (CODEX_IMAGE_HINT as CODEX_IMAGE, CREDIT_COST, SEEDANCE_COST, NEXABOT_ASPECT, NEXABOT_RATIO, Nexabot,
                    data_uri, env, find_style_reference, load_json, save_json)

lock = threading.Lock()


def log(msg):
    with lock:
        print(msg, flush=True)


def name_tokens(names):
    toks = set()
    for n in names:
        toks.add(n.lower())
        toks.update(t.lower() for t in re.split(r"[\s.\-']+", n) if len(t) > 2)
    return toks


def validate(clip, stage):
    """Hard rules for public-figure clips. Returns a list of errors."""
    errs, figs = [], clip.get("public_figures") or []
    if stage == "images":
        p = clip.get("image_prompt", "").lower()
        if not p:
            errs.append("image_prompt is empty")
        if figs:
            if "black bar" not in p:
                errs.append("public-figure image_prompt must specify a black bar over the eyes")
            if not any(k in p for k in ("distance", "far away", "far off", "background", "wide shot")):
                errs.append("public-figure image_prompt must place the figure far from camera")
    else:
        p = clip.get("video_prompt", "")
        if not p:
            errs.append("video_prompt is empty")
        hits = [t for t in name_tokens(figs) if re.search(rf"\b{re.escape(t)}\b", p.lower())]
        if hits:
            errs.append(f"video_prompt must not name public figures (found: {', '.join(sorted(hits))})")
    return errs


def to_png(src, dest):
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), str(dest)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"png conversion failed: {r.stderr[-300:]}")
    Path(src).unlink(missing_ok=True)


def image_nexabot(nb, run, clip):
    out = run / "images" / f"{clip['id']}.png"
    body = {"mode": "img", "prompt": clip["image_prompt"], "aspect": NEXABOT_ASPECT[env("ASPECT_RATIO", "16:9")]}
    for attempt in (1, 2):
        try:
            path, err = nb.run(body, out.with_suffix(".jpg"), timeout=600)
        except RuntimeError as e:
            path, err = None, str(e)
        if path:
            to_png(path, out)
            log(f"[image] {clip['id']} done")
            return None
        log(f"[image] {clip['id']} attempt {attempt} failed: {err}")
    return f"{clip['id']}: {err}"


def image_codex(run, clip, style):
    out = run / "images" / f"{clip['id']}.png"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(clip["image_prompt"])
        prompt_file = f.name
    aspect = env("ASPECT_RATIO", "16:9")
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(CODEX_IMAGE), "-PromptFile", prompt_file,
           "-Out", str(out), "-Aspect", aspect, "-Width", "1920" if aspect == "16:9" else "1080",
           "-Reference", str(style), "-Overwrite"]
    try:
        for attempt in (1, 2):
            log(f"[image] {clip['id']} codex attempt {attempt}")
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            if r.returncode == 0 and out.exists():
                log(f"[image] {clip['id']} done")
                return None
            err = (r.stderr or r.stdout)[-400:]
            log(f"[image] {clip['id']} attempt {attempt} failed: {err}")
        return f"{clip['id']}: {err}"
    finally:
        Path(prompt_file).unlink(missing_ok=True)


def run_video(nb, run, clip, engine="veo"):
    local = run / "images" / f"{clip['id']}.png"
    if not local.exists():
        return f"{clip['id']}: no image - run the images step first"
    ratio = NEXABOT_RATIO[env("ASPECT_RATIO", "16:9")]
    if engine == "seedance":
        # prompt max 2000 chars; jobs queue in 60 s batches, so allow a long wait
        body = {"mode": "seedance", "prompt": clip["video_prompt"][:2000], "duration": 15, "ratio": ratio,
                "media": [data_uri(local)]}
    else:
        body = {"mode": "sfv", "prompt": clip["video_prompt"], "media": [data_uri(local)], "ratio": ratio,
                "resolution": int(env("VIDEO_RESOLUTION", "720"))}
    for attempt in (1, 2):
        try:
            path, err = nb.run(body, run / "clips" / f"{clip['id']}.mp4",
                               timeout=2700 if engine == "seedance" else 1500)
        except RuntimeError as e:
            path, err = None, str(e)
        if path:
            log(f"[video] {clip['id']} done")
            return None
        log(f"[video] {clip['id']} attempt {attempt} failed: {err}")
    return f"{clip['id']}: {err}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["images", "videos"])
    ap.add_argument("run_dir")
    ap.add_argument("--only", help="comma-separated clip ids")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry", action="store_true", help="print the job count and cost, generate nothing")
    ap.add_argument("--engine", choices=["veo", "seedance"], help="video engine (default VIDEO_ENGINE or veo)")
    a = ap.parse_args()
    run = Path(a.run_dir)
    plan_path = run / "plan.json"
    plan = load_json(plan_path)
    only = set(a.only.split(",")) if a.only else None

    clips = [c for ch in plan["chapters"] for c in ch["clips"]]
    errors = {c["id"]: validate(c, a.stage) for c in clips}
    errors = {k: v for k, v in errors.items() if v}
    if errors:
        for cid, errs in errors.items():
            print(f"{cid}:\n  - " + "\n  - ".join(errs))
        sys.exit("Fix plan.json before generating.")

    sub = "images" if a.stage == "images" else "clips"
    ext = "png" if a.stage == "images" else "mp4"
    todo = []
    for c in clips:
        out = run / sub / f"{c['id']}.{ext}"
        if only is not None:
            if c["id"] in only:
                todo.append(c)
        elif a.force or not out.exists():
            todo.append(c)
    if not todo:
        print("Nothing to do (all outputs exist; use --force or --only).")
        return

    backend = env("IMAGE_BACKEND", "nexabot") if a.stage == "images" else "nexabot"
    engine = a.engine or env("VIDEO_ENGINE", "veo")
    unit = SEEDANCE_COST if a.stage == "videos" and engine == "seedance" else CREDIT_COST
    cost = 0 if backend == "codex" else len(todo) * unit
    via = backend if a.stage == "images" else f"nexabot {engine}"
    print(f"{len(todo)} {a.stage} via {via} · ~{cost:.2f} credits")
    if a.dry:
        return

    if backend == "codex":
        style = find_style_reference()
        if not style:
            sys.exit("Missing assets/style_reference_colored.(png|jpg|jpeg|webp)")
        job, workers = (lambda c: image_codex(run, c, style)), 1
    elif backend == "nexabot":
        nb = Nexabot()
        print(f"balance: {nb.credit().get('credit')} credits")
        job = (lambda c: image_nexabot(nb, run, c)) if a.stage == "images" else (lambda c: run_video(nb, run, c, engine))
        # Concurrent `img` jobs came back as copies of one image (2026-10-30), so images run one at a time
        workers = 1 if a.stage == "images" else int(env("MAX_PARALLEL", "4"))
    else:
        sys.exit(f"IMAGE_BACKEND must be 'nexabot' or 'codex', got {backend!r}")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda c: _safe(job, c), todo))
    save_json(plan_path, plan)

    failed = [r for r in results if r]
    print(f"\n{len(todo) - len(failed)}/{len(todo)} {a.stage} succeeded.")
    if failed:
        print("FAILED:\n  " + "\n  ".join(failed))
        sys.exit(1)


def _safe(job, clip):
    try:
        return job(clip)
    except Exception as e:  # keep other parallel jobs running
        return f"{clip['id']}: {e}"


if __name__ == "__main__":
    main()
