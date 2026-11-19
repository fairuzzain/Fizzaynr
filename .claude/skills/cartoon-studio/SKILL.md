---
name: cartoon-studio
description: Make a vertical 2.5D animated short (flat 2D cartoon characters standing inside lit 3D Blender sets) that tells one true story from history or science in about 65 seconds. Use for /cartoon-studio, "2.5D short", "kartun 2.5D", "cartoon about a true story", "history short like Ricks Clips", or any request for a 55-70 s animated true-story episode.
---

# Cartoon Studio: 2.5D true-story shorts

Format studied from the Ricks Clips bronze-jar short (27M views in 8 days) and the
"2.5D motion studio" course by @Y0urDumble (x.com/Y0urDumble/status/2115164938884862375).
Take the grammar of the format, never its characters, designs or scripts.

Before starting, read `references/house-rules.md` (the format) and `references/prompts.md`
(the prompts for each step). Project folder: `${RUNS_DIR:-$ROOT/runs}/<Project Title>\`.

## Fizz's rules that override the course

| Course says | Here |
|---|---|
| Record your own voice | VO by project language: English via Nexabot TTS, Malay via `gemini_tts.py`. History/science = **Fenrir** locked for the whole episode (state it in the storyboard). |
| Word-timed captions on screen | **No captions** unless Fizz asks. Whisper still runs, but only to time cuts and SFX to words. |
| Any SFX / music source | SFX: openverse-sfx (check `${SFX_DIR:-$ROOT/assets/sfx}/` first) -> real-sfx -> earshot critique. Music: Nexabot `music`. |
| Render and ship | Storyboard sheet of Blender stills + shot list, **wait for "approved"** before animating and rendering. |
| Upload | QA gates 1-4, then Drive sync: `AI VIDEO/<MMM YYYY>/<Project Title>`; revisions in `Editted-<DDMMYYYY>`. |
| CPU render | Render on the GPU: Cycles with OptiX (RTX A2000) or EEVEE; ffmpeg `h264_nvenc`. |
| English only | Language of Fizz's title locks script, VO and every on-screen word. Malay = Malaysian Malay, no rojak; write e pepet as ë in TTS text. |

## Setup notes (checked 9 Nov 2026)
- Blender 5.2.3 at `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`; the MCP addon starts with it.
  Never call `read_factory_settings` through the MCP: it unloads the addon and drops the connection
  (restart Blender). Clear a scene by deleting objects instead.
- Only engine id on 5.2 is `BLENDER_EEVEE` (EEVEE Next renamed). Cycles for finals on OptiX.
- Poly Haven / Sketchfab libraries are **off** in the addon: turn them on in Blender's N panel > MCP before `search_assets`.
- `scripts/cutout_rig.py` tested: parts stand at true height, Locked Track (yaw only) keeps them upright,
  contact shadow sits at z 0.015 so rugs don't hide it. Test render: `Downloads\Video Ai\Cartoon Studio Test\review\still_test5.png`.

## Pipeline (stop where it says WAIT)

1. **Pitch** 5 true stories, each with 2 sources Fizz can open. WAIT for the pick.
2. **Script** `script.md` (150-170 words, hook in line 1, twist near 40 s, last line pays off the hook) + `sources.md` (a source for every claim). WAIT for OK. Fizz checks the sources.
3. **Shot list** `shotlist.md`: one shot per idea, 1.5-3 s each, 3-5 reusable sets, hero prop marked. Key beats written in **global frames at 30 fps** (a 30 cm fall = 7-8 frames).
4. **VO** generated now (locked voice), then `whisper vo.wav --model small --word_timestamps True --output_format json` -> retime the shot list to the words.
5. **Sets** in Blender through the MCP: BLOCK (grey shapes + every camera) -> LIGHT (one motivated key, warm practicals, Poly Haven HDRI fill, no 3-point studio) -> DRESS (worn materials, props, DoF on the character's mark). `look` after every pass.
6. **Hero prop** built in 3D, real scale, bevelled, wear in crevices, 6-angle look sheet before it goes in a set.
7. **Characters** as separate SVG parts (round head, body, arms, legs, costume) + expression parts (eyes: neutral, wide, narrow, closed, side-look; mouth: closed, small open, wide open, frown, grin; sweat drop, blush). Flat colour, one thick dark outline, no gradients. PNG at 2x -> image planes with an **emission/shadeless** material (set lights never shade them) + a soft contact shadow under the feet. Use `scripts/cutout_rig.py`.
8. **Storyboard**: render one still per shot at 1080x1920, tile into a contact sheet, present sheet + shot list + voice choice in an artifact. **WAIT for approval.**
9. **Acting line** per shot (thought, anticipation 4 frames before anything moves, action on the stressed word, 10-frame hold). No idle bounce. Mouths swap only on stressed words; no lip-sync when nobody speaks on screen.
10. **Animate and render** at exactly 1080x1920, 30 fps. Fix renders by frame range only (`blender -b ep.blend -o //review/fix_ -s A -e B -a`).
11. **Sound**: cue list in the same frame numbers (only physical events get a sound, no whoosh more than twice, music resolves on the last frame); place with real-sfx (`--voice-safe`), music ducked under VO; earshot `critique` the mix.
12. **Review loop**: contact sheet (`fps=1,scale=240:-1,tile=8x9`) + phone sheet (`fps=1/3,scale=360:-1,tile=6x4`). Critic pass with `references/prompts.md#critic`. Fix the 3 worst, re-render only those frames, repeat. Fix order: wrong/missing -> readability -> timing -> detail.
13. **Deliver**: ffprobe must show 1080x1920, 30/1, the planned duration. Outro hold 2-3 s, fade to black 1.5-2 s, audio fade 2-3 s. Run video-qa-auditor Gate 4, then Drive sync.

## Folder per episode
`script.md  sources.md  shotlist.md  cues.md  vo.wav  vo.json  sets/ chars/ review/ out/episode.mp4`
This folder is the template for the next episode.

## Corrections format
Every fix gets four fields: WHERE (global frames), PROBLEM, CHANGE, KEEP. See `references/prompts.md#revision`.

## Platform
Original episodes only (YouTube targets mass-produced repetitive content). Animation is normally exempt
from the AI label; label anything that could pass for real footage. One wrong date costs more than any render.
