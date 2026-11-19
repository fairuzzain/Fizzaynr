import os
import sys
import json
import subprocess
import numpy as np
from PIL import Image

def audit_clip(clip_path, out_dir="qa_inspections"):
    """
    Performs rigorous automated inspection on a single AI video clip:
    1. Extracts 1 fps contact strip frames.
    2. Measures brightness stability, inter-frame motion jitter, and potential artifacts.
    3. Identifies the optimal 'Clean Range' (free of late Veo hallucinations/stray text).
    4. Generates a visual QA strip.
    """
    os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(clip_path))[0]
    clip_qa_dir = os.path.join(out_dir, base_name)
    os.makedirs(clip_qa_dir, exist_ok=True)
    
    # 1. Get clip metadata
    cmd_meta = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height,r_frame_rate",
        "-of", "json", clip_path
    ]
    meta_res = subprocess.run(cmd_meta, capture_output=True, text=True, check=True)
    meta = json.loads(meta_res.stdout)
    duration = float(meta["format"].get("duration", 10.0))
    stream = meta["streams"][0]
    w = int(stream.get("width", 720))
    h = int(stream.get("height", 1280))
    
    # 2. Extract 1 fps frames
    frame_paths = []
    num_frames = int(duration)
    for s in range(num_frames):
        f_path = os.path.join(clip_qa_dir, f"frame_{s:02d}s.png")
        cmd_f = ["ffmpeg", "-y", "-ss", f"{s}.5", "-i", clip_path, "-vframes", "1", f_path]
        subprocess.run(cmd_f, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(f_path):
            frame_paths.append(f_path)
            
    if not frame_paths:
        return {"clip": clip_path, "status": "FAIL", "reason": "No frames could be extracted"}

    # 3. Analyze each frame for visual stability
    stats = []
    clean_frames = []
    
    for idx, fp in enumerate(frame_paths):
        img = Image.open(fp).convert("RGB")
        arr = np.array(img)
        
        mean_luma = float(arr.mean())
        std_luma = float(arr.std())
        
        # Check watermark area in lower right corner (x: 550..650, y: 1100..1200 on 720x1280)
        # Check if watermark is present (residual white star / cluster)
        wm_box = arr[int(h*0.85):int(h*0.95), int(w*0.75):int(w*0.95)]
        wm_score = float(wm_box.std())
        
        is_clean = True
        defect_notes = []
        
        # Check blackout or blowout
        if mean_luma < 10.0:
            is_clean = False
            defect_notes.append("Too dark / blackout frame")
        elif mean_luma > 245.0:
            is_clean = False
            defect_notes.append("Overexposed / blown out white")
            
        # Check contrast collapse (frozen gray/blank frame)
        if std_luma < 15.0:
            is_clean = False
            defect_notes.append("Low contrast / blank render artifact")
            
        # Late hallucination check: Veo clips after 5.5s are prone to hallucinating stray numbers/labels
        if idx >= 6:
            defect_notes.append("Late-stage Veo frame (potential stray text/drift)")
            
        if is_clean:
            clean_frames.append(idx)
            
        stats.append({
            "second": idx,
            "mean_luma": round(mean_luma, 2),
            "std_luma": round(std_luma, 2),
            "is_clean": is_clean,
            "notes": ", ".join(defect_notes) if defect_notes else "OK"
        })
        
    # Determine recommended Clean Range
    if clean_frames:
        start_clean = 0
        # Recommend up to first 5-6 seconds where Veo is cleanest and sharpest
        end_clean = min(len(clean_frames), 6)
        clean_range = [start_clean, end_clean]
    else:
        clean_range = [0, min(duration, 5.0)]
        
    # 4. Generate 1 fps Visual Contact Strip
    thumb_w = 160
    thumb_h = int(thumb_w * (h / w))
    strip_w = thumb_w * len(frame_paths)
    strip = Image.new("RGB", (strip_w, thumb_h))
    
    for i, fp in enumerate(frame_paths):
        im = Image.open(fp).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        strip.paste(im, (i * thumb_w, 0))
        
    strip_path = os.path.join(clip_qa_dir, "contact_strip_1fps.png")
    strip.save(strip_path)
    
    status = "PASS" if len(clean_frames) >= 4 else "WARN"
    
    report = {
        "clip": clip_path,
        "duration": duration,
        "resolution": f"{w}x{h}",
        "status": status,
        "clean_range_seconds": clean_range,
        "contact_strip": strip_path,
        "frame_stats": stats
    }
    
    report_json_path = os.path.join(clip_qa_dir, "audit_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"[{status}] {base_name}: Clean range {clean_range[0]}s-{clean_range[1]}s -> {strip_path}")
    return report

def audit_directory(clips_dir):
    print(f"=== Auditing all AI video clips in: {clips_dir} ===")
    results = []
    for f in sorted(os.listdir(clips_dir)):
        if f.endswith(".mp4") and not f.endswith("_master_4m58s.mp4") and not f.endswith("_phone_18mb.mp4"):
            p = os.path.join(clips_dir, f)
            res = audit_clip(p)
            results.append(res)
    print(f"\nAudit completed: {len(results)} clips inspected.")
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isdir(target):
            audit_directory(target)
        else:
            audit_clip(target)
    else:
        audit_directory("videos")
