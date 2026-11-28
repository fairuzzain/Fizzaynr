---
name: magi-2
description: MAGI-2-style cinematic video with sound - long, timed, multi-shot prompts written to Sand AI's MAGI-2 rules (overview, fixed characters, timed shot list, one camera move per shot, physical light, Audio line) - but EVERY generation runs on the user's Nexabot API - character/start images with Nexabot img, video with Nexabot t2v / sfv / i2v (up to 3 reference images) / r2v / extend, voice with Nexabot tts, music with Nexabot music. Clips are 15 s; longer films are split by shot ranges or extended, then joined and checked with ffmpeg. Use when the user types /magi-2, pastes a MAGI-2 / Seedance-style shot-list prompt, or asks for a MAGI-2 video. Higgsfield is not used unless the user explicitly asks to spend Higgsfield credits.
argument-hint: "[prompt or shot list] [reference images] [duration] [16:9|9:16]"
---

# MAGI-2 style, generated on Nexabot

The **prompt craft** comes from Sand AI's MAGI-2 (`references/prompting.md`). The **generating** is
all Nexabot (`https://nexabot.id`, the user's account): images, video, voice, music.
Higgsfield's real MAGI-2 model is documented in `references/higgsfield.md` and is used **only** if the
user explicitly asks to spend Higgsfield credits.

Scripts:
- `scripts/nexabot_run.py <body.json> <out> [--trim S]` - any Nexabot mode: submit, wait, download
  (fixes the file extension to what Nexabot actually returned, e.g. `.jpg`).
- `scripts/join.sh <out.mp4> <clip1> <clip2> ...` - joins clips into one film (same size/fps/audio).
- `scripts/fetch_and_check.sh <url|file://path> <out.mp4> <1|0 audio> <seconds>` - copy + check.

```
ROOT="$(git rev-parse --show-toplevel)"; set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a
S="$ROOT/.claude/skills/magi-2/scripts"
SLUG=<short-name>; RUN="${RUNS_DIR:-$ROOT/runs}/magi-2/$SLUG"; mkdir -p "$RUN/refs"
```
Key: `NEXABOT_API_KEY` in `.env` (or injected by the environment). Never print it.

## Nexabot modes (checked GET /api/v1/modes on 2026-11-28 - re-check, limits change)

| mode | input | output | cost |
|---|---|---|---|
| `img` | prompt, `aspect` 1=1:1, 2=16:9, 5=9:16 | still image (JPEG, ~768x1376 for 9:16) | 0.15 |
| `t2v` | prompt | 15 s video + sound, `ratio` 1=16:9 / 2=9:16, `resolution` 720/1080 | 0.3 |
| `sfv` | prompt + 1 image = first frame | 15 s | 0.3 |
| `i2v` | prompt + 1-3 "ingredient" images (characters, product, place) | 15 s | 0.3 |
| `r2v` | prompt + 1 video (+ optional 1 style image) | 10 s | 0.3 |
| `extend` | 1 video (+ optional prompt) | continues the video, always 1080p | 0.3 |
| `tts` | text + `voice` (e.g. Achernar, Kore, Puck) | voice-over | 0.02 |
| `music` | description / lyrics | music track | - |

Video model: Omni Flash 1.2, no watermark. Typical times: img ~20 s, video ~2-3 min.
Only 16:9 and 9:16 - other MAGI-2 ratios (21:9, 4:3, 1:1, 3:4) = render 16:9/9:16 then crop.
Nexabot's image model is not named by the API; it is whatever `img` runs (used here in place of
GPT Image / codex-image, on the user's instruction for this skill).

## MAGI-2 feature → Nexabot

| MAGI-2 | Nexabot |
|---|---|
| text only | `t2v` |
| start frame | `sfv` |
| start + end frame | `sfv`, end frame described in words (no true last frame) |
| image references (characters/product/place) | `i2v` with 1-3 images |
| video reference | `r2v` |
| audio reference (voice) | `tts` for lines, mixed in afterwards; the clip's own sound otherwise |
| 4-30 s single take | 15 s clips: split by shot ranges **or** clip 1 + `extend` (more continuous) |
| native audio | Omni Flash makes sound with the video; ask for "no music" in the Audio line |
| 1080p | `resolution: 1080` |

## Steps

1. **Brief.** From the user's text: characters, look, duration, ratio, shot list, dialogue, sound.
   Missing reference images → make them in step 3. Tell the user in one line what changes vs. real
   MAGI-2 (15 s clips, 16:9/9:16 only, 1080p not 4K, `@Image N` tags rewritten in words).
2. **Plan the clips.** Duration ≤ 15 s → one clip. Longer → split the shot list at a natural break
   into ~15 s parts (30 s → S-ranges of ~15 s each) and re-time each part to 0-15 s. If one
   unbroken take matters more than shot accuracy, use clip 1 + `extend` instead.
3. **Reference images (Nexabot `img`).** One full-body character sheet per hero (aspect 5),
   describing face, hair, build, outfit, footwear, setting light. Run in parallel:
   `python "$S/nexabot_run.py" "$RUN/refs/kitty.json" "$RUN/refs/kitty"` (extension is added).
   Look at them (contact sheet with ffmpeg `hstack`) and send them to the user. If the user supplied
   images, use theirs instead. Max 3 images per `i2v` clip.
4. **Prompts.** Follow `references/prompting.md`: overview → "The woman in the first image is
   NAME: ..." for each reference → look/physics/camera/light block (shared by every clip, so
   characters and grade match) → `Shot list, 15 seconds, hard cuts:` with `0-1.5s: ...` lines →
   `Audio:` line last (dialogue in quotes, in its own language; diegetic SFX; "no music" if wanted).
   Keep the user's wording where it works; turn "No X" locks into positive descriptions.
   Long prompts are fine (~4,000 chars tested). Delegate drafting to
   `python "$ROOT/tools/llm.py"` when its keys are set; otherwise write it yourself (say so in one line).
   Save each as `$RUN/clipA_prompt.md` and the request as `$RUN/clipA.json`:
   `{"mode":"i2v","ratio":1,"resolution":1080,"prompt":"...","media":["refs/kitty.jpg","refs/sena.jpg"]}`
   (media paths are relative to the json; sent as data URIs).
5. **Generate (all clips in parallel).**
   `python "$S/nexabot_run.py" "$RUN/clipA.json" "$RUN/clipA.mp4"` (& for each clip, then `wait`).
   On a timeout the job can still be downloaded within 60 min - do not resubmit blindly.
   Extend route: generate clip A, then `{"mode":"extend","ratio":1,"prompt":"<next shots>","media":["clipA.mp4"]}`.
6. **Check.** For each clip: `bash "$S/fetch_and_check.sh" "file://$RUN/clipA.mp4" "$RUN/check.mp4" 1 15`
   and a contact sheet (frames every ~2 s, `hstack`/`vstack`) - look at it: same faces as the refs,
   right outfits, shots in order, no text. Re-run only a clip that is clearly wrong (0.3 credit).
7. **Join.** `bash "$S/join.sh" "$RUN/final.mp4" "$RUN/clipA.mp4" "$RUN/clipB.mp4"`, then check the
   final with `fetch_and_check.sh ... 1 <total seconds>`. Send the final film and the contact sheet.
8. Vertical delivery → `reel-export`. Dialogue that came out wrong → `tts` the line and mix it in
   with ffmpeg at the shot's time.

## Don'ts
- Don't call Higgsfield (no quotes, no generation) unless the user asks for Higgsfield by name.
- Don't use codex-image / OpenAI images in this skill - images come from Nexabot `img`.
- Don't paste `@Image 1` style tags into the prompt; name what each reference image shows.
- Don't fake a second shot by stretching or looping a clip; generate it.
- Don't print or commit the Nexabot key.
