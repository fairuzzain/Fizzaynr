# UGC captions and optional hook

On-video text is **OFF by default** for the sibling UGC flows. Run this stage only
when the user opts into Subtitles, Hook or Both; generation must not bake text.

Timing comes from the **finished video's actual speech**, never planned beats or evenly
spread words. Keep authored text synchronized with the final takes; preserve brand
spelling and every spoken word. Save a JSON `script_manifest.json` with
`{"blocks":[{"vo_line":"the complete final spoken text"}]}` (or ordered blocks).

```bash
python3 "${HF_WORKFLOWS}/video-montage/scripts/audio_to_captions.py" output/final.mp4 \
  --mixed --language '<spoken-language-code>' --script script_manifest.json \
  --srt caps.srt --json caps.json --max-words 5 --max-chars 32
```

Use the actual spoken language. Inspect the transcript, alignment score, word coverage
and cue timing. If alignment fails, correct genuine display-form mismatches or retry
with a larger Whisper model; never lower the similarity gate to force a pass. If there
is no speech, report that fact and retain the clean video rather than invent captions.

Read [caption-clearance.md](caption-clearance.md) and execute its complete sequence:
clean-frame evidence → actual image inspection → protected regions → guarded safe burn
→ inspection of the encoded video → exact-file review receipt. Use `sandbox_exec`
`image_paths` to view the evidence directly. Keep the clean master durable before
rendering, and preserve its audio unchanged.

Use Metropolis with original case, compact outlined text, no plate or animation unless
requested. The shared guide specifies UGC sizing and the safe profile. There is no
fixed bottom-safe-zone shortcut: protect the moving face, hands, product labels,
website cards, existing hooks and tutorial text throughout every cue.

For an explicitly requested Hook or Both mode, place and inspect the hook in the clean
composition first, ending it at the actual first body-word boundary. Treat it as
protected existing text during speech-caption placement; do not duplicate spoken hook
words underneath it. Hook-only output needs no invented speech captions. An optional
hook is not permission to use an ASS speech-caption burner or skip final inspection.

Deliver the reviewed `output/final_captioned.mp4` together with its caption-review
receipt, layout receipt, SRT and clean source (supporting files may be one archive).
If placement or visual review cannot pass, return `caption_incomplete` with the clean
master and exact failing interval. Do not claim success from encoding alone.
