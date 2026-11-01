# Colored Paper Diorama — Video Prompt System (vox-colored)

**/vox in color.** Identical to `guidelines/video-prompts.md` (same blocks, SHOT beats, camera
library, AUDIO table, sequencing rules); only the style and AVOID blocks below change so the
clip keeps the keyframe's hand-tinted color. The video model (Nexabot `sfv`, Veo) gets the
keyframe as the exact first frame. Four blocks in order: **STYLE BLOCK → SHOT → AUDIO → AVOID**.

---

## 1. Style Blocks (choose per clip)

### A. Flat Parallax (restrained data beats)

> The provided image is the exact first frame: animate from it, keeping its vintage hand-tinted collage materials — colorized photo cutouts with white keylines and red offset strokes, aged paper, newsprint, archival maps, torn labels, palette and print grain. Layers sit at distinct depths like a paper diorama — true parallax, never glossy 3D. Motion: spring pop-ups with overshoot, staggered entrances, underline swipes; one slow camera move per clip. Audio: sound design only — paper pops, thwips, stamps, ticks, low newsroom hum. No music. No voice-over.

### B. Deep Diorama (reveals, cinematic, camera-as-actor)

> The provided image is the exact first frame: animate from it, keeping its vintage hand-tinted collage materials — colorized photo cutouts with white keylines and red offset strokes, aged paper, newsprint, archival maps, torn labels, palette and print grain. Do NOT flatten it: every clip is a deep 3D paper diorama — cutouts are physical layers separated in real space, strong shallow depth of field, foreground elements crossing close to the lens. The camera is an actor: it flies between layers, orbits, dives, whips, racks focus — one committed cinematic move per clip. Motion: springs with overshoot, staggered entrances. Audio: sound design only — paper pops, whooshes, stamps, ticks. No music. No voice-over.

---

## 2. SHOT, camera, escalation, AUDIO, sequencing

Use `guidelines/video-prompts.md` sections 2, 3 and 6 unchanged, with two rules learned on
Nexabot/Veo:
- **Describe beats literally, never by a capitalised beat name.** Veo paints capitalised prompt
  words into the frame ("ALERT WASH"). Write "the whole background floods to hot red in one
  beat", once per video, on the biggest beat.
- **Keep text still.** Words and numbers already in the frame must not be covered, moved or
  re-drawn; Veo garbles text in motion. Animate the objects around them.

---

## 3. AVOID (verbatim, matching block)

### For A (Flat Parallax)

> AVOID: no glossy CG 3D, no lens flares, no camera cuts within the clip, no black-and-white conversion (keep the hand-tinted color), no modern saturated neon color, no warped or gibberish text, no extra words or numbers appearing, no invented logos, no watermarks, no simultaneous entrances, no music, no soundtrack, no voice-over, no narration, no lyrics

### For B (Deep Diorama)

> AVOID: no flat single-plane composition, no static locked-off camera, no glossy plastic CG (depth stays papercraft), no black-and-white conversion (keep the hand-tinted color), no modern saturated neon color, no warped or gibberish text, no extra words or numbers appearing, no invented logos, no watermarks, no music, no soundtrack, no voice-over, no narration, no lyrics

Add `no UI or glass elements` when the shot involves screens, dashboards or tech.
