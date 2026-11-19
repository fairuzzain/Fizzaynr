---
name: one-take-product-film
description: Make a 15-20 second 9:16 product film for an app or brand as one continuous camera flight with no cuts. The camera climbs through a stylised world, pulls back until that world is the app screen on a phone, dives back in and lands on the logo. Built in code with HyperFrames, using a strict three-colour palette, a scene plan where every beat has a job, sound placed on the frame and an ending that stops on the call to action. Use for "one-take product film", "app promo reel", "continuous camera product video", "drone-shot style app ad", "film like the Strava video", or any short product reel that should feel expensive and not like AI.
---

# One-take product film (9:16, code-built)

One HTML file with a single timeline and `window.seek(t)`, rendered to MP4 with HyperFrames.
The look comes from four decisions written down to the second before any code is written.
The model can't guess these well, so each one gets a written answer.

Load first: `hyperframes` (render contract), `antislop` + `antislop-ui` + `antislop-copywriting` (DURING mode).
Read `brand.md` / `MOTION.md` in the project if they exist.

## The four decisions

1. **Open on a feeling, not on the product.** Second 0 shows a moment the viewer already
   knows (a hill on the morning run, an inbox at 23:00, a queue at the bank). The product
   name and logo stay hidden until the last ~4 seconds.
2. **Exactly three colours.** One action colour (routes, highlights, the dot the eye
   follows), one dark ground, one reward colour (crown, badge, win state). Write the hex
   codes and where each is allowed. Any other colour is a defect. White and tints of the
   three are fine for type.
3. **Every beat has a job.** Plan 7-9 beats. Each row says: start second, what moves,
   what the viewer should feel, the job. A beat without a job gets cut. Usual arc:
   question → rival or problem → how it works → the prize → you take part → the effort
   → the reward → a small human joke → logo + CTA.
4. **Polish that doesn't read as AI.**
   - One camera, never cut. Changes of scale (world → phone screen → world) do the
     work of transitions: pull back until the world becomes the UI, then dive through
     the glass.
   - One leading line (route, thread, cursor path) is always on screen and leads the eye
     into the next beat.
   - Every move eases in and out (no linear moves, no pops). Camera moves overlap
     slightly, so the flight never stops dead.
   - No stock "logo pops up / text fades in" moves.
   - **The ending stops.** The CTA holds ~1.5-2.0 s, then fades out (follows the global
     outro rule: hold + fade to black + audio fade). No 5-second slow outro where nothing
     happens, because viewers swipe away early and watch time drops.

## Workflow

### Step 1: Ask, then wait
1. Product name, the one line, and the CTA, word for word.
2. **The facts list.** Every number, name and claim allowed on screen. Nothing invented:
   rival names, times and stats are placeholders until the user confirms them.
3. The everyday moment for second 0 (offer 3 options if none is given).
4. The three colours (or a logo / brand file to take them from).
5. Language. This sets VO and all on-screen text (language lock: 100% Malay or 100% English).

### Step 2: Write the plan (`plan.md` in the project folder)
- Palette table: hex, name, where it's allowed.
- Beat table: `start s | what you see | VO line | feeling | job`. Total 15-20 s.
- Camera path: one sentence per beat on position, scale and direction, plus where the
  world → UI → world change of scale happens.
- Sound map: one row per sound, `frame | event | sound type | level (dB) | why`.
- VO: voice auto-locked by the genre matrix (product/commercial → Fola-style bright voice;
  English via Nexabot TTS, Malay via `gemini_tts.py`). State voice + tone.

### Step 3: Storyboard approval (mandatory)
Render one still per beat from the HTML (`seek` to the mid-point of each beat), tile them
into one contact sheet, put the sheet + plan in an artifact, and **wait for "approved"**.
If a beat needs a picture that code can't draw (photo product, real person), make it
with Nexabot `img`, not a paid connector.

### Step 4: Build
- 1080×1920, 30 fps, one timeline. All motion is a function of `t` (no time-based
  CSS animations, no `setTimeout`).
- The camera is one transform (or a three.js camera), driven by keyframes with eased
  segments. Scale changes come from that camera, not from cuts.
- On-screen text: only titles, UI labels, stat callouts and the CTA. **No captions** that
  transcribe the VO unless the user asks for them.
- Type has to read on a phone: keep it ≥ 48 px for key words, inside safe margins
  (top 220 px, bottom 320 px clear of the platform UI).

### Step 5: Sound
SFX pipeline only: `openverse-sfx` (check `${SFX_DIR:-$ROOT/assets/sfx}/` first) →
`real-sfx` places each sound on the frame from the sound map, mixed with `--voice-safe` →
`earshot critique` on the final mix. Music bed from Nexabot `music`. Voice sits clearly
above music and SFX.

### Step 6: QA and delivery
- 1 fps contact strip of the render: check every colour against the palette, spelling of
  every word against the facts list, no stray text, no caption track.
- Gate 4: audio balance, VO sync to the beat changes, outro hold + fade.
- Encode on the GPU (`h264_nvenc`). Save to `Downloads\Video Ai\<project>` and sync to
  Drive `AI VIDEO/<MMM YYYY>/<project>`. Revisions go in `Editted-<DDMMYYYY>`.

## Checks before calling it done
- Does second 0 work with the sound off and no product name on screen?
- Count the colours in five random frames. More than three families means it fails.
- Point to each beat's job. If you can't, cut the beat.
- Is there a single frame where the camera cuts or the leading line disappears?
- Does the film end within ~2 s of the CTA appearing (plus the fade)?
