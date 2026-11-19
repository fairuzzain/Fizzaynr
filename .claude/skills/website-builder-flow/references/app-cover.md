# App cover + OG image (3:2, Higgsfield brand style)

Produce launch covers that could sit NEXT TO the official Higgsfield covers
without looking like a knock-off. This is the image behind `og_image_url` and
the marketplace card. Also use it when the user directly asks for a "cover",
"кавер", "обложка", "OG image", "launch cover" or "thumbnail" for a product,
model, feature or app announcement.

## The one rule that makes or breaks this skill

**The image model NEVER renders text. Not the title, not the wordmark, not
labels, not UI. It renders ONLY the scene.** Every glyph on the cover is drawn
by `compose_cover.py` from the Inter font — that is why the type is identical
and crisp on every cover, like the official ones. If a generated scene comes
back with lettering in it, the candidate is DEAD. Regenerate with "no text, no
letters, no logos, no captions" appended.

Division of labor:

- **`generate_image`** → one vivid full-bleed scene (people, product, world).
  Nothing else.
- **`remove_background`** → subject cutout for the capsule break-out.
- **`compose_cover.py`** (run in the sandbox) → capsule, frame, dots, wordmark,
  TITLE, CTA pill, scrim, break-out compositing. All geometry and typography.
  Text is ALWAYS the topmost layer.

**Outputs** (one compose run makes all three, same scene in each):

| file                 | what                                  | use                                   |
| -------------------- | ------------------------------------- | ------------------------------------- |
| `<slug>_cover.png`   | full-bleed 3:2 scene + type lockup    | marketplace / `marketplace_cover_url` |
| `<slug>_og.png`      | frame + stadium capsule + corner dots | OG / `og_image_url`                   |
| `<slug>_og_wide.png` | same, 1.91:1                          | Twitter/FB link cards                 |

## What an official cover looks like (internalize before prompting)

1. **A big, vivid, energetic scene with STORY DENSITY.** Saturated color,
   strong art direction, subject filling 55–75 % of the frame — and the frame
   is FULL: 2–4 supporting story props/layers around the subject. Never a dim
   empty room, never a lone subject floating on a bare seamless. One person on
   an empty backdrop reads as AI slop even when bright — stage a world, not a
   portrait.
2. **One structured type lockup**, left-anchored or centered: the real
   Higgsfield wordmark (squiggle glyph + "Higgsfield", drawn automatically by
   the script) → HUGE display-caps title (2 lines max; the title is the loudest
   thing on the cover) → `( Available now at higgsfield.ai )` pill. NO tagline
   — the reference lockup is wordmark → title → CTA, three rows, nothing else.
   Tight, aligned, flat white. It reads as ONE unit, not scattered captions.
3. **Text is the LAST layer — always.** The full lockup renders on top of
   everything; the subject NEVER covers a letter. Type may sit over the
   subject's body/props — keep it OFF the face: position with `--block-x/y` so
   the title crosses shoulders, arms or background, not eyes/mouth.
4. **The capsule variant**: solid frame color from the approved palette,
   stadium-shaped window, 4 corner dots — and with `--cutout` the subject
   BREAKS OUT of the capsule onto the frame. That pop-out is the whole point of
   the cutout.

Hard bans (non-negotiable): acid lime/yellow `#D9FF2E`-family frames or text
(the script blocks them), 3D/chrome/beveled/gradient lettering, watermarks,
borders inside the art, model-rendered UI panels, any MODEL-rendered
squiggle/logo (the real glyph is pasted by code — never ask the model to draw
it).

## Workflow

### 1. Brief

You need: the **product/feature name** (exact spelling — the script renders it
as the title), a **scene concept**, and a **typography treatment**. For an app
build, derive the name from `og_title` and the scene from what the app does.

**Keep `og_title` SHORT — at most 3–4 words, ideally ONE** (`Lumen`,
`PixelForge`, `Recipe Vault`): it is the feed-card title, the browser tab
title, and the dominant cover text. Put the pitch in `og_description`, never in
`og_title`.

Decide:

- **slug** (`dreamcut`), **title** (`DreamCut` — break long names with `\n`),
  CTA (default stands). NO tagline unless the user explicitly hands you one.
- **Scene concept** — the creative leap. Take the product's core verb and stage
  it as a physical, photographable moment with humor or spectacle (Higgsfield
  covers are witty, not corporate). "AI video editor" → an editor mid-leap
  slicing a giant ribbon of film with chrome scissors in a bright studio.
  "Skill marketplace" → a tiny craftsman forging a glowing card. Never settle
  for "person looks at hologram UI".
- **Route**: humans/lifestyle/fashion → PHOTO (a Soul model). Product/3D/
  illustrated world, no humans → GRAPHIC (`gpt_image_2_6`). Default PHOTO in
  doubt. Use `models_list` if unsure which models are available.

### 2. Scene prompt doctrine (both routes)

Build the prompt from these blocks, in order:

1. Subject + action, concrete and physical ("a film editor in a bold red
   bomber jacket mid-leap, cutting a giant arc of 35mm film with oversized
   chrome scissors").
2. **World + props (story density)**: name 2–4 supporting elements that fill
   the frame around the subject. Add "no readable screens" whenever
   screens/props could sprout text.
3. **Scale + placement**: "waist-up, subject fills two thirds of the frame,
   positioned right-of-center" — and reserve the block side: "soft open
   negative space upper-left on a warm white wall". Negative space = a real
   surface (wall, sky, backdrop), NOT a black void.
4. Palette, committed and saturated: name 2–3 colors. Avoid lime/acid
   yellow-green.
5. Light + lens: "bright soft key with punchy shadows, low wide angle,
   commercial editorial grade".
6. Always end with: "no text, no letters, no logos, no captions, no UI".

**Reference the scene mood.** Import 1–2 hosted scene refs that match the
intended mood with `media_import_url` and pass the returned ids as `medias`
(role `image`) — they carry grade/energy only; never let a ref's content leak
into the concept. Hosted at
`https://static.higgsfield.ai/website-builder/app-cover-generator/refs/`:

| ref file                                                 | mood                                   |
| -------------------------------------------------------- | -------------------------------------- |
| `scene-stadium-action.jpg`                               | epic sports spectacle, golden hour     |
| `scene-studio-fashion.jpg`                               | clean bright studio, bold single color |
| `scene-epic-film.jpg`                                    | cinematic blockbuster scale            |
| `scene-glow-portrait.jpg`                                | neon/beauty glow portrait              |
| `scene-street-lifestyle.jpg`                             | sunny UGC lifestyle                    |
| `scene-office-banana.jpg` / `scene-office-slapstick.jpg` | office comedy                          |
| `scene-comedy-absurd.jpg`                                | staged absurdist studio humor          |
| `scene-beauty-product.jpg`                               | glossy product macro                   |
| `scene-cozy-ugc.jpg`                                     | warm handheld authenticity             |
| `scene-painterly-epic.jpg`                               | painterly fantasy                      |

**PHOTO route** — `generate_image`, a Soul model (`soul_cinematic`, or a
cleaner fashion/studio Soul), `aspect_ratio: "3:2"`, `quality: "2k"`, count 2,
with 1–2 scene-ref ids in `medias`.

**GRAPHIC route** — `generate_image`, `gpt_image_2_6`, `aspect_ratio: "3:2"`,
`quality: "high"`, `resolution: "2k"`, count 2. Same prompt doctrine; style
words like "glossy 3D render / claymation diorama / painterly still" replace
the lens block.

### 3. Judge the scenes BEFORE composing

Look at both candidates. Kill a candidate if ANY of: text/letters appeared;
subject under ~50 % of frame; palette washed-out or muddy; the reserved
negative space is missing (no room for the lockup); anatomy/prop glitches; "AI
slop" tells (waxy skin, melted hands, gibberish objects). If both die, fix the
prompt (more concrete action, harder scale words, brighter palette) and
regenerate — do not compose a weak scene. Compose is free; generations are not.

If the winning scene is under ~1500 px wide, run `upscale_image` first — the
script refuses art below 1500 px.

### 4. Break-out pass (whenever there is a clear subject)

Run `remove_background` on the winning scene — the cutout is the SAME image,
subject isolated with alpha. On the framed OG variants the subject then BREAKS
OUT of the stadium capsule onto the frame color instead of being amputated by
the window edge (the official pop-out look). The window shrink is ADAPTIVE — it
only kicks in when the subject actually reaches the window's top/side edges; a
subject fully inside keeps the full scene, no fat frame ring. The cutout MUST
come from the same generation as the scene or it silently misaligns.

### 5. Compose — run `compose_cover.py` in the sandbox

Composition happens in the Higgsfield cloud sandbox via **`sandbox_exec`**
(NEVER a local/built-in shell). The sandbox has `python3` + Pillow + `curl`
preinstalled and internet access; `compose_cover.py` is too long to paste, so
`curl` it in. The sandbox is per-user and discarded shortly after each call, so
**chain the whole compose into ONE `sandbox_exec` command with `&&`** and
export the results before finishing.

One `sandbox_exec` call does everything — pull the scene + cutout + script,
compose all three outputs (the script fetches the Inter font + wordmark glyph
from the hosted asset base itself):

```bash
cd /home/user &&
curl -fsSL "<SCENE_IMAGE_URL>"  -o scene.png &&
curl -fsSL "<CUTOUT_IMAGE_URL>" -o cutout.png &&
curl -fsSL "https://static.higgsfield.ai/website-builder/app-cover-generator/compose_cover.py" -o compose_cover.py &&
python3 compose_cover.py \
  --art scene.png --cutout cutout.png \
  --title "DreamCut" \
  --title-width 0.48 \
  --anchor left --block-x 0.07 --block-y 0.30 \
  --frame-color "#D23B2E" \
  --out-cover dreamcut_cover.png --out-og dreamcut_og.png \
  --out-og-wide dreamcut_og_wide.png
```

Then upload each output from the SAME sandbox: call `media_upload` for a
presigned PUT URL, `curl -X PUT --upload-file dreamcut_og.png "<upload_url>"`
inside `sandbox_exec`, then `media_confirm`.

**ONE typeface, hardcoded.** Inter — the title face on the reference cover —
renders everything: wordmark, title, CTA. There is no font flag.

**All type is flat white — no shadows.** Legibility comes from scene contrast
(dark negative space) and the scrim, not effects.

**Frame color** (approved palette): pick FROM the scene's palette with contrast
— bright scene → deep frame (`#243A5E` deep-navy, `#D23B2E` signal-red,
`#7A7D3C` olive); dark scene → light frame (`#A9CFF4` sky-blue, `#F7DDB9` peach,
`#F1EEE6` cream, `#E7B7B0` dusty-rose, `#D6D3CE` warm-gray). Echoing an accent
already in the scene (red jacket → signal-red) looks intentional; a random
pastel does not. Lime is BLOCKED by the script — do not `--force-frame-color`
around it.

**Block placement**: `--anchor left --block-x 0.07` with the subject on the
right (or mirror it); `--anchor center` only for symmetric hero scenes.
`--block-y` so the title sits on the subject's torso band (0.26–0.38 usually).
`--scrim 60-110` depending on how busy the art is behind the block. On framed
outputs the whole lockup is clamped INSIDE the capsule automatically — text
never touches the frame.

### 6. Final check + deliver — the side-by-side gate

Open your `_og.png` NEXT TO the official covers at
`https://static.higgsfield.ai/website-builder/app-cover-generator/layout/layout-hooks.jpg`
and `.../layout/layout-stadium.jpg` and honestly answer: **"If these were in
the same folder, does mine look like the intern made it?"** Concretely verify:

- [ ] scene is vivid + dense — no dead darkness, subject dominates
- [ ] lockup reads as one designed unit; title huge (≥ 3× wordmark height)
- [ ] text is the topmost layer, fully legible, off the face; on OG the subject
      breaks out of the capsule (no window amputation)
- [ ] zero model-rendered text anywhere in the art
- [ ] frame color from palette, correct contrast, dots visible
- [ ] no lime, no 3D text, no squiggle, no watermarks
- [ ] art ≥ 1500 px wide (script enforces)

If any box fails — fix and re-run. Adjusting the drawn text is a compose-flag
change (`--title`, `--block-x/y`, `--title-width`), never a regeneration — the
model never touched the text.

### 7. Deliver / wire into the app

- **Standalone cover request**: show all three files to the user and save them
  to their folder if one is connected.
- **App/website build (the publish gate)**: after uploading (step 5), set the
  durable URLs in `app/src/app-meta.json`: `<slug>_og.png` → `og_image_url`,
  `<slug>_cover.png` → `marketplace_cover_url`. Commit before `publish_website`.

## Deviations

The user's explicit wishes always beat the defaults above: different aspect
ratio, no capsule, another CTA, partner lockups ("Higgsfield MCP × Claude"
style, `--tagline`/wordmark tweaks), vertical format. On errors: the sandbox
lacks Pillow → it should not (report it); font/glyph won't fetch → check the
sandbox reached the hosted asset base; generation refusals → rework the prompt
content, keep the structure. The brand system is the default, not a cage.
