---
name: character-sheet
version: 1.0
description: >-
  Build stylish, consistent character sheets (character reference / model
  sheets) from a brief, and optionally generate them. Assembles a
  copy-paste-ready image prompt using a proven slot-based architecture with a
  built-in "anti-AI / unretouched" realism engine, then can run it via
  Higgsfield generate_image. Multi-style presets: photoreal-unretouched,
  editorial, anime/2D, 3D-stylized, game-concept. Trigger on: "character
  sheet", "char sheet", "model sheet", "reference sheet", "turnaround",
  "expression sheet", "лист персонажа", "character reference", "консистентный
  персонаж", "split-screen character sheet", or any request to describe a
  character across multiple views/poses for image generation.
---

> **ENGINE OVERRIDE — Nexabot only.** This skill came from the Higgsfield connector. Do NOT call any
> Higgsfield tool, sandbox or model. Every `generate_image` / `generate_video` / `generate_audio` call,
> model name (Seedance, Seedream, Soul, Nano Banana, Kling, Veo, ElevenLabs, MiniMax...), `sandbox_exec`,
> `media_*`, `jobs_*`, `get_cost` / `use_unlim` and `get_workflow_bundle_file` maps to the local Nexabot /
> PowerShell equivalent in `$ROOT/.claude/skills/_shared/nexabot-routing.md`. Read that file
> before the first tool call. Keep this skill's creative workflow; only the engine changes. Scripts and
> references are local in this skill's `scripts\` and `references\` folders.

# Character Sheet Builder

Turn a character brief into a **stylish, internally-consistent character sheet prompt**, then (on request) generate it. Two modes:

- **Mode A — Prompt (default):** output one finished, copy-paste-ready prompt.
- **Mode B — Generate:** when the user says "сгенерируй / generate / make it / запусти", assemble the prompt **and** call `generate_image` (see § Generation).

The core value is the **slot architecture** below plus a **realism engine** that kills the AI-airbrushed look. Never freestyle a character-sheet prompt — fill the slots in order.

---

## Non-negotiable principles

These override any brief and apply to every preset unless the user explicitly changes them.

1. **Photorealism means anti-retouch, never idealized.** "Realistic" is *never* a synonym for flawless, beauty-filtered, or glamorized. Real means visible pores, natural asymmetry, matte skin with no glare/shine, naturally-worn (slightly uneven) makeup, and zero AI-smoothing artifacts. If a photoreal preset is chosen, the anti-AI realism module is mandatory, not optional.
2. **IP awareness — original characters only.** Never replicate a recognizable real person's likeness or a copyrighted character/property. Reference images are for *style and mood inspiration*, not direct reproduction. Always describe an **original** character; if the user names a celebrity or existing IP, use it only as a loose vibe and build a distinct original face/identity. Keep the wording "identical **original** character on all views".
3. **Mature facial structure for adults.** When a character is meant to read as an adult, actively avoid babyface / youthful rounded proportions. Specify grown-up structure: defined (not soft-round) jaw and cheekbones, longer facial thirds, mature bone structure, adult proportions. This is a recurring correction point — bias toward mature, not cute.
4. **Consistency carries forward.** When iterating on an existing character, **every previously-established detail (face, hair, body, outfit, accessories, jewelry) carries forward unchanged** unless the user explicitly changes it. Change only what's requested; restate the rest so nothing silently drifts.

---

## Workflow

1. **Read the brief.** Extract character identity, wardrobe, and desired style. Ask *at most* the 1–2 questions that genuinely block assembly (usually: style preset, and whether to generate). If the user pasted a reference character, preserve every physical detail verbatim. **If iterating on an existing character, carry forward every established detail unchanged and only alter what's explicitly requested** (Principle 4).
2. **Pick a style preset** (§ Style Presets) → this decides the Realism/Render module and the quality tail.
3. **Pick a composition preset** (§ Composition Presets) → this decides the opening clause.
4. **Fill the slots in order** (§ Slot Architecture). Every character-defining detail must be *specific* (materials, colors, cut, finish) — never generic ("nice top", "pretty face").
5. **Append the negative tail** (§ Negative Tail).
6. **Output** the single-line prompt. If Mode B, generate.

**Golden rules**
- **Consistency is the product.** Always state the character is *identical / the same original character* across every view. Physical description is written **once** and implicitly applies to all views.
- **One paragraph, comma-separated, ordered.** Image models weight earlier tokens more — composition and identity go first, quality tail last.
- **Specificity beats adjectives.** "cream white cropped wide-leg pants with eyelet floral embroidery and drawstring waist" ≫ "nice pants".
- **Head-to-toe wardrobe.** Top → layers → bottom → belt/sash → shoes → jewelry → bag. No gaps.
- **Consistent lighting + seamless background** are what make it read as a *sheet*, not a photo.

---

## Slot Architecture

Fill these in this exact order. Bracketed slots are variable; unbracketed text is the reusable scaffold.

```
[COMPOSITION CLAUSE], identical original [subject] on all views,
pure white seamless studio background, professional character sheet presentation,
[IDENTITY: age + ethnicity/skin],
[FACE: face shape, jawline, cheekbones, nose, lips],
[EYES + anti-glare clause],
[EYEBROWS], [HAIR: color, tone, length, style, finish, parting], [HAIR ACCESSORY if any],
[REALISM MODULE — from the chosen preset],
[BODY: body type + proportions],
[WARDROBE: top → layers → bottom → belt/sash → shoes → jewelry → bag],
[LIGHTING MODULE — from the chosen preset],
[QUALITY TAIL — from the chosen preset],
[NEGATIVE TAIL]
```

### Slot notes
- **IDENTITY:** age band ("young woman in her early twenties"), skin tone, heritage if relevant. Be respectful and specific. Original character only — never a real person's likeness (see Principle 2).
- **FACE:** oval/round/heart/square; jaw (soft/angular/delicate); cheekbones; nose; lips (shape + finish, e.g. "full lips, natural rosy-nude tint, soft matte-to-satin finish"). **For adult characters, enforce mature structure** (Principle 3): defined jawline and cheekbones, mature adult bone structure and facial proportions, explicitly *not* a youthful/rounded babyface.
- **EYES:** shape + tilt + color, then **always** the anti-glare clause for realism presets: *"naturally muted catchlights, no oversized specular glare in the iris, eye color muted rather than glowing."*
- **HAIR:** color + undertone + length + style + **finish** ("loose voluminous waves, round-barrel blowout finish") + parting. Finish is what sells realism.
- **WARDROBE:** name material, cut, color, and one detail per item. Jewelry is small and specific ("thin gold bracelet, small delicate gold rings"). State "no bag" explicitly if none.

---

## Style Presets

Each preset supplies three modules: **Realism/Render**, **Lighting**, **Quality Tail**. Default is `photoreal-unretouched` — the signature look.

### 1. `photoreal-unretouched` (default / signature)
> **Realism module (the anti-AI engine — this is the whole trick):**
> `visible fine skin texture with natural pores, fine lines, subtle asymmetries and texture irregularities, natural visible makeup with slightly uneven foundation blending rather than flawless coverage, faint natural blush, slight natural sheen rather than glossy or dewy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin completely free of artificial glare, shine or highlight blooms, matte-to-natural complexion` — plus optional imperfection anchors: `a few faint freckles, a small mole near the collarbone`.
>
> **Lighting:** `soft diffused studio lighting without harsh reflections`.
> **Quality tail:** `natural anatomy, high-end but unretouched commercial photography style, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail`.

### 2. `editorial-polished`
Same photoreal base, but allow refined glam: `flawless-but-natural skin with fine texture retained, soft dewy highlight on cheekbones, editorial beauty lighting with a soft key and gentle fill`. Quality tail: `high-end fashion editorial photography, magazine cover quality, cinematic realism, 4K`.

### 3. `anime-2d`
> **Render module:** `clean anime illustration, crisp lineart, cel-shaded flat color with soft gradient shadows, expressive large eyes with detailed iris highlights, consistent character model-sheet style`.
> **Lighting:** `even flat lighting, soft ambient shading`.
> **Quality tail:** `high-quality anime key visual, clean vector-like linework, sharp, 4K`. (Drop the skin-texture/pores clauses — they don't apply.)

### 4. `3d-stylized` (Pixar / DreamWorks feel)
> **Render module:** `stylized 3D character render, appealing exaggerated proportions, smooth subsurface-scattering skin, soft rounded features, detailed hair strands and cloth simulation`.
> **Lighting:** `soft global illumination, three-point studio lighting, gentle rim light`.
> **Quality tail:** `high-end 3D animation studio quality, octane/Unreal-style render, clean neutral background, 4K`.

### 5. `game-concept`
> **Render module:** `painterly game concept art, semi-realistic rendering, orthographic model sheet, clear silhouette, material callouts implied through detail`.
> **Lighting:** `neutral even concept-art lighting`.
> **Quality tail:** `professional character concept art, artstation quality, sharp, 4K`.

> If the user's style doesn't match a preset, build a custom render module in the same shape (Render + Lighting + Quality tail) and keep the composition + consistency scaffold intact.

---

## Composition Presets

Choose the opening clause. The user's default is **split-screen**.

- **split-screen** (default): `Split-screen character sheet composition, left side a full-body shot of the character standing upright in a neutral straight standing pose facing the camera with both feet flat on the ground and arms relaxed at the sides, full head-to-toe framing with the whole body and both feet visible, right side a tight close-up chest-up portrait of the same character,`
  - variants for the right side: `close-up face portrait`, `chest-up portrait`, `beauty close-up`.
  - **Hard framing rules (repeat these verbatim — this is what breaks most often):**
    - **Standing, always.** Left panel character is *standing* — never sitting, crouching, leaning, or cropped. Bake in: `standing full-body, head-to-toe, entire body and both feet in frame, not cropped, not sitting`.
    - **Close-up on the right, always.** Right panel is a tight crop (face or chest-up), never a second full body.
    - **Only the character.** Add to the Negative Tail every time: `single subject only, exactly one person, only the character in frame, no other people, no duplicate figures, no mannequin, no reflections, no props, no furniture, no background objects, empty seamless studio`.
- **turnaround / model sheet:** `Character turnaround model sheet, four consistent full-body views in a row — front view, 3/4 view, side profile, and back view, evenly spaced,`
- **expression sheet:** `Character expression sheet, one full-body reference on the left and a grid of head-and-shoulders portraits on the right showing varied expressions (neutral, smiling, serious, surprised),`
- **outfit variations:** `Character wardrobe sheet, the same character shown full-body in [N] different outfits side by side,`
- **triple panel:** `Three-panel character sheet — full body, chest-up portrait, and detail close-up of face and accessories,`

Match aspect ratio to composition (see § Generation).

---

## Negative Tail

Always end with (adjust the situational items):

```
no text, no watermark, no logos, no frame borders
```

Add when relevant: `no bag, no branding, no extra characters, no background props, no harsh shadows, no distorted anatomy, no extra fingers`.

**Always for split-screen sheets** (prevents the recurring breakage): `single subject only, exactly one person, only the character in frame, no other people, no duplicate figures, no mannequin, no reflections, no props, no furniture, no background objects, empty seamless studio, left panel standing full-body head-to-toe not cropped not sitting, right panel tight close-up not full body`.

For adult characters add: `no babyface, no overly youthful rounded proportions`. For photoreal add: `no beauty filter, no digital smoothing, no airbrushing, no plastic skin, no glossy skin`. Always (IP safety): the character is original — do not resemble any real celebrity or existing copyrighted character.

---

## Generation (Mode B)

Only when the user asks to generate/run. Assemble the prompt exactly as in Mode A, then call `generate_image`:

- **Aspect ratio by composition:** split-screen / turnaround / expression / triple → **16:9** (or 3:2). Single portrait → 2:3 or 3:4.
- **Model:** if unsure which model best fits (photoreal vs anime vs 3D), call `models_explore(action:'recommend')` with the goal first; otherwise use the account default image model.
- Pass the full assembled prompt as the prompt. Put hard exclusions from the Negative Tail into a negative field if the chosen model supports one; otherwise keep them inline in the prompt.
- After generating, show the result and offer one round of targeted fixes (e.g. "tighten wardrobe", "more skin texture", "swap right panel to face close-up").

Do not generate without an explicit ask — default is Mode A (text only).

---

## Reference skeleton (photoreal split-screen)

Use as a fill-in template when starting from scratch:

> Split-screen character sheet composition, left side a full-body shot of the character standing upright in a neutral straight standing pose facing the camera with both feet flat on the ground and arms relaxed at the sides, full head-to-toe framing with the whole body and both feet visible, right side a tight close-up chest-up portrait of the same character, identical original female character on both sides, single subject only exactly one person with only the character in frame, pure white seamless studio background, professional character sheet presentation, [AGE] with [SKIN TONE], [FACE SHAPE] with [JAW], [CHEEKBONES], [NOSE], [LIPS + finish], [EYE color/shape] with naturally muted catchlights and no artificial glare, [EYEBROWS], [HAIR color/tone/length/style/finish], visible fine skin texture with natural pores and subtle uneven tone, natural visible makeup with visible foundation texture rather than flawless coverage, [BLUSH/CONTOUR], slight natural sheen rather than glossy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin free of artificial glare or highlight blooms, matte-to-natural complexion, [BODY TYPE] with balanced proportions, wearing [TOP], [LAYERS], [BOTTOM], [BELT/SASH], [SHOES], [JEWELRY], [BAG or "no bag"], natural anatomy, high-end but unretouched commercial photography style, soft diffused studio lighting without harsh reflections, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail, single subject only, exactly one person, only the character in frame, no other people, no duplicate figures, no mannequin, no props, no furniture, no background objects, left panel standing full-body head-to-toe not cropped not sitting, right panel tight close-up not full body, no text, no watermark, no logos, no frame borders.

---
(Shared section: see ../_shared/unlimited-generations-use_unlim.md)
