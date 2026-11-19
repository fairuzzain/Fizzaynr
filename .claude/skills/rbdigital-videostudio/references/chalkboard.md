# 21. Chalkboard / kelas (recipe — not yet tested)

**Look:** Dark green chalkboard with smudges; chalk text writes itself (rough edges, grain), chalk diagrams and underline/circle annotations, eraser swipe clears between sections; optional teacher hand silhouette.

**Best for:** Belajar, formula kewangan, tips sekolah, penerangan konsep takaful step by step.

## Flow prompts
Background: `Vertical 9:16 dark green school chalkboard, chalk dust smudges, wooden frame edge at bottom, empty, no text`. Doodles 4x4 sheet: `…white chalk line drawings on black background…`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Chalk text: render caveat/marker text in off-white, multiply by noise mask (random dropouts) for chalk texture, reveal left→right (rank = x) like whiteboard. Doodles: cut from black bg (bright pixels), reveal by sweep. Eraser: soft-edged dark rect sweeping and blending text away.

## Audio (Mix)
Chalk scratch (bandpassed noise with jitter) during writing, knock of chalk tap on full stops, lofi music 0.2.
