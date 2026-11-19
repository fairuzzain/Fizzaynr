---
name: "rbdigital-mascotexplainer"
description: "Faceless explainer / promo videos with motion-graphic storytelling in 10 design themes (editorial, neon, pastel, notebook, tech grid, sunset, corporate, comic, calm, bold) and any cartoon mascot from user-generated images (topic-picked poses, human or cute/animal mouths) that lip-syncs to the VO (Rhubarb), built and rendered with HyperFrames, 16:9 or 9:16, SFX + lo-fi music. Use when the user wants a mascot / lip-sync explainer, a product promo with their cartoon, or a video like the 6-skill promo."
---

# RB Digital Mascot Explainer

Faceless video: themed motion graphics on the left (or top) + a cartoon mascot bottom-right whose mouth follows the VO
(Rhubarb, phonetic mode = works for Malay) + SFX and lo-fi music. Everything is generated from one `video.json` by bundled
scripts — don't hand-write the HTML, don't rewrite the scripts. Reply in the user's language (default informal BM / rojak), concise.
Work autonomously after the brief; the only waits are for the VO mp3 and the mascot images.

`<skill>` = this skill's folder. Scripts: `<skill>/scripts/`. Default mascot: `generic` (built-in SVG host); if a pack exists in
`<skill>/assets/mascot/` other than `generic`, use it by default.

## 0. Setup (once per chat / machine, silently)

- Python 3 + numpy, pillow; ffmpeg; Node 22+; HyperFrames:
  `which hyperframes || npm i -g hyperframes` then `hyperframes browser ensure`.
- **Rhubarb** (lip-sync): `python <skill>/scripts/setup_rhubarb.py` → downloads v1.13.0 for this OS into
  `~/.rbdigital/rhubarb-1.13.0/` once and prints the binary path (`vo_prep.py` calls it automatically).
- **Windows (Claude Code on a PC):** use `python` (or `py`), not `python3`. Missing Python →
  `winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements`, then
  `python -m pip install numpy pillow`; ffmpeg → `winget install -e --id Gyan.FFmpeg`; Node → `winget install -e --id OpenJS.NodeJS.LTS`.
  The current shell won't see the new PATH: call `"$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"` or ask them to reopen
  Claude Code. If winget fails, ask them to install from python.org (tick "Add python.exe to PATH") and wait.
  (The RB Digital setup kit `SETUP-WINDOWS.bat` installs all of this including Rhubarb.)
- Linux sandbox: `pip install numpy pillow --break-system-packages -q` if an import fails.

## 1. Brief + mascot (one message, skip what they already said)

Ask once: topic / product + key points, **format** (16:9 or 9:16 Reels), CTA keyword ("Komen VIDEO"),
**theme** (10 design themes — before asking, copy `<skill>/assets/themes-preview.jpg` into the work folder and send the copy with
SendUserFile, then list them as text: 1 editorial (krim & coklat, premium) · 2 neon (malam, tech/AI) · 3 pastel (comel, kids/lifestyle) ·
4 notebook (buku nota, edu) · 5 techgrid (gelap, coding/SaaS) · 6 sunset (retro, motivasi/cerita) · 7 corporate (biru, takaful/kewangan) ·
8 comic (pop, lawak/jualan) · 9 calm (hijau, kesihatan/Islamik) · 10 bold (hitam merah, amaran/mitos).
Each theme is a whole motion kit, not just colours: its own layout (left / centred / stacked title), entry motion (move, blur-in,
bouncy pop, marker wipe, terminal scan, rise, slide, slam, soft), scene transition (hard cut, glitch, circle wipe, page turn,
scanline, blinds, push, comic burst, soft veil, flash), decorations (HUD brackets, blobs & sparkles, doodle arrow & tape, code &
cursor, retro sun, dot grid, starburst & speed lines, leaves, caution tape) and component skins (glow cards, sticky notes,
terminal blocks, speech-bubble captions...). See `templates/themes.json` ("kit") and `templates/kits.css`. "Kau pilih" → pick by topic,
and never repeat the theme of the previous video in this chat), the **label top-right** (their @handle / brand / website, or none —
never assume rbdigital.studio),
length (default 45–60 s), and **the mascot**: do they already have a pack (in `assets/mascot/` or uploaded), or what
character they want (describe it or upload a photo — any person, animal, object). Then, in the same reply:
- the plan (scene list) and the **VO script** (§2),
- if they need a new mascot: the **image prompts** from `references/mascot-pack.md` filled with their character description:
  **2 pose sheets** (6–8 poses picked for THIS topic from the pose library §2a — not the same 4 every time; always `think`
  and `thumbs`), and **1 mouth chart** — the human version for people, the **cute/animal version** for animals, mascots,
  objects and chibi characters (no human lips or teeth on a cute character). Plus the line about the plain green
  background for clean cut-outs. Even with an existing pack, if the topic needs poses it doesn't have, offer one extra
  pose sheet (4 new poses, same character, sheet 1 as reference).
Ask them to upload the images and the VO mp3 together. Only offer the built-in `generic` host if they don't want their own.

## 1b. Mascot pack (when the images arrive)

Follow `references/mascot-pack.md` §3: `make_pack.py cut sheet1.png,sheet2.png mouths.png --poses a,b,c,d/e,f,g,h` → look at
every `anchor_<pose>.png` → `make_pack.py anchor ...` (add `--no-patch` for cute/animal mouths) → `mascot_check.py` → look at
the preview sheet, nudge, repeat → show them the preview. In video.json use the pack's pose names and change pose per
sentence so most poses get used (match the pose to what is said: shocked on "jangan", money on the price, laptop on setup...). Then offer to keep it as their default
mascot (copy into `<skill>/assets/mascot/<name>/`).

## 2. VO script (they generate it on ElevenLabs)

- BM santai, ~2.3 words/s (55 s ≈ 125–135 words). **One paragraph per scene, blank line between** — the pauses become the scene cuts.
- Shape: hook question (brown bg) → answer/overview → one scene per point/step/product → who it's for / price → CTA "Komen <KATA>".
- Give it in one code block with light ElevenLabs v3 tags at paragraph starts (`[excited]`, `[curious]`, `[serious]`).
  One line under it: "Model Eleven v3, pilih suara kau sendiri, export MP3, upload sini." Don't fix a voice.
- Save the same text as `vo.txt`. Count the paragraphs = number of scenes in `video.json`.
- Don't wait idle: build a silent preview from `dur` values while they generate the VO if they want to see the look first.

## 3. Build (when the mp3 arrives)

```bash
W=<work dir>/<slug>; mkdir -p $W && cd $W && cp <upload> vo.mp3
python <skill>/scripts/vo_prep.py vo.mp3 <n_scenes> --script vo.txt   # -> vo.wav, cues.json (Rhubarb), timing.json (cuts by paragraph word count, snapped to pauses)
HYPERFRAMES_SKIP_SKILLS=1 hyperframes init proj --example blank --resolution landscape --non-interactive   # portrait for 9x16
# write video.json  (schema + every visual type: <skill>/references/video-json.md)
python <skill>/scripts/build.py video.json proj                # -> proj/index.html, fonts, GSAP, events.json
cd proj && hyperframes lint                                     # 0 errors (warnings about file size / sub-compositions are fine)
python <skill>/scripts/slop_lint.py index.html --profile talking-head   # 0 ERROR; top label is part of the style; M_OVERSHOOT is expected for pastel (bouncy kit)
hyperframes snapshot --at <one time per scene> --no-end -o snaps
```
- Always pass `--script vo.txt`: ElevenLabs pauses between paragraphs are not reliably longer than pauses inside them, so cuts placed by word count and snapped to the nearest pause are far more accurate. Check the printed scene times against the script (or a quick faster-whisper transcript if available).
- If `vo_prep` finds fewer pauses than scenes: re-run with `--min-pause 0.12` or `--noise -28`; still short → put `dur` on the
  scenes it couldn't split and drop `timing` for those (or ask for a VO with clearer paragraph breaks).
- `timing.json` also lists `phrases` (start/end of every spoken phrase): use them for `at` times (ticks, highlights, price
  reveal, sticker) so things land on the word. Times in a scene are relative to that scene's start.
- **Look at `snaps/contact-sheet.jpg`** before rendering: text overlapping the mascot, lead wrapping into the title, cards
  outside the column, empty-looking frames, and the **mascot sitting on the bottom edge of the frame** (cut off by it, no gap
  under it, no rounded body bottom showing — otherwise raise `"sink"` in mascot.json and rebuild). Shorten text / change visual and rebuild — don't hack the HTML.
- Motion rules (eases, cuts, no grow-from-zero) are built into `build.py`; read `references/motion.md` only if you add custom motion.

## 4. Render, audio, QA

```bash
hyperframes render --output render.mp4          # run in the background; ~3–4 fps on a laptop (55 s ≈ 8–10 min). Poll the log, don't block.
python <skill>/scripts/audio.py . --video render.mp4 --vo ../vo.mp3 --out ../final.mp4   # SFX + lo-fi ducked under VO + -14 LUFS
python <skill>/scripts/look.py ../final.mp4 --expect-duration <s> --audio --lufs -14 --max-end 1.5 --sheet ../qa.jpg
```
- `look.py` must PASS (no frozen run > 0.4 s, end hold ≤ 1.5 s, duration, audio, loudness). FAIL → fix and re-render.
- Look at `qa.jpg` (frames from the real MP4): mascot visible in every frame, mouth changing, overlays present.
- Background music is always on: a synthesized track in the theme's style (editorial/notebook lofi, neon funky, pastel/corporate cheerful, techgrid retro8bit, sunset/calm emotional, comic comedy, bold epic), new seed per video, sitting ~12 dB under the VO and ducked while she/he speaks. Louder/softer: `--music-gain 0.55` / `0.3`; other mood: `--style tense`; their own track: `--music their.mp3`. Silent preview (no VO yet): drop `--vo`.

## 5. Deliver

Copy `final.mp4` to `/mnt/user-data/outputs/` if it exists (else keep it in the work dir) and send it with SendUserFile, then a
short BM summary: scenes, format, QA numbers in one line, music seed, cost (0 unless a paid service was used — then the cost and
remaining balance). Offer: Threads/IG caption, the other aspect ratio (same `video.json`, change `format`, re-init with the
other resolution), or a cover frame.

**Caption (Threads/IG) when asked:** BM santai, 4 short paragraphs: personal hook → what it does → one benefit/safety point →
CTA "Komen <KATA>" (same keyword as the video). If a copy-humanizer skill is available, run the caption through it.

## Rules

- Never real brand logos or app names in mockups; generic text names only. Example figures get "contoh".
- One idea per scene; lead ≤ 1 line on 16:9; title ≤ 2 words + badge.
- Mascot never floats: it is anchored to the bottom edge of the frame (`sink`). Poses are picked per topic, not a fixed 4.
- Scenes change on VO pauses (hard cut + whoosh); mascot pose changes on sentence boundaries.
- Top-right label = `"brand"` in video.json: the user's handle/brand/website, or empty (hidden). Never default to rbdigital.studio.
- Vary the look: a different `theme` per video; inside a video mix scene backgrounds `main` / `hook` / `alt` / `accent` (hook for the opening question, accent or alt for one punchy beat, main for the rest).
- Don't use paid image/voice generation unless they ask; report cost + balance if you do.
