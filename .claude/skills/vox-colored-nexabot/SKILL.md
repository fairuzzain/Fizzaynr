---
name: vox-colored-nexabot
description: Vox Colored (Nexabot) - the /vox diorama explainer in vintage hand-tinted color (same aged-paper collage, keylined cutouts and giant numbers, colorized photos). Produce a researched, Vox-style news/politics explainer video end to end - current-events research, narration script, Nexabot TTS voice-over with word timestamps from a local faster-whisper pass, keyframes from the project style sheet (Nexabot img or Codex), Veo start-frame clips via the Nexabot API timed to the speech, and an ffmpeg final cut with music. Use when the user asks for a Nexabot Vox video, Vox Video without ElevenLabs/kie/Magnific, or runs /vox-colored. Same pipeline as vox-video-nexabot, colored style sheet and prompt system.
argument-hint: "[optional guidance: story/topic, number of chapters 1-4]"
---

# Vox-style news video, COLORED (Nexabot)

Identical pipeline to `vox-video-nexabot`, and **the /vox look in vintage hand-tinted color**:
the same composition, density and materials as /vox (aged ledger paper, newsprint, archival
maps, torn edges, layered photo cutouts with rough white keylines and offset red strokes, giant
numbers on torn labels, deep diorama), with the photos colorized like 1950s hand-tinted prints.
Earlier looks were rejected: v1 busy magazine collage (`assets/_archive/colored_v1/`) and v2
minimal flat color fields (`assets/_archive/colored_v2/`); do not use them.
Style board: `assets/style_reference_colored.png` (the approved v3 test frame).
Prompt rules: `guidelines/colored/`. Image prompts put the SHOT first, then `STYLE:` + the block.

Voice, video and (by default) images go through the **Nexabot API** (`NEXABOT_API_KEY`,
`https://nexabot.id`, 0.15 credit per request, refunded on failure). Word timestamps come from
a local faster-whisper pass. With `IMAGE_BACKEND=codex` the keyframes are made free by Codex
CLI with the style sheet attached. Note: a Nexabot *web* Unlimited plan does NOT cover API
requests; only the "API Unlimited" plan does (submit response then shows `"credit_cost": 0`).

Guidance from the user (may be empty): `$ARGUMENTS`

The output is a 16:9 journalism explainer made of **chapters**, each about 30 s and made of
4-8 clips. **Top priority: what is on screen matches what the narrator is saying at that
moment.** Every design choice below serves that.

Paths (run every command from the project root):

```
PY=".venv/Scripts/python"; [ -x "$PY" ] || PY=".venv/bin/python"   # Windows / macOS-Linux
S=".claude/skills/vox-colored-nexabot/scripts"
```

If `.venv` is missing: `python -m venv .venv && $PY -m pip install requests python-dotenv faster-whisper` (re-run the `PY=` line after creating it).

## 0. Parse guidance and check setup

- **Story**: whatever topic/story the guidance names. If none, you choose (step 1).
- **Chapters**: the number requested, default **1**, maximum **4** (cap and tell the user if more).
- Run `$PY $S/check_setup.py`. If it fails, tell the user exactly what's missing (key goes in
  `.env` as `NEXABOT_API_KEY`, faster-whisper in `.venv`, music in `assets/music/`) and stop.
  It also prints the credit balance.
- Create the run folder `runs/<YYYY-MM-DD>_<short-slug>/`; call it `$R`.

## 1. Research (always, even when the story is given)

Use WebSearch/WebFetch. Never write from memory: these are current events.
- No story given: survey today's top US/world news and politics and pick the story with the
  best mix of stakes for ordinary people, a clear explainable mechanism (a "why"/"how"), fresh
  developments in the last few days, and strong visual potential. Briefly say why you picked it.
- Gather from **at least 3 independent, reputable sources** (wire services, major papers,
  official data and primary documents). Pin down dates, numbers, who said what.
- Write `$R/research.md`: key facts with source URLs, numbers you might show on screen, the
  people involved (flag which are **public figures**), and what is still uncertain or disputed.

## 2. Script

Write `$R/script.json`:

```json
{"title": "...", "topic": "...", "chapters": [
  {"index": 1, "title": "...", "narration": "..."}]}
```

- About **75 words per chapter** (≈30 s; Nexabot TTS pace varies by voice). Plain spoken English, short sentences,
  no abbreviations the voice could misread, numbers written the way they should be spoken.
- Vox voice: open on a hook (a surprising fact, tension, or question), explain the mechanism,
  make it concrete with one or two hard numbers, end each chapter pulling into the next.
  Multiple chapters form ONE story arc (e.g. what happened → why → who it hits → what's next);
  only the final chapter resolves or lands the open question.
- Journalism standards: every claim must trace to `research.md`. Attribute contested claims
  ("critics say", "the White House argues"). Present major sides fairly. No invented quotes,
  numbers, or motives.
- Think visually while writing: each sentence or clause should suggest a picture.

### ✋ Checkpoint: the only approval stop

Show the user: the chosen story (and why, if you chose it), the narration per chapter, the
key sources, a rough visual beat list (one line per planned clip, marking any
public-figure clips), and the **credit estimate**: 0.15 × (chapters for TTS + clips for
video + clips for images when `IMAGE_BACKEND=nexabot`). **Wait for approval before any
paid API call.** Apply requested
edits and re-confirm only if the changes are substantial.

## 3. Voice-over + word timestamps

```
$PY $S/tts.py $R            # all chapters; --chapter N to redo one; --align-only re-aligns for free
```

Writes `audio/chapter_NN.wav` (Nexabot `tts`, voice `NEXABOT_VOICE`, default `Charon`; list
with `GET /api/v1/modes`) and `audio/chapter_NN.words.json` (per-word start/end: faster-whisper
timings mapped onto the script's own words). If a chapter prints a low "aligned" percentage,
listen to it: the voice may have skipped or misread words; regenerate that chapter.
Pacing: `SENTENCE_PAUSE` (default 0.6 s in `.env`) adds silence after every sentence plus `HEAD_PAUSE`/`TAIL_PAUSE` breath at the start/end, so clips stay on screen longer; the raw take is kept as `chapter_NN.raw.wav` (re-run `--align-only --pause X` to re-pace for free). With pauses a chapter of ~32 s speech lands near 37 s, which is fine. If the raw speech is outside 26-36 s, tighten or extend its narration in `script.json`
and regenerate that chapter (no need to re-ask the user for small length trims).

## 4. Split speech into clips

```
$PY $S/segment.py $R --auto     # proposes boundaries -> segments.json + plan.json
```

Then **review the split by meaning**: each clip should carry ONE visual idea, and a cut
should land where the subject of the narration changes. Edit `$R/segments.json` (per
chapter: index of the first word of each clip, starting at 0) and re-run
`$PY $S/segment.py $R` until it prints `OK`. The constraints are enforced by the script:
4-8 clips per chapter, each 1.5-5.75 s on screen. It assigns `gen_duration` 4 or 6.

`plan.json` now holds each clip's `narration`, its exact on-screen window, and
`word_times`: **clip-local times already shifted by the 0.25 s that is trimmed off every
generated video**. Use these numbers directly in prompts.

## 5. Write prompts (edit `plan.json`)

First **read `guidelines/colored/image-prompts.md` and `guidelines/colored/video-prompts.md` in full, every
run**. They define the style blocks, the SHOT formula, AUDIO and AVOID blocks. Follow them,
with the pipeline adaptations below. For every clip set:

| field | value |
|---|---|
| `public_figures` | list of real public people depicted, e.g. `["Jerome Powell"]`, else `[]` |
| `image_prompt` | prompt for the keyframe image |
| `video_prompt` | prompt for the video clip |

**Alignment with the narration (the core rule).** Read the clip's `narration` and design the
visual to literally show that idea: the place, object, number, or action being spoken about.
On-screen numbers/headlines must be the exact facts from `research.md`, spelled exactly;
keep text short (headlines, a giant number, labels).

**Image prompt** (Codex receives `assets/style_reference_colored.png` as reference; Nexabot `img` gets text only):
the Style Block from `guidelines/colored/image-prompts.md` verbatim, then a SHOT describing the **opening frame**
of the clip: background, foreground/midground elements at named depths, focus, and the text
on screen. Single 16:9 frame, not a style sheet. No timecodes.

**Video model** (Nexabot `sfv`, Veo): **the keyframe is the first frame** of the clip, so
design the image as the exact opening of the shot and let the SHOT describe motion away from
it. Clips run ~8 s and come with Veo's own sound; only the first 0.25 s + the clip's window is
used, which also skips Veo's habit of drawing stray labels/numbers after ~4-5 s.

**Video prompt**: the four blocks from `guidelines/colored/video-prompts.md` (STYLE BLOCK A or B
chosen per clip → SHOT → AUDIO → AVOID), verbatim — they already open with "The provided
image is the exact first frame". Vary camera moves and backgrounds clip to clip, use the
color flood at most once per video, describe every beat literally (never a capitalised beat
name — Veo paints those words into the frame), and continue geometry across clips.

**Timing cues**: add them when they genuinely help sync, typically a 6 s clip (or any clip)
where the narration names something mid-clip that should visibly happen at that moment
(a number ticks up as it's said, a stamp lands on "rejected", a second cutout appears when
the second person is named). Add one line before AUDIO:
`TIMING: at 2.6s the giant number "4.1%" slams into focus; at 4.3s a red underline swipes under "TARIFFS".`
Take times from `word_times`; use at most 1-3 prominent events; never cue trivial words.
Short single-idea clips need no cues. The cue describes the visual event, not the voice-over
(clips must contain no narration).

**Public figures (hard rules, also checked by the scripts):**
- Image prompt: the person is a small cutout **far in the distance / background**
  (never close to camera, no facial detail), with a **solid black bar over the eyes**.
  Identify them by context (podium, flag, building, role label) rather than by facial
  likeness. You may name them in the image prompt only if needed for context.
- Video prompt: **never contain the person's name** (no first or last name, no nickname).
  Refer to "the distant figure at the podium", etc. Keep the figure distant throughout;
  no camera push-ins onto the face.

## 6. Generate keyframe images

```
$PY $S/generate.py images $R --dry    # prints count + credits first
$PY $S/generate.py images $R          # --only ch1_c03,ch2_c01 to redo; --force to redo all
```

`IMAGE_BACKEND=nexabot` (default): Nexabot `img`, parallel, text only, so the Style Block
in the prompt carries the whole look (spell out the materials and palette; do not say "the
attached sheet"). `IMAGE_BACKEND=codex`: free, `assets/style_reference_colored.png` is attached as a
reference, one image at a time (~1-3 min each; run the step in the background).

Then **look at every image** (Read the PNGs). Check: matches the narration, style matches
the colored board (looks like a /vox frame in hand-tinted color: aged paper, maps, keylined colorized cutouts, one hero number; no B&W drift, no neon modern color), text spelled correctly, public-figure rules respected (black bar, distant).
Fix prompts and regenerate failures with `--only`. If a keyframe is regenerated, its video
must be (re)generated too.

## 7. Generate videos

```
$PY $S/generate.py videos $R --dry    # count + credits
$PY $S/generate.py videos $R          # parallel (MAX_PARALLEL); same --only / --force flags
```

**Seedance option** ("guna seedance"): add `--engine seedance` (or `VIDEO_ENGINE=seedance` in `.env`).
Nexabot Seedance 2.5, 15 s clips at 1284x716 from the keyframe, 0.2 credit each (always charged,
refunded on failure), jobs queue in 60 s batches. Its clips have NO Gemini watermark: assemble with
`WATERMARK_BOX=off`. `src` may then go up to 15 − display_duration; text in a Seedance clip stays
clean for about 8-9 s, then starts to soften (first tested on "Wahyu Pertama", 2026-11-01).

For a new topic/look, generate ONE clip first (`--only ch1_c01`), pull a frame and check it
before the rest. Each failed task is retried once automatically. A refusal "Konten ditolak
filter keamanan" is refunded. For persistent failures (Veo safety filter), soften the prompt (less political charge, more distance, no
violence) and rerun with `--only`. Never add names to get past a failure.

## 7b. Choose each clip's cut (do not skip)

The 10 s Nexabot clips usually put their best action (number ticking over, stamp, arrival on
the destination tag, the settle) in the middle or end, and Veo sometimes writes prompt words or stray numbers into a few seconds. So never just take the first seconds:
make a 1 fps strip of every clip
(`ffmpeg -i clips/<id>.mp4 -vf "fps=1,scale=256:-1,tile=10x1" -frames:v 1 build/raw_<id>.png`,
stack them with `vstack`), look at it, and set per clip in `plan.json`:
- `src`: start second in the source so the window `src … src + display_duration` holds the
  best action, lands the key visual on the word it illustrates, ends on a settle, and skips
  any garbled text. It must stay ≤ 10 − display_duration.
- `speed`: keep 1.0 (natural motion); go below 1 only when the clean part is shorter than
  the window.
Then sample 4 frames per clip from `final.mp4` and check them.

## 8. Assemble

```
$PY $S/assemble.py $R                 # --music path to force a track
```

This removes the Gemini ✦ watermark with `delogo` (box set in `assemble.py`, override
`WATERMARK_BOX=x,y,w,h` as frame fractions; the landscape box is mirrored from the measured
portrait one, so check the bottom-right corner of the first final frame), trims 0.25 s off
the head of every clip, plays clips at `CLIP_SPEED` (default 1.0; a clip's own
`speed` in plan.json wins, e.g. 0.6 to stay inside Veo's clean first seconds), cuts each clip frame-accurately to its
narration window (holding the last frame if a clip runs short), keeps clip sound effects at
low volume (`CLIP_AUDIO_VOLUME`), lays narration on top, and adds one random track from
`assets/music/` at `MUSIC_VOLUME` with fades. Output: `$R/final.mp4`.

Spot-check sync by extracting a few frames at moments where a timing cue was set
(`ffmpeg -ss <global_time> -i $R/final.mp4 -frames:v 1 $R/build/check.png`) and viewing them.

## 9. Report

Tell the user: the final video path (as a link), title, chapters and duration, the music
track used, sources (from `research.md`), any clips regenerated or compromises made.
