# Shared caption clearance and final review

Applies to standalone and UGC speech captions. Faceless uses the simpler fixed
bottom layout in [faceless-captions.md](faceless-captions.md), without these region
maps or dense review receipts. Platform
UI margins do not establish subject clearance. A successful encode or layout
receipt is not a visual PASS. Keep the clean source and its audio.

## MCP sandbox execution

Run preparation and rendering through sandbox_exec. Visual review is an actual
inspection between computation stages, never a set of pre-filled booleans.
For this supervised route use the tool's bounded background lease and poll within
its lifetime; do not assume files survive an expired sandbox. Keep the clean master
at its confirmed durable URL. After preparation completes, use a foreground call
with `image_paths` to return up to four PNG/JPEG files directly as native tool images
(at most 512 KiB combined per call). Start with one sheet per call; combine only
when their total size fits. An oversized response returns an explicit error with
no images: retry all requested sheets in smaller calls. For example:

```json
{
  "command": "test -f clean-evidence/evidence.json",
  "image_paths": ["clean-evidence/sheet-000.jpg"]
}
```

Use the actual sheet names returned by preparation; repeat until all sheets have
been viewed. Request individual full-resolution frames when a sheet is ambiguous;
resize a review copy only if needed for the image limit. Review native pixels, not
base64 text. Image uploads, CDN browser opening and PDF conversion are unnecessary.
An image-path argument alone is not inspection: the tool must return visible images.

Before each subsequent stage, verify the source hash and required local evidence.
If the sandbox expired, download that exact master and regenerate evidence and
word timing; re-materialize authored text and genuine review data only when their
hashes still match. Never invent a storage/upload tool for JSON or SRT. Group each
compute-and-upload step into one self-contained command. Keep commands below the
128,000-character limit, including presigned URLs; upload large sets in small batches. Stop with retained clean
assets if the current host cannot inspect evidence or preserve the required inputs.
The standalone/UGC safe route here owns placement and final inspection instead
of the older fixed-position examples in subtitles.md and the UGC hook references.
Faceless follows its fixed-bottom reference and does not need region maps.

## Inspect the clean source after actual-audio transcription

Use the finished SRT, not planned beats. Extract evidence for every cue:

```bash
set -euo pipefail
python3 "${HF_WORKFLOWS}/video-montage/scripts/caption_evidence.py" prepare \
  --video final.mp4 --srt caps.srt --out-dir clean-evidence
```

Open **all** listed contact sheets; inspect the full-size frame whenever a face,
hand/product label, diagram, existing text or camera movement is near the
caption area. Frames include both cue edges and samples at most 0.25s apart.
Also inspect cuts and fast movement between samples; sampling is not tracking.

Write protected_regions.json from those actual frames. Copy video_sha256 from
clean-evidence/evidence.json. Cover **every caption interval** in
reviewed_intervals; use conservative region boxes covering all movement within
each interval. Split at cuts. Protect the whole face, including mouth and chin,
product labels, tutorial Step N labels, hooks and essential objects. Include
already baked text. An empty regions list is legitimate only after inspecting
the entire declared window and finding no protected subjects. Never copy example
boxes or shrink/delete them just to make a render pass.

```json
{
  "video_sha256": "copy exact source digest from evidence.json",
  "reviewed_duration": 30.04,
  "reviewed_intervals": [{ "start": 0, "end": 30.04 }],
  "regions": [{ "start": 0, "end": 10, "box": [0.3, 0.1, 0.9, 0.85] }]
}
```

The renderer checks source identity, review coverage and actual caption alpha
bounds, including outline/paper/shadow. Prefer a low position, then try the upper
safe area if necessary. Keep top 10%, bottom 17% (portrait) and side margins
clear. Never cover a face to retain a fixed position. If neither area fits,
return caption_incomplete with the clean source and the offending interval.
Do not silently add blank panels, crop the subject, change aspect ratio, shrink
text until unreadable or pay for new footage. Ask for a composition repair only
when needed. New scene prompts should leave a **compact** plausible text location;
never reserve an empty half-screen.

## Review the boxes on the source pixels and lock the map

Before burning, draw the proposed boxes on the actual clean frames:

```bash
python3 "${HF_WORKFLOWS}/video-montage/scripts/caption_regions.py" prepare \
  --video final.mp4 --srt caps.srt --regions protected_regions.json \
  --clean-evidence clean-evidence/evidence.json --out-dir region-evidence
```

Open **every** returned `region-evidence/sheet-*.jpg` through foreground
`sandbox_exec.image_paths`, one sheet per call within 512 KiB. Each sample has three views: clean pixels, proposed boxes, and **unprotected
pixels** with the exact protected union hidden in dark gray. In the third view,
look specifically for escaped fingers, cream on fingertips, mouth/chin edges,
product labels, lids and baked text. No protection padding is added to this view. Coordinates are
relative to the source image, never to the surrounding contact sheet. Inspect
mouth and chin inside the face box, both moving hands, complete product labels,
and other essential subjects. Open individual annotated frames where ambiguous.
The boxes must contain the subjects throughout each interval, including cuts and
motion between samples. The tool does not detect missing faces automatically.

Copy `region-review-template.json` to `region-review.json`. Review every sample
individually. First scan the **unprotected** view and populate
`unprotected_subjects` with the visible essential fragments, for example
`["raised index fingertip with cream at upper right"]`. An empty array means the
remaining pixels contain only permissible background, not that most of a subject
is protected. Then set `subjects_covered` and add specific notes about the
unprotected pixels. Unseen entries stay null; any essential fragment means false.
Do not fill a whole cue/group with identical all-clear conclusions. A hand box
must contain every fingertip, including separated fingers, not only the palm.
Open the full-resolution `*-unprotected.jpg` beside its clean/annotated source
whenever a small fragment is ambiguous. If the second map still leaves a subject
exposed, stop with `caption_incomplete` before rendering; the review receipt does
not detect semantic mistakes for you. Never generate all-true answers from
coordinates, a prompt, or successful rendering.

```bash
python3 "${HF_WORKFLOWS}/video-montage/scripts/caption_regions.py" verify \
  --video final.mp4 --srt caps.srt --regions protected_regions.json \
  --clean-evidence clean-evidence/evidence.json \
  --evidence region-evidence/region-evidence.json --review region-review.json \
  --receipt region-review-receipt.json
```

The receipt binds the source, SRT, exact map, marked frames and explicit decisions.
**Budget per clean source: at most two maps (initial plus one correction), and two
render attempts (initial plus one retry).** Correct a box only from visible evidence
before the first render, then regenerate marked evidence and review. The first
render freezes that exact map, even when placement fails. Never shrink, delete,
replace or move boxes after a render failure to create space for captions.

A single render retry may re-chunk the same spoken words using the actual word
clock, or adjust readable styling. If SRT changes, regenerate clean and annotated
evidence and review with the frozen map. Do not lower STT verification thresholds,
change speech timing, remove words, change profiles or edit helper scripts to pass.
At budget exhaustion or unresolved subject coverage, return `caption_incomplete`
with the durable clean master and offending interval. Do not upload a final success.

Budget state lives under `~/.higgsfield/caption-guards`, keyed by source bytes;
renaming input/output files does not reset it. Never delete/modify that state or
restart the sandbox to reset retries. Preserve the clean master and stop if the
state is lost. This is a local workflow guard, not an adversarial sandbox boundary.

## Burn once with shared guarded geometry

Default is compact white outlined text in the original case, no plate, no
animation. Explicit paper/caps/font choices remain binding. Paper scenery alone
does not request paper captions. UGC retains its Metropolis face and compact
size (about 50px at 1920 height); use --font-key metropolis below. Standalone and
Faceless use montserrat unless another covering face was requested.

```bash
python3 "${HF_WORKFLOWS}/video-montage/scripts/subtitle_paper_burn.py" \
  --in final.mp4 --srt caps.srt --out final_subbed.mp4 \
  --style bold --no-caps --font-key montserrat --stroke-frac 0.045 \
  --profile safe --protected-regions protected_regions.json \
  --region-review region-review-receipt.json
```

UGC uses --profile safe
--font-key metropolis --fontsize-frac 0.02604 --stroke-frac 0.12 (up to two short
balanced lines). Explicit paper uses --style paper and a covering handwritten
font. Preserve exact SRT windows; never extend holds across unchecked motion.
Do not use --profile default or the old fixed-position clean/ASS burners as a
fallback for a placement failure. make_captions.py remains available for legacy
ASS/hook assets, but does not implement subject-aware speech-caption delivery.
Missing fonts/dependencies must be resolved or reported, never bypass clearance.

## Verify the rendered file independently

Extract new evidence from **the final burned MP4**, not the clean source:

```bash
python3 "${HF_WORKFLOWS}/video-montage/scripts/caption_evidence.py" prepare \
  --video final_subbed.mp4 --srt caps.srt --out-dir final-evidence
```

Open every sheet and all ambiguous original frames. Check each sample for actual
caption presence/correct wording, no clipped glyphs, no face/product/diagram/text
overlap and readable placement. Compare speech timing against audio too. Never
infer these findings from the renderer's coordinates or say "frame-by-frame" for
a sampled inspection. Copy review-template.json to review.json, then fill each
frame's clear/text_ok booleans and a brief concrete observation in notes.
A failed or uninspected frame must remain false/null. Do not prefill all PASS.
Review must be based on viewing the artifacts, not the source code or prompt.

```bash
python3 "${HF_WORKFLOWS}/video-montage/scripts/caption_evidence.py" verify \
  --video final_subbed.mp4 --srt caps.srt \
  --evidence final-evidence/evidence.json --review review.json \
  --receipt final_subbed.mp4.caption-review.json
```

This checks evidence hashes, every required sample and all review results.
It does not recognize faces itself. A failed rerun invalidates the old receipt.
After any video/transcript change, regenerate evidence and review again.
Return the exact-file caption-review receipt, layout receipt, SRT, protected map,
annotated region evidence/review/receipt and clean source with the finished video. Do not upload a caption-required success until
this gate and the caller's audio/duration/word-coverage checks pass.

### Readability failures

The guarded renderer enforces a minimum font size of 2% of frame height (at least
14px). If a cue cannot fit at that size, re-chunk it using the existing word
clock; preserve every word and pause. Never discard a third line or shrink below
the floor. Malformed or empty SRT blocks fail the whole burn, not just that cue.
An explicitly supplied font file must exist. Resolve missing resources or report
the failure; do not claim an unavailable requested font was used.
