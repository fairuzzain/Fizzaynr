---
name: theme
description: Decide colours, fonts and card design for an Edit Kit edit. For a client, always use that client's brand kit (colours, fonts, logo, cards, design rules). Otherwise ask for brand colours, fonts and vibe; if they skip, design the theme from the footage itself (theme, light and frame analysis) and write theme.json. Use at the start of every edit, or when the user says "pick colours for me", "what font", "match my brand", or uploads a logo.
---

# Motion Theme

Output: `theme.json` (CSS tokens + layout notes) that `fx/scripts/new_project.py --theme` applies.

## 0. Whose video is it? (always first)
Brand priority, highest wins. Never skip a level that exists:
1. **A client's brand kit.** If the video is for a client (or any brand that isn't the user's own channel), find and
   use THAT client's brand kit: an installed brand-kit skill named after the client, a saved
   `~/.claude/motion-kit/brands/<client>/brand.json` (see the kit's `brands/README.md`), or brand files the user gives (guidelines PDF, logo,
   colours, fonts, existing cards or templates). Use their colours, fonts, logo, card style, caption style and
   layout rules exactly, everywhere: key words, cards, lower thirds, end card. If no kit exists yet, ask for it
   before building, then save it as `~/.claude/motion-kit/brands/<client>/brand.json` so every later edit for them reuses it.
2. **Colours/fonts the user gives in the prompt.**
3. **Designed from the footage** (section 2), only when there is no brand at all.

Rules:
- One video = one brand. Never mix two clients, and never put a client's brand on the user's own channel (or the
  user's own channel look, like the Creator Explainer palette, on a client's video).
- Presets give motion and pacing only; the client's brand overrides every preset colour, font and card style.
- If a brand rule conflicts with a house rule (e.g. their captions are boxed, their font is not free), follow the
  brand and tell the user once.
- If unsure whether it's a client job, ask: "Is this for your own channel or for a client?"

## 1. Ask once (skip anything already known)

Ask in one message, all optional:
1. **Colours**: brand hex codes, a logo file, or "pick for me".
2. **Fonts**: names, or "pick for me". Free Google Fonts only for anything shared publicly.
3. **Vibe**: clean/premium, bold/hype, playful, techy, luxury, industrial.

A logo file: sample its colours (Pillow `quantize`) and use its strongest saturated colour as the accent,
its darkest as the background (SaaS) or text-on-light colour.

## 2. If they skip: design from the footage

```bash
python3 scripts/analyze.py <clip> --style <style-id> --out theme.json
```
Style ids: saas, motion-explainer, vox, ali-abdaal, real-estate, construction, gadzhi, bold-impact, podcast, finance, talking-head.

It measures and decides:
- **Theme** (style → mood): luxury, tech, editorial, clean, bold, industrial.
- **Light**: bright footage → white text needs `.mk-scrim` and dark-glass cards; dark footage → bare text with glow.
  Warm light (wood, tungsten, sunset) vs cool light (office, daylight, screens).
- **Frame**: dominant colours → the accent is the candidate farthest in hue from them, so it pops; emptiest regions
  → where headlines go; busy backgrounds → text gets a card or pill.
- **Fonts**: always a pair, serif display + bold sans:

| Mood | Serif (lead words, titles) | Bold sans (key words, labels) |
|---|---|---|
| luxury / real estate | Playfair Display Italic | Inter Tight (free stand-in for Helvetica) |
| editorial / Vox | DM Serif Display | Inter Tight |
| clean / education | Instrument Serif | Poppins |
| bold / motivation / construction | Playfair Display 900 | Montserrat 900 Italic, Anton |
| tech / SaaS / finance | Instrument Serif | Inter Tight, JetBrains Mono for numbers |

Then sanity-check by eye on a real frame: accent readable on its background (≥ 3:1 for big text), text never on the face.

### Creator talking heads: the opposite-light rule
When a creator sits in a strongly lit room, the accent is the colour **opposite the room light** on the wheel, on a
neutral graphite stage:
- red / magenta room → ice cyan #3EE0FF on graphite #0B0D12 (about 9.7:1), warm white text #F5F2EA
- blue / teal room → warm amber #FFB547; green room → soft magenta #FF5FA2; neutral white room → one brand-like accent
- Gold / metallic only when the words literally say gold or "golden" (and on a hero object named that way).
- Never reuse another brand's or client's colours and fonts on someone's own channel. Their footage decides.
- Typography check: Inter Tight 900 at about -0.015em with .08em word-spacing for key words, Instrument Serif italic
  for leads, sentence-case sans labels. No wide-tracked uppercase mono labels: they read as "AI-made".

## 3. Show it before building

Put the palette (bg, text, accent, negative) and the font pair at the top of the storyboard so the user can change it.
Save the final choice in `theme.json` next to the project. For a client or any named brand, also save it to
`~/.claude/motion-kit/brands/<client>/brand.json` and reuse it for every edit for that brand.
