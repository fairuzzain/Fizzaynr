# 42. Thread / post sosial (tweet cards) (recipe — not yet tested)

**Look:** Social post cards (avatar, name, handle, text, like/reply counts) appear one after another like a thread, counts tick up, replies nest, a hot reply gets highlighted; generic UI (not a real brand).

**Best for:** Repurpose Threads/X content (Rantai), hot takes, Q&A, 'komen netizen' reactions.

## Flow prompts
Optional avatar sheet 2x2; everything else drawn.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Card: dark or light theme rounded rect, avatar circle, bold name + grey handle, body text wrap (poppins 44), action row with icons drawn simply (heart, reply, repost) and animated counts. Thread line connecting avatars. Scroll up as cards stack (like fakechat). Use the user's own posts or clearly fictional handles.

## Audio (Mix)
Notif on new card, pop on like, typing clicks, lofi 0.25.
