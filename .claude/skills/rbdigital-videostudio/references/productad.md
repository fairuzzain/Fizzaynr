# 39. Iklan produk / TikTok Shop (recipe — not yet tested)

**Look:** Product hero image with 360-ish rotation illusion (slight scale/tilt), feature callouts with lines, price tag slam (old price strike-through, new price), countdown 'Promo tamat dalam…', CTA button pulsing 'Beli sekarang'.

**Best for:** TikTok Shop, produk digital BCL.my, promo, affiliate.

## Flow prompts
Product shots 2x2: `…separate studio product photos of <product>, different angles, clean gradient background, soft reflections, no text…` (or the user's real product photos — better for accuracy).
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Hero: cut product (cut_sheet on solid bg) and float with subtle bob + shadow; background gradient drawn; callouts = dot + line + label pill growing; price: old price with animated strike line, new price slam (anton, yellow on red tag); CTA pill pulsing scale 1→1.06. Claims must match the real product.

## Audio (Mix)
Upbeat cheerful 0.3, cash ding on price, whoosh on callouts, slam on promo.
