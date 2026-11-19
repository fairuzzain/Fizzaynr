# Mascot pack — any character the user wants

The user describes (or uploads a photo of) the mascot they want; Claude gives **2 image prompts**; the user generates both
images (ChatGPT / Gemini / Flow / any image tool) and uploads them; Claude turns them into a pack with `make_pack.py`.
A pack is a folder: `mascot.json` + transparent PNGs. It can be reused for every future video.

## 1. Character description (write it once, reuse it in both prompts)

From their words or photo: who/what (person, animal, object), age/look, hair, face details (glasses, moustache, hijab...),
clothes and colours, art style. Example: `a friendly Malay man in his 30s, short black hair swept up, gold round glasses,
thin moustache and short goatee, navy crew-neck t-shirt, flat 2D cartoon with thick dark outlines and soft cel shading`.
Never a copyrighted character or a real celebrity.

## 2. The prompts (give them in code blocks, with the note on clean cut-outs)

### 2a. Pick the poses for THIS topic (6–8, two sheets of 4)

Don't reuse the same 4 poses for every video. Pick 6–8 poses that fit the script, from this library (or invent one that
fits a scene), and always keep `think` (hook) and `thumbs` (CTA). Sheet 1 = the 4 used most, sheet 2 = the rest.

| pose name | prompt words | fits |
|---|---|---|
| think | thinking, one hand touching the chin | hook, question |
| point | pointing to the left side with the index finger | explaining, "tengok ni" |
| phone | holding a smartphone up in one hand, other hand open | apps, "buka", online |
| thumbs | both thumbs up, happy | done, CTA, price |
| wave | waving hello with one hand raised | opening, greeting |
| explain | both hands open in front, palms up, explaining | overview, "senang je" |
| shocked | both hands on the cheeks, surprised | problem, warning, "jangan" |
| laptop | typing on a small laptop held in front | tutorial, coding, setup |
| money | holding a gold coin or a small stack of cash | price, savings, earnings |
| clipboard | holding a clipboard with a checklist | steps, plan, checklist |
| magnify | holding a magnifying glass up to one eye | research, check, compare |
| heart | holding a small red heart in both hands | thanks, care, family |
| sign | holding a blank rectangular sign board up with both hands | announcement (Claude draws the text) |
| celebrate | both arms raised up, cheering | success, launch, "siap" |
| shrug | shrugging, palms up, confused | myth, "tak tahu?" |
| facepalm | one hand on the forehead, embarrassed | common mistake |
| point-up | pointing up with one finger, "idea" | tip, key point |
| megaphone | holding a megaphone | promo, offer |

Write the chosen names in the plan and use exactly these names in `video.json` `pose`.

### 2b. Pose sheet prompt (one per sheet, wide 16:9 image, ask for 2K / high resolution)
```
Character sheet of ONE cartoon character shown 4 times side by side in a row, identical size, identical camera distance,
waist-up, facing the viewer, clear empty space between the figures (they must not touch or overlap):
(1) <POSE 1 words>; (2) <POSE 2 words>; (3) <POSE 3 words>; (4) <POSE 4 words>.
IMPORTANT FRAMING: every figure is cut off by the bottom edge of the image at the waist, the body continues below the
frame, no legs, no feet, no rounded bottom of the body visible; the heads sit at the same height. Hands and props stay
inside the image. Mouth gently CLOSED and neutral in all 4.
<CHARACTER DESCRIPTION>. Plain solid flat pure green #00FF00 background, no shadows on the background, no floor, no text,
no logos, no extra objects. 2K, high resolution.
```
Sheet 2 = same prompt with the next 4 poses, and tell them to give sheet 1 as a reference image so the character matches.

### 2c. Mouth chart prompt (square image). Pick the version for the character.

**Human / realistic face** (people, humanlike characters):
```
Lip-sync mouth chart for the SAME cartoon character: a 3x3 grid of 9 mouths only (lips, inside of the mouth, plus the
moustache/beard if the character has one), all the same size, centred in their cells, front view, no nose, no eyes, no face
outline. Row 1: lips closed pressed together; slightly open with teeth together; open showing the top teeth.
Row 2: wide open "aah" with tongue visible; rounded medium "oh"; small puckered "oo".
Row 3: top teeth resting on the lower lip "f"; open with the tongue tip touching the top teeth "l"; relaxed closed gentle smile.
<SAME CHARACTER DESCRIPTION: lip colour, skin tone, facial hair>. Same line thickness and style as the character.
Plain solid flat pure green #00FF00 background, no labels, no text, no grid lines.
```

**Cute / animal / mascot / object characters** (cat, butterfly, robot, fruit, chibi...): never human lips or rows of teeth.
Simple cartoon mouths in the character's own style, each drawn on a small soft patch of the face colour so it covers the
mouth drawn in the poses:
```
Lip-sync mouth chart for the SAME cute cartoon character: a 3x3 grid of 9 simple cartoon mouths, all the same size, centred
in their cells, each drawn on a small soft oval patch of the face colour <FACE COLOUR, e.g. white>, front view, no nose,
no eyes. Style: the same thick dark outline as the character, very simple, cute, NO realistic lips, NO individual teeth,
NO lipstick. Row 1: small closed curved line; small slightly open mouth (thin dark gap); small open mouth with a tiny pink
tongue. Row 2: big open round mouth "aah" with a pink tongue; medium round "oh"; tiny round "oo".
Row 3: small mouth with one tiny tooth bump resting on the lower edge "f"; open mouth with the tongue tip up "l";
gentle closed smile (same as the poses). <CHARACTER DESCRIPTION: muzzle shape, e.g. cat "w" mouth / beak / simple line>.
Plain solid flat pure green #00FF00 background, no labels, no text, no grid lines.
```
Use the muzzle-style anchoring for this version (§3): width = the patch width, and run `make_pack.py anchor ... --no-patch`.

Add one line: "Background hijau rata supaya senang potong. Kalau watak ada benda hijau, tukar #00FF00 kepada magenta #FF00FF."

## 3. Build the pack (after upload)

```bash
python <skill>/scripts/make_pack.py cut poses1.png,poses2.png mouths.png --out mascot/<name> --poses think,point,phone,thumbs/wave,explain,shocked,celebrate
# one sheet: cut poses.png mouths.png --poses think,point,phone,thumbs ; sheets are matched to the scale of sheet 1
```
- It keys the background (reads the colour from the border), splits the poses on the gaps, puts every pose on one canvas size
  (same scale, head centred, bottom aligned), cuts the 9 mouths in A B C / D E F / G H X order, writes `mascot.json`
  with guessed anchors, and `anchor_<pose>.png` (pose on a pixel grid, labels every 100 px).
- **Look at each `anchor_<pose>.png`** and read the centre of the drawn mouth (x, y) and its width. Then:
```bash
python <skill>/scripts/make_pack.py anchor mascot/<name> think=512,388,120 point=505,392,118 phone=... thumbs=...
python <skill>/scripts/mascot_check.py mascot/<name> --out mascot_preview.png
```
- `anchor` also samples the skin colour beside the mouth; build.py paints a soft patch of it over the drawn mouth so only
  the lip-sync mouth shows. Look at the preview: every mouth must sit on the face in every pose and match its size.
  Nudge x/y/width and re-run until right. Show the user the preview sheet.
- **Muzzle-style mouths** (animals, or any mouth sprite that is a whole patch with its own background shape, e.g. a white cat
  muzzle with the nose): anchor = centre of that muzzle in the pose, width = muzzle width (+5%), and clear the skin patch
  (`"patch": {}` in mascot.json) — the sprite itself covers the drawn mouth. Tip to find it: the largest near-white blob in
  the top 45% of the pose image.
- **Sitting on the frame edge:** build.py bottom-aligns the pose to the frame and pushes it down by `"sink"` (fraction of the
  pose height hidden below the edge) so the mascot looks cut off by the frame, never floating. Auto: 0.04 when the figure is
  already cut flat at the waist, 0.16 when its bottom is rounded/full. Override in mascot.json (e.g. `"sink": 0.22`) if the
  bottom of the body or a gap still shows in the snapshot.
- Low-res images (under ~800 px tall per pose) look soft at 720 px in the video: ask for a 2K / high-resolution image.
- Wrong split (figures touching): ask for the poses again with more space, or cut them by hand into 4 PNGs and edit
  `mascot.json` (format: docstring of `mascot_check.py`).
- Mouth sheet in a different order: rename the `mouth_*.png` files to match the shapes table below.

## 4. Keep it

Point `"mascot"` in video.json at the pack folder. To reuse it in every video, copy it into `<skill>/assets/mascot/<name>/`
and (Claude Code / their own copy) repackage the skill with the same name. The skill uses a pack in `assets/mascot/` (other than
`generic`) as the default.

## Mouth shapes (Rhubarb)

| shape | sound | looks like |
|---|---|---|
| A | M B P | lips closed |
| B | K S T, "ee" | slightly open, teeth together |
| C | "e", "a" (short) | open, teeth visible |
| D | "aa" | wide open, tongue |
| E | "o", "er" | rounded medium |
| F | "u", "w", "oo" | small puckered |
| G | F V | upper teeth on lower lip |
| H | L | open, tongue up behind teeth |
| X | rest / silence | closed, relaxed (slight smile) |
