# 30. Neon / cyberpunk (recipe — not yet tested)

**Look:** Dark city/grid background, neon tube text that flickers on (glow = blurred copies in cyan/magenta), scanning light sweeps, glitch transitions, synth vibe.

**Best for:** Tech, AI, gaming, event malam, promo app (AutoSocial AI).

## Flow prompts
Background: `Vertical 9:16 dark cyberpunk city street at night, neon reflections, rain, empty center, no text, no signs with letters`. Optional icons in neon style on black.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Neon text: render text, make glow via GaussianBlur(20) of coloured version composited additively (ImageChops.add) under a white core; flicker = random on/off first 0.4 s. Background slow push-in + rain streaks (random lines moving down). Transitions: glitch (Post.glitch) + RGB split.

## Audio (Mix)
Synthwave: saw-ish (sum of harmonics) bass + arpeggio at 100 bpm, electric buzz on neon flicker, glitch static.
