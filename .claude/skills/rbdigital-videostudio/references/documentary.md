# 6. Dokumentari / Ken Burns (recipe — not yet tested)

Look: realistic or archival-style images, slow pan & zoom (Ken Burns), cross-dissolves, letterbox bars optional, lower-third title cards (place/date) in clean serif or typewriter font, subtle film grain, serious narrator.
Best for: history, true stories, biographies, places, "kisah sebenar".

## Flow prompts
2 sheets of 4 (2x2) scene images: `A 2x2 grid of 4 separate cinematic documentary photographs with thin white gutters, no text, no borders, square 1:1. All: realistic, natural light, <era> <location>, muted film colour grade, 35mm grain. Image 1 (top-left): ...`. For vertical impact, compose subjects centrally (the image will be cropped to 9:16 from a square → zoom in).

## Build (common.py)
- Each scene image (≈615 px square) is upscaled to cover 1080x1920 → crop is a central vertical slice; Ken Burns = animate crop box (start/end rect) with ease; alternate zoom-in / zoom-out / pan-left / pan-right. Upscaling costs quality → keep zoom subtle and add grain to hide softness.
- Transitions: 0.6 s cross-dissolve (Image.blend of both scenes), sometimes dip to black.
- Text: lower third (y≈1550) with thin bar + typewriter reveal: "Johor Bahru, 1942". Big chapter title cards on black between acts.
- Colour: slight desaturation + warm/teal grade (ImageEnhance.Color 0.8), vignette.
- Audio: `drone` low + sparse `tense`/`lofi` at 0.2, boom on revelations, typing on lower-third reveals.
