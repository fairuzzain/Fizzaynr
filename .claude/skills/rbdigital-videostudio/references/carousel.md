# 27. Photo slideshow beat (recipe — not yet tested)

**Look:** TikTok photo-mode feel: photos with white borders slide/zoom in exactly on music beats, some split-grid moments (2–4 photos), short text overlays per photo, flash transitions.

**Best for:** Showcase produk, before/after, portfolio, recap event, jalan-jalan.

## Flow prompts
the user's own photos, or 2 sheets 2x2 of photos.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Generate beat grid from bpm (e.g. 120 → cut every 0.5/1.0 s); transitions alternate: zoom-punch (1.15→1), slide, white flash 0.08, grid split. Text: small caption pill bottom (poppins). Keep 12–20 photos for 30 s.

## Audio (Mix)
Beat-based music (synth 'cheerful' at 120 bpm, plus kick = low sine thump every beat), whoosh on some cuts.
