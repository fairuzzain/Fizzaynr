# 4. Kinetic typography (recipe — not yet tested)

Look: text only, big bold words (Anton/Bebas) hitting the beat: slam in, slide, scale punch, one keyword per beat highlighted in accent colour (yellow/red) on a dark or solid-colour background; occasional full-screen single word; subtle background texture/gradient that shifts colour per section.
Best for: quotes, hooks, motivational, tips, ad hooks, announcements. Fastest style — no Flow assets needed (optional: 1 background texture prompt).

## Flow (optional)
`Vertical 9:16 abstract dark gradient background with subtle grain and soft light leak, empty, no text` (1–2 colour variants).

## Build (common.py only)
- Break VO into phrases with `vo_segments.py -32 0.18`; each phrase = one "card" of 1–4 words. Estimate word times inside a segment by splitting its duration proportional to word length.
- Card layouts (rotate through): (a) stacked words, each line different size, left-aligned x=90; (b) one giant word centred, fills width (fit font size to 900 px); (c) small lead-in + huge keyword; (d) word-by-word typewriter.
- Animation per word: slam (scale 1.6→1 in 0.12 s + tiny shake), slide from left with ease_out, or mask reveal (crop width grows). Previous card exits with fast slide/scale-down 0.15 s. Keyword in accent colour, rest white.
- Background colour switches at section changes with a quick whoosh + flash 0.1.
- Audio: `music('lofi' or 'cheerful')` with a steady beat; word_pop per word, slam per keyword, whoosh per card change.
- Very cheap to render (<0.05 s/frame) — cache each word sprite.
