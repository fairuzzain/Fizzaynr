# Prompt templates (fill <...>; STYLE string from SKILL.md §1)

## Background (one per scene, 9:16 = 1536x2688, 16:9 = 2688x1536)
```
<scene description>, no people. <STYLE>, <palette for the mood>, vertical composition, no text, no letters.
```
16:9: replace "vertical composition" with "wide horizontal 16:9 composition, open empty floor space in the center foreground".

## Character sheet (3 poses, 2560x1440, always green)
```
Character sheet with 3 poses in a row of the same <character description>. Pose 1: <...>. Pose 2: <...>. Pose 3: <...>.
Full body, all poses same scale, evenly spaced with wide gaps, not touching. <STYLE>, no text.
Isolated on a plain flat solid bright green (#00FF00) background, no shadows on the background, no ground, nothing else.
```
No green clothes or green props on the character.

## FG border sheet (2 borders, 2560x1440) — key colour from the FG key column
Green key (no plants or green items):
```
Two horizontal <style> borders stacked with a wide gap between them, each spanning the full width.
Top: <flowers / objects / hearts / stars ...>. Bottom: <...>. Strong saturated colours, <STYLE>.
Isolated on a plain flat solid bright green (#00FF00) background, no shadows on the background, nothing else.
```
Magenta key (leaves, grass, bushes, trees allowed; nothing pink, magenta or purple):
```
Two horizontal <style> borders stacked with a wide gap between them, each spanning the full width.
Top: <leaves, grass, flowers in red/orange/yellow/white ...>. Bottom: <...>. Strong saturated colours, <STYLE>.
Isolated on a plain flat solid bright magenta (#FF00FF) background, no shadows on the background, nothing else.
No pink, magenta or purple anywhere on the borders.
```

## Character consistency
Define once and reuse verbatim in every sheet, e.g.
"the same young Malay woman wearing a soft pink hijab and pastel pink long-sleeve baju kurung top" (pink = keep her on a green sheet).

## draft.json template (timing is filled by plan_scenes.py)
```json
{"target": 15, "size": [720, 1280], "style": "paper",
 "caption_look": {"preset": "kertas", "color": [59, 42, 31]},
 "fg_w": 1.55, "fg_drop": 0.18,
 "scenes": [
  {"bg": "b1.png", "fg": "f1_1_cut.png", "chars": [{"file": "p1_cut.png", "x": 0.5, "h": 0.54}],
   "caption": "Bermula dari dapur rumah", "cam": "push"},
  {"bg": "b2.png", "fg": "f1_2_cut.png", "chars": [{"file": "p2_cut.png", "x": 0.45, "h": 0.54, "idle": "bounce"}],
   "caption": "Niaga di gerai tepi jalan", "cam": "pan"},
  {"bg": "b3.png", "fg": "f1_1_cut.png", "chars": [{"file": "p3_cut.png", "x": 0.55, "h": 0.54}],
   "caption": "Kini, kedai sendiri!", "cam": "reveal", "particles": "confetti"}],
 "tagline": {"lines": ["Mulakan langkah anda", "hari ini."], "cta_word": 3, "y": 0.76}}
```

## Worked example (15 s "Perjalanan Usahawan Kecil")
Kitchen at night → roadside stall → own bakery at sunset. FG: paper leaves + flowers (magenta key), boxes + flowers.
Captions: "Bermula dari dapur rumah", "Niaga di gerai tepi jalan", "Kini, kedai sendiri!"; tagline "Mulakan langkah anda / hari ini."
Music mood: hopeful. Caption preset: kertas.
