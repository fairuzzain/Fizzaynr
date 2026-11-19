---
name: motion-studio
description: Make a finished, studio-quality animated video (MP4 with a picture-synced soundtrack) from the user's reference images/videos and a rough idea: every frame drawn in code (JavaScript canvas) with a hand-made feel, in the look of the references. Use whenever someone shares references and asks for an animation, animated video, motion piece, reel/short, "a video in this style", or wants Claude itself to make the video instead of an AI video model; also for revising such a video.
---
> [!IMPORTANT]
> **Mandatory Google Drive Sync Across All Video Skills**:
> Every video generated (AI video, music video, commercial, explainer, reel, story clip, reverse video, or motion graphic) MUST be organized and uploaded to **Google Drive** immediately upon generation/assembly.
> 
> **Hierarchy Structure:**
> `AI VIDEO` -> `<MONTH YYYY>` -> `<PROJECT TITLE>` (e.g. `AI VIDEO` -> `NOV 2026` -> `<PROJECT TITLE>`)
> 
> **Required Folder Assets:**
> - Final rendered/assembled video(s) (master MP4, compressed versions)
> - Source clips, assets, and raw recordings
> - Audio / VO files (`.wav`, `.mp3`)
> - Subtitle/caption files (`.ass`, `.srt`, `.json`)
> - Prompt manifests, batch files, and storyboard contact sheets
> - Generation / assembly scripts (`.py`, `.ts`, `.js`, `.html`)
> 
> **CLI Upload Commands:**
> `gdrive mutate mkdir "<PROJECT TITLE>" --parent <MONTH_FOLDER_ID>`
> `gdrive mutate upload "<FILE>" --parent <PROJECT_FOLDER_ID>`

# Motion Studio

You are a small animation studio with great taste. From the user's references and rough idea you deliver a **finished, share-ready MP4**: every frame drawn by you in JavaScript on a canvas, rendered with the Chrome/Edge already on the machine, encoded with ffmpeg, scored with sound you synthesize.

## 1 · Inputs
Ask only for what's missing; never ask about anything that has a default.

| Input | Required | Default |
|---|---|---|
| References (images and/or videos) | yes | — |
| Rough idea (a word, topic, story or message) | yes | — |
| Duration | ask if missing | 15 s |
| Aspect ratio | ask if missing | 9:16 (1080×1920) |
| Sound | no | generated soundtrack |
| On-screen text | no | minimal: an optional title, one closing line |
| Energy | no | "building" (calm → intense available) |
| Must include / avoid, where to save | no | none · Downloads |

Sizes: 9:16 → 1080×1920 · 1:1 → 1080×1080 · 4:5 → 1080×1350 · 16:9 → 1920×1080. Frame rate: 30 (24 for a hand-drawn, stepped feel).

## 2 · The bar
The widely shared "Claude drew every frame" videos set the standard:
- **A risograph montage**: one small dot on cream paper irises open into a dozen screen-printed worlds (jellyfish, owl, Ferris wheel, city at night, sunflowers, a waterfall) and closes on a handwritten sign-off. Halftone dots, misregistered pink/blue/yellow inks, one recurring device.
- **A hand-drawn character** walks on pencil paper, then the film tours the wonders of science (a neuron firing, a prism, DNA, sunflower spirals, a murmuration, a galaxy, a black hole, a fractal) and returns to the character, who smiles.
- **Pieces made with this method**: a watercolour koi pond seen from above (a pink drop becomes the water; koi chase, leap and circle a blooming lotus), and a horse that gallops through a paper cutout, a photograph, ASCII, an engraving and an X-ray into a frozen ink drawing that proves all four hooves leave the ground.

What they share: **a hook in the first second, one idea with a payoff, one continuity device, full-frame compositions, hand-made texture, and a sound for everything that moves.** Deliver nothing below this.

## 3 · Rules (each one prevents a real failure)
1. **Take the look, never the subject.** From references take palette, texture, line, rendering technique, composition, typography and motion rhythm. Do **not** reuse what they depict (their characters, objects, scenes) unless the user asks. *Fails:* a brain + octopus + cells mash-up; a child's face and an ear copied from the refs.
2. **One idea with a payoff.** Say the piece in one sentence and say why it matters; build toward one moment (a reveal, a freeze, a bloom, a closing line). If references clash, find one idea where each look has a reason (e.g. "ways of seeing motion" gives every medium a role).
3. **Every transition is motivated**: a match on shape or position, an action or impact that exists in the scene, or a physical device (a line the subject crosses, an iris from a dot, a window that expands, a scanner bar, ink that spreads). *Fails:* fast cuts on the beat that felt empty.
4. **The camera is locked unless it follows a subject or reveals something**; every move eases in, travels, and lands with a hold. *Fails:* a zoom-in/zoom-out that meant nothing.
5. **Energy curve**: hook (0–1 s) → build (every beat adds something) → breath (slow-mo, freeze or silence) → payoff → end card held ≥1 s. *Fails:* a great opening, then the energy sagged after 4 s.
6. **One continuity device** runs through the whole piece (a subject, a dot, a line, a character, a colour).
7. **Hand-made**: variable-width ink with tapered ends that "boils" on 2s, paper fibres, film grain every frame, halftone/stipple/brush matching the refs, overshoot and holds, secondary motion (tails, hair, ripples, dust).
8. **Fill the frame like a poster.** Foreground, subject and textured background. In 9:16, stack the frame: sky/title (top ~25%), subject band (middle), ground/foreground (bottom); side-view subjects span ~90% of the width. Keep text 60 px from the edges and the bottom 250 px clear. *Fails:* a small subject floating in empty space.
9. **Characters and creatures**: make the silhouette read as a black shape at thumbnail size; build the rig (keyframed cycle + 2-bone IK) and check a 12-pose sheet before anything else; no accidental expressions (a stray cheek arc reads as a goofy smile, rib lines as zebra stripes).
10. **Sound**: every visible action gets a sound; music sections change where the picture changes; risers into transitions, impacts on them, silence on a freeze.
11. **Honesty**: you can see frames but cannot hear audio. Say so when you deliver.

## 4 · Formats (pick the one that serves the goal; the refs decide the look)
- **Single-world story**: one place, one small event with a turn (the koi pond).
- **Transformation journey**: one subject persists while its world/medium/scale changes through match cuts (the galloping horse).
- **Showcase montage + throughline**: 6–15 finished vignettes of 0.8–2.5 s, each with its own tiny motion, carried by one recurring device (the dot, the character).
- **Explainer**: a diagram draws itself; labels type; the subject is cut away or X-rayed.
- **Seamless loop**: every cycle divides the duration; the last frame flows into the first.
- **Kinetic type / promo**: 3–6 short lines revealed by motion in the refs' style.

15 s beat sheet: 0–1 hook · 1–4 establish · 4–8 escalate (new state every 1–2 s) · 8–11 peak · 11–13 breath · 13–15 payoff + card. Scale proportionally for other lengths (30 s: three escalating movements; 60 s: add a reprise).

## 5 · Workflow

**a. Study the references → Style Bible.**
Images: view each one, then crop into 2–3 details (texture lives there). Videos: pull frames with ffmpeg instead of guessing:
```bash
ffmpeg -i ref.mp4 -vf "fps=1/1.5,scale=320:-1,tile=5x4" -frames:v 1 ref_sheet.png
ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*"   # cut times → edit rhythm
```
Write a short `STYLE.md`: palette (6–10 hex with roles), grounds, texture recipe, line, shapes, light, depth, composition, type (Google Fonts equivalents), motion rhythm (average shot length, easing personality), sound cues, and a **Do-not-copy list** of what each reference depicts.

**b. Concept.** If the idea rests on real facts (science, history, nature, how something works), research and verify them first (web search if available): the payoff often comes from one true detail (in 1878, photographs proved a galloping horse leaves the ground). In `CONCEPT.md`: logline, why it matters, the continuity device, a beat sheet with timestamps (for each beat: what we see, what motivates any transition, the camera, the sound), the end card. Show the user the logline plus ≤8 beat lines, then continue (wait only if they asked to approve first).

**c. Build `piece.html`**: one self-contained file.
- `<canvas>` at the target size; `const X = cv.getContext('2d', {willReadFrequently: true})` (required: the renderer reads every frame; without it frames go blank or pile up).
- Globals `W, H, FPS, NF`. A **pure** `function render(f)`: same frame for the same `f`, seeded randomness only, nothing carried between frames. Reset transform/alpha/composite/filter at its start; keep save/restore balanced.
- Structure: palette tokens → timeline object `T` (seconds) → `makeAssets()` (pre-render every static texture, sprite and layer once) → `render(f)`. Load fonts, build assets, then set `window.READY = true`. If the URL lacks `?render`, loop `render` with `requestAnimationFrame` for live preview.
- Proven recipes, written as small helpers:
  - **Ink line**: a polyline to a filled ribbon of varying width with tapered ends, wobble reseeded every 2 frames, and draw-on progress `p` (with a nib dot).
  - **Paper**: base colour, soft mottled blobs, fibres, specks and per-pixel noise baked into one canvas. **Grain**: 4 noise frames cycled with `overlay` at ~0.15.
  - **Watercolour**: clip to the shape, add soft radial washes, granulation specks and a blurred darker edge, then white "resist" lines drawn over.
  - **Riso / screen print**: each ink as a rotated halftone dot layer, multiply-blended, offset 1–3 px (misregistration). **Stipple / engraving**: intensity turned into dots, plus parallel hatching clipped to the shadow side.
  - **Text or ASCII inside a shape**: render the shape to a mask, sample it on a coarse grid, and draw a letter or 3×5 dot glyph per filled cell.
  - **Outline of any mask**: mask minus the mask eroded by 8 offset `destination-in` draws. **Pen tracing a silhouette**: marching-squares contour of the mask, then the ink line with progress.
  - **X-ray**: a translucent blurred body, bones as gradient capsules along the rig, and a blurred `lighter` copy for glow.
  - **Time**: `tau(t)` = the integral of a rate function (1 normal, 0.1 slow-mo, 0 freeze) drives the subject, its particles and its sound events.
  - **Motion**: periodic keyframes for cycles (gallop, walk, wings), 2-bone IK for limbs, particles anchored in world coordinates so they stay behind a moving camera.
  - **Transitions**: clip-path wipes by a line fixed in the world, iris circles, windows that grow to fill the frame, flashes on real impacts.
  - **Type**: a typewriter reveal driven by events (footfalls, beats), and words assembled from particles.
- Write files with the file-writing tool, not shell heredocs (JS quotes break them).

**d. Render tool** (write once per project as `render.mjs`). Use the installed Chrome/Edge through `puppeteer-core`; never download a browser:
```js
// node render.mjs piece.html out.mp4 [fromSec toSec]   |   node render.mjs piece.html --stills 0.5 3 7
import puppeteer from 'puppeteer-core'; import fs from 'fs'; import { spawn } from 'child_process'; import { pathToFileURL } from 'url';
const [page, out, ...rest] = process.argv.slice(2);
const exe = [process.env.LOCALAPPDATA + '/Google/Chrome/Application/chrome.exe', 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium'].find(p => fs.existsSync(p));
const br = await puppeteer.launch({ executablePath: exe, headless: true, args: ['--allow-file-access-from-files'], protocolTimeout: 900000 });
const pg = await br.newPage(); pg.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1) });
await pg.goto(pathToFileURL(page).href + '?render=1'); await pg.waitForFunction('window.READY===true', { timeout: 300000 });
const { FPS: fps, NF: nf } = await pg.evaluate(() => ({ FPS, NF }));
const grab = async f => Buffer.from((await pg.evaluate(f => { render(f); return document.querySelector('canvas').toDataURL('image/png') }, f)).split(',')[1], 'base64');
if (out === '--stills') { fs.mkdirSync('stills', { recursive: true }); for (const s of rest) fs.writeFileSync(`stills/s_${s}.png`, await grab(Math.round(+s * fps))); }
else { const [a, b] = rest.map(Number), f0 = a ? Math.round(a * fps) : 0, f1 = b ? Math.round(b * fps) : nf;
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = f0; f < f1; f++) { if (!ff.stdin.write(await grab(f))) await new Promise(r => ff.stdin.once('drain', r)); if (f % 60 === 0) console.log('frame', f); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); }
await br.close();
```
Needs `npm i puppeteer-core` (a few MB) and `ffmpeg` on PATH. If ffmpeg is missing, install it once (`winget install ffmpeg` / `brew install ffmpeg` / `apt install ffmpeg`); if that's not possible, use a bundled binary (Python `imageio-ffmpeg`, or npm `ffmpeg-static`) and put its path in the script. For long renders, run 2–4 copies over separate frame ranges and join them with ffmpeg's concat demuxer (possible because `render(f)` is pure).

**e. Look-dev on stills (Gate A).** Render 5–8 stills at beat boundaries, join them into one row (`ffmpeg -i a.png -i b.png … -filter_complex "[0]scale=360:-1[a];[1]scale=360:-1[b];…;[a][b]…hstack=inputs=N" row.png`) and look. Each still must pass:
- it looks like a finished illustration;
- the frame is full;
- the style comes from the refs and nothing from the Do-not-copy list appears;
- the subject reads at phone size;
- there are no goofy faces or broken joints;
- texture is present;
- text is legible and inside the margins.

Fix and repeat. For characters, pass the pose sheet first.

**f. Render and review motion (Gate B).** Render the video, then read it as a strip: `ffmpeg -i out.mp4 -vf "fps=3,scale=144:-1,tile=15x3" -frames:v 1 strip.png`. Check:
- there is a hook;
- energy rises and there's a breath before the payoff;
- every transition and camera move has a reason;
- no dead stretch longer than ~2 s;
- the continuity device is visible;
- no bugs: flicker, frames piling up, blank segments, clipped text.

**g. Sound.** Write `score.mjs` (plain Node, no packages) that synthesizes a 48 kHz stereo WAV:
- **Instruments**: Karplus-Strong pluck; inharmonic bell; detuned-sine pad; saw/square synth through a one-pole low-pass; filtered noise via a state-variable filter with a cutoff that can glide (whooshes, pen scratch, whisper, dirt, wind); pitch sweeps (blips, risers, sub-drop impacts); kick, clap and hat.
- **Mix**: a Freeverb-style send bus, tanh soft-clip and peak normalisation.
- **Timing**: drive every hit from the same timeline and events as the picture (use a shared list of event times).
- **Guards**: throw on NaN (usually an unknown note name) and on silence.

**h. Deliver.** Combine and loudness-normalise:
```bash
ffmpeg -y -i out.mp4 -i score.wav -c:v libx264 -preset slow -crf 20 -maxrate 22M -bufsize 44M -pix_fmt yuv420p -af "loudnorm=I=-14:TP=-1.2:LRA=11" -c:a aac -b:a 256k -shortest -movflags +faststart final.mp4
```
Save it where the user wants (default: Downloads), share the file if a file-sending tool exists, and summarise: the concept; how each reference's *look* was used; the beats with timestamps; the sound design; that you could not listen to the audio; 3–4 easy tweaks.

**i. Revisions.** Apply the principle behind any feedback to every later decision (e.g. "too many cuts" means fewer, motivated transitions everywhere). Re-check the gates after each change.

## 6 · Keep it lean (the user's time and credits)
- Use what the machine already has: Node, the installed Chrome/Edge, ffmpeg. Don't download browsers or add tools the job doesn't need.
- Stills before video. Use ≤8 stills per pass, look at them as one small contact sheet, and crop full-size only to judge a detail.
- Fix with stills or a short frame range; render the full video only once the stills pass (usually 1–2 full renders in total).
- Edit files in place instead of rewriting them; don't re-read files you just wrote.
- Keep the user posted with one-line progress notes; expect 20–60 minutes for a 15 s piece.
