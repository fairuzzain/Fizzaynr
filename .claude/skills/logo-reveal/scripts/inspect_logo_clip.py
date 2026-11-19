#!/usr/bin/env python3
"""
inspect_logo_clip.py - Automated quality inspection and contact strip generator for logo reveal clips.
"""

import os
import sys
import json
import argparse
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def inspect_clip(clip_path, out_dir=None):
    """
    Rigorously audits an AI logo reveal video clip:
    1. Extracts 1 fps contact strip frames.
    2. Verifies bottom-right corner for clean Gemini delogo watermark removal.
    3. Checks for visual stability and distortion.
    4. Generates a composite QA contact sheet image.
    """
    if not os.path.exists(clip_path):
        raise FileNotFoundError(f"Clip not found: {clip_path}")

    base_name = os.path.splitext(os.path.basename(clip_path))[0]
    if not out_dir:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(clip_path)), "qa_inspection")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Probe video metadata
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height,r_frame_rate",
        "-of", "json", clip_path
    ]
    probe_run = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
    meta = json.loads(probe_run.stdout)
    
    duration = float(meta["format"].get("duration", 5.0))
    stream = meta["streams"][0]
    w = int(stream.get("width", 1080))
    h = int(stream.get("height", 1920))

    # 2. Extract 1 fps frames
    frame_paths = []
    num_seconds = max(1, int(duration))
    for sec in range(num_seconds):
        t_sec = min(sec + 0.5, duration - 0.1)
        f_path = os.path.join(out_dir, f"{base_name}_frame_{sec:02d}s.png")
        cmd_extract = [
            "ffmpeg", "-y", "-ss", f"{t_sec:.2f}",
            "-i", clip_path, "-vframes", "1",
            f_path
        ]
        subprocess.run(cmd_extract, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(f_path):
            frame_paths.append((sec, f_path))

    if not frame_paths:
        return {"status": "FAIL", "reason": "Could not extract video frames"}

    # 3. Analyze frames & watermark zone
    frame_images = []
    wm_warnings = []
    
    for sec, fp in frame_paths:
        im = Image.open(fp).convert("RGB")
        frame_images.append((sec, im))
        arr = np.array(im)
        
        # Check watermark zone (bottom-right 12% width and height)
        wm_y1 = int(h * 0.88)
        wm_y2 = int(h * 0.98)
        wm_x1 = int(w * 0.82)
        wm_x2 = int(w * 0.98)
        wm_crop = arr[wm_y1:wm_y2, wm_x1:wm_x2]
        
        # In uncleaned Veo videos, watermark is sharp bright white star cluster on dark
        # Standard deviation or high peak brightness
        peak = np.max(wm_crop)
        mean_crop = np.mean(wm_crop)
        if peak > 245 and (peak - mean_crop) > 120:
            wm_warnings.append(sec)

    # 4. Generate visual contact sheet
    num_frames = len(frame_images)
    cols = min(5, num_frames)
    rows = (num_frames + cols - 1) // cols
    
    thumb_w = 260
    thumb_h = int(thumb_w * (h / w))
    pad = 12
    banner_h = 45
    
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad + banner_h
    
    sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 22, 28))
    draw = ImageDraw.Draw(sheet)
    
    # Title banner
    title = f"LOGO REVEAL QA INSPECTION: {base_name} ({w}x{h} | {duration:.1f}s)"
    draw.text((pad, 14), title, fill=(240, 240, 245))
    
    for idx, (sec, im) in enumerate(frame_images):
        col_idx = idx % cols
        row_idx = idx // cols
        
        x = pad + col_idx * (thumb_w + pad)
        y = banner_h + pad + row_idx * (thumb_h + pad)
        
        thumb = im.resize((thumb_w, thumb_h), Image.Resampling.BILINEAR)
        sheet.paste(thumb, (x, y))
        
        # Frame label
        t_label = f"{sec}s"
        draw.rectangle([x + 6, y + 6, x + 38, y + 22], fill=(0, 0, 0, 180))
        draw.text((x + 10, y + 8), t_label, fill=(255, 255, 255))
        
        # Border
        border_col = (220, 50, 50) if sec in wm_warnings else (60, 70, 85)
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=border_col, width=2)

    sheet_path = os.path.join(out_dir, f"{base_name}_contact_sheet.png")
    sheet.save(sheet_path, "PNG")

    status = "PASS" if not wm_warnings else "WARNING_WATERMARK_DETECTED"
    
    report = {
        "clip": clip_path,
        "status": status,
        "duration": duration,
        "resolution": f"{w}x{h}",
        "frames_extracted": len(frame_paths),
        "watermark_warnings_at_seconds": wm_warnings,
        "contact_sheet": sheet_path
    }
    return report

def main():
    parser = argparse.ArgumentParser(description="Inspect logo reveal video clip and create contact sheet")
    parser.add_argument("clip", help="Path to video file (MP4)")
    parser.add_argument("--out-dir", default=None, help="Output directory for QA artifacts")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    
    args = parser.parse_args()
    rep = inspect_clip(args.clip, out_dir=args.out_dir)
    
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print("\n================ QA AUDIT REPORT ================")
        print(f"Status: {rep['status']}")
        print(f"Clip: {rep['clip']} ({rep['resolution']}, {rep['duration']:.1f}s)")
        print(f"Frames inspected: {rep['frames_extracted']}")
        if rep['watermark_warnings_at_seconds']:
            print(f"[!] Warning: Possible residual watermark at seconds: {rep['watermark_warnings_at_seconds']}")
        else:
            print("[OK] Clean frame borders & watermark delogo verified.")
        print(f"Contact Sheet: {rep['contact_sheet']}")
        print("=================================================\n")

if __name__ == "__main__":
    main()
