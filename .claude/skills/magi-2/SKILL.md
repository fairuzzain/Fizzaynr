---
name: magi-2
description: Generate a 1080p video with native audio on Sand AI's MAGI-2 through the Higgsfield connector - text-to-video, first frame, first+last frame, or up to 10 image / 5 video / 5 audio references, 4-30 s, 21:9 to 9:16. Quotes the credit cost and waits for the user's OK before spending. Includes Sand.ai prompt rules, batch/variants, and a Nexabot fallback mapping. Use only when the user names MAGI-2 / magi_2 / /magi-2 or asks for it on Higgsfield; other video work stays on Nexabot.
argument-hint: "[prompt] [start image] [end image] [duration 4-30] [16:9|9:16|...]"
---

# MAGI-2 (Sand AI) on Higgsfield

Spec pulled from the Higgsfield catalog (`models_explore` get `magi_2`) on 2026-11-26.
Prompt guide: `references/prompting.md` (from Sand.ai's own docs). Scripts: `scripts/fetch_and_check.sh`
(download + check), `scripts/nexabot_run.py` (Nexabot fallback).
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

1. **Brief.** Get subject, mode (text / frames / references), duration, aspect ratio, audio on/off,
   and how many takes. Defaults: 5 s, 16:9 (9:16 for Reels/TikTok), audio on, enhance off, 1 take.
   For a new idea, test at 4-5 s first; make the long version once it works.
2. **Prompt.** Read `references/prompting.md` (Sand.ai's structure: overview, fixed subject, timed
   beats covering the clip, one camera move, physical light, `Audio:` line last, no negation).
   Delegate the writing: put the brief and the rules from that file into `$RUN/brief.md`, run
   `python "$ROOT/tools/llm.py" --prompt-file "$RUN/brief.md" --out "$RUN/prompt.md"`, then skim and
   fix only what breaks the rules. Keep each prompt under 15,000 characters.
3. **Media** (skip for text-only). Pick one mode: frames (`start_image` [+ `end_image`]) **or**
   references (`image_references` / `video_references` / `audio_references`).
   - Missing still images: make them with `codex-image` (repo default).
   - Local files: `media_upload` with all files in one `files[]` call → `curl -X PUT --upload-file`
     each file to its `upload_url` (check HTTP 200) → `media_confirm` with `media_ids` and `type`
     (`image` / `video` / `audio`; one confirm call per type).
   - Web links: `media_import_url` (`type` image/video/audio or `auto`, max 50 MB) returns a
     confirmed media_id - no upload step.
   - A finished Higgsfield job can be passed as `value` directly (its job_id).
   - Check reference clips first: `ffprobe` each video/audio is 2-30 s and the set is ≤ 30 s total.
4. **Destination.** Once per conversation, before the first generation, call `get_preferences`.
   - `auto_create_project: false` (default) → omit `folder_id`.
   - `true` → `create_project` once and pass its `default_folder_id` as `folder_id` on every call
     (quote, generate, batch item) in this conversation.
   - A project the user names wins over both; never change the saved preference for a one-off.
5. **Quote.** `estimate_video_cost` with the exact params (one quote per distinct request; for
   `count` > 1 the quote covers all takes). Tell the user the credits in one line and wait for a yes.
   Optionally show `balance` too.
6. **Generate.**
   - One request: `generate_video` with `params: {"ref": "<quote_ref>"}` so it runs exactly what was
     quoted. For 2-4 takes of the *same* prompt/media/settings, put `count` in the quoted params.
   - 2-12 *different* requests (several shots, several aspect ratios): `generate_video_batch` with
     `requests: [{"index": n, "params": {"ref": "<quote_ref n>"}}, ...]`. Keep each returned job_id.
   - **Free-trial unlimited generations:** leave `use_unlim` out. If the account holds an allowance
     for MAGI-2, the call submits nothing and returns `unlim_choice`. Ask the user that question,
     then call again with the same params plus `use_unlim: true` (caps count to 1) or `false`
     (credits). Never set it yourself, and never set `use_free_gens` unless the user asks.
   - On a timeout, do **not** resubmit: the job may exist. Reuse any returned job_id.
7. **Wait.** `jobs_wait` with up to 12 `{index, job_id}` per call (≤ 15 s each; call again after
   `poll_after_seconds` until `all_terminal`). A failed / nsfw / ip_detected job carries `error` -
   tell the user in words. For batch jobs, show them once with `show_generation_by_ids` at the end.
8. **Save & check.** For each done job:
   `bash "$ROOT/.claude/skills/magi-2/scripts/fetch_and_check.sh" "<result_url>" "$RUN/magi2_<n>.mp4" <1|0 audio> <seconds>`
   It downloads, then prints size/fps/duration/audio and exits 1 with a WARN line if the clip is
   under 1080p, has no audio when audio was on, or is off the asked length. Keep `$RUN/prompt.md`
   and a `$RUN/params.json` copy of what was sent next to the clips.
9. Vertical delivery for socials: hand the file to `reel-export`.

## Nexabot fallback (no Higgsfield credits, or the user asks for Nexabot)

Nexabot (repo default, `https://nexabot.id`, model Omni Flash, 0.3 credit per clip) has no MAGI-2.
Map the request, keep the same prompt (it reads fine as a Veo-style prompt), and say what changes:

| MAGI-2 mode | Nexabot mode | difference |
|---|---|---|
| text only | `t2v` | fixed ~15 s, `ratio` 1 = 16:9 / 2 = 9:16 only, `resolution` 720/1080 |
| `start_image` | `sfv` (1 image) | same limits |
| `start_image` + `end_image` | `sfv` with the end frame described in words | no true last frame |
| `image_references` (1-3) | `i2v` (1-3 images) | max 3 images |
| `video_references` (1) | `r2v` (1 video + optional 1 image) | 10 s output |
| `audio_references` | none | drop, or add the audio in the edit |

Run with the bundled script (key from `NEXABOT_API_KEY` / `.env`, local media paths sent as data URIs):
```
python "$ROOT/.claude/skills/magi-2/scripts/nexabot_run.py" "$RUN/body.json" "$RUN/clip.mp4" --trim <seconds>
```
`body.json` e.g. `{"mode":"t2v","ratio":2,"resolution":1080,"prompt":"..."}`. Check
`GET https://nexabot.id/api/v1/modes` first; limits change. `--trim` cuts the ~15 s clip to the asked
length. Other aspect ratios (21:9, 4:3, 1:1, 3:4) need a crop afterwards. Then run
`fetch_and_check.sh "file://$RUN/clip.mp4" ...` to check it. Tested 2026-11-26: t2v 9:16 1080p,
~2 min, 0.3 credit - scene and look follow the prompt well, timed camera beats only loosely.

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
- Don't put "no ..." / "without ..." in the scene description; describe what is there.
- Don't resubmit after a timeout, and don't retry a rejected free/unlim request on credits unasked.
