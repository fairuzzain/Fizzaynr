# 19. Buku cerita kanak-kanak (recipe — not yet tested)

**Look:** Open book on a table; each spread shows a soft watercolour illustration on one page and text on the other appearing word by word (read-along highlight); page turn animation (page scales on x with shading) between spreads; sparkles.

**Best for:** Cerita moral, kandungan budak (3M), bedtime story, kisah nabi/teladan (tone respectful).

## Flow prompts
2 sheets 2x2: `…separate children's storybook illustrations, soft watercolor, warm cozy colors, cute rounded characters, <scenes>, same characters described identically, no text, thin white gutters, square 1:1.`
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Book drawn in code: two cream pages with centre crease shadow, slight perspective not needed. Illustration on left page (rounded corners), text right page (caveat/comicneue 54, dark brown) with current word highlighted yellow (use VO phrase timings, split by word length). Page turn: right page width shrinks to 0 with darkening, then new left page grows — 0.6 s. Keep language simple for 4–6 year olds.

## Audio (Mix)
Soft 'lofi'/cheerful at 0.2, page flip = paper noise sweep, sparkle = high ding, gentle narrator VO ([cheerful] [calm] [whispers]).
