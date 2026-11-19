---
name: qa
description: Final quality gate for Edit Kit videos - format, loudness, SFX sync, and a frame-by-frame visual check (safe zone, face clear, captions readable, no leftover logos, nothing mid-animation looking broken). Use before delivering any edit, or when the user asks "is it ready", "check the video", "why does this look off".
---

# Edit QA

Run before every delivery. Fix and re-render until everything passes; never report a FAIL as done.

## 1. Automatic checks
```bash
python3 scripts/qa.py Final.mp4 --expect 1080x1920 --lufs -14 --cues cues.json --sfx audio/sfx.wav --at 1.5,3.3,6.0,9.5,13,16.5
```
- **format**: resolution matches the target (9:16 = 1080x1920, 16:9 = 1920x1080), 30 fps, audio present
- **loudness**: -14 LUFS ±1.5, true peak ≤ -1 dBTP
- **sync**: every SFX within 1 frame (33 ms) of its cue

## 2. Look at the frames (`qa_sheet.jpg`)
Pick times 0.3 s after each entrance and in the middle of each beat. For every frame:
- [ ] All text and cards inside the safe zone (9:16: x 150-930, y 210-1530; 16:9: x 96-1824, y 54-1026)
- [ ] Nothing covers the face, mouth or the product, including at the tightest zoom
- [ ] Captions readable on their background (scrim on bright footage), key word clearly the hero
- [ ] Captions are kinetic typography, not boxed karaoke
- [ ] No leftover watermarks or third-party logos the user asked to remove
- [ ] Frames are varied: no beat looks like the previous one
- [ ] No em/en dashes in on-screen copy; no invented stats (illustrative UI numbers flagged to the user)
- [ ] The last frame is a deliberate end (logo, CTA or a clean hold), not a mid-word cut
- [ ] Every visual matches the exact words at that moment (time of day, numbers, what is being shown)
- [ ] Typography looks human: words never merge, no wide-tracked mono labels, even gaps between text, icons, cards
- [ ] Brand: a client video uses ONLY that client's colours, fonts, logo and card style (checked against their kit);
      no other client's or the user's personal look leaks in
- [ ] On-screen language is the one the user asked for (e.g. English key words on a Hinglish video)
- [ ] No hard punch-in jump cuts on a talking head unless the user asked for them; zooms land on impact lines only
- [ ] The whole requested clip is edited (no unfinished tail), and the raw cut kept only the last take of each line

## 3. Will it open in an editor?
Check the keyframe spacing (must be ≤ 1 s, i.e. finalize.py was used, not the raw render):
`ffprobe -v error -select_streams v -skip_frame nokey -show_entries frame=pts_time -of csv=p=0 Final.mp4 | head`

## 4. Listen once
Voice is the loudest thing, music barely there, every SFX lands with its visual, no clicks at the end.

## 5. Report
Tell the user: file path, resolution, length, size, loudness, what each beat does, and anything you chose on their
behalf (auto colours, voice, illustrative numbers, trimmed endings).
