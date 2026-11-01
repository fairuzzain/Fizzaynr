---
name: title-to-motion-video
description: Turn a title or topic into a finished, voiced motion-graphics explainer video built entirely in code with the user's "Motion as Code" kit (pdoom-style engine: ink/bone/signal-orange palette, graph-paper plates, plotter pen, karaoke type, spark motif; TypeScript + three.js, rendered to MP4). Writes the voiceover script, generates the voice with ElevenLabs, force-aligns it, designs and codes the plates, previews with stills, then renders and mixes SFX on request. Use this whenever the user gives a title, topic or one-line idea and wants a motion-graphics video, animated explainer, kinetic-typography video or "a video like the Motion as Code one" — even if they don't mention the kit, plates or ElevenLabs by name.
---

# Title → Motion-as-Code video

You are making a new voiced motion-graphics video in the style of the user's **Motion as Code** kit.
Every frame is a deterministic function of time, written as TypeScript "plates" (scenes) that animate
on the word timings of the voiceover. The template kit is `$MOTION_KIT` (default `<repo root>/vendor/Motion_as_kit`; env `MOTION_KIT`
overrides; if it is missing tell the user the kit is not installed and stop). Each video is a **fresh copy** under
`${MOTION_VIDEOS_DIR:-<repo root>/runs/motion-videos}/<slug>/`; never modify the template.

The work is long and creative, so it runs in **stages with a check-in after each one**: the user
reviews cheap artefacts (script → voice cost → animatic → plate stills) before anything expensive.
A full render takes ~25 min per minute of video; only start one when the user asks.

Before writing plate code read `references/kit-anatomy.md` (timing, toolkit, pitfalls).
`references/plate-cookbook.md` maps script beats to proven devices in the template plates.
`<skill-dir>` below means this skill's folder.

## Inputs to gather (ask once; offer defaults)

- **Title / topic** (required) · **length** (default ~60 s) · **audience & goal** · **voice**
  description (e.g. "calm, confident male").
- Format is **16:9, 1920×1080, 60 fps**; the engine canvas is fixed. If they want 9:16, say so and
  offer 16:9 (or a later crop) — don't edit `src/engine/`.

| Length | Plates | Words (conversational) |
|---|---|---|
| 30 s | 4–5 | ~75 |
| 45 s | 5–6 | ~110 |
| 60 s | 6–7 | ~150 |
| 90 s | 8–10 | ~225 |

## Stage 1 — Project

```bash
python "<skill-dir>/scripts/new_project.py" "<Title>" [--slug short-name]
```
Copies the kit, adds the `animatic` placeholder plate, writes a project `CLAUDE.md` (which allows
the ElevenLabs voice step and still forbids unrequested renders), patches kit pitfalls, picks a free
preview port, and makes the shared analysis venv. It ends with `KEY=VALUE` lines — keep
`PROJECT`, `VENV_PYTHON`, `PREVIEW_NAME`, `PREVIEW_PORT`, `LAUNCH_ENTRY`. If the folder already
exists, continue in it (ask the user) or choose another `--slug`.

**Preview wiring:** `preview_start` only reads `.claude/launch.json` in the *session's working
directory*. Merge the `LAUNCH_ENTRY` JSON into that file's `configurations` (create the file if
needed; keep existing entries), then `preview_start` with `PREVIEW_NAME`. Pass
`--url http://localhost:<PREVIEW_PORT>` to every `render.ts` call so stills come from this project
(without it, render.ts grabs whatever answers on :5173 — possibly another project).

## Stage 2 — Script (check-in)

Write the voiceover as a list of **lines** (each becomes one `SCRIPT` entry in
`analysis/align_vo.py`; plate cuts sit in the pauses between lines). Write for the ear and for the
animation at once:

- **Pace**: ~2.2 words/s for calm reads, 2.5 conversational, 2.8 energetic. State the estimate.
- **Shape**: hook → setup → 3–6 idea beats → turn → a short payoff line that can slam full-frame
  (the last plate holds it, implodes, and lands on the opening frame so the video loops).
- **Lines** of 3–18 words, one idea each; a plate = 1–5 lines, ~4–14 s.
- **Drawable**: every line should suggest something that can be *drawn* — a diagram, a ticked
  list, a pipeline, a counter, a before/after. Abstract filler animates badly.
- **Anchors**: each plate's first line needs a short phrase that appears in **no other line**.
  Matching is a case-insensitive substring search over whole lines (punctuation included, first
  match wins), so `'No bank'` would also hit "There's no bank…". Prefer 3–4 distinctive words.
- **Only letters are aligned.** Digits, symbols, arrows and hyphenated words are silently dropped
  or merged unless `SPOKEN` maps them (`"5.5." → ["FIVE","POINT","FIVE"]`, `"→" → ["TO"]`,
  `"15-second" → ["FIFTEEN","SECOND"]`). Spell numbers out where you can. A bare `—` is fine
  (it becomes a pause).

Put the lines into `SCRIPT`/`SPOKEN` and lint them:
```bash
python "<skill-dir>/scripts/check_script.py" "<PROJECT>" --wps 2.2
```
Fix every flagged token. (Until Stage 5 it also lists the template plates' anchors as MISSING —
expected.) Show the user a table — plate · lines · ≈ seconds · visual idea — plus word count and
duration. Continue only after they approve.

## Stage 3 — Voice via ElevenLabs (check-in on cost)

Load the tools with ToolSearch: `creative_list_voices`, `creative_generate_speech`,
`creative_get_flow_run_status`, `creative_get_flow`.

1. `creative_list_voices` with filters from the description (`languages: ["en"]`, `gender`,
   `descriptives` like `calm`/`confident`, `use_cases: ["informative_educational"]`). Pick one and
   name it so the user can swap.
2. TTS text = the approved lines joined by newlines, in spoken form ("→" → "to", numbers as words
   if SPOKEN spells them). Keep dashes/ellipses — they make the pauses the cuts need. No audio tags
   (`[whispering]` etc.) unless asked.
3. `creative_generate_speech` with `estimate_only: true` first (`model_id: "eleven_v4"`); tell the
   user the credit cost and wait for a yes. Then generate **once** (`generations_count` 1–2 unless
   they want options). Never call it again to retry — each call charges.
4. Poll `creative_get_flow_run_status` (respect `poll_after_seconds`) until `all_completed`, then
   `creative_get_flow` for the audio URL; `curl -L -o "<PROJECT>/audio/voiceover.mp3" "<url>"`. If
   no direct URL is exposed, give the user the canvas link to download the take and copy it in.
5. `ffprobe` it; report duration vs. the estimate.

## Stage 4 — Align & analyse

```bash
cd "<PROJECT>"
PYTHONIOENCODING=utf-8 "<VENV_PYTHON>" analysis/align_vo.py
PYTHONIOENCODING=utf-8 "<VENV_PYTHON>" analysis/audio_vo.py
```
(`PYTHONIOENCODING` stops the Windows console crashing on `→`/quotes after the work is done.)
Read the printed alignment: lines in order, times increasing, no words bunched at one timestamp.
If the take differs from `SCRIPT` (dropped/changed words), edit `SCRIPT` to what was said and
re-run. Now `data/lyrics.json` and `data/audio.json` belong to this video.

## Stage 5 — Animatic, then plates (check-in with stills)

1. **Timeline + animatic.** Rewrite `app/src/timeline.ts`: one `cut('<anchor>')` per boundary, and
   every entry pointing at the placeholder: `E('<id>', 'animatic', start, end)`; last ends at
   `au.duration`. The video now plays end to end (karaoke of each plate's lines). Delete the
   template plates from `app/src/scenes/` (keep `_vo.ts`, `_motifs.ts`, `animatic.ts`; the
   originals stay readable in the template kit for the cookbook). Run `check_script.py` — all clean.
   Show the user `bun scripts/render.ts sheet --cuts --url … --out ../out/wip/cuts.png` (from
   `app/`) so they can judge the cuts.
2. **Plan** each plate in 2–4 sentences: what is drawn, which word triggers each beat, camera,
   hand-over to the next plate. Reuse cookbook devices. Share briefly.
3. **Build** plates one at a time as `app/src/scenes/<id>.ts`, then switch that timeline entry from
   `'animatic'` to `'<id>'`. Start from the closest template plate (copy from the template kit),
   and **replace every `lineOf`/`wordOf` lookup** for the new script — a copied plate keeps the old
   words and throws `lyric not found` / `word not found` on load. Derive readouts (durations, frame
   counts) from `this.ctx`, not template constants. The first plate opens on the bookend frame and
   the last ends on it (see template `verdict.ts` → `fin`, `HOLD ≤ TAIL`). Don't edit `src/engine/`.
4. **Verify** each plate: preview (`?t=<s>`; check console + the red error overlay), then stills at
   its key words: `bun scripts/render.ts stills --t a,b,c --only <id> --url http://localhost:<PORT> --out ../out/wip`.
   Look at them yourself, then send them to the user (SendUserFile) with a line each, and iterate.

## Stage 6 — Render (only when the user asks)

```bash
cd "<PROJECT>/app" && bun scripts/render.ts video --samples auto --min-samples 4 --max-samples 12 --shutter 0.5 --crf 17 --url http://localhost:<PORT> --out ../out/<slug>.mp4
```
Run it in the background. Don't edit plates while it runs (plates load lazily, so edits leak into
the file). Afterwards check with `ffprobe`: video frames = round(duration × 60) and the audio
stream covers the full length; grab the first and last frames and confirm they match (loop).

## Stage 7 — Sound effects (when asked)

`analysis/sfx_mix.py`'s cue sheet is the template's — its `line()`/`W()` lookups use the old words.
Rewrite the per-plate cue sections for the new plates with its helpers (`cue`, `bed`, `W`, `cut`)
and the 28 sounds in `audio/sfx/` (whoosh on camera moves, pen_line/pen_tick on plotter strokes,
typewriter on typed text, impact_slam on slams, reverse_suck into the final implode…). Then:
```bash
PYTHONIOENCODING=utf-8 "<VENV_PYTHON>" analysis/sfx_mix.py
cd out && ffmpeg -i <slug>.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -af apad -c:a aac -b:a 320k -shortest <slug>_sfx.mp4
```
`-af apad` matters: the picture runs 0.3 s past the voice, and plain `-shortest` chops the ending.

## Reporting

At each check-in: what was made, show it (table, sheet, stills, file link), and the one decision
needed next. At the end: the MP4 path, duration/resolution, which stages ran, anything skipped.
