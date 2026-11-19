---
name: fx
description: Shared motion-graphics effects library and build engine for the Edit Kit (HyperFrames + GSAP). Use whenever an edit needs kinetic typography captions, glass UI cards, checklist chips, text behind a subject, smooth zooms, counters, cursor clicks, 3D tilted dashboards, logo orbits, progress steps, decoder text, a hero folder, picture-in-picture, social proof posts, chat UI, a light studio layout, grain, flashes or any named effect, and to scaffold, render and finalize a MotionKit project. Called by reels, youtube, saas and director.
---

# Motion FX

One runtime (`assets/motionkit.js` + `assets/motionkit.css`) holds every effect. Compositions are HyperFrames HTML with
ONE paused GSAP timeline; every helper adds tweens to it, so renders are frame-exact and repeatable.
Read `/hyperframes-core` once before writing composition HTML (lint rules matter).

## Platform notes
Commands are written for macOS/Linux. On **Windows** use `python` (or `py`) instead of `python3`, run shell steps in
Git Bash or PowerShell, and quote paths with spaces. `ff.py` finds ffmpeg.exe from winget, choco, scoop or npm.

## Build loop (every edit)

1. **Scaffold**: `python3 scripts/new_project.py <dir> --aspect 9:16|16:9|1:1 --duration <s> --theme theme.json [--video clip.mp4]`
   (copies runtime, GSAP, free fonts, grain texture; theme.json comes from `/theme`).
2. **Words**: `python3 scripts/words.py <clip> --start 0 --end 20 --refine` → paste `WORDS` into the composition.
   Every animation that belongs to a spoken word starts on that word's timestamp.
3. **Measure the frame** before placing anything: grab a frame with a 10% grid and note where the face/body is
   and where the empty space is. Text and cards go in empty space, never over the face.
4. **Write** `index.html` with the helpers below. Keep a `CUES` list (time + sound type) for every impact moment
   while you write: `/sound` turns it into SFX that land on the exact frame.
5. **Check**: `npx hyperframes check` (0 errors), then `npx hyperframes snapshot --at t1,t2,...` and LOOK at every frame.
   Snapshot a moment 0.3 s after an entrance, not during it.
6. **Render**: `npx hyperframes render -o render_silent.mp4` → audio via `/sound` →
   `python3 scripts/finalize.py --video render_silent.mp4 --audio mix.wav --out Final.mp4 --target social|youtube|master`.
7. **QA**: `/qa` before delivering.

## Helpers (`const MK = MotionKit(tl)`)

| Helper | Effect | Typical use |
|---|---|---|
| `MK.captions({words, container, end, keys?, hide?})` | **Kinetic captions**: serif italic lead words + ONE big bold glowing key word per phrase, each word blur-rises on its timestamp, no boxes | every edit with speech |
| `MK.lead(sel, [[w,t],...])` | serif lead line, word by word | "most agents just", "built in" |
| `MK.popIn(sel,t)` / `MK.slam(sel,t)` / `MK.blurRise(sel,t)` | key word entrances (back-out pop / scale-down hit / rise) | giant words |
| `MK.out(sel,t)` | blur-up exit | end of a beat |
| `MK.strike(sel,t)` | line drawn through a word | HOPE, WEEKS |
| `MK.zoom(sel,t,{to,origin,inDur,hold,outDur})` | **smooth eased push in, hold, ease out** (default) | impact lines on talking heads, 4-6 per minute |
| `MK.camera(sel,[{t,scale,origin,push}])` | hard punch-in/out cuts + slow push | only when the user asks for punchy jump cuts |
| `MK.cardIn/cardOut(sel,t,±x)` | glass card slides in with a slight 3D turn | side cards (YouTube) |
| `MK.chipIn(sel,t)` + `MK.draw(tickPath,t+0.1,0.22,30)` | checklist chip + tick draw-on | lists in speech |
| `MK.counter(sel,from,to,t,dur,fmt)` | rolling number | stats, followers, % |
| `MK.type(sel,text,t)` + `MK.blink(caret,t)` | typewriter + caret | prompt bars |
| `MK.click(cursor,ripple,target,t,{x,y})` | cursor glide, press, ripple | UI demos |
| `MK.tiltIn(sel,t)` / `MK.zoomThrough(sel,t)` | 3D panel settles flat / zoom through to next scene | SaaS dashboards |
| `MK.draw(svgPath,t,d,len)` | stroke draw-on (graphs, rings, curves) | charts, target rings |
| `MK.grain(sel,dur)` / `MK.flash(sel,t)` / `MK.drift(blob,dx,dy,dur)` | film grain, white flash, drifting glow | texture |

CSS building blocks: `.mk-cam` (video wrapper you scale), `.mk-scrim` (bottom gradient so white text reads on bright
footage), `.mk-vig`, `.mk-grain`, `.mk-flash`, `.mk-grid`, `.mk-blob`, `.mk-lead`, `.mk-big` + `.mk-glow`,
`.mk-caps`, `.mk-glass` (light glass on dark), `.mk-dark` (dark glass on footage), `.mk-card`, `.mk-chip`, `.mk-tick`, `.mk-x`.

Full catalog with code for every effect, including ones built inline (text behind subject, logo orbit, progress steps,
MLS-style status card, target ring + avatars, hearts float, bar chart): `references/effects.md`.
Working compositions to copy from: `examples/` (real-estate reel 9:16, SaaS promo 16:9, YouTube talking head 16:9,
creator explainer 16:9).

## CreatorFX (`const CF = CreatorFX(tl, { root: "#root" })`)
Creator-YouTube effects from a real channel edit: decoder text, metallic shimmer, a hero folder that opens,
picture-in-picture showcase, rounded camera box on a light studio stage, X-style proof posts, WhatsApp-style chat,
glass progress bar. Catalog, markup and the "real UI beats" list: `references/creator-effects.md`.

## House rules (non-negotiable)

- **Captions are kinetic typography, never boxed/pill karaoke.** On bright footage add `.mk-scrim`.
- Keep text inside the safe zone: 9:16 → x 150-930, y 210-1530; 16:9 → x 96-1824, y 54-1026. Never over the face.
- One accent colour for key words; red only for negatives (hope, waiting, weeks, never).
- **Human typography**: big words at about -0.015em tracking with a little word-spacing (never so tight words merge);
  small labels in the sans, sentence or title case, no wide-tracked uppercase mono kickers; even gaps between a lead
  line, its key word, icons and cards.
- **Talking heads**: smooth `MK.zoom` on impact lines only, never hard punch-in jump cuts unless asked. Measure the
  face at the tightest zoom and keep every graphic off the face and mouth (side wall, chest band or bottom band).
- **Every visual must match the exact words** (no "3 AM" over daylight, no reels on "100 clients"). Prefer real UI
  recreations and the user's own screenshots over invented mock cards; no picture fits → speaker + one key word.
- No em/en dashes in on-screen copy. Never invent stats; UI numbers that are illustrative must be called out to the user.
- Every pop/hit/click/whoosh moment gets a cue in `CUES` with the **impact** time (when it lands, not when it starts).
- HyperFrames lint: no CSS transform on an element GSAP also transforms (use `fromTo`), no `letterSpacing` tweens
  (animate per-letter `x` instead), `<audio>`/`<video>` need ids, only one root `index.html` per project folder.
