#!/usr/bin/env python3
"""SFX + lo-fi music + final mix for a mascot explainer.

  python audio.py <project_dir> --video render.mp4 [--vo vo.mp3] [--music mine.mp3]
                  [--style lofi] [--seed "<title>"] [--vo-offset 0] [--out final.mp4]

Reads <project_dir>/events.json (written by build.py), synthesizes sfx.wav (whoosh on
scene cuts, pop on cards/pills, click, typing, ding on ticks, slam on stickers/prices)
and music.wav (seeded lo-fi ~90 bpm), then mixes: VO + music (theme style, --music-gain, default 0.42) ducked under the VO
(sidechain) + SFX, limiter, loudnorm -14 LUFS / -1 dBTP. Without --vo the music sits higher.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import common  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--video", required=True)
    ap.add_argument("--vo")
    ap.add_argument("--music", help="user's own track instead of synthesized music")
    ap.add_argument("--style", default=None, help="music style; default = the theme's (events.json)")
    ap.add_argument("--music-gain", type=float, default=0.42, help="music level under the VO (before ducking)")
    ap.add_argument("--seed", default=None)
    ap.add_argument("--vo-offset", type=float, default=0.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    ev = json.load(open(os.path.join(a.project, "events.json")))
    dur = float(ev["duration"])
    sfx = common.Mix(dur, seed=7)
    for e in ev["events"]:
        t, k, g = e["t"], e["type"], e.get("g")
        if k == "whoosh":
            sfx.whoosh(t, g or 0.3)
        elif k == "pop":
            sfx.pop(t, g or 0.3)
        elif k == "click":
            sfx.knock(t, (g or 0.25) * 0.6); sfx.word_pop(t, 0.12)
        elif k == "ding":
            sfx.ding(t, g or 0.18)
        elif k == "slam":
            sfx.slam(t, g or 0.4)
        elif k == "typing":
            sfx.typing(t, t + e.get("d", 0.8), g or 0.13)
    sfx_path = os.path.join(a.project, "sfx.wav")
    sfx.write(sfx_path)

    music_path = a.music
    if not music_path:
        mus = common.Mix(dur, seed=3)
        info = mus.music(a.style or ev.get("music", "lofi"), gain=0.9, seed=a.seed or os.path.basename(os.path.abspath(a.project)))
        music_path = os.path.join(a.project, "music.wav")
        mus.write(music_path)
        print(f"[music] {info}")

    out = a.out or os.path.join(a.project, "final.mp4")
    if a.vo:
        delay = int(a.vo_offset * 1000)
        fc = (f"[1:a]adelay={delay}|{delay},aresample=48000,aformat=channel_layouts=stereo,apad,asplit=2[vo][sc];"
              f"[2:a]aresample=48000,aformat=channel_layouts=stereo,volume={a.music_gain}[m];"
              f"[m][sc]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[md];"
              f"[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.45[s];"
              f"[vo][md][s]amix=inputs=3:normalize=0:duration=longest,atrim=0:{dur},"
              f"alimiter=limit=0.95:level=false,loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000[a]")
        inputs = ["-i", a.video, "-i", a.vo, "-stream_loop", "-1", "-i", music_path, "-i", sfx_path]
    else:
        fc = (f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={a.music_gain * 1.4:.2f}[m];"
              f"[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.5[s];"
              f"[m][s]amix=inputs=2:normalize=0:duration=longest,atrim=0:{dur},"
              f"alimiter=limit=0.95:level=false,loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000[a]")
        inputs = ["-i", a.video, "-stream_loop", "-1", "-i", music_path, "-i", sfx_path]
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                                                      "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(dur),
                                                      "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    print(f"OK {out}")


if __name__ == "__main__":
    main()
