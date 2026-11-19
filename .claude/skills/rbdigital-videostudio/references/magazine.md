# 47. Majalah cover / editorial (recipe — not yet tested)

**Look:** Magazine covers and editorial spreads: masthead title, cover lines appearing, barcode/price corner, page turns into inside spreads with pull quotes, big numbers, and photo cut-outs; glossy fashion/business feel.

**Best for:** Profil personaliti/agent terbaik, 'Top achiever', launch produk premium, kisah kejayaan.

## Flow prompts
2x2 sheet: `…separate editorial magazine photographs, studio lighting, <subjects>, clean backgrounds, vertical composition, no text…` (or the user's real photos).
Follow common.md sheet rules (no text in images, shared style line, sheet 1 as ingredient for sheet 2).

## Build (common.py)
Cover: photo full-bleed 9:16 crop, masthead huge (anton/bebas) behind subject's head if a cut-out is available (cut subject with cut_sheet if plain bg), cover lines slide in from sides, small elements (issue no., barcode drawn as random bars). Spread: two-column layout, pull quote in large serif-like font, drop cap. Page turn like storybook.

## Audio (Mix)
Fashion/editorial beat: cheerful synth faster (120 bpm) with kick, camera shutter on cover reveal, whoosh on page turns.
