# 26. Caption viral (Hormozi-style) (recipe — not yet tested)

**Look:** Fast-cut background images/b-roll with slow zoom, HUGE centred captions 1–3 words at a time (anton/poppins black, white with thick black stroke), keyword in yellow/green, word pops with scale bounce, emojis-like icons pop next to keywords.

**Best for:** Talking points, tips bisnes, motivasi, ads hooks — paling standard TikTok format.

## Flow prompts
2–3 sheets 2x2 of b-roll stills matching each phrase: `…separate realistic photos, <subjects>, vertical-friendly composition centred, no text, thin white gutters, square 1:1.` Icon sheet 4x4 optional.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Image changes every 1.5–3 s (hard cut or quick zoom-cut), constant push-in 1.0→1.08, darken 25% so text pops. Captions synced to phrase segments split by word; each word pops (ease_back 0.12 s). Keyword colour rule: numbers & key nouns.

## Audio (Mix)
Energetic music 'cheerful' 0.25, word_pop quiet, whoosh on image cuts, slam on keywords.
