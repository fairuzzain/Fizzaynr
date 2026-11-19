# 43. Infinite zoom (recipe — not yet tested)

**Look:** Endless zoom-in: each image is nested inside the previous one (a window, a phone screen, an eye, a painting), the camera keeps pushing in and the next scene emerges seamlessly; text captions float over each layer.

**Best for:** Hook yang buat orang tengok sampai habis, 'dari besar ke kecil' (bandar → rumah → bilik → skrin), kisah berlapis, reveal produk.

## Flow prompts
Ask for images with a clearly framed centre region: `A 2x2 grid of 4 separate square images, <style>, each with a central framed area (window / screen / picture frame) occupying the middle third, no text, thin white gutters, square 1:1. Image 1: … Image 2 (what is seen inside image 1's frame): …` — sheet 1 as ingredient for sheet 2 for style match.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Nest: scale image k+1 to fit the frame region of image k (measure the frame box by viewing the image, per image), composite the chain into a stack. Camera zoom is exponential: scale = r^(t/T) where r = ratio between layers; at each layer boundary switch the base to keep resolution (render the current layer + next layer only). Soft-edge (feather) the inner image's border so seams disappear. Crop centre to 9:16.

## Audio (Mix)
Continuous whoosh/riser layers, ambient lofi or drone 0.25, soft boom at the final reveal.
