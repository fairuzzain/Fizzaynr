---
name: edit
description: START HERE. Edit Kit is the one command for the whole editing kit - give it a raw clip, a script or just an idea and it delivers a finished, professionally edited video. Checks the computer is set up, asks only what it needs, picks one of 11 styles (Creator Explainer, SaaS, Motion Graphics Explainer, Vox, Ali Abdaal, Real Estate, Construction, Gadzhi, Bold Impact, Podcast, Finance) or a special look (anime, pixel art, whiteboard, paper cutout, crayon, painted, 3D product), storyboards, builds with HyperFrames, adds frame-synced sound and runs QA. Use for "edit this video", "make a reel/short/YouTube video/ad/promo", "motion graphics", "use the Edit Kit", or any video request.
---

# Edit Kit

The user types one prompt. You run the whole edit and only ask what you truly need.
This skill is the front door: it checks the setup, picks the right skill, then runs the `/director` pipeline.

## 0. First run on a new computer (do once, quietly)
Check `node --version` (22+), `ffmpeg -version` (or `python3 fx/scripts/ff.py`), `python3 -c "import numpy, PIL"`.
If something is missing, tell the user the ONE command to fix it (see the kit's START HERE.txt), wait, re-check.
Optional full check: `python3 <kit>/selftest.py` renders a 3 s test video with sound and QA.

## 1. Pick the route
| The user has / wants | Route |
|---|---|
| Raw clip of a person talking, reel, YouTube edit, podcast, real estate, construction, finance | `/director` (11 styles, it runs intake, storyboard, build, sound, QA) |
| App, SaaS or agency promo with no footage | `/saas` (through `/director`) |
| Product launch from a website | `/product-launch-video` |
| Faceless explainer from text or a topic | `/faceless-explainer` |
| Vox-style documentary explainer | `/vox-director` |
| Copy the look of a reference video | `/video-clone` (routes to anime, pixel art, whiteboard, paper cutout, crayon, painted, 3D product) |
| Music video / beat montage | `/music-to-video` |
| Captions on an existing talking head | `/embedded-captions` |
| Shots that feel cinematic (camera moves, transitions) | `/video-shotcraft`, `/cut-the-curve`, `/seam-craft` |
| 3D, particles, shaders | `/threejs-animation`, `/particle-system`, `/shader-glsl` |

If it is not clear, recommend ONE route in a single line and go.

## 2. Always
- Ask the intake questions of `/director` in one message (whose video, input, style, format, language, brand,
  audio, length). Skip anything already known. "Just do it" → decide everything and skip the storyboard approval.
- Colours and fonts come from the client's brand kit, the user's own, or `/theme` designs them from the footage.
- Storyboard first (time | words | on screen | effect | sound) as a themed page, then build.
- Finish with `/sound` (if the user wants SFX or music) and `/qa`, then hand over the MP4.

## Rules
- Kinetic typography only (never boxed karaoke captions). Text in the safe zone, never on the face or mouth.
- Every visual matches the exact words at that moment. Prefer real UI and the user's own screenshots.
- Smooth zooms on impact lines; no hard punch-in jump cuts unless asked.
- Human typography: real word gaps, no wide-tracked labels, even spacing.
- Client work uses only that client's brand kit. One video = one brand. Never invent facts or numbers.
- Free fonts and code-made or user-owned audio only. Never spend paid credits without asking.
- Keep edits lean: no effect without a reason in the words.
