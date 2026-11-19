# 10. Surat khabar / breaking news (recipe — not yet tested)

Look: (a) old newspaper: front page spins in from the centre (rotate 720° + scale up) and lands, headline in huge condensed serif, photo halftoned, columns of fake text lines; camera zooms to headline/photo; or (b) TV breaking-news: red "BREAKING NEWS" banner, lower-third ticker scrolling, live dot, anchor-less.
Best for: dramatic reveals, "viral" stories, announcements, parody news, product launch as news.

## Flow prompts
2x2 sheet of news photos: `A 2x2 grid of 4 separate news photographs with thin white gutters, photojournalism style, <scene>, no text, square 1:1.` Optional background: `Vertical 9:16 old yellowed newspaper paper texture, empty, no text` (or draw paper in code).

## Build (common.py)
- Newspaper page composed in code (1080x1600 page): masthead (typewriter/serif font), date line, headline (Anton, auto-fit width), photo with halftone (convert('L') → dot pattern or ordered dither), 3 columns of grey placeholder lines (never readable fake text), caption under photo.
- Spin-in: rotate + scale over 0.8 s with ease_out, `whoosh` + `slam` when it lands; then camera zoom to headline (crop-resize like polaroid camera).
- Breaking-news variant: red banner slides in, ticker text scrolls continuously (x = -speed·t mod width), headline lower-third.
- Audio: news sting (riser → slam), `tense` or `drone` bed, typing SFX on text reveals.
