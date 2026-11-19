# 11. Split screen VS / before-after (recipe — not yet tested)

Look: screen split top/bottom (better for 9:16) or diagonal; labels "SEBELUM / SELEPAS" or "A vs B"; items compared row by row with ticks ✓ and crosses ✗ drawn in code; a slider wipe for before→after; score counter; winner highlight at the end.
Best for: comparisons (with vs without takaful, product A vs B, myth vs fact), transformations, pricing.

## Flow prompts
2x2 sheet: `A 2x2 grid of 4 separate images with thin white gutters, no text, square 1:1, consistent <style>. Image 1 (top-left): <A situation>. Image 2 (top-right): <B situation>. Image 3: ... Image 4: ...` Keep pairs visually parallel (same framing) so the split reads clearly.

## Build (common.py)
- Top half y 0–960, bottom 960–1920 (or diagonal mask polygon). Divider bar with "VS" badge that slams in.
- Images Ken-Burns slightly inside each half. Labels as pill badges.
- Comparison rows: each point appears on both halves at the same time, ✓ (green) / ✗ (red) drawn as thick lines with ease draw-on, pop SFX.
- Before/after wipe: mask x = ease(k)·W revealing the after image with a white vertical line + handle.
- Ending: loser half desaturates (ImageEnhance.Color 0.2) and darkens, winner scales up slightly + ding.
