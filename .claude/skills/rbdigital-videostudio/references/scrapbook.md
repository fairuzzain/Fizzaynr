# 1. Scrapbook sticker (TESTED — "5 Fakta Ikan Jerung")

Look: paper backgrounds (kraft / notebook), paper-cut stickers with white border pop in/out with bounce, word-by-word sticker captions, stop-motion jitter at 12 fps, cheerful plucked music + pops.
Best for: facts, tips, lists, light explainers.

## Flow prompts
- 2 backgrounds (alternate per scene):
  `Vertical 9:16 scrapbook background, <light blue kraft paper texture | old notebook paper with faint lines and coffee stain, torn edge at top>, <subtle corner doodles>, empty center, top-down flat lay, no text`
- ONE sticker sheet, ≤16 items, 4x4 (objects A1.., decorations D1.. e.g. red arrow, yellow question mark, masking tape, red X, torn paper strip):
  `A sticker sheet with N separate items arranged in a neat 4x4 grid with wide empty space between each item, nothing overlapping, no text labels. Row 1: ...; ...; ...; .... Row 2: ... . Every item is a paper cutout sticker with thick white border, scrapbook collage style, slightly textured paper, soft drop shadow, flat colors, consistent style, all isolated on a plain solid dark grey background. Square 1:1, high resolution.`

## Build
1. `cut_sheet.py sheet assets --names A1,...,D5` → view `_check.png`.
2. Copy `examples/scrapbook/shark_storyboard.py`, set backgrounds, rewrite scenes. API in `scripts/scrapbook_engine.py` docstring: `scene()`, `el(sprite(), x, y, t0, t1, rot, anim)`, anim `pop|slam|fall|word`, `caption(words, y, t0, t1, size, color, step)`.
3. Layout: label "FAKTA #n" y≈300–330 (90) · visual y≈600–1250 · main caption y≈1320–1450 (105–120) · sub caption y≈1500–1620 (70). Hero sticker width 420–560, secondary 230–380. Comparison scenes stacked top/bottom with torn strip + "VS".
4. `python storyboard.py preview` → view grid → `run(out, DUR, vo='vo.mp3')` (engine renders in one go ~0.1 s/frame; if >50 s video, split: render frames via common.render_chunk with engine.compose).
