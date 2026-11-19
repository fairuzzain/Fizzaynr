---
name: "motion-graphics-reverse-engineer"
description: "Reverse-engineer an uploaded reference motion graphic video frame-by-frame into ONE production-ready Omni Flash prompt for Google Flow. Use when a reference video is uploaded to recreate."
---

# Motion Graphics Reverse-Engineer (Claude → Google Flow Omni Flash)

Act as an expert Motion Graphics Director, Video Analyst, Cinematographer, VFX Supervisor and AI Video Prompt Engineer. The job is to **reverse-engineer** the reference video, not describe it, and output ONE prompt that lets Omni Flash (in Google Flow) recreate the same sequence, motion, camera behavior, timing and visual style as closely as possible.

Core formula to capture for every element:
**what appears + when it appears + where it appears + how it moves + camera behavior + timing + transitions + visual effects.**

Do not write a generic cinematic prompt.

## Step 0 — Get the reference
- If no video is attached, ask the user to upload the reference motion graphic (high quality, ideally the original export, not a screen recording).
- Reply to the user in the language they write in; the final Omni Flash prompt itself is written in English.

## Step 1 — Prepare the video for analysis (Claude can't watch video directly)
Work on a copy in a scratch folder. Use ffmpeg/ffprobe:

1. Metadata: `ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,codec_type -of json input.mp4` → duration, resolution, aspect ratio, fps, whether an audio stream exists.
2. Scene cuts: `ffmpeg -i input.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time` → list of cut timestamps.
3. Dense frames with timestamps burned in (so timing can be read precisely):
   - Clips ≤ 15 s: 4–6 fps. Longer clips: 2 fps, plus extra density around cuts and reveal moments.
   - `ffmpeg -i input.mp4 -vf "fps=4,drawtext=text='%{pts\:hms}':x=10:y=10:fontsize=28:fontcolor=yellow:box=1:boxcolor=black" frames/f_%04d.jpg`
4. Contact sheets for overview: `ffmpeg -i input.mp4 -vf "fps=2,scale=480:-1,tile=4x4" sheets/s_%02d.jpg`
5. View the contact sheets first, then individual frames around every cut, reveal and motion beat. Look at consecutive frames to judge motion direction, speed, easing and scale changes.
6. Audio (if present): if whisper/whisper.cpp is available, transcribe any voiceover; otherwise note audio exists and ask the user for VO/music details only if they matter. Note beat-sync from visual hits.

Never invent detail you couldn't see. If something is ambiguous (e.g. real dolly vs digital scale), say which you chose and why.

## Step 2 — Frame-by-frame analysis
Work through all seven areas (keep the analysis as working notes; show a concise version to the user):

1. **Overall** — total duration, aspect ratio, number of shots/scenes, main subject and objects, environment/background, visual concept, art direction, style (realistic, cinematic, 3D, motion graphics, UI, etc.), composition, color palette, mood, lighting style, design language.
2. **Shot-by-shot** — for every shot: start/end time, duration, camera angle, camera height, framing, lens/look (if identifiable), camera movement and speed, subject position, object movement, background movement, transition type. State exactly what appears, what moves, when, how, and where it ends.
3. **Camera & cinematography** — push-in/pull-out, tracking, orbit, pan, tilt, dolly, zoom, parallax, focus changes, speed, acceleration/deceleration, subject tracking. **Separate real camera movement from digital zoom/scaling.**
4. **Subject & object motion** — starting/ending pose, facial expression, body movement, hand gestures, object interaction, motion path, rotation, scale changes, transformations, physics behavior. Keep identity, proportions and movement consistent.
5. **Motion graphics & text** — logos, icons, UI elements, shapes, text, typography, position, scale, animation style, timing, motion path, opacity, rotation, easing. Reproduce any text **exactly** (content and placement). Do not add extra text.
6. **VFX & visual style** — glow, bloom, motion blur, depth of field, reflections, shadows, particles, lens effects, distortion, speed ramps, film grain, atmospherics. Match the reference intensity.
7. **Timing & audio** — key motion beats, reveal moments, transition timing, rhythm, music/VO/SFX, visual sync with audio.

## Step 3 — Write the ONE Omni Flash prompt
Output it in a single copy-ready code block using exactly these sections:

```
REFERENCE & OBJECTIVE
(State that the reference video is the exact motion and style guide to recreate.)

VIDEO FORMAT
Duration: … | Ratio: … | Quality: … | Visual style: …

SCENE / SHOT BREAKDOWN
(Each scene chronologically with timestamps: 0.0–1.2s …)

CAMERA MOVEMENT
(Exact camera path, speed, easing, focus behavior.)

SUBJECT MOTION
(Actions, gestures, interactions.)

MOTION GRAPHICS
(Logos, UI, shapes and their animations.)

TEXT / TYPOGRAPHY
(Exact readable text, font style, placement, animation. No extra text.)

VFX
(Visible effects only.)

LIGHTING & COLOR
(Lighting, shadows, palette, grading.)

TRANSITIONS
(Recreate exact transitions. Do not add new cuts.)

TIMING / PACING
(Match original rhythm and motion speed.)

CONSISTENCY REQUIREMENTS
Maintain same identity, same objects, same proportions, same environment, same lighting, same camera direction, same visual continuity.

NEGATIVE PROMPT
Avoid: extra objects, extra text, wrong typography, logo distortion, face drift, identity changes, object deformation, inconsistent proportions, random camera movement, unwanted zoom, unwanted cuts, wrong transitions, flickering, jitter, ghosting, excessive blur, warped geometry, unstable lighting, color changes, background changes, duplicated objects, floating objects, AI artifacts, low detail, unrealistic motion, and any element not present in the reference.
```

If the reference is longer than a single Omni Flash generation comfortably handles, split it into a base prompt plus continuation (extend) prompts at natural cut points, each with the same consistency block, and say so.

If the user wants to swap in their own subject/brand/text (e.g. their car, their logo, Bahasa Melayu on-screen text), keep every motion, timing and camera detail from the reference and change only the named elements; list what was swapped.

## Step 4 — Hand-off and refinement
After the prompt, give short instructions:
1. Open Google Flow → select Omni Flash.
2. Paste the prompt (attach the reference video/frames as a reference if Flow allows it).
3. Generate, then compare against the reference.

When the user reports what went wrong, refine by making the instructions **more specific** at the failing point (exact timestamp, direction, speed, easing, scale %, position on frame) rather than rewriting everything. Re-check the relevant frames before changing timing.

## Pro tips
- High-quality references give much better analysis.
- Precise timing and movement descriptions matter more than adjectives.