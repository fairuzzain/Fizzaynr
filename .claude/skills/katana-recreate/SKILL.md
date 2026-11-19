---
name: "katana-recreate"
description: "Recreate a reference video edit (shots, pacing, cuts on the beat) with the user's own photos of any subject: people, products, cars, food, fashion, places. Use for 'katana', 'recreate this edit', 'buat semula edit ni'."
---

# Katana Recreate

A Katana-style edit rebuilder for any subject. Input: one **reference edit** (an uploaded video or a built-in preset) + **up to 5 asset photos** (people, products, cars, food, clothing, pets, places, logos the user owns) + optional instructions. Output: a new MP4 that keeps the reference's shot order, shot lengths, cut points on the music, camera moves and typography, with the user's assets in frame.

Reply in the language the user writes in. On-screen text and any voiceover default to Bahasa Melayu unless the user asks for another language or the reference's language should be kept.

## Commands
- `/katana` → show the preset catalog (below) grouped by subject and ask which one, or ask for a reference video.
- `/katana <preset-name>` → run that preset directly.
- Plain request ("recreate this edit with my product", "buat edit macam ni guna gambar aku") → start the workflow without a command.

## Rights rule (always)
Only rebuild a reference the user owns or has permission to use, including its music. If the reference uses a commercial track, keep the timing but tell the user to swap in licensed music before posting. Asset photos of real people must be the user or people who agreed to it; never put a celebrity's face, a copyrighted character or someone else's brand/mascot into generated shots. Links to Instagram/TikTok profiles are not accepted; the reference must be an uploaded file or a direct media-file link.

## Step 0 — Production Engine: Nexabot (Mandatory Default)
Under user global rules, all video generation is automated through **Nexabot** client (`bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"`):
1. **Mandatory Daily API Check**: Run `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check` before generating.
2. **Batch Video Generation**: Generate all shots via Nexabot batch (`bun nexabot.ts batch clips.json --parallel 4`) using modes `sfv` (with input photo start frame), `omni`, or `nexadance`. Cost: 0.4 credit/video (free on API Unlimited).
3. **Never wait for user manual generation** in Axcel/Flow/Seedance web, and **never call paid connectors** (Magnific, Higgsfield, kie.ai).

## Step 1 — Analyze the reference
Work on a copy in the working directory.
1. Probe: `ffprobe` for duration, resolution, aspect ratio, fps. The output must match these exactly.
2. Cut detection: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.30)',showinfo" -f null - 2>&1 | grep pts_time` → list of cut timestamps. If fewer cuts than visually obvious, retry at 0.22; merge cuts closer than 0.25 s.
3. Keyframes: extract the middle frame of every shot (`ffmpeg -ss <mid> -frames:v 1 shot_NN.jpg`) and view each with Read.
4. Audio: extract `ref_audio.wav`. Detect beats/onsets (`pip install librosa --break-system-packages`; `librosa.beat.beat_track` + `onset_detect`). Note which cuts land on beats, drops, whooshes. Note any voiceover or speech separately.
5. Text: note any on-screen typography per shot (font feel, position, animation, words).

Write `breakdown.md` — a table with one row per shot:
| # | start–end (s) | length | framing (ECU/CU/MS/WS) | camera move | subject & action | lighting/look | transition in | text overlay | beat sync |

Show the breakdown to the user as a compact list and ask only if something is ambiguous (e.g. which asset goes in which shot). Otherwise continue.

## Step 2 — Assets
- Up to 5 photos. Label them @A1…@A5 and describe each in one line (e.g. "@A1 = woman, shoulder-length black hair, cream hijab", "@A2 = matte black 500 ml water bottle, white logo").
- Identify the subject type of each asset and apply the matching **consistency lock** in every prompt that uses it:
  - **Person** — face, skin tone, hair/hijab, build, outfit, accessories. Same outfit across shots unless the reference changes outfits.
  - **Product** — exact shape, colour, material/finish, logo placement, label text, packaging, size relative to hands.
  - **Vehicle** — make, model, colour, rims, body kit, plate (blank or the user's own).
  - **Clothing/fashion** — garment cut, fabric, colour, pattern, fit, how it drapes; who or what wears it.
  - **Food/drink** — dish components, plating, garnish, vessel, portion, steam/condensation.
  - **Pet/animal** — breed, fur colour and markings, size, collar.
  - **Place/interior** — layout, key furniture or landmarks, colour palette, signage.
  - **Logo/brand mark** (user-owned only) — exact colours and proportions; never redraw, place the real file in assembly when possible.
  - Anything else — list the 4–6 visual traits that make it recognisable and lock them.
- Map assets to shots: the hero asset gets the shots the reference gives its hero; secondary assets fill the rest. If the reference subject differs from the user's (e.g. reference shows a car, user has a perfume), translate each shot's role (hero reveal, detail macro, in-use, lifestyle, end card) to the user's subject instead of copying the action literally. Respect user instructions about which shot matters most or what must stay unchanged.
- If a shot needs an angle or detail no photo shows (back of a product, side profile of a person), say so and either ask for that photo or flag the shot as "inferred angle".

## Step 3 — Generate shots
For each shot write a prompt with this structure (one block per shot, copy-ready):
```
SHOT 03 — 1.4s — 9:16 — 30fps
Ref image: @A1 (+ @A3)
Subject: <locked asset description from Step 2>
Action: <what happens, matched to the reference's role for this shot>
Camera: <exact move from breakdown: fast push-in / orbit left / low tracking / whip pan>
Look: <lighting, grade, time of day, lens feel copied from the reference>
Keep: <must-not-change details from the consistency lock>
Avoid: morphing logos, warped text, extra fingers/limbs, duplicate objects, extra people
```
- Generate each shot a little longer than needed (≥ +0.5 s, or the model's minimum length) so it can be trimmed on the cut.
- Skip generation for shots that are pure text/graphic cards — build those in code during assembly (ffmpeg drawtext or a small Remotion/HTML render).
- Prompt mode: deliver all shot prompts in one file `shot_prompts.md` (send it) and tell the user to upload the clips named shot_01.mp4, shot_02.mp4 …

## Step 4 — Assemble
1. Normalize every clip to the reference's resolution, fps and pixel format; crop/scale to fill (no letterbox).
2. Trim each clip to its exact shot length from the breakdown, choosing the most active segment.
3. Rebuild transitions from the breakdown (hard cut, flash, whip/blur, zoom punch, dissolve) with ffmpeg filters.
4. Rebuild text overlays with the same position, size and timing (in the language chosen above). Overlay user-owned logo files directly instead of generated versions.
5. Audio: lay the reference audio (or the user's licensed replacement) so every cut lands on the same beat as the reference. If the reference had voiceover, write a new script in the chosen language matching the original's length and offer TTS. Loudness-normalize to about -14 LUFS.
6. Render `katana_<preset-or-ref>_v1.mp4`.

## Step 5 — Verify, then deliver
- Compare cut timestamps of output vs reference (re-run scene detection on the output); every cut within ±2 frames.
- Check duration, aspect ratio and fps match the reference.
- Extract a contact sheet (one frame per shot) and view it: asset identity consistent across shots per the consistency lock, no warped logos/text/hands.
Send the MP4 with SendUserFile plus one line of context. Then stop — no recap of steps.

## Revisions
Corrections come as plain messages ("shot 4 the bottle looks blue, fix it", "swap @A2 for this photo"). Regenerate only the affected shots, re-assemble, bump the version (v2, v3 …). A new subject on the same reference = reuse breakdown.md and redo Steps 2–5 only.

## Preset catalog
Each preset is a ready-made breakdown so no reference upload is needed. Category in brackets: [P] personalized edit, [S] style transfer, [M] motion transfer. Any preset works with any subject; the "best for" note is a hint, and Step 2's role translation adapts it.

**Any subject**
1. **hero-reveal** [P] — 9:16, 12 s, 8 shots. Black screen → detail ECU light catch → 3/4 slow push-in → macro orbit on a key detail → side tracking → second detail ECU → in-use/context shot → hero pull-back with name title on the drop. Best for: product, car, gadget.
2. **beat-sync-montage** [P] — 9:16, 10 s, 12 shots ~0.8 s each, hard cuts on every beat, flash frames on snare hits, bold condensed white text, 2 words max per card. Best for: anything with many photos.
3. **turntable-360** [M] — 9:16, 8 s, continuous orbit around the subject on a turntable in a clean studio, one cut at 4 s to a detail, spec/feature text slides in from left. Best for: product, shoe, car, figurine.
4. **before-after** [P] — 9:16, 10 s, 5 s before (@A1) / 5 s after (@A2), whip-pan transition on the drop, "SEBELUM / SELEPAS" text. Best for: makeovers, renovations, mods, cleaning, edits.
5. **film-look** [S] — restyle the user's own footage/photos to 35 mm film: grain, halation, warm highlights, 4:5 crop, light leaks between shots. Best for: anything.
6. **asmr-macro** [P] — 9:16, 14 s, slow macro shots of textures and small actions (open, press, pour, close), soft cuts, no music, foley sounds. Best for: product, food, skincare, car interior.

**People & fashion**
7. **aura-walk** [P] — 9:16, 8 s, person walks slow-motion toward camera, low angle, golden hour, lens flare, freeze frame + name text at the end.
8. **outfit-transition** [P] — 9:16, 9 s, 6 outfit swaps on the beat via jump/cover-the-lens transitions, same pose and framing each time, outfit name text.
9. **day-in-life** [P] — 9:16, 15 s, 10 handheld POV/lifestyle shots (wake, coffee, commute, work, evening), time stamps on screen.

**Products & brands**
10. **unboxing-pop** [P] — 9:16, 10 s, top-down box open → hands lift product → three quick feature close-ups → product on a colour backdrop with logo end card.
11. **floating-product** [M] — 9:16, 8 s, product floats and rotates against a gradient, ingredient/feature elements orbit around it, splash or particle burst on the drop.

**Food & drink**
12. **recipe-speed** [P] — 9:16, 12 s, top-down fast cuts of each prep step on the beat, final plated hero shot with steam, dish name text.
13. **pour-shot** [P] — 9:16, 6 s, slow-motion pour or sauce drizzle macro, condensation/steam close-up, hero with name.

**Places & travel**
14. **place-tour** [P] — 9:16 or 16:9, 15 s, drone/wide establishing → walk-through gimbal shots → detail shots → sunset wide with location text.

**Vehicles**
15. **night-drive** [P] — 9:16, 10 s, neon street, wet-asphalt reflections, rolling shots, light-trail transitions, model name end card.
16. **pov-drive** [M] — 16:9 or 9:16, 15 s, driver POV hands on wheel, dashboard ECU, side-mirror shot, window-down highway, ends on parked hero shot at sunset.

To add a preset: the user gives a 3–30 s reference; run Step 1 and save the breakdown under a new preset name in this catalog only if the user asks to save it.