---
name: scenario-kinetic-film
description: Use when someone wants a fast, high-energy launch film, game teaser, trailer, product promo or brand film in kinetic typography, the style of viral motion design reels (huge words on every beat, whip pans, colour flips, 3D letters the camera flies through, a hard drop), for their own product, game or brand. Builds the film as code (one web page, a pure function of time, assembled from scene blocks on the music's beat grid), renders it at 1080p or 4K with motion blur, bloom and grain, and checks every frame for dynamism, size and playback. Scenario MCP makes what code cannot draw or play, chosen with recommend and priced with a dry run - the soundtrack (a music bed at an exact tempo and a sound-effect kit) and any key art, product shots or screenshots the film shows. Keywords - kinetic type, motion graphics in code, launch video, teaser, trailer, beat sync, whip pan, motion blur, 4K render, music to picture, sound design.
---

# Kinetic launch films in code, scored and illustrated with Scenario MCP

## Overview

A film here is a spec: a list of scene blocks placed on the beat grid of its music, plus a palette, a
caption track and a logo. The engine turns it into one web page where every frame is a pure function of
time, so a renderer can seek anywhere and average sub-frames into real motion blur. Nothing in the motion
is generated: no warping, no flicker, every word is exactly the word you wrote, and changing one colour
rebrands the whole film.

Scenario MCP brings what code cannot: the **music** (generated at the exact tempo the beat grid needs),
the **sound-effect kit** (whooshes, impacts, key clicks, a custom sound for the gag), and the **pictures**
(key art, a product, a character) that the Picture block cuts in. "Just code" (52 s, type only, 4K, on the
Explorations page) is built from these blocks; `examples/kaiju-postal` is a worked example from a fresh
brief (a 24 s game teaser whose music, sound kit and key art were generated through Scenario MCP).

What makes it read as professional motion design rather than a slideshow is measured, not guessed:
the references this style comes from keep under a quarter of their frames still and never hold a shot
longer than about 0.4 to 0.7 s. `finish.py` measures the same numbers on every render and fails a film
that parks.

Needs: Node 18 or newer with Playwright (`npm install playwright` in the film folder; `npx playwright
install chromium` if Google Chrome is not installed), ffmpeg and ffprobe, Python 3 with `numpy` and
`opencv-python-headless`. Scenario MCP for the sound and pictures: connection and the generation loop
are in the `scenario` skill if installed, otherwise [references/scenario-mcp.md](references/scenario-mcp.md).

## Quick reference

`$K` is this skill's folder.

```bash
sh $K/scripts/new_film.sh my-film starter        # engine + an editable spec.js + fonts + audio/ folder
cd my-film && npm install playwright             # once per folder
python3 -m http.server 5671                       # preview: http://127.0.0.1:5671  (space plays, arrows step one beat)
node $K/scripts/snap.mjs stills 0.5 b4 b12 b20    # stills at beats (or seconds) to look at
python3 $K/scripts/beat_grid.py audio/music.mp3 --bpm 172 --window 40   # tempo, downbeat offset, drops
python3 $K/scripts/mix.py .                       # the soundtrack, from the film's own cue list -> out/mix.wav
python3 $K/scripts/render.py . --res 1080         # check render; workers sized to the machine's memory
python3 $K/scripts/finish.py . --video out/video_1080.mp4 --audio out/mix.wav   # deliverables + every check
python3 $K/scripts/render.py . --res 4k && python3 $K/scripts/finish.py . --video out/video_4k.mp4 --audio out/mix.wav
```

| Rule | Why |
| --- | --- |
| Everything is in beats: blocks, shots, captions, cues. `B(k)` = k beats in seconds | cuts land on the music; one tempo change retimes the film |
| One idea per beat or half beat; one or two words, filling the frame width | the references change something every 0.3 to 0.7 s |
| No still stretch over 0.6 s before the end card | `finish.py` fails it; a parked frame reads as a slideshow |
| Transitions are moves: `whipIn`/`whipOut`, a zoom through a letter, a collapse to a point | fades are the tell of template motion |
| Flip the ground (`bg`, `accent`, `paper`) on phrase changes | colour rhythm carries as much energy as cuts |
| A pure function of `t`: no `Math.random`, `Date` or state between frames | motion blur renders sub-frames out of order |
| 4K masters: H.264 Level 5.2 at most, under 1 GB, checked on the hardware decoder | above 5.2 QuickTime and phones refuse the file |
| On-screen numbers come from the film (`{lines}`, `{frames}`, `{seconds}`) or the user, never invented | a launch film's claims get checked |

| Scenario MCP step | Calls |
| --- | --- |
| Connect, choose team and project | `teams_list` (ask the user when there are several) |
| Choose a model | `recommend` (`txt2audio` for music and sounds, `txt2img` or `img2img` for pictures) |
| Read its inputs | `model_schema_get` |
| Price, then run after the user's go | `model_run` with `dry_run: true`, then `model_run` and `jobs_wait` |
| Fetch the result | `asset_download`, then `curl -L -o` |

## How a film is built

1. **Brief to beat sheet.** Length, tempo, the phrases, one block per phrase, where the drop lands, how it
   ends. Method and energy targets: [references/method.md](references/method.md). For a film made "like
   this reference", measure the reference first (`rectify2.py` flattens a filmed screen, `dyn.py` and
   `holds.py` measure it) and put its numbers next to yours.
2. **Sound and pictures with Scenario MCP.** A music bed at the sheet's tempo, then a kit of about 15
   one-shot sounds, then any pictures. Prompts, durations, levels and the beat grid:
   [references/sound.md](references/sound.md).
3. **spec.js.** Blocks, palette, logo, captions, extra cues. Every block and option:
   [references/blocks.md](references/blocks.md). Motion rules that keep it looking designed:
   [references/craft.md](references/craft.md).
4. **Preview and stills.** Scrub in the browser; `snap.mjs` at the beats you care about; fix and repeat.
5. **Render and check.** A 1080p check render, `finish.py` (every gate must say `PASS`), then the 4K master
   and `finish.py` again. Render traps and encode rules: [references/render.md](references/render.md).

## Worked example: a game teaser (how Kaiju Postal was made)

Goal: a 24-second teaser for an indie game about a courier delivering mail in a city of giant monsters:
kinetic type on a 172 BPM drum and bass track, two pieces of key art cut in on the drop, a door-knock gag
on the beat cuts, the title card on the last hit.

1. **Connect.** `teams_list`. If several teams or projects come back, ask which one to use and pass its
   `team_id` and `project_id` to every later call.

2. **Write the beat sheet (local, free).** 68 beats at 172 BPM (23.7 s): beats 0-8 type (a charge, then
   THE CITY / HAS NEW / VERY BIG NEIGHBOURS. / THEY STOMP.), 8-16 key art 1 on the drop, 16-24 type
   ending in a zoom through the D of DELIVER., 24-32 key art 2, 32-43 a fly-through (DODGE THE BIG FEET.),
   43-51 the 3D title YOU ARE THE POST., 51-57 the knock gag, 57-68 the title card.

3. **Music at an exact tempo.** `recommend`:

   ```json
   { "capability": "txt2audio", "prompt": "Instrumental drum and bass for a playful video game trailer at a fixed 172 BPM, a tense intro, then a huge drop, punchy kick on every downbeat, no vocals", "limit": 4 }
   ```

   Prefer a model whose schema has a tempo (`bpm`) input and an instrumental switch: a tempo you set beats a
   tempo you hope for. `model_schema_get`, then a dry run with the full parameters, for example:

   ```json
   { "model_id": "<id from recommend>", "dry_run": true, "parameters": { "prompt": "High-energy drum and bass for a playful video game trailer, 172 BPM. Eight bars of tense intro with filtered drums and a rising synth, then a huge drop: punchy kick on every downbeat, rolling breakbeats, growling reese bass, bright brass stabs. No vocals.", "instrumental": true, "duration": 40, "bpm": 172, "numOutputs": 2 } }
   ```

   Tell the user the price and wait for a go. Run, `jobs_wait`, `asset_download`, `curl -L -o audio/music_a.mp3 "<url>"`.
   Then measure each take:

   ```bash
   python3 $K/scripts/beat_grid.py audio/music_a.mp3 --bpm 172
   ```

   Pick the take with the clearest grid and the strongest drop (`drops[].rise`). In the build, take B held
   172.0 BPM with a drop at 10.74 s; the film starts on the downbeat 8 beats earlier
   (`music: { offset: 7.95, stopBeat: 58 }`), so the drop lands on the first key art and the music stops dead
   on the title.

4. **The sound kit.** `recommend` with `"capability": "txt2audio"` and "short isolated sound effects for
   motion graphics". One run per sound, short durations (each second costs), a negative prompt that keeps
   music and voices out, `"wait": false` for all of them, then one `jobs_wait` with every job id. The 12 core
   names and the prompts that worked are in [references/sound.md](references/sound.md); add custom sounds
   for the film's own jokes (here `stomp`, `roar`, `bell`, `knock`). Save them as `audio/sfx/<name>.wav`
   (variants `key_1.wav`, `key_2.wav` rotate).

5. **Key art.** `recommend` with `"capability": "txt2img"` and the art direction. Describe the composition,
   never ask for empty space: "a calm darker band for the title" was drawn as a literal grey band. Darken
   for type in the film instead (`tint`). For the second picture, pass the first as a reference image so the
   character and city match:

   ```json
   { "model_id": "<id from recommend>", "dry_run": true, "parameters": { "prompt": "Same game, same art style, same courier and same rainy neon city as the reference image. Close-up three-quarter shot of the courier on the yellow scooter, looking up with a determined grin; a puddle on the right reflects one enormous glowing monster eye. Stylized 3D, soft global illumination, crisp rim light.", "referenceImages": ["<asset id of picture 1>"], "aspectRatio": "16:9", "resolution": "2K", "numOutputs": 1 } }
   ```

   Download with `"format": "png"` into `art/`. Look at every picture at 100 %: generated vehicles and
   clothes carry real brand marks (the scooter came back with a maker's script logo). Remove them before the
   film uses the picture.

6. **spec.js.** Start from `examples/kaiju-postal/spec.js` or `examples/starter/spec.js`. An excerpt:

   ```js
   bpm: 172, beats: 68,
   palette: { bg: '#0B1020', paper: '#F3EEE3', accent: '#FFC21A', hot: '#FF8A1F', ink: '#14120E' },
   music: { file: 'audio/music.mp3', offset: 7.95, stopBeat: 58, gain: -7 },
   sounds: { stomp: -1, roar: -5, bell: -7, knock: -1, hit: 1 },
   cues: [[5.5, 'stomp'], [8.25, 'roar', .9], [24.6, 'bell']],
   scenes: [
     [Words, 0, 8, { charge: true, shots: [
       { at: 1, style: 'punch3d', text: 'THE CITY', fx: 'punch' },
       { at: 2, style: 'slam', text: 'HAS NEW', ground: 'accent' },
       { at: 3, style: 'stack', text: ['VERY BIG', 'NEIGHBOURS.'], ground: 'paper', in: 'whipX', fx: 'none' },
       { at: 5, style: 'split', text: ['THEY', 'STOMP.'], in: 'whipY', fx: 'punch', big: true } ] }],
     [Picture, 8, 16, { src: 'art/key1.png', weather: 'rain', words: [[1, 'MONSTERS'], [3, 'NEXT DOOR.', 'accent']], cutIns: [[5, 1.65, [.62, .2], 'stomp']] }],
     ...
   ```

7. **Preview, mix, check render.** Scrub the page, snap stills, then:

   ```bash
   python3 $K/scripts/mix.py .            # lists any hit quieter than the music: raise it in spec.sounds
   python3 $K/scripts/render.py . --res 1080
   python3 $K/scripts/finish.py . --video out/video_1080.mp4 --audio out/mix.wav
   ```

   In the build, the first check failed on two pictures that held for 1.5 s and 1.2 s; the Picture block
   now pushes, pans, punches in on every word, cuts in to a detail and draws weather over the image, and
   the teaser passed with 24 % still frames, no hold over 0.6 s and 12.5 cuts per 10 s.

8. **Master.** `render.py . --res 4k`, then `finish.py` on it: a 4K master under 1 GB, a 1080p version and a
   9:16 version (the film centred on black), each checked.

## Common mistakes

- **Matching the cut timing but parking between hits.** A film can land every cut on the reference's
  rhythm and still feel slow: the first version of "Just code" had 81 % still frames and a 6 s hold. Keep
  something moving every frame (camera drift, sliding type, ghost rows, particles); `finish.py` measures it.
- **Asking an image model for empty space.** "Leave a calm darker band for title text" came back as a grey
  rectangle across the picture. Describe the composition; darken for type with the Picture block's `tint`.
- **"No watermark" with a reference image.** The request was blocked as watermark removal (and still
  charged). Say "no text, no logos"; never mention watermarks when editing from a reference.
- **Real brand marks in generated pictures.** Scooters, cars, shoes and clothes come back with makers'
  logos. Inspect at 100 % and paint them out or regenerate.
- **Trusting a generated track's tempo.** Fit the grid on the stretch the film uses (`--window`), give the
  intended tempo (`--bpm`), and prefer a music model with a tempo input. A 0.15 % tempo error puts the last
  hits of a 50 s film 70 ms late.
- **Text that does not fit.** Blocks measure and scale words to the frame; custom code must too, and must
  measure once, while visible (a hidden element measures 0).
- **Reading `offsetLeft` inside a transformed parent.** It is relative to that parent, and a typing caret
  jumps back. Use `relPos` from blocks.js.
- **A nested film sharing state.** The Rewind block builds a second film from the same spec: never store
  per-film state on shared objects.
- **Headless capture traps.** A 1920x1080 viewport paints only about 990 px (use the 1300 px viewport in
  `browser.mjs`); a capture without `clip.scale` comes back at 1080p; big 3D layers come out half drawn
  without `--run-all-compositor-stages-before-draw`. The scripts handle all three.
- **Too many 4K workers.** Six filled 36 GB of memory and stalled the machine. `render.py` sizes workers to
  memory; do not override upward.
- **Clipping the shutter at a cut.** The fastest frame of every whip renders sharp. `render.mjs` slides the
  window back instead.
- **A slower preset without a level.** The file came out H.264 Level 6.0: it plays in ffmpeg and nowhere on
  a Mac. Keep `-level 5.2` at 4K; `finish.py` checks it on the hardware decoder.
- **`-shortest` when muxing.** It drops the last frames when the audio is a few milliseconds shorter.
- **Model ids or prices from memory, or a local path in `model_run`.** Choose with `recommend`, read
  `model_schema_get`, price with `dry_run` and wait for a go, upload files first.
- **Several teams and no question.** If `teams_list` returns more than one team or project, ask.
