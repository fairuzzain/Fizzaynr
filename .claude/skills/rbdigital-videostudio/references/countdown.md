# 8. Countdown / Top 5 (recipe — not yet tested)

Look: bold title card ("5 KESILAPAN ..."), then #5 → #1: giant number slams in (Anton, accent colour, stroke), item image card slides in, item name + one-line reason, progress ladder at the side showing which rank is active, #1 gets a bigger reveal (riser + flash + shake).
Best for: rankings, "5 tips", "Top 5 tempat", mistakes to avoid, product picks.

## Flow prompts
ONE sheet 2x2 or 3x2 of item images (or a 4x4 sticker sheet if icons suit better):
`A 3x2 grid of 6 separate <style: realistic product photos | flat illustrations> with thin white gutters, each centred on a plain background, no text, square 1:1. Image 1: ... (#5) ...` plus one background: `Vertical 9:16 dark bold background with subtle diagonal stripes and light rays, empty, no text`.

## Build (common.py)
- Per rank segment (≈6–8 s): number slam at start (scale 2.2→1, 0.2 s, shake 0.3 s, slam SFX), image card (rounded corners, white border, shadow) slides in from right with slight rotation, name caption word-pops, reason in smaller text; number shrinks to the side ladder when segment ends.
- Side ladder: 5 small circles x=990, y 600–1300, active one highlighted and scaled.
- #1: `riser` 1.5 s before, then flash + boom-lite + confetti (small coloured rects falling, seeded).
- Audio: `cheerful` or energetic, slam per number, whoosh per card, ding when reason appears.
