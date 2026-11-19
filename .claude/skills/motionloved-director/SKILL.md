---
name: motionloved-director
description: Direct, build and review motion graphics videos made with Claude — promos, explainers, logo stings, lyric and beat-synced videos, product films, reels. Use whenever someone asks to make, remake, revise or critique a motion graphics video or plan its sound. Works on top of HyperFrames (default renderer) and also Remotion, Three.js or Manim projects. Brings tested taste rules, beat-sync and mix numbers, QA tools (contact sheets, hit-frame strips, tempo grid, loudness, mastering, ElevenLabs) and renderer gotchas.
---

# MotionLoved Director

You are the director and the reviewer. A renderer skill (HyperFrames by default) builds the frames; this skill decides **what** to make, **when** things happen, how it **sounds**, and whether the result is **good enough to ship**. Read the renderer's own skill before writing composition code: its contracts change between versions, this skill does not repeat them.

Tools live in `scripts/` next to this file (Python 3 + FFmpeg only). Run them with the full path, e.g.
`python "<this skill folder>/scripts/sheet.py" film.mp4`.

## 0 · Start from what you were given

- Read the brief, every reference and the existing project before asking anything. For a small fix, fix that moment; don't restart.
- Settle the deliverable: length, format(s), frame rate, sound (music · voice · SFX · silent), references, brand assets. Ask **one** question only when an answer would change the build (usually the format, if none is given). Otherwise pick a sensible default and say it in one line:
  16:9 1920×1080 at 30 fps for explainers and site videos; 9:16 1080×1920 for phone; 60 fps for fast kinetic type.
- Two formats are **two films**: design every 9:16 shot for the tall frame. Never crop or reflow the 16:9.
- "Make it like this, this one is good" means: keep that reference's look and raise the craft. "Here's something I like" means: inspiration for **your own** look. Never copy footage, frames, HUD layouts or copy text from a reference, and never build motifs out of a file name.

## 1 · Study references densely

- Contact sheets at 4 fps across the whole clip: `scripts/sheet.py ref.mp4 --fps 4`. Add a 1 fps sheet for side-by-side comparisons later.
- If the reference is a screen recording, cut out just the clip first.
- Write down what actually makes it work: how many techniques, how much text and for how long, the palette and how often it changes, the cuts per 10 s, what happens on the beats. See [references/taste.md](references/taste.md).
- Music in the reference: measure it (step 2), don't guess.

## 2 · Sound first, picture on its grid

The picture is timed to the sound, never the other way round.
- **Music:** measure the real tempo, beat phase and bars: `scripts/beat_grid.py track.mp3 --json beats.json --click check.wav`. Listen to `check.wav`: if the clicks sit between the kicks, rerun with the `--phase` it suggests. Choose a length that is a whole number of bars (`--length 15`).
- **Voice:** write the script, generate it with word timings (`scripts/eleven.py tts …` writes `vo.words.json`), then cut it at its pauses and start every line on a beat. Never estimate word times from word counts.
- Generated music doesn't follow the plan exactly (drops land elsewhere, endings fade early). Make two takes, measure both, keep the one whose real structure fits, and edit to what is really there.
- Rules and numbers: [references/beat-sync.md](references/beat-sync.md) · [references/voice.md](references/voice.md).

## 3 · Concept: one system, a range of techniques

- One visual system that **transforms** through the piece (match cuts: an object becomes the next scene), not a slideshow of unrelated scenes.
- Plan a **different technique per section**: flat graphic, typographic, generative/procedural, particles, live 2D charts, glass UI, real 3D, logo animation. If two sections share a look, replace one.
- Text is rare and readable: a hook, one type moment, the lockup. Count the seconds with text on screen before building; on a 15 s motion piece it is usually ~4 s.
- A controlled palette (ink + paper + one accent as home base) with **colour chapters** that flip on the big hits. No rainbow fields, no primary "kids" palettes.
- Real logo files only, animated (draw-on, spark, lockup). Never redraw a logo.
- If the reference is 3D-rendered, plan a real 3D build (Three.js: PBR materials, environment light, motion blur, depth of field) from the start. CSS 2.5D won't reach that level. Prefer flat type under real glass over extruded 3D words.

## 4 · Shot list on the grid

Write a table before building: `bar.beat → time → what changes → why`. Then:
- Small moves on 16ths/8ths, medium on beats, scene changes on bar lines, the biggest changes (new world, drop, logo) where a group of 4 or 8 bars starts.
- Something changes at least every bar and something moves on most beats, **but leave space**: a held or emptied beat before a drop makes the drop hit.
- Every hit must be **visible on its own frame**: the frame before and the hit frame must differ strongly (brightness, colour, composition). No fades into a drop; no white flash after a pale scene (invert or cut to dark instead).
- Words are fully readable on the frame they are sung or spoken. Decoration (particles, swarms) may follow, never precede.

## 5 · Build

- Prototype the hardest shot first and show one style frame when the look is uncertain.
- Follow the renderer's determinism rules (seekable time, no wall clock, no unseeded randomness). Use HyperFrames for HTML/GSAP/Canvas/Three.js; see [references/engines.md](references/engines.md) for when Remotion, Manim, Motion Canvas or Blender fit better.
- Known renderer traps (fonts, images, Three.js, audio, render workers): [references/hyperframes-gotchas.md](references/hyperframes-gotchas.md) and [references/threejs.md](references/threejs.md).
- Images (generated or supplied) are textures inside motion, never held full-frame stills. Use each image once.

## 6 · Review what actually ships

Run these on the **rendered file**, then fix by timestamp, biggest problem first:
1. `scripts/sheet.py film.mp4 --fps 4`: read every frame. Is every word readable? Is anything held or blank? Is there range?
2. `scripts/hit_strip.py film.mp4 beats.json` (or a list of hit times): does each hit read on its frame?
3. Sound: `scripts/loudness.py --voice vo.wav --bed bed.wav` (narrated: median 15 dB+, worst 10% 9 dB+) or `--hits sfx.wav --bed music.wav` (music-led: every hit 6 dB+). Mix rules: [references/sound.md](references/sound.md).
4. Master the final sound and lay it onto the render: `scripts/master.py film.mp4 film-final.mp4` (-14 LUFS, peaks under -1 dBTP).
5. If a song was used "from the start", verify it wasn't shifted: `scripts/align_check.py film-final.mp4 song.mp3`.
Full checklist and rubric: [references/review.md](references/review.md).

## 7 · Deliver

- Deliver the minimum that was asked for (one file per format), named clearly. Offer variants in one line instead of sending a pile.
- Report the beats that carried the big moments: `bar.beat · time · event · why`.
- Say what you checked (frames, hits, loudness, full playback) and what you didn't.

## Tools (scripts/)

| script | what it does |
|---|---|
| `beat_grid.py` | real tempo, beat phase, bar lines, energy per bar; `--click` preview, `--length` whole-bar planning, `--json` for timelines |
| `sheet.py` | contact sheets with time labels (`--fps`, `--start/--end`, `--cols`) |
| `hit_strip.py` | frames around each hit time, hit frame outlined |
| `loudness.py` | LUFS / range / true peak; voice-over-bed and SFX-over-music margins |
| `master.py` | loudness target with a true-peak ceiling; video picture copied untouched |
| `align_check.py` | offset between a delivered video's audio and the source song (ms) |
| `eleven.py` | ElevenLabs: narration with word timings, SFX takes, music from a prompt or plan |
