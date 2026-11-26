# Writing MAGI-2 prompts

Sources (read 2026-11-26):
- Sand.ai, "MAGI-2: A 480B Frontier Video Generation Model" - sand.ai/blog/magi-2
- SandAI-org/MAGI-2-preview README and its prompt-enhancer system prompts
  (`inference/prompt_enhancement/prompts/t2v.md`, `i2v.md`) - github.com/SandAI-org/MAGI-2-preview
- Higgsfield, "Best Ways to Access MAGI-2" - higgsfield.ai/blog/best-ways-to-access-magi-2
- Third-party guides summarising the same rewriter (imagera.ai, flyaigh.com, pixeldojo.ai) - used only
  where they quote Sand.ai's files.

## Why prompts must be long
Sand.ai: "The captions the model was trained on are long and structured, so a short hand-written
prompt underuses it." Their pipeline rewrites every idea into a structured caption before the video
model sees it. On Higgsfield, `enhance_prompt: true` does that step for you; with it off (repo
default, so the shot stays as written) the prompt must carry that structure itself.

## Structure (in this order)
1. **Overview** - one paragraph, about 35-85 words: subject, place, time, light, overall mood.
2. **Subject** - who/what, with one or two fixed details (coat colour, hairstyle, product shape).
   Use the same wording for the same subject every time; name it, don't paraphrase it later.
3. **Timeline** - timed beats that cover the whole clip with no gaps:
   `0-4s: ...`, `4-9s: ...`. One continuous take = one segment; a cut clip = 2-6 segments
   (say whether each cut is hard or on an action). Roughly one beat per 5 s on long clips.
4. **Camera** - one framing and one camera path per segment (static, slow dolly-in, side tracking,
   handheld). Never stack opposing moves ("orbit while zooming in and out").
5. **Light** - a physical source, direction and colour temperature ("warm tungsten lamp from the
   left"), not "epic cinematic lighting".
6. **References note** (only with reference media) - say what each reference is for: "the woman is
   the person in the first image; the room is the second image; follow the rhythm of the audio".
7. **Audio** - last, on its own line, starting `Audio:`.

## Timing that reads (from Sand.ai's rewriter)
- reaction or simple reveal: ~1.2-1.7 s
- simple gesture / short object move: ~1.5-2.2 s
- pickup, handoff, jump, throw, spin, vehicle move: ~2.0-3.5 s
- readable on-screen text: at least 1.0 s, nearly still
A "single take" only stays single if its actions fit at natural speed; otherwise plan cuts.

## Wording rules
- Plain, simple English. Describe only what is visible in the final video.
- **No negation** inside the description ("no people", "without text"). Write what *is* there.
  Exclusions go in the Audio line ("no music") or are left out entirely.
- Keep spoken lines and on-screen text in their original language, in double quotes, copied exactly.
  On-screen text sits on a front-facing surface.

## Audio line
`Audio: "<exact line>" (who says it); <2-3 named sounds tied to visible events>; <music genre + mood | no music>.`
- Quote every spoken line; unquoted paraphrase gives mumbled speech.
- Tie SFX to things that happen on screen (a door slam, a landing).
- If you leave out music/silence, the model invents a soundtrack. Write `no music` or `Audio: silent.`
- Adding your own music later? Set `generate_audio: false` - same price.

## Risky content (keep these simple)
Sand.ai's rewriter simplifies a segment when it holds: several places or times, more than two active
people in the foreground, many hand/body/object contacts, fast running/fighting/dancing, detailed
hands and faces, damage or transformation, cloth, hair, liquid, smoke, fire, glass and reflections,
moving readable text, crowds. For those: one main action, one active person, static camera or
constant-speed side tracking, fixed lens/focus/light, beats one after another.
Unspecified look defaults to a natural documentary photo, 35-50 mm feel for people, 65-85 mm for
hands and small objects, moderate depth of field, one broad soft light, neutral white balance.

## Per mode
- **Start frame (i2v):** describe what is already in the image, then one action that starts from its
  pose. A prompt describing a different scene will repaint the image. Keep the camera calm.
- **Start + end frame:** pick two images with the same setting, light and character; describe the
  action that gets from A to B.
- **References:** clean, consistent sets beat many mixed ones (e.g. 4 angles of one outfit + a few
  location plates), and say in the prompt what each reference is.

## Template
```
<Overview paragraph, 35-85 words.>
Subject: <name> - <fixed details>.
0-<t1>s: <framing>, <camera move>. <action>.
<t1>-<t2>s: <hard cut | cut on action> to <framing>. <action>.
Light: <source, direction, colour temperature>.
Audio: "<line>" (<speaker>); <sfx 1>; <sfx 2>; <music genre + mood | no music>.
```

## Example (8 s, 9:16, one continuous take)
```
A rainy night street market in Kuala Lumpur. Wet asphalt mirrors red and amber lanterns while a
street cook works a flaming wok under a canvas awning. Steam rises past hanging bulbs and a few
shoppers pass behind him, soft and out of focus. The mood is warm, busy and close.
Subject: the cook - a middle-aged man in a white apron and a black cap.
0-3s: medium shot at eye level, slow dolly-in past the lanterns. Flames burst up from the wok and
light his face.
3-8s: the dolly-in continues to a close-up of the wok. He tosses the noodles high, catches them and
the steam rolls toward the lens.
Light: orange wok fire from below, warm tungsten bulbs from above, cool blue rain light behind.
Audio: wok sizzle and roaring gas flame; metal spatula clanging on the wok; light rain dripping from
the awning; no music.
```
