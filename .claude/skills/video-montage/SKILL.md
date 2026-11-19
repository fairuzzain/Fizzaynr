---
name: video-montage
description: >-
  Assemble existing clips into a finished video, add or change a soundtrack, or burn/restyle speech captions. Owns all subtitle transcription, authored-word alignment, placement, burning and final caption checks. Use for a requested rendered video; exclude text-only subtitle translation/correction, transcription, SRT/VTT delivery, analysis, native Higgsedit project authoring and generative edits.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Video montage

Own the finished-file edit and all caption production. Preserve the original clean
master. Re-evaluate each follow-up: a request to translate words is a text task,
not another render. Missing video is an intake gap only for a requested video edit.
Native editable Higgsedit projects and motion graphics use video-editing and
motion-craft; do not turn an ordinary assembly into a native composition.

## Runtime contract

- Use only tools exposed by the current full MCP host.
- Use native client elicitation when it is available; otherwise ask one concise
  normal-chat question. Never invent an elicitation tool name.
- For a local user attachment in an Apps UI-capable client, call
  `media_upload_widget`. When the client can provide bytes directly, use
  `media_upload`, PUT the bytes to its `upload_url`, then call `media_confirm`.
  Keep the returned `media_id`.
- Import an authorized HTTPS image URL with `media_import_url` before generation
  and reuse the returned `media_id`; full-profile generation inputs never receive
  raw URLs.
- Run ffmpeg, Python, downloads, probes, transcription, assembly, and uploads
  only through `sandbox_exec`, never a client-local shell.
- For a sandbox-created output, call `media_upload` before the producing
  `sandbox_exec`, PUT the file to its `upload_url` in that same sandbox command,
  and call `media_confirm` only after HTTP 200. Never pass a sandbox path to
  any attachment-only helper.
- Workflow scripts are preinstalled at `${HF_WORKFLOWS}/video-montage/scripts/` inside
  the sandbox. Run them from there. Load detailed workflow references with
  `get_workflow_bundle_file` only when the phase names them.

## Select the requested edit

- Standalone speech captions or Faceless clean masters: read [subtitles](references/subtitles.md).
- UGC optional hook/captions: read [UGC captions](references/ugc-captions.md).
- Website UGC screenshot composite: read [website captions](references/website-captions.md).
- For standalone and UGC captions also read [caption clearance](references/caption-clearance.md).
  Its measured placement and final-frame inspection override fixed-size examples.
  Faceless preserves its supplied fixed-bottom style and orientation-aware sizing.

The calling workflow supplies the finished master, authored script, language,
requested look and any per-block voice files/assembler sidecar. Do not re-ask
resolved choices. Caption an already assembled master without rearranging clips
or remixing its audio. Transcribe actual audio, verify authored wording, burn,
then inspect the encoded result. A transcript is not proof of a correct burn.

## Assembly and soundtrack

Probe each source with ffprobe. Preserve the requested ordering, source resolution,
aspect ratio and timing. Default to hard cuts; do not add transitions unasked.
For matching codecs, dimensions, fps and audio layouts, use an explicit ordered
concat manifest and ffmpeg concat demuxer with stream copy. If inputs differ,
normalize only what the requested output needs before concatenation; retain audio
sync and inspect cut boundaries. Never claim successful assembly from a command
exit alone: verify duration, streams, first/last frames and every join.

For a requested music change preserve speech, mix/duck to keep it intelligible,
and trim music to the measured edit. Do not add music when it was not requested.
Perform requested captions after the clean edit is complete. Reserve output upload
slots before the producing sandbox command, upload there, then confirm successful
outputs. Return one confirmed finished video and disclose any unverified stage.
