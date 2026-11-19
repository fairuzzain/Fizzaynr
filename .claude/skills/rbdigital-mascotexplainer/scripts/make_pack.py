#!/usr/bin/env python3
"""Turn the user's two AI images into a mascot pack (any character).

Step 1 - cut the sheets:
  python make_pack.py cut poses.png mouths.png --out mascot/<name> [--poses think,point,phone,thumbs] [--grid 3x3]
  python make_pack.py cut poses1.png,poses2.png mouths.png --out mascot/<name> --poses think,point,phone,thumbs/wave,shocked,laptop,celebrate
    poses.png  : the poses side by side on solid green (mouth closed); several sheets = comma list, one '/'-group of names per sheet
    mouths.png : 9 mouths in a grid on solid green, order A B C / D E F / G H X (see references/mascot-pack.md)
  -> pose_<name>.png (same scale, head centred, bottom aligned), mouth_A..X.png, mascot.json,
     and anchor_<pose>.png helper images (pose with a labelled pixel grid) - LOOK at them to read the mouth position.

Step 2 - set where the mouth goes (pixels in the pose image), one per pose:
  python make_pack.py anchor mascot/<name> think=512,388,120 point=505,392,118 ...
    cx,cy = centre of the drawn mouth, w = mouth width to draw (≈ the drawn mouth width x 1.1)
    add --no-patch for cute/animal mouth sheets (each mouth sits on its own face-colour patch)
  -> updates mascot.json, samples the skin colour around each mouth (used to paint over the drawn mouth),
     then run mascot_check.py and look at the sheet; repeat step 2 until every mouth sits right.

Keying: background colour is read from the image border (green, magenta, white or any flat colour works).
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SHAPES = list("ABCDEFGHX")


def key(img):
    a = np.asarray(img.convert("RGB")).astype(int)
    h, w, _ = a.shape
    border = np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3), a[:, :4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)])
    bgc = np.median(border, axis=0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2)
    dist = np.sqrt(((a - bgc) ** 2).sum(2))
    if bgc[1] > bgc[0] + 40 and bgc[1] > bgc[2] + 40:  # green screen: key by hue (generators give muted greens + shadows)
        d = g - np.maximum(r, b)
        bg = ((d > 19) & (mx - mn > 42) & (g > 35)) | ((d > 7) & (mx < 120)) | (dist < 40)
    else:
        bg = dist < 38
    from scipy.ndimage import binary_opening, binary_fill_holes, label
    fg = binary_opening(~bg, iterations=2)
    lab, n = label(fg)
    if n > 1:
        sz = np.bincount(lab.ravel())[1:]
        fg = np.isin(lab, 1 + np.where(sz >= 0.02 * sz.max())[0])
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    al = np.asarray(alpha).astype(int)
    out = a.copy()
    if bgc[1] > bgc[0] + 40:
        edge = (al > 0) & (al < 250)
        out[..., 1] = np.where(edge, np.minimum(g, np.maximum(r, b) + 12), g)  # despill
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), al]).astype(np.uint8)), fg


def segments(occ, min_gap):
    segs, s, i, n = [], None, 0, len(occ)
    while i < n:
        if occ[i] and s is None:
            s = i
        if not occ[i] and s is not None:
            j = i
            while j < n and not occ[j]:
                j += 1
            if j - i >= min_gap or j == n:
                segs.append((s, i)); s = None
            i = j
            continue
        i += 1
    if s is not None:
        segs.append((s, n))
    if not segs:
        return []
    big = max(e - b for b, e in segs)
    return [(b, e) for b, e in segs if e - b > 0.2 * big]


def head_cx(rgba):
    al = np.asarray(rgba)[..., 3] > 128
    ys = np.where(al.any(1))[0]
    top = ys[0]
    band = al[top: top + max(4, int(0.22 * (ys[-1] - top)))]
    xs = np.where(band.any(0))[0]
    return (xs[0] + xs[-1]) / 2


def cut_sheet(path, names):
    """Cut one pose sheet into len(names) cropped RGBA figures."""
    rgba, fg = key(Image.open(path))
    segs = segments(fg.any(0), max(10, fg.shape[1] // 90))
    if len(segs) != len(names):
        print(f"WARN {os.path.basename(path)}: found {len(segs)} figures, expected {len(names)} - using equal columns")
        W = fg.shape[1]
        segs = [(int(i * W / len(names)), int((i + 1) * W / len(names))) for i in range(len(names))]
    crops = []
    from scipy.ndimage import label as _label
    for (x0, x1) in segs:
        sub = rgba.crop((x0, 0, x1, rgba.height))
        arr = np.asarray(sub).copy()
        lab, n = _label(arr[..., 3] > 128)
        if n > 1:  # drop slivers of the neighbouring figure
            sz = np.bincount(lab.ravel())[1:]
            keep = np.isin(lab, 1 + np.where(sz >= 0.15 * sz.max())[0])
            near = np.asarray(Image.fromarray(keep.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
            arr[..., 3] = np.where(near, arr[..., 3], 0)
            sub = Image.fromarray(arr)
        bb = sub.getbbox()
        crops.append(sub.crop(bb))
    return crops


def cut(a):
    os.makedirs(a.out, exist_ok=True)
    sheets = a.poses_img.split(",")
    groups = [g.split(",") for g in a.poses.split("/")]
    if len(groups) != len(sheets):
        sys.exit(f"{len(sheets)} pose sheet(s) but {len(groups)} pose group(s) in --poses (separate sheets with '/')")
    names, crops, ref_h = [], [], None
    for path, gnames in zip(sheets, groups):
        cs = cut_sheet(path, gnames)
        med = float(np.median([c.height for c in cs]))
        if ref_h is None:
            ref_h = med
        elif abs(med - ref_h) > 2:  # sheets generated separately: bring them to the scale of sheet 1
            k = ref_h / med
            cs = [c.resize((max(1, round(c.width * k)), max(1, round(c.height * k))), Image.LANCZOS) for c in cs]
            print(f"scaled {os.path.basename(path)} x{k:.3f} to match sheet 1")
        names += gnames
        crops += cs
    # common canvas: same scale (same sheet), head centred, bottoms aligned
    cxs = [head_cx(c) for c in crops]
    half = int(max(max(cx, c.width - cx) for c, cx in zip(crops, cxs))) + 8
    H = max(c.height for c in crops) + 8
    info = {"poses": {}, "mouths": {}, "anchor": {}, "patch": {}, "avatar_pose": names[-1]}
    for name, c, cx in zip(names, crops, cxs):
        canvas = Image.new("RGBA", (2 * half, H), (0, 0, 0, 0))
        canvas.alpha_composite(c, (int(half - cx), H - c.height))
        f = f"pose_{name}.png"
        canvas.save(os.path.join(a.out, f))
        info["poses"][name] = f
        # anchor helper: grid every 50 px with labels
        g = Image.new("RGBA", canvas.size, (241, 239, 235, 255))
        g.alpha_composite(canvas)
        d = ImageDraw.Draw(g)
        for x in range(0, g.width, 50):
            d.line([(x, 0), (x, g.height)], fill=(255, 0, 0, 90) if x % 100 else (255, 0, 0, 170), width=1)
            if x % 100 == 0:
                d.text((x + 2, 2), str(x), fill=(200, 0, 0, 255))
        for y in range(0, g.height, 50):
            d.line([(0, y), (g.width, y)], fill=(0, 0, 255, 90) if y % 100 else (0, 0, 255, 170), width=1)
            if y % 100 == 0:
                d.text((2, y + 2), str(y), fill=(0, 0, 200, 255))
        g.convert("RGB").save(os.path.join(a.out, f"anchor_{name}.png"))
        print(f"pose {name}: {f} {canvas.size}")
    # mouths
    rows, cols = (int(x) for x in a.grid.lower().split("x"))
    mrgba, mfg = key(Image.open(a.mouths_img))
    W, Hm = mrgba.size
    k = 0
    for r in range(rows):
        for cc in range(cols):
            if k >= len(SHAPES):
                break
            cell = mrgba.crop((int(cc * W / cols), int(r * Hm / rows), int((cc + 1) * W / cols), int((r + 1) * Hm / rows)))
            bb = cell.getbbox()
            if not bb:
                print(f"WARN mouth cell {r},{cc} empty")
                k += 1
                continue
            m = cell.crop(bb)
            f = f"mouth_{SHAPES[k]}.png"
            m.save(os.path.join(a.out, f))
            info["mouths"][SHAPES[k]] = f
            k += 1
    # first guess anchors: centre column, ~38% down the head band (Claude refines after looking at anchor_*.png)
    for name in names:
        p = Image.open(os.path.join(a.out, info["poses"][name]))
        al = np.asarray(p)[..., 3] > 128
        ys = np.where(al.any(1))[0]
        top = ys[0]
        info["anchor"][name] = [p.width // 2, int(top + 0.30 * (ys[-1] - top)), int(p.width * 0.12)]
    json.dump(info, open(os.path.join(a.out, "mascot.json"), "w"), indent=1)
    print(f"mouths: {len(info['mouths'])}/9  -> {a.out}/mascot.json (anchors are a GUESS: look at anchor_*.png, then run 'anchor')")


def anchor(a):
    mj = os.path.join(a.pack, "mascot.json")
    info = json.load(open(mj))
    for spec in a.specs:
        name, _, v = spec.partition("=")
        cx, cy, w = (int(float(x)) for x in v.split(","))
        info["anchor"][name] = [cx, cy, w]
        p = np.asarray(Image.open(os.path.join(a.pack, info["poses"][name])).convert("RGBA")).astype(int)
        # skin = median of opaque pixels in a ring left/right of the mouth, above the chin line
        samp = []
        for dx in (-0.85, -0.7, 0.7, 0.85):
            for dy in (-0.25, 0, 0.15):
                x, y = int(cx + dx * w), int(cy + dy * w)
                if 0 <= y < p.shape[0] and 0 <= x < p.shape[1] and p[y, x, 3] > 200:
                    samp.append(p[y, x, :3])
        if a.no_patch:
            info["patch"] = {}
        elif samp:
            s = np.median(np.array(samp), axis=0).astype(int)
            info.setdefault("patch", {})[name] = "#%02X%02X%02X" % tuple(s)
        print(f"{name}: anchor {cx},{cy} w{w} skin {info.get('patch', {}).get(name)}")
    json.dump(info, open(mj, "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cut")
    c.add_argument("poses_img"); c.add_argument("mouths_img")
    c.add_argument("--out", required=True)
    c.add_argument("--poses", default="think,point,phone,thumbs")
    c.add_argument("--grid", default="3x3")
    n = sub.add_parser("anchor")
    n.add_argument("pack"); n.add_argument("specs", nargs="+")
    n.add_argument("--no-patch", action="store_true", help="mouth sprites carry their own face-colour patch (cute/animal mouths): don't paint a skin patch")
    a = ap.parse_args()
    cut(a) if a.cmd == "cut" else anchor(a)


if __name__ == "__main__":
    main()
