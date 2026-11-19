---
name: ugc-video
description: >-
  Produce a finished UGC video: creator review or productless creator story,
  product-only off-screen voiceover, creator-led unboxing, wearable try-on,
  step-by-step tutorial, or creator-led website tour using real screenshots.
  Select one format from the requested deliverable; a product URL alone does
  not imply a website tour. Missing assets or duration are intake gaps only
  after a production request. Exclude scripts, text-only plans, generic ads,
  still images, footage edits, testimonials and impersonation. Silent product-only
  commercials use ordinary generation, not the voiceover product format.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# UGC video

One shared execution pipeline, six format profiles. Select exactly one profile
from the user's intent; review is the default for an otherwise unspecified UGC
video. A long video is one stitched deliverable, not an implicit series.

| Format   | Requested result | Read |
| -------- | ---------------- | ---- |
| review   | One consenting/generated adult creator demonstrates a product or tells a supplied story; product optional | [Review](references/formats/review.md) |
| product  | Product is the hero, off-screen native voiceover; no on-camera speaker | [Product](references/formats/product.md) |
| unboxing | Visible creator opens packaging and reacts | [Unboxing](references/formats/unboxing.md) |
| try-on   | Creator wears an item and demonstrates fit/texture | [Try-on](references/formats/try-on.md) |
| tutorial | Creator demonstrates actual use with Step N labels | [Tutorial](references/formats/tutorial.md) |
| website  | Real captured website/app/page appears with a presenter | [Website](references/formats/website.md) |

A product URL identifies the product unless its page itself must appear. Do not
change formats because a URL was supplied. Read only the selected profile and
its prompt references. Format is workflow state, never an invented tool argument.

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
- Workflow scripts are preinstalled at `${HF_WORKFLOWS}/ugc-video/scripts/` inside
  the sandbox. Run them from there. Load detailed workflow references with
  `get_workflow_bundle_file` only when the phase names them.
- Use `generate_image_batch` and `generate_video_batch` for headless workflow
  stages. Each request is `{index, params}`, `params.count` is `1`, and one call
  contains at most twelve requests. Keep stable indices across retries.
- Wait on returned `{index, job_id}` pairs with `jobs_wait` in groups of at most
  twelve and `timeout_seconds:15`. If `all_terminal:false`, wait the returned
  `poll_after_seconds` and poll only active or retryable lookup-failed jobs.
  Freeze completed indices. Never poll jobs through a legacy singleton status
  tool.
- Never pass a batch `submission_failed` entry without a `job_id` to
  `jobs_wait`. Retry only rejected or failed indices, never the whole stage.
- `unlim_choice` means no job was submitted. Ask its message and resubmit the
  unchanged request with the user's `use_unlim` choice; never choose for them.
- Do not substitute a different model when a locked model is unavailable.
  Report the incompatible slug and stop that phase.

## Shared execution — before generation

1. Resolve format-specific intake and safety gates before spending. Reuse supplied
   creator/product assets. Review supports productless requests: never invent a
   product or demand one. Product-only skips creator generation. Website uses
   real captures and no boards; retain its caption-style and capture-failure gates.
2. Run [duration planning](references/duration.md); use its exact clip durations.
3. Read the selected profile's actual prompt references before writing prompts.
   Preserve user-authored beats, authorized identity, real product labels and
   geometry. Approved claims are an allowlist, not inspiration for stronger claims.
   Never fabricate personal use, endorsements, results, measurements or reviews.
4. Physical formats follow [board execution](references/boards.md): GPT Image 2.6
   → Seedream 5 Pro → visual inspection → Seedance 2.5. Cleanup is mandatory;
   inspection alone is not cleanup. Keep raw and cleaned IDs/URLs separately.
   Only the completed inspected cleaned result may seed another board or video.
   Stop dependent generation if cleanup fails; never fall back to the raw board.
5. Compile every clip prompt before submission. Use the selected format's ordered
   reference roles, native audio, `seedance_2_5`, `mode:"omni_reference"`, and
   `generate_audio:true`. Do not add a separate narration/TTS job. Follow batch
   and upload limits in the runtime contract above, not another host's schema.
6. Inspect completed clips for identity/product continuity, actual duration,
   framing, speech and intended text. Tutorial Step N labels are required;
   other generated text is forbidden. Correct only identified failed clips.
7. For assembly and requested captions load video-montage directly, passing ordered
   accepted clip URLs, authored words, language, look and any website hook/card
   clearance. Physical captions/post package are opt-in; website retains its
   upfront selection. Caption scripts belong exclusively to video-montage.

## Failures and delivery

A timeout or unknown outcome is not a failed submission: poll existing IDs first.
Never resubmit a whole batch because one index failed. An explicit technical
failure may be retried once within authorized spending; a bare failed status with
no reason remains unknown. Moderation stops the dependent path; do not switch
providers, regenerate identities, remove references or use text-to-video to bypass it.
Never replace a locked model silently. Retain successful artifacts for recovery.
Return the confirmed finished video and requested chat-only post package. Check
actual output metadata and encoded frames; job completion alone is not quality proof.

---
(Shared sections: see ../_shared/bundled-scripts-note.md and ../_shared/unlimited-generations-use_unlim.md)
