"""Per-source caption review budget. Local workflow state, not a sandbox security boundary."""
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path

from caption_evidence import sha256

STATE_ROOT = Path.home() / ".higgsfield" / "caption-guards"
MAX_REGION_VERSIONS = 2
MAX_RENDERS = 2


@contextmanager
def state_for_digest(digest):
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    path = STATE_ROOT / (digest + ".json")
    with (STATE_ROOT / (digest + ".lock")).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = json.loads(path.read_text()) if path.exists() else {
            "video_sha256": digest, "regions": [], "renders": 0, "locked_regions": None,
            "approved": None, "prepared": None,
        }
        if data.get("video_sha256") != digest:
            raise ValueError("caption_incomplete: invalid caption guard state")
        try:
            yield data
        finally:
            # A failed validation must not restore an old approval or spent attempt.
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(data, indent=2))
            temporary.replace(path)


def state(video):
    return state_for_digest(sha256(video))


def reserve_regions(video, regions_digest):
    with state(video) as data:
        if data["locked_regions"] and data["locked_regions"] != regions_digest:
            raise ValueError("caption_incomplete: protected regions are frozen after the first render; do not shrink, replace or delete boxes")
        if data["regions"] and data["regions"][-1] == regions_digest:
            data["approved"] = None
            data["prepared"] = None
            return
        if len(data["regions"]) >= MAX_REGION_VERSIONS:
            data["approved"] = None
            raise ValueError("caption_incomplete: region revision limit reached (initial map plus one correction)")
        data["regions"].append(regions_digest)
        data["approved"] = None
        data["prepared"] = None


def prepared(video, evidence_digest):
    with state(video) as data:
        data["prepared"] = evidence_digest


def approve(video, result):
    with state(video) as data:
        data["approved"] = None
        if (not data["regions"] or data["regions"][-1] != result["regions_sha256"]
                or data["prepared"] != result["evidence_sha256"]):
            raise ValueError("caption_incomplete: region evidence is no longer current")
        data["approved"] = result


def invalidate(video):
    with state(video) as data:
        data["approved"] = None


def begin_render(video, srt, regions, receipt):
    with state(video) as data:
        if data["renders"] >= MAX_RENDERS:
            data["approved"] = None
            raise ValueError("caption_incomplete: render limit reached (initial render plus one retry)")
        digest = sha256(regions)
        if data["locked_regions"] and data["locked_regions"] != digest:
            raise ValueError("caption_incomplete: protected regions are frozen after the first render")
        review = json.loads(Path(receipt).read_text())
        if (review.get("verdict") != "REGIONS_REVIEWED" or
                review.get("review_view") != "source_boxes_unprotected" or
                review.get("video_sha256") != sha256(video) or
                review.get("srt_sha256") != sha256(srt) or
                review.get("regions_sha256") != digest or
                data["approved"] != review):
            raise ValueError("caption_incomplete: missing, failed or stale annotated-region review")
        data["renders"] += 1
        data["locked_regions"] = digest
        result = {"attempt": data["renders"], "max_attempts": MAX_RENDERS,
                  "regions_sha256": digest, "region_review_sha256": sha256(receipt)}
        data["last_render"] = result
        data["render_approval"] = review
        return result


def check_delivery(layout):
    import re
    digest = layout.get("source_sha256", "")
    if not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("caption_incomplete: missing reviewed source identity")
    with state_for_digest(digest) as data:
        guard = layout.get("region_guard")
        approved = data.get("approved")
        if (not guard or guard != data.get("last_render") or not approved
                or approved.get("review_view") != "source_boxes_unprotected"
                or approved != data.get("render_approval")
                or guard.get("attempt") != data["renders"]
                or guard.get("regions_sha256") != data["locked_regions"]
                or approved.get("regions_sha256") != guard.get("regions_sha256")
                or approved.get("srt_sha256") != layout.get("srt_sha256")):
            raise ValueError("caption_incomplete: stale or missing region guard on final render")
