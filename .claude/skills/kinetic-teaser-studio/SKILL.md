---
name: kinetic-teaser-studio
description: Build a 10-40 s kinetic-typography teaser video in code for any subject (car, product, event, food, sport, game, brand), in Bahasa Melayu or any language, with a free code-synthesized soundtrack (phonk, trap, dnb, house, cinematic) and a 1080p MP4 render. Use when the user asks for a teaser, promo, launch film, hype video or kinetic type video. Do not use for talking-head edits or AI-generated footage.
---

# Kinetic Teaser Studio

A short, high-energy kinetic-type teaser: huge words on every beat, whip pans, colour flips, 3D type the camera flies through, and a hard drop. The film is one web page where every frame is a pure function of time. Headless Chromium renders it with motion blur, and `scripts/synth.py` makes the music and sound effects in numpy, so there are no paid services.

`$K` below is this skill's folder (the one containing this SKILL.md). Set it first:

```bash
K="$(cd "$(dirname "$(find ~/.codex/skills ~/.agents/skills .agents/skills -name SKILL.md -path '*kinetic-teaser-studio*' 2>/dev/null | head -1)")" && pwd)"; echo "$K"
```

## 0. Check the tools

```bash
node -v                      # 18 or newer
ffmpeg -version | head -1; ffprobe -version | head -1
python3 -c "import numpy, cv2, scipy; print('py ok')"
nproc; free -g 2>/dev/null || sysctl -n hw.memsize
```

Install anything missing: `pip install numpy opencv-python-headless scipy` (add `--break-system-packages` on Debian/Ubuntu system Python), and `npm install playwright` in the film folder, plus `npx playwright install chromium` if neither Chrome nor Chromium is installed.

## 1. The brief

Take these from the request or from an attached poster or brief. Ask only for things that are genuinely missing and matter; otherwise use the defaults.

| Item | Default |
| --- | --- |
| Subject, name / title | required |
| Length | 20 s |
| Genre and BPM | from the subject pack |
| Drop beat | 8 |
| Language | the user's language (Malay → Bahasa Melayu copy) |
| Palette | subject pack, or the brand / poster colours |
| On-screen facts (dates, venue, prices, specs) | only what the user gave; never invent numbers |
| End card | name + one-line tagline + a small line (AKAN DATANG, date, URL) |

When the user supplies a poster, copy the name, date, time, venue, URL and colours exactly as printed.

## 2. Beat math and structure

`beats = round(seconds * bpm / 60)`. Everything in `spec.js` is in beats. The music stops dead on the logo's first beat (`stop`). Here's the template for ~20 s at 140 BPM (47 beats); scale the spans proportionally for other lengths, keeping the drop on a multiple of 4 and the logo at least 6 beats long.

| Beats | Block | Job |
| --- | --- | --- |
| 0 → 8 | `Words`, `charge: true` | hook: punch3d, slam, stack, split, then two half-beat `cut`s into the drop |
| 8 → 16 | `Words` | THE DROP: `slam` with `fx: 'punch', big: true, cue: 'drop'` on beat 8, half-beat cuts, a `split`, exit `zoom` |
| 16 → 27 | `Fly` | camera flies through 3-5 words |
| 27 → 35 | `Hero` | kicker + NAME in 3D + sub line (the music's break) |
| 35 → 40 | `Words` | countdown / call-to-action cuts, `exit: { type: 'flash', at: 39.25 }` |
| 40 → 47 | `Logo` | wordmark, tagline, small line |

One idea per beat or half beat, one or two words per shot. Malay words run long: put long words in `split`/`stack` (they auto-fit), and keep `cut` words to 8 characters or fewer.

## 3. Subject packs (the user's words and colours win)

| Subject | Genre / BPM | Palette bg, paper, accent | `--extras` | Word ideas (BM) |
| --- | --- | --- | --- | --- |
| Car / motor | phonk 140 | #0A0A0C, #F1EEE8, #E8122B | rev,skid | HIDUPKAN ENJIN · PECUT · DERUM · TAYAR MENJERIT · TIADA BREK · TEKAN MINYAK |
| Product / gadget | house 124 / trap 140 | #0D0F14, #F2F0EA, #3D7BFF | ding,shutter | BARU · LEBIH NIPIS · LEBIH PANTAS · DAPATKAN SEKARANG |
| Event / career fair | cinematic 120 / house 124 | poster colours | crowd,ding | JOM HADIR · 2 HARI SAHAJA · DAFTAR SEKARANG + exact date/venue |
| Food / F&B | trap 140 / house 124 | #1A0F08, #FFF4E2, #FF8A1F | sizzle | PANAS · RANGUP · PEDAS · SEKALI RASA · PASTI KEMBALI |
| Sport / fitness | dnb 172 | #08110C, #EEF5EF, #2BE36B | whistle,crowd | SATU LAGI · JANGAN BERHENTI · LEBIH KUAT · MENANG |
| Game / tech | dnb 172 / phonk 140 | #0B1020, #F3EEE3, #FFC21A | ding | MAIN · KALAH · ULANG · GILIRAN ANDA |

## 4. Create the film folder and spec

```bash
sh "$K/scripts/new_film.sh" <slug> starter && cd <slug> && npm install playwright
```

`new_film.sh` copies the engine (`$K/engine`) and fonts into the folder. Then write `spec.js`. `$K/examples/car-teaser-spec.js` is a complete working 20 s example (phonk 140, Malay copy); copy it and replace the words, palette, cues and names. Every block option is in `$K/references/blocks.md`; motion rules are in `$K/references/craft.md`.

Spec essentials:

```js
title: 'NAME', bpm: 140, beats: 47, fps: 30,
music: { file: 'audio/music.wav', offset: 0, stopBeat: 40, gain: -9 },
sounds: { hit: 2, slash: 0 },            // + extras levels, e.g. rev: -3
cues: [[5, 'rev', 1]],                    // [beat, sound, gain]
```

## 5. Soundtrack (free)

```bash
python3 "$K/scripts/synth.py" . --genre phonk --bpm 140 --beats 47 --drop 8 --brk 27 35 --stop 40 --key 5 --extras rev,skid
python3 "$K/scripts/beat_grid.py" audio/music.wav --bpm 140 --window 15   # bpm within ~0.3; a drop at film_beat = drop
```

- Genres: `phonk` (cowbell riff, distorted 808), `trap` (bell melody, 808, hat rolls), `dnb` (reese, two-step), `house` (four-on-the-floor, stabs), `cinematic` (toms, braams, pulse; good for official/government events).
- `--key`: root pitch class (0 = C, 5 = F, 9 = A). `--brk`: the quieter break (match the Hero span). `--stop`: the logo beat.
- Extras: rev, skid, sizzle, whistle, shutter, ding, crowd → `audio/sfx/<name>.wav`. Play them with `spec.cues` and set their levels in `spec.sounds`.
- `music.offset` stays 0 (film beat 0 = 0 s of the track).

## 6. Preview stills

```bash
(python3 -m http.server 5671 >/dev/null 2>&1 &); sleep 1
FILM_URL=http://127.0.0.1:5671 node "$K/scripts/snap.mjs" stills 0.5 b1.5 b3.8 b5.8 b7.7 b8.3 b9.7 b11.8 b13.8 b20 b25 b31 b36 b38.7 b43
python3 "$K/scripts/montage.py" stills/sheet.jpg 4 480 stills/t_*.png
```

Open `stills/sheet.jpg` and check that every word fits, the grounds flip colour between phrases, and the spelling is right. If snap prints `ERRORS`, fix the spec first.

## 7. Mix, render, finish

```bash
python3 "$K/scripts/mix.py" .            # weak hits listed? lower music.gain (-9..-11) or raise spec.sounds
python3 "$K/scripts/render.py" . --res 1080 > render.log 2>&1   # long; run in background and poll out/parts/part0.log
python3 "$K/scripts/finish.py" . --video out/video_1080.mp4 --audio out/mix.wav
```

- Use 30 fps on machines with 4 cores or fewer (about 2-4 s per frame on 2 cores, so a 20 s film takes about 30 min). Use 60 fps only on strong machines.
- Don't kill processes with `pkill -f <pattern>` when the pattern also matches your own shell command.
- Let `finish.py` complete: it writes `out/final/<name>_1080p30.mp4` and a 9:16 version, and must print `ALL CHECKS PASS`. On a dynamism failure, add shots or motion where `scripts/holds.py` points.
- 4K only when asked: `render.py . --res 4k` then `finish.py` on that file (see `$K/references/render.md`).
- The finish.py hardware-decoder check only runs on macOS; elsewhere it's skipped.

## Traps

- `exit: { type: 'zoom' }` requires the block's **last shot** to be `slam`, `stack`, `split`, `cut` or `punch3d`. With `pair` it crashes (`last.counter is not a function`). `char` = the index of a letter with a hole (O D B P R A 0).
- The drop shot sits exactly on the drop beat. The music's breath gap is the quarter beat before it, so don't place a shot at drop − 0.25.
- Pure function of time: no `Math.random` or `Date` in custom block code.
- Dates, prices, specs, venues and stats come only from the user or their poster.
- No real brand logos, car badges or known characters unless the brand is the user's own.

Fonts in `engine/fonts` are SIL OFL (licences included).
