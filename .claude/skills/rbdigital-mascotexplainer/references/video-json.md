# video.json — full schema

`build.py` turns this file into a HyperFrames project. Times inside a scene are **seconds from the scene start**.
Text fields accept `*italic serif accent*` (red Instrument Serif italic) and `**red bold**`.

```json
{
  "title": "promo 6 skill",            // also seeds the music
  "format": "16x9",                    // "16x9" (1920x1080, content left, mascot right) or "9x16" (1080x1920, content top, mascot bottom-right)
  "theme": "editorial",                // editorial | neon | pastel | notebook | techgrid | sunset | corporate | comic | calm | bold (templates/themes.json)
  "theme_override": {"accent": "#FF6A00"},  // optional: change any theme variable (colours, radius, shadow...)
  "enter": "slam",                     // optional: override the theme's entry motion (move blur pop wipe scan rise slide slam soft)
  "brand": "@handlekau",               // top-right label of every scene; "" or omit = hidden
  "accent": "#C8102E",                 // optional shortcut for theme_override.accent
  "mascot": "najib",                   // "generic" (built-in SVG host), a pack name in assets/mascot/, or a path to a pack folder
  "mascot_colors": {"skin":"#E8B48A","hair":"#23201F","shirt":"#26304F"},   // generic mascot only
  "timing": "timing.json",             // from vo_prep.py: scene start/end follow the VO pauses
  "cues": "cues.json",                 // from vo_prep.py: Rhubarb mouth cues
  "vo_offset": 0,                      // seconds the VO starts after 0 (keep 0 unless audio.py --vo-offset is used)
  "outro": 0.8,                        // seconds after the last scene
  "scenes": [ ... ]
}
```

## Scene

```json
{
  "bg": "main",                        // main (default) | hook (opening question) | alt (contrast beat) | accent (accent-colour full bleed); old names cream/brown/dark still work
  "dur": 4.5,                          // only used when there is no timing.json
  "top": "// skill 01 · video studio", // small mono label top-left
  "lead": [[0, "Satu, *Video Studio.*"], [2.2, "Bagi topik, pilih *110 style.*"]],   // one string, or [time, text] list (lead changes inside the scene)
  "title": ["VIDEO", "*STUDIO*"],      // Anton words; *word* = red. Omit for hook/CTA scenes
  "badge": "01",                       // black number box after the title
  "visual": { "type": "...", "delay": 0, ... },   // one main visual (below); "delay" = seconds before it appears
  "pill": {"num": "110", "text": "style", "at": 1.2},      // black pill bottom-left; text may use *x* for yellow Anton
  "progress": {"text": "Pasang sekali", "at": 2.0},         // thin progress bar under the visual
  "sticker": {"small": "Tak reti edit?", "big": "PENING.", "at": 1.4},   // torn-paper slam (hook)
  "pose": [[0, "point"], [2.2, "phone"]],                    // mascot pose(s); one string or [time, pose] list
  "transition": "burst",               // optional: transition INTO this scene (cut flash glitch circle push page scan blinds burst veil); default from the theme
  "deco": ["sun", "dots"]              // optional: decorations for this scene (brackets scanlines blobs sparkles doodles code cursor sun dots burst speed leaves caution); default from the theme
}
```

Poses: the built-in `generic` host has `think`, `point`, `phone`, `thumbs`, `base`. A PNG pack defines its own pose names
(picked per topic from the pose library in mascot-pack.md §2a: wave, explain, shocked, laptop, money, clipboard, magnify,
celebrate...). Change pose on sentence boundaries, not mid-word, and match the pose to what is said.

mascot.json may carry `"sink"` (0–0.4): the fraction of the pose height hidden below the frame edge so the mascot is cut off
by the frame; build.py picks it automatically if missing.

## Visual types

| type | keys | use for |
|---|---|---|
| `timeline` | `title`, `label` | editor/problem mockup (hook) |
| `numcards` | `items: [["01","Video Studio"],...]`, `cols` (3), `stagger` | list of products/steps/audiences as numbered cards |
| `tiles` | `items: ["Komik",...]` (colours from the theme palette) or `[["Komik","#F5D94E","#111"],...]` (text, bg, fg), `cols` (4), `highlight: [[t, index],...]` | menu of styles/options; highlight = outline + click |
| `phone` | `caption`, `big`, `big_at`, `chips: [...]` | a short video / app on a phone + feature chips |
| `list` | `items: [...]`, `side: ["5 TIPS","JIMAT"]`, `step` | numbered list that highlights row by row |
| `landscape` | `tree` (true) | parallax scene (layers drift) |
| `filmstrip` | `frames: ["BABAK 1",...]` | story / scenes / series |
| `prompt` | `file`, `label`, `lines: [...]`, `cps` (26), `copy_at` | prompt / code typed in, Copy button turns green |
| `window` | `title`, `label`, `rows: [["Akaun","Najib"],...]` | any app screen (generic, no real logos) |
| `checklist` | `items: [[t, "text"],...]` | steps ticked on the VO word |
| `price` | `tag`, `old`, `new`, `new_at` | normal price → strike → launch price |
| `comment` | `keyword`, `handle`, `dm`, `at` | CTA: avatar comment box types the keyword, heart, "→ terus ke DM" |
| `text` | `big: ["JOM","*MULA*"]` | one huge statement (no title needed) |

## Layout rules (already in the CSS — keep content inside them)

- **16:9**: content column x 190–990; mascot owns x ≥ 1150. Lead ≤ 1 line (~38 characters), title ≤ 2 words + badge.
- **9:16**: top 0–240 px empty (Reels/TikTok UI); lead from y 310 (≤ 2 short lines), title y 440, visual y 620–1150; the mascot owns the bottom-right from y ~1200 / x ~480, so cards below y 1150 stay ≤ 560 px wide (pill, sticker).
- Example numbers in a mockup that are not real get the word "contoh".
- No real brand logos; mockups use generic names in text.
