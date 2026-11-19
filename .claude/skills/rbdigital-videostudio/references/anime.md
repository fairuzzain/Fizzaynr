# 36. Anime opening (recipe — not yet tested)

**Look:** Fast cinematic cuts of anime-style character shots, character intro cards (name + role in big katakana-style layout using our text), speed lines, colour flashes, title logo slam at the end synced to a beat drop.

**Best for:** Perkenalkan team/agent, launch dengan hype, cerita watak, 'meet the founder' style.

## Flow prompts
2 sheets 2x2: `…separate anime key visual frames, vibrant colors, dramatic lighting, same characters described identically, <shots>, no text…`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Cuts every 0.5–1.2 s following bpm grid; each shot has fast push-in or slide + speed-line overlay (radial lines drawn in code, alpha 0.3). Intro cards: diagonal colour band slides in, name in bangers/anton huge + role small. Flash frames (white/colour) on beats. Final logo slam + shake.

## Audio (Mix)
Energetic synth at 140 bpm (cheerful preset faster) with kick every beat, riser before drop, slam on title.
