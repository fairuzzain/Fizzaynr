# The style master: reference images in 3D and 2D

Scope: every film whose style's family is 3D or 2D (`styles.md`). Live action makes its references without a master
(`sheet-realism.md`, `sheet-stylized.md`, `location.md`). Every "<the style's …>" below is taken from the film's style file
(`scripts/styles/<template>.md`): its style block, its light words and its image words.

Separate images of separate characters drift apart in look and scale. So a 3D or 2D film first makes one picture of its world, the
style master: the main place with its characters and props in it, in the style's look. Every other reference image is made from
it, with it attached, and copies its look, its designs and their sizes against each other.

## The style block in every image

The style is written out in every image prompt, never only named. An image that only named the look, or pointed at the attached image's
look in a short phrase, came out in a style of its own: a pixel master gave plates on a finer grid than its
own and sheets on a coarser one, so the film's places and characters did not match.

- **The master** opens with the style file's style block, word for word (The master, paragraph 1).
- **Every image made from the master** (character sheets, prop sheets, location sheets, plates) says three things, right after its
  opening sentence:
  1. **It looks like the original:** what it shows looks exactly as it does in the attached reference image, when the master shows
     it: "<He | She | It> looks exactly as <he | she | it> does in the attached reference image: <the character's facts>."
  2. **It copies the style completely:** "Copy the style of the attached reference image completely, <the style's copy words>, and
     draw <him | her | it | the place> in it:". The copy words are "its rendering, materials, palette and shading" unless the style
     file's image words give others.
  3. **The style block, word for word,** right after that colon.
- **The check:** `checks.py` refuses an image prompt whose style block differs from the style file's (`--style
  scripts/styles/<template>.md` on `master`, `sheet`, `prop`, `plate` and `location`).
- **Tested in pixel art:** written this way, three sheets with uploaded photos, a prop sheet and two plates came out in the master's
  style and grid on the first try.

## Order of work

1. **The master** (below), with no image attached. Look at it: the style's look; every character in full, apart from the others,
   on-model to its facts, at the right size against the others; the place's layout; the props; no lettering. A wrong size (a character
   drawn bigger or smaller against the others than its facts give) or a wrong layout is remade: every reference after it copies it, faults included. Nothing else remakes the master,
   and it is made again at most once, all its fixes in that one remake: a detail it gets wrong (a thing on the wrong character, a
   prop missing or extra) is left to the sheet or prop sheet made after it, looked at and remade like any sheet (one film's master
   was made three times over one character's accessory). Look also at:
   - **each character's age, read from the face alone:** a stylised look draws adults younger, and the master's face is the one
     every sheet and clip copies (a <number>-year-old drawn five to nine years younger stayed that age through the film). A face that reads more than five years off is fixed in the master, once: its age written as what shows it (lines at the eyes and
     mouth, the jaw, the hair's colour) and the master made again before any sheet. One remake brought faces 10-19 years off to
     within 5 years of their age in 4 of 4 masters, while in a cartoon look whose faces carry no age marks it moved the age by a year
     (judged blind by two readers who agreed within 3 years on 28 stylised faces); a face still off after that one remake keeps
     the master, and its sheet carries the age by hair, build and clothes; a <number>-year-old drawn 11-16 years younger read within a year of that age with the age written so (2 of 2);
2. **Read the master as drawn.** In the details the facts leave open, the image wins (a colour the master chose won over the one a
   later sheet prompt named). Write every later prompt from what the master shows, and name each thing it added: named, they come back; added pictures and posters are written as plain or abstract, as `location.md` says. Then rewrite each clip's `positions`
   and `stateIn` against the fixtures as the location sheet drew them (where each fixture stands, which side it is on): the clips
   take the place from the images, and the characters' places from the story.
3. **One parallel batch, each with the master attached** (settings: `models.md`, Reference images): a character sheet per character
   (`sheet-stylized.md`), a prop sheet per prop in 3D and per prop that moves in 2D (below), and the location references: a two-panel sheet per place in 3D (`location.md`, OTHER STYLES), background plates
   in 2D (below), where the props are drawn into the plates. A character, prop or place the master does not show is made the same
   way, with the master attached as the style source only. A character or prop that changes on screen gets one sheet per
   form.
4. **Look at every image** as `SKILL.md` says, beside the master: the same style, grid or material and finish. Remake a failed one.
5. **Clips** get the location references, then the character sheets, then the prop sheets (`clips.md`). Never the master.
   A place, character or prop the script changes after its image is made gets its image made again before any clip uses it: a
   fixture written into a place after its sheet existed only in words, and every clip drew it its own way.
6. **After the first clips,** the places, the changed states and the props a clip drew first come from the film's own frames
   (`clips.md`, References from the film's own frames); the master stays the design.

A location photo the user uploaded is attached, after the master, to that place's location sheet (3D) or plates (2D) ("the
attached photo is the place: keep its layout, drawn in this look"). On a plate, the master first and the photo second, the
photo's layout held, drawn in the look.

## The master

Write it in these paragraphs, about 3,500-5,000 characters with the style block (masters of 3,300-4,800 worked; the check refuses one
over 6,000), and check
it with `python3 "${HF_WORKFLOWS}/drama-ads/scripts/checks.py" master master.txt --style "${HF_WORKFLOWS}/drama-ads/scripts/styles/<template>.md"`:

1. "A single wide film still from a <the style's medium>." Then the style block, word for word. It holds no light and no place:
   the film's own place and light follow.
2. The place: the film's main location (where most of the cast meet) as a map, in `location.md` THE PLACE's order (far end, left
   side, right side, floor and the anchor), with its materials and colours, and its light in the style's light words (its file's Light words, fitted to the scene's time and sources): a light
   sentence from another look pulls the picture into that look (another style's light words turned one 3D look into another). In a look
   whose sets are one material, write every set material in it, with the shape words of its style file: a set piece written in a
   real material was built in that material. Never name a story prop's kind in the set dressing: the kind named there was drawn
   again as more of the prop.
   Never name a light source out of frame as a thing: write only its light (its warmth, height and side),
   or the source itself is drawn. When the anchor is one of a set of alike things, describe the
   others as "the far ones" and the anchor's different state in its own sentence.
3. The props the story turns on, each where it is at the first frame, every visible part named (an unnamed part is dropped later):
   a prop someone holds is in that character's hand, or the location sheet keeps a spare copy on the set. A machine, pack or sign is
   a plain unbranded object (`clips.md`, The clip's prompt), except the user's own product, with its label (Prop sheets).
4. The characters, each in its own sentence: where it stands relative to the anchor; its facts (`cast[]`) in the style's words;
   "seen in full from head to <feet>" (without it a figure stood behind furniture and its legs were never drawn); its size against
   the others ("its head level with <a part of another character>"), all of them at the same distance from the camera so their sizes
   compare (a small character nearer the lens read as tall as a big one); where the hook's first frame puts it, in one calm pose, facing the camera at
   three-quarters, apart from the others.
   A human's age is a number with adult proportions, never cute, little or chubby: stylised looks make adults read young.
5. The camera: at the near end, at the characters' eye height (at their scale: about 20 cm for 25 cm puppets), level, looking
   diagonally into the depth so both sides recede; the characters in the middle ground, apart, with open floor between them. A style
   file that names its own camera (Image words) is followed; a flat world is seen straight on, square to its backdrop.
6. "No text, labels, logos or watermarks.", or the style file's own closing sentence; a master that shows the user's own product
   ends with its label sentence in its place (Prop sheets).

The master holds the place and the characters who meet there; tested with two and three characters. A character who is not in it
gets its sheet from the master as the style source only (`sheet-stylized.md`). With an uploaded face photo, the photo goes to that
character's sheet call after the master (`sheet-stylized.md`).

## Prop sheets

In 3D, one per prop in `props` of script.json, checked with `python3 "${HF_WORKFLOWS}/drama-ads/scripts/checks.py" prop prop-<id>.txt --style "${HF_WORKFLOWS}/drama-ads/scripts/styles/<template>.md"`; a piece of furniture that
is also the anchor needs none unless it moves. In 2D a prop lives in the plate of the place where it sits still, and gets a prop sheet
for the shots where it moves, left out of those plates (tested: no prop drawn twice). A prop that sits still in an early clip and
moves in a later one is drawn into the plate and also gets its sheet; the frame plates of the clips where it moves remove it. Left out
of the plate and sent only as a sheet, a still prop was never drawn. A prop that changes form gets one entry per form. Its size is
written in centimetres only: a size written against a body part drew that body part into the sheet.
"A prop reference sheet of the <prop> from the attached reference image, as a prop of a <the style's medium>. It looks exactly
like the <prop> in the attached reference image: <the prop from its facts, every visible part named>. Copy the style of the attached
reference image completely, <the style's copy words>, and draw it in it: <the style block>. The finish of the film rather than a
product photograph. Two views side by side on a plain light-grey background: a front view at eye level and a three-quarter view from
above. Soft, even studio light from the front, the same in both views. One object only: take only this <prop> from the attached
reference image, nothing of its room, its light or anything else in it. No text, labels, logos or watermarks."

- Without the finish sentence a prop on a plain background comes out a photoreal product shot.
- **In 2D, six views**, each named by where it faces, like a 2D character sheet (`sheet-stylized.md`). In place of the two views,
  write:

  "Six views of the whole <prop> at one size on <the style's sheet background>, in two rows. Top row: the front at eye level, <its
  front feature> toward us; its left <side or end>, seen from the viewer's left; the back at eye level, <its back feature>
  toward us. Bottom row: its right <side or end>, seen from the viewer's right; a three-quarter view from above at its
  front-left; and straight down from above. Soft, even studio light from the front, the same in every view."

  When the story turns on a side none of them shows, swap the three-quarter view for that side. Check it
  with `checks.py prop prop-<id>.txt --2d`.

- **A prop the user gave a photo of:** attach the photo after the master and call it "the attached photo". After the looks-like
  sentence write "Its shape, parts, colours and markings come from the attached photo, redrawn in this style." (untested). The finish
  sentence keeps it from coming back as the photo.
- A prop that is not in the master: "A prop reference sheet of <the prop>, as a prop of a <the style's medium>: <the prop from
  its facts, every visible part named, its size in centimetres>. Copy the style of the attached reference image completely, <the
  style's copy words>, and draw it in it: <the style block>. The finish of the film rather than a product photograph." Then the
  views, the light, "One object only: take nothing from the attached reference image but its style. No text, labels, logos or
  watermarks."
- **The user's own product** keeps its name and label. In place of "No text, labels, logos or watermarks." its sheet ends: "Its
  label reads exactly "<the words the user or their photo gives>", <its lettering, colour and place on the product>; no other
  text, logos or watermarks." Ended with "No text, labels, logos", an ad's product came back with its name nowhere on screen.
  - The label sentence gives its lines in order, top to bottom ("<line one>" above "<line two>"), and that it reads upright and
    level across <its face>.

## Background plates (2D)

A drawn world has no reverse side to photograph, and a two-panel sheet halves each view (a pixel grid came out finer in a half-width
panel than in the film's frame). So a 2D location is **one plate per direction its scene's shots face**: a picture in the film's aspect ratio of the empty
place in the film's own framing, open floor in its lower third, the scene's props in their places. A scene shot one way gets one
plate; shot and reverse shot gets two, toward the far end and back toward the near end. A flat world is one straight-on backdrop: nothing lies
behind its camera. Write the directions in the location's `plates` (`script-format.md`),
and check each plate with `python3 "${HF_WORKFLOWS}/drama-ads/scripts/checks.py" plate plate-<id>-<n>.txt --style "${HF_WORKFLOWS}/drama-ads/scripts/styles/<template>.md"`.

- Toward the far end: "A background plate for one shot of a <vertical | horizontal | square> <the style's medium>: the <place> from the
  attached reference image. It looks exactly as it does in the attached reference image: the same room, fixtures, materials, colours
  and light. Copy the style of the attached reference image completely, <the style's copy words>, and draw the place in it: <the style
  block>. One <vertical | horizontal | square> frame, seen from the open floor near the <near end>, looking toward the <far end> at a slight three-quarter angle: <what fills the background,
  the props in their places, what shows at the left and right edges>. The lower third of the frame is open, clear floor in <light>.
  Camera at about <the characters' eye height> above the floor, perfectly level, zero Dutch angle; nothing closer than <three metres
  at human scale> to the lens. No people, figures, silhouettes or animals anywhere, in windows and reflections too; the place stands
  empty. No text, logos, user interface or watermarks." (or the style file's own closing sentence)
- A place the master does not show: "A background plate for one shot of a <vertical | horizontal | square> <the style's medium>:
  <the place, its description>. Copy the style of the attached reference image completely, <the style's copy words>, and draw the place
  in it: <the style block>. Take nothing else from the attached reference image, none of its room or the characters in it." Then the
  view, the floor, the camera and the empty-place sentence, as above.
- The reverse plate adds: "This is the reverse view: the camera stands on the open floor just in front of the <far-end landmark> and
  looks back toward the <near end>, the side the attached reference image is seen from." Then what fills its background, and "The
  <left-side things> now stand along the right side, the <right-side things> at the left."
- A flat backdrop: "A flat backdrop for a <vertical | horizontal | square> <the style's medium>: the <place> from the attached reference
  image. Copy the style of the attached reference image completely, <the style's copy words>, and draw the place in it: <the style
  block>. The <place>'s <wall> seen straight on, flat like a theatre backdrop. One <vertical | horizontal | square> frame. Across the upper half,
  <…>. Across the middle, <what the characters stand in front of, the props in their places>. The bottom quarter is a flat strip of
  <floor>, open and clear across the whole width. Seen dead level and square to the wall, no perspective." Then the empty-place
  sentence and "No text, logos or watermarks."
- Make each plate as its own view: a plate made as "the master with the characters taken out" lost the prop a character was holding.
- A plate draws its props in their first state, and every shot "the view of" it brings them back so: after a prop changes, write the later
  shots as "the same framing as the end of @Video1" with the changed state named, or make a second plate.
- Put the camera on open floor, never behind furniture, and keep the floor at the characters' feet clear: 2D has few depth cues, and
  an object at a character's ground line reads as something it stands on.
- The first clip in a place takes these plates; every later clip there takes frame plates from that clip (`clips.md`, References from
  the film's own frames). In a test the plates drawn from the master gave two clips of one place that looked like two places; plates
  from the first clip's frames held the place, its pixel grid and the characters' faces through three clips.
