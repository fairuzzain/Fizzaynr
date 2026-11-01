"""Clean Nexabot clips and make 1 fps contact sheets for picking each clip's clean range.

Usage: python clean.py <run_dir> [--names c01 c02 ...] [--no-delogo]
Reads <run>/videos/*.mp4 (Nexabot sfv output), removes the Gemini watermark with delogo
BEFORE scaling, writes <run>/clean/<name>.mp4 at the film size (frames/index.json) at the clip's OWN
frame rate (no resampling: real speed, frame for frame), muted (cut.py takes ambience from videos/),
plus <run>/sheets/<name>.png (1 tile per second, labelled) and <run>/sheets/_all.png.
"""
import os
import argparse, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def probe(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", str(p)], capture_output=True, text=True).stdout
    j = json.loads(o)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def delogo_box(w, h):
    # Verified boxes: 1080x1920 -> 855,1695,95,95 ; 1280x720 -> 1130,570,63,63. Others scale from those.
    if h > w:
        k = w / 1080; return round(855 * k), round(1695 * k), round(95 * k), round(95 * k)
    k = w / 1280; return round(1130 * k), round(570 * k), round(63 * k), round(63 * k)


def font(size):
    for f in (*([os.environ["FONT_BOLD"]] if os.environ.get("FONT_BOLD") else []), "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()


def sheet(clip, out, dur, tw=320):
    n = max(1, int(dur))
    tiles = []
    for s in range(n):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{s + 0.5:.2f}", "-i", str(clip), "-frames:v", "1",
                              "-vf", f"scale={tw}:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        if not raw: continue
        from io import BytesIO
        im = Image.open(BytesIO(raw)).convert("RGB")
        d = ImageDraw.Draw(im); f = font(max(14, tw // 14))
        d.rectangle((0, 0, tw // 4, tw // 11), fill=(0, 0, 0)); d.text((4, 1), f"{s}s", fill=(255, 220, 0), font=f)
        tiles.append(im)
    if not tiles: return None
    cols = 5 if tiles[0].width > tiles[0].height else 10
    rows = -(-len(tiles) // cols)
    W, H = tiles[0].size
    sh = Image.new("RGB", (cols * W, rows * H))
    for i, t in enumerate(tiles): sh.paste(t, ((i % cols) * W, (i // cols) * H))
    sh.save(out)
    return sh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("--names", nargs="*"); ap.add_argument("--no-delogo", action="store_true")
    a = ap.parse_args()
    run = Path(a.run)
    W, H = json.loads((run / "frames/index.json").read_text())["size"]
    vids = sorted((run / "videos").glob("*.mp4"))
    if a.names: vids = [v for v in vids if v.stem in a.names]
    (run / "clean").mkdir(exist_ok=True); (run / "sheets").mkdir(exist_ok=True)
    sheets = []
    for v in vids:
        w, h, dur = probe(v)
        vf = [] if a.no_delogo else ["delogo=x=%d:y=%d:w=%d:h=%d" % delogo_box(w, h)]
        vf += [f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}", "setsar=1"]
        out = run / "clean" / v.name
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-vf", ",".join(vf), "-an", "-c:v", "libx264",
                        "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", str(out)], check=True)
        sh = sheet(out, run / "sheets" / f"{v.stem}.png", dur)
        if sh: sheets.append((v.stem, sh))
        print(f"{v.name}: {w}x{h} {dur:.1f}s -> clean/{v.name}")
    if sheets:  # one overview: each clip's sheet scaled to the same width, stacked
        tw = 1600
        rows = [s.resize((tw, round(s.height * tw / s.width))) for _, s in sheets]
        allim = Image.new("RGB", (tw, sum(r.height + 30 for r in rows)), (20, 20, 20))
        y, d, f = 0, None, font(22)
        d = ImageDraw.Draw(allim)
        for (name, _), r in zip(sheets, rows):
            d.text((8, y + 3), name, fill=(255, 255, 255), font=f); allim.paste(r, (0, y + 30)); y += r.height + 30
        allim.save(run / "sheets/_all.png")
        print(f"overview: {run / 'sheets/_all.png'}")


if __name__ == "__main__":
    main()
