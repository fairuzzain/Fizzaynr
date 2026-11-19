---
name: "lady-seraphine-vlog"
description: "Use when the user gives a topic for a Lady Seraphine video: a gossipy 18th-century court lady filming a front-facing selfie vlog. Writes a copy-ready Seedance 2.5 prompt."
---

# Lady Seraphine: Selfie Court Vlog (Seedance 2.5)

The user gives only a TOPIC (e.g. "tukar tayar", "traffic jam", "harga minyak naik", "review kereta baru"). Claude creatively turns it into one copy-ready Seedance 2.5 prompt starring the recurring character Lady Seraphine. She is an 18th-century palace lady who vlogs her life with a front-facing phone camera as if it were totally normal modern content, speaking in grand, aristocratic ENGLISH.

Do not ask questions. Pick the funniest angle on the topic yourself and go.

## 0. Hard rules

- ALL of Lady Seraphine's dialogue is in English. No Malay words in her lines, even if the user gives the topic in Malay.
- No brand, product, car-maker, app, shop, show, film or character names anywhere in the reply. Describe things generically ("small white hatchback", "black smartphone").
- No real historical person's name and no "in the style of". Lady Seraphine is an original character.
- The whole prompt is in English.
- The CHARACTER, PERSONA and PHONE STYLE blocks below are copied VERBATIM into every prompt, never paraphrased, so she looks and sounds the same across the series.

## 1. Locked blocks (copy verbatim)

```
CHARACTER (Lady Seraphine): woman in her late 20s, pale porcelain skin, bright blue-grey eyes, two round rose-pink rouge circles high on the cheeks, small black beauty mark under the left eye. Towering powdered grey pouf wig about 60 cm tall, rows of sausage curls on both sides, decorated with white ostrich plumes, pink-and-lavender striped satin bows and small pearls. Pale-blue silk brocade gown, square neckline trimmed with layered ivory lace, large pink-and-lavender striped bow with a pearl brooch at the bodice. Long white opera gloves. Maintain identical face, wig, rouge, gown and gloves throughout.

PERSONA & DELIVERY: haughty, theatrical, gossipy noblewoman who vlogs her life as if it were completely normal modern content. She speaks English in a refined, upper-class aristocratic accent with a slow, crisp, regal cadence, chin lifted, enunciating every word as if issuing a royal decree, then occasionally drops into a quick modern slang aside in a lower, gossipy voice. She looks directly into the lens like addressing her loyal subjects. Signature expressions: slow knowing wink, exaggerated eye-roll to the ceiling, pursed "ooh" lips, raised eyebrows, smug little closed-mouth smile, haughty chin lift. Signature gestures with the free gloved hand: raised index finger to make a point, limp-wrist flick, hand pressed to chest in mock shock, waving a white ostrich-feather fan.

PHONE STYLE: front-facing selfie, phone held at arm's length slightly below eye level and tilted up, her right arm and shoulder visible at the bottom-left edge of the frame. Framing chest-up, wig often cropped at the top of the frame. Natural handheld micro-shake, small reframing whenever she moves or gestures, phone-camera wide lens, sharp face, mild background distortion.
```

Optional wardrobe swaps (only when the topic needs it; state it in the beat and keep the face, wig and rouge identical): plain white linen morning robe with no wig powder for "bangun tidur" or behind-the-scenes topics; a maid's gloved hands entering the frame to pin her wig for "get ready with me" topics.

## 2. Her voice: aristocratic English

She talks like royalty addressing the court, not like a modern influencer. The comedy comes from her grand, old-fashioned English describing totally mundane modern things.

**Formula:** about 80% grand court English. Exactly ONE short modern slang slip per video (usually in the mishap or verdict beat), delivered as a quick aside, as the punchline. Never mix slang into every line.

**Vocabulary to draw from:**
- Address: "my loyal subjects", "my dearest peasants", "good people of the realm", "one" (instead of I), "we" (royal we)
- Openers: "Pray tell...", "Behold...", "I daresay...", "It is with great displeasure...", "Today, one shall review..."
- Grand words: dreadfully, frightfully, most vulgar, utterly ghastly, simply divine, scandalous, unbecoming, beneath one's station, insufferable, exquisite, a travesty
- Commands: "Summon the footman!", "Fetch my smelling salts!", "Off to the stables with it!", "Guards!"
- Verdicts: "We are not amused.", "One approves.", "A triumph for the crown.", "Ten carriages out of ten."
- Modern slip examples (pick one): "no cap", "it's giving peasant", "lowkey slay", "red flag", "the ick", "ate, no crumbs", "ten out of ten, would recommend", "don't forget to follow"

**Example lines:**
- "My loyal subjects, today one reviews the royal carriage."
- "Velvet seats, simply divine for the royal posterior."
- "That bump was frightfully vulgar. We are not amused."
- "One does not approve... but lowkey, it slaps."
- "Guards! Who dares cut ahead of my carriage?"

Dialogue rules: one line per beat, at most ~10 words (Seedance lip-sync drifts on long lines). In the prompt write the delivery cue each time, e.g. `She declares in a refined aristocratic English accent:` or for the slip `She drops her voice and adds in casual modern slang:`.

## 3. Creative engine: how to turn a topic into a video

The comedy always comes from the CLASH between modern influencer formats and her 18th-century royal world. For each topic:

1. **Translate the modern topic into her world.** Car becomes a horse carriage (the royal carriage); fuel becomes hay or oats; traffic jam becomes a line of carriages stuck at the palace gate; a mechanic becomes the royal stable boy; a GPS becomes a footman shouting directions; a car wash becomes servants with buckets; a speeding ticket becomes a royal guard waving a scroll; a road trip becomes a countryside carriage ride; a phone charger becomes a candle. Invent fresh ones for each topic.
2. **Use real influencer formats**, announced like a royal decree: review, unboxing, "get ready with me", "day in my life", storytime, "rate my ride", reacting to a sealed letter as if it were a DM.
3. **Build one escalating mishap** (wig too tall for the carriage door, horse eats her fan, bump wobbles the wig, guard interrupts), then her reaction face plus the single modern slang slip is the punchline.
4. **End with her royal verdict and a sign-off**: a decree-style rating, wink, finger raised, fan flutter, or she lowers the phone and the recording cuts off.

If the user's topic is already historical or not car-related, still keep the selfie-vlog format and find the modern-vs-old clash.

## 4. Locations (pick 1–3 per video, vary across the series)

Gilded mirror hall with painted ceiling and crystal chandeliers; candlelit dressing room with vanity and powder puffs; tufted pale-blue velvet carriage interior with countryside passing the window; palace stable with horses and straw; formal garden with hedges and fountain; cobblestone courtyard full of carriages; palace kitchen; grand staircase.

## 5. Prompt structure (default 15s, 9:16, text-to-video)

```
15-second realistic selfie-vlog comedy video set in [location(s)], where [premise in one sentence: Lady Seraphine does X like a modern influencer, narrated in grand aristocratic English].

STYLE: photorealistic, shot on a front phone camera, [lighting for the location], ornate 18th-century details. Handheld micro-shake, natural reframing, slight wide-lens distortion, focus stays on her face. Natural weight in head turns, wig sway and gown fabric[, plus physics for any bump, fall, horse or object]. No cinematic glamour, no stabilization, no text overlay.

[CHARACTER block verbatim]

[PERSONA & DELIVERY block verbatim]

[PHONE STYLE block verbatim]

0–3s — HOOK
[Selfie action + haughty chin lift or signature expression]. She declares in a refined aristocratic English accent: "[decree-style hook line]"
Sound: [concrete SFX].

3–7s — [BEAT TITLE]
[One action, camera stays selfie]. She declares: "[grand line]"
Sound: [...].

7–11s — [MISHAP / TWIST]
[Escalation + reaction face]. She declares: "[outraged grand line]"
Sound: [...].

11–15s — [ROYAL VERDICT]
[Verdict gesture, then she drops her voice for the slang aside, wink or fan, she lowers the phone and the recording cuts off]. She declares: "[grand verdict]" then drops her voice and adds in casual modern slang: "[one short slang slip]"
Sound: [SFX + soft harpsichord sting].

Negative prompt: blurry, low quality, distorted face, deformed hands or fingers, extra limbs, duplicated characters, changing wig or gown, rouge disappearing, phone visible in frame, frame flicker, background warping, text, subtitles, logos, brand names, watermark, choppy animation
```

Rules for the beats:
- 4 beats for 15s (3–4s each); 3 beats for 10s; for 30s, write 2 linked 15s prompts and repeat STYLE plus all locked blocks in both.
- Timestamps add up exactly to the duration.
- One action and one expression per beat. The camera is ALWAYS her own selfie; never cut to a third-person shot. Show movement by her walking, sitting or being jolted while she holds the phone.
- The slang slip can sit in the mishap beat instead of the verdict, but there is only one per video.
- Every beat has a `Sound:` line with concrete SFX (silk rustle, heels on marble, hooves, wooden wheels creaking, horse snort, fan swish, harpsichord sting).
- Include at least one signature expression (wink, eye-roll, "ooh" lips or chin lift) and one gloved-hand gesture in every video.

## 6. Image-to-video option

If the user has a reference image of Lady Seraphine, open the prompt with: `Use @image1 as the exact subject anchor. Preserve the exact face, wig, rouge, beauty mark, gown and gloves from @image1 throughout.` Then keep PERSONA and PHONE STYLE and the beats, but drop the long CHARACTER description. If he has no image yet and wants one, give an image prompt: Lady Seraphine with the CHARACTER description, front-facing selfie framing, on a plain light-grey background.

## 7. Output format

Reply to the user in informal Bahasa Melayu (rojak), short (only the reply is in Malay; the prompt and all of her dialogue stay in English):

1. One line: the angle you picked for the topic (the funny twist), plus settings (duration, 9:16, text-to-video).
2. The full prompt in ONE code block, ready to copy.
3. Optional: one line with an alternative angle or tweak (e.g. "kalau nak versi 30s, cakap je").

If the user asks for a series (e.g. 5 topics), number each prompt and keep the locked blocks identical in all of them.

Before sending, scan the reply for any brand, title or real-person name and remove it, and check that none of her dialogue lines contain Malay.