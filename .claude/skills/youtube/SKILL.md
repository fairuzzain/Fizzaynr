---
name: youtube
description: Edit talking-head, interview or explainer footage into a 16:9 YouTube video (1920x1080 or 4K) with key words or kinetic captions, smooth impact zooms, real UI beats, picture-in-picture showcases, glass side cards, charts and clean sound. Presets - Creator Explainer, Creator Light Studio, Clean Talking Head, Gadzhi Cinematic, Vox Explainer, Documentary Collage. Also removes static background logos and corner watermarks. Use for "YouTube edit", "horizontal", "16:9", "long-form", "edit my video", or when director picks a YouTube style.
---

# Horizontal Edit (16:9, 1920x1080, render 4K on request)

> **Client work:** use the client's brand kit for every colour, font, logo and card (`/theme` section 0).
> Presets below set motion and pacing only; the brand overrides their colours and fonts.

Built on `/fx` (+ CreatorFX), `/theme`, `/sound`, `/qa`.
Workflow: source → raw cut → words → frame map → preset + theme → storyboard → build → audio → finalize → QA.

## 0. Ask first (one message, skip what's known)
1. **Spoken language vs on-screen language.** A Hindi/Hinglish video usually wants ENGLISH key words on screen; the
   script or SRT is only the reference. Ask for the script/SRT if they have one.
2. **Captions or key words?** Creator videos often want NO caption track, just highlighted key words.
3. **Audio scope.** Voice only (loudness-normalised), or SFX/music too? Colour grade or not? Default for creator
   talking heads: voice only, no grade, unless they ask.
4. **Output**: 1080p or 4K. 4K = author at 1920x1080, render `--resolution landscape-4k --quality delivery`.

## 1. Raw cut (when the clip has retakes)
- Many creators record each line several times and the **last take is the keeper**. Group takes by similarity,
  keep the last full take of each line, drop false starts and partial attempts, remove repeated words, close the
  pauses inside a line. Keep real jokes and ad-libs that are not retakes.
- Check the script before cutting: an opening repeat can be a deliberate setup ("If I said... If I said...").
- **Edit the whole clip they give you**, start to end. If something can't be covered, say so; never stop silently.

## 2. Layout
- Speaker usually centre or right: text and cards live in the **empty wall** (left x 96-640 when they sit right).
  Size text to fit that wall at normal framing. Use a soft dark left scrim (not a grade) on bright or coloured walls.
- **Never on the face or mouth.** Measure the face at the tightest zoom; cards go on the side wall, chest band or
  bottom band. Recheck every text frame against the face.
- Safe zone x 96-1824, y 54-1026. Leave the last 20 s of long videos clear for end screens.

## 3. Rhythm
- **Smooth zooms only on impact lines**: `MK.zoom` (0.5-0.9 s ease in, hold, ease out), 4-6 per minute. No hard
  punch-in jump cuts, no zoom every time text appears, no constant reframe. (`MK.camera` cuts only if asked.)
- **A designed beat every 1-3 sentences**, chosen by what the words literally say:
  key word (serif lead + one big word) → real UI beat (chat, render error, timeline, app window, own screenshot) →
  showcase (PiP over a fan or wall of examples) → hero object (the product folder) → back to the speaker.
- Don't make it a text-only video: swap text beats for real-world UI wherever it fits. If nothing real matches the
  line, stay on the speaker with one key word.
- Pattern break every 30-60 s (PiP showcase, light studio box, full-frame graphic).
- Keep edits lean: zooms + key words + a few hero beats. Every beat must earn its place.

## 4. Footage fixes
- **Low-res source** (≤ 720p): upscale first:
  `ffmpeg -i src.mp4 -vf "scale=1920:1080:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,eq=contrast=1.04:saturation=1.06,fps=30" -an talk.mp4`
- **Corner watermark**: a base zoom of 1.12-1.14 crops it; keep that zoom as the "wide" shot.
- **Logo/sign in the background** (tripod shot): `python3 scripts/remove_logo.py talk.mp4 --box x0,y0,x1,y1 --from above`
  → `<img src="patch.png">` inside `.mk-cam` at the box position. Check `patch_preview.png`.
- **Screen recordings**: crop to the content (no browser tabs, menu bar or dock); use only segments where the
  screen is actually moving.
- **Ending mid-sentence**: end after the last complete phrase with a 0.25 s audio fade.

## 5. Deliver
`fx/scripts/finalize.py --target youtube` (1080p) or `--target youtube4k`. Both put a keyframe every 30 frames
with a closed GOP so the file plays and scrubs in Premiere Pro. Never hand over the raw render.
Multi-part videos: keep one project folder per part with a `HANDOFF.md` (beat sheet, files, rules, rebuild
commands, open items) so the next part matches the look.

Presets: `references/presets.md`. Reference builds: `fx/examples/creator-explainer_16x9.html`,
`fx/examples/youtube-talking-head_16x9.html`.
