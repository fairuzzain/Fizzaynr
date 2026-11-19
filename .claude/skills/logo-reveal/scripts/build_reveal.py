#!/usr/bin/env python3
"""
build_reveal.py - End-to-end automation engine for generating cinematic AI Logo Reveal videos.
Coordinates: Image Preparation -> Nexabot Generation -> Delogo -> Clean Settle Lock -> SFX Pipeline -> Dual MP4 -> GDrive Sync.
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from PIL import Image

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure scripts directory is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Repo-relative paths (see CLAUDE.md); override with env vars or .env.
_ROOT = os.environ.get("ROOT") or subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip() or os.getcwd()
_MOTION_KIT = os.environ.get("MOTION_KIT") or os.path.join(_ROOT, "vendor", "Motion_as_kit")
NEXABOT_TS = os.environ.get("NEXABOT_TS") or os.path.join(_MOTION_KIT, "nexabot", "nexabot.ts")
NEXABOT_SCRIPT = NEXABOT_TS
GDRIVE_SYNC_SCRIPT = os.path.join(_MOTION_KIT, "sync_gdrive.py")
SFX_LIB_DIR = os.environ.get("SFX_DIR") or os.path.join(_ROOT, "assets", "sfx")

# Motion Style Recipes
MOTION_STYLES = {
    "golden-ribbon-trace": (
        "cinematic logo reveal animation. On a clean off-white studio background with soft central lighting, "
        "fine luminous contours and glowing golden line-art trace out the logo elements from the top down. "
        "The outer and inner shapes emerge with elegant dimensional extrusion. A dynamic swirling ribbon of "
        "golden stardust and sparkling light particles sweeps gracefully across the calligraphy and typography "
        "from left to right, illuminating each line into crisp, vibrant solid color. The camera smoothly pulls back "
        "into a perfectly centered composition as delicate lens flare glints travel across the beveled edges, "
        "settling into a razor-sharp, stable, pristine logo lockup with soft contact drop shadow. "
        "8K commercial studio lighting, ultra-sharp vector details, zero warping, pristine commercial finish."
    ),
    "light-sweep": (
        "cinematic light sweep animation. On a clean studio background, radiant volumetric light rays and floating "
        "micro-particles trace the outer and inner contours. Specular rim reflections glide smoothly across the typography "
        "from bottom to top, settling cleanly into the crisp, illuminated emblem with subtle lens shimmer."
    ),
    "3d-bevel": (
        "premium 3D metallic extrusion reveal. The beveled emblem emerges with rich depth, slowly rotating "
        "in soft studio cyclorama lighting. Gentle amber and platinum rim reflections highlight the beveled edges, "
        "smooth camera ease-out settling into a razor-sharp frontal lockup."
    ),
    "liquid-gold": (
        "luxurious molten liquid gold materialization. Molten chrome and liquid amber caustics pool and flow across "
        "a dark glossy surface, swirling upward and instantly hardening into the sculpted metallic logo contours "
        "with micro-refractions and crystal clarity."
    ),
    "cyber-neon": (
        "high-energy cyberpunk circuit surge. Electric cyan and magenta energy pulses ignite along the vector paths. "
        "Dynamic sparks trace the calligraphy and secondary symbols, culminating in a bright shockwave that resolves "
        "into the stable, glowing solid neon emblem."
    ),
    "smoke-ink": (
        "dramatic organic ink and volumetric smoke dispersion. Swirling tendrils of colored smoke bloom outward "
        "from the center in slow motion, gently revealing the outer shapes and typography before condensing into "
        "a clean, solid, opaque vector emblem on a textured backdrop."
    )
}

DELOGO_COORDS = {
    (720, 1280): "x=565:y=1125:w=68:h=68",
    (1080, 1920): "x=855:y=1695:w=95:h=95",
    (1280, 720): "x=1130:y=570:w=63:h=63",
    (1920, 1080): "x=1695:y=855:w=95:h=95",
    (1080, 1080): "x=855:y=855:w=95:h=95"
}

def get_delogo_filter(w, h):
    """Returns ffmpeg delogo filter based on resolution."""
    key = (w, h)
    if key in DELOGO_COORDS:
        return f"delogo={DELOGO_COORDS[key]}"
    # Proportional calculation for arbitrary resolutions
    bw = int(w * 0.088)
    bh = bw
    bx = int(w * 0.79)
    by = int(h * 0.88)
    return f"delogo=x={bx}:y={by}:w={bw}:h={bh}"

def run_cmd(cmd, cwd=None):
    """Run command and log output."""
    print(f"\n[EXEC] {' '.join(str(c) for c in cmd)}", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        print(f"[ERROR] STDERR: {res.stderr}", flush=True)
        print(f"[ERROR] STDOUT: {res.stdout}", flush=True)
        raise RuntimeError(f"Command failed with code {res.returncode}")
    return res.stdout.strip()

def prepare_canvas(logo_path, out_dir, ratio="9:16", bg_choice=None):
    """Prepares centered logo canvas for video generation."""
    im = Image.open(logo_path)
    w, h = im.size
    canvas_sizes = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
    cw, ch = canvas_sizes.get(ratio, (1080, 1920))
    
    # If already exact canvas dimensions, use directly
    if (w, h) == (cw, ch):
        target_canvas_file = os.path.join(out_dir, "canvas_logo.png")
        shutil.copyfile(logo_path, target_canvas_file)
        meta = {
            "target_canvas": {"width": cw, "height": ch, "ratio": ratio},
            "source_image": logo_path
        }
        return target_canvas_file, meta

    from analyze_logo import analyze_logo_image
    result = analyze_logo_image(logo_path, target_ratio=ratio, bg_choice=bg_choice)
    canvas_path = result["prepared_canvas_path"]
    target_canvas_file = os.path.join(out_dir, "canvas_logo.png")
    shutil.copyfile(canvas_path, target_canvas_file)
    return target_canvas_file, result

def assemble_sfx(duration_sec, out_wav):
    """Mixes whoosh/riser buildup and climax impact/chime from SFX library."""
    whoosh_path = os.path.join(SFX_LIB_DIR, "whoosh", "swosh_swoosh_whoosh_air_sound_free_high__f1dc6045.mp3")
    hit_path = os.path.join(SFX_LIB_DIR, "hit", "hit_impact_7f3dc6f7.mp3")
    chime_path = os.path.join(SFX_LIB_DIR, "chime", "chime_notification_adb6e260.mp3")

    # If local files exist, mix with ffmpeg
    if os.path.exists(whoosh_path) and os.path.exists(hit_path):
        climax_ms = 2500  # 2.5s hit cue
        # Delay the hit sound by climax_ms
        cmd = [
            "ffmpeg", "-y",
            "-i", whoosh_path,
            "-i", hit_path,
            "-filter_complex",
            f"[1:a]adelay={climax_ms}|{climax_ms}[hit_delayed];"
            f"[0:a][hit_delayed]amix=inputs=2:duration=first:dropout_transition=2,volume=1.2[aout]",
            "-map", "[aout]",
            "-t", str(duration_sec),
            out_wav
        ]
        try:
            run_cmd(cmd)
            return out_wav
        except Exception as e:
            print(f"[WARNING] SFX mix error: {e}", flush=True)
    return None

def build_logo_reveal(
    logo_path,
    filled_prompt,
    style="golden-ribbon-trace",
    ratio="16:9",
    mode="sfv",
    title="Logo Reveal",
    out_dir="./output_logo_reveal",
    dry=False,
    sync_gdrive=True
):
    """Runs complete Logo Reveal pipeline."""
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print("==================================================", flush=True)
    print(f"[LOGO REVEAL] PRODUCTION PIPELINE: {title}", flush=True)
    print(f"Logo Source: {logo_path}", flush=True)
    print(f"Style Recipe: {style}", flush=True)
    print(f"Aspect Ratio: {ratio} (Mode: {mode})", flush=True)
    print("==================================================", flush=True)

    # 1. Canvas Preparation
    print("\n[Step 1/7] Preparing video canvas from logo...", flush=True)
    canvas_file, meta = prepare_canvas(logo_path, out_dir, ratio=ratio)
    cw = meta["target_canvas"]["width"]
    ch = meta["target_canvas"]["height"]
    print(f"Canvas ready: {canvas_file} ({cw}x{ch})", flush=True)

    # 2. Construct Prompt
    style_desc = MOTION_STYLES.get(style, MOTION_STYLES["light-sweep"])
    full_prompt = f"{filled_prompt.strip()} {style_desc} Zero text morphing, high-end motion design, sharp clean edges, studio finish."

    manifest = {
        "title": title,
        "style": style,
        "ratio": ratio,
        "mode": mode,
        "base_prompt": filled_prompt,
        "full_prompt": full_prompt,
        "metadata": meta
    }
    manifest_path = os.path.join(out_dir, "reveal_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n--- Production Video Prompt ---")
    print(full_prompt)
    print("-------------------------------\n")

    if dry:
        print("[DRY RUN] Halting before Nexabot API call. Cost: ~0.15 - 0.20 credits.")
        return manifest_path

    # 3. Nexabot Generation
    print("\n[Step 2/7] Generating AI video via Nexabot...", flush=True)
    raw_video = os.path.join(out_dir, "raw_reveal.mp4")
    
    nex_ratio = 2 if ratio == "9:16" else 1 if ratio == "16:9" else "1:1"
    
    if mode == "seedance":
        nex_cmd = [
            "bun", NEXABOT_SCRIPT, "seedance", full_prompt,
            "--duration", "15",
            "--ratio", str(nex_ratio),
            "--media", canvas_file,
            "--out", raw_video
        ]
    else: # sfv mode
        nex_cmd = [
            "bun", NEXABOT_SCRIPT, "sfv", full_prompt,
            "--media", canvas_file,
            "--ratio", str(nex_ratio),
            "--res", "1080" if cw >= 1080 and ch >= 1080 else "720",
            "--out", raw_video
        ]

    nex_out = run_cmd(nex_cmd)
    
    # Locate saved output path from stdout
    actual_saved = None
    for line in nex_out.splitlines():
        if "saved " in line:
            parts = line.split("saved ", 1)[1].strip()
            # Path might be followed by " (1080x1920)"
            candidate = parts.split(" (")[0].strip()
            if os.path.exists(candidate):
                actual_saved = candidate
                break

    if actual_saved and os.path.exists(actual_saved):
        raw_video = actual_saved
    elif not os.path.exists(raw_video):
        # Check if raw_reveal-2.mp4 or similar exists
        stem, ext = os.path.splitext(raw_video)
        candidates = list(Path(out_dir).glob(f"{os.path.basename(stem)}*{ext}"))
        if candidates:
            raw_video = str(sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0])
        else:
            raise FileNotFoundError(f"Generated video not found at {raw_video}")

    # 4. Probe Video
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height",
        "-of", "json", raw_video
    ]
    p_meta = json.loads(run_cmd(probe_cmd))
    vid_dur = float(p_meta["format"]["duration"])
    vw = int(p_meta["streams"][0]["width"])
    vh = int(p_meta["streams"][0]["height"])

    # 5. Delogo Gemini Watermark
    print("\n[Step 3/7] Removing Gemini watermark...", flush=True)
    clean_video = os.path.join(out_dir, "clean_reveal.mp4")
    delogo_filter = get_delogo_filter(vw, vh)
    
    run_cmd([
        "ffmpeg", "-y", "-i", raw_video,
        "-vf", delogo_filter,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        clean_video
    ])

    # 6. Settle Lock (Overlay Authentic Logo for Final 1.5s)
    print("\n[Step 4/7] Applying pristine artwork settle lock (zero-defect branding)...", flush=True)
    locked_video = os.path.join(out_dir, "settled_reveal.mp4")
    settle_start = max(0.0, vid_dur - 1.5)
    
    # Smooth crossfade overlay of original canvas onto the tail of video
    overlay_filter = (
        f"[0:v][1:v]overlay=0:0:enable='gte(t,{settle_start})',fade=t=in:st={settle_start}:d=0.4:alpha=1[v]"
    )
    run_cmd([
        "ffmpeg", "-y",
        "-i", clean_video,
        "-loop", "1", "-i", canvas_file,
        "-filter_complex", overlay_filter,
        "-map", "[v]",
        "-t", str(vid_dur),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        locked_video
    ])

    # 7. Sound Design / SFX
    print("\n[Step 5/7] Adding synchronized SFX (Riser -> Climax Impact)...", flush=True)
    sfx_wav = os.path.join(out_dir, "reveal_sfx.wav")
    assembled_sfx = assemble_sfx(vid_dur, sfx_wav)

    # 8. Dual MP4 Master & Phone Render
    print("\n[Step 6/7] Rendering Master & Compressed Phone deliverables...", flush=True)
    master_mp4 = os.path.join(out_dir, f"{title.replace(' ', '_')}_Master.mp4")
    phone_mp4 = os.path.join(out_dir, f"{title.replace(' ', '_')}_Phone.mp4")

    # Master render
    master_cmd = ["ffmpeg", "-y", "-i", locked_video]
    if assembled_sfx and os.path.exists(assembled_sfx):
        master_cmd.extend(["-i", assembled_sfx, "-c:a", "aac", "-b:a", "320k"])
    else:
        master_cmd.extend(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:a", "aac"])
    
    master_cmd.extend([
        "-c:v", "libx264", "-crf", "17", "-preset", "slow",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        master_mp4
    ])
    run_cmd(master_cmd)

    # Phone render (< 20 MB)
    phone_cmd = ["ffmpeg", "-y", "-i", master_mp4, "-c:v", "libx264", "-crf", "23", "-preset", "slow", "-movflags", "+faststart", phone_mp4]
    run_cmd(phone_cmd)

    # 9. QA Contact Sheet Inspection
    print("\n[Step 7/7] Generating QA Inspection Contact Sheet...", flush=True)
    from inspect_logo_clip import inspect_clip
    qa_report = inspect_clip(master_mp4, out_dir=os.path.join(out_dir, "qa"))
    contact_sheet = qa_report.get("contact_sheet", "")
    print(f"QA Status: {qa_report['status']}")
    print(f"Contact Sheet: {contact_sheet}")

    # 10. Auto-Sync to Google Drive
    gdrive_link = None
    if sync_gdrive and os.path.exists(GDRIVE_SYNC_SCRIPT):
        print("\n[Google Drive Auto-Sync] Syncing assets to Drive...", flush=True)
        files_to_sync = [master_mp4, phone_mp4, canvas_file, manifest_path]
        if contact_sheet and os.path.exists(contact_sheet):
            files_to_sync.append(contact_sheet)
        
        sync_cmd = ["python", GDRIVE_SYNC_SCRIPT, title] + files_to_sync
        try:
            gdrive_out = run_cmd(sync_cmd)
            for line in gdrive_out.splitlines():
                if "drive.google.com" in line:
                    gdrive_link = line.strip()
        except Exception as e:
            print(f"[WARNING] GDrive sync failed: {e}", flush=True)

    print("\n==================================================", flush=True)
    print("[OK] LOGO REVEAL PRODUCTION COMPLETE!", flush=True)
    print(f"Master MP4: {master_mp4} ({os.path.getsize(master_mp4)/(1024*1024):.2f} MB)")
    print(f"Phone MP4:  {phone_mp4} ({os.path.getsize(phone_mp4)/(1024*1024):.2f} MB)")
    print(f"QA Sheet:   {contact_sheet}")
    if gdrive_link:
        print(f"Drive URL:  {gdrive_link}")
    print("==================================================\n", flush=True)

    return master_mp4

def main():
    parser = argparse.ArgumentParser(description="Build cinematic AI Logo Reveal video")
    parser.add_argument("logo", help="Path to input logo image (PNG/JPG)")
    parser.add_argument("--prompt", required=True, help="Filled template prompt")
    parser.add_argument("--style", default="golden-ribbon-trace", choices=list(MOTION_STYLES.keys()), help="Motion reveal recipe")
    parser.add_argument("--ratio", default="16:9", choices=["16:9", "9:16", "1:1"], help="Aspect ratio")
    parser.add_argument("--mode", default="sfv", choices=["sfv", "seedance", "t2v"], help="Nexabot generation mode")
    parser.add_argument("--title", default="Logo Reveal", help="Project Title for GDrive & files")
    parser.add_argument("--out-dir", default="./output_logo_reveal", help="Output directory")
    parser.add_argument("--dry", action="store_true", help="Dry run without API generation")
    parser.add_argument("--no-gdrive", action="store_true", help="Skip Google Drive upload")

    args = parser.parse_args()

    build_logo_reveal(
        logo_path=args.logo,
        filled_prompt=args.prompt,
        style=args.style,
        ratio=args.ratio,
        mode=args.mode,
        title=args.title,
        out_dir=args.out_dir,
        dry=args.dry,
        sync_gdrive=not args.no_gdrive
    )

if __name__ == "__main__":
    main()
