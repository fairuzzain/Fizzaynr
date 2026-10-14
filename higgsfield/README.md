# Higgsfield prompt pack

Seven live-action slots (S05, S06, S07, S13, S18, S22, S24). Generate them in Higgsfield, then drop each clip into
`plates/<SHOT>.mp4` and run `npm run assemble`. Each clip is cropped to 1920×1080, conformed to 24 fps and trimmed
to its slot. If a take is short, the last frame is held.

The character and location are original. They are not based on the reference's cast or set.

## 1. Lock the character and location first

Generate these once, pick the best take of each, and reuse them as the reference image on every shot.

### Character sheet: "Theo"
```
Character turnaround sheet, photoreal, neutral studio grey background, 16:9.
Theo: man in his late 30s, warm brown skin, close-cropped black hair with grey at the temples,
short salt-and-pepper beard, round tortoiseshell glasses, rust-orange cotton chore jacket over a
heather-grey crew-neck tee, dark indigo selvedge jeans rolled once, tan leather work boots,
thin silver ring on right index finger, simple black digital watch.
Panels: front full body, 3/4 left, profile right, back, plus close-ups of face (neutral, laughing,
surprised) and of both hands. Soft even key light, true-to-life skin texture, no text, no logos.
```

### Location sheet: the studio
```
Location reference sheet, photoreal, 16:9, four panels of the same space.
A converted brick warehouse studio used by a freelance video editor who rides bikes:
long oak workbench under tall steel-framed windows, morning sun raking in from camera left,
birch-plywood shelving with lenses and helmets, a matte-sage road bike hanging on a wall hook,
a floor pump and a toolbox under the bench, a large fiddle-leaf fig in a terracotta pot,
grey open laptop and an SD card reader on the bench, enamel mug, dust in the light beams.
Panels: wide establishing from the door, reverse wide toward the windows, medium on the bench,
detail of the bench surface. Warm natural palette with orange accents. No text, no logos.
```

Global settings for every shot: 16:9, 24 fps, natural handheld micro-motion unless the shot says locked off,
35 mm film look, soft contrast, warm highlights, no on-screen text, no brand logos on the laptop.

## 2. Shots

The frame counts are exact slot lengths at 24 fps. Generate a little longer, then trim with `plates/<SHOT>.json` `{"offset": N}`.

| Slot | Abs. frames | Length | Framing / move | Prompt |
|---|---|---|---|---|
| **S05** | 257–287 | 30f · 1.25 s | ECU, top-down, locked off | Overhead extreme close-up of an oak bench: Theo's hand (silver ring, chore-jacket cuff) slides an SD card into a small aluminium card reader cabled to a grey laptop's side port; a status LED blinks orange. Shallow depth of field. |
| **S06** | 287–364 | 77f · 3.21 s | WIDE, then a fast push-in to a CU of the face (whip-in over f14–24) | Theo sits at the long oak bench in the sunlit studio, laptop open, and starts speaking toward it. The camera holds wide, then pushes fast into a close-up of his face as he talks, relaxed and focused. Glasses catch the window light. |
| **S07** | 364–436 | 72f · 3.00 s | MS, slight low angle; tilt down as he stands | Medium shot from the side of the bench. Theo finishes his sentence, nods once, and pushes back on his stool to stand; the camera tilts down to follow his torso as he rises out of frame top. |
| **S13** | 719–807 | 88f · 3.67 s | MCU on hands and bench, slow slider move left to right | While he waits, Theo pumps up the front tyre of the sage road bike with a floor pump beside the bench. Rhythmic strokes, sun beams, dust in the air. Slow lateral slider move. |
| **S18** | 1134–1181 | 47f · 1.96 s | CU, shallow focus, near-static | Close-up of the floor pump's pressure gauge as the needle climbs, then Theo's thumb and fingers squeeze the tyre to check it. Background softly out of focus with the orange jacket. |
| **S22** | 1560–1691 | 131f · 5.46 s | MS frontal over the laptop, slow push | Theo sits back down with the enamel mug, watches the laptop screen, breaks into a delighted laugh, pushes his glasses up and points at the screen, saying "No way… that's the take." Natural, unforced reaction. |
| **S24** | 1752–1812 | 60f · 2.50 s | WIDE of the studio, slow pull-back | Wide establishing shot of the studio. Theo lifts the sage road bike off the wall hook, clips on a helmet and wheels it toward the door; the laptop on the bench still glows. Leave clean space in the centre for the tagline super. |

Captions for S06, S07 and S22 and the S24 super are drawn by the renderer (`out/captions.mov`) and composited over your
plates, so leave the plates clean. To change the wording or timing, edit `props.captions` and `props.super` in `timeline/timeline.json`.

## 3. Consistency checklist
- Use the same character reference image and the same location reference image on all seven shots.
- Keep the wardrobe identical: the jacket, glasses and ring are the continuity anchors.
- Keep the light direction (sun from camera left) and the time of day (morning) constant.
- Keep the laptop lid logo-free, and keep screen content out of focus so the UI shots carry the interface.
