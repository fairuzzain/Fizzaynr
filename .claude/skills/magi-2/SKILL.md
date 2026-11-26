---
name: magi-2
description: Generate a 1080p video with native audio on Sand AI's MAGI-2 through the Higgsfield connector - text-to-video, first frame, first+last frame, or up to 10 image / 5 video / 5 audio references, 4-30 s, 21:9 to 9:16. Quotes the credit cost and waits for the user's OK before spending. Use only when the user names MAGI-2 / magi_2 / /magi-2 or asks for it on Higgsfield; other video work stays on Nexabot.
argument-hint: "[prompt] [start image] [end image] [duration 4-30] [16:9|9:16|...]"
---

# MAGI-2 (Sand AI) on Higgsfield

Spec pulled from the Higgsfield catalog (`models_explore` get `magi_2`) on 2026-11-26.
Higgsfield has no `/magi-2` recipe; it is a plain model run through `generate_video`.

**Paid connector.** Repo default for video is Nexabot (CLAUDE.md). Use this skill only when the
user asks for MAGI-2 / Higgsfield by name. Always quote first and get a yes before generating.

## Model

| field | value |
|---|---|
| model id | `magi_2` |
| output | video + native audio, **1080p only** |
| `duration` | whole seconds, 4-30 (default 5) |
| `aspect_ratio` | `21:9` `16:9` `4:3` `1:1` `3:4` `9:16` |
| `generate_audio` | bool, default `true` |
| `enhance_prompt` | bool, default `false` (model rewrites the prompt) |
| `seed` | 0-4294967295, omit for random |

Media roles (`params.medias[] = {role, value}`; value = Higgsfield media_id or a job_id, never a URL):

| role | rule |
|---|---|
| `start_image` | first frame. **Cannot be combined with any reference media.** |
| `end_image` | last frame. **Requires `start_image`.** |
| `image_references` | up to 10 images |
| `video_references` | up to 5 clips, 2-30 s each, 30 s total |
| `audio_references` | up to 5 clips, 2-30 s each, 30 s total |

So there are two exclusive modes: **frames** (start, optional end) or **references** (any mix of
image/video/audio refs). Text-only needs no media.

Price (quoted 2026-11-26): **2.5 credits / second** - 5 s = 12.5, 10 s = 25, 30 s = 75.
Audio on/off and aspect ratio did not change the quote. Re-quote every run; prices move.

## Steps

```
ROOT="$(git rev-parse --show-toplevel)"; set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a
SLUG=<short-name>; RUN="${RUNS_DIR:-$ROOT/runs}/magi-2/$SLUG"; mkdir -p "$RUN"
```

1. **Brief.** Get subject, mode (text / frames / references), duration, aspect ratio, audio on/off.
   Defaults: 5 s, 16:9 (9:16 for Reels/TikTok), audio on, enhance off.
2. **Prompt.** For anything beyond one line, delegate: write `$RUN/brief.md` (shot, camera move,
   action beats, sound/dialogue, style, the rules above) and run
   `python "$ROOT/tools/llm.py" --prompt-file "$RUN/brief.md" --out "$RUN/prompt.md"`, then skim.
   Write the prompt as one continuous shot: subject, action over time, camera, light, and a
   `Sound:` line (ambience, SFX, any spoken line in quotes) since audio is generated with the picture.
   With `end_image`, describe the motion that gets from frame A to frame B.
3. **Upload media** (skip for text-only). Still images the user lacks: make them with
   `codex-image` (repo default). Then `media_upload` (one call, `files[]`) → `curl -X PUT` each file
   to its `upload_url` → `media_confirm` with the right `type`. A prior Higgsfield job_id can be
   passed directly.
4. **Quote.** `estimate_video_cost` with the exact params. Tell the user the credits in one line
   and wait for approval. Optionally check `balance` first.
5. **Generate.** `generate_video` with `params: {"ref": "<quote_ref>"}` so it runs exactly what was
   quoted. Do not resubmit on a timeout; reuse the returned job id.
6. **Wait & save.** `jobs_wait` (≤15 s per call) until terminal, then download the result URL to
   `$RUN/magi2_<n>.mp4` and check it: `ffprobe -v error -show_entries stream=codec_type,width,height,duration -of csv=p=0 "$RUN/magi2_1.mp4"`
   (expect 1080p video plus an audio stream when `generate_audio` was on).
7. Vertical delivery for socials: hand the file to `reel-export`.

## Example params

Text-to-video:
```json
{"model":"magi_2","prompt":"...","duration":8,"aspect_ratio":"9:16","generate_audio":true}
```
First + last frame:
```json
{"model":"magi_2","prompt":"...","duration":6,"aspect_ratio":"16:9",
 "medias":[{"role":"start_image","value":"<media_id>"},{"role":"end_image","value":"<media_id>"}]}
```
References (character + voice):
```json
{"model":"magi_2","prompt":"...","duration":10,"aspect_ratio":"16:9",
 "medias":[{"role":"image_references","value":"<media_id>"},{"role":"audio_references","value":"<media_id>"}]}
```

## Don'ts
- Don't mix `start_image`/`end_image` with any `*_references` - the request is rejected.
- Don't pass https URLs in `medias`; upload or `media_import_url` first.
- Don't set `use_unlim` / `use_free_gens` unless the user asks.
- Don't generate without a quoted, approved cost.
