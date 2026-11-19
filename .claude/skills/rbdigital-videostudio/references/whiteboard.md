# 5. Whiteboard doodle (recipe — not yet tested)

Look: white board / off-white paper, black line-art doodles that get "drawn" progressively, handwritten captions (Caveat/Marker) written stroke by stroke, a few colour accents (one marker colour), arrows linking ideas, camera slides to a new empty area of the board for each idea.
Best for: explaining concepts (takaful, how a product works), step-by-step, education.

## Flow prompts
ONE sheet, 4x4 doodles: `A sheet of 16 separate simple hand-drawn doodle illustrations in a 4x4 grid with wide white space between, black marker line art on pure white background, whiteboard explainer style, minimal shading, no text, no labels. Row 1: ...` Optional background: `Vertical 9:16 clean slightly textured whiteboard surface, soft light reflection, empty, no text`.

## Build (common.py)
- Cut doodles: white bg → threshold dark pixels (`gray<200`), connected components per grid cell (cells are known: 4x4), crop with padding; keep alpha = darkness (so lines only).
- "Draw-on" effect: reveal the doodle with a mask that grows along a sweep — cheap version: sort dark pixels by angle/distance from a start point or by a noisy scanline (x + 0.3·y + noise), reveal pixels with rank < k·N over 0.8–1.5 s; show a small marker/hand icon (drawn circle or pen shape) at the reveal front. Precompute rank map once per doodle.
- Handwriting text: reveal letters left→right with the same mask trick (rank = x), plus `scribble` SFX.
- World canvas 2–3 screens wide; camera pans to the next free area per scene (like polaroid CAM keyframes).
- Audio: `lofi` or `cheerful` at 0.3, scribble during drawing, pop when a colour fill appears.
