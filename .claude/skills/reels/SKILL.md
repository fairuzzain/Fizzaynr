---
name: reels
description: Edit raw talking-head or phone footage into a finished 9:16 Reel / TikTok / Short with kinetic captions, smooth zooms, words behind the subject, checklist chips, cards, real UI beats and frame-synced SFX. Presets - Real Estate, Construction, Bold Impact, Ali Abdaal Clean, Faceless Kinetic, Podcast Clip, Finance. Use for "edit this reel", "make a short", "vertical edit", a phone clip, or when director picks a vertical style.
---

# Vertical Edit (9:16, 1080x1920)

> **Client work:** use the client's brand kit for every colour, font, logo and card (`/theme` section 0).
> Presets below set motion and pacing only; the brand overrides their colours and fonts.

Built on `/fx` (effects + build loop + CreatorFX), `/theme` (colours/fonts), `/sound` (audio), `/qa`.

## Workflow

1. **Source**: probe it, cut the requested range (`ffmpeg -ss A -t D`), never edit the original.
2. **Raw cut + words**: `fx/scripts/words.py clip.mp4 --refine`. Find the hook line, retakes, flubs and dead
   air. The **last full take** of each line is the keeper; drop earlier attempts and repeated words, close pauses
   inside lines. Keep jokes and ad-libs. Check the script before cutting a deliberate repeat.
3. **Frame map**: frames at 3-4 moments with a 10% grid → where the face is (at the tightest zoom), where the
   empty space is per shot.
4. **Style + theme**: preset from `references/presets.md`; colours/fonts from `/theme`.
5. **Storyboard first** (unless the user said "don't wait"): time | what they say | on-screen | motion | SFX,
   palette and fonts on top. Wait for OK.
6. **Build** with `new_project.py --aspect 9:16 --video clip.mp4`, then the beats below, then check/snapshot/render.
7. **Audio** `/sound` (vertical = SFX on every pop and change), **finalize** `--target social`, **QA**.

## Beat grammar (what makes vertical work)

- **0-3 s hook**: the strongest line first. A giant word (behind the subject if the background allows) or a bold
  claim on screen by 1.5 s. Captions start on word one.
- **Change something every 1.5-3 s**: a card, a chip, a key word, a smooth zoom on an impact line, a real UI beat.
  Smooth zooms, not hard punch-in jump cuts (use `MK.camera` cuts only if the user wants that punchy feel).
- **Lists in speech → checklist chips**, each landing on its word. **"Not X" → red X chip or strike-through.**
- **Numbers → counters / big condensed numbers.** "the right buyers" → target ring + avatars.
- **End**: a payoff word + hold, or a CTA. No mid-word endings.
- Captions: kinetic typography (`MK.captions`), 2-3 words per phrase, `.mk-scrim` on bright footage; hide them
  while a giant word is on screen.
- **Graphics below the chin**: text, cards and icons never sit on the mouth or face. Measure the chin at the
  tightest zoom and put the graphics band below it (upper chest or bottom band), captions under that band.
  Compact one-row cards that change state fit better than tall stacks. A short hook word may sit above the head.
- **Visuals match the words**: no generic stand-ins. A real UI recreation or the user's own screenshot beats a mock card.
- Safe zone x 150-930, y 210-1530. Everything (including overshoot) stays inside it.

## Talking-head cleanup
- Use `data-media-start` clips for the raw cut (see `/hyperframes-core` creator-editing-recipes) and hide each joint
  with a graphic or a gentle zoom, not a hard jump.
- Low-res source: pre-upscale with ffmpeg (`scale=1080:1920:flags=lanczos,unsharp=5:5:0.6`).

Reference build: `fx/examples/real-estate-reel_9x16.html`.
