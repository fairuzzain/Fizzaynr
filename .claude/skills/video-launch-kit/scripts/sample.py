"""Create a small timestamped contact sheet from a finished video."""
import argparse
import io
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageOps


def run(args):
    return subprocess.run(args, check=True, stdout=subprocess.PIPE).stdout


def duration(path):
    data = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "V:0",
                           "-show_entries", "stream=duration:format=duration", "-of", "json", str(path)]))
    streams = data.get("streams", [])
    if not streams:
        raise ValueError("No video stream")
    for field in (streams[0], data.get("format", {})):
        try:
            seconds = float(field.get("duration", 0))
        except (ValueError, TypeError):
            continue
        if math.isfinite(seconds) and seconds > 0:
            return seconds
    raise ValueError("Unknown video duration")


def frame(path, sec, width):
    raw = run(["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", str(sec), "-i", str(path),
               "-map", "0:V:0", "-frames:v", "1", "-vf",
               f"scale={width}:{width}:force_original_aspect_ratio=decrease",
               "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"])
    if not raw:
        raise ValueError("No frame at the requested time")
    return Image.open(io.BytesIO(raw)).convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("output", type=Path, help="Use a new or empty sample folder")
    parser.add_argument("--seconds", type=float, nargs="+", help="1 to 3 targeted timestamps")
    args = parser.parse_args()
    seconds = duration(args.video)
    if args.seconds is None:
        count = 3 if seconds < 30 else 6
        times = [seconds * (0.05 + 0.9*i/(count-1)) for i in range(count)]
    else:
        times = args.seconds
        if not 1 <= len(times) <= 3 or any(not (0 <= t < seconds) for t in times):
            parser.error("Use 1 to 3 timestamps within the video duration.")
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        parser.error("Output folder must be empty")
    cols = min(3, len(times))
    sheet = Image.new("RGB", (cols*384, math.ceil(len(times)/cols)*246), "#141b20")
    drawer = ImageDraw.Draw(sheet)
    manifest = []
    for i,t in enumerate(times):
        try:
            img = frame(args.video, t, 1024)
        except ValueError:
            t = max(0, t - min(1, seconds/2))
            img = frame(args.video, t, 1024)
        name = f"frame-{i+1:02}.jpg"
        img.save(args.output/name, quality=91)
        small = ImageOps.contain(img, (380,212))
        x, y = (i%cols)*384, (i//cols)*246
        sheet.paste(small, (x+(384-small.width)//2, y+(216-small.height)//2))
        drawer.text((x+8,y+221), f"{i+1:02}   {int(t)//60:02}:{int(t)%60:02}", fill="white")
        manifest.append({"file":name, "seconds":round(t,3)})
    sheet.save(args.output/"sheet.jpg", quality=86)
    print(json.dumps({"duration":seconds, "frames":manifest}))


if __name__ == "__main__":
    main()
