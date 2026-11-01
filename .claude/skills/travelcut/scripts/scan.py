"""Read the trip photos: fix orientation, convert, score, find near-duplicates, make a contact sheet.

Usage: python scan.py <run_dir> <photo|folder>... [--dup 10]
Writes <run>/photos/pNN.jpg (EXIF-upright, sRGB JPEG q95; originals untouched),
<run>/photos/analysis.json and <run>/photos/contact.png (numbered tiles with scores).
HEIC/HEIF/RAW go through ffmpeg (PIL has no HEIC here); if that fails the photo is listed as "unreadable".
Scores: sharp = variance of the Laplacian on a 1200 px copy (higher = sharper; < ~60 is soft),
expo = mean luma 0..1, clip_hi / clip_lo = share of blown / crushed pixels.
Near-duplicates: 64-bit dHash, Hamming <= --dup -> same group; "keep" marks the sharpest of a group.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageOps

PIL_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
FF_EXT = {".heic", ".heif", ".avif", ".dng", ".cr2", ".cr3", ".nef", ".arw", ".raf", ".orf", ".rw2"}


def font(size):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()


def load(path):
    if path.suffix.lower() in PIL_EXT:
        return ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "x.png"
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-frames:v", "1", str(out)], capture_output=True)
        if r.returncode or not out.exists():
            raise RuntimeError(r.stderr.decode(errors="replace")[-300:])
        return Image.open(out).convert("RGB")  # ffmpeg applies the HEIC rotation itself


def dhash(gray):
    s = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
    bits = (s[:, 1:] > s[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("inputs", nargs="+"); ap.add_argument("--dup", type=int, default=10)
    a = ap.parse_args()
    files = []
    for p in map(Path, a.inputs):
        files += sorted(f for f in p.iterdir() if f.suffix.lower() in PIL_EXT | FF_EXT) if p.is_dir() else [p]
    out = Path(a.run) / "photos"; out.mkdir(parents=True, exist_ok=True)
    rows, thumbs = [], []
    for i, f in enumerate(files, 1):
        pid = f"p{i:02d}"
        try:
            im = load(f)
        except Exception as e:
            rows.append({"id": pid, "source": str(f), "unreadable": str(e)}); print(f"{pid} UNREADABLE {f.name}: {e}"); continue
        im.save(out / f"{pid}.jpg", quality=95)
        g = np.asarray(im.convert("L"))
        k = 1200 / max(g.shape)
        gs = cv2.resize(g, None, fx=k, fy=k, interpolation=cv2.INTER_AREA) if k < 1 else g
        row = {"id": pid, "file": f"photos/{pid}.jpg", "source": str(f.resolve()), "size": [im.width, im.height],
               "orient": "portrait" if im.height > im.width else "landscape",
               "sharp": round(float(cv2.Laplacian(gs, cv2.CV_64F).var()), 1),
               "expo": round(float(gs.mean() / 255), 3),
               "clip_hi": round(float((gs > 250).mean()), 3), "clip_lo": round(float((gs < 5).mean()), 3),
               "hash": dhash(gs)}
        rows.append(row)
        t = im.copy(); t.thumbnail((360, 360)); thumbs.append((row, t))
        print(f"{pid} <- {f.name} {im.width}x{im.height} sharp {row['sharp']} expo {row['expo']}")
    ok = [r for r in rows if "hash" in r]
    # near-duplicate groups (union-find on Hamming distance)
    parent = {r["id"]: r["id"] for r in ok}
    def root(x):
        while parent[x] != x: x = parent[x]
        return x
    for i, r in enumerate(ok):
        for s in ok[i + 1:]:
            if bin(r["hash"] ^ s["hash"]).count("1") <= a.dup: parent[root(s["id"])] = root(r["id"])
    groups = {}
    for r in ok: groups.setdefault(root(r["id"]), []).append(r)
    for g in groups.values():
        best = max(g, key=lambda r: r["sharp"])
        for r in g:
            r["group"] = best["id"]; r["keep"] = r is best
            r["hash"] = f"{r['hash']:016x}"
    # contact sheet
    if thumbs:
        cols = 6; tw, th = 360, 400
        sh = Image.new("RGB", (cols * tw, -(-len(thumbs) // cols) * th), (24, 24, 24))
        d = ImageDraw.Draw(sh); f1, f2 = font(26), font(17)
        for i, (r, t) in enumerate(thumbs):
            x, y = (i % cols) * tw, (i // cols) * th
            sh.paste(t, (x + (tw - t.width) // 2, y + (360 - t.height) // 2))
            col = (255, 220, 0) if r["keep"] else (255, 90, 90)
            d.text((x + 6, y + 4), r["id"], fill=col, font=f1)
            tag = f"sharp {r['sharp']:.0f}  expo {r['expo']:.2f}" + ("" if r["keep"] else f"  dup of {r['group']}")
            d.text((x + 6, y + 366), tag, fill=(230, 230, 230), font=f2)
        sh.save(out / "contact.png")
    (out / "analysis.json").write_text(json.dumps({"photos": rows}, indent=1))
    dups = sum(1 for r in ok if not r["keep"])
    print(f"{len(ok)} photos read, {len(rows) - len(ok)} unreadable, {dups} near-duplicates -> {out / 'contact.png'}", file=sys.stderr)


if __name__ == "__main__":
    main()
