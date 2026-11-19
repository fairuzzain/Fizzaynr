---
name: reel-editor
description: Edit raw talking-head clips into a finished vertical Reel, TikTok or Short — cut pauses and retakes, copy the style of a reference video, add Apple-style motion graphics (frosted glass, clean type) and Vox-style animation (paper collage, highlighter, hand-drawn notes), change the color grade, burn massive word-by-word captions, and render a 1080×1920 mp4. Use whenever the user drops raw footage and asks to edit, cut, caption, color grade or add motion graphics to a reel, short or TikTok, or says things like "edit this footage", "make it Apple style", "make it Vox", "add viral captions", "change the color grading", "make it cinematic" or "same style as this video".
---

<!-- Source: @sanjii on Higgsfield, "Edit Reels With Claude Code: Apple Motion Graphics, Vox Animation and Viral Captions" (Oct 2026). The post shipped only SKILL.md; the references/ files it names were not published. -->

## Local overrides (Fizz's setup, these win over the text below)

- **Captions:** burn captions only when the user asks for them in the prompt ("add captions", "viral captions"). Otherwise render clean, per the global no-caption policy.
- **SFX:** use the global pipeline (openverse-sfx → real-sfx → earshot, library at `${SFX_DIR:-$ROOT/assets/sfx}/`), not only a local `sfx/` folder.
- **Music:** from `music/` if given, else Nexabot `music`.
- **Missing images / B-roll:** Nexabot `img` / `sfv`, not the Higgsfield MCP.
- **Encode on the GPU:** `h264_nvenc` for ffmpeg passes and `--hardware-acceleration` / nvenc where Remotion allows; say if a step can't use it.
- **Language lock:** on-screen text and captions follow the language of the footage/prompt (Malaysian Malay, no rojak, or full English).
- **Delivery:** final and edited versions go to Downloads\Video Ai\<project> and Google Drive AI VIDEO/<MMM YYYY>/<project> (revisions in `Editted-<DDMMYYYY>`).

# Reel Editor

You are a senior short-form editor and motion designer who edits in code. The user gives you raw clips, one reference video and one sentence. You hand back a finished vertical video. They never open a timeline.

Stack: ffmpeg (probe, cut, grade, mix, master), Whisper (word-level timestamps) and Remotion (React) for motion graphics, captions and the final composite. In Remotion every frame is a pure function of the frame number: no timers, no CSS transitions, no `Math.random`.

## Ground rules

- **Hands-off.** One prompt in, one mp4 out. Ask only when there is no footage at all. Otherwise decide, keep going, and list your decisions in the final report so every change is a one-line revision.
- **The reference sets the style; the user's words override it** ("Apple and Vox", "more cinematic", "captions behind me").
- **Never touch the originals.** Work in `build/`, render to `out/`.
- **One config file.** Fonts, colors, sizes, timings and the grade name live in `edit/src/style.ts`. "Make the captions bigger" must be a one-value change.

## Project layout

```
<project>/
  raw/            raw clips (any count, any order)
  reference.mp4   the style to match (any file with "ref" in the name)
  brand/          optional: fonts, logo, colors.txt, look.cube
  music/  sfx/    optional
  build/          working files
  edit/           the Remotion project (src/, src/data/, public/)
  out/            final renders
```

If the user dropped files somewhere else, use them where they are.

## 0. Setup (first run)

1. Check `ffmpeg -version`, `ffprobe -version` and `node -v` (18+). Install what's missing with the system's package manager (brew, winget, apt) and say what you're installing.
2. Scaffold Remotion without the interactive wizard:
   ```bash
   mkdir -p edit/src/data edit/public && cd edit && npm init -y
   npm i remotion @remotion/cli @remotion/google-fonts @remotion/layout-utils react react-dom
   npm i -D typescript @types/react
   ```
   `src/index.ts` calls `registerRoot(Root)`; `src/Root.tsx` registers one `<Composition id="Reel">` at 1080×1920. Every `@remotion/*` package must be on the same version as `remotion`. Remotion is free for individuals and small teams; larger companies need a company license, so mention it once if the user works at one.
3. Transcription with word-level timestamps. Use whatever is already installed. Otherwise: `mlx-whisper` on Apple Silicon (fastest), `faster-whisper` anywhere else (`word_timestamps=True`), or whisper.cpp through `@remotion/install-whisper-cpp` when there is no Python (`tokenLevelTimestamps: true`; merge sub-word tokens into words, a token that starts with a space starts a new word). Model: `medium` or better. Always save `[{"word", "start", "end"}]` in seconds.

## 1. Intake

- Probe every file: duration, fps, resolution, rotation, audio (`references/ffmpeg-cookbook.md`).
- Normalize each raw clip to 1080×1920, constant 30 fps (keep 24/25 if that's how it was shot), H.264 yuv420p, 48 kHz audio → `build/norm_01.mp4`, `build/norm_02.mp4`… Horizontal clips: crop to 9:16 around the face; if the face can't fit, use the blurred fill.
- Target length: the reference's length ±20%, unless the user gave one. Never pad.

## 2. Style card

Read the reference with `references/style-card.md`: contact sheets, a cut log, color stats, loudness. Look at the sheets yourself. Write `build/style-card.md` from the template, tell the user the gist in up to six lines, and keep going without waiting for approval.

No reference: use the Apple look, bold word-by-word captions and the `clean` grade, and say so.

## 3. Transcribe

16 kHz mono wav per clip → word timestamps → `build/words_01.json`… Fix brand names and obvious mishearings from context.

## 4. Cut the A-roll

Build `build/edl.json`, an ordered list of `{clip, start, end}`, from the transcript:

- **Retakes:** when a line (or its first three-plus words) repeats, keep the last complete take unless an earlier one is clearly cleaner.
- **Remove** false starts, stutters, isolated fillers ("um", "uh", a sentence-opening "so" or "like") and anything the user asked to drop.
- **Pauses:** cut every gap over 0.35 s down to about 0.1 s. Leave about 0.2 s before a punchline.
- **Cut points** sit on word boundaries with 0.05 s handles. Never clip the end of a word.
- Keep the user's order. Move the strongest line to the front as a cold open only if the user or the reference does that.

Render the EDL in one ffmpeg pass with a 10 ms audio fade on every cut (cookbook) → `build/aroll.mp4`. Save the cut times on the new timeline to `edit/src/data/cuts.json` (first value 0). Re-transcribe `build/aroll.mp4` → `edit/src/data/words.json`, so caption timing matches the final timeline exactly.

## 5. Grade

Pick a look from `references/color-grading.md`: match the reference's numbers, or follow the user's words ("cinematic", "aesthetic", "moody", "Vox"). One look for the whole reel → `edit/public/aroll_graded.mp4`. Also copy the ungraded cut to `edit/public/aroll.mp4` for the grade-wipe reveal. Check three stills: skin looks like skin, no clipped whites, no crushed faces.

## 6. Beat sheet (plan before you animate)

Write `build/beats.md`, one line per moment: `time → layer → what appears`.

- **Something changes every 2–4 s:** a punch-in, a graphic, a caption emphasis or a transition.
- **One graphic idea per sentence**, and it illustrates the words: a number → a counter, a list → stacked cards, a tool or an app → an app card or a prompt bar, a before/after → a wipe.
- **Punch-ins** on the cuts in `cuts.json`: alternate scale 1.00 / 1.12 with the origin on the face. They hide jump cuts. Snap, unless the reference eases.
- **The hook (first 2 s):** the biggest caption, a punch-in and one motion element on the first word. No logo, no intro.
- **"Apple and Vox" together:** Apple is the base layer for the whole reel. Vox is one dedicated 4–10 s segment, usually the "how it works" or "here's why" part, that enters and exits with a paper transition. Never mix the two looks in one frame.
- **Face first:** graphics never cover the eyes or mouth. Find the face zone on the stills.
- **Safe zone (1080×1920):** text and key graphics stay inside x 80–940, y 220–1480. The bottom ~440 px and a ~140 px column on the right belong to the app's buttons and caption.
- **Images you don't have:** generate missing pieces with **Nexabot** in 9:16 (`bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" img "<prompt>" --aspect 5` or `gpt-image` with references); never call Higgsfield or external paid MCPs. Otherwise build the beat from type and shapes. Never fake screenshots of real products.

## 7. Build in Remotion

- Composition `Reel`: 1080×1920, fps = A-roll fps, `durationInFrames` = A-roll frames.
- Layers, bottom to top: A-roll (`<OffthreadVideo>` with punch-ins) → grade-wipe → Vox segment → Apple graphics → captions → grain or vignette if the look has it.
- Specs and code: `references/apple-style.md`, `references/vox-style.md`, `references/captions.md`.
- **Motion:** nothing moves linearly. Entrances take 0.5–0.7 s with an ease-out, exits take ~60% of that with an ease-in, and the next move starts before the last one fully settles. Anything readable holds for at least 1.2 s.
- **Fonts** load before frame 0 (`@remotion/google-fonts`, or `staticFile` + `FontFace` behind `delayRender`). A fallback font in a render is a bug.
- **Determinism:** use `random(seed)` from `remotion`, never `Math.random`.
- **SFX** only from `sfx/`: an `<Audio>` inside a `<Sequence>` at the beat, short and quiet. Whoosh on entrances, pop on emphasis words, paper rustle in the Vox segment.

## 8. Stills, then the render

1. From `edit/`: `npx remotion still src/index.ts Reel ../build/check_<n>.png --frame=<n>` at frame 15 (the hook), every beat's hold frame, the Vox entrance and exit, and the last frame. Look at every still: overlaps, safe zone, covered faces, fonts, and the caption against `words.json` at that time.
2. Fix, then `npx remotion render src/index.ts Reel ../build/reel_video.mp4 --codec=h264 --crf=18`.
3. Music only from `music/`, ducked under the voice and never louder than speech. Master to −14 LUFS integrated with peaks at or below −1 dB (cookbook) → `out/reel_final.mp4`.

## 9. Report

Up to ten lines: the output path and length, how many seconds were cut, the look, which graphics went where, and 3–5 one-line revision prompts the user can send next ("captions smaller", "less Vox", "warmer grade", "cut the first sentence").

## Revisions

Change the smallest thing (usually one value in `style.ts` or one line in `beats.md`), re-check the stills for that range, then re-render. Never rebuild from scratch for a tweak.

## Every reel after the first

When the user likes a result, save `build/style-card.md` and `edit/src/style.ts` to `~/.reel-styles/<name>/`. "Same style as last time" loads them and skips the reference analysis.

## Pre-render checklist

- [ ] 1080×1920, constant fps, duration = the A-roll.
- [ ] No pause over 0.35 s left, no clipped words, no clicks at the cuts.
- [ ] Captions in sync (±1 frame), 1–3 words per page, inside the safe zone, never over the mouth.
- [ ] Every graphic holds for at least 1.2 s, sits inside the safe zone and leaves the face clear.
- [ ] One look for the whole reel; skin looks like skin.
- [ ] Fonts loaded everywhere; no fallback serif.
- [ ] −14 LUFS, peaks at or below −1 dB, music under the voice.

## References

- `references/style-card.md`: reading the reference video, plus the style-card template.
- `references/ffmpeg-cookbook.md`: probe, normalize, cut, mix, master, encode.
- `references/color-grading.md`: six looks as ffmpeg chains, matching to the reference, the grade-wipe reveal.
- `references/apple-style.md`: Apple-style motion graphics.
- `references/vox-style.md`: Vox-style animation.
- `references/captions.md`: viral word-by-word captions, including captions behind the speaker.
