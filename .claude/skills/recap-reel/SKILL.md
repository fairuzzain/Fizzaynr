---
name: recap-reel
description: Turn a handful of photos (event, launch, behind-the-scenes, team, product, travel) into a fast beat-cut cinematic recap reel like the FOH Media "LIVEX 2026" reel - every photo animated into a Veo clip with Nexabot sfv, music generated with Nexabot music, beat-detected, then cut in code with flash frames, whip blur, black title card with text-window reveal, negative-to-B&W hits, triptych/grid splits, warm grade, grain and synth whooshes. Use when the user gives several images and asks to "animate gambar ni jadi video", "buat recap reel / event recap / highlight video", "video macam reel ni", "BTS reel", "hype video dari gambar", or names /recap-reel.
argument-hint: "[photos or folder] [title text] [16:9|9:16] [length s]"
---

# Recap reel (photos → Nexabot clips + Nexabot music → beat cut)

Reference look: `references/style.md` (read it) and the two 8 fps contact sheets
`references/reference_sheet_0-6s.png`, `references/reference_sheet_6-12s.png` (look at them once).

Everything generative goes through **Nexabot** (never a paid image/video/music API): `sfv` for each photo's clip,
`music` for the soundtrack. 0.15 credit per request, failed jobs are refunded.

```
ROOT="$(git rev-parse --show-toplevel)"; set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a   # repo root + overrides
NB="${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"
S="$ROOT/.claude/skills/recap-reel/scripts"     # python = system Python (numpy, PIL, cv2, scipy)
R="${RUNS_DIR:-$ROOT/runs}/recap-reel/<slug>"               # one folder per reel
```
Always pass **absolute** `--out` paths to nexabot.ts (relative ones resolve inside the Nexabot kit folder).

## 0. Brief (ask once, in Malay if the user writes Malay)
Get or default: the photos (paths/folder; 4–12 works best), title text for the card (e.g. event
name + year, or none), optional logo PNG for the end card, aspect (default **16:9** like the
reference; 9:16 for Reels/TikTok), length (default ~12–15 s; 20–30 s for 10+ photos), music feel
(default: punchy cinematic event hype, ~125 BPM). Do not ask about anything with a sensible default.

## 1. Start frames
```
python $S\prep.py $R <photo|folder>... --aspect 16:9        # or 9:16; --fit blur for photos far off aspect
```
Writes `frames/fNN.png` + `frames/index.json`. Look at the frames: if a crop cut off heads or the
key subject, redo that photo with `--gravity 0.2` (or `--fit blur`). The photo IS the first frame of
the clip, so faces, logos and outfits stay the user's own.

## 2. Clip + music plan → approval
Write `$R/videos/clips.json` — one `sfv` clip per photo (media `"../frames/fNN.png"`, `ratio` 1 for
16:9 / 2 for 9:16, `resolution` 1080, names `c01`, `c02`… matching the frames). For 3–5 photos add a
second clip of the best photos with a different camera move (`c01b`) so the cut has enough angles.
Prompts: `references/prompts.md` (STYLE / SHOT / ACTION / AUDIO / AVOID, one camera move per clip,
vary the moves across clips, describe only motion that fits the photo).

Write the music prompt (also in `references/prompts.md`).

Show the user: frame list, each clip's camera move in one line, the music prompt, and the cost:
`0.15 × (clips + 1 music)`. Run `bun $NB batch $R\videos\clips.json --dry` for the count.
**Wait for approval.**

## 3. Generate
1. Style test first (new reel = new look): run ONE clip (put just it in a temp JSON, or generate
   with `bun $NB sfv "<prompt>" --media $R\frames\f01.png --ratio 1 --res 1080 --out $R\videos\c01`),
   clean it (step 4) and look at its sheet. Fix the prompt if faces morph, text appears or nothing moves.
2. Then the rest: `bun $NB batch $R\videos\clips.json --parallel 4` (sfv clips are fine in parallel;
   remove the already-made test clip from the JSON first).
3. Music, in parallel with the clips:
   `bun $NB music "<music prompt>" --out "$R\audio\music"` (extension is added; usually .mp3).
   Then `python $S\beats.py $R\audio\music.mp3 --out $R\audio\beats.json --span <beats needed>`
   (beats needed ≈ length_s × bpm / 60). Note `bpm`, `suggested_start` (skips a quiet intro),
   `strong` beats (use them for flash / title hits). If the track is shorter than the reel, or has
   no drive, generate one more with a clearer prompt (tell the user: +0.15). Fallback only if
   Nexabot music fails twice: a track from `${MUSIC_DIR:-$ROOT/assets/music}/`.
   A safety-filter rejection is refunded; reword neutrally.

## 4. Clean + look
```
python $S\clean.py $R            # delogo (Gemini mark) → clean/*.mp4 at reel size, 25 fps, muted; sheets/
```
Read `sheets/_all.png` (1 tile per second per clip). For each clip note the usable windows: good
motion, faces intact, no stray text/numbers (Veo often draws junk after ~4–5 s), no morphing.
Rule (cut AI clips by content): pick each window from the strip and keep natural speed
(`speed` 1; 0.5–0.8 only to stretch a calm moment). One 10 s clip usually gives 2–4 shots from
different seconds; vary `zoom`/`pan` so repeats read as new angles.

## 5. Edit plan → render
Write `$R/edit.json` (schema in the docstring at the top of `scripts/render.py`). Follow the
shot grammar in `references/style.md`: hook with blur_in, title card on a strong beat then
title_reveal, 1–2 beat cuts alternating wide/close, a neg_flash→bw hero, flash on strong beats,
one split (v3 stagger in 16:9, h3 in 9:16) and one grid per ~8 s, wash or defocus_in to breathe,
bw + blur_out near the end, last shot = opener window again (seamless loop) or a title/logo end card.
Set `"music_start"` to `suggested_start` and keep `"sfx": true` (synth whoosh on blur/wash, low hit
on flash/title).

```
python $S\render.py $R --preview                 # 640x360, seconds; check the cut
ffmpeg -v error -y -i $R\preview.mp4 -vf "fps=8,scale=200:-1,tile=8x12" -frames:v 1 $R\qa.png
```
Read `qa.png`: no stray text, no repeated window back to back, title readable, rhythm even, no
black/empty frames except the title card. Fix edit.json and re-preview (free). Then:
```
python $S\render.py $R                           # final.mp4, full size, loudnorm -14 LUFS
```

## 6. Deliver
Give the user the full path to `final.mp4` (plus a smaller `final_share.mp4`, CRF 26, for sharing), length, BPM, shot count, credits
spent, and offer quick variants that cost nothing: a 9:16 re-cut is NOT free (clips are 16:9) —
say so; a different cut/length/title/logo from the same clips is free.

## Gotchas
- Watermark: clean.py removes it before scaling; never scale raw clips first.
- `img` is not needed here (the user's photos are the frames). If the user has fewer than 3
  photos, offer extra B-roll frames made with ChatGPT images (`codex-image/openai_image.py`; venue detail, crowd, lights) — they cost too.
- Nexabot clips carry Veo audio; clean.py mutes it on purpose (the reel is music-led).
- Keep people's likeness: no prompts that change faces, add celebrities or invent logos.
- Learned on "Kembara Kerjaya" (Oct 2026): the words "face" / "hijab" in the prompt tripped the
  safety filter on a photo of real people; "Keep every person, outfit and the whole scene exactly
  as in the start frame" passed for all 11 photos. Rejections are refunded — reword and retry.
- `JSON Parse error: Unrecognized token '<'` = Nexabot nginx 502 at submit (server side, not the
  file size). Retry the failed names a few minutes later with `--parallel 1`; nothing is charged.
- Event posters / text-heavy graphics: don't animate them (Veo garbles text). Blur-fit them to the
  reel size and make a still clip in `clean/` (`ffmpeg -loop 1 -t 5`) for a zooming end card.
- Never pipe render.py into `head` (the broken pipe kills the render); use `tail`.
