# 28. Timeline sejarah (recipe — not yet tested)

**Look:** Horizontal timeline line across the screen that scrolls left; year markers pop (big numbers), event cards with image + 1-line text rise above/below the line alternately, progress dot travels along.

**Best for:** Sejarah syarikat/produk, evolusi (contoh sejarah takaful), biografi, milestone bisnes.

## Flow prompts
2 sheets 2x2 of event images (archival/illustrated consistent style).
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
World strip width = N·900 px; camera x moves with ease per event; line + ticks drawn in code; year labels anton 120 count-up/slam; cards (image + text) alternate above (y 500–1000) and below (y 1100–1600) the line at y 1050.

## Audio (Mix)
Whoosh per move, slam on year, typing for text, music lofi/documentary drone.
