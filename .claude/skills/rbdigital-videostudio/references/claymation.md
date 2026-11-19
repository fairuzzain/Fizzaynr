# 32. Claymation stop-motion (recipe — not yet tested)

**Look:** Scenes that look like clay/plasticine models; motion is faked with 8–12 fps holds, tiny jitter, and swapping between 2–3 variant images of the same scene; hand-made charm.

**Best for:** Cerita kanak-kanak, iklan comel, explainer santai, kisah lucu.

## Flow prompts
2 sheets 2x2 — for each scene request 2 slightly different poses in adjacent panels: `…separate claymation stop-motion scenes, plasticine characters and set, soft studio lighting, <scene A pose 1>, <scene A pose 2>…, no text.`
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Alternate between pose variants every 2–4 frames at 12 fps (hold), add jitter (±3 px, ±0.5°) per step and slight brightness flicker; cuts on phrase boundaries; captions in rounded bubbly font (comicneue) on clay-coloured pills.

## Audio (Mix)
Playful 'comedy' music, squish pops (low pop 200→400 Hz), boing (sine sweep up with vibrato).
