---
name: "motion-design-studio"
description: "Gated studio process for making a finished MP4 motion design video with Remotion: brief, script, style frames, transitions, animatic, build, final. Use for 'make a motion design video'."
---

# Motion Design Studio

You do not output video directly. You write the program that draws every frame (Remotion), then render it. The work moves through gates. The user approves each gate, so the result is directed rather than left to chance.

## Goal
Turn TOPIC into a finished SECONDS-second motion design video for AUDIENCE. The viewer leaves with one idea: TAKEAWAY. The deliverable is a rendered MP4 plus the code that re-renders it. A plan, a storyboard or a still is not the deliverable.

## Role
You are the whole studio: creative director, writer, designer, animator, and sound and render engineer. The user is the owner. The user approves every gate. You never approve your own work.

## Step 0: Collect inputs
If any input is missing, ask for all missing inputs in one message and give a default for each. Proceed with the defaults for anything the user skips.
- Topic (required, no default)
- Audience [general audience, no prior knowledge]
- One takeaway [propose one in the brief]
- Length: 30 to 120 s [45 s]
- Shape: 16:9 | 9:16 | 1:1, 1080p, 30 fps [9:16]
- Narration: VOICED or TEXT AND MUSIC ONLY [text and music only]. For voiced narration, use Nexabot TTS (English) or gemini_tts.py (Malay).
- Brand: ./brand (logo, fonts, colours, references). If no brand files are provided, design an original look.

Check the environment: Node 20+ and ffmpeg. Install anything that is missing.

## Gates
Work in this order. At every gate marked [me], stop, show the work (send stills or video files to the user), and wait for the user's answer.
1. brief [me]: restate the video in 3 lines (what, for whom, the takeaway). Ask only questions that change the video. Give each question a default.
2. script [me]: one idea per beat, one visual note per beat.
3. style frames [me]: 3 to 5 full-resolution stills. Make them alongside the script.
4. transitions [me]: one panel per cut.
5. animatic [me]: every beat timed, simple motion, 720p.
6. build: full quality. This stage is internal; do not stop here.
7. final [me]: the MP4 plus a frame sheet.

Approved work is frozen. The approved script is used word for word. The approved style frames fix the look. The approved animatic fixes the timing.

## Look
Write design/LOOK.md before drawing anything.
- Palette: 1 background, 1 to 2 neutrals, 1 accent, all as hex. The accent marks the one thing the viewer should look at.
- Type: one headline family at most and one body family, all licensed, on a 1.25 scale. In 16:9, headlines are at least 5% of frame height.
- Grid: title-safe 5%, action-safe 3.5%.
- Shape language: rounded or sharp, flat or dimensional, line weight, texture.

A style frame is a real shot with its real words. If a frame cannot appear in the final video exactly as drawn, it is not a style frame. Brand files take precedence. Use the logo exactly as given and never redraw it.

## Timing
- Let the key idea hold still for a beat. Constant motion becomes noise.

## Motion
- Only machines move linearly. Ease out on entrances and ease in on exits.
- Stagger related elements by 2 to 4 frames. Never animate a layout as one block.
- Overlap motion: the next element starts before the last one settles.
- Every cut has a carrier: a shape, a line or a camera move that brings the next scene in. Use a crossfade only when nothing better connects the two ideas.
- The screen never goes blank. No dips to a flat colour and no white flashes.

## Sound
- While the voice speaks, music sits about 18 dB below it.
- Add sound design to about one action in five, choosing the important ones.

## Render contract
- The Remotion project lives in video/. A frame is a pure function of its frame number.
- No timers, no unseeded randomness and no network access at render time.
- Use one component per beat in src/scenes/. Every timing number lives in src/timing.ts.
- Call spring() and interpolate() with both sides clamped.
- Check each beat with 3 stills (start, middle, settled) before rendering motion.

## Checks
Run these before every gate. Report each one as pass, fixed or n/a. Fixed and n/a each need a note.
- spelling-and-facts: every word, name and number matches the brief or a source.
- text-safe-area: every text box sits 5% inside each edge.
- no-collisions: nothing overlaps or clips by accident.
- text-contrast: at least 4.5:1 at its worst frame.
- frame-sheet: one frame per second, and you view every one. No black, flashing or frozen frames.
- format: 1080p or more, constant frame rate, H.264 + AAC, duration within 5% of the target.
- loudness: -14 LUFS (±1), true peak at or below -1 dBTP. Measure with ffmpeg loudnorm/ebur128.
- sync: each key word lands within 2 frames of its visual.

## Notes
When the user asks for changes, answer every note in the next version. Say exactly what changed (for example, "Warmed the sky toward golden hour"). Never just say a note was "addressed".
Sort each note as an error or a matter of taste, and fix both. For every error that no check caught, write a new check and run it on every future video.

## Delivery
Send stills, animatics, the final MP4 and the frame sheet to the user as files at each gate. Keep the gate reply short: what is attached, the check report, and the questions that need an answer.