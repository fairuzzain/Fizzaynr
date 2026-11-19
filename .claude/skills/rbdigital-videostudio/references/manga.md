# 2. Komik / manga panel (TESTED — "Ali Kata Takaful Tak Perlu")

Look: B&W manga panels slide in one by one (or slam in for dramatic beats) over speed-line backgrounds (light / dark), slow push-in inside each panel, white speech bubbles (Comic Neue) with tails, red Bangers SFX ("KRAK!!", "WOOSH!"), yellow narrator boxes at bottom, screen shake + white flash on impact, outro with big slogan.
Best for: skits, stories, sales stories with a punchline, relatable situations.

## Flow prompts
2 pages, each `square 1:1, exactly 4 panels in a 2x2 grid with thick black borders and white gutters, no text, no speech bubbles, no sound effect lettering`, character descriptions repeated identically in both, `Japanese manga style, clean ink lines, screentone shading, high contrast, dynamic angles`. Page 1 = panels 1–4, page 2 = 5–8; page 1 as ingredient for page 2. Flow still sometimes adds bubbles/text → paint out and replace with your own bubble.
Note: Flow returned 3:4 pages (896x1200) not square — handle any aspect.

## Build (copy `examples/manga/manga.py` + `audio.py`)
- Crop panels via white gutters (threshold `mean>0.97`), keep black border. Panel display width 960, centre y≈980 → panel spans ~y 330–1630; bubbles overlap panel top, narrator box y≈1790.
- Timeline tables: `PANELS (id, t0, t1, bg, enter right|left|slam, rot)`, `ITEMS` (bubbles/sfx/custom overlays in panel coords, 420-wide space), `NARR`, `SHAKE`, `FLASH`.
- Bubble tails: short (100–200 px) pointing at the mouth, never across a face. Jagged bubble for crying/shouting.
- Audio: comedy music, mute during the drama (impact → reveal) with a low drone, resume for the punchline; impact SFX on slams, whoosh on slides, pops on bubbles.
- Speed: ~0.3 s/frame → render in 3 chunks of ~330 frames.
