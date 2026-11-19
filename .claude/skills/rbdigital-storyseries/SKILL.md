---
name: "rbdigital-storyseries"
description: "Make long cartoon, explainer, documentary or drama videos from AI scene clips (30 styles, cartoon to realistic, with Explainer/Dokumentari/Drama presets): writes VO script, character sheet and scene-by-scene image + 10s video prompts, then edits the uploaded clips with VO, SFX, captions and music into an MP4. Use when the user wants a cartoon, documentary or drama story video built scene by scene."
---

# Toon Series Video

The toon-explainer trick, done by hand: lock a style + character sheet, make ONE clean image per scene, animate each image with a short safe-motion AI clip (Flow / Gemini / Seedance, max 10s), then Claude assembles everything: cuts to the VO, punch-ins, crossfades, captions, music, SFX.

Two phases:
- **Phase 1 (prompt pack):** Claude writes the VO script, character sheet prompts and per-scene prompts. the user generates.
- **Phase 2 (assembly):** the user uploads the clips (plus their VO MP3 and any free library SFX). Claude identifies the scenes, generates VO with ElevenLabs if needed, makes free procedural SFX, edits and renders the MP4.

Reply in the user's language (default: informal Bahasa Melayu / rojak when they write in Malay), concise. Prompts are in English.

## Setup: Python (check once per chat, esp. Claude Code on a Windows PC)
Scripts here need Python 3 + numpy and ffmpeg. Check: `python --version` (or `py --version`) and `python -c "import numpy"`.
- **Windows:** `python3` usually doesn't exist and plain `python` may be a Microsoft Store stub → use `python` (or `py`) in every command below where it says `python3`. Missing → install it yourself, don't skip steps:
  ```powershell
  winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
  python -m pip install numpy
  ```
  The current shell won't see the new PATH → call `"$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"` (Git Bash: `"$LOCALAPPDATA/Programs/Python/Python312/python.exe"`) or ask them to reopen Claude Code. No `--break-system-packages` on Windows. ffmpeg missing → `winget install -e --id Gyan.FFmpeg --scope user`. If winget fails, ask them to install Python from python.org (tick "Add python.exe to PATH") and wait.
- Linux/Mac sandbox: `pip install numpy --break-system-packages -q` if an import fails.

## 0. Settle inputs (one short question max)

Needed: topic, duration, aspect ratio (16:9 YouTube / 9:16 TikTok), **style (1-30 from the menu below)**, and the **genre preset** (Explainer default, Dokumentari or Drama — section 1b) when the topic makes it unclear. Defaults if not said: 1 minute, 16:9. VO via the ElevenLabs connector when connected (Claude generates it); otherwise Claude gives the script and the user generates the MP3.

**Style:** if the user did not name a style, show the 30-style menu as a numbered text list (name + one short line each) and ask them to pick, together with any other missing input, in ONE message. Add your top 2-3 picks for the topic first (e.g. "untuk sains kanak-kanak aku cadang 1, 12 atau 18", "untuk dokumentari sejarah aku cadang 22, 23 atau 19", "untuk drama aku cadang 26, 21 atau 29"). If they say "ikut kau" or doesn't answer, use the first recommendation and say which one.

Scene count, 10s clips (the user's default, Flow/Gemini max is 10s):
- 30s = 3 scenes + 1 optional = 4
- 1 min = 6 scenes + 1 backup = 7
- 2 min = 12-13, 3 min = 18-20
- each scene carries ~2 VO sentences (~8-10s of speech)

## 1. Style menu (30 styles)

Each style has a STYLE LOCK (pasted word for word into every image prompt and the character sheet), a short tag used in the video prompt, and a motion note. Replace `[palette]` with 5 colors that fit the topic. Never add artist, studio, film or brand names to any style.

| # | Style | Best for |
|---|---|---|
| 1 | Flat 2D Kartun | general explainer, sains, sejarah ringan |
| 2 | 3D Family Film | cerita emosi, iklan premium |
| 3 | Kartun Klasik Vintage | lucu, nostalgia, hook TikTok |
| 4 | Vector Explainer Moden | bisnes, kewangan, takaful, SaaS |
| 5 | Komik | aksi, drama, sejarah perang |
| 6 | Anime | remaja, motivasi, cerita |
| 7 | Watercolor Storybook | cerita lembut, kisah nabi/moral |
| 8 | Buku Cerita Kanak-kanak | prasekolah, 3M, lagu |
| 9 | Paper Cut Craft | kanak-kanak, DIY, cerita rakyat |
| 10 | Claymation | lucu, produk, kanak-kanak |
| 11 | Pixel Art | gaming, tech, retro |
| 12 | Chibi Kawaii | kanak-kanak, comel, social media |
| 13 | Lukisan Minyak | sejarah, sirah, dokumentari klasik |
| 14 | Ink Wash (Dakwat) | falsafah, sejarah Asia, puisi |
| 15 | Doodle Whiteboard | tutorial, konsep, cikgu |
| 16 | Retro Synthwave 80s | tech, muzik, hype |
| 17 | Noir Grafik | misteri, jenayah, thriller |
| 18 | Felt Fabric | kanak-kanak, cerita tidur, lagu, 3M |
| 19 | Cinematic Digital Painting | dokumentari, sejarah epik |
| 20 | Batik Nusantara | cerita rakyat Melayu, budaya, Merdeka |
| 21 | Sinematik Realistik | drama, iklan premium, kisah benar |
| 22 | Arkib Dokumentari | sejarah, Merdeka, biografi |
| 23 | Reenactment Sejarah | dokumentari sejarah, sirah, tamadun |
| 24 | True Crime Misteri | misteri, kes, thriller |
| 25 | Nature Documentary | sains alam, haiwan, alam sekitar |
| 26 | Drama Keluarga Melayu | drama, motivasi, kisah sedih, Raya |
| 27 | Isometric 3D Explainer | tech, bisnes, proses kerja, SaaS |
| 28 | Painted Motion Comic | aksi, legenda, drama epik |
| 29 | Filem Retro 70an-80an | nostalgia, kisah lama, drama retro |
| 30 | Seram Kampung | cerita seram, misteri kampung, urban legend |

Categories when showing the menu: KARTUN & ILUSTRASI 1-12, 15, 18 · SENI & BUDAYA 7, 9, 13, 14, 20 · GAYA RETRO 3, 11, 16, 29 · DOKUMENTARI 19, 22, 23, 25 · DRAMA & REALISTIK 21, 24, 26, 28, 30 · BISNES & TECH 4, 15, 27. Show it as one numbered list (name + one short line), grouped under these headings.

**STYLE LOCKS**

1. Flat 2D Kartun: `Clean flat 2D cartoon illustration, bold black outlines, flat cel shading with soft single-tone shadows, [palette], simple expressive faces, tidy uncluttered composition.` Tag: flat 2D cartoon. Motion: normal.
2. 3D Family Film: `3D animated family-film look, soft subsurface skin, rounded friendly shapes, rich golden-hour lighting, volumetric light rays, shallow depth of field, cinematic color grade, [palette], detailed but clean environments.` Tag: 3D animated film. Motion: smooth, cinematic.
3. Kartun Klasik Vintage: `Vintage 1930s rubber-hose cartoon, black and white with a warm sepia tint, pie-cut eyes, white gloves, bouncy bendy limbs, hand-inked lines, slight film grain and gentle flicker, simple painted backgrounds.` Tag: vintage rubber-hose cartoon. Motion: bouncy, squash and stretch, small rhythmic bobbing.
4. Vector Explainer Moden: `Modern flat vector explainer illustration, no outlines, clean geometric shapes, subtle gradients, [palette], friendly minimal characters with simple faces, generous negative space, corporate infographic feel.` Tag: flat vector explainer. Motion: clean, minimal; elements gently slide or pop in place.
5. Komik: `Bold comic book illustration, thick black ink lines, halftone dot shading, dramatic shadows, saturated [palette], dynamic angles, panel-like framing, speech-bubble-free.` Tag: comic book. Motion: punchy camera push, small dramatic gestures.
6. Anime: `Japanese TV anime cel style, crisp clean lineart, large expressive eyes, soft cel shading with sharp highlights, painted detailed backgrounds, [palette], bright skies.` Tag: anime. Motion: hair and clothes in wind, blinks, sparkles.
7. Watercolor Storybook: `Soft watercolor storybook illustration, gentle wet-edge washes, visible paper texture, light pencil outlines, warm muted [palette], dreamy soft light.` Tag: watercolor storybook. Motion: very gentle, slow drift.
8. Buku Cerita Kanak-kanak: `Children's picture book illustration, gouache and colored pencil texture, chunky rounded characters with big heads and dot eyes, bright cheerful [palette], simple cozy backgrounds.` Tag: children's picture book. Motion: gentle bounces, happy small gestures.
9. Paper Cut Craft: `Layered paper cut craft illustration, cut paper shapes with soft drop shadows between layers, visible paper fibers, [palette], handmade diorama feel, shallow depth.` Tag: layered paper craft. Motion: layers shift with parallax, slight paper wobble.
10. Claymation: `Stop-motion claymation look, handmade plasticine characters with visible fingerprints and soft clay texture, miniature set, warm soft studio lighting, [palette], shallow depth of field.` Tag: claymation stop-motion. Motion: slightly stepped stop-motion feel, small hops and nods.
11. Pixel Art: `16-bit pixel art, crisp square pixels, limited [palette], retro game scene, simple sprite characters, clean tile-based background.` Tag: 16-bit pixel art. Motion: sprite-like idle bobbing, twinkling pixels; keep pixels crisp.
12. Chibi Kawaii: `Cute chibi kawaii illustration, tiny bodies with oversized heads, huge sparkly eyes, rosy cheeks, soft pastel [palette], rounded shapes, little sparkles and hearts.` Tag: chibi kawaii. Motion: bouncy, blinks, sparkles.
13. Lukisan Minyak: `Classical oil painting, rich textured brushstrokes, dramatic chiaroscuro lighting, deep warm [palette], museum fine-art feel, painterly backgrounds.` Tag: oil painting. Motion: slow push-ins, flickering light, drifting smoke.
14. Ink Wash: `East Asian ink wash painting, flowing black ink brushstrokes, soft gray washes, large empty rice-paper space, a single accent color, calm poetic mood.` Tag: ink wash painting. Motion: mist drifting, ink-like slow flow.
15. Doodle Whiteboard: `Hand-drawn whiteboard doodle, black marker lines on clean white background, a few color marker accents ([palette]), simple stick-style characters and icons, sketchy friendly lines.` Tag: whiteboard doodle. Motion: minimal; lines wiggle slightly, elements pop in.
16. Retro Synthwave 80s: `Retro 1980s synthwave illustration, neon pink and cyan glow, purple sunset gradient, grid horizon, chrome highlights, VHS scanlines, dark night sky with stars.` Tag: retro synthwave. Motion: neon flicker, grid scrolling, glow pulses.
17. Noir Grafik: `High-contrast graphic noir illustration, stark black and white with heavy shadows, one accent color ([accent]), rain and fog, venetian-blind light, moody detective atmosphere.` Tag: graphic noir. Motion: rain, slow light sweeps, smoke.
18. Felt Fabric: `Handmade felt fabric craft look, soft fuzzy felt textures with visible fibers, neat stitched edges and tiny button details, rounded simple characters with embroidered faces, cozy [palette], miniature felt diorama set, soft warm studio lighting, shallow depth of field.` Tag: felt fabric stop-motion. Motion: gentle stop-motion feel, soft fabric wobble, small hops and head tilts; keep fibers and stitches visible.
19. Cinematic Digital Painting: `Cinematic semi-realistic digital painting, epic wide compositions, atmospheric haze and god rays, detailed environments, painterly finish, [palette], documentary storytelling mood.` Tag: cinematic digital painting. Motion: slow epic camera moves, drifting dust and clouds.
20. Batik Nusantara: `Malay Nusantara batik-inspired illustration, flowing wax-resist line patterns, floral and wave motifs filling backgrounds, rich [palette] (indigo, soga brown, maroon, gold, cream), elegant stylized characters in traditional dress.` Tag: batik-inspired illustration. Motion: gentle, patterns subtly flow, cloth sways.
21. Sinematik Realistik: `Photorealistic cinematic film still, natural skin texture, anamorphic lens look, shallow depth of field with soft bokeh, motivated practical lighting, subtle film grain, teal-and-amber cinematic color grade, [palette] accents, real-world Malaysian locations and props.` Tag: photorealistic cinematic. Motion: slow, grounded camera moves; natural micro-movements only (breathing, blinks, small head turns).
22. Arkib Dokumentari: `Vintage archival documentary photograph, black and white or faded sepia, heavy film grain, soft focus edges, dust and scratches, slightly uneven exposure, period-accurate clothing and objects, candid unposed composition, mid-20th-century press photo feel.` Tag: archival documentary photo. Motion: mostly still; slow Ken Burns pan or push-in, flickering grain, a tiny far-away movement (flag, smoke, water) at most.
23. Reenactment Sejarah: `Realistic historical reenactment film still, period-accurate costumes, props and architecture, desaturated earthy [palette], soft overcast or candle/torch light, atmospheric haze, documentary-drama cinematography, faces partly in shadow or turned away.` Tag: historical reenactment. Motion: slow push-in or slow pan; torch flicker, smoke and dust drift, cloth sways; characters stay mostly in place.
24. True Crime Misteri: `Dark realistic true-crime documentary still, cold teal and gray grade with one warm accent ([accent]), low-key lighting, deep shadows, rain-wet surfaces, evidence-style close-ups (papers with no readable writing, photographs, a desk lamp), tense quiet atmosphere.` Tag: dark true-crime documentary. Motion: very slow push-in, light flicker, rain, slow rack focus; no sudden action.
25. Nature Documentary: `Wildlife nature documentary photograph, ultra-detailed natural textures, telephoto or macro lens, shallow depth of field, golden-hour or soft morning light, lush tropical rainforest and coastal environments, [palette], calm majestic mood.` Tag: nature documentary. Motion: slow glide or slow push; leaves sway, water ripples, insects or birds make small natural movements, mist drifts.
26. Drama Keluarga Melayu: `Warm realistic Malay family drama film still, cozy home interiors (kampung house or terrace house), soft window light and warm tungsten lamps, gentle bokeh, natural skin tones, emotional close-ups, modest everyday clothing (baju kurung, baju Melayu, t-shirts, tudung), [palette].` Tag: warm realistic family drama. Motion: slow push-in on faces, tears welling, soft smile, glance away, curtain or steam drifting.
27. Isometric 3D Explainer: `Clean isometric 3D illustration, soft clay-like render, rounded miniature objects and buildings on floating tiles, soft global illumination with gentle shadows, pastel [palette], tidy diagram-like layout, small simple characters.` Tag: isometric 3D render. Motion: elements pop up or slide on the grid, small gears turn, tiny characters bob; camera static or slow orbit up to 30 degrees max.
28. Painted Motion Comic: `Painted graphic novel illustration, dramatic brush-painted shading over ink lines, cinematic panel compositions, strong rim light, textured paper grain, moody saturated [palette], heroic dynamic poses held still.` Tag: painted graphic novel. Motion: parallax-like slow push, cloak and hair in wind, sparks or embers drift, eyes narrow; pose stays held.
29. Filem Retro 70an-80an: `1970s-80s retro film still, warm faded film stock colors, strong grain, light leaks and soft halation, period interiors and fashion (bell-bottoms, patterned shirts, vintage cars without logos, old radios and TVs with blank screens), slightly soft focus, [palette].` Tag: retro 70s film. Motion: gentle handheld sway or slow zoom, light leak flicker, curtain sways or steam drifts from a kettle.
30. Seram Kampung: `Dark atmospheric Malaysian folk-horror film still, kampung at night, wooden stilt houses, banana trees and coconut palms, thick ground mist, cold moonlight with a single warm oil-lamp glow, deep shadows, desaturated green-blue [palette], eerie quiet mood, any figure only as a distant silhouette.` Tag: Malaysian folk horror. Motion: very slow push-in, mist creeping, lamp flame flickering, leaves rustling, a distant silhouette barely shifting; no jump-scare motion.

If the user asks for a style not in the list, write a new STYLE LOCK in the same shape (render look + line + shading + palette + mood) and use it.

**Realistic styles (21-26, 29, 30) extra rules:** people drift more than cartoons between clips, so the character sheet is mandatory for any recurring person and every scene prompt repeats 3 identifiers (hair, outfit color, one accessory). Prefer medium and wide shots, back/side views and faces partly in shadow; keep close-ups to 1-2 per video. No lip-sync: characters never speak to camera on screen (dialogue is VO over a reaction shot, a back/side view or an object). Real historical figures and public figures appear only as generic unnamed figures (silhouette, from behind, far away), never a recognizable real face.

## 1b. Genre presets (pick with the style)

**Explainer (default):** what the rest of this skill describes — friendly VO, captions every sentence, cheerful or soft music, punch-ins.

**Dokumentari:**
- Script: cold open hook question → context → 3-5 chapters (each opens with a date/place) → reflection → closing line. Narrator tone, calm, factual, hedged numbers ("lebih kurang", "dipercayai").
- Voice: deeper narrator (Daud M / Zain or another deep Malay voice), slower pace (~2 words/s), longer pauses between chapters.
- Visuals: more wide/establishing scenes; insert 1 "map/date card" per chapter (Claude makes it in code: dark card, place + year in serif, small map outline) — no image prompt needed.
- Edit: slower (one shot per scene unless > 9s), 0.6s crossfades, slow push-ins; lower-third for place/year at chapter starts (Poppins regular, small, bottom-left); captions optional (ask once; default on, smaller).
- Sound: ambience-first (wind, city, rain, crowd far), minimal music (drone or soft piano, gain ~0.08), one low boom on chapter cards.

**Drama:**
- Script: hook moment → setup → conflict → turning point → emotional peak → resolution or cliffhanger (for a series, end each episode on a cliffhanger line).
- Voice: narrator + up to 2 character voices (ElevenLabs, different voices, same flow); dialogue lines short (≤ 8 words); write who speaks in the script as `NARATOR:`, `AMINAH:`, `AYAH:`.
- Visuals: alternate wide (where) → medium (who) → close-up/reaction (feeling); a speaking character is shown from the side/back or the listener's reaction is shown instead (no lip-sync).
- Edit: cut on the emotional word, 0.3s crossfades, hold 0.5-1s of silence before the peak line, slow push-in on the peak reaction.
- Sound: emotional music (minor piano/strings bed, gain ~0.12-0.15, swells at peak), room tone/ambience per location, mute music for 1-2s right before the peak.

## 2. Hard rules for all prompts

- No brand names, no copyrighted characters, no real artists/studios, no "in the style of X". Describe visual traits only. Characters get original names.
- Signs, screens, walls with writing: "no letters or words" (hieroglyph-like symbols are fine).
- Character sheets come first when there's a recurring character.
- Max 1-2 characters per scene. Crowds go far and small. Hands relaxed or out of frame. No hands picking up/giving small objects.
- Every image prompt repeats the chosen STYLE LOCK word for word.

## 3. Phase 1 output (prompt pack)

Send in this order:

**a) Settings line:** aspect, number of scenes x 10s, style number + name, genre preset, character name(s).

**b) STYLE LOCK** of the chosen style with the palette filled in.

**c) Character sheet prompt** (one code block per character):
```
Character turnaround model sheet of [NAME], [age], [build], [skin], [hair], [outfit with colors], [signature prop]. Front view, 3/4 view, side view and back view full body, plus 3 facial expression close-ups: [3 emotions the story needs]. [STYLE LOCK]. Plain solid white background, no scenery, no ground shadows, even soft studio lighting, generous spacing between views, no overlapping poses. Same character, identical design in every view. 16:9. No text, no labels, no watermark, no logos, no extra characters.
```
Always add one line: background is plain white so the cut-out comes out clean. Say which scenes need the sheet attached. (For Doodle Whiteboard the background is white anyway; for Synthwave/Noir still use plain white for the sheet.)

**d) Per scene** `### sNN` with:
1. VO lines (BM, the 2 sentences this scene covers)
2. Image prompt (code block):
```
[If character: Use the attached character sheet as the exact reference for NAME; preserve face, hair, outfit and colors exactly.] [SHOT: wide / medium / close-up / low-angle / aerial] of [subject + simple pose] in [location, 3-4 key props]. [Light / time of day]. [STYLE LOCK]. [aspect]. [No text, no watermark, no logos.]
```
3. Video prompt, 10s, short (code block). Structure: anchor + ONE camera move + TWO small motions in sequence + the style's motion note + stability negatives:
```
Use @image1 as the exact anchor, keep the same [style tag] style, face, outfit and composition. [Slow push-in / slow pull-out / slow pan left|right / slow tilt up / slow crane up / slow drone glide / static locked-off]. [Small motion 1], then [small motion 2]. [Style motion note]. Stable background, keep face identity stable, same number of people, no style change, no morphing, no warping, no extra limbs, no new characters, no text.
```

Safe motions: blink, eyes shift, small nod, soft smile, head turn toward camera, shoulders rise with a breath, sigh and lean back, cloth/hair in wind, water ripples, leaves sway, dust drifts, flames flicker, clouds drift, light sweep/gleam, tiny far-away figures move slightly.
Avoid: walking far, running, hands grabbing/giving objects, eating, writing, 3+ characters moving, full body spins, 360 orbit around a character. A big action = two images (before / after) cut together.

**e) Upload instructions:** name files `s01.mp4 ... sNN.mp4`. If a scene fails, skip it and say which number (Claude replaces it with the still image + code zoom). Upload the character sheet too.

**f) Free SFX list (optional):** a short table of 3-6 specific sounds the procedural presets cannot make (scene, what to search in English, length), e.g. `s01 | "rooster crowing distant village morning" | 10s`. Tell the user to download them from Pixabay Sound Effects (first choice), Freesound (CC0 filter) or Mixkit and upload them with the clips. Say that skipping this is fine: Claude will use procedural sounds instead (wind, rain, room tone, city hum, crowd, crickets, boom, whoosh, chime, film crackle).

## 4. Phase 2: assembly

Work in the scratchpad: `clips/`, `sfx/`, `scripts/`. Make a task list.

### 4a. Identify clips
Uploads usually come with random names. Copy them to `clips/`, make a labeled contact sheet (3-4 frames per clip, `drawtext` the index), read it, map to scenes, rename to `sNN.mp4`. Check fps/size/duration with ffprobe. Note any defects (extra people appearing, face drift, melting, style change) and the second they start.

### 4b. VO (ElevenLabs connector)
If no ElevenLabs connector is in this session (or the user prefers to generate it), give the whole VO script in ONE code block (one sentence per paragraph, light audio tags like `[excited]`; for Drama mark each line with the speaker), tell them to paste it into ElevenLabs (model Eleven v3, any Malay voice they like; one voice per speaker for Drama), download the MP3(s) and upload, then continue from step 5 with their file. Otherwise:
1. `creative_create_flow` (name: "VO <topic>").
2. `creative_list_voices` languages=["ms"], use_cases narrative_story / informative_educational. Default voice: **Rizal – Youthful Malay Storyteller** (`T1mr7V3bcaBm2vQhsxFG`), model `eleven_v4` (if the workspace doesn't offer it, use `eleven_v3`; check with `creative_get_flow_node_types`). Say which voice was used. If a named voice ID isn't available in the user's workspace, pick the closest Malay voice from `creative_list_voices` instead. (For Noir/Komik/Cinematic, Dokumentari and styles 22-24, 30 use a deeper voice such as Daud M or Zain. For Drama, generate each character's lines with its own voice in the same flow and join them in script order with the pauses from the script.)
3. Whole script in ONE generation, one sentence per paragraph (blank line between). Generate with **generations_count=1** (fewer generations = lower cost).
4. Poll `creative_get_flow_run_status`; download `content_url` with curl to `vo.mp3`.
5. Timing: `ffmpeg -i vo.mp3 -af silencedetect=noise=-35dB:d=0.3 -f null -`. Pauses >= ~0.45-0.55s are sentence ends; shorter ones are commas. Count must match the sentence count; map each sentence to start (silence_end) / end (silence_start). Group sentences into scenes. If there are more pauses than sentences (the narrator also paused at commas or colons), match segments to sentences by length: Malay narration runs about 6 syllables per second (numbers spoken in full: 1925 = 14 syllables), so add up segment durations until they fit each sentence. Split a long caption at the matching syllable fraction.

### 4c. SFX (free only: procedural + free libraries, never ElevenLabs)
No paid SFX generation. Two free sources:

1. **Procedural (Claude makes these, always available, ffmpeg only):**
   `python3 <skill>/scripts/sfx_gen.py <preset> sfx/<name>.wav <seconds>` (`--list` shows presets).
   Presets: `wind, rain, room, city, crowd_far, waves, fire, crackle, projector, crickets, tick, heartbeat, boom, whoosh, chime, drone`.
   Use them for beds and texture (wind, rain, room tone, city hum, film crackle, crickets) and simple hits (boom on chapter cards, whoosh on cuts, chime on the key word). Beds 10-15s with `loop: true` in the plan; hits 2-4s.
2. **Free libraries (for specific real sounds: rooster, cheering crowd, frying, birds, a car, a market):** the user downloads them (list given in Phase 1, section 3e) and uploads them with the clips. Sources:
   - **Pixabay Sound Effects**: free, commercial use OK, no credit needed (first choice).
   - **Freesound.org**: filter licence to **CC0** only (CC-BY needs a credit line in the video description).
   - **Mixkit**: free SFX licence, good for short hits and transitions.
   - Avoid BBC Sound Effects for monetized channels (non-commercial licence), and any file with music or speech inside.

Rules:
- Copy uploaded library files to `sfx/` with clear names (`rooster.mp3`, `crowd_cheer.mp3`). Trim leading silence (`silenceremove=start_periods=1:start_threshold=-50dB`) and keep the best 8-15s.
- If the user uploads no library sounds, build the whole mix from procedural presets and say which scenes a library sound would improve.
- ~4-5 sounds per 30s, ~8-10 per minute: one ambience per location group + 1-3 accent hits. Add a quiet `projector` or `crackle` bed across the whole video for archival / retro styles (22, 23, 29), gain ~0.25.
- Level-match every file (procedural presets come out between about -20 and -45 dB): measure `mean_volume` with volumedetect and set `gain = 10^((target-mean)/20)`, targets ambience about -32 dB, accents about -26 dB, archival texture about -40 dB. The bed sits ~8-10 dB under the VO (VO mean is usually about -22 dB). Use `"sfx_gain": 1.0` in the plan once each file is level-matched.
- In the report, list each library sound with its source and licence so the user can credit it if needed.

### 4d. Music
If the user uploads a track, use it (gain ~0.12). Otherwise generate a soft procedural bed: `python3 <skill>/scripts/music.py music.wav <seconds>` (edit the scale/drone/tempo lines first if needed: swap the scale/drone and tempo to fit the style: pentatonic major + faster beat for kids/cheerful, Phrygian dominant for Middle East history, minor for noir/drama) and say it is a placeholder. `music.py` needs numpy; if it is missing, use `python3 <skill>/scripts/sfx_gen.py drone music.wav <seconds>` (ffmpeg only) for a dark documentary/drama drone, gain ~0.2-0.25. Free music sources the user can download: Pixabay Music and the YouTube Audio Library.

### 4e. Shot plan (making 10s clips feel faster)
Scene duration comes from the VO (next scene starts 0.15s before its first word). Per scene pick 1-3 shots from the same clip:
- <= 5s: one shot, `from: 0.1`.
- 5-9s: two shots: wide `{from:0.1}` then a later part `{from:~5}`; if the clip has no camera move of its own, make the second a punch-in `{zoom:1.3, cx, cy}` aimed at the face/subject.
- > 9s or 9:16: three shots (wide, punch-in on face, punch-in on detail).
- cx/cy = crop position 0-1. To center a target at (tx,ty): `cx = (tx - 1/(2z)) / (1 - 1/z)`, clamp 0-1.
- Avoid clip time after a noted defect. If the clip is too short, add `speed: 0.9` or the script freezes the last frame.
- For 9:16 from 16:9 clips, use zoom >= 1.78 crops (cx chooses the subject).

### 4f. Build
Write `plan.json` and run `python3 <skill>/scripts/toon_build.py plan.json` (`<skill>` = this skill's folder; it's bundled, don't rewrite it). Captions: one per sentence, split long sentences at a comma pause (Poppins bold, white with dark outline, bottom), numbers written as digits where natural (146 meter, 4,000 tahun).

Fonts: copy the caption and lower-third `.ttf` files into `<workdir>/fonts/` (the script passes that folder to libass). If Poppins is not installed, use a bold sans the system has (e.g. Arial bold on Windows) and set `cap_font`. Use a forward-slash absolute `workdir` (`C:/Users/...` on Windows).

Optional keys: `xfade` (0.3 default; 0.6 for Dokumentari), `cap_font`, `cap_size` (58 default; ~50 for Dokumentari), `lt_font` (Georgia default), `lower_thirds` (place/year text, top-left, serif, for Dokumentari chapter starts).

```json
{"workdir": "/abs/path", "size": [1920,1080], "fps": 24, "total": 26.8, "xfade": 0.3,
 "cap_font": "Poppins", "cap_size": 58,
 "vo": "vo.mp3", "music": "music.wav", "music_gain": 0.12, "sfx_gain": 1.0,
 "output": "Topic_16x9.mp4",
 "scenes": [{"clip": "clips/s01.mp4", "start": 0.05, "end": 5.81,
   "captions": [{"text": "...", "start": 0.05, "end": 3.23}, {"text": "...", "start": 3.76, "end": 5.81}],
   "shots": [{"from": 0.1}, {"from": 5.0, "zoom": 1.3, "cx": 0.5, "cy": 0.4}]}],
 "lower_thirds": [{"text": "1925 · Alor Setar", "start": 0.4, "end": 4.5}],
 "sfx": [{"file": "sfx/wind.wav", "start": 0, "end": 6.2, "gain": 0.6, "loop": true},
         {"file": "sfx/chime.wav", "start": 4.6, "end": 7.0, "gain": 0.8}]}
```
`total` = VO length + ~1.5s tail.

### 4g. Check, deliver, report
- Contact sheet every 1.5-3s: caption matches picture, punch-ins aimed right, no black frames. volumedetect on the final: mean about -20 dB, peak under -1 dB.
- QA gates: `python3 <skill>/scripts/look.py <final>.mp4 --expect-duration <s> --audio --sheet qa.jpg` → every gate PASS: decodes, right size/length, audio present, no frozen run > 0.4 s mid-video (deliberate pauses: `--allow-still <t>`), end hold ≤ 1.5 s. FAIL = fix and re-render, don't deliver. Look at `qa.jpg` (frames from the real MP4). Quote the numbers in one line of the summary. Dokumentari slow push-ins still count as motion; a planned freeze-frame → `--allow-still <t>`.
- Send the MP4 with SendUserFile.
- Report: style used, which voice, defects noticed (and the fix prompt if a scene should be regenerated), which SFX were procedural and which came from libraries (source + licence), and **ElevenLabs credits used for VO only** (with USD; zero if the user made the VO). SFX cost nothing. This connector does not show the balance, so point to the ElevenLabs dashboard.



## Lessons from past builds
- Tamadun Mesir (15 x 5s): worked well; model once added an extra person mid-clip, so keep "same number of people, no new characters".
- Fotosintesis (4 x 10s, 30s): clips with their own push-in/crane needed few punch-ins; using the later part of the clip as shot 2 was enough. VO 6 sentences = 25s.
- SFX levels vary a lot (from about -15 to -45 dB): always level-match before mixing.
- Kisah Tun Mahathir (7 x 10s, Dokumentari, style 22): the VO ran 80s instead of 60s, so scenes became 11-16s. Shot plans of 2-3 shots per clip plus `speed: 0.6-0.85` covered it without visible freezes. One clip had blurry split panels for its first 6s; a `zoom: 1.9` centre crop hid them. For a real public figure, back/side/far views worked and no face appeared.
- On Windows: plain `python` may be a Store stub (try `~/.local/bin/python.exe`), numpy may be missing (`sfx_gen.py` and `toon_build.py` need only ffmpeg + stdlib), and `alimiter` must use `level=false` or the final peak hits 0 dB.
- One VO take (generations_count=1) was good enough both times, and pause detection mapped all sentences cleanly.
