#!/usr/bin/env python3
"""effects.py - reel effects on a talking-head clip: prepare, transcribe, build, render.

The effects are fixed, parameterised HTML pages (templates/<effect>.html, contract: window.hfPage with
width/height/fps/frames/ready/render(t, f)). This script never writes effect code; it fills params, renders
the page frame by frame in headless Chromium (render.mjs) and encodes with ffmpeg.

Subcommands (W = one workspace per effect; prepared media can be shared, see `link`):
  prepare W CLIP [--matte MATTE] [--max-seconds 60]
      CLIP  -> W/src/clip.mp4 (1080x1920 cover crop, 30 fps CFR, AAC audio kept) + W/plates/main/%05d.jpg
      MATTE -> remove_background output of the ORIGINAL clip (person on black): same chain, then
               W/mattes/main/%05d.png (white + alpha, half size; specks removed, holes filled)
  matte W [--step 3]  person matte made in the sandbox (U^2-Net human segmentation, Apache-2.0), for hosts
                      without remove_background: W/mattes/main/%05d.png from W's plates, same format as prepare
  link W SRC_W        reuse SRC_W's src/, plates/, mattes/ and transcript.json in another workspace
  stack W PREV_W      W starts from PREV_W's rendered effect (several commands on one video; same matte)
  logos W --items JSON
      -> W/logos/ + W/logos.json for tier-list items the user sent no logo for: {"ChatGPT": {"brand":
         "OpenAI", "domain": "chatgpt.com"}}; Simple Icons in brand colour, else the site's favicon
  transcribe W        -> W/transcript.json (word timestamps, faster-whisper); prints the timed text
  build W EFFECT [--params JSON]
      -> W/motion/ (index.html, effect-kit.js, fonts/, logos/, params.json). Effects fire at `moments`
         across the clip, each at its `cue` (words as spoken) or `start`; tier-list `items` land when said.
  render W [--stills T1,T2,..] [--jobs 4]
      stills -> W/qa/stills.jpg (contact sheet); otherwise W/out/<effect>.mp4 with the clip's audio
  effects             the effect list with parameters and defaults, as JSON

Python 3.11+, stdlib + Pillow; ffmpeg/ffprobe; node with Playwright Chromium (render.mjs).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WIDTH, HEIGHT, FPS = 1080, 1920, 30
# Instagram/TikTok buttons and caption cover the edges: important graphics stay between these columns.
SAFE_LEFT, SAFE_RIGHT = 120, 960
CLIP = "main"
TIERS = ("S", "A", "B", "C", "D")
AMOUNT_RE = re.compile(r"^[^\d-]{0,3}-?[\d,]*\.?\d+\s*[kKmMbB]?\S{0,6}$")
CUE_LEAD = 0.15  # start the effect just before the cue word

# Each effect fires at one or more moments across the clip, usually where the speaker says the matching
# thing (`cue`). `moment` fields belong to one occurrence, `global` ones to the whole clip.
TIMING = {
    "start": {"type": "float", "default": None, "min": 0.0},
    "cue": {"type": "str", "default": None, "max_len": 60},
}
EFFECTS = {
    "over-the-shoulder": {
        "font": "Inter.ttf",
        "needs_matte": True,
        "seconds": (2.8, 2.0, 8.0),
        "max_moments": 6,
        "moment": {
            "before_value": {"type": "str", "required": True, "max_len": 16},
            "after_value": {"type": "str", "required": True, "max_len": 16},
            "before_label": {"type": "str", "default": "BEFORE", "max_len": 16},
            "after_label": {"type": "str", "default": "AFTER", "max_len": 16},
        },
        "global": {"card_y": {"type": "int", "default": None, "min": 200, "max": 1500}},
    },
    "glass-graph": {
        "font": "Inter.ttf",
        "needs_matte": False,
        "seconds": (3.0, 2.0, 10.0),
        "max_moments": 6,
        "moment": {
            "title": {"type": "str", "required": True, "max_len": 32},
            "from_value": {"type": "amount", "required": True},
            "to_value": {"type": "amount", "required": True},
        },
        "global": {
            "color": {"type": "color", "default": "#D97757"},
            "card_top": {"type": "int", "default": None, "min": 500, "max": 1260},
        },
    },
    "freeze-frame": {
        "font": "Inter.ttf",
        "needs_matte": True,
        "seconds": (2.5, 2.0, 8.0),
        "max_moments": 8,
        "moment": {
            "name": {"type": "str", "required": True, "max_len": 24},
            "role": {"type": "str", "default": "", "max_len": 24, "allow_empty": True},
        },
        "global": {"tag_y": {"type": "int", "default": None, "min": 600, "max": 1600}},
    },
    "tier-list": {
        "font": "Inter.ttf",
        "needs_matte": False,
        "global": {
            "topic": {"type": "str", "required": True, "max_len": 32},
            "rows": {"type": "rows", "default": None},
            "items": {"type": "items", "required": True},
            "logos": {"type": "logos", "default": None},
            "hold": {"type": "float", "default": 2.0, "min": 0.5, "max": 10.0},
            "panel_top": {"type": "int", "default": None, "min": 500, "max": 1000},
        },
    },
    "text-behind": {
        "font": "LeagueGothic.ttf",
        "needs_matte": True,
        "seconds": (2.2, 1.0, 10.0),
        "max_moments": 12,
        "moment": {"word": {"type": "str", "required": True, "max_len": 24}},
        "global": {
            "color": {"type": "color", "default": "#ffffff"},
            "font_px": {"type": "int", "default": 330, "min": 120, "max": 520},
            "head_y": {"type": "int", "default": None, "min": 200, "max": 1700},
        },
    },
    "captions": {
        "font": "Inter.ttf",
        "needs_matte": False,
        "global": {
            "look": {"type": "enum", "choices": ["spotlight", "cascade", "classic"], "default": "spotlight"},
            "color": {"type": "color", "default": None},
            "upper": {"type": "bool", "default": True},
            "y": {"type": "int", "default": 1380, "min": 900, "max": 1500},
            "max_words": {"type": "int", "default": 3, "min": 1, "max": 6},
        },
    },
    "grade-wipe": {
        "font": "Inter.ttf",
        "needs_matte": False,
        "seconds": (3.0, 1.5, 10.0),
        "max_moments": 1,
        "moment": {},
        "global": {
            "labels": {"type": "bool", "default": True},
            "before_label": {"type": "str", "default": "BEFORE", "max_len": 16},
            "after_label": {"type": "str", "default": "AFTER", "max_len": 16},
            "keep_after": {"type": "bool", "default": False},
            "warmth": {"type": "float", "default": 0.22, "min": 0.0, "max": 0.5},
            "teal": {"type": "float", "default": 0.35, "min": 0.0, "max": 0.7},
            "vignette": {"type": "float", "default": 0.28, "min": 0.0, "max": 0.6},
        },
    },
}


# Whole-clip looks: accent colour and panel tones shared by every effect, so outputs are not all alike.
STYLES = {
    "clean": {"accent": "#D97757", "panel": "rgba(14,14,16,0.88)", "tag": "rgba(12,12,14,0.82)"},
    "bold": {"accent": "#FFCF4A", "panel": "rgba(5,6,7,0.94)", "tag": "rgba(5,6,7,0.92)"},
    "neon": {"accent": "#39FF88", "panel": "rgba(6,10,24,0.86)", "tag": "rgba(8,12,30,0.86)"},
    "red": {"accent": "#EF3C32", "panel": "rgba(12,6,6,0.9)", "tag": "rgba(16,6,6,0.88)"},
}
GLOBAL_COMMON = {"style": {"type": "enum", "choices": list(STYLES), "default": "clean"}}


class UsageError(Exception):
    pass


# ------------------------------------------------------------------------------------------- helpers
def run(args, **kw):
    subprocess.run(args, check=True, **kw)


def ffmpeg(*args):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout
    return bool(out.strip())


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, data):
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def frame_count(W):
    return len(glob.glob(os.path.join(W, "plates", CLIP, "*.jpg")))


# ------------------------------------------------------------------------------------------- prepare
COVER = (f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
         f"crop={WIDTH}:{HEIGHT},fps={FPS},setsar=1")
BT709 = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
# Plates are JPEGs that Chromium decodes as full-range BT.601; the clip is limited-range BT.709.
TO_PLATE = "scale=in_color_matrix=bt709:in_range=tv:out_color_matrix=bt601:out_range=full,format=yuvj420p"
# Chromium screenshots are full-range BT.601 JPEGs; the delivery is limited-range BT.709 H.264.
FROM_FRAMES = "scale=in_color_matrix=bt601:in_range=full:out_color_matrix=bt709:out_range=tv"
# Finishing pass: fine moving grain and a gentle vignette so graphics sit in the footage like the plate.
FINISH = "noise=alls=3:allf=t,vignette=angle=PI/5"
# Grain defeats compression: cap the bitrate (about 12 Mb/s for 1080x1920 at 30 fps) so a 30 s clip stays ~45 MB.
RATE_CAP = ["-maxrate", "12M", "-bufsize", "24M"]
# remove_background returns the person on black without alpha: alpha = matte / original, so dark clothes
# and hair keep full opacity (A = matte grey, B = original grey).
DIVIDE = "if(lt(B,34),if(gt(A,10),255,0),clip((A*255/B-70)*1.9,0,255))"


def cmd_prepare(a):
    W = os.path.abspath(a.W)
    for path in (a.clip, a.matte):
        if path and not os.path.isfile(path):
            raise UsageError(f"not found: {path}")
    os.makedirs(os.path.join(W, "src"), exist_ok=True)
    clip = os.path.join(W, "src", "clip.mp4")
    audio = ["-map", "0:a:0", "-c:a", "aac", "-b:a", "192k"] if has_audio(a.clip) else ["-an"]
    ffmpeg("-i", a.clip, "-t", str(a.max_seconds), "-map", "0:v:0",
           "-vf", COVER + ",scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-c:v", "libx264", "-crf", "12", "-preset", "medium", *BT709, *audio, "-movflags", "+faststart", clip)
    plates = os.path.join(W, "plates", CLIP)
    shutil.rmtree(plates, ignore_errors=True)
    os.makedirs(plates)
    ffmpeg("-i", clip, "-vf", TO_PLATE, "-q:v", "1", "-start_number", "0", os.path.join(plates, "%05d.jpg"))
    n = frame_count(W)
    mattes = 0
    if a.matte:
        out = os.path.join(W, "mattes", CLIP)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        mw, mh = WIDTH // 2, HEIGHT // 2
        k = max(0, a.clean)
        # Opening (erode, then dilate) removes specks and thin strands the remover picks up around the
        # person (chair legs, table edges); closing fills small holes in hair and dark clothes.
        morph = ",".join(["erosion"] * k + ["dilation"] * k + ["dilation"] * 2 + ["erosion"] * 2)
        fc = (f"[0:v]{COVER},scale={mw}:{mh},format=gray[c];[1:v]scale={mw}:{mh},format=gray[o];"
              f"[c][o]blend=all_expr='{DIVIDE}':shortest=1,{morph},gblur=sigma=0.8[a];"
              f"color=white:s={mw}x{mh}:r={FPS}[w];[w][a]alphamerge=shortest=1,format=rgba")
        ffmpeg("-i", a.matte, "-i", clip, "-filter_complex", fc, "-frames:v", str(n), "-start_number", "0",
               os.path.join(out, "%05d.png"))
        mattes = len(glob.glob(os.path.join(out, "*.png")))
        if mattes < n:
            raise UsageError(f"the matte has {mattes} frames for {n} plates; use the matte of this exact clip")
    print(json.dumps({"clip": "src/clip.mp4", "frames": n, "mattes": mattes, "fps": FPS, "seconds": round(n / FPS, 2)}))


# U^2-Net human segmentation (Apache-2.0), fetched once per sandbox and checked against this digest.
MATTE_MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx"
MATTE_MODEL_SHA256 = "01eb6a29a5c4d8edb30b56adad9bb3a2a0535338e480724a213e0acfd2d1c73c"


def _matte_model():
    import hashlib
    path = os.path.expanduser("~/.cache/reel-effects/u2net_human_seg.onnx")
    if not os.path.isfile(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        run(["curl", "-sfL", "--retry", "3", "-o", path + ".part", MATTE_MODEL_URL])
        os.replace(path + ".part", path)
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    if digest.hexdigest() != MATTE_MODEL_SHA256:
        os.remove(path)
        raise UsageError("the matte model download is corrupt; run matte again")
    return path


def cmd_matte(a):
    """Matte from the prepared plates: segmentation every `step` frames, blended in between."""
    import cv2
    import numpy as np
    import onnxruntime as ort

    W = os.path.abspath(a.W)
    plates = sorted(glob.glob(os.path.join(W, "plates", CLIP, "*.jpg")))
    if not plates:
        raise UsageError("run prepare first")
    session = ort.InferenceSession(_matte_model(), providers=["CPUExecutionProvider"])
    name = session.get_inputs()[0].name
    mean, std = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])
    mw, mh = WIDTH // 2, HEIGHT // 2

    def segment(path):
        rgb = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
        x = (cv2.resize(rgb, (320, 320)).astype(np.float32) / 255 - mean) / std
        o = session.run(None, {name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
        o = (o - o.min()) / (o.max() - o.min() + 1e-6)
        return cv2.resize(o.astype(np.float32), (mw, mh), interpolation=cv2.INTER_CUBIC)

    step = max(1, a.step)
    keys = list(range(0, len(plates), step))
    if keys[-1] != len(plates) - 1:
        keys.append(len(plates) - 1)
    out = os.path.join(W, "mattes", CLIP)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    # Same clean-up as prepare: opening removes specks around the person, closing fills small holes.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    white = np.full((mh, mw, 3), 255, np.uint8)
    prev_f, prev = keys[0], segment(plates[keys[0]])
    for f in keys[1:] + [None]:
        cur = segment(plates[f]) if f is not None else prev
        last = f if f is not None else prev_f + 1
        for i in range(prev_f, last):
            k = 0 if f is None else (i - prev_f) / (f - prev_f)
            m = np.clip((prev * (1 - k) + cur * k - 0.15) / 0.7, 0, 1)
            m = (m * 255).astype(np.uint8)
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, kernel, iterations=max(0, a.clean // 2))
            m = cv2.GaussianBlur(cv2.morphologyEx(m, cv2.MORPH_CLOSE, kernel, iterations=2), (0, 0), 0.8)
            cv2.imwrite(os.path.join(out, f"{i:05d}.png"), np.dstack([white, m]))
        if f is None:
            break
        prev_f, prev = f, cur
    print(json.dumps({"mattes": len(glob.glob(os.path.join(out, "*.png"))), "frames": len(plates),
                      "segmented": len(keys)}))


def cmd_link(a):
    W, S = os.path.abspath(a.W), os.path.abspath(a.src)
    os.makedirs(W, exist_ok=True)
    for name in ("src", "plates", "mattes", "transcript.json"):
        if os.path.exists(os.path.join(S, name)) and not os.path.exists(os.path.join(W, name)):
            os.symlink(os.path.join(S, name), os.path.join(W, name))
    print(json.dumps({"workspace": W, "linked_from": S}))


def cmd_stack(a):
    """Use PREV's rendered effect as the clip of W, so several commands land on one video."""
    W, P = os.path.abspath(a.W), os.path.abspath(a.prev)
    prev = load_json(os.path.join(P, "motion", "params.json"))
    rendered = os.path.join(P, "out", f"{prev['effect']}.mp4")
    if not os.path.isfile(rendered):
        raise UsageError(f"render {prev['effect']} in {a.prev} first")
    if prev["effect"] == "freeze-frame":
        raise UsageError("freeze-frame holds frames, so the matte no longer lines up: apply it last")
    if os.path.islink(os.path.join(W, "src")):
        raise UsageError("W/src is linked to another workspace; use a fresh workspace for stack")
    os.makedirs(os.path.join(W, "src"), exist_ok=True)
    clip = os.path.join(W, "src", "clip.mp4")
    shutil.copyfile(rendered, clip)
    plates = os.path.join(W, "plates", CLIP)
    shutil.rmtree(plates, ignore_errors=True)
    os.makedirs(plates)
    ffmpeg("-i", clip, "-vf", TO_PLATE, "-q:v", "1", "-start_number", "0", os.path.join(plates, "%05d.jpg"))
    # Timing is unchanged, so the person matte and transcript of the original clip still apply.
    for name in ("mattes", "transcript.json"):
        src = os.path.realpath(os.path.join(P, name))
        if os.path.exists(src) and not os.path.exists(os.path.join(W, name)):
            os.symlink(src, os.path.join(W, name))
    print(json.dumps({"workspace": W, "on_top_of": prev["effect"], "frames": frame_count(W)}))


# ------------------------------------------------------------------------------------------- transcribe
def cmd_transcribe(a):
    W = os.path.abspath(a.W)
    clip = os.path.join(W, "src", "clip.mp4")
    if not os.path.isfile(clip):
        raise UsageError("run `prepare` first")
    from faster_whisper import WhisperModel  # preinstalled in the sandbox

    root = "/opt/whisper-models" if os.path.isdir("/opt/whisper-models") else None
    model = WhisperModel(a.model, device="cpu", compute_type="int8", download_root=root)
    segments, info = model.transcribe(clip, word_timestamps=True, vad_filter=True)
    words, lines = [], []
    for seg in segments:
        lines.append(f"[{seg.start:6.2f}] {seg.text.strip()}")
        for w in seg.words or []:
            words.append({"w": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)})
    save_json(os.path.join(W, "transcript.json"),
              {"language": info.language, "words": words, "onsets": speech_onsets(clip)})
    print("\n".join(lines) or "(no speech found)")


def speech_onsets(clip):
    """Times (s) of stressed syllables: peaks of rising loudness in 10 ms frames of the speech.

    Whisper word starts drift by a frame or two; effects snap to the nearest of these instead.
    """
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=False).stdout
    if not raw:
        return []
    import array
    import math

    pcm = array.array("h", raw)
    hop = 160
    env = [math.sqrt(sum(x * x for x in pcm[i:i + hop]) / hop) + 1.0 for i in range(0, len(pcm) - hop, hop)]
    db = [20 * math.log10(e) for e in env]
    flux = [max(0.0, db[i] - db[i - 2]) for i in range(2, len(db))]
    if not flux:
        return []
    mean = sum(flux) / len(flux)
    sd = math.sqrt(sum((x - mean) ** 2 for x in flux) / len(flux)) or 1.0
    out = []
    for i in range(1, len(flux) - 1):
        if flux[i] > mean + 1.5 * sd and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]:
            t = round((i + 2) * hop / 16000, 3)
            if not out or t - out[-1] > 0.08:
                out.append(t)
    return out


def _norm(s):
    # "mid-journey" and "Midjourney" compare equal; punctuation around words is ignored.
    return re.sub(r"[^\w%$.]+", " ", s.lower().replace("-", "")).strip(" .")


def _snap(t, onsets, window=0.12):
    """Nearest stressed onset within `window` seconds of t, else t."""
    best = min(onsets, key=lambda o: abs(o - t), default=None)
    return best if best is not None and abs(best - t) <= window else t


def cue_time(W, cue):
    """Start time of the first occurrence of `cue` (a word or short phrase) in the transcript."""
    path = os.path.join(W, "transcript.json")
    if not os.path.isfile(path):
        raise UsageError("`cue` needs a transcript: run `transcribe` first")
    words = load_json(path)["words"]
    # Compare without spaces so "midjourney" matches "mid" + "-journey" and "11 labs" matches "11labs";
    # the cue must start at a word and may end inside one ("plan" matches "plans").
    target = _norm(cue).replace(" ", "")
    norm = [_norm(w["w"]).replace(" ", "") for w in words]
    for i in range(len(words)):
        if not norm[i] or not target.startswith(norm[i][: len(target)]):
            continue
        joined = ""
        for w in norm[i:i + 6]:
            joined += w
            if len(joined) >= len(target):
                break
        if joined.startswith(target):
            return _snap(words[i]["start"], load_json(path).get("onsets", []))
    raise UsageError(f"cue {cue!r} is not in the transcript; use words exactly as spoken or pass start")


# ------------------------------------------------------------------------------------------- logos
# Simple Icons (CC0 SVG brand icons with official colours), pinned, through jsDelivr; the site's favicon
# is the fallback. Items found by neither stay text chips.
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0"
SLUG_CHARS = {"+": "plus", ".": "dot", "&": "and", "đ": "d", "ħ": "h", "ı": "i", "ĸ": "k", "ŀ": "l", "ł": "l",
              "ß": "ss", "ŧ": "t"}


def _get(url, limit=4_000_000):
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "reel-effects/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read(limit + 1)
    if len(data) > limit:
        raise ValueError("response too large")
    return data


def _slug(title):
    import unicodedata

    s = "".join(SLUG_CHARS.get(c, c) for c in title.lower())
    s = unicodedata.normalize("NFD", s)
    return re.sub(r"[^a-z0-9]", "", s)


def cmd_logos(a):
    """Find a logo for each item: Simple Icons by brand name, else the brand site's favicon."""
    W = os.path.abspath(a.W)
    try:
        items = json.loads(a.items)
    except json.JSONDecodeError as e:
        raise UsageError(f"--items is not JSON: {e}") from e
    if not isinstance(items, dict) or not items or len(items) > 12:
        raise UsageError('--items must map 1-12 item names to {"brand": ..., "domain": ...}')
    icons = json.loads(_get(f"{SIMPLE_ICONS}/_data/simple-icons.json"))
    icons = icons.get("icons", icons) if isinstance(icons, dict) else icons
    by_slug = {i.get("slug") or _slug(i["title"]): i for i in icons}
    by_title = {_slug(i["title"]): i for i in icons}
    out_dir = os.path.join(W, "logos")
    os.makedirs(out_dir, exist_ok=True)
    found, report = {}, {}
    for n, (name, hint) in enumerate(items.items()):
        hint = hint if isinstance(hint, dict) else {}
        brand, domain = str(hint.get("brand") or name), str(hint.get("domain") or "")
        if domain and not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", domain.lower()):
            raise UsageError(f"{name}: domain must look like example.com")
        icon = by_slug.get(_slug(brand)) or by_title.get(_slug(brand)) or by_title.get(_slug(name))
        rel = None
        if icon:
            slug = icon.get("slug") or _slug(icon["title"])
            try:
                svg = _get(f"{SIMPLE_ICONS}/icons/{slug}.svg").decode()
                # Brand colour, unless it is too light to read on the white tile.
                hexc = icon.get("hex", "000000")
                r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
                fill = "#111111" if 0.299 * r + 0.587 * g + 0.114 * b > 200 else f"#{hexc}"
                svg = svg.replace("<svg ", f'<svg width="256" height="256" fill="{fill}" ', 1)
                rel = f"logos/{n:02d}.svg"
                with open(os.path.join(W, rel), "w", encoding="utf-8") as fh:
                    fh.write(svg)
                report[name] = f"simple-icons:{slug}"
            except Exception:  # noqa: BLE001 - fall through to the favicon
                rel = None
        if not rel and domain:
            try:
                from io import BytesIO

                from PIL import Image

                data = _get(f"https://www.google.com/s2/favicons?domain={domain}&sz=256")
                with Image.open(BytesIO(data)) as im:
                    if min(im.size) >= 64:  # tiny favicons look worse than a clean text chip
                        rel = f"logos/{n:02d}.png"
                        im.convert("RGBA").save(os.path.join(W, rel))
                        report[name] = f"favicon:{domain} {im.size[0]}px"
            except Exception:  # noqa: BLE001 - stays a text chip
                rel = None
        if rel:
            found[name] = rel
        else:
            report[name] = "not found: text chip"
    save_json(os.path.join(W, "logos.json"), found)
    print(json.dumps(report, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------------------------------- params
def _coerce(name, spec, value):
    kind = spec["type"]
    if kind == "str":
        if not isinstance(value, str) or not (value.strip() or spec.get("allow_empty")):
            raise UsageError(f"{name} must be a non-empty string")
        value = value.strip()
        if len(value) > spec.get("max_len", 200):
            raise UsageError(f"{name} is longer than {spec['max_len']} characters")
        return value
    if kind == "amount":
        # Same grammar as EffectKit.parseAmount: optional prefix, number, optional K/M/B, optional suffix.
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            value = f"{value:,}"
        if not (isinstance(value, str) and len(value) <= 16 and AMOUNT_RE.match(value.strip())):
            raise UsageError(f"{name} must be a number such as 1,204 or 412K")
        return value.strip()
    if kind == "items":
        # Tier-list entries in speaking order: [{"name": "Claude", "tier": "S", "cue": "Claude"}, ...].
        if not isinstance(value, list) or not 1 <= len(value) <= 12:
            raise UsageError(f"{name} must be a list of 1 to 12 items")
        out, per_tier = [], {}
        for i, it in enumerate(value):
            if not isinstance(it, dict) or set(it) - {"name", "tier", "cue", "start"}:
                raise UsageError(f"{name}[{i}] must be {{name, tier, cue | start}}")
            item = {"name": _coerce(f"{name}[{i}].name", {"type": "str", "max_len": 18}, it.get("name")),
                    "tier": str(it.get("tier", "")).strip()}
            per_tier[item["tier"]] = per_tier.get(item["tier"], 0) + 1
            if per_tier[item["tier"]] > 4:
                raise UsageError(f"row {item['tier']} has more than 4 items")
            for k in ("cue", "start"):
                if it.get(k) is not None:
                    item[k] = _coerce(f"{name}[{i}].{k}", TIMING[k], it[k])
            out.append(item)
        return out
    if kind == "rows":
        # Row labels top to bottom, as the speaker says them: letters, numbers or short words; S-D by default.
        if not (isinstance(value, list) and 1 <= len(value) <= 8
                and all(isinstance(r, (str, int)) and 0 < len(str(r).strip()) <= 6 for r in value)):
            raise UsageError(f"{name} must be 1 to 8 labels of up to 6 characters")
        rows = [str(r).strip() for r in value]
        if len(set(rows)) != len(rows):
            raise UsageError(f"{name} has duplicate labels")
        return rows
    if kind == "logos":
        # {"Claude": "logos/claude.png"}: image files inside the workspace, keyed by item name.
        if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
            raise UsageError(f"{name} must map item names to image paths inside the workspace")
        return value
    if kind == "enum":
        if value not in spec["choices"]:
            raise UsageError(f"{name} must be one of {', '.join(spec['choices'])}")
        return value
    if kind == "color":
        if not (isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value)):
            raise UsageError(f"{name} must be #RRGGBB")
        return value
    if kind == "bool":
        if not isinstance(value, bool):
            raise UsageError(f"{name} must be true or false")
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UsageError(f"{name} must be a number")
    value = int(round(value)) if kind == "int" else float(value)
    if value < spec.get("min", value) or value > spec.get("max", value):
        raise UsageError(f"{name} must be between {spec.get('min')} and {spec.get('max')}")
    return value


def specs_for(effect):
    """(moment specs, global specs) for an effect; moment specs include timing and length."""
    if effect not in EFFECTS:
        raise UsageError(f"unknown effect {effect!r}; available: {', '.join(EFFECTS)}")
    e = EFFECTS[effect]
    g = {**e["global"], **GLOBAL_COMMON}
    if "moment" not in e:
        return None, g
    default, lo, hi = e["seconds"]
    return {**e["moment"], **TIMING, "seconds": {"type": "float", "default": default, "min": lo, "max": hi}}, g


def _fill(prefix, specs, raw):
    unknown = sorted(set(raw) - set(specs))
    if unknown:
        raise UsageError(f"unknown parameter(s) {prefix}: {', '.join(unknown)}")
    out = {}
    for name, spec in specs.items():
        if raw.get(name) is not None:
            out[name] = _coerce(f"{prefix}{name}", spec, raw[name])
        elif spec.get("required"):
            raise UsageError(f"missing {prefix}{name}")
        else:
            out[name] = spec.get("default")
    return out


def resolve_params(effect, raw):
    """{"global": {...}, "moments": [...]} from either {"moments": [...], ...} or one flat moment."""
    mspecs, gspecs = specs_for(effect)
    raw = dict(raw)
    if mspecs is None:
        return {"global": _fill("", gspecs, raw), "moments": []}
    moments = raw.pop("moments", None)
    if moments is None:
        moments = [{k: raw.pop(k) for k in list(raw) if k in mspecs}]
    elif any(k in mspecs for k in raw):
        raise UsageError("with `moments`, put per-moment values inside each moment")
    limit = EFFECTS[effect]["max_moments"]
    if not isinstance(moments, list) or not 1 <= len(moments) <= limit:
        raise UsageError(f"{effect} takes 1 to {limit} moments")
    out = [_fill(f"moments[{i}].", mspecs, m if isinstance(m, dict) else {}) for i, m in enumerate(moments)]
    return {"global": _fill("", gspecs, raw), "moments": out}


def head_top(W, first, count):
    """Median top row of the person over a frame window, from the prepared mattes."""
    from PIL import Image

    tops = []
    for f in range(first, first + count, max(1, count // 12)):
        path = os.path.join(W, "mattes", CLIP, f"{f:05d}.png")
        if not os.path.isfile(path):
            continue
        with Image.open(path) as im:
            alpha = im.getchannel("A").point(lambda v: 255 if v > 128 else 0)
            box = alpha.getbbox()
            if box:
                tops.append(box[1] * HEIGHT / im.height)
    if not tops:
        raise UsageError("no person found in the mattes; check the matte")
    tops.sort()
    return tops[len(tops) // 2]


def _phrases(W, max_words):
    """Transcript words grouped into short caption phrases (frames), split on punctuation and pauses."""
    path = os.path.join(W, "transcript.json")
    words = load_json(path)["words"] if os.path.isfile(path) else []
    n = frame_count(W)
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        text = " ".join(x["w"] for x in cur)
        if (nxt is None or len(cur) >= max_words or len(text) >= 18 or w["w"][-1:] in ".,?!:;"
                or nxt["start"] - w["end"] > 0.35):
            f0 = int(round(cur[0]["start"] * FPS))
            f1 = int(round((nxt["start"] if nxt and nxt["start"] - w["end"] < 0.6 else w["end"] + 0.25) * FPS))
            out.append({"f0": f0, "f1": min(max(f1, f0 + 6), n),
                        "words": [{"w": x["w"].strip(".,?!:;"), "f0": int(round(x["start"] * FPS)),
                                   "f1": int(round(x["end"] * FPS))} for x in cur]})
            cur = []
    return [p for p in out if p["f0"] < n]


def _at(W, item):
    """Frame where a moment or item starts: its cue in the transcript, else `start` seconds."""
    if item.get("cue"):
        return max(0, int(round((cue_time(W, item["cue"]) - CUE_LEAD) * FPS)))
    if item.get("start") is not None:
        return int(round(item["start"] * FPS))
    raise UsageError("every moment needs `cue` (words as spoken) or `start` (seconds)")


def _windows(W, moments, n, min_frames):
    """Moment windows on the clip, in time order; a moment is shortened when the next one starts early."""
    timed = sorted(((_at(W, m), int(round(m["seconds"] * FPS)), m) for m in moments), key=lambda x: x[0])
    out = []
    for i, (f0, length, m) in enumerate(timed):
        end = min(f0 + length, n, timed[i + 1][0] if i + 1 < len(timed) else n)
        if end - f0 < min_frames:
            raise UsageError(f"moment at {f0 / FPS:.2f}s has only {(end - f0) / FPS:.2f}s before the next one or the "
                             "end; drop a moment or move its cue")
        out.append((f0, end - f0, m))
    return out


# ------------------------------------------------------------------------------------------- sound + camera
# Per category: level (dB) after matching each file's loudness to SFX_REF_DB. Speech stays on top.
SFX_LEVEL = {"whoosh": -10, "longwhoosh": -11, "hit": -9, "ui_blip": -13, "flash": -8, "type": -18,
             "riser": -12, "dataswish": -12}
SFX_REF_DB = -14.0


def _events(effect, page):
    """Sound cues [{f, cat}] and camera hits [{f, k}] (k = punch/shake strength 0-1) for a built page."""
    sfx, hits = [], []
    if effect == "tier-list":
        sfx.append({"f": page["panel_f0"], "cat": "whoosh"})
        for it in page["items"]:
            sfx.append({"f": it["f"] + 3, "cat": "ui_blip"})  # the chip lands ~3 frames after it starts
            hits.append({"f": it["f"] + 3, "k": 0.25})
        last = max(it["f"] for it in page["items"]) + 6
        sfx.append({"f": last, "cat": "flash"})
        hits.append({"f": last, "k": 0.45})
        return sfx, hits
    for m in page.get("moments", []):  # captions have no moments: no cues
        f0, n = m["f0"], m["n"]
        if effect == "text-behind":
            sfx += [{"f": f0, "cat": "whoosh"}, {"f": f0 + round(n * 10 / 90), "cat": "hit"}]
            hits.append({"f": f0 + round(n * 10 / 90), "k": 0.55})
        elif effect == "freeze-frame":
            freeze = f0 + round(15 * n / 90)
            sfx += [{"f": freeze, "cat": "flash"}, {"f": f0 + round(60 * n / 90), "cat": "dataswish"}]
            hits.append({"f": freeze, "k": 1.0})
        elif effect == "glass-graph":
            s = n / 90
            sfx.append({"f": f0, "cat": "whoosh"})
            sfx += [{"f": f0 + round(8 * s) + i, "cat": "type"} for i in range(0, round(48 * s), 5)]
            sfx.append({"f": f0 + round(60 * s), "cat": "hit"})
            hits += [{"f": f0 + round(8 * s), "k": 0.3}, {"f": f0 + round(60 * s), "k": 0.45}]
        elif effect == "over-the-shoulder":
            s = n / 84
            sfx += [{"f": f0 + round(5 * s), "cat": "longwhoosh"}, {"f": f0 + round(10 * s), "cat": "ui_blip"},
                    {"f": f0 + round(27 * s), "cat": "whoosh"}, {"f": f0 + round(40 * s), "cat": "ui_blip"}]
        elif effect == "grade-wipe":
            sfx += [{"f": f0 + round(25 * n / 90), "cat": "longwhoosh"}, {"f": f0 + round(45 * n / 90), "cat": "flash"}]
            hits.append({"f": f0 + round(45 * n / 90), "k": 0.3})
    return sfx, hits


def _sfx_mix(W, page, out_audio):
    """Speech plus the page's sound cues, each file's onset on its frame; writes a WAV or returns None."""
    clip = os.path.join(W, "src", "clip.mp4")
    duration = page["frames"] / FPS
    lib = load_json(os.path.join(HERE, "sfx", "catalog.json"))["sounds"]
    by_cat = {}
    for snd in lib:
        by_cat.setdefault(snd["cat"], []).append(snd)
    inputs = ["-i", clip] if has_audio(clip) else ["-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    chains, labels, used = [], [], {}
    for i, cue in enumerate(c for c in page.get("sfx", []) if c["cat"] in by_cat):
        pool = by_cat[cue["cat"]]
        snd = pool[used.get(cue["cat"], 0) % len(pool)]  # a different file each time within a category
        used[cue["cat"]] = used.get(cue["cat"], 0) + 1
        delay = max(0, int(round((cue["f"] / FPS - snd["onset"]) * 1000)))
        gain = SFX_LEVEL[cue["cat"]] + max(-10.0, min(10.0, SFX_REF_DB - snd["rms_db"]))
        inputs += ["-i", os.path.join(HERE, "sfx", snd["file"])]
        k = len(labels) + 1
        chains.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.1f}dB,"
                      f"adelay={delay}|{delay}[s{k}]")
        labels.append(f"[s{k}]")
    if not labels:
        return None
    fc = (";".join(chains) + f";[0:a]aresample=48000,aformat=channel_layouts=stereo[v];[v]{''.join(labels)}"
          f"amix=inputs={len(labels) + 1}:normalize=0:duration=first,"
          f"alimiter=limit=0.89:attack=1:release=40:level=disabled,apad,atrim=0:{duration:.3f}[a]")
    ffmpeg(*inputs, "-filter_complex", fc, "-map", "[a]", "-c:a", "pcm_s16le", out_audio)
    return out_audio


# ------------------------------------------------------------------------------------------- build
def cmd_build(a):
    W = os.path.abspath(a.W)
    try:
        raw = json.loads(a.params)
    except json.JSONDecodeError as e:
        raise UsageError(f"--params is not JSON: {e}") from e
    if not isinstance(raw, dict):
        raise UsageError("--params must be a JSON object")
    effect = EFFECTS[a.effect]
    p = resolve_params(a.effect, raw)
    g = p["global"]
    n = frame_count(W)
    if not n:
        raise UsageError("no plates: run `prepare` (or `link`) first")
    has_mattes = bool(glob.glob(os.path.join(W, "mattes", CLIP, "*.png")))
    if effect["needs_matte"] and not has_mattes:
        raise UsageError(f"{a.effect} draws behind the person: run `prepare` with --matte first")
    page = {"effect": a.effect, "width": WIDTH, "height": HEIGHT, "fps": FPS, "frames": n,
            "plate": f"../plates/{CLIP}/%05d.jpg", "safe_left": SAFE_LEFT, "safe_right": SAFE_RIGHT}
    if effect["needs_matte"]:
        page["alpha"] = f"../mattes/{CLIP}/%05d.png"

    def below_face(override, offset, default, lo, hi):
        """A y below the face over the whole clip: explicit, else head top + offset (mattes), else a default."""
        if override is not None:
            return override
        if not has_mattes:
            return default
        return int(min(hi, max(lo, head_top(W, 0, n) + offset)))

    motion = os.path.join(W, "motion")
    shutil.rmtree(motion, ignore_errors=True)
    os.makedirs(os.path.join(motion, "fonts"))
    report = []
    look = STYLES[g["style"]]
    page.update(style=g["style"], accent=look["accent"], panel=look["panel"], tag=look["tag"])
    if a.effect == "captions":
        phrases = _phrases(W, g["max_words"])
        if not phrases:
            raise UsageError("captions need speech: run `transcribe` first (no words were found)")
        page.update(phrases=phrases, look=g["look"], color=g["color"] or look["accent"], upper=g["upper"], y=g["y"],
                    window=[phrases[0]["f0"], phrases[-1]["f1"]])
        report = [f"{p['f0'] / FPS:.2f}s " + " ".join(w["w"] for w in p["words"]) for p in phrases]
    elif a.effect == "tier-list":
        rows = g["rows"] or list(TIERS)
        for it in g["items"]:
            if it["tier"] not in rows:
                raise UsageError(f"{it['name']}: tier {it['tier']!r} is not one of the rows {', '.join(rows)}")
        items = sorted(({**it, "f": _at(W, it)} for it in g["items"]), key=lambda it: it["f"])
        for prev, it in zip(items, items[1:]):  # items said in one breath still land one after another
            it["f"] = max(it["f"], prev["f"] + 4)
        f0 = max(0, items[0]["f"] - 12)
        f1 = min(n, items[-1]["f"] + 12 + int(round(g["hold"] * FPS)))
        if items[-1]["f"] >= n:
            raise UsageError("an item lands after the end of the clip")
        logos = {}
        # Logos the user supplied win; otherwise the ones `effects.py logos` found.
        auto = os.path.join(W, "logos.json")
        source = g["logos"] if g["logos"] is not None else (load_json(auto) if os.path.isfile(auto) else {})
        for name, rel in source.items():
            src = os.path.realpath(os.path.join(W, rel))
            if not src.startswith(os.path.realpath(W) + os.sep) or not os.path.isfile(src):
                raise UsageError(f"logo for {name!r} not found inside the workspace: {rel}")
            dst = f"logos/{len(logos):02d}{os.path.splitext(src)[1].lower()}"
            os.makedirs(os.path.join(motion, "logos"), exist_ok=True)
            shutil.copyfile(src, os.path.join(motion, dst))
            logos[name] = dst
        # The panel is ~640 px tall; keep it below the face and above the caption area.
        page.update(topic=g["topic"], rows=rows, logos=logos, panel_f0=f0, panel_f1=f1,
                    items=[{"name": it["name"], "tier": it["tier"], "f": it["f"]} for it in items],
                    panel_top=below_face(g["panel_top"], 520, 940, 700, 1000), window=[f0, f1])
        report = [f"{it['name']} -> {it['tier']} at {it['f'] / FPS:.2f}s" for it in items]
    else:
        wins = _windows(W, p["moments"], n, FPS)
        moments = []
        for f0, length, m in wins:
            mm = {"f0": f0, "n": length}
            if a.effect == "text-behind":
                # The word's centre sits a little below the top of the head, so the head covers its lower part.
                top = g["head_y"] if g["head_y"] is not None else head_top(W, f0, length) + 0.28 * g["font_px"]
                mm.update(word=m["word"].upper(), head_y=round(top))
            elif a.effect == "over-the-shoulder":
                mm.update(before_label=m["before_label"].upper(), before_value=m["before_value"],
                          after_label=m["after_label"].upper(), after_value=m["after_value"])
            elif a.effect == "glass-graph":
                mm.update(title=m["title"], from_value=m["from_value"], to_value=m["to_value"])
            elif a.effect == "freeze-frame":
                mm.update(name=m["name"], role=m["role"].upper())
            moments.append(mm)
            label = next((str(v) for k, v in m.items() if k in effect["moment"] and v), "")
            report.append(f"{f0 / FPS:.2f}-{(f0 + length) / FPS:.2f}s {label}".rstrip())
        page["moments"] = moments
        page["window"] = [wins[0][0], wins[-1][0] + wins[-1][1]]
        if a.effect == "text-behind":
            page.update(color=g["color"], font_px=g["font_px"])
        elif a.effect == "over-the-shoulder":
            # Cards just above the shoulder line, beside the head.
            page["card_y"] = below_face(g["card_y"], 250, 760, 300, 1400)
        elif a.effect == "glass-graph":
            # 520 px card at chest height; its bottom stays above the caption area.
            page.update(color=g["color"] if g["color"] != "#D97757" else look["accent"], card_top=below_face(g["card_top"], 560, 1000, 700, 1260))
        elif a.effect == "freeze-frame":
            page["tag_y"] = below_face(g["tag_y"], 640, 1240, 900, 1560)
        else:
            page.update(labels={"before": g["before_label"], "after": g["after_label"]} if g["labels"] else None,
                        keep_after=g["keep_after"], warmth=g["warmth"], teal=g["teal"], vignette=g["vignette"])

    templates = os.path.join(HERE, "templates")
    shutil.copyfile(os.path.join(templates, f"{a.effect}.html"), os.path.join(motion, "index.html"))
    shutil.copyfile(os.path.join(templates, "effect-kit.js"), os.path.join(motion, "effect-kit.js"))
    font = effect["font"]
    shutil.copyfile(os.path.join(HERE, "fonts", font),
                    os.path.join(motion, "fonts", "display.ttf" if font.startswith("League") else "ui.ttf"))
    sfx, hits = _events(a.effect, page)
    page["sfx"] = [c for c in sfx if 0 <= c["f"] < n]
    page["hits"] = [h for h in hits if 0 <= h["f"] < n]
    if has_mattes:
        # Punch-ins zoom toward the head, not the frame centre.
        page["hit_center"] = [WIDTH / 2, round(head_top(W, 0, n) + 160)]
    save_json(os.path.join(motion, "params.json"), page)
    print(json.dumps({"effect": a.effect, "frames": n, "moments": report, "sounds": len(page["sfx"]),
                      "camera_hits": len(page["hits"])}, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------------------------------- render
def _capture(W, out_dir, frames, jobs):
    """Render frames with `jobs` parallel render.mjs processes."""
    os.makedirs(out_dir, exist_ok=True)
    chunks = [frames[i::jobs] for i in range(jobs)] if len(frames) < 64 else [
        frames[i * len(frames) // jobs:(i + 1) * len(frames) // jobs] for i in range(jobs)]
    procs = []
    for chunk in filter(None, chunks):
        contiguous = chunk == list(range(chunk[0], chunk[-1] + 1))
        spec = f"{chunk[0]}:{chunk[-1] + 1}" if contiguous else ",".join(map(str, chunk))
        procs.append(subprocess.Popen(["node", os.path.join(HERE, "render.mjs"), W, out_dir, spec],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
    errors = [p.communicate()[1].strip() for p in procs if p.wait() != 0]
    if errors:
        raise UsageError("render failed: " + errors[0][-800:])


def _sheet(paths, labels, out):
    from PIL import Image, ImageDraw

    tw, th = 270, 480
    sheet = Image.new("RGB", (tw * len(paths), th), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for i, (path, label) in enumerate(zip(paths, labels)):
        with Image.open(path) as im:
            sheet.paste(im.convert("RGB").resize((tw, th)), (i * tw, 0))
        draw.rectangle([i * tw, th - 26, i * tw + 110, th], fill=(0, 0, 0))
        draw.text((i * tw + 6, th - 22), label, fill=(255, 220, 0))
    sheet.save(out, quality=85)


def _times_to_frames(spec, n):
    frames = []
    for item in spec.split(","):
        item = item.strip()
        f = int(round(float(item[:-1]) * FPS)) if item.endswith("s") else int(item)
        frames.append(min(max(f, 0), n - 1))
    return frames


def cmd_render(a):
    W = os.path.abspath(a.W)
    params = os.path.join(W, "motion", "params.json")
    if not os.path.isfile(params):
        raise UsageError("run `build` first")
    page = load_json(params)
    n = page["frames"]
    if a.stills:
        frames = _times_to_frames(a.stills, n)
        qa = os.path.join(W, "qa")
        shutil.rmtree(qa, ignore_errors=True)
        _capture(W, qa, sorted(set(frames)), min(a.jobs, len(frames)))
        _sheet([os.path.join(qa, f"{f:05d}.jpg") for f in frames], [f"f{f} {f / FPS:.2f}s" for f in frames],
               os.path.join(qa, "stills.jpg"))
        print(json.dumps({"stills": "qa/stills.jpg", "frames": frames}))
        return
    frames_dir = os.path.join(W, "frames")
    shutil.rmtree(frames_dir, ignore_errors=True)
    _capture(W, frames_dir, list(range(n)), a.jobs)
    os.makedirs(os.path.join(W, "out"), exist_ok=True)
    out = os.path.join(W, "out", f"{page['effect']}.mp4")
    clip = os.path.join(W, "src", "clip.mp4")
    mixed = None if a.no_sfx else _sfx_mix(W, page, os.path.join(W, "out", "audio.wav"))
    if mixed:
        audio = ["-i", mixed, "-map", "1:a:0", "-c:a", "aac", "-b:a", "256k"]
    elif has_audio(clip):
        audio = ["-i", clip, "-map", "1:a:0", "-c:a", "aac", "-b:a", "256k"]
    else:
        audio = []
    vf = FROM_FRAMES + ("" if a.no_finish else "," + FINISH) + ",format=yuv420p"
    # Exact frame count; audio is cut to the same length (never -shortest).
    ffmpeg("-framerate", str(FPS), "-start_number", "0", "-i", os.path.join(frames_dir, "%05d.jpg"), *audio,
           "-map", "0:v:0", "-vf", vf, "-frames:v", str(n), "-t", f"{n / FPS:.3f}", "-c:v", "libx264", "-crf", "18",
           *RATE_CAP, "-preset", "medium", *BT709, "-movflags", "+faststart", out)
    shutil.rmtree(frames_dir, ignore_errors=True)
    if mixed:
        os.remove(mixed)
    print(json.dumps({"out": os.path.relpath(out, W), "frames": n, "seconds": round(n / FPS, 2),
                      "sounds": 0 if not mixed else len(page.get("sfx", [])), "finish": not a.no_finish}))


def cmd_effects(_a):
    out = {}
    for name, e in EFFECTS.items():
        mspecs, gspecs = specs_for(name)
        out[name] = {"needs_matte": e["needs_matte"], "max_moments": e.get("max_moments"),
                     "moment": mspecs, "global": gspecs}
    print(json.dumps(out, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="effects.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("prepare", help="normalise the clip (and matte) and extract plates/mattes")
    p.add_argument("W")
    p.add_argument("clip")
    p.add_argument("--matte", help="remove_background output for the same clip (person on black)")
    p.add_argument("--max-seconds", type=float, default=60.0)
    p.add_argument("--clean", type=int, default=4, help="matte speck removal strength (opening iterations)")
    p.set_defaults(fn=cmd_prepare)
    p = sp.add_parser("matte", help="person matte made in the sandbox (no remove_background needed)")
    p.add_argument("W")
    p.add_argument("--step", type=int, default=3, help="segment every Nth frame and blend between them")
    p.add_argument("--clean", type=int, default=4, help="speck removal strength")
    p.set_defaults(fn=cmd_matte)
    p = sp.add_parser("link", help="reuse another workspace's prepared media")
    p.add_argument("W")
    p.add_argument("src")
    p.set_defaults(fn=cmd_link)
    p = sp.add_parser("stack", help="start a workspace from another effect's render (several commands, one video)")
    p.add_argument("W")
    p.add_argument("prev")
    p.set_defaults(fn=cmd_stack)
    p = sp.add_parser("logos", help="find logos for tier-list items (Simple Icons, then the site favicon)")
    p.add_argument("W")
    p.add_argument("--items", required=True, help='{"ChatGPT": {"brand": "OpenAI", "domain": "chatgpt.com"}, ...}')
    p.set_defaults(fn=cmd_logos)
    p = sp.add_parser("transcribe", help="word-timed transcript of the clip")
    p.add_argument("W")
    p.add_argument("--model", default="small")
    p.set_defaults(fn=cmd_transcribe)
    p = sp.add_parser("build", help="write motion/ for one effect")
    p.add_argument("W")
    p.add_argument("effect", choices=sorted(EFFECTS))
    p.add_argument("--params", default="{}", help="JSON object; see `effects.py effects`")
    p.set_defaults(fn=cmd_build)
    p = sp.add_parser("render", help="render stills or the full effect video")
    p.add_argument("W")
    p.add_argument("--stills", help="comma-separated times (1.5s) or frame numbers")
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--no-sfx", action="store_true", help="keep the clip's audio without sound effects")
    p.add_argument("--no-finish", action="store_true",
                   help="skip grain/vignette (for every layer but the last when stacking)")
    p.set_defaults(fn=cmd_render)
    p = sp.add_parser("effects", help="list effects and their parameters")
    p.set_defaults(fn=cmd_effects)
    a = ap.parse_args(argv)
    try:
        a.fn(a)
    except UsageError as e:
        print(f"effects.py: error: {e}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as e:
        print(f"effects.py: error: {' '.join(map(str, e.cmd[:3]))}... exited {e.returncode}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
