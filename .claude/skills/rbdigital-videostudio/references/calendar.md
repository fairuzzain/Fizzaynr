# 49. Kalendar koyak (hari demi hari) (recipe — not yet tested)

**Look:** Tear-off desk calendar: big date number, day name, and a short note or icon per page; pages rip off and fly away (rotate + fall), days speed up in a montage, then stop on a key date with a stamp/circle.

**Best for:** Journey 30 hari, countdown event/promo, 'setiap hari kau lengah…', kisah kemajuan, deadline.

## Flow prompts
Optional icon sheet 4x4 for the notes. Background: `Vertical 9:16 wooden desk surface with soft window light, empty center, no text`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Calendar drawn in code: binding rings on top, stack of pages (slight offset shadows), page = white card with red header (month), huge date number (anton), day name, note text (caveat) + icon. Tear: page rotates around top-left with gravity fall + spin, fading; montage speeds up by shrinking per-page duration (0.8 s → 0.12 s). Final date: red marker circle draw-on.

## Audio (Mix)
Paper rip (noise burst with envelope), ticking clock accelerating during montage, ding/boom on the final date; music tense or cheerful depending on topic.
