# 33. Isometric 3D scene (recipe — not yet tested)

**Look:** Clean isometric diorama illustrations (rooms, cities, office); camera glides across a big isometric world; elements pop up from the ground with bounce; labels with leader lines.

**Best for:** Explainer bisnes/sistem, 'sehari dalam hidup', proses kerja, property/rumah.

## Flow prompts
2 sheets 2x2: `…separate isometric 3D illustration scenes, clean low-poly style, soft pastel colors, <scenes>, no text…`; or one big `square 1:1 isometric city map` as the world plus a 4x4 sheet of isometric objects on dark grey.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
World = big image; camera keyframes like polaroid; objects from sticker sheet rise from +60 px with ease_back and shadow; labels: white rounded pill + thin line to object.

## Audio (Mix)
Soft pops, whooshes, lofi/cheerful 0.25.
