# 41. Foto + contengan (annotated photo) (recipe — not yet tested)

**Look:** Real photo backgrounds with hand-drawn annotations appearing on top: red circles, arrows, underlines, scribbled notes, emoji-like doodles, 'zoom here' — like a creator marking up a screenshot.

**Best for:** Breakdown iklan/post, review, tips sebelum-selepas, analisis gambar produk atau rumah.

## Flow prompts
Photos 2x2 sheet or the user's own screenshots/photos (best).
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Annotations drawn in code with marker-like strokes: jittered polyline circles (radius noise), arrows with hand wobble, text in marker/caveat; reveal via progressive point count. Camera zoom to annotated area with crop-resize.

## Audio (Mix)
Marker squeak (bandpassed noise), pop, lofi 0.25.
