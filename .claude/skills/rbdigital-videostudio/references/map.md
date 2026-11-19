# 16. Peta perjalanan (recipe — not yet tested)

**Look:** Hand-drawn/vintage map; dashed route line draws itself from pin to pin, camera follows the moving head of the line, location pins drop with bounce, small photo cards pop beside each pin with place name labels, compass rose rotating subtly.

**Best for:** Sejarah, travel, kisah 'dari kampung ke bandar', franchise/cawangan expansion, delivery coverage.

## Flow prompts
Background: `Vertical 9:16 vintage hand-drawn illustrated map of <region>, parchment paper, no text, no labels, empty areas for markings` (make it tall; or square and extend). Photos: 2x2 sheet.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
World = map image upscaled 2x; route = list of (x,y) waypoints; interpolate along cumulative length, draw dashed polyline up to progress k with `ImageDraw.line` segments; camera (like polaroid CAM) centred on route head, clamped. Pins: red teardrop drawn in code. Labels in caveat/marker font on paper tags. Never trust AI map geography — labels are ours; keep map stylised.

## Audio (Mix)
Pencil scribble while drawing route, pop on pin drop, ding on photo card; music cheerful/lofi.
