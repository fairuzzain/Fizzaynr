# 22. Mind map (recipe — not yet tested)

**Look:** Central bubble with main topic; branches grow out (curved bezier lines drawing on) to child nodes that pop in with icons; camera zooms into each branch then zooms out to the full map at the end.

**Best for:** Ringkasan konsep, rancangan bisnes, pilihan pelan, perbandingan banyak faktor.

## Flow prompts
Icon sheet 4x4 (flat icons on dark grey). Background plain drawn in code (dotted grid) or `Vertical 9:16 soft paper texture, empty, no text`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
World canvas 2160x3840; node layout radial; branch = quadratic bezier sampled, drawn up to k; nodes = rounded rect with pastel fill per branch + icon + text. Camera keyframes per branch, final overview. Text short (≤4 words/node).

## Audio (Mix)
Pop per node, soft whoosh per camera move, cheerful/lofi 0.25.
