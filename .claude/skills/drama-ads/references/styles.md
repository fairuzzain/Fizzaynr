# Styles

## Choosing the style

`template` in script.json is the id of the film's style (the table below), and `style` is that style's line. Take the style the user
names or describes, or the look of a reference they ask for. When they name none, take the look of what they give (a character
design, a reference video); with none, the format's default look (`formats.md`), else `live action`. What they give never changes a
style they name. A look no style covers gets a style file of your own (Any other style), written from the reference when the look
is a reference's (`SKILL.md`, The user's own material).

Read only the chosen style's file in `scripts/styles/`. A style sets how the world looks and how its characters are built, move and sound;
it never sets the genre or the story.

- **Characters can be anything** (`characters.md`). What the style makes normal (animals that talk in a cartoon) is not a world rule
  (`story-rules.md`, OBVIOUS FIRST).
- **Everything is original:** no existing character, game, show, logo or brand, and never their names. `scripts/checks.py` refuses
  known names in image prompts but never checks `script.json`, so keep them out of the script too; moderation stops jobs that look
  like protected IP. A style line describes a look in plain words and never names a studio, an artist, a film, a show or a game.

## Families

The family decides how the reference images are made and how the clips are written:

| Family      | Its world                                     | Reference images                                                                                                                                                | Clips                    |
| ----------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| live action | photographed                                  | No master: `sheet-realism.md` (humans), `sheet-stylized.md` (others, as real things), two-panel location sheets (`location.md`)                                 | `clips.md`               |
| 3D          | built: computer-generated or a real miniature | `style-master.md`: the master, then from it the character sheets (`sheet-stylized.md`), prop sheets and two-panel location sheets (`location.md`, OTHER STYLES) | `clips.md`               |
| 2D          | drawn                                         | `style-master.md`: the master, then from it the character sheets in nine views (`sheet-stylized.md`), prop sheets and background plates                         | `clips.md`, its 2D rules |

## The styles

| Template        | Family      | For                                                                                                                          | File                              |
| --------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| `live action`   | live action | photoreal scenes shot like a feature film (the default)                                                                      | `scripts/styles/live-action.md`   |
| `phone`         | live action | a story told on phone video: selfies to the front camera and handheld observed scenes                                        | `scripts/styles/phone.md`         |
| `feature-3d`    | 3D          | a 3D animated feature-film cartoon                                                                                           | `scripts/styles/feature-3d.md`    |
| `hyperreal-3d`  | 3D          | glossy hard-surface figures in a spotless photoreal CG world                                                                 | `scripts/styles/hyperreal-3d.md`  |
| `doll-3d`       | 3D          | a world of dolls: every character a doll with a smooth sculpted head, big glossy eyes and moulded clothes, in realistic sets | `scripts/styles/doll-3d.md`       |
| `crochet`       | 3D          | a handmade world knitted and crocheted from yarn                                                                             | `scripts/styles/crochet.md`       |
| `claymation`    | 3D          | stop-motion plasticine puppets and sets                                                                                      | `scripts/styles/claymation.md`    |
| `paper-diorama` | 3D          | a cardboard-and-paper model set with flat printed cut-out figures                                                            | `scripts/styles/paper-diorama.md` |
| `pixel-art`     | 2D          | a cozy pixel-art life-sim game                                                                                               | `scripts/styles/pixel-art.md`     |
| `paper-collage` | 2D          | a flat torn-paper scrapbook world with sticker cut-out characters                                                            | `scripts/styles/paper-collage.md` |
| `ink-cartoon`   | 2D          | a classic drawn cartoon with bold ink outlines and gloved characters                                                         | `scripts/styles/ink-cartoon.md`   |

## What a style file holds

Every style file has the same sections in the same order. A section the style has nothing for says "None."

| Section                  | What it is                                                                                                                                                                                                     | Where it goes                                                                                                                                                               |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Style line**           | One line of plain words: the medium, the rendering, the palette, how characters are built                                                                                                                      | script.json's `style`; the first words of every clip prompt                                                                                                                 |
| **Style block** (3D, 2D) | The look written out in full, with no light and no place: medium, rendering, materials, palette, how characters and sets are built                                                                             | Word for word into the master and into every image made from it, after the copy sentence (`style-master.md`, The style block in every image); `checks.py --style` checks it |
| **Light words** (3D, 2D) | How light looks in this style                                                                                                                                                                                  | The master, the plates and the location sheets write their scene's light in these words; a sheet keeps its studio light                                                     |
| **Image words**          | What the style adds to image prompts: its medium, copy words, sheet words, set materials, the camera of its master and plates, its closing sentence, how its look fares at a resolution when that was measured | The prompts `style-master.md`, `sheet-stylized.md` and `location.md` name                                                                                                   |
| **Video words**          | The rendering, motion, faces, voices and the hold sentence in this style                                                                                                                                       | Every clip prompt, after the style line; the hold sentence at its end (`clips.md`, The clip's prompt)                                                                       |
| **Acting**               | How characters act and speak in this style                                                                                                                                                                     | The clips' beats                                                                                                                                                            |
| **Motion and physics**   | How bodies, materials and effects move                                                                                                                                                                         | The clips' beats                                                                                                                                                            |
| **Light and camera**     | The clips' light, framing and cutting rhythm                                                                                                                                                                   | The clips' shots                                                                                                                                                            |
| **Captions**             | The captions' look in words, then the flags of the caption scripts of the `video-montage` workflow that draw it, taken from the style's references                                                             | Handed to the `video-montage` workflow with the film (`clips.md`, Captions)                                                                                                 |
| **Pitfalls**             | What the style breaks in the image or video model, and the words that prevent it                                                                                                                               | Wherever they apply                                                                                                                                                         |

## Any other style

A look no style covers (anime, a watercolour storybook, felt puppets, a noir comic…) gets a style file of your own, `style-<name>.md`
in the film's folder, written before the script with the sections above:

- **Family:** 3D when its world is built (rendered in 3D, or a photographed model, puppet or miniature); 2D when it is drawn or flat;
  live action when it is a real camera.
- **Style line, style block, light words, video words:** in plain descriptive words, with no studio, artist or title. Start from the
  nearest style's file, and take over its pitfalls.
- **Captions:** the look of the captions in the user's reference when it has any (outlined capitals or plain text, a label, how many
  words at a time), written as the same tools' flags; otherwise the nearest style's.
