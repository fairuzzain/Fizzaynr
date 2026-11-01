# Reference look: FOH Media "LIVEX 2026" recap reel

Source: thefohproductions reel (Oct 2026), 1276×720, 25 fps, 11.8 s, ~22 shots.

## What it is
A behind-the-scenes event recap: a media crew in black branded tees filming an expo. Real-looking
documentary footage, warm venue light, shallow depth of field, slight film grain, mild vignette.
No voice-over; one punchy music bed (~130 BPM feel) carries it. It loops: the last shot is the
first shot again.

## Rhythm
- Average shot ≈ 0.5–0.6 s (12–15 frames). Cuts land on beats and accents, mostly 1 beat, some
  2 beats; the hero moments get 2–3 beats.
- Energy never drops: every few cuts there is a "hit" (flash, negative, split, title).

## Transition / effect vocabulary (render.py names)
| Seen in the reference | render.py |
|---|---|
| Opener smeared by horizontal motion blur that snaps sharp | `blur_in` |
| Single white flash frame into a shot | `flash` |
| Milky white overexposed fade that clears over ~0.3 s | `wash` |
| Defocused frame racking into focus | `defocus_in` |
| Inverted (negative) B&W frame, then a grayscale punch-in close-up | `neg_flash` + `bw` + `zoom [1.1,1.15]` |
| Black card with small bold white "LIVEX 2026", centred | `title` |
| Same text while footage opens in a widening window from the left | `title_reveal` |
| Three vertical panels of different shots (triptych) | `split` `v3` (`stagger` pops them in) |
| Four strips / mosaic of crew shots | `split` `grid4` or `v4`, `h3` in 9:16 |
| Slow push-ins and drifting handheld moves inside each shot | `zoom`, `pan` |
| Motion blur out of the last shot | `blur_out` |
| Warm grade, contrast, vignette, grain | `grade` |

## Shot grammar (template for ~26 beats ≈ 12 s at 130 BPM; scale for longer reels)
1. **Hook** (beats 1–6): opener wide `blur_in` 2 → second angle 2 (zoom in) → close-up 2.
2. **Title** (on a strong beat): `title` 1 → `title_reveal` 2–3 over a wide crowd shot.
3. **Montage** (bulk): 1–2 beat cuts alternating wide / medium / close; `flash` on strong beats;
   one `neg_flash`+`bw` hero (2–3 beats); one `split v3 stagger` (2 beats); `wash` once to breathe;
   one `grid4`/`v4` (2 beats); `defocus_in` once.
4. **Outro**: `bw` close-up + `blur_out` (2 beats) → opener window again (2 beats, `blur_in`) for a
   seamless loop, or a `title` end card with the brand name / `logo`.

Rules: never the same clip window twice in a row; fx on at most ~40 % of shots; one split per ~8 s;
keep text only on the title cards (no captions); keep it under the music's length.
