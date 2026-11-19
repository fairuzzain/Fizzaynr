#!/usr/bin/env python3
"""Check a PNG mascot pack and draw a preview sheet (every pose x every mouth).

  python mascot_check.py <pack_dir> [--out preview.png]

<pack_dir>/mascot.json:
{
  "poses":  {"think": "pose_think.png", "point": "pose_point.png", "phone": "pose_phone.png", "thumbs": "pose_thumbs.png"},
  "mouths": {"A": "mouth_A.png", "B": "...", "C": "...", "D": "...", "E": "...", "F": "...", "G": "...", "H": "...", "X": "mouth_X.png"},
  "anchor": {"think": [cx, cy, width], ...},     # mouth centre + drawn width, in that pose image's pixels
  "avatar_pose": "thumbs"                          # optional, used in the comment-box avatar
}
"mouths" may instead be per pose: {"think": {"A": "...", ...}, ...}.
Pose PNGs: transparent background, same framing (bottom of the image = bottom of the body).
Mouth PNGs: transparent, the mouth plus a little surrounding skin so it covers the drawn mouth.
Look at the sheet: every mouth must sit exactly on the face in every pose. Adjust "anchor" and re-run.
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw

SHAPES = list("ABCDEFGHX")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack")
    ap.add_argument("--out", default="mascot_preview.png")
    a = ap.parse_args()
    info = json.load(open(os.path.join(a.pack, "mascot.json")))
    problems = []
    poses = info.get("poses", {})
    if not poses:
        sys.exit("no poses in mascot.json")
    per_pose = isinstance(next(iter(info["mouths"].values())), dict)
    rows = []
    for p, f in poses.items():
        img = Image.open(os.path.join(a.pack, f)).convert("RGBA")
        if img.getchannel("A").getextrema()[0] == 255:
            problems.append(f"{f}: no transparency (background not removed)")
        if p not in info.get("anchor", {}):
            problems.append(f"pose {p}: missing anchor")
            continue
        cx, cy, mw = info["anchor"][p]
        mouths = info["mouths"][p] if per_pose else info["mouths"]
        missing = [s for s in SHAPES if s not in mouths]
        if missing:
            problems.append(f"pose {p}: missing mouths {''.join(missing)} (X = rest is required)")
        # crop around the face for the sheet
        box = (int(cx - mw * 1.6), int(cy - mw * 1.3), int(cx + mw * 1.6), int(cy + mw * 1.1))
        cells = []
        for s in SHAPES:
            base = img.copy()
            skin = info.get("patch", {}).get(p)
            if skin:
                pw, ph = mw * 1.25, mw * 0.8
                patch = Image.new("RGBA", base.size, (0, 0, 0, 0))
                ImageDraw.Draw(patch).ellipse([cx - pw * 0.36, cy - ph * 0.36, cx + pw * 0.36, cy + ph * 0.36], fill=skin)
                from PIL import ImageFilter
                base.alpha_composite(patch.filter(ImageFilter.GaussianBlur(max(1, mw * 0.04))))
            if s in mouths:
                m = Image.open(os.path.join(a.pack, mouths[s])).convert("RGBA")
                h = int(m.height * mw / m.width)
                m = m.resize((int(mw), max(1, h)), Image.LANCZOS)
                base.alpha_composite(m, (int(cx - mw / 2), int(cy - h / 2)))
            c = Image.new("RGBA", base.size, (241, 239, 235, 255))
            c.alpha_composite(base)
            c = c.crop(box).resize((220, int(220 * (box[3] - box[1]) / (box[2] - box[0]))))
            d = ImageDraw.Draw(c)
            d.text((6, 4), f"{p}:{s}", fill=(200, 16, 46, 255))
            cells.append(c)
        rows.append(cells)
    if rows:
        cw, ch = rows[0][0].size
        sheet = Image.new("RGB", (cw * len(SHAPES), ch * len(rows)), "white")
        for r, cells in enumerate(rows):
            for c, im in enumerate(cells):
                sheet.paste(im.convert("RGB"), (c * cw, r * ch))
        sheet.save(a.out)
        print(f"sheet: {a.out}")
    for pr in problems:
        print("PROBLEM", pr)
    print("VERDICT:", "FAIL" if problems else "PASS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
