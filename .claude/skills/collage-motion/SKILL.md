---
name: collage-motion
description: Make a premium editorial paper-collage motion graphic video (stop-motion 12 fps, paper cutouts, floating-head and Polaroid cutouts of a real presenter, full-body paper puppet, tape, torn-paper wipes, crash zooms, black-ink-on-electric-yellow kinetic type) from a voiceover script, a few style references (Pinterest "collage art" boards) and optionally a presenter photo. Claude plays the creative director (analyses the references, writes a scene-by-scene brief with identity-lock rules), Nexabot renders each beat (i2v with the presenter photo, or sfv), two takes per beat, then the best takes are cut to the Nexabot voice-over with code-drawn kinetic type. Based on the ANDR3 AI "AI Motion Graphics Videos" workflow (Pinterest → ChatGPT → Gemini Omni in Flow). Use when the user asks for a collage motion graphic, paper cutout / stop-motion editorial video, "motion graphics without After Effects", a presenter collage reel, or names /collage-motion. Vox-style news/history explainers still go to the vox skill.
argument-hint: "[voiceover script or topic] [presenter photo] [style refs] [9:16|16:9]"
---

# Collage motion graphic (refs → creative brief → Nexabot takes → cut to VO)

Source workflow (ANDR3 AI, X article, 24 Jun 2026): save 4-6 Pinterest "collage art" refs → ChatGPT
turns refs + VO script into a scene-by-scene Gemini video prompt (style written directly, never
"based on the reference"; strict identity rule for the presenter) → Gemini Omni in Google Flow →
generate at least two versions → combine the best parts in an editor.
Here: **Claude is the creative director, Nexabot renders, `build.py` edits.** Never send the user to
ChatGPT or Flow. Prompts and the default style: `references/prompts.md` (read it).

```
ROOT="$(git rev-parse --show-toplevel)"; set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a   # repo root + overrides
NB="${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"
S="$ROOT/.claude/skills/collage-motion/scripts"      # system Python (PIL)
R="${RUNS_DIR:-$ROOT/runs}/collage-motion/<slug>"                 # one folder per video
```
Always pass **absolute** `--out` paths to nexabot.ts. 0.15 credit per request; filter rejections are refunded.

## 0. Brief (ask once, in Malay if the user writes Malay)
- **Voiceover script** - the user's, or write one (English VO always, even for Malay topics; short
  punchy lines, ~2.5 words/s). 20-45 s is the sweet spot.
- **Presenter photo** (optional) - a clear face/upper-body photo, no text on it. Without one the
  video uses anonymous paper characters and objects.
- **Style refs** (optional) - images the user drops in. None → the default style in prompts.md.
- Aspect: default **9:16** (`ratio 2`, `aspect 5`); 16:9 → `ratio 1`, `aspect 2`.
- Takes: default **2 per beat** (the source's rule). The user may choose 1 to halve the cost.
Do not ask about anything with a sensible default.

## 1. Creative-director pass (no credits)
1. Look at every style ref; write `$R\style.md` in direct visual language (prompts.md §1). Never
   mention references in it.
2. Split the script into **beats** of one sentence / ≈ 6-9 s (≤ 22 words) - one Veo clip each.
3. Write `$R\beats.md`: per beat the VO line, shot, camera, movement, character treatment, transition,
   emphasis words (prompts.md §2).
4. Write `$R\takes\clips.json` from the template (prompts.md §3), takes `<id>_a` / `<id>_b`:
   - presenter beat: `{"name":"s01_a","mode":"i2v","prompt":"...","ratio":2,"resolution":1080,"media":["../input/presenter.png"]}`
   - no presenter: first make a ChatGPT image `python "$ROOT/.claude/skills/codex-image/openai_image.py" --prompt "<board composition, no text, no letters>" --aspect 9:16 --width 1080 --out "$R/frames/s03.png"`
     (fallback if it fails twice: `bun $NB img "<...>" --aspect 5 --out ...`)
     (look at it; redo if it has text), then `"mode":"sfv","media":["../frames/s03.png"]`.
5. Show the user: style summary (3 lines), the beat table, and the cost
   (`bun $NB batch $R\takes\clips.json --dry` count + TTS beats + start frames, × 0.15). **Wait for approval.**

## 2. Test, then generate
- **One test first:** run beat 1 take a alone (a one-item JSON), then `python $S\build.py sheet $R`
  and look at `sheets\s01_a.png`: identity kept? stop-motion feel? stray text? Fix the prompt before
  the rest (prompts.md rules). Skip the test only if this style + presenter worked before.
- Rest: `bun $NB batch $R\takes\clips.json --parallel 4` (clips; images stay `--parallel 1`).
- Voice-over, one request per beat so each beat's length is exact:
  `bun $NB tts "<beat line>" --voice Charon --out $R\audio\s01.wav`. Listen-check for skipped words.

## 3. Pick the best of each beat
`python $S\build.py sheet $R` → delogoed `clean\*.mp4` + labelled 1 fps `sheets\*.png`. **Look at
every sheet.** Per beat choose the take and the clean window: start (`in`) after any slow first
second, end before Veo's stray text/morphs (~4-6 s). Window = VO length × speed; speed 0.5-1 stretches
a short clean range. A beat may switch takes - split it into two plan beats with the VO split too
only if really needed; otherwise one take per beat.
If a beat has no usable take, reword and regenerate that beat only (+0.15, tell the user).

## 4. Cut
Write `$R\plan.json` (format in the docstring of `build.py`): per beat `vo`, `clip`, `in`, `speed`,
and `words` = the 1-3 emphasis words in CAPS with `at`/`pos` timed to when the VO says them
(≈ 2.5 words/s from the beat start, or listen). Music optional: `bun $NB music "<upbeat quirky
stop-motion percussion, paper and claps, no vocals>" --out $R\audio\music.mp3`, `"music": "audio/music.mp3"`.
```
python $S\build.py render $R      # → $R\final.mp4
```
Words are drawn by PIL (Impact, black ink on electric yellow paper label, stamp specks, ±5°,
2-frame slap-in); `fps 12` steps the picture like stop-motion; Veo's own paper/tape sound stays under the VO
(`veo_gain`). Check: extract 3-4 frames at word hits and play the cut once for VO/word sync.

## Delivery
Send `final.mp4` (give its full path) and report: credits used (clips + TTS + images + music), which
take each beat used, and anything Veo got wrong (identity drift, stray text). Offer re-rolls of weak beats.
