# 45. Retro desktop Windows 95 (recipe — not yet tested)

**Look:** Old-school desktop: teal background, grey 3D-bevel windows pop up with messages, mouse cursor moves and clicks, loading bars, error dialogs ('Duit tidak mencukupi. OK / Cancel'), start menu, pixel icons — all drawn generically (no Microsoft logos).

**Best for:** Humor, nostalgia, 'error dalam hidup' content, tech explainer lucu, meme bisnes.

## Flow prompts
Optional pixel icon sheet 4x4 (`…separate retro 1990s computer desktop icons, pixel style, no text…`). Everything else drawn.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Draw bevel windows: light/dark 2 px edges, blue gradient title bar with title text (poppins-regular small or mono), close button; windows pop with scale 0.9→1 and stack/offset; cursor = drawn arrow polygon moving along bezier paths, click = cursor press + button inverse; progress bar blocks fill. Use NEAREST upscale feel (render at 540x960 then upscale 2x NEAREST for pixel look).

## Audio (Mix)
Click sounds, error 'ding' (two short tones), startup-like chord (original synth), keyboard typing, lofi 0.2.
