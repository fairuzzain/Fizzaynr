---
name: sound
description: Separate audio pass for Edit Kit edits - SFX that land exactly on each visual impact frame at -17 dB, a very soft music bed under the voice, voice clean-up, AI voiceover, and the final -14 LUFS mix. Use after the picture is rendered, or when the user asks for sound effects, music, voiceover, "make the audio clean", "sync the SFX", or loudness. Never changes the picture.
---

# Sound Design

Audio is its own pass. The presets never touch audio; they only keep a `CUES` list of impact moments.

## Voice-only edits
Many creator videos want no music and no SFX. Then only clean and normalise the voice:
`ffmpeg -i clip.mp4 -vn -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 voice.wav`, mux with `finalize.py`.

## Editors who finish in Premiere
If the user will move or swap sounds themselves, hand over stems (voice, SFX, music as separate WAVs) plus
`cues.json` (every hit time) so each sound can be placed on its frame, along with the preview mix.

## Fixed mix (house rules)

| Layer | Level | Notes |
|---|---|---|
| Voice | **-14 LUFS**, -1.5 dBTP | always the loudest; cleaned (high-pass, de-noise, de-ess, gentle compression) |
| SFX | **peak -17 dBFS** each | under the voice, max one per 0.25 s, 3 variations per type so nothing repeats |
| Music | **24 dB under the voice** (≈ -38 LUFS), ducked further under speech | very soft; with no voice (pure motion) music sits at -20 LUFS |

## Sync rule: the sound hits ON the visual

Each cue time is the **impact frame**: the pop peaks, the card lands, the cursor presses, the wipe crosses centre,
the cut happens. Not when the animation starts. `sfx_music.py` measures every sound's transient and places it exactly
on that time; whooshes and risers start early by design and peak on the frame. `/qa` fails anything > 1 frame off.

| Cue | Use on |
|---|---|
| `pop` | key word pop, card/chip/icon pop, counter start |
| `click` | ticks, cursor clicks, checklist items, highlights |
| `whoosh` | punch-in cuts, zoom-throughs, 3D fly-ins, scene changes |
| `swipe` | strike-throughs, wipes, punch-outs, graph/line draw-on |
| `hit` | hero words, punchlines, flashes, logo landing |
| `shimmer` | stars, sheens, sparkles, logo orbit |

How many: **vertical** = SFX on every pop and cut; **horizontal** = only transitions and key reveals;
**SaaS** = every UI move, music carries the piece.

## Steps

1. **Cue sheet** `cues.json`: `[{"t": 2.4, "cue": "hit", "fx": "Generate click + ONE PROMPT"}, ...]` from the composition's CUES.
2. **SFX + music** (generated in code, no licences needed):
   `python3 scripts/sfx_music.py --cues cues.json --dur <s> --out audio/ --bpm 96 --mood warm|tech|calm`
   If the user has their own music (Epidemic, Artlist, YouTube Audio Library), use their file instead of `music_raw.wav`.
3. **Mix**:
   `python3 scripts/mix.py --voice clip.mp4 --start <src offset> --clean --music audio/music_raw.wav --sfx audio/sfx.wav --dur <s> --out audio/mix.wav`
   (an ElevenLabs/TTS voiceover: `--voice vo.wav` without `--clean`; pure motion: omit `--voice`).
4. Mux with `fx/scripts/finalize.py`, then `/qa`.

## Voiceover

- **User's ElevenLabs** (best): they export an MP3; transcribe it with `fx/scripts/words.py vo.mp3 --refine`
  and time the animation to its words.
- **Free local AI voice** (Kokoro): `npm i kokoro-js` once, then
  `node scripts/tts.mjs am_fenrir vo/ "line one" "line two" ...` and
  `python3 scripts/place_lines.py vo/line_*.wav --gaps 0.25,0.3,0.15,0.3,0.7,0.12 --dur 15 --out vo/vo_full.wav`
  (longer gap before the brand line so the logo reveal lands). `am_fenrir` = punchy ad voice, `am_michael` = deep.
- Never spend paid credits without the user's OK.

Check printed levels: voice ≈ -14 (a peak-limited voice may read -15, fine), sfx peak ≈ -17, music ≈ -38.
