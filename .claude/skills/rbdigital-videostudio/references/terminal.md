# 31. Terminal hacker (recipe — not yet tested)

**Look:** Black screen, green/amber monospace text typing fast, command prompts, progress bars, 'ACCESS GRANTED' flashes, matrix rain transitions, CRT curvature/scanlines.

**Best for:** Tech tips, cyber security awareness, AI/automation demo, dramatic tech storytelling.

## Flow prompts
None needed.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Monospace font: `get_font('mono')` (JetBrains Mono). Lines appear via typing at 40–60 chars/s; blinking block cursor; scroll when full. Progress bar [#####-----] updating. Matrix rain: columns of random chars falling (cache glyph sprites). Scanlines + slight green glow (blur add).

## Audio (Mix)
Rapid typing clicks, beep on 'ACCESS GRANTED', low drone/tense bed.
