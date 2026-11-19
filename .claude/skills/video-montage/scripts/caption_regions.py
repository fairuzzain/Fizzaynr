#!/usr/bin/env python3
"""Show protected boxes on actual clean frames, then bind explicit visual decisions.

No face detector: a reviewer must inspect the paired pixels, including mouth/chin,
hands, labels and motion. Receipts prove review coverage and identity, not semantics.
"""
import argparse
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw
from caption_evidence import sha256, samples
from caption_placement import read_regions
import caption_guard


def clean_evidence(video, srt, evidence_path):
    from subtitle_paper_burn import parse_srt
    path = Path(evidence_path)
    data = json.loads(path.read_text())
    if (data.get("schema_version") != 1 or data.get("video_sha256") != sha256(video)
            or data.get("srt_sha256") != sha256(srt)):
        raise ValueError("region review needs current clean-source evidence")
    expected = samples(parse_srt(srt))
    if [{k: r[k] for k in ("id", "cue", "time", "text")} for r in data["samples"]] != expected:
        raise ValueError("region evidence must cover every caption sample")
    for row in data["samples"]:
        frame = path.parent / row["frame"]
        if frame.resolve().parent != path.parent.resolve() or sha256(frame) != row["sha256"]:
            raise ValueError("clean frame missing or changed")
    return data


def pixel_box(box, width, height):
    left, top, right, bottom = box
    return (round(left*width), round(top*height), round(right*width)-1, round(bottom*height)-1)


def unprotected_view(original, regions, time):
    """Hide exactly the protected union, leaving escaped subject pixels visible.

    Do not dilate the mask: even a fingertip one pixel outside a box must remain
    visible. This is a review aid, not automatic subject detection.
    """
    image = original.convert("RGB")
    draw = ImageDraw.Draw(image)
    for region in regions:
        if region["start"] <= time < region["end"]:
            draw.rectangle(pixel_box(region["box"], *image.size), fill="#202020")
    return image


def save_sheet(sheet, path):
    # Native image calls have a 512 KiB aggregate limit. Preserve tile dimensions
    # and fail explicitly instead of silently omitting a difficult sample.
    for quality in (85, 75, 65, 55):
        sheet.save(path, quality=quality)
        if path.stat().st_size <= 480*1024:
            return
    raise ValueError("region sheet exceeds image budget; inspect individual full-resolution frames")


def draw_regions(original, regions, time):
    image = original.convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    active = []
    for index, region in enumerate(regions):
        if region["start"] <= time < region["end"]:
            active.append(index)
            left, top, right, bottom = region["box"]
            box = pixel_box(region["box"], width, height)
            draw.rectangle(box, outline="#ff4040", width=max(2, round(width/270)))
            label = f"R{index} x:{left:.2f}-{right:.2f} y:{top:.2f}-{bottom:.2f}"
            draw.text((box[0]+3, max(0, box[1])), label, fill="white", stroke_width=1, stroke_fill="black")
    return image, active


def prepare(video, srt, regions_path, evidence_path, out_dir):
    from subtitle_paper_burn import parse_srt
    evidence = clean_evidence(video, srt, evidence_path)
    duration = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "csv=p=0", str(video)], text=True))
    regions = read_regions(regions_path, duration, video, parse_srt(srt))
    digest = sha256(regions_path)
    caption_guard.reserve_regions(video, digest)
    directory = Path(out_dir)
    if directory.resolve() == Path(evidence_path).parent.resolve():
        raise ValueError("region evidence must not overwrite clean evidence")
    directory.mkdir(parents=True, exist_ok=True)
    rows = []
    sheets = []
    # Three views keep the source, exact boxes and escaped pixels side by side.
    for offset in range(0, len(evidence["samples"]), 3):
        sheet = Image.new("RGB", (1080, 3*680), "#202020")
        draw = ImageDraw.Draw(sheet)
        for j, source in enumerate(evidence["samples"][offset:offset+3]):
            original_path = Path(evidence_path).parent / source["frame"]
            with Image.open(original_path) as original:
                annotated, active = draw_regions(original, regions, source["frame_time"])
                frame = directory / (source["id"] + "-regions.jpg")
                annotated.save(frame, quality=90)
                exposed = unprotected_view(original, regions, source["frame_time"])
                exposed_path = directory / (source["id"] + "-unprotected.jpg")
                exposed.save(exposed_path, quality=95)
                for column, picture in enumerate((original.copy(), annotated, exposed)):
                    picture.thumbnail((360, 640))
                    sheet.paste(picture, (column*360+(360-picture.width)//2, j*680+20))
                draw.text((4, j*680), "CLEAN", fill="white")
                draw.text((364, j*680), "PROTECTED BOXES (source coordinates)", fill="white")
                draw.text((724, j*680), "UNPROTECTED: any face/hand/label left?", fill="white")
                draw.text((4, j*680+662), f'{source["id"]} @ {source["frame_time"]:.3f}s | R{active}', fill="white")
                rows.append({"id": source["id"], "frame_time": source["frame_time"],
                             "frame": frame.name, "sha256": sha256(frame), "regions": active,
                             "unprotected_frame": exposed_path.name,
                             "unprotected_sha256": sha256(exposed_path)})
        name = f"sheet-{offset//3:03d}.jpg"
        save_sheet(sheet, directory/name)
        sheets.append({"file": name, "sha256": sha256(directory/name)})
    manifest = {"schema_version": 2, "review_view": "source_boxes_unprotected",
                "video_sha256": sha256(video), "srt_sha256": sha256(srt),
                "regions_sha256": digest, "clean_evidence_sha256": sha256(evidence_path),
                "samples": rows, "sheets": sheets}
    manifest_path = directory / "region-evidence.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    caption_guard.prepared(video, sha256(manifest_path))
    template = {"evidence_sha256": sha256(manifest_path), "frames": [
        {"id": row["id"], "subjects_covered": None, "unprotected_subjects": None,
         "notes": ""} for row in rows]}
    (directory/"region-review-template.json").write_text(json.dumps(template, indent=2))
    return manifest


def verify(video, srt, regions, clean_path, evidence_path, review_path, receipt_path):
    receipt_path = Path(receipt_path)
    inputs = [Path(p).resolve() for p in (video, srt, regions, clean_path, evidence_path, review_path)]
    if receipt_path.resolve() in inputs:
        raise ValueError("region receipt must not overwrite an input")
    caption_guard.invalidate(video)
    receipt_path.write_text(json.dumps({"verdict": "FAIL", "reason": "region review incomplete"}))
    clean = clean_evidence(video, srt, clean_path)
    data = json.loads(Path(evidence_path).read_text())
    review = json.loads(Path(review_path).read_text())
    if (data.get("schema_version") != 2 or data.get("review_view") != "source_boxes_unprotected"
            or data.get("video_sha256") != sha256(video)
            or data.get("srt_sha256") != sha256(srt) or data.get("regions_sha256") != sha256(regions)
            or data.get("clean_evidence_sha256") != sha256(clean_path)
            or review.get("evidence_sha256") != sha256(evidence_path)):
        raise ValueError("annotated region review is stale")
    expected = [row["id"] for row in clean["samples"]]
    if [row["id"] for row in data["samples"]] != expected:
        raise ValueError("region evidence must cover every sampled frame")
    answers = review.get("frames", [])
    if sorted(row["id"] for row in answers) != sorted(expected):
        raise ValueError("every region frame needs exactly one review")
    for row in data["samples"] + data["sheets"]:
        frame = Path(evidence_path).parent / row.get("frame", row.get("file", ""))
        if frame.resolve().parent != Path(evidence_path).parent.resolve() or sha256(frame) != row["sha256"]:
            raise ValueError("annotated frame or sheet missing or changed")
    for row in data["samples"]:
        frame = Path(evidence_path).parent / row.get("unprotected_frame", "")
        if (frame.resolve().parent != Path(evidence_path).parent.resolve()
                or not frame.is_file() or sha256(frame) != row.get("unprotected_sha256")):
            raise ValueError("unprotected frame missing or changed")
    if any(row.get("subjects_covered") is not True or not isinstance(row.get("notes"), str)
           or not row["notes"].strip() or row.get("unprotected_subjects") != [] for row in answers):
        raise ValueError("caption_incomplete: subject coverage failed or uninspected")
    result = {"verdict": "REGIONS_REVIEWED", "video_sha256": sha256(video),
              "srt_sha256": sha256(srt), "regions_sha256": sha256(regions),
              "evidence_sha256": sha256(evidence_path), "review_sha256": sha256(review_path),
              "sample_count": len(expected), "review_view": "source_boxes_unprotected",
              "basis": "explicit sampled pixel review; not face detection"}
    caption_guard.approve(video, result)
    receipt_path.write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    check = commands.add_parser("verify")
    for command in (prep, check):
        for arg in ("video", "srt", "regions", "clean-evidence"):
            command.add_argument("--"+arg, required=True)
    prep.add_argument("--out-dir", required=True)
    for arg in ("evidence", "review", "receipt"):
        check.add_argument("--"+arg, required=True)
    a = parser.parse_args()
    if a.command == "prepare":
        result = prepare(a.video, a.srt, a.regions, a.clean_evidence, a.out_dir)
        print(json.dumps({"samples": len(result["samples"]), "sheets": result["sheets"]}))
    else:
        print(json.dumps(verify(a.video, a.srt, a.regions, a.clean_evidence, a.evidence, a.review, a.receipt)))


if __name__ == "__main__":
    main()
