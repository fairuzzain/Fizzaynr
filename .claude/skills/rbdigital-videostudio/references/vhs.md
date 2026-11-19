# 13. VHS retro 90an (recipe — not yet tested)

**Look:** Scanlines, colour bleed (RGB split 2–4 px), tracking noise bands rolling down, rounded-corner CRT vignette, 'PLAY ▶' + date/time OSD in VCR font (typewriter/oswald), occasional tape wobble (row-wise sine shift) and pause/rewind bars.

**Best for:** Nostalgia, kisah lama, horror 'rakaman jumpa', throwback content.

## Flow prompts
2x2 sheet: `A 2x2 grid of 4 separate frames from a 1990s home video camcorder, <scenes>, soft focus, washed-out colors, no text, no timestamp, thin white gutters, square 1:1.`
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Crop 4 frames, fill 9:16 with Ken Burns. Per frame FX in numpy: downscale→upscale (0.5x) for softness, RGB split, horizontal sine wobble `np.roll` per row band, noise band (bright stripe) moving down, scanlines (darken every 3rd row 15%), chroma desaturate 0.8. OSD: 'PLAY ▶' top-left blinking, 'JAN 12 1996 / 11:42 PM' bottom-left ticking. Scene changes = 0.2 s static + rewind lines.

## Audio (Mix)
Tape hiss bed (lowpassed noise 0.05), mechanical click on PLAY, static bursts on cuts; music optional muffled 'lofi' at 0.15.
