#!/usr/bin/env python3
"""
genjutsu_tool.py - Automated utilities for Genjutsu Character Swap workflows.

Features:
1. prep: Validates, trims, and formats source video to meet Genjutsu requirements (4-30s, MP4/MOV, <200MB).
2. sync-audio: Restores original audio to the silent or stripped swapped video clip.
3. split-screen: Generates side-by-side comparison video (Real vs Character) in perfect sync.
4. character-prompt: Generates tailored character reference prompts (3D, Anime, Claymation, Pixel-Art, etc.).
"""

import argparse
import json
import os
import subprocess
import sys

# Repo-relative paths (see CLAUDE.md); override with env vars or .env.
_ROOT = os.environ.get("ROOT") or subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip() or os.getcwd()
_MOTION_KIT = os.environ.get("MOTION_KIT") or os.path.join(_ROOT, "vendor", "Motion_as_kit")
NEXABOT_TS = os.environ.get("NEXABOT_TS") or os.path.join(_MOTION_KIT, "nexabot", "nexabot.ts")


def run_cmd(cmd):
    """Run shell command and print output."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=isinstance(cmd, str))
    if res.returncode != 0:
        print(f"Error (code {res.returncode}):\n{res.stderr}", file=sys.stderr)
        return False, res.stdout, res.stderr
    return True, res.stdout, res.stderr


def probe_video(video_path):
    """Probes video metadata using ffprobe."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-show_entries", "format=duration,size",
        "-of", "json",
        video_path
    ]
    ok, out, _ = run_cmd(cmd)
    if not ok:
        return None
    try:
        data = json.loads(out)
        duration = float(data.get("format", {}).get("duration", 0) or data.get("streams", [{}])[0].get("duration", 0))
        size_mb = float(data.get("format", {}).get("size", 0)) / (1024 * 1024)
        width = int(data.get("streams", [{}])[0].get("width", 0))
        height = int(data.get("streams", [{}])[0].get("height", 0))
        return {
            "duration": duration,
            "size_mb": size_mb,
            "width": width,
            "height": height,
            "aspect": f"{width}:{height}"
        }
    except Exception as e:
        print(f"Failed to parse ffprobe output: {e}", file=sys.stderr)
        return None


def cmd_prep(args):
    """Prepares and validates video for Genjutsu."""
    meta = probe_video(args.input)
    if not meta:
        print("[-] Could not analyze input video.", file=sys.stderr)
        return 1

    print(f"[+] Input Video: {args.input}")
    print(f"    Dimensions: {meta['width']}x{meta['height']} ({meta['aspect']})")
    print(f"    Duration:   {meta['duration']:.2f} seconds")
    print(f"    File Size:  {meta['size_mb']:.2f} MB")

    needs_trim = meta['duration'] > 30.0 or meta['duration'] < 4.0 or args.start or args.end
    out_file = args.output or "prep_ready.mp4"

    if meta['duration'] < 4.0:
        print("[!] Warning: Video is under 4 seconds. Genjutsu requires 4 to 30 seconds.", file=sys.stderr)

    start_sec = args.start if args.start is not None else 0.0
    duration = min(30.0, meta['duration'] - start_sec)
    if args.end is not None:
        duration = args.end - start_sec

    # Trim and normalize
    cmd = ["ffmpeg", "-y", "-ss", str(start_sec), "-i", args.input, "-t", str(duration)]
    
    # Optional vertical cropping to 9:16 (1080x1920) if requested
    if args.vertical:
        cmd.extend(["-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac"])
    else:
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac"])

    cmd.append(out_file)
    ok, _, _ = run_cmd(cmd)
    if ok:
        print(f"[+] Prepared clip saved to: {out_file}")
        meta_out = probe_video(out_file)
        if meta_out:
            print(f"    New duration: {meta_out['duration']:.2f}s | Size: {meta_out['size_mb']:.2f}MB")
        return 0
    return 1


def cmd_sync_audio(args):
    """Restores original audio to the swapped clip."""
    if not os.path.exists(args.original):
        print(f"[-] Original video not found: {args.original}", file=sys.stderr)
        return 1
    if not os.path.exists(args.swapped):
        print(f"[-] Swapped video not found: {args.swapped}", file=sys.stderr)
        return 1

    out_file = args.output or "swapped_audio_synced.mp4"

    # Mux swapped video with original video audio
    cmd = [
        "ffmpeg", "-y",
        "-i", args.swapped,
        "-i", args.original,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0?",
        "-shortest",
        out_file
    ]

    ok, _, _ = run_cmd(cmd)
    if ok:
        print(f"[+] Audio synced successfully! Saved to: {out_file}")
        return 0
    else:
        print("[-] Audio sync failed.", file=sys.stderr)
        return 1


def cmd_split_screen(args):
    """Creates a side-by-side comparison video (Real vs Swapped)."""
    if not os.path.exists(args.left) or not os.path.exists(args.right):
        print("[-] Both left (real) and right (swapped) clips must exist.", file=sys.stderr)
        return 1

    out_file = args.output or "split_screen_comparison.mp4"

    # Stack horizontally (hstack) with equal heights
    # Left = real clip, Right = swapped character
    # Audio taken from left (original audio)
    filter_complex = (
        "[0:v]scale=-1:1920,crop=540:1920[v0];"
        "[1:v]scale=-1:1920,crop=540:1920[v1];"
        "[v0][v1]hstack=inputs=2[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", args.left,
        "-i", args.right,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a:0?",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        out_file
    ]

    ok, _, _ = run_cmd(cmd)
    if ok:
        print(f"[+] Split-screen comparison video created: {out_file}")
        return 0
    else:
        print("[-] Split-screen creation failed.", file=sys.stderr)
        return 1


def cmd_prompt(args):
    """Outputs copy-ready character reference prompts."""
    prompts = {
        "3d": (
            "Character reference of a stylized 3D animated young man, waist-up, facing the camera, "
            "standing in front of a plain soft grey background with gentle even studio light. "
            "Big expressive eyes, warm brown skin, short curly black hair, a friendly confident half smile. "
            "He wears an oversized mustard-yellow hoodie with the sleeves pushed up. Clean animated family-film look, "
            "soft shadows, detailed skin and fabric texture, neutral relaxed pose with arms down. Vertical 9:16, no text, no logos."
        ),
        "anime": (
            "Character reference of an anime-style young woman, waist-up, facing the camera, "
            "against a plain soft grey background with even, soft lighting. Long silver hair with a straight fringe, "
            "sharp violet eyes, a calm, slightly playful expression. She wears a black high-collar jacket with thin red trim. "
            "Clean cel shading, crisp line art, neutral relaxed pose with arms down. Vertical 9:16, no text, no logos."
        ),
        "claymation": (
            "Character reference of a handcrafted claymation stop-motion figure, waist-up, facing the camera, "
            "standing against a neutral tactile background. Visible fingerprint textures, soft plasticine material, "
            "warm studio lighting, miniature scale depth of field, charming quirky character design. Vertical 9:16, no text."
        ),
        "pixel": (
            "Character reference of a modern high-detail 16-bit pixel art hero character, waist-up portrait, "
            "clean dithering, vibrant retro color palette, crisp outlines, facing camera, neutral pose. Vertical 9:16, no text."
        ),
        "animal": (
            "Character reference of an anthropomorphic friendly red fox character, waist-up, wearing a modern stylish denim jacket, "
            "photorealistic fur texture, expressive amber eyes, standing in front of a soft neutral studio background. Vertical 9:16, no text."
        )
    }

    genjutsu_prompt = (
        "Replace the person in the video with the character from the reference images. "
        "Keep the background, lighting, camera movement and framing exactly as in the original. "
        "Match the original body movement, head turns, facial expressions, lip movement and timing frame by frame. "
        "Keep the character's face, hair, outfit and colors the same in every frame."
    )

    style = args.style.lower()
    char_prompt = prompts.get(style, prompts["3d"])

    print("=" * 60)
    print(f"CHARACTER REFERENCE PROMPT ({style.upper()}):")
    print("=" * 60)
    print(char_prompt)
    print("\n" + "=" * 60)
    print("NEXABOT CLI COMMAND (0.10 credit via GPT Image 2.5):")
    print("=" * 60)
    print(f'bun "{NEXABOT_TS}" gpt-image "{char_prompt}" --aspect 5 --out character_ref.png')
    print("\n" + "=" * 60)
    print("HIGGSFIELD GENJUTSU PROMPT (Copy & Paste):")
    print("=" * 60)
    print(genjutsu_prompt)
    print("=" * 60)
    return 0


def cmd_r2v(args):
    """Formats and executes/prints Nexabot r2v (Reference-to-Video) character swap."""
    video = args.video
    ref = args.character
    prompt = args.prompt or (
        "Replace the person in the video with the character from the reference images. "
        "Keep the background, lighting, camera movement and framing exactly as in the original. "
        "Match the original body movement, head turns, facial expressions, lip movement and timing frame by frame. "
        "Keep the character's face, hair, outfit and colors the same in every frame."
    )
    ratio = args.ratio  # 2 = 9:16, 1 = 16:9
    res = args.res      # 1080 or 720
    out = args.output or "swapped_r2v.mp4"

    cmd = [
        "bun", NEXABOT_TS,
        "r2v", prompt,
        "--media", video
    ]
    if ref:
        cmd.extend(["--media", ref])
    cmd.extend(["--ratio", str(ratio), "--res", str(res), "--out", out])

    manifest = [{
        "name": os.path.splitext(os.path.basename(out))[0],
        "mode": "r2v",
        "prompt": prompt,
        "ratio": ratio,
        "resolution": res,
        "media": [video] + ([ref] if ref else [])
    }]

    print("=" * 60)
    print("NEXABOT R2V COMMAND (Reference-to-Video Character Swap):")
    print("Cost: 0.15 credit (0 credit / Free on API Unlimited plan)")
    print("=" * 60)
    cmd_str = f'bun "{NEXABOT_TS}" r2v "{prompt}" --media "{video}"'
    if ref:
        cmd_str += f' --media "{ref}"'
    cmd_str += f' --ratio {ratio} --res {res} --out "{out}"'
    print(cmd_str)
    print("\n" + "=" * 60)
    print("BATCH JSON ENTRY (clips.json):")
    print("=" * 60)
    print(json.dumps(manifest, indent=2))
    print("=" * 60)
    print("\nWatermark Delogo Post-Process (ffmpeg):")
    if ratio == 2:
        print(f'ffmpeg -i "{out}" -vf "delogo=x=855:y=1695:w=95:h=95" clean_{out}')
    else:
        print(f'ffmpeg -i "{out}" -vf "delogo=x=1130:y=570:w=63:h=63" clean_{out}')

    if args.run:
        print("\n[+] Executing Nexabot r2v...")
        run_cmd(cmd)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Genjutsu Character Swap Utilities")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # prep
    p_prep = subparsers.add_parser("prep", help="Validate and trim source video")
    p_prep.add_argument("-i", "--input", required=True, help="Path to input video")
    p_prep.add_argument("-o", "--output", help="Path to output prepared video")
    p_prep.add_argument("-s", "--start", type=float, help="Start trim time in seconds")
    p_prep.add_argument("-e", "--end", type=float, help="End trim time in seconds")
    p_prep.add_argument("--vertical", action="store_true", help="Crop/scale to 1080x1920 (9:16)")

    # sync-audio
    p_sync = subparsers.add_parser("sync-audio", help="Restore original audio to swapped clip")
    p_sync.add_argument("-o", "--original", required=True, help="Original video containing audio")
    p_sync.add_argument("-s", "--swapped", required=True, help="Swapped video clip (silent)")
    p_sync.add_argument("--output", help="Output path for synced video")

    # split-screen
    p_split = subparsers.add_parser("split-screen", help="Create side-by-side comparison video")
    p_split.add_argument("-l", "--left", required=True, help="Left video (Original clip)")
    p_split.add_argument("-r", "--right", required=True, help="Right video (Swapped character clip)")
    p_split.add_argument("--output", help="Output path for split comparison video")

    # prompt
    p_prompt = subparsers.add_parser("prompt", help="Get character reference prompts and CLI commands")
    p_prompt.add_argument("-s", "--style", default="3d", choices=["3d", "anime", "claymation", "pixel", "animal"], help="Character art style")

    # r2v
    p_r2v = subparsers.add_parser("r2v", help="Generate Nexabot r2v command or run video-to-video character swap")
    p_r2v.add_argument("-v", "--video", required=True, help="Path to source video clip")
    p_r2v.add_argument("-c", "--character", help="Path to character reference image")
    p_r2v.add_argument("-p", "--prompt", help="Custom transformation prompt")
    p_r2v.add_argument("--ratio", type=int, default=2, choices=[1, 2], help="Aspect ratio (1 = 16:9, 2 = 9:16)")
    p_r2v.add_argument("--res", type=int, default=1080, choices=[720, 1080], help="Resolution (720 or 1080)")
    p_r2v.add_argument("-o", "--output", help="Output video path")
    p_r2v.add_argument("--run", action="store_true", help="Directly trigger Nexabot CLI")

    args = parser.parse_args()

    if args.subcommand == "prep":
        sys.exit(cmd_prep(args))
    elif args.subcommand == "sync-audio":
        sys.exit(cmd_sync_audio(args))
    elif args.subcommand == "split-screen":
        sys.exit(cmd_split_screen(args))
    elif args.subcommand == "prompt":
        sys.exit(cmd_prompt(args))
    elif args.subcommand == "r2v":
        sys.exit(cmd_r2v(args))


if __name__ == "__main__":
    main()
