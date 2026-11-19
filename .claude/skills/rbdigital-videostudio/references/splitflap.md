# 44. Split-flap board (papan airport) (recipe — not yet tested)

**Look:** Airport/train departure-board text: each character tile flips through random letters before landing on the right one, rows fill one by one, board clacks; headings like 'DESTINASI: BEBAS HUTANG'.

**Best for:** Pengumuman, senarai tips/langkah, launch tarikh, quote, 'perjalanan' metafora.

## Flow prompts
None needed (board drawn). Optional background `Vertical 9:16 dim airport terminal interior, blurred, no text`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Grid of tiles (e.g. 12 cols x 10 rows, tile 80x110) drawn once as dark rounded rects with a centre split line; each tile animates: from t_start, show random chars changing every 0.04 s for 0.3–0.9 s (staggered left→right), top-half flip effect by squashing the glyph image vertically at each change; final char locks. Font: oswald/bebas white-yellow. Cache glyph images per char.

## Audio (Mix)
Clack per tile change (very short noise click, many layered → rattling), low ambient terminal hum, ding when a row completes.
