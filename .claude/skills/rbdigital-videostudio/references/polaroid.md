# 3. Polaroid / papan siasatan (TESTED — "Rumah Sewa RM300")

Look: dark cork board; each photo becomes a polaroid pinned with a red thumbtack while a virtual camera glides to it; red string grows pin to pin; handwritten notes (Permanent Marker) on torn paper pinned below photos; film grain, vignette, flicker; camera-flash on key photos; RGB glitch + static on scares; pull back to show the whole board; final photo zoom + typewriter line, fade to black.
Best for: horror, mystery, true crime, "kisah benar", timelines, investigations.

## Flow prompts
- Background: `Vertical 9:16 close-up of an old cork board texture, dim moody lighting, dark vignette at edges, a few empty pin holes and faint paper scraps, top-down flat lay, no photos, no text`
- 2 sheets: `A 2x2 grid of 4 separate vintage instant film photographs with thin white gutters between them, no borders, no text, square 1:1. All photos: 1990s disposable camera flash photography, heavy film grain, faded colors, slight blur, dark eerie atmosphere, same <place>. Photo 1 (top-left): ... ` (sheet 1 as ingredient for sheet 2). Keep scary content subtle, not gory.

## Build (copy `examples/polaroid/pol.py` + `audio.py`)
- World board 1728x3072 (bg upscaled), polaroids 440 px photo (500x590 frame) in 2 columns x 4 rows at x≈480/1240, y≈480/1190/1900/2600; notes hang just below each photo (`_NB`), width 400, font 46.
- Camera keyframes `CAM (t, cx, cy, view_width)` with log-zoom interpolation, **clamped to board** (else black bars). Focus view width ≈ 880; overview = full board width; creepy zoom to 460–560.
- Base states cache: finished items baked into the board, only animating items drawn per frame → ~0.08 s/frame, 2 chunks.
- Audio: drone + wind bed, shutter on each pin, paper on notes, knocks, heartbeat during build-up, boom on scares, static on glitches.
