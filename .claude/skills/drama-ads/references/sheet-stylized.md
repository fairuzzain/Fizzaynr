# Character sheet: every other character (any style, any kind)

Scope: every character `references/sheet-realism.md` does not make: every character of a 3D or 2D film (a human in a cartoon
included), made from the style master (`references/style-master.md`); and a non-human character (`kind: other`) in live action, made
without one. Write the prompt into `sheet-<id>.txt` as plain text and nothing else (checks.py reads the whole file as the prompt) and
check it with `python3 "${HF_WORKFLOWS}/drama-ads/scripts/checks.py" sheet sheet-<id>.txt --stylized`. When checks.py refuses it, fix exactly what it names and
keep the rest.

You write the English prompt for one character reference sheet of a short video. The sheet is copied by the video model,
so it must show the character's exact design and nothing else.

## Every sheet

- One paragraph beginning with exactly "A character reference sheet of ": 600-1,500 characters without a style block (checks.py
  refuses one over 2,000), up to 3,500 with one in 3D and 4,000 with the nine views of 2D.
- Three views side by side on a plain light-grey background (in 2D, nine: In a 2D film, below): front view full body, back view full
  body, and a large front close-up of the face or head (of its front, for a character with neither). An object: "front view of the whole <object>, back view of the
  whole <object>, and a large front close-up of its face". Soft, even studio light from the front, the same in every view; a relaxed,
  neutral pose, arms loose at the sides, hands empty, the face calm. One character only.
- A human is written with the age as a number ("a <number>-year-old <woman | man>"), the gender, skin tone and hair the facts give, and the body
  proportions of that age; never "young woman", "young man" or a youth word. A human or humanlike body is always fully clothed in the
  wardrobe the facts give (`references/story-rules.md` NO SENSITIVE CONTENT). A non-human in its natural form
  needs no clothes, and no character is sexualised or drawn as a baby or the young of its kind.
- The image model draws every noun it reads, so name only what is in the picture: "a plain <thing>", never "<a thing> without <a feature>".
  Frame overlays are the one exception, safe in a ban because they are laid over the image, not things in it: end with "No text,
  labels, logos or watermarks."
- The design is original (`references/styles.md`): never name an existing meme character, game character, mascot or brand; checks.py
  refuses known names. It also refuses youth words (child, kid, boy, girl, teen, teenager, minor…), even in a negation.
- A double or twin of another cast member: make that member's sheet first, then repeat its prompt word for word, changing only the
  one visible detail that tells them apart.

## In a 3D or 2D film: from the style master

The master is attached (`references/models.md`, Reference images); call it "the attached reference image". Every sheet carries
the style block as `style-master.md` (The style block in every image) says; check it with `--style "${HF_WORKFLOWS}/drama-ads/scripts/styles/<template>.md"`.

**A character the master shows.** Write:

"A character reference sheet of the <character as the master shows it> from the attached reference image. <He | She | It> looks
exactly as <he | she | it> does in the attached reference image: <the character's facts, as the master drew them>. Copy the style
of the attached reference image completely, <the style's copy words>, and draw <him | her | it> in it: <the style block>."

Then come the views, the light and the pose, and: "One character only: take only this <character> from the attached reference image,
nothing of its room, its light or anything else in it. No text, labels, logos or watermarks." (or the style file's own closing
sentence; a character that is the user's own product ends with its label sentence in its place, `style-master.md`, Prop sheets)

The style file's sheet words (its image words), where it has them, follow the style block.

**Describe nothing differently from the master.** A sheet changes whatever its prompt words differently: one detail,
written in other words than the master's, became what those words name. For a detail the words could change, write "the same <detail> as in the
attached reference image".

**A character the master does not show.** Write:

"A character reference sheet of <the character>: <its facts>. Copy the style of the attached reference image completely, <the style's
copy words>, and draw it in it: <the style block>. Take nothing else from the attached reference image, none of its room, its light
or the characters in it."

Then come the views, the light, the pose, "One character only." and the closing sentence.

**Size.** It does not show on a one-character sheet, so the clip prompt says each character's size against the others.

**An uploaded face photo (`faceImage`).** Attach it after the master and call it "the attached face photo".

- **The photo wins on the face.** The master drew the face from words, so the looks-like sentence leaves the face and hair out:
  "<He | She | It> looks exactly as <he | she | it> does in the attached reference image, <his | her | its> face and hair aside:
  <the character's facts>." Then: "<His | Her | Its> face and hair come from the attached face photo, not from the attached reference
  image: <the parts of the face and hair>, redrawn in this style." Told only "exactly as in the attached reference image", a clay
  sheet followed the master's generic face, and the character read younger than the photo.
- **An animal:** its photo counts as its face photo too: "only this <animal>'s face and the colours and markings of its coat".
- **Identity, never texture:** take a photo's identity and colours, never its texture, and write its coat or hair in the style's own
  material, the same finish as the others, as the style file's sheet words give it. A coat's texture taken whole from a
  photo came back near-photographic beside the drawn or sculpted humans in pixel art and in clay. With that sentence the clay sheet held, though a trace of fine fur stayed in the clips.
- **Asymmetric marks by side:** name each by the character's own side ("its right <part> <its state>, its left
  <part> <its state>"). Written without sides, two different parts came out the same.
- **Tested** in pixel art, clay and paper collage: every sheet kept the photo's face, age, hair or coat, and every clip made from
  those sheets kept them.
- **A character design of the user's own** (a drawing, a render, a sheet) is attached the same way and wins on the whole design:
  "<His | Her | Its> face, hair, body, clothes and colours come from the attached face photo, redrawn in this style." (untested)
- **Never send the photo itself to a clip** (`clips.md`, References and their limits).

## In a 2D film: nine views

A drawn character has no body behind its drawings. Every angle a clip shows is a new drawing, and the video model invents whatever no
sheet shows. So a 2D sheet shows the character turning in place, every view named by where it faces. Live action and 3D keep the three
views of Every sheet: the video model builds a body from them.

**The views block.** In place of the three views, write (<their> is the character's own word: his, her or its):

"Nine views on <the style's sheet background, a plain light-grey background unless the style file gives another>, in two rows. Top row: six full-body views of <the character> at one size on one ground line, each
turned a different way: the front, facing us; three-quarter left, <their> face and body turned halfway toward the left edge of the sheet;
profile left, <their> face and whole body turned to the left edge of the sheet, <their> nose pointing at the left edge and the
back of <their> head toward the right edge, <their> left side toward us; the back, <their> back toward us; profile right, the mirror
image of profile left, <their> face and whole body turned to the right edge of the sheet, <their> nose pointing at the right edge
and the back of <their> head toward the left edge, <their> right side toward us; three-quarter right, turned halfway toward the
right edge. The two profiles face opposite edges. Bottom row: three large close-ups of <their> head and shoulders: the
front, three-quarter left, and profile left, <their> nose pointing at the left edge."

An animal takes "six views of the whole <animal>" and "close-ups of its head".

**Name each view by the sheet's edges.** Say where the nose and the back of the head point, and call the right profile the mirror of
the left. Never write "the viewer's left" or "the right shoulder nearer" alone.

- Written with "the viewer's left", one of three sheets drew both profiles facing right.
- Named by the nose alone, the same character's sheet still drew both profiles facing right in two of four takes.
- With the mirror and the back of the head added, both of two takes held, as did every other sheet of that film (pixel art);
  in later films it failed 2 of 3, 2 of 2 and 4 of 4 takes on other characters, so check both profiles on every sheet.

**Look at every view.** The three-quarter views turned less reliably than the profiles. Remake a sheet in which two views face the
same way.

**Length.** With the style block, a 2D sheet runs to about 3,000-3,600 characters. Check it with `--2d` (`checks.py sheet sheet-<id>.txt
--stylized --2d`), which allows up to 4,000 with the style block and refuses a block without both profiles.

## A non-human character in live action

No image is attached unless the user uploaded one. The character is a real, photographed thing of its kind, with true materials and textures, described in the sheet in plain literal words: shape, size, materials, colours, the face it has or has
not, accessories, the same in every view. The call is `seedream_v5_pro` (`references/models.md`).

With an uploaded photo (a pet), attach it and call it "the attached face photo": "Take from the attached face photo only this
<animal>'s face, ears, coat colours and markings." Here it keeps its real texture: tested on an animal's photo, the clips kept its coat, ears and
what it wore. Check it with `--stylized --photo`.
