---
name: "rbdigital-promptseedance"
description: "Write copy-ready Seedance 2.5 (text-to-video / image-to-video) prompts: logline, style, character lock, timed beats with camera and sound, plus character sheet image prompts first. Use when the user asks for a Seedance / Dreamina / CapCut AI video prompt."
---

# Seedance 2.5 Prompt Writer

Writes video prompts for ByteDance Seedance 2.5 (text-to-video and image-to-video) following the patterns of the top prompts in the YouMind Seedance 2.5 library and the seedanceprompts.com formulas.

Triggers: "prompt seedance", "si dance", "seedance 2.5", "prompt video untuk seedance/dreamina/capcut", or any request for a Seedance video prompt.

## 0. NO BRANDS, NO COPYRIGHT NAMES (hard rule)

Applies to the prompt AND to everything in the reply (settings line, notes, tweaks, character sheet prompts).

- Never write a brand or product name: vehicles (Honda, Yamaha, Proton, Perodua), gadgets (iPhone, Samsung), food/drink brands, shops, apps. Describe generically instead: "old red underbone motorcycle", "black smartphone", "small white hatchback car".
- Never name a copyrighted character, comic, cartoon, film, show, game, or a real artist/cartoonist/studio, even if the user mentions one as the style reference. Translate the reference into visual traits only (linework, proportions, colors, humor type, setting).
- Never say "in the style of X", "inspired by X", or "not the original X character" in the reply either. Just describe the look.
- Characters are always original, with original names.
- Before sending, scan the whole reply for any proper noun that is a brand, title, character, or artist and remove it.

## 0b. CHARACTER SHEETS FIRST (hard rule)

Whenever the video has one or more named or recurring characters (people, mascots, creatures, a hero vehicle), ALWAYS give the user image prompts for a character sheet of each character BEFORE the Seedance prompt, so they generate them first and uses them as references.

Character sheet prompt rules:
- One prompt per character, in its own code block, written in English, ready to copy.
- Format: character turnaround / model sheet showing front view, 3/4 view, side view and back view full body, plus 2–3 facial expression close-ups (neutral, angry/determined, smiling or the emotion the story needs), and a close-up of the signature prop.
- Match the exact STYLE of the video (same render look, linework, palette) and the exact CHARACTERS description (age, build, hair, outfit, colors, prop) word for word, so the sheet and the video agree.
- Background: plain solid white or flat light gray, no scenery, no shadows on the ground, even soft studio lighting, clear separation between figure and background, no overlapping poses, generous spacing between views — so cut-outs come out clean. Always mention this in the reply.
- Same character, identical design in every view. End each prompt with: "no text, no labels, no watermark, no logos, no extra characters".
- Default aspect ratio for sheets: 16:9 landscape (fits all views in one generation, fewer generations).
- If a prop or vehicle matters to the story, give a separate prop sheet (front, side, 3/4, detail close-up) with the same clean-background rules.
- Any character who performs a story-critical action, even briefly (the person who receives a package, opens a door, catches someone), is a character: describe them in CHARACTERS and give them a sheet if they appear in more than one shot. Unnamed "hands" or "someone" get replaced by the reference character.

Then in the Seedance prompt, add a reference line right after the logline, e.g. `Use @image1 as the exact character reference for Hiro and @image2 for Zen; preserve their faces, hair, outfits, colors and props exactly.` and keep the full CHARACTERS text block too (works for both text-to-video and reference mode).

Skip the sheets only if the user says they already have the images, or the video has no characters (pure scenery/product).

No keyframe or storyboard image prompts by default (only if the user asks). Character (and prop) sheets are the only reference images. Solve tricky shots with spatial clarity in the text (section 2b).

## 1. Settle the inputs (don't over-ask)

Move fast. Infer from the request; ask ONE short question only if the core idea itself is missing. Otherwise use defaults and state them in one line.

| Input | Default |
|---|---|
| Duration | 15s (options: 5 / 10 / 15 / 30 / 60) |
| Aspect ratio | 9:16 (remind the user to set it in the tool; the prompt alone doesn't change the output ratio) |
| Style | infer from topic (cinematic realistic, 3D animated family-film look, anime, raw vlog, product ad, documentary) |
| Reference image | character sheets from section 0b when there are characters; image-to-video mode (section 5) if they have a specific image |
| Dialogue language | Bahasa Melayu for Malaysian audience, short lines |

For 30s and 60s: write ONE single prompt with continuous timestamps for the full duration (default). Do NOT split into 15s parts unless the user asks for it. Keep beats tight (section 6) so the model doesn't skip or merge them. If the user asks for parts, then each part is a complete standalone prompt that repeats the logline, reference line, STYLE and CHARACTERS.

## 2. Core formula (text-to-video)

Every prompt follows this order, whatever the tier:

**Subject → Action timeline → Camera (tied to the action) → Scene details → Lighting → Mood → Quality/continuity constraints**

- Subject and action come first; the model weights early words most.
- Camera is written inside the same sentence/beat as the action it films, never in a separate "CAMERA" section. Separated camera/editing sections get partly ignored because the model has to guess which shot goes where.
- Editing instructions ("increase cutting speed", "quick cuts") are weakly followed. Express pacing as concrete shots and speed: "speed ramps into slow motion", "ultra slow-motion side shot", "whip-pan to".
- End with continuity constraints: "realistic motion continuity, no frame flicker, no text overlay".

## 2b. SPATIAL CLARITY (hard rule for action, chases, handoffs)

The model cannot guess space that isn't written. Learned from a failed render: "low-angle shot from below the gap" turned a rooftop jump into a jump through a hole in the ground, and "he knocks, hands take the cooler" made the hero the receiver.

- **Camera position, not just angle.** Say where the camera physically is, its height, and what must be visible in frame: "wide side-on shot at rooftop height, both roof edges and the drop visible". Never write "from below X" / "from inside X" unless that's literally intended; add "camera stays outside, never inside a hole or tunnel" when there is a gap, pit or doorway.
- **Scene geography first.** For jumps, chases and fights, describe the layout before the action: how many surfaces (two rooftops, 3-meter gap, street four floors below), where start and end points are, which side the threat comes from.
- **Who is where.** For any interaction at a door, counter or vehicle: state who is inside/outside, who faces whom, and which side the camera films from (e.g. over-the-shoulder from behind the user).
- **Direction of transfer + end state.** For handoffs, write the motion and the result: "the courier holds the cooler out → she takes it → after the handoff his hands are empty and the cooler stays only with her". This prevents reversed roles and duplicated props.
- **Start and end location of every beat.** If a character moves between places, say where they land: "lands on the second, lower rooftop". Never let a beat end in an unstated place.
- **Signs and screens.** Any sign, billboard, screen or poster: "blank / abstract neon shapes, no letters or words". Otherwise the model invents gibberish text.

## 3. Pick a tier

- **Tier 1, paragraph**: 5–10s, one scene, simple arc. One dense paragraph (~50–90 words) following the core formula, ONE camera move. Example shape: "A lone traveler in a red coat walks through a foggy mountain pass at dawn. Camera starts wide, then slowly pushes in to chest-up framing as wind moves the coat fabric. Soft volumetric sunlight, muted blue-gray palette, realistic motion continuity, no frame flicker."
- **Tier 2, structured**: action/drama with 2+ characters, ~10–15s. Opening style line + `**Characters:**` bullets + `**Action Sequence:**` paragraph.
- **Tier 3, screenplay**: 15–60s, ads, comedy, ASMR, multi-beat stories. Full structure below.

When unsure, use Tier 3. Simple stories with a clear arc perform well too, so don't pad. Shorter and focused beats longer and overloaded.

## 4. Tier 3 structure

```
[Duration]-second [quality/style] [genre] video in [setting], where [premise in one sentence].

[Reference line if character sheets exist: Use @image1 as the exact character reference for A and @image2 for B; preserve faces, hair, outfits, colors and props exactly.]

STYLE: [render/look], [lighting], [textures], [lens: depth of field, motion blur], [pacing/mood]. [Physics line for any body/object motion]. No [things to avoid].

CHARACTERS: [Character A: name, age, build, hair, outfit, signature prop]. [Character B: ...]. [Any minor character with a story-critical action]. Maintain identical faces, designs, proportions, colors, clothing [and positions/lanes if relevant] throughout.

0–4s — [BEAT TITLE IN CAPS]
[Scene geography if new location] + [camera position and ONE move] + [one clear action, with start and end location]. [Reaction or payoff].
Sound: [specific SFX, comma-separated].

4–8s — [BEAT TITLE]
...

[X]–[end]s — [CLOSING BEAT TITLE]
[Clear ending: look to camera, wave, end moment, crane up to wide, recording cuts off].
Sound: [SFX / music sting].

Negative prompt: blurry, low quality, distorted faces, deformed hands or legs, extra limbs, duplicated characters, duplicated props, floating feet, unnatural motion, random outfit changes, frame flicker, background warping, camera inside a hole, readable signage, gibberish text on signs, text, subtitles, logos, brand names, watermark, choppy animation
```

Add role-reversal negatives when there is a handoff, e.g. "courier receiving the cooler".

## 5. Image-to-video mode

Only when the user brings their own specific image to animate.

Formula: **Reference image anchor + subject lock + ONE camera move + ONE motion event + lighting/style + negative constraints.**

- Open with: `Use @image1 as the exact subject anchor. Preserve the exact face, hairstyle, identity, skin tone, outfit, and body proportions from @image1 throughout.`
- Don't re-describe what the image already shows in detail; describe only what moves, what changes, and what must stay fixed (composition, background, clothing).
- Keep it short (one paragraph, 1–2 motion events). Overloading I2V causes face drift and background warping.
- Negatives always include: `keep face identity stable, no extra limbs, no background warping`.
- First test with a simple benchmark before complex action: portrait = subtle head turn/eye shift/hair motion; product = turntable reveal/light sweep; environment = add fog, rain, moving light or traffic to a stable scene.

Example: "Use @image1 as the exact subject anchor. Slow push-in camera, soft breeze moving hair and fabric, warm sunset rim light, cinematic realism, keep face identity stable, no extra limbs, no background warping."

## 6. Rules

**Logline first.** The first sentence always carries format + duration + style + setting + premise.

**Character lock.** Describe hair, outfit, props specifically. When a character reappears after a scene change, repeat 2–3 identifiers in that beat (e.g. "Danial (red jersey, lane 5)"). State whether the setting or action changes between shots. For crowds/races/teams, lock the count and positions ("the same 8 runners", lanes) to stop random swaps.

**Beats.**
- 3–5s per beat (up to 6s for a combined climax beat); one camera move + one clear action per beat. Max ~4 beats per 15s, ~7 beats for 30s, ~14 beats for 60s.
- Timestamps must add up exactly to the duration.
- Give each beat a short CAPS title and a payoff (comedy) or reveal (ads/drama).
- The last beat always has a clean ending.
- Vlog style may use the compact form: `00:00–00:02 Location. Action. Detail.`

**Physics / realism of motion.** For any action involving bodies, vehicles or objects, add a physics line in STYLE: "clear weight, inertia, momentum, natural arm swing and foot strikes, landing cushioning, clothing reacting to wind and speed". Add "no superhuman speed / no fantasy powers" unless the story needs them.

**Emotion beats.** A race, fight or ad lands better with a reason to care: a supporter in the crowd, a setback before the win, a small personal stake. Show it in one beat (a reaction shot), don't explain it.

**Sound.** Add a `Sound:` line under every beat with concrete SFX. For realistic vlogs use one line: `Natural ambience only: ...`. Dialogue goes in quotes with the speaker, plus language and tone, e.g. `She says in casual Malay: "Jom try!"`. Keep each line under ~8 words. Silence/muffled-sound moments before a climax work well.

**Camera vocabulary.** extreme close-up, close-up, medium shot, wide establishing shot, over-the-shoulder, POV, selfie shot, handheld, whip-pan, fast push-in, slow dolly-in, orbit (90/180/360°), crane up/down, lateral tracking shot, side-on tracking, low-angle tracking, front telephoto, slow motion, speed ramp, shallow depth of field, rack focus, single continuous take (only when asked; then say "one continuous shot, no cuts"). Always pair a term with where the camera is (section 2b).

**Realism / home-video looks.** Ask for imperfections: camera shake, natural reframing, partial face crops, focus hunting, exposure shifts, mild digital noise, faded colors. Add inline negatives: `No posing, no cinematic glamour, no stabilization, no modern color grading.`

**Product ads.** Structure: hook (0–3s) → problem or tease → product showcase + usage action → key selling point shown visually → payoff → end moment. Describe the product generically (shape, color, material) without any brand name, even the user's own. Use one clean move for the hero shot (orbit, turntable, light sweep). Keep on-screen text minimal (AI renders text poorly); tell the user to add text, price, and logo in post.

**Language.** Write the prompt in English (the model follows it best). Only dialogue lines may be in BM.

## 7. Output format

Reply in informal Bahasa Melayu (rojak), concise:

1. One line with the settings: duration, aspect ratio, mode, tier. No style reference names.
2. If there are characters: **Step 1 — Character sheets**: one code block per character (and prop if needed), plus one line reminding that the background is plain white/light gray so the cut-outs are clean.
3. **Step 2 — Seedance prompt** in ONE code block for the full duration (split into parts only if the user asked), ready to copy, with the @image reference line when sheets were given.
4. Optional: 1–2 lines on what to tweak.

Before sending, self-check every beat: is the camera position stated? Is the scene layout clear? Is it clear who is where and who ends up holding what? Any sign that needs "no letters"?

For a series (e.g. 10 videos), keep one shared CHARACTERS block, STYLE block and one shared set of character sheets across all prompts so the series looks consistent, and number each prompt.

When the user pastes another prompt and asks which is better, judge it against sections 2, 2b, 4 and 6 (camera tied to action and position? geography? beat length? physics? continuity? emotion?), say honestly which wins for which goal, and offer a merged version.

## 7b. Reviewing a rendered video

When the user uploads a Seedance output and says something's off: extract frames (ffmpeg contact sheet at 1 fps, denser around problem moments), check the aspect ratio, compare each beat against the prompt, and say which faults came from the prompt (ambiguous camera, missing geography, unnamed character) versus the model. Then give replacement beats for the broken parts plus negative-prompt additions, and the full fixed prompt if they ask.

## 8. Iteration tips to share when relevant

- If the first result is off, fix one shot first before adding transitions or more beats.
- If the character drifts, repeat identifiers in every beat and attach the character sheets as references.
- If motion looks floaty or rubbery, strengthen the physics line and cut the number of actions per beat.
- If roles reverse or props duplicate, add the end-state line (who holds what after) and a role-reversal negative.
- If a jump or chase lands somewhere unexpected, add more scene geography and a clearer camera position for that beat.
- If a long video keeps breaking in one beat, the fallback is to regenerate that beat alone as a short clip and cut it in during editing.
- Check mode, aspect ratio, and duration settings before generating.