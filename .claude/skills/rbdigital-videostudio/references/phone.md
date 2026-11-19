# 20. Skrin phone / Google search (recipe — not yet tested)

**Look:** Vertical phone UI drawn in code: search bar, text typed character by character, results list appears with shimmer, finger-tap ripple, scroll, notification banners dropping from top, screenshot zoom with red circle annotation.

**Best for:** Hook 'Aku Google benda ni…', review app/produk, demo AutoSocial/GetQuote, 'tanya AI' content.

## Flow prompts
Usually none (UI is drawn). Optional app screenshots the user uploads. Don't copy real brand logos — generic search UI with own colours.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Screen = full 1080x1920 as phone (status bar with time/battery, rounded search pill). Typing 12–15 chars/s with blinking caret; results = cards with title (poppins bold), url line (green/grey), snippet grey lines (placeholder bars, not real copied text). Tap: expanding circle alpha fade. Zoom: crop-resize onto a card + red marker circle drawn progressively (arc).

## Audio (Mix)
Typing clicks, tap tick, notif, whoosh on scroll; music lofi 0.25.
