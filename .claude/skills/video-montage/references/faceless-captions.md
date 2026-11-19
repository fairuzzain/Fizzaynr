# Faceless Studio captions

Video Montage owns transcription and burning. Read subtitles.md for actual-audio
word timing and transcript checks; this profile overrides its subject-clearance
placement/review steps. Do not load caption-clearance.md for Faceless.

Keep the finished cut and original audio. With a centered assembly sidecar
containing speech_abs_s, use --per-block with clean takes. Explainer fixed-window
sidecars lack that field: use final audio with --mixed and matching --script.
Stills use narration; without matching authored text use actual-audio STT.
Captions OFF skips caption generation.

Always place captions **bottom center**, at one fixed baseline for the whole
video. The renderer reserves bottom 17% / side 11% in portrait and bottom 10% /
side 7.5% in landscape or square. Size scales with frame height and fits the
available width, using one readable font size across all cues. Default compact
sentence-case white outlined single-line text; no plate or animation. Paper is
an explicit choice, never inferred from paper scenery.

```bash
python3 "${HF_WORKFLOWS}/video-montage/scripts/subtitle_paper_burn.py" \
  --in final.mp4 --srt caps.srt --out final_subbed.mp4 \
  --style bold --no-caps --font-key montserrat --stroke-frac 0.045 \
  --profile faceless
```

Do not author protected-region maps, search around objects, move captions up or
sideways, or run dense caption_evidence.py review for this profile. Do not reject
an ordinary subtitle because scenery passes behind it. Compose new scenes with
important content above the lower text area; no blank panels or empty half-screen.

Use up to four words / 42 chars per explainer cue. Preserve all spoken words and
actual timing. Re-chunk long phrases from the word clock instead of shrinking
below the readable floor. Do not extend cues through pauses.

After burning, confirm duration and audio are preserved, verify transcript and
cue timings, and inspect representative frames from each scene, including the
longest cue, for readability and edge clipping. One render and one targeted
repair if needed; no repeated object-clearance passes. The .captions.json file
records exact-file lower placement, not a claim of visual inspection. Return it
with the SRT and final video. Keep the clean source. Faceless structural/timing
QC remains required before delivery; no separate caption-review.json is needed.
