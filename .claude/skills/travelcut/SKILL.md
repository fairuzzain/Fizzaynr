---
name: travelcut
description: Turn real trip photos into a finished cinematic 9:16 travel film - reads and scores every photo, picks the strongest 6-16, finds and levels the best vertical frame inside each one (auto-crop with before/after sheets), animates each crop with Nexabot sfv (Veo start frame), makes the music with Nexabot, and edits the clips to the beat at REAL SPEED with diagonal whips, zoom punches, light dissolves, per-colour-world grades and the clips' own ambience. Use when the user drops trip / holiday / vacation / travel photos and asks for a travel film, travel reel, "video percutian", "jadikan gambar trip ni video", "cinematic travel video", or names /travelcut or TRAVELCUT. Event / launch / BTS recaps go to recap-reel instead.
argument-hint: "[photos or folder] [10|15|30 s] [feel] [music file]"
---

# TravelCut (trip photos → auto-crop → Nexabot clips → real-speed beat cut)

Turn ordinary trip photos into a short cinematic travel film. Read the photos, choose the strongest
moments, find the best vertical frame inside each one, animate them, and cut the clips to music.
Based on @sferro21's TRAVELCUT (Higgsfield/Seedance), rebuilt on the user's own stack:
**Nexabot** generates clips and music (global CLAUDE.md: never Higgsfield or another paid video
connector), the cut is local Python/ffmpeg.

Work for any person, trip or camera. Assume nothing about the place or people. Talk in the user's
language (Malay if they write Malay); write generation prompts in English. Never name real people in
prompts; describe them by what is visible ("the woman in the yellow dress").

```
ROOT="$(git rev-parse --show-toplevel)"; set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a   # repo root + overrides
NB="${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"
S="$ROOT/.claude/skills/travelcut/scripts"     # system python (numpy, PIL, cv2, scipy)
R="${RUNS_DIR:-$ROOT/runs}/travelcut/<slug>"               # one folder per film, e.g. cappadocia-2026
```
Always pass **absolute** `--out` paths to nexabot.ts (relative ones resolve inside the Nexabot kit folder).
Cost: 0.15 credit per request (clip, image or music). Failed / filtered jobs are refunded.

**Best input** (tell the user if they ask what to send): 6–20 photos with good light, one clear
subject each, and something that can move (water, steam, crowds, hair, flags, a road ahead). Wide or
crooked shots are fine, TravelCut reframes them.

## 1. Intake (one round, AskUserQuestion)
Ask only what is missing:
- **Length**: 10 / **15 (default)** / 30 s.
- **Feel**: 2–3 directions that fit THESE photos (e.g. energetic beat-cut · cinematic and calm ·
  warm nostalgic). Skip if already said.
- **Music**: their own track, or TravelCut makes one with Nexabot (section 6).
Format is always 9:16 1080×1920. No other questions.

## 2. Read the photos
```
python $S\scan.py $R <photo|folder>...
```
→ `photos/pNN.jpg` (EXIF-upright, HEIC/RAW converted through ffmpeg, originals untouched),
`photos/analysis.json` (sharpness = Laplacian variance, exposure, clipping, near-duplicate groups),
`photos/contact.png`. If a photo is "unreadable", ask the user for a JPEG of it.
- Drop near-duplicates (keep the sharpest, marked yellow on the sheet), badly blurred (sharp ≪ the
  set's median), heavily obstructed or unusable-at-phone-size photos.
- **Look at every photo** (Read each `photos/pNN.jpg`, not only the contact sheet). Note light, time
  of day, scale, people, action, materials, small details (a cup, hands, a doorway, food,
  reflections) and what could move. Name a place or season only when certain.
- Choose one emotional idea and an arc. Give each chosen photo a job: hook, orientation, human
  moment, detail, spectacle, breath, payoff, ending. Real-speed shots hold the screen longer:
  **15 s ≈ 6–9 photos, 30 s ≈ 10–16, 10 s ≈ 5–6.** Leave out redundant ones even if pretty.
- Group shots into **colour worlds** (dawn, warm day, golden hour, night colour…) and plan a
  place ↔ detail rhythm.

## 3. Find the frame (auto-crop)
Write `$R/crop_plan.json`, one entry per chosen photo **in shot order** (schema at the top of
`scripts/autocrop.py`): the `hero` box and any `keep` boxes as normalised x0,y0,x1,y1 on the
original photo (estimate them from the full photo you read, never from the contact sheet), plus one
`drop` line ("keep the couple and the sunset; drop the bin, the railing and the empty sky"), and
`people` / `symmetric` / `look` where they apply. A photo that already works still goes through
(it just gets a near-full crop); a photo no 9:16 crop can save gets `"fit": "blur"`.
```
python $S\autocrop.py $R                     # all; --only f03 f05 to redo some
```
What it does: levels small accidental tilts (Canny + Hough, weighted median, verticals 0.7 weight,
only 0.4–8°, crops must stay inside the rotated image) → saliency (spectral residual + Lab colour
contrast, + weight on hero/keep boxes) → searches 9:16 crops at 40–100 % scale × many positions,
rejecting crops that keep < 97 % of the hero (people 99.5 % + every keep box whole) → scores
thirds placement (centre if symmetric), hero size, keep boxes, salient density, empty borders
(nothing cut in half), larger crops slightly preferred; penalises cutting any detected head, missing
headroom, and no space in the `look` direction → keeps the top 3 distinct candidates.

**Read every `review/fNN.png`** (original with boxes | levelled analysis with heat map, candidates,
thirds grid, tilt | candidates 1–3). Override when the score is visibly wrong: `"pick": 2`, a manual
`"box"`, `"tilt": 0` (slopes, dunes, stairs and deliberate angles fool the line detector: check the
corrected horizon by eye), or a new hero box; re-run with `--only`. Read the printed warnings: a crop
under ~700 px tall → choose a looser crop or warn the user (the frame is only resized to the
model's input, never upscaled to fake detail). `review/fNN_ba.png` is a postable before/after.

## 4. Shot plan → one approval
Per shot: photo/frame, job, the camera move, the action, the transition into the next shot, and
the planned on-screen time (0.75–3 s at real speed; the used ranges add up to the chosen length).
- **Motion comes from the photo.** Animate what is plausibly there (water, wind, steam, light,
  crowds, a natural step or head turn, a camera move revealing space the photo implies). Never
  invent landmarks, people or events.
- **Vary scale and energy**: wide, human, tactile detail, movement, a held view. Plan one match cut
  by shape or colour if the photos offer one (round cup → round lamp, red → red, horizon → horizon).
- **Hook**: the first second is a legible visual event, not a title card. **Ending**: feels chosen
  (a reveal, a look to camera, a pull-back).

Write `$R/videos/clips.json`: one `sfv` clip per shot, names `c01`… matching `f01`…:
`{"name":"c01","mode":"sfv","prompt":"…","ratio":2,"resolution":1080,"media":["../frames/f01.png"]}`.
For a hero shot you want two angles from, add `c01b` with a different camera move.
Prompts: `references/prompts.md` (TravelCut template, unchanged in spirit). Then
`bun $NB batch $R\videos\clips.json --dry` and show the user a compact table + **one total**:
`0.15 × (clips + 1 music [+ 1 style test is part of the clips])` credits, and the wait
(~2–6 min per batch of 4 on Nexabot). There is no quality choice to offer: Nexabot clips are
1080p 9:16 at the same price. Ask once for the whole batch; if already approved, don't ask again.
A clip regenerated later is announced with its cost first.

## 5. Generate (Nexabot)
1. `bun $NB credit` (free) — enough credits?
2. **Style test**: generate the hook clip alone first:
   `bun $NB sfv "<prompt>" --media $R\frames\f01.png --ratio 2 --res 1080 --out $R\videos\c01`,
   then `python $S\clean.py $R --names c01` and Read `sheets/c01.png`. Fix the prompt if the first
   frame drifts from the photo, faces/people morph, text appears or nothing moves.
3. The rest: remove c01 from clips.json, `bun $NB batch $R\videos\clips.json --parallel 4`.
   Music runs in parallel (section 6).
4. Failures: never resubmit just to check on a job; read `videos/nexabot-results.json` first.
   `JSON Parse error: Unrecognized token '<'` = server 502 at submit, nothing charged: retry those
   names later with `--parallel 1`. Safety-filter rejection ("Konten ditolak filter keamanan") is
   refunded: reword neutrally (see prompts.md) and retry once; otherwise drop the shot and re-plan.
   Log every job (shot, prompt, settings, result file, cost) in `$R/log.md`.

## 6. Music
- **User's track**: copy to `$R/audio/` and use as given.
- **Otherwise Nexabot**: `bun $NB music "<music prompt>" --out "$R\audio\music"` (prompt only, no
  length/tempo params; describe genre, tempo, instruments, energy curve and a clear quiet→loud lift;
  never name artists or works; no vocals). Included in the approved total. Fallback only if it fails
  twice: a track from `${MUSIC_DIR:-$ROOT/assets/music}/` (say so, note its source).
- Analyse: `python $S\beats.py $R\audio\music.mp3 --out $R\audio\beats.json --span <beats needed>`
  → bpm, beat grid, `drop` (strongest quiet→loud jump), `suggested_start`. **Put the drop on the
  first cut**: `music_start = drop − shots[0].dur`. If the track is short after that point, cut.py
  repeats a bar-aligned 4-bar section (or set `loop_bars`) instead of ending early.
- Be honest: analysis is not listening. Say the music was chosen by analysis; offer an earshot
  `describe` pass if the user wants it checked.

## 7. Edit (real speed)
```
python $S\clean.py $R          # delogo BEFORE scaling → clean/*.mp4 at 1080x1920, source fps, muted; sheets/ at 1 fps
```
**Review clips first**: Read `sheets/_all.png`. Per clip check the first frame matches the photo,
identity, hands, anatomy, warping, flicker, melting text; Veo often draws stray text/numbers or
drifts after ~4–5 s, so note each clip's **clean range**. Regenerate only clips that cannot be
saved (announce the cost). Remove any shot whose staging looks physically odd, even if spectacular.

Write `$R/edit.json` (schema at the top of `scripts/cut.py`):
- **Real speed, always.** Every clip plays frame for frame: no speed-ups, slow motion, ramps or
  frame blending (cut.py has no speed key on purpose). If the film runs long, shorten or drop whole
  shots, never speed them up.
- **Rhythm comes from the cuts.** Choose each `in` so the key action (a door opening, a wave
  breaking, a step, a look) sits inside the shot; `snap: "half"` puts every cut on a beat or
  half-beat. Lengths: hook 1–2 s, details 0.75–1.5 s, connecting 1–2 s, reveals/ending 2–4 s. On a
  match cut keep the frame at the joint (`to: "match"`) and trim from the other end.
- **Transitions** change per colour world; never one device three times in a row. `cut` on a beat,
  `whip` (uneven diagonal: directional blur + slight rotation/scale + RGB split; it alternates
  angle, override with `angle`), `zoom` punch, `light` dissolve through warm haze, `shake` hit,
  `match`.
- **Grade** per world in `worlds` (warmth, saturation, contrast, exposure), gentle, skin natural;
  light `vignette` (0.2).
- **Sound**: music + continuous ambience from each clip's own Veo audio (`ambience_gain_db`, per-shot
  `amb_db`), with J-cuts (`jcut` 0.3 s: the next place is heard before it is seen). No whooshes for
  camera moves. If the user asks for sound effects anyway, they go through the SFX pipeline
  (global CLAUDE.md: openverse-sfx → real-sfx → earshot), never synthesized here.
- **Text**: none by default. If asked, keep it short, inside the phone safe area, readable at phone
  size. The film never announces "made from photos"; the before/after belongs in the post packaging.

```
python $S\cut.py $R --preview      # 540x960, fast; prints each shot's source range, film time, beat check
```
Read `qa_cuts.png` (4 frames around every cut) and the printed plan: every cut "on beat"/"on
half-beat", no shot reported "window ran past the clip" that lost its key action, no junk frames.
Fix edit.json and re-preview (free). Then `python $S\cut.py $R` → `final.mp4` (H.264 high,
yuv420p, 24 fps = Veo's rate, AAC 48 kHz, −14 LUFS, true peak ≤ −1 dBTP, last ~1 s faded).

## 8. Check and deliver
- cut.py prints duration, size, fps, integrated loudness and true peak; also look at the first and
  last frames and a 2 fps strip of `final.mp4`
  (`ffmpeg -i final.mp4 -vf "fps=2,scale=135:-1,tile=10x4" -frames:v 1 strip.png`).
- Name what you could not verify ("music chosen by analysis, not by listening").
- Deliver: `final.mp4` (SendUserFile + path), the `review/*_ba.png` before/afters, the cropped
  `frames/`, length, BPM, shot count, credits spent. Save new versions under new names
  (`final_v2.mp4`); never overwrite a delivered file.
- `$R/log.md`: photos used, crops, prompts, jobs, costs, music source/licence, edit decisions, limits.
- Free variants from the same clips: another length, cut order, grade or music start. A 16:9
  version is not free (new crops and clips).

## Prompt package (only if the user asks for "just the prompts")
Do sections 2–4 and deliver the numbered 9:16 start frames, one copyable prompt per shot, settings
in neutral terms (start-frame/image-to-video, 9:16, 5–10 s, native ambience on, no music) and the
edit plan (order, in/out ranges at real speed, transitions, where the drop goes). Then offer to
render it with Nexabot (state clip count and cost) and stop.

## Gotchas
- Nexabot `img` is not needed: the user's photos are the start frames. Only if the user has < 5
  usable photos, offer extra B-roll frames (cost per image) and say they are generated, not theirs.
- Clips are ~10 s; prompts ask for the key action in the first 4 s, the rest is spare range.
- The Gemini mark sits at x 855, y 1695, 95×95 on 1080×1920; clean.py removes it before scaling.
- cut.py reads ambience from `videos/<clip>.mp4` (raw) and picture from `clean/` — keep both.
- Never pipe cut.py into `head` (broken pipe kills the render); use `tail`.
