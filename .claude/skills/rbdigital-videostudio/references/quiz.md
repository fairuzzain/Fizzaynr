# 17. Kuiz game show (recipe — not yet tested)

**Look:** Question card with number badge, 4 answer pills A/B/C/D slide in one by one, circular countdown timer (5→0) ticking, then correct answer flashes green (+ confetti), wrong ones dim red, running score; end card 'Berapa markah kau? Komen!'.

**Best for:** Engagement tinggi, edu content, trivia takaful/kewangan, fakta produk.

## Flow prompts
Optional icon/sticker sheet 4x4 for question images; background `Vertical 9:16 game show stage with spotlights and bokeh lights, empty center, no text`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Each question ≈ 8–10 s: question text (poppins bold, wraps in card) → options staggered 0.3 s → timer arc (PIL arc end angle) 5 s with tick per second → reveal: correct pill fills green + scale pulse, others fade 40%. Keep 3–5 questions. VO reads question, pauses for timer, then reveals.

## Audio (Mix)
Tick per second (short click), buzzer for wrong (low square), ding + applause-ish noise burst for correct, upbeat music 'cheerful' at 0.25, mute during the countdown except ticks.
