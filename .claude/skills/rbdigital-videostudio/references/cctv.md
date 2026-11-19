# 37. CCTV / found footage (recipe — not yet tested)

**Look:** Grainy CCTV frames (grayscale/green), camera labels 'CAM 03 – LORONG', REC ● blinking, timestamp ticking, occasional frame skips and signal loss, split multi-cam grid, zoom-enhance on a suspicious area.

**Best for:** Horror, misteri, 'kejadian pelik', security awareness.

## Flow prompts
2 sheets 2x2: `…separate security camera footage frames, high angle wide lens, grainy low light, black and white, <scenes>, no text, no timestamp…`.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Convert to L + slight green tint, heavy grain, reduce frame rate to 8 fps holds, barrel-ish vignette. OSD in typewriter font. Multi-cam 2x2 grid moments. Enhance: crop-zoom with pixelation (downscale NEAREST) that sharpens over 1 s. Signal loss: full static + 'NO SIGNAL'. Subtle 'figure appears' = diff between two frames Flow made (before/after).

## Audio (Mix)
Electrical hum 60 Hz low, static bursts, boom on reveal, silence otherwise.
