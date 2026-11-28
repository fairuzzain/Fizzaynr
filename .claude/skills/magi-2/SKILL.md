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
| `tts` | text + `voice` (e.g. Leda bright, Kore low/firm, Puck) | voice-over WAV | 0.15 |
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
2. **Plan the clips - shot by shot.** Tested 2026-11-28: one 15 s clip with a 10-shot timed list
   comes out as one generic scene (most shots missing). One clip **per 1-2 beats** follows well.
   Group the user's shot list into ~10-15 beats, one Nexabot clip each, and plan how many seconds
   of each you will use (sum = target length). Only for a ≤ 15 s single take use one clip.
3. **Images (Nexabot `img`).**
   - One full-body character sheet per hero (aspect 5): face, hair, build, outfit, footwear, light.
   - One start frame (aspect 2 or 5) per scene that has no hero in it yet, or has props/extras
     (e.g. the couple with a puddle, the grandmother and dog on the crossing, the sedan).
   - Run in parallel: `python "$S/nexabot_run.py" "$RUN/refs/kitty.json" "$RUN/refs/kitty"`.
   - Make a contact sheet (ffmpeg `hstack`), look at it, send it to the user. User images win.
4. **Clip prompts (short, ~1,000-1,500 chars each).** Per clip:
   - hero shot → `i2v` with the character sheets (+ one scene image, max 3):
     "The woman in the first image is NAME (look)." + **one beat** with camera + `Audio:` line;
   - no-hero or scene-setting shot → `sfv` from its start frame + the beat.
   - Append one shared look/physics/camera block to every clip so the grade matches.
   - Positive wording; dialogue in quotes in its own language; "no music".
   Drafting: `python "$ROOT/tools/llm.py"` when its keys are set, else write it (say so in one line).
   Save as `$RUN/clips/cNN.json` (`media` paths relative to the json file).
5. **Generate all clips in parallel** (6 at a time is fine):
   `ls "$RUN"/clips/*.json | xargs -P 6 -I{} sh -c 'python3 "$S/nexabot_run.py" {} "${0%.json}.mp4"' {}`
   or a loop. ~2 min each. On a timeout don't resubmit blindly (job downloadable for 60 min).
6. **Review.** One sheet per clip, frames every 1.5 s with timestamps
   (`fps=2/3,scale=192:-1,drawtext=...%{pts\:hms}...,tile=10x1`), stacked with `vstack`. For each
   clip write the usable window: `cNN start end speed` in `$RUN/edit.txt` (speed 1.25-1.33 sells
   superspeed shots). Re-generate only a clip with no usable window (0.3).
7. **Cut.** For each line of `edit.txt` (use `ffmpeg -nostdin` inside `while read` loops):
   `-ss start -to end -vf "delogo=x=1695:y=855:w=95:h=95,setpts=PTS/speed,fps=24" -af atempo=speed`
   (the Gemini sparkle sits bottom-right: 1920x1080 → 1695,855,95,95; 1080x1920 → 855,1695,95,95).
   Concat with re-encode and `fps=24,setpts=N/24/TB` (stream copy drifts to 23.92 fps).
8. **Dialogue.** Nexabot clips rarely lip-sync the exact line. `tts` each line with **only the words**
   in `prompt` (any delivery note gets read aloud), `atrim` to the speech, `adelay` to the shot,
   duck the clip sound under it (`volume='if(between(t,a,b),0.35,1)':eval=frame`), `amix`
   `normalize=0`, `alimiter`. End with a 0.25 s fade if the brief says cut to black.
9. **Check & deliver.** `fetch_and_check.sh "file://$RUN/final.mp4" ... 1 <seconds>` plus a
   1.5 s frame sheet of the final; send both. Vertical delivery → `reel-export`.

Alternative for a single continuous take > 15 s: clip 1, then `extend` with the next beats.
`scripts/join.sh` joins whole clips (no trimming) when no cut list is needed.

Tested run (2026-11-28, "PINKSHIFT: Morning Rush V2", 18-shot 30 s brief): 5 images + 13 clips +
2 tts ≈ 5 Nexabot credits; every shot present except a weak overtake; faces consistent via `i2v`.

## Don'ts
- Don't call Higgsfield (no quotes, no generation) unless the user asks for Higgsfield by name.
- Don't use codex-image / OpenAI images in this skill - images come from Nexabot `img`.
- Don't paste `@Image 1` style tags into the prompt; name what each reference image shows.
- Don't fake a second shot by stretching or looping a clip; generate it.
- Don't print or commit the Nexabot key.
