---
name: "queen-marigold-omni"
description: "Use when the user gives a topic for a Queen Marigold video and wants a Gemini Omni Flash 1.1 prompt (not Seedance): deadpan Tudor queen selfie vlog, base take + Extend prompts."
---

# Queen Marigold: Tudor Selfie Vlog (Gemini Omni Flash 1.1)

The user gives only a TOPIC (e.g. "tukar tayar", "traffic jam", "floral season"). Claude turns it into a copy-ready Gemini Omni Flash 1.1 prompt starring the recurring character Queen Marigold: a 16th-century English queen who films her "day off" on a front-facing phone camera as if it were normal modern content, speaking dry, deadpan, regal ENGLISH.

Sister series to Lady Seraphine (loud, gossipy) and Madame Grimelda (chaotic, cackling). Marigold is the opposite: calm, blunt, bored, confident, unbothered. The comedy is flat delivery about absurd royal life and modern topics.

Do not ask questions. Pick the funniest angle yourself and go. Use this skill instead of queen-marigold-vlog whenever the user says Omni, Omni Flash, Gemini Omni or Omni 1.1.

## 0. Hard rules

- ALL of Marigold's dialogue is in English, even if the topic is given in Malay. No Malay in her lines.
- She is an ORIGINAL character. Never a real monarch's name, never "a real queen", never "in the style of" anyone.
- No real historical or living person's name anywhere. Invent names ("the Duke of Somewhere", "Sir Kit", "Sir Bertram"). Say "the kingdom", never a real country tied to a real figure.
- No brand, product, car-maker, app, shop, show, film or character names anywhere in the reply. Describe generically. Omni also blocks real brands and recognizable people.
- If the user pastes an old transcript or idea containing real names, keep the joke and staging, swap every name for an invented one, and say so in one line.
- The prompt is in English.
- The CHARACTER LOCK and VOICE LINE below are copied VERBATIM into every base prompt so she looks and sounds the same across the series.

## 1. Locked blocks (copy verbatim)

```
Queen Marigold: woman in her 40s, cracked chalk-white face paint with faint freckles, thin pale arched eyebrows, small bright-red lips, slightly darkened sugar-stained teeth, tight copper-red curled heart-shaped wig with a small pearl-and-dark-stone crescent headpiece and sheer black veil, huge stiff white lace cartwheel ruff, red-and-gold brocade gown with an embroidered bodice and puffed pearl-trimmed sleeves, long ropes of pearls, large jewelled rings including a big ruby ring. She holds the phone herself at arm's length, slightly below eye level and tilted up, her puffed sleeve at the bottom-left of frame, chest-up framing with the full ruff visible.
```

```
She speaks low and unhurried in a crisp, refined upper-class English accent, short blunt sentences, no contractions, completely deadpan, never raising her voice, looking straight into the lens like talking to a friend she slightly pities.
```

Look line (use in every base prompt, adapt the light to the location):

```
Photorealistic front-phone-camera selfie vlog, phone wide lens, handheld micro-shake, natural reframing, slight focus hunting, mild wide-lens distortion, no beauty filter, authentic 16th-century Tudor details.
```

Optional wardrobe swaps (state them in the action, keep face paint, wig and ruff): dark riding cloak for outdoor/travel; heavy gold crown for "official duty"; servants' white-gloved hands entering frame with a letter, goblet or tray of sweets.

**Companions (never named after real people):** a quiet lady-in-waiting in a dark gown and white coif, or only her white-gloved hand; an oarsman or coachman in red-and-gold livery seen in a brief pan. Max 3 tracked subjects total, Marigold included. Prefer gloved hands or a brief pan over full extra characters.

**Signature props:** sugared almond or marzipan held to the lens before she eats it; plain gold ring held up for "I am already married. To the kingdom."; sealed suitor letter.

## 2. Her voice

Short declarative lines, formal grammar, no contractions, zero hype. Dramatic things said flatly, mundane things said like state matters.

**Backbone rhythm:** set-up fact, tiny pause, then a ONE-OR-TWO-WORD verdict. "Letters, gifts, he even sent his brother. Too keen." / "Married my sister, then asked me. No."

**Running bits (1–2 per video, rotate across the series):**
- Opener: "Good morrow, my sweet peasants." + "Day off today."
- Modern-word confusion: "Vlog. Is that the word?", "Subscribe. Is that a threat?"
- "Very royal." as a flat verdict on anything ordinary.
- Sweet tooth: "Do not tell my physician."
- Suitor roll-call with micro-verdicts; one pet name ("I call him my frog. He is small. I like him.").
- Forbidden name: "We do not talk about Sir Kit." then "Row, please."
- Gold ring to lens: "I am already married. To the kingdom."
- "Okay. Where were we." after an interruption.
- "My ladies showed me something... Very educational."
- Sign-off: "Follow your queen. That is an order."

**Exactly ONE modern slang slip per 10–15s video**, said just as flatly, as the punchline: "red flag", "that is the ick", "it is giving peasant", "no cap", "main character energy", "he is not the one", "rent free", "lowkey". Long reels: max two across all clips.

Vocabulary: "the kingdom", "my subjects", "my sweet peasants", "the court", "my physician", "my ladies", "treason" for tiny offences, "most tiresome", "acceptable", "very royal", "no".

**Omni dialogue rules:** each line under ~8 words; max 2–3 short lines per 10s; put each line in quotes inside the Audio paragraph; tie lines to triggers ("When she lifts the letter: ...") rather than exact timestamps.

## 3. Creative engine

The comedy is the CLASH between modern vlog culture and her Tudor world, played straight.

1. **Translate the topic:** car → royal coach or horse; fuel price → price of hay and oats; traffic jam → coach stuck behind a turnip cart; mechanic → royal farrier; GPS → nervous courtier with a map; speeding ticket → scroll from her own guards ("I am the law. Dismissed."); road trip → royal progress; car wash → servants with buckets. Invent fresh ones.
2. **Vlog formats said flatly:** day-off vlog, ranking, what I eat in a day, review, storytime, Q&A, rate my ride, letter-as-DM, show-and-tell to the lens.
3. **One small escalation** (interruption, pothole spills sweets, ugly suitor gift, slow oarsman) answered with a slow blink or flat stare.
4. **Verdict + sign-off:** flat rating, tease, smirk, she lowers the phone and the recording cuts off.

## 4. Locations (pick 1 per generation; vary across the series)

Sunny estate garden with stone fountain, hedges, pink roses, red-brick manor; candlelit wood-panelled banquet room with fruit, nuts and marzipan sculptures; small rowing boat on a willow-lined river with a liveried oarsman; sunlit portrait hallway with a lady-in-waiting trailing; shadowy throne room with a carved wooden chair; red velvet coach interior bumping along a country road; stone courtyard with horses and grooms; torchlit corridor; private chamber with canopy bed.

One location per generation. Change location in a new generation or a palm-over-lens transition, not mid-take.

## 5. Omni behaviours to write around

- **Multi-shot by default:** always write `One continuous selfie shot, no scene cuts, no third-person angles.` She is always filming herself; only a brief pan to a companion or the place is allowed.
- **Audio is invented unless directed:** always write an Audio paragraph with SFX, ambience, her dialogue, and `No music.` (or a named soft lute/recorder sting at the end only).
- **Timing ranges are budgets:** 2–4 beats per 10s, one action per beat. Triggers ("When she...") land better than timestamps.
- **Physics line:** stiff ruff and heavy pearls swing with her steps, brocade weight, plus any bump, horse, boat or prop.
- **No negative-prompt field:** end with `No on-screen text, no captions, no logos, no phone visible in frame.`
- **Duration, aspect ratio and resolution are SETTINGS**, never prompt text. Default 9:16, draft 360p, final 720p/1080p.

## 6. Prompt structure

Default: **10s base (format B) + 1 Extend (~5s)** for a 15s video.

```
[Logline: front-facing selfie vlog, Queen Marigold does X like a modern vlogger, in [location detail]]. [Look line, with light for the location].

[CHARACTER LOCK verbatim]. [Companion line if any: e.g. "A lady-in-waiting appears only as a white-gloved hand."]

[0-3s] [hook action + signature expression].
[3-6s] [one action, often an object held up to the lens].
[6-10s] [escalation + slow blink or flat stare].

One continuous selfie shot, no scene cuts, no third-person angles. [Physics line].
Audio: [concrete ambience + SFX]. [VOICE LINE verbatim] "[line 1]" Then: "[line 2]" When [trigger]: "[line 3]" No music.
No on-screen text, no captions, no logos, no phone visible in frame.
```

Extend:

```
Extend this video. The scene continues in the same selfie shot: [verdict gesture: wrist flick, smirk, close lean-in]. She says flatly in the same crisp English accent: "[verdict]. [slang slip]." She then lowers the phone and the recording cuts off. Audio: [SFX], a short soft lute sting at the end. Keep her face paint, wig, ruff, gown and pearls exactly the same.
```

Rules:
- Every video has at least one lens interaction (object to lens, too-close lean-in, or palm-over-lens), one signature expression (slow blink, smirk, raised eyebrow, lean-in) and one gesture (wrist flick, eating a sweet, showing an object, tapping pearls).
- Keep the base prompt around 150–220 words; don't overload beats.
- Short 8s version: 3 beats, verdict and slang inside the base, no Extend.

### Long "day off" reel (30–40s per chain, or separate generations)

Arc across clips: garden opener → banquet snack break ("Do not tell my physician.") → portrait hallway list with micro-verdicts → river boat ("The roads are terrible. So, boat.", forbidden name, "Row, please.") → throne room (pet-name suitor, gold ring, "married to the kingdom") → closer (modern twist, tease, "Follow your queen. That is an order.").

- Omni Extend tops out around 30–40s total, so for reels beyond that write each location as its own 10s base generation, repeating the look line and CHARACTER LOCK verbatim in every one (or use the same reference image).
- Transitions: each clip ends with her palm sliding over the lens (frame goes dark); each next clip opens with her palm pulling away to reveal the new location. Write both into the prompts.
- Sign-off only in the last clip.

## 7. Reference image option

If the user has a Marigold image, attach it before the first generation and replace the CHARACTER LOCK with:
`Queen Marigold from <IMAGE_REF_0>: her face paint, lips, teeth, wig, headpiece, ruff, gown, pearls and rings come from <IMAGE_REF_0> unchanged. She holds the phone herself at arm's length, slightly below eye level, her sleeve at the bottom-left of frame, chest-up framing.`
If using it as the opening still instead, use `<FIRST_FRAME>` and describe only what moves.

If he has no image and wants one, give an image prompt: Queen Marigold with the CHARACTER LOCK, front-facing selfie framing, sunny estate garden by a stone fountain and pink roses, plain clean light.

## 8. Edit follow-ups

Offer 1–2 one-change edits when useful, e.g.:
- `Make her delivery even flatter and slower. Keep everything else the same.`
- `Keep all character details and motion exactly as they are, only remove the background music.`
- If it cuts away: add `the camera never cuts away` to the base.

Max ~4 edits per chain, then regenerate with the reference image.

## 9. Output format

Reply in informal Bahasa Melayu (rojak), short; the prompts and all her dialogue stay in English:

1. One line: the angle picked + settings (base 10s + Extend, 9:16, draft 360p → final 720p/1080p, text-to-video or reference).
2. Numbered code blocks: 1. Base, 2. Extend (more for a reel).
3. Optional: one tweak or alternative angle line.

For a series, number each video and keep the locked blocks identical.

Before sending, scan for any brand, title or real-person name and remove it, and check none of her lines contain Malay.