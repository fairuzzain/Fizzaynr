# 40. Testimonial / review card (recipe — not yet tested)

**Look:** Review cards slide in: star rating fills one by one, quote text with big quotation marks, reviewer name/initial avatar, badges ('Pelanggan sebenar'); stack of cards scrolling; final rating summary.

**Best for:** Social proof takaful/produk/kelas, ads retargeting.

## Flow prompts
None (cards drawn); optional avatar illustrations 2x2. Use only real testimonials the user provides (with permission); never invent reviews.
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Card: white rounded rect with shadow on soft gradient; stars drawn polygons filling yellow sequentially; quote in poppins regular, key phrase bold/highlight; cards enter from bottom with ease_back, older cards scale down behind (stack).

## Audio (Mix)
Soft pops, ding per star, warm lofi 0.25.
