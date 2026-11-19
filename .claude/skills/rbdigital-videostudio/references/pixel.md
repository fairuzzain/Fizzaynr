# 14. Pixel art / game 8-bit (recipe — not yet tested)

**Look:** Chunky pixel scenes, pixel character walks between scenes, HP/XP bars, 'LEVEL UP!' flashes, RPG dialogue box with typewriter text + blinking ▼, coins popping, screen shake on damage.

**Best for:** Perjalanan hidup/bisnes sebagai 'level', tips bertahap, kisah motivasi, gamified content.

## Flow prompts
Scenes 2x2: `A 2x2 grid of 4 separate 16-bit pixel art game scenes, <scenes>, vibrant limited palette, crisp pixels, no text, no UI, thin white gutters, square 1:1.` + sprite sheet 4x4 of pixel items/characters on solid dark grey background.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Upscale with NEAREST (never bilinear) to keep pixels crisp; snap all positions to 4–6 px grid and animate at 12 fps. Dialogue box: black rect with white 6 px border bottom (y 1450–1800), pixel-ish font (bebas fallback, or draw with NEAREST-scaled small font), letters appear 30/s. UI bars drawn as rects. Transitions: pixel-dissolve (random block reveal) or iris wipe.

## Audio (Mix)
Chiptune: synth square waves (np.sign(sin)) arpeggio instead of plucks; blip per letter (short square 1200 Hz), coin = two-note square up, level-up = rising arpeggio.
