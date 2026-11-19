# 48. Lakaran → warna (recipe — not yet tested)

**Look:** Each scene starts as a rough pencil sketch that draws itself, then colour floods in (wipe or brush-shaped reveal) to the final painted image; a pencil/brush tip follows the reveal edge.

**Best for:** Proses kreatif, before/after, kisah 'dari idea ke realiti', produk dari konsep ke siap, kandungan design.

## Flow prompts
Ask for the coloured image only (2x2 sheet). The sketch is derived in code.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Sketch from colour image: gray → invert → GaussianBlur → colour dodge (gray / (255 - blurred_inverse)) = pencil lines; add paper texture. Draw-on: reveal sketch with a scanline/noise rank mask; then colour reveal with a growing brush mask (union of soft circles along a path, or a diagonal wipe with noisy edge). Hold the final image with slow zoom, caption in caveat.

## Audio (Mix)
Pencil scratch during sketch, soft 'swoosh' for colour, lofi/cheerful 0.25.
