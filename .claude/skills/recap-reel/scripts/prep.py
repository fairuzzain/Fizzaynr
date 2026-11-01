"""Turn the user's photos into Nexabot start frames at the reel's aspect.

Usage: python prep.py <run_dir> <photo|folder>... [--aspect 16:9|9:16] [--fit cover|blur] [--gravity 0.4]
Writes <run>/frames/fNN.png (1280x720 or 1080x1920) in the given order and <run>/frames/index.json.
cover = fill and crop (gravity = vertical crop position 0 top .. 1 bottom; 0.4 keeps heads).
blur  = fit the whole photo over a blurred, darkened copy of itself (for photos far off the aspect).
"""
import argparse, json, os, sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp"}


def cover(im, W, H, gravity):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = round((im.height - H) * gravity)
    return im.crop((x, y, x + W, y + H))


def blurfit(im, W, H):
    bg = ImageEnhance.Brightness(cover(im, W, H, 0.5).filter(ImageFilter.GaussianBlur(40))).enhance(0.6)
    s = min(W / im.width, H / im.height)
    fg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("inputs", nargs="+")
    ap.add_argument("--aspect", default="16:9"); ap.add_argument("--fit", default="cover")
    ap.add_argument("--gravity", type=float, default=0.4)
    a = ap.parse_args()
    W, H = (1280, 720) if a.aspect == "16:9" else (1080, 1920)
    files = []
    for p in map(Path, a.inputs):
        files += sorted(f for f in p.iterdir() if f.suffix.lower() in EXT) if p.is_dir() else [p]
    out = Path(a.run) / "frames"; out.mkdir(parents=True, exist_ok=True)
    index = []
    for i, f in enumerate(files, 1):
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        mode = a.fit
        fr = blurfit(im, W, H) if mode == "blur" else cover(im, W, H, a.gravity)
        name = f"f{i:02d}.png"
        fr.save(out / name)
        index.append({"frame": f"frames/{name}", "source": str(f.resolve()), "src_size": [im.width, im.height], "fit": mode})
        print(f"{name} <- {f.name} ({im.width}x{im.height}, {mode})")
    (out / "index.json").write_text(json.dumps({"size": [W, H], "aspect": a.aspect, "frames": index}, indent=1))
    print(f"{len(index)} frames at {W}x{H} in {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
