---
name: "seedance-prompt"
description: "Use when the user asks for a Seedance (2.5) video prompt — writes copy-ready prompts using the YouMind library structure: logline, style, character lock, timed beats with sound."
---

# Seedance 2.5 Prompt Writer

Writes video prompts for ByteDance Seedance 2.5 (text-to-video and image-to-video) following the patterns of the top prompts in the YouMind Seedance 2.5 library and the seedanceprompts.com formulas.

Triggers: "prompt seedance", "si dance", "seedance 2.5", "prompt video untuk seedance/dreamina/capcut", or any request for a Seedance video prompt.

## 0. NO BRANDS, NO COPYRIGHT NAMES (hard rule)

Applies to the prompt AND to everything in the reply (settings line, notes, tweaks).

- Never write a brand or product name: vehicles (Honda, Yamaha, Proton, Perodua), gadgets (iPhone, Samsung), food/drink brands, shops, apps. Describe generically instead: "old red underbone motorcycle", "black smartphone", "small white hatchback car".
- Never name a copyrighted character, comic, cartoon, film, show, game, or a real artist/cartoonist/studio, even if the user mentions one as the style reference. Translate the reference into visual traits only (linework, proportions, colors, humor type, setting).
- Never say "in the style of X", "inspired by X", or "not the original X character" in the reply either. Just describe the look.
- Characters are always original, with original names.
- Before sending, scan the whole reply for any proper noun that is a brand, title, character, or artist and remove it.

## 1. Settle the inputs (don't over-ask)

The user prefers moving fast. Infer from the request; ask ONE short question only if the core idea itself is missing. Otherwise use defaults and state them in one line.

| Input | Default |
|---|---|
| Duration | 15s (options: 5 / 10 / 15 / 30) |
| Aspect ratio | 9:16 |
| Style | infer from topic (cinematic realistic, 3D animated family-film look, anime, raw vlog, product ad, documentary) |
| Reference image | none; if he says he has one, use image-to-video mode (section 5) |
| Dialogue language | Bahasa Melayu for Malaysian audience, short lines |

## 2. Core formula (text-to-video)

Every prompt follows this order, whatever the tier:

**Subject → Action timeline → Camera (tied to the action) → Scene details → Lighting → Mood → Quality/continuity constraints**

- Subject and action come first; the model weights early words most.
- Camera is written inside the same sentence/beat as the action it films, never in a separate "CAMERA" section. Separated camera/editing sections get partly ignored because the model has to guess which shot goes where.
- Editing instructions ("increase cutting speed", "quick cuts") are weakly followed. Express pacing as concrete shots and speed: "speed ramps into slow motion", "ultra slow-motion side shot", "whip-pan to".
- End with continuity constraints: "realistic motion continuity, no frame flicker, no text overlay".

## 3. Pick a tier

- **Tier 1, paragraph**: 5–10s, one scene, simple arc. One dense paragraph (~50–90 words) following the core formula, ONE camera move. Example shape: "A lone traveler in a red coat walks through a foggy mountain pass at dawn. Camera starts wide, then slowly pushes in to chest-up framing as wind moves the coat fabric. Soft volumetric sunlight, muted blue-gray palette, realistic motion continuity, no frame flicker."
- **Tier 2, structured**: action/drama with 2+ characters, ~10–15s. Opening style line + `**Characters:**` bullets + `**Action Sequence:**` paragraph.
- **Tier 3, screenplay**: 15–30s, ads, comedy, ASMR, multi-beat stories. Full structure below.

When unsure, use Tier 3. Simple stories with a clear arc perform well too, so don't pad. Shorter and focused beats longer and overloaded.

## 4. Tier 3 structure

```
[Duration]-second [quality/style] [genre] video in [setting], where [premise in one sentence].

STYLE: [render/look], [lighting], [textures], [lens: depth of field, motion blur], [pacing/mood]. [Physics line for any body/object motion]. No [things to avoid].

CHARACTERS: [Character A: name, age, build, hair, outfit, signature prop]. [Character B: ...]. Maintain identical faces, designs, proportions, colors, clothing [and positions/lanes if relevant] throughout.

0–4s — [BEAT TITLE IN CAPS]
[ONE camera move/shot type] + [one clear action]. [Reaction or payoff].
Sound: [specific SFX, comma-separated].

4–8s — [BEAT TITLE]
...

[X]–[end]s — [CLOSING BEAT TITLE]
[Clear ending: look to camera, wave, end moment, crane up to wide, recording cuts off].
Sound: [SFX / music sting].

Negative prompt: blurry, low quality, distorted faces, deformed hands or legs, extra limbs, duplicated characters, floating feet, unnatural motion, random outfit changes, frame flicker, background warping, text, subtitles, logos, brand names, watermark, choppy animation
```

## 5. Image-to-video mode

Formula: **Reference image anchor + subject lock + ONE camera move + ONE motion event + lighting/style + negative constraints.**

- Open with: `Use @image1 as the exact subject anchor. Preserve the exact face, hairstyle, identity, skin tone, outfit, and body proportions from @image1 throughout.`
- **Mandatory Face & Character Identity Lock**: When the prompt aims to lock face and character details completely ("sekiranya tak nak berubah apa pada wajah, karektor or anything"):
  Include: `Identity lock: keep [character/subject]'s face and features exactly as in @image1. Same face shape, eyes, nose, mouth, skin tone, hairline, freckles and marks. Don't slim, smooth, reshape, or age anything. Keep face identity stable, no extra limbs, no background warping.`
- Don't re-describe what the image already shows in detail; describe only what moves, what changes, and what must stay fixed (composition, background, clothing).
- Keep it short (one paragraph, 1–2 motion events). Overloading I2V causes face drift and background warping.
- Negatives always include: `keep face identity stable, no extra limbs, no background warping`.
- First test with a simple benchmark before complex action: portrait = subtle head turn/eye shift/hair motion; product = turntable reveal/light sweep; environment = add fog, rain, moving light or traffic to a stable scene.
- For longer I2V stories, chain clips: one short I2V prompt per shot, or use first/last frame mode.

Example: "Use @image1 as the exact subject anchor. Identity lock: keep the subject's face exactly as it is in @image1, same face shape, eyes, nose, mouth, skin tone, hairline, freckles and marks; don't slim, smooth, reshape or age anything. Slow push-in camera, soft breeze moving hair and fabric, warm sunset rim light, cinematic realism, keep face identity stable, no extra limbs, no background warping."

## 6. Rules

**Logline first.** The first sentence always carries format + duration + style + setting + premise.

**Character lock & Face Codes.** Describe hair, outfit, props specifically. When an edit or continuation changes only one element, use the Face Codes approach: "change only X, keep everything else exactly the same" (e.g. Pose only, Expression only, Outfit only, Background only) and append the Identity lock line: `Identity lock: keep face exactly as in reference, same face shape, features, skin tone, hairline; don't slim, smooth, reshape or age anything.` When a character reappears after a scene change, repeat 2–3 identifiers in that beat (e.g. "Danial (red jersey, lane 5)"). State whether the setting or action changes between shots. For crowds/races/teams, lock the count and positions ("the same 8 runners", lanes) to stop random swaps.

**Beats.**
- 3–5s per beat; one camera move + one clear action per beat. Max ~5 beats for 15s, ~7 beats for 30s.
- Timestamps must add up exactly to the duration.
- Give each beat a short CAPS title and a payoff (comedy) or reveal (ads/drama).
- The last beat always has a clean ending.
- Vlog style may use the compact form: `00:00–00:02 Location. Action. Detail.`

**Physics / realism of motion.** For any action involving bodies, vehicles or objects, add a physics line in STYLE: "clear weight, inertia, momentum, natural arm swing and foot strikes, landing cushioning, clothing reacting to wind and speed". Add "no superhuman speed / no fantasy powers" unless the story needs them.

**Emotion beats.** A race, fight or ad lands better with a reason to care: a supporter in the crowd, a setback before the win, a small personal stake. Show it in one beat (a reaction shot), don't explain it.

**Sound.** Add a `Sound:` line under every beat with concrete SFX. For realistic vlogs use one line: `Natural ambience only: ...`. Dialogue goes in quotes with the speaker, plus language and tone, e.g. `She says in casual Malay: "Jom try!"`. Keep each line under ~8 words. Silence/muffled-sound moments before a climax work well.

**Camera vocabulary.** extreme close-up, close-up, medium shot, wide establishing shot, over-the-shoulder, POV, selfie shot, handheld, whip-pan, fast push-in, slow dolly-in, orbit (90/180/360°), crane up/down, lateral tracking shot, low-angle tracking, front telephoto, slow motion, speed ramp, shallow depth of field, rack focus, single continuous take (only when asked; then say "one continuous shot, no cuts").

**Realism / home-video looks.** Ask for imperfections: camera shake, natural reframing, partial face crops, focus hunting, exposure shifts, mild digital noise, faded colors. Add inline negatives: `No posing, no cinematic glamour, no stabilization, no modern color grading.`

**Product ads.** Structure: hook (0–3s) → problem or tease → product showcase + usage action → key selling point shown visually → payoff → end moment. Describe the product generically (shape, color, material) without any brand name, even the user's own. Use one clean move for the hero shot (orbit, turntable, light sweep). Keep on-screen text minimal (AI renders text poorly); tell the user to add text, price, and logo in post.

**Language.** Write the prompt in English (the model follows it best). Only dialogue lines may be in BM.

## 7. Output format

Reply in informal Bahasa Melayu (rojak), concise:

1. One line with the settings: duration, aspect ratio, mode (text-to-video / image-to-video), tier. No style reference names.
2. The prompt in ONE code block, ready to copy.
3. Optional: 1–2 lines on what to tweak (e.g. shorten to 10s, split into 2×15s).

If the video needs reference images, also give image prompts and note that character/prop sheets should be on a plain, clean background so cut-outs come out clean.

For a series (e.g. 10 videos), keep one shared CHARACTERS block and STYLE block across all prompts so the series looks consistent, and number each prompt.

When the user pastes another prompt and asks which is better, judge it against sections 2, 4 and 6 (camera tied to action? beat length? physics? continuity? emotion?), say honestly which wins for which goal, and offer a merged version.

## 8. Iteration tips to share when relevant

- If the first result is off, fix one shot first before adding transitions or more beats.
- If the character drifts, repeat identifiers in every beat or switch to image-to-video mode.
- If motion looks floaty or rubbery, strengthen the physics line and cut the number of actions per beat.
- If 30s isn't supported or is unstable in one go, split into 2×15s at a natural beat and repeat STYLE + CHARACTERS in both.
- For I2V, run a simple benchmark motion first, then add complexity.
- Check mode, aspect ratio, and duration settings before generating.