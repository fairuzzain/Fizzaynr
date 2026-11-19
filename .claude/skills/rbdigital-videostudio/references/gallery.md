# 46. Galeri muzium (recipe — not yet tested)

**Look:** Artworks hang in gilded frames on a gallery wall; camera glides along the wall, stops at each frame with a small museum placard (title, year, 1-line description), spotlight cones, final wide shot of the hall.

**Best for:** Sejarah, koleksi/portfolio, 'evolusi' sesuatu, cerita keluarga, showcase karya.

## Flow prompts
Artworks 2 sheets 2x2 in a consistent painting style: `…separate classical oil paintings, <subjects>, rich textures, no text, no frames…` + background `Vertical 9:16 elegant museum gallery wall, warm spotlights, wooden floor, empty wall space, no paintings, no text`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
World = long wall (tile/extend the background horizontally by mirroring). Frames drawn: layered gold bevels + inner shadow; paintings inside. Placard: small off-white card with typewriter/serif text. Camera: horizontal pan with ease and slight zoom at each piece; spotlight = radial gradient overlay (ImageChops.add at low alpha).

## Audio (Mix)
Soft reverb-y ambient pad (drone base 110, low gain), footstep-ish soft thuds on moves, gentle piano-like plucks (lofi slow).
