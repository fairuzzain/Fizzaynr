# 24. Kad flip reveal (recipe — not yet tested)

**Look:** Row/stack of cards face down; each card lifts, flips (x-scale → 0 → back with the face), revealing an image + title; cards fan out, the chosen one zooms. Tarot-like or collectible-card look with ornate borders drawn in code.

**Best for:** 'Pilih satu kad', personality/produk pick, rahsia/tips reveal, giveaway teaser.

## Flow prompts
Card faces 2x2 or 3x2 sheet: `…separate illustrated card artworks, ornate fantasy style, <subjects>, no text, no borders, thin white gutters, square 1:1.`
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Card = art + drawn ornate gold border + title plate. Flip: scale width by |cos(θ)|, swap to face when θ>90°, add shading by angle; lift = translate up + shadow grows. Background dark velvet (drawn radial gradient) + floating particles.

## Audio (Mix)
Whoosh on flip, shimmer ding on reveal, mystical pad (drone with higher base 110 Hz) at 0.1.
