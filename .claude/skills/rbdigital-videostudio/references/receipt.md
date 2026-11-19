# 18. Resit / bil (recipe — not yet tested)

**Look:** Long thermal receipt prints out from the top of the screen line by line (with printer jitter), items + prices typed in monospace (typewriter font), subtotal lines, then TOTAL slams in red and the camera zooms; can compare two receipts (with vs without).

**Best for:** Kos hidup, kos hospital vs caruman takaful, bajet bulanan, kos buka bisnes, 'berapa sebenarnya…'.

## Flow prompts
None needed. Optional background `Vertical 9:16 dark wooden table surface with soft top light, empty, no text`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Receipt sprite drawn in code: off-white paper (noise texture), zigzag torn bottom edge, text lines appended as time passes; receipt y slides down by line height each new line (printer feed). Numbers from the user or searched facts; hedge. TOTAL: count-up animation then slam + shake. Camera: crop-zoom onto TOTAL at end.

## Audio (Mix)
Thermal printer buzz (bandpassed noise 1.5 kHz chunks) per line, cash-register ding on total, music lofi 0.2 or tense for shocking totals.
