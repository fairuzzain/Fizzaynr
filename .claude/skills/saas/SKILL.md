---
name: saas
description: Create a fully code-built motion graphics promo from a prompt alone (no footage) - SaaS / product / agency launch videos in the viral Opus-style look - prompt bars, glass UI, 3D dashboards, progress steps, counters, logo orbit, kinetic type, synced to a voiceover or music. Presets - Dark Neon, Clean SaaS Glass, Crimson Brand Punch, Character Explainer. Renders 16:9 or 9:16. Use for "SaaS video", "motion graphics promo", "product launch video", "make an ad from this script", "showreel".
---

# SaaS Motion

> **Client work:** use the client's brand kit for every colour, font, logo and card (`/theme` section 0).
> Presets below set motion and pacing only; the brand overrides their colours and fonts.

No footage: everything is drawn in code with `/fx`. Works from a one-line prompt.

## Workflow

1. **Brief → script**: write 2-3 rough 15 s scripts (on-screen text + visual per beat) and recommend one.
   Typical arc: hook question (0-3 s) → product UI showing the promise (3-9 s) → proof/steps (9-12 s) → logo + tagline.
2. **Voice**: the user's ElevenLabs file, or free Kokoro (`/sound`), or music only. Get word timings with
   `fx/scripts/words.py vo.mp3 --refine`; **every beat lands on its word**.
3. **Brand**: logo files → colours (`/theme`); no logo → clean text logo.
4. **Layout by aspect**:
   - 16:9: kinetic text in a left column (x 160-880), UI in a right column (x 980-1760); intro/outro centred.
   - 9:16: text top (y 330-650), UI centre (y 760-1380), labels bottom.
5. **Build** (`new_project.py --aspect 16:9|9:16 --theme theme.json`), check, snapshot, render.
6. **Audio**: SaaS rule = SFX on every UI move, music carries the piece (under the voice if there is one).
7. **Finalize** `--target youtube` (16:9) or `social` (9:16), **QA**.

## Scene kit (pick 4-5)
| Scene | Build |
|---|---|
| Prompt bar | glass pill, typewriter text, caret blink, cursor glides to Generate, click + ripple on the key word |
| 3D dashboard | `MK.tiltIn`, rows/modules light up on each spoken word, timeline tracks grow, playhead sweeps, slow push |
| Before/after words | "built in **MINUTES**, not ~~WEEKS~~" (strike) |
| Zoom-through | `MK.zoomThrough` into the next scene |
| Progress steps | 4 nodes ticked on words, fill bar, % counter, "Rendering" → "Ready" |
| Stat cards | glass cards with counters (only real numbers, or flag them as placeholders) |
| Hero word + flash | giant glowing word (SELL.) with a white flash |
| Logo orbit | logo lands, tool icons orbit, wordmark sheen, letter-spaced subline, tagline flanking the logo |

## Presets
- **Dark Neon** (default): near-black #04080f, one glow colour (cyan #1ec8ff / electric blue #2e7bff / mint #3ef0b0),
  drifting blur blobs + faint grid, glass UI, Inter Tight 900 + Instrument Serif Italic + JetBrains Mono.
- **Clean SaaS Glass**: #f7f9fd background, pastel blobs, ink #1c1c28, accent #3a5bff, per-word blur text, glass
  cards with 20 px backdrop blur, light/dark switch every 2 beats. Manrope/Inter.
- **Crimson Brand Punch**: #3a0006 → #c4001a gradient, white + gold, Poppins 800, pill highlights, cursor +
  selection box, stat counters, 3-4 s hard cuts.
- **Character Explainer**: one brand hue on dark, Poppins/Nunito rounded, a simple SVG mascot (blink + bob) anchoring
  each scene, UI chips floating around it, icon line draw-ons.

Reference build: `fx/examples/saas-promo_16x9.html`.
