"""Assemble the final video with ffmpeg (Nexabot clips: the Gemini watermark is removed first).

Usage: python assemble.py <run_dir> [--music path] [--out name.mp4]

  1. Every clip: drop the first TRIM_START seconds, then cut to exactly its on-screen
     window from plan.json (frame-accurate, cumulative, so there is no drift against the
     narration). Short clips are held on the last frame.
  2. Concatenate clips (clip audio kept, turned down to CLIP_AUDIO_VOLUME).
  3. Lay the chapter narrations end to end on top, plus one random track from
     assets/music at MUSIC_VOLUME, looped and faded out.
"""
import argparse
import random
import subprocess
import sys
from pathlib import Path

from common import AUDIO_EXTS, MUSIC_DIR, TRIM_START, env, load_json

FPS = 30


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-3000:]}")


def has_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                        "stream=index", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def video_size(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


def delogo(path):
    """delogo filter for the Gemini watermark of a Nexabot (Veo) clip, as fractions of the frame.
    Portrait box measured on 1080x1920 clips (x 855, y 1695, 95x95); landscape mirrors its margins
    and should be checked on a test clip. Override with WATERMARK_BOX=x,y,w,h (fractions) or 'off'."""
    box = env("WATERMARK_BOX", "")
    if box == "off":
        return ""
    w, h = video_size(path)
    if box:
        fx, fy, fw, fh = map(float, box.split(","))
    elif h > w:
        fx, fy, fw, fh = 855 / 1080, 1695 / 1920, 95 / 1080, 95 / 1920
    else:
        fx, fy, fw, fh = 1695 / 1920, 855 / 1080, 95 / 1920, 95 / 1080
    x, y = int(fx * w), int(fy * h)
    bw, bh = min(int(fw * w), w - x - 1), min(int(fh * h), h - y - 1)
    return f"delogo=x={x}:y={y}:w={bw}:h={bh},"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--music")
    ap.add_argument("--out", default="final.mp4")
    a = ap.parse_args()
    run = Path(a.run_dir)
    plan = load_json(run / "plan.json")
    w, h = (1280, 720) if env("ASPECT_RATIO", "16:9") == "16:9" else (720, 1280)
    clip_vol = env("CLIP_AUDIO_VOLUME", "0.15")
    music_vol = env("MUSIC_VOLUME", "0.12")
    build = run / "build"
    build.mkdir(exist_ok=True)

    # 1. normalise + trim every clip to its exact frame window
    segs, offset = [], 0.0
    for ch in plan["chapters"]:
        for c in ch["clips"]:
            src = run / "clips" / f"{c['id']}.mp4"
            if not src.exists():
                sys.exit(f"missing clip {src} - run generate.py videos first")
            f0 = round((offset + c["start"]) * FPS)
            f1 = round((offset + c["end"]) * FPS)
            frames = f1 - f0
            dur = frames / FPS
            seg = build / f"{c['id']}.mp4"
            # optional plan.json "speed" (0.5-1): play the clip slower so only its clean opening is used
            speed = float(c.get("speed", env("CLIP_SPEED", "1.0")))
            slow = f"setpts=(PTS-STARTPTS)/{speed}," if speed != 1.0 else ""
            vf = (f"{delogo(src) if c.get('delogo', True) else ''}{slow}scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,"
                  f"fps={FPS},tpad=stop_mode=clone:stop_duration=3")
            # optional plan.json "src": where in the 10 s source this clip's window starts (default TRIM_START);
            # pick it from a 1 fps strip so the clip's best action lands on the narration
            cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(c.get("src", TRIM_START)), "-i", str(src)]
            if has_audio(src):
                af = ("aresample=48000,aformat=channel_layouts=stereo,"
                      + (f"atempo={max(speed, 0.5)}," if speed != 1.0 else "") + "apad")
                cmd += ["-vf", vf, "-af", af, "-map", "0:v:0", "-map", "0:a:0"]
            else:
                cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                        "-vf", vf, "-map", "0:v:0", "-map", "1:a:0"]
            cmd += ["-frames:v", str(frames), "-t", f"{dur:.4f}", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    str(seg)]
            sh(cmd)
            segs.append(seg)
        offset += ch["duration"]
    total = offset
    print(f"prepared {len(segs)} clips, total {total:.2f}s")

    # 2. concat clips
    lst = build / "concat.txt"
    lst.write_text("".join(f"file '{s.name}'\n" for s in segs), encoding="utf-8")
    joined = build / "joined.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c", "copy", str(joined)])

    # 3. narration + music mix
    narr = [run / ch["audio"] for ch in plan["chapters"]]
    if a.music:
        music = Path(a.music)
    else:
        tracks = [p for p in MUSIC_DIR.iterdir() if p.suffix.lower() in AUDIO_EXTS] if MUSIC_DIR.exists() else []
        if not tracks:
            sys.exit(f"No music found in {MUSIC_DIR}")
        music = random.choice(tracks)
    print(f"music: {music.name}")

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(joined)]
    for n in narr:
        cmd += ["-i", str(n)]
    cmd += ["-stream_loop", "-1", "-i", str(music)]
    k = len(narr)
    fade_start = max(total - 2.5, 0)
    fc = "".join(f"[{i + 1}:a]aresample=48000,aformat=channel_layouts=stereo[n{i}];" for i in range(k))
    fc += "".join(f"[n{i}]" for i in range(k)) + f"concat=n={k}:v=0:a=1[narr];"
    fc += f"[0:a]volume={clip_vol}[sfx];"
    fc += (f"[{k + 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume={music_vol},"
           f"afade=t=in:d=1,afade=t=out:st={fade_start:.2f}:d=2.5[mus];")
    fc += "[narr][sfx][mus]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[aout]"
    out = run / a.out
    cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[aout]", "-t", f"{total:.3f}",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    sh(cmd)
    print(f"DONE -> {out}")


if __name__ == "__main__":
    main()
