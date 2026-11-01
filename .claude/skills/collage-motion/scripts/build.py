"""Collage motion graphic - clean takes, contact sheets, final edit.

Usage:
  python build.py sheet  <run_dir>   # delogo takes/*.mp4 -> clean/, write sheets/<take>.png (1 fps, labelled)
  python build.py render <run_dir>   # plan.json -> final.mp4

plan.json:
{
  "w": 1080, "h": 1920, "fps": 12, "veo_gain": 0.25, "pad": 0.2,
  "music": "audio/music.mp3", "music_gain": 0.18,          # optional
  "beats": [
    {"id": "s01", "vo": "audio/s01.wav", "clip": "s01_a", "in": 0.4, "speed": 1.0,
     "words": [{"text": "NOBODY", "at": 0.2, "len": 1.0, "pos": "top"},
               {"text": "TELLS YOU", "pos": "bottom"}]}
  ]
}
Beat length = VO length + pad. "at"/"len" are seconds inside the beat (default: spread evenly).
"pos": top | mid | bottom (default alternates). "fps" 12 gives the stop-motion step; 0 keeps Veo's.
ffmpeg drawtext segfaults on this machine, so labels are drawn with PIL and overlaid as PNGs.
"""
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "C:/Windows/Fonts/impact.ttf"
YELLOW, INK, PAPER = (255, 224, 0), (24, 24, 24), (244, 240, 230)


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def probe(path, entries, stream=None):
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "default=nw=1:nk=1", str(path)]
    return subprocess.run(cmd, capture_output=True, text=True).stdout.split()


def duration(path):
    return float(probe(path, "format=duration")[0])


def has_audio(path):
    return bool(probe(path, "stream=codec_type", "a"))


def delogo_filter(w, h):
    # Gemini watermark: 1080x1920 -> 855,1695 95x95; 1280x720 -> 1130,570 63x63 (scale for other sizes)
    s = w / 1080 if h > w else w / 1920
    x, y = (855, 1695) if h > w else (1695, 855)
    return f"delogo=x={round(x * s)}:y={round(y * s)}:w={round(95 * s)}:h={round(95 * s)}"


def sheet(run_dir):
    takes = sorted((run_dir / "takes").glob("*.mp4"))
    (run_dir / "clean").mkdir(exist_ok=True)
    (run_dir / "sheets").mkdir(exist_ok=True)
    for take in takes:
        clean = run_dir / "clean" / take.name
        w, h = map(int, probe(take, "stream=width,height", "v:0"))
        if not clean.exists():
            run(["ffmpeg", "-v", "error", "-y", "-i", take, "-vf", delogo_filter(w, h),
                 "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", clean])
        d = duration(clean)
        with tempfile.TemporaryDirectory() as tmp:
            run(["ffmpeg", "-v", "error", "-y", "-i", clean, "-vf", "fps=1,scale=240:-2",
                 Path(tmp) / "f%02d.png"])
            frames = sorted(Path(tmp).glob("f*.png"))
            tw, th = Image.open(frames[0]).size
            cols = 5
            rows = (len(frames) + cols - 1) // cols
            board = Image.new("RGB", (cols * tw, rows * (th + 26)), "white")
            draw = ImageDraw.Draw(board)
            font = ImageFont.truetype(FONT, 20)
            for i, f in enumerate(frames):
                x, y = (i % cols) * tw, (i // cols) * (th + 26)
                board.paste(Image.open(f), (x, y + 26))
                draw.text((x + 6, y + 2), f"{take.stem}  {i:.0f}s", fill="black", font=font)
            board.save(run_dir / "sheets" / f"{take.stem}.png")
        print(f"{take.stem}: {d:.1f}s -> sheets/{take.stem}.png")


def label_png(text, size, out, scale=1.0, seed=0):
    rnd = random.Random(seed)
    font = ImageFont.truetype(FONT, int(size * scale))
    l, t, r, b = font.getbbox(text)
    padx, pady = int(size * 0.35 * scale), int(size * 0.18 * scale)
    card = Image.new("RGBA", (r - l + 2 * padx, b - t + 2 * pady), YELLOW + (255,))
    d = ImageDraw.Draw(card)
    d.text((padx - l, pady - t), text, font=font, fill=INK)
    # stamp texture: knock a few specks out of the ink
    for _ in range(int(card.width * card.height / 900)):
        x, y = rnd.randrange(card.width), rnd.randrange(card.height)
        if card.getpixel((x, y))[:3] == INK:
            d.point((x, y), fill=YELLOW + (255,))
    card = card.rotate(rnd.uniform(-5, 5), expand=True, resample=Image.BICUBIC)
    off = int(size * 0.08)
    canvas = Image.new("RGBA", (card.width + off * 3, card.height + off * 3), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 150))
    shadow.putalpha(card.getchannel("A").point(lambda a: 150 if a else 0))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(off / 2)), (off * 2, off * 2))
    canvas.alpha_composite(card, (off // 2, off // 2))
    canvas.save(out)
    return canvas.size


def render(run_dir):
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    W, H = plan.get("w", 1080), plan.get("h", 1920)
    fps, pad, veo_gain = plan.get("fps", 12), plan.get("pad", 0.2), plan.get("veo_gain", 0.25)
    work = run_dir / "build"
    work.mkdir(exist_ok=True)
    size = int(H * 0.06 if H > W else H * 0.09)
    ys = {"top": 0.16, "mid": 0.45, "bottom": 0.70}
    segs = []
    for n, beat in enumerate(plan["beats"]):
        vo = run_dir / beat["vo"]
        clip = run_dir / "clean" / f"{beat['clip']}.mp4"
        speed, start = beat.get("speed", 1.0), beat.get("in", 0.0)
        d = duration(vo) + pad
        if duration(clip) - start < d * speed:
            print(f"warning {beat['id']}: clip has {duration(clip) - start:.1f}s from in, needs {d * speed:.1f}s - last frame held")
        inputs = ["-ss", f"{start}", "-i", clip, "-i", vo]
        step = f"fps={fps}," if fps else ""
        fc = [f"[0:v]setpts=(PTS-STARTPTS)/{speed},{step}scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},fps=24,tpad=stop_mode=clone:stop_duration=20,trim=duration={d:.3f},setsar=1[v0]"]
        words = beat.get("words", [])
        for i, wd in enumerate(words):
            at = wd.get("at", i * d / max(len(words), 1) + 0.1)
            ln = wd.get("len", min(1.4, d / max(len(words), 1) - 0.1))
            pos = wd.get("pos", ["top", "bottom"][(n + i) % 2])
            seed = hash((beat["id"], i)) & 0xFFFF
            big, small = work / f"{beat['id']}_{i}_a.png", work / f"{beat['id']}_{i}_b.png"
            bw, bh = label_png(wd["text"], size, big, 1.18, seed)
            sw, sh = label_png(wd["text"], size, small, 1.0, seed)
            inputs += ["-loop", "1", "-i", big, "-loop", "1", "-i", small]
            a, b = 2 + 2 * i, 3 + 2 * i
            slap = 2 / 24  # two frames oversized, then it lands
            y = ys.get(pos, 0.45) * H
            fc.append(f"[v{2 * i}][{a}:v]overlay=x={(W - bw) // 2}:y={int(y - bh / 2)}:"
                      f"enable='between(t,{at:.3f},{at + slap:.3f})'[v{2 * i + 1}]")
            fc.append(f"[v{2 * i + 1}][{b}:v]overlay=x={(W - sw) // 2}:y={int(y - sh / 2)}:"
                      f"enable='between(t,{at + slap:.3f},{at + ln:.3f})'[v{2 * i + 2}]")
        vout = f"v{2 * len(words)}"
        if has_audio(clip):
            fc.append(f"[0:a]asetpts=PTS-STARTPTS,atempo={max(speed, 0.5)},volume={veo_gain},apad,"
                      f"atrim=duration={d:.3f}[sfx]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={d:.3f}[sfx]")
        fc.append(f"[1:a]aresample=48000,apad,atrim=duration={d:.3f}[vo]")
        fc.append("[vo][sfx]amix=inputs=2:normalize=0[a]")
        seg = work / f"seg_{n:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
             "-map", f"[{vout}]", "-map", "[a]", "-t", f"{d:.3f}", "-r", "24",
             "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-b:a", "192k", seg])
        segs.append(seg)
        print(f"{beat['id']}: {d:.2f}s")
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in segs), encoding="utf-8")
    joined = work / "joined.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    final = run_dir / "final.mp4"
    total = duration(joined)
    if plan.get("music"):
        g = plan.get("music_gain", 0.18)
        run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-stream_loop", "-1", "-i", run_dir / plan["music"],
             "-filter_complex", f"[1:a]volume={g},atrim=duration={total:.3f},afade=t=out:st={max(total - 1.5, 0):.3f}:d=1.5[m];"
                                f"[0:a][m]amix=inputs=2:normalize=0[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", final])
    else:
        run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-c", "copy", final])
    print(f"final.mp4 {total:.1f}s")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("sheet", "render"):
        sys.exit(__doc__)
    {"sheet": sheet, "render": render}[sys.argv[1]](Path(sys.argv[2]).resolve())
