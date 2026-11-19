#!/usr/bin/env python3
"""
make_captions.py — TikTok/IG-safe .ass subtitles for UGC clips + ffmpeg burn command.
Animation tags mirror Higgsfield capsmith's production renderer (same \\t/\\fad math).

Default: plain captions — each phrase simply appears on its timestamp. Big, bold,
Metropolis, white with black outline, locked inside TikTok/Instagram safe zones.
Animations and fonts are OPT-IN flags.

Usage:
    python3 make_captions.py script.json                       -> plain captions
    python3 make_captions.py script.json --anim pop            -> entrance animation
    python3 make_captions.py script.json --font "Montserrat"   -> font override
    python3 make_captions.py script.json --size 100            -> bigger text (auto-fit still applies)
    python3 make_captions.py script.json --no-caps             -> natural case (no uppercasing)

Animations (--anim): none (default) | fade | pop | bounce | slide-up | slide-down |
                     zoom-out | flip | blur-in | shake | stretch

Fonts: default "Metropolis" (Unlicense, bundled in ./fonts — the printed command
includes fontsdir=fonts). Any other installed font works via --font; Montserrat
(also bundled, OFL) is the secondary option.

Input JSON:
{
  "video": "clip.mp4",
  "style": {                            // optional overrides (same keys as flags)
    "font": "Metropolis",
    "size": 88,                         // px at 1080x1920; auto-shrinks if a line is too wide
    "fill": "&H00FFFFFF",               // ASS BGR: white
    "outline_color": "&H00000000",      // black
    "outline": 5,
    "margin_v": 620,                    // px from bottom; clamped to >=320 (safe zone)
    "caps": true,
    "anim": "none"
  },
  "segments": [
    {"start": 0.0, "end": 1.5, "text": "that almost died and so did I"},
    {"start": 1.9, "end": 4.6, "text": "I wasn't gonna post this"}
  ]
}

Safe zones baked in (1080x1920): bottom >=320px kept clear (TikTok/IG UI + captions bar),
side margins 80px, top 10% never reached. Max 2 lines; the longest line auto-shrinks the
font so text NEVER crosses the side margins (fitSize, k=0.58 avg glyph width).
"""

import json, argparse, pathlib

PLAY_W, PLAY_H = 1080, 1920
MARGIN_X = 80                 # side margins, px
MIN_MARGIN_V = 320            # hard floor: bottom ~17% stays clear (TikTok/IG UI)
GLYPH_K = 0.58                # avg glyph width in em (capsmith fitSize)

DEF_STYLE = {
    "font": "Metropolis", "size": 88,
    "fill": "&H00FFFFFF", "outline_color": "&H00000000", "outline": 6,
    "margin_v": 620, "caps": True, "anim": "none",
}

# ASS entrance tags — 1:1 with capsmith's production build_ass()
ANIM_TAGS = {
    "none": "",
    "fade": "{\\fad(220,0)}",
    "pop": "{\\fscx60\\fscy60\\t(0,160,\\fscx100\\fscy100)}",
    "bounce": "{\\fscx30\\fscy30\\t(0,200,\\fscx112\\fscy112)\\t(200,340,\\fscx100\\fscy100)}",
    "zoom-out": "{\\fscx140\\fscy140\\t(0,180,\\fscx100\\fscy100)\\fad(110,0)}",
    "flip": "{\\fscy10\\t(0,200,\\fscy100)\\fad(80,0)}",
    "blur-in": "{\\blur12\\t(0,220,\\blur0)\\fad(110,0)}",
    "shake": "{\\frz3\\t(0,70,\\frz-3)\\t(70,140,\\frz2)\\t(140,210,\\frz0)\\fad(70,0)}",
    "stretch": "{\\fscx170\\t(0,190,\\fscx100)\\fad(90,0)}",
}

def slide_tags(direction: str, margin_v: int, size: int) -> str:
    x = PLAY_W / 2
    y = PLAY_H - margin_v
    off = size * 0.6
    dx, dy = 0.0, 0.0
    if direction == "slide-up": dy = off
    elif direction == "slide-down": dy = -off
    return f"{{\\move({x + dx:.0f},{y + dy:.0f},{x:.0f},{y:.0f},0,200)\\fad(140,0)}}"

def ts(sec: float) -> str:
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def wrap(text: str, width: int = 16):
    words = text.split()
    if len(" ".join(words)) <= width or len(words) == 1:
        return [" ".join(words)]
    # balanced 2-line split: pick the break that minimizes the longer line
    best, best_len = None, 10**9
    for i in range(1, len(words)):
        l1, l2 = " ".join(words[:i]), " ".join(words[i:])
        m = max(len(l1), len(l2))
        if m < best_len:
            best, best_len = [l1, l2], m
    return best

def fit_size(desired: int, lines) -> int:
    """Shrink font so the longest line fits inside the side margins (capsmith fitSize)."""
    max_w = PLAY_W - 2 * MARGIN_X
    longest = max((len(l) for l in lines), default=1)
    fitted = min(desired, int(max_w / (longest * GLYPH_K)))
    return max(36, fitted)

def build_ass(data: dict, cli_style: dict) -> str:
    st = {**DEF_STYLE, **data.get("style", {}), **{k: v for k, v in cli_style.items() if v is not None}}
    margin_v = max(MIN_MARGIN_V, int(st["margin_v"]))
    anim = st["anim"] if st["anim"] in ANIM_TAGS or str(st["anim"]).startswith("slide") else "none"

    # Pre-wrap all segments, find the global fitted size so every caption matches
    seg_lines = []
    for seg in data["segments"]:
        raw = seg["text"].strip()
        if st["caps"]: raw = raw.upper()
        seg_lines.append((seg, wrap(raw)))
    size = min(fit_size(int(st["size"]), lines) for _, lines in seg_lines) if seg_lines else int(st["size"])

    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {PLAY_W}
PlayResY: {PLAY_H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{st['font']},{size},{st['fill']},{st['fill']},{st['outline_color']},&H96000000,-1,0,0,0,100,100,0,0,1,{st['outline']},0,2,{MARGIN_X},{MARGIN_X},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for seg, lines in seg_lines:
        t0, t1 = float(seg["start"]), float(seg["end"])
        tags = slide_tags(anim, margin_v, size) if str(anim).startswith("slide") else ANIM_TAGS.get(anim, "")
        ev.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Cap,,0,0,0,,{tags}" + "\\N".join(lines))
    return head + "\n".join(ev) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--anim", choices=list(ANIM_TAGS) + ["slide-up", "slide-down"], default=None)
    ap.add_argument("--font", default=None)
    ap.add_argument("--size", type=int, default=None)
    ap.add_argument("--no-caps", action="store_true", help="render captions in natural case (no uppercasing)")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    src = pathlib.Path(a.json_path)
    data = json.loads(src.read_text(encoding="utf-8"))
    out = pathlib.Path(a.out) if a.out else src.with_suffix(".ass")
    out.write_text(build_ass(data, {"anim": a.anim, "font": a.font, "size": a.size, "caps": False if a.no_caps else None}), encoding="utf-8")
    video = data.get("video", "clip.mp4")
    stem = pathlib.Path(video).stem
    print(f"wrote {out}")
    print(f'burn:            ffmpeg -i "{video}" -vf "ass={out.name}" -c:a copy "{stem}_captioned.mp4"')
    print(f'burn w/ fonts:   ffmpeg -i "{video}" -vf "ass={out.name}:fontsdir=fonts" -c:a copy "{stem}_captioned.mp4"')
    print('note: default font is Metropolis (bundled in ./fonts — use the fontsdir command).')

if __name__ == "__main__":
    main()
