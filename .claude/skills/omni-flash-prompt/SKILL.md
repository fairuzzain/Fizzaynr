---
name: "omni-flash-prompt"
description: "Use when the user asks for a Gemini Omni Flash 1.2 video prompt — writes copy-ready shot briefs with shot structure, audio direction, reference/frame tags, edit and extend prompts."
---

# Gemini Omni Flash 1.2 Prompt Writer

Writes video prompts for Google's Gemini Omni Flash 1.2 (text-to-video, image-to-video, first/last frame, reference-to-video, edit, extend). Omni Flash is built for iteration: generate a short take, then edit it with one-line follow-ups and extend it. Prompts are short shot briefs written as direction to a crew, not a screenplay.

Triggers: "prompt omni", "omni flash", "gemini omni", "omni 1.1", or any request for an Omni Flash video prompt.

## 0. NO BRANDS, NO COPYRIGHT NAMES (hard rule)

Applies to the prompt AND everything in the reply (settings line, notes, tweaks). Omni Flash also blocks real brands and recognizable people, so this protects the generation too.

- Never write a brand or product name: vehicles (Honda, Yamaha, Proton, Perodua), gadgets, food/drink brands, shops, apps. Describe generically: "old red underbone motorcycle", "small white hatchback car".
- Never name a copyrighted character, comic, cartoon, film, show, game, or a real artist/studio, even if the user names one as reference. Translate it into visual traits only.
- Never say "in the style of X" / "inspired by X". Just describe the look. ("in the style of <IMAGE_REF_0>" pointing to the user's own uploaded image is fine.)
- Characters are always original, with original names. No real people.
- Before sending, scan the whole reply for any brand, title, character or artist name and remove it.

## 1. Settle the inputs (don't over-ask)

The user moves fast. Infer from the request; ask ONE short question only if the core idea is missing. Otherwise use defaults and state them in one line.

| Input | Default |
|---|---|
| Duration | 15s per generation Full HD (range 10–15s). Longer = generate 15s then Extend (section 7) |
| Aspect ratio | 9:16 (only 16:9 or 9:16) |
| Resolution | 1080p (Full HD) default, atau 720p |
| Mode | text-to-video unless he has an image/clip |
| Dialogue language | Bahasa Melayu, short lines |

Duration, aspect ratio and resolution are SETTINGS, never prompt text.

## 2. The five elements (in this order)

1. **Subject + action** (required, first): who is in frame and what they do. Be specific; vague subjects go generic.
2. **Scene**: location, time of day, weather, background.
3. **Camera + light**: shot size, ONE named move, lens, light source.
4. **Audio** (always): dialogue, SFX, ambience, music, or explicit silence.
5. **Shot structure**: one continuous shot, or cuts with timing.

Then end with in-prompt negatives (there is NO negative-prompt field): e.g. `No on-screen text, no captions, no logos.`

## 3. Key Omni behaviours to write around

- **Multi-shot by default.** Unprompted, Omni cuts into a mini-story across several shots. For one take write: `One continuous shot, no scene cuts.` For a cut sequence, say so and time it.
- **Audio is invented if you don't direct it.** Always write the sound. Silence must be asked for: `No music, just room tone.` / `No dialogue.`
- **Timing ranges are budgets, not frame-accurate cuts.** Use a timecode block for sequences; keep 2–4 beats in 10s.
- **Triggers beat timestamps.** Event-driven lines land more precisely: `When he turns the key, the dashboard lights flicker on.`
- **Max 3 tracked subjects.** Four or more merge or drift. Crowds stay background, unnamed.
- **On-screen text:** renders well only when spelled out exactly (`a sign that says BENGKEL ALI`); undefined text gets invented. Latin script only; still verify. Default to no text and tell the user to add text/price/logo in post.
- **Physics knowledge is built in**, but still describe weight for vehicles/bodies: `tyres bite and squirm, body rolls into the corner, suspension compresses on landing`.
- **Camera vocabulary in film language** is understood: dolly in/out, push-in, pull-back, tracking, lateral tracking, crane up/down, orbit (90/180/360°), whip pan, snap zoom, dolly zoom, handheld, locked-off, POV, low-angle, overhead, rack focus, long lens, shallow depth of field, slow motion.
- **Prompt length:** 4 words to a paragraph both work. Default ~60–120 words. Shorter and focused beats overloaded.

## 4. Pick a format

**A. Single shot (default for most car content, product hero, vlog).** One paragraph following section 2.

```
[Subject + action, specific]. [Scene: place, time, weather]. [ONE camera move tied to the action], [lens], [light]. One continuous shot, no scene cuts. [Audio: SFX, ambience, dialogue in quotes with speaker and tone, or "no music"]. No on-screen text, no captions, no logos.
```

Example: "An old red underbone motorcycle idles outside a small kampung workshop at dusk, its rider in a faded blue jersey kicking the stand up and rolling onto the wet road. Low-angle tracking shot at wheel height follows the bike as it pulls away, 35mm lens, orange streetlight reflecting in puddles. One continuous shot, no scene cuts. Two-stroke engine crackle rising, tyres hissing on wet tarmac, distant azan, no music. No on-screen text, no logos."

**B. Timed sequence (ads, comedy, multi-beat, 8–10s).**

```
[One-line premise: format + setting + what happens]. [Look: light, lens, grade, texture].
[Character lock: name, age, build, hair, outfit, signature prop — max 3 characters].

[0-3s] [shot + one action].
[3-6s] [shot + one action / reaction].
[6-10s] [payoff shot + clean ending].

Audio: [SFX per beat, ambience, music or none]. [Dialogue: Name says in casual Malay: "..."].
Keep the same faces, outfits and car throughout. No on-screen text, no captions, no logos.
```

Rules: timestamps add up to the duration setting; one camera move + one action per beat; last beat has a clean end (look to camera, car drives out of frame, crane up to wide).

**C. Longer story (15–40s).** Don't cram it. Write the first 10s as format A or B, then give 1–3 Extend prompts (section 7). Or split into separate generations with the same reference images.

## 5. Image-to-video and first/last frame

- **Image-to-video:** the still is the opening frame. Don't re-describe it; describe only what moves, and name what must survive: `Nothing about the car, the background or the light changes from the still.`
- **First + last frame:** tag them in the prompt: `<FIRST_FRAME> <LAST_FRAME> One continuous camera move from the front view to the rear three-quarter view, orbiting right at bumper height...` Describe the transition between them.
- Make the last frame by EDITING the first frame image (same car, same light), not by generating it separately; near-matches cause morphing.
- Same image as first and last frame = seamless loop (good for product/car turntables).
- Frames can't be combined with references or edit input.

## 6. Reference-to-video (character/car/style lock across videos)

- Up to 10 reference images + 3 reference videos (each ≤3s; their audio is ignored). Tags are numbered from 0 in upload order: `<IMAGE_REF_0>`, `<IMAGE_REF_1>`, `<VIDEO_REF_0>`.
- Give each reference ONE job and say it: `The man in <IMAGE_REF_0> drives the car in <IMAGE_REF_1> along the coastal road. Match the camera move in <VIDEO_REF_0>.`
- Repeat what must carry over: `His face, hair and jacket come from <IMAGE_REF_0> unchanged.`
- Video refs are best for a camera move or body mechanics (a drift, a stunt, a dolly).
- Attach all references before the first generation; adding one mid-conversation destabilizes the scene.
- Tell the user reference sheets work best on plain, clean backgrounds, and give image prompts for them if he needs them.

## 7. Edit and Extend prompts

**Edit (follow-up on a take):** short, one change per turn, then preserve.
`Change the car colour to matte grey. Keep everything else the same.`
- Never re-describe the scene; everything described may be re-rendered.
- One change per turn; compound edits break consistency.
- ~4 edits per chain max. Re-anchor with: `Keep all character details and motion exactly as they are, only change the lighting.` Past that, regenerate with references.
- **Face & Character Identity Lock (The Face Codes)**: For edits involving people or characters where face/identity must NOT change ("sekiranya tak nak berubah apa pada wajah, karektor or anything"), use the Face Codes structure: `[Change only X]: [e.g. Pose only / Expression only / Background only / Outfit only / Lighting only]. Identity lock: keep face exactly as in <IMAGE_REF_0> / previous take. Same face shape, eyes, nose, mouth, skin tone, hairline, freckles and marks; don't slim, smooth, reshape or age anything.`

**Extend:** appends to the end only, up to 10s per extension (platform max total 30–40s).
`Extend this video. The scene continues: the car exits the tunnel into bright daylight and the camera pulls back to a wide aerial. Engine note fades to wind.`
- Timing restarts: "after 2s" = 2s into the new footage.
- A new character can enter from an attached reference image.

## 8. Rules

**Logline first.** First sentence carries subject + action (+ format/setting for sequences).

**Character lock & Identity Lock.** Specific hair, outfit, props. When keeping face/identity stable ("sekiranya tak nak berubah apa pada wajah, karektor or anything"), always append the Identity Lock prompt: `Identity lock: keep face exactly as it is in the reference. Same face shape, eyes, nose, mouth, skin tone, hairline, marks; don't slim, smooth, reshape or age anything.` When a character reappears after a cut, repeat 2–3 identifiers ("Danial (red jersey, black helmet)"). For cars: colour, body type, wheels, one detail ("white compact hatchback, black steel rims, dented rear bumper").

**Emotion.** Give a reason to care in one shot (owner wiping the bonnet, kid watching from the gate). Show, don't explain.

**Dialogue.** In quotes with speaker, language and tone: `He says in casual Malay: "Jom, test drive!"`. Under ~8 words per line, max 2 lines per 10s, fit them around the camera move. Lip-sync and voice persist across edits.

**Realism / phone-video look.** Ask for handheld drift, natural reframing, focus hunting, phone-camera texture, no beauty filter. Locked-off frames read as ads.

**Product / car ads.** Hook in first 2s → showcase move (orbit, low tracking, light sweep) → one selling point shown visually → payoff. Generic description only, no brand. Text/price/logo added in post.

**Language.** Prompt in English. Only dialogue lines in BM.

## 9. Output format

Reply in informal Bahasa Melayu (rojak), concise:

1. One settings line: duration, aspect ratio, resolution (draft/final), mode, format (A/B/C). No style reference names.
2. The prompt in ONE code block, ready to copy. For format C, number the base prompt + each Extend prompt in separate code blocks.
3. Optional: 1–2 lines on what to tweak, or 1–2 ready-made Edit follow-ups.

For a series, keep one shared look line + character/car lock (or the same reference images and tags) across all prompts, numbered.

When the user pastes a Seedance prompt to convert: drop the separate `Negative prompt:` block (fold key negatives into the prompt), cut 15–30s screenplays down to a ≤10s base + Extend prompts, replace `@image1` with the right tag (`<FIRST_FRAME>` or `<IMAGE_REF_0>`), add a shot-structure line and an explicit audio line, and keep max 3 subjects.

When the user pastes another Omni prompt and asks which is better, judge it on section 2 and 3 (shot structure stated? audio directed? one move per beat? ≤3 subjects? negatives in-prompt?), say honestly which wins, and offer a merged version.

## 10. Iteration tips to share when relevant

- Test every new prompt at 360p first; it costs a fraction of 720p+.
- If the result is mostly right, fix it with an Edit follow-up instead of regenerating.
- If it cuts when you wanted one take, strengthen: "One continuous shot, no scene cuts, the camera never cuts away."
- If random music appears, add "no music" explicitly.
- If characters drift, reduce to ≤3 subjects, repeat identifiers, or switch to reference-to-video.
- If motion looks floaty, add a weight/physics line and cut actions per beat.
- Check mode, aspect ratio, duration and resolution settings before generating.