#!/usr/bin/env python3
"""Extract every caption interval for visual review; verify an exact-file review.
A geometry/render receipt is NOT a visual PASS. No automatic subject recognition.
"""
import argparse
from bisect import bisect_left
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import shutil
from PIL import Image, ImageDraw


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def samples(cues):
    result = []
    for index, (start, end, text) in enumerate(cues):
        if not math.isfinite(start + end) or not 0 <= start < end:
            raise ValueError("invalid caption interval")
        # Both edges plus <=0.25s spacing; include each short cue too.
        inset = min(.02, (end-start)/4)
        count = max(2, math.ceil((end-start-2*inset)/.25)+1)
        for i in range(count):
            result.append({"id": f"c{index:04d}-{i:03d}", "cue": index,
                           "time": round(start+inset+(end-start-2*inset)*i/(count-1), 6),
                           "text": text})
    if not result:
        raise ValueError("no captions to inspect")
    return result


def prepare(video, srt, directory):
    from subtitle_paper_burn import parse_srt
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    cues = parse_srt(srt)
    rows = samples(cues)
    # Seek to an existing decoded frame, including the last displayed frame.
    # Seeking beyond the final frame's PTS otherwise succeeds without a JPEG.
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(video)
    ], text=True))
    times = sorted(float(f["best_effort_timestamp_time"]) for f in probe["frames"])
    if not times:
        raise ValueError("video has no decoded frames")
    for row in rows:
        start, end, _ = cues[row["cue"]]
        first, last = bisect_left(times, start), bisect_left(times, end)-1
        if first > last:
            raise ValueError("caption interval has no visible video frame")
        row["frame_index"] = max(first, min(bisect_left(times, row["time"]), last))
        row["frame_time"] = times[row["frame_index"]]
    indices = sorted({row["frame_index"] for row in rows})
    # FFmpeg 5.x cannot parse long left-nested sums reliably. Bound each filter
    # while retaining exact decoded indices (including shared low-FPS samples).
    with tempfile.TemporaryDirectory() as td:
        extracted = {}
        for offset in range(0, len(indices), 24):
            batch = indices[offset:offset+24]
            prefix = f"batch-{offset:06d}"
            pattern = str(Path(td)/f"{prefix}-%06d.jpg")
            selection = "+".join(f"eq(n,{index})" for index in batch)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(video),
                            "-vf", f"select='{selection}'", "-fps_mode", "vfr", "-q:v", "2", pattern], check=True)
            extracted.update({index: Path(td)/f"{prefix}-{i+1:06d}.jpg"
                              for i,index in enumerate(batch)})
        for row in rows:
            frame = directory/(row["id"]+".jpg")
            shutil.copyfile(extracted[row["frame_index"]], frame)
            row["frame"] = frame.name
            row["sha256"] = sha256(frame)
    sheets = []
    for offset in range(0, len(rows), 6):
        batch = rows[offset:offset+6]
        sheet = Image.new("RGB", (3*360, 2*670), "#202020")
        draw = ImageDraw.Draw(sheet)
        for j, row in enumerate(batch):
            with Image.open(directory/row["frame"]) as original:
                preview = original.copy()
                preview.thumbnail((360, 640))
                x, y = (j%3)*360, (j//3)*670
                sheet.paste(preview, (x+(360-preview.width)//2, y))
                draw.text((x+4,y+645), f'{row["id"]} @ {row["frame_time"]:.3f}s', fill="white")
        name = f"sheet-{offset//6:03d}.jpg"
        sheet.save(directory/name, quality=85)
        sheets.append(name)
    manifest = {"schema_version": 1, "video_sha256": sha256(video),
                "srt_sha256": sha256(srt), "samples": rows, "sheets": sheets}
    (directory/"evidence.json").write_text(json.dumps(manifest, indent=2))
    # Never overwrite a review with fabricated passing answers.
    template = {"evidence_sha256": sha256(directory/"evidence.json"),
                "frames": [{"id": row["id"], "clear": None, "text_ok": None,
                            "notes": ""} for row in rows]}
    (directory/"review-template.json").write_text(json.dumps(template, indent=2))
    return manifest


def verify(video, srt, evidence_path, review_path, receipt_path):
    receipt_path = Path(receipt_path)
    protected = [Path(p).resolve() for p in (video, srt, evidence_path, review_path, str(video)+'.captions.json')]
    if receipt_path.resolve() in protected:
        raise ValueError("receipt must not overwrite an input")
    receipt_path.write_text(json.dumps({"verdict": "FAIL", "reason": "review incomplete"}))
    evidence = json.loads(Path(evidence_path).read_text())
    review = json.loads(Path(review_path).read_text())
    layout = json.loads(Path(str(video)+'.captions.json').read_text())
    if layout.get('verdict') != 'RENDERED' or layout.get('video_sha256') != sha256(video) or layout.get('srt_sha256') != sha256(srt):
        raise ValueError('caption render failed or layout receipt is stale')
    if layout.get("profile") != "safe":
        raise ValueError("subject-clear review requires the safe profile")
    from caption_guard import check_delivery
    check_delivery(layout)
    if evidence.get("schema_version") != 1 or evidence.get("video_sha256") != sha256(video) or evidence.get("srt_sha256") != sha256(srt):
        raise ValueError("evidence belongs to a different video or transcript")
    if review.get("evidence_sha256") != sha256(evidence_path):
        raise ValueError("review belongs to different evidence")
    from subtitle_paper_burn import parse_srt
    expected = samples(parse_srt(srt))
    actual = evidence.get("samples", [])
    if [{k:r[k] for k in ("id","cue","time","text")} for r in actual] != expected:
        raise ValueError("evidence does not cover every caption sample")
    answers = review.get("frames", [])
    ids = [row.get("id") for row in answers]
    if len(ids) != len(set(ids)) or set(ids) != {row["id"] for row in expected}:
        raise ValueError("every frame needs exactly one visual review")
    for row in actual:
        frame = Path(evidence_path).parent / row["frame"]
        if frame.resolve().parent != Path(evidence_path).resolve().parent or sha256(frame) != row["sha256"]:
            raise ValueError("review frame missing or changed")
    if any(row.get("clear") is not True or row.get("text_ok") is not True or
           not isinstance(row.get("notes"), str) or not row["notes"].strip() for row in answers):
        raise ValueError("visual review failed or incomplete")
    result = {"schema_version": 1, "verdict": "PASS", "video_sha256": sha256(video),
              "srt_sha256": sha256(srt), "evidence_sha256": sha256(evidence_path),
              "review_sha256": sha256(review_path), "layout_sha256": sha256(str(video)+".captions.json"),
              "sample_count": len(expected),
              "basis": "reviewed sampled frames; not automatic face detection"}
    receipt_path.write_text(json.dumps(result, indent=2))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--video", required=True); prep.add_argument("--srt", required=True)
    prep.add_argument("--out-dir", required=True)
    check = commands.add_parser("verify")
    for arg in ("video", "srt", "evidence", "review", "receipt"):
        check.add_argument("--"+arg, required=True)
    a = p.parse_args()
    if a.command == "prepare":
        result = prepare(a.video, a.srt, a.out_dir)
        print(json.dumps({"samples":len(result["samples"]), "sheets":result["sheets"]}))
    else:
        print(json.dumps(verify(a.video,a.srt,a.evidence,a.review,a.receipt)))


if __name__ == "__main__":
    main()
