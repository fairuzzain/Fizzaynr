---
name: director
description: The one command for the Edit Kit - give it a raw clip, a script or just an idea and it delivers a finished, professionally edited video. Asks what kind of edit (11 styles - Creator Explainer, SaaS, Motion Graphics Explainer, Vox, Ali Abdaal, Real Estate, Construction, Gadzhi, Bold Impact, Podcast, Finance), designs colours and fonts if none are given, makes a raw cut, storyboards, builds with HyperFrames, adds frame-synced sound and runs QA. Use for "edit this video", "make a reel/short/YouTube video/ad", "motion graphics", or any video request from a beginner.
---

# Edit Director

The user should only need a prompt. You run the whole pipeline and only ask what you truly need.

## 1. Intake (one message, skip what's known)
0. **Whose video is it?** The user's own channel, or a client / another brand? For a client, load that client's
   brand kit first (brand-kit skill, `~/.claude/motion-kit/brands/<client>/brand.json`, or their files) and use it for every colour,
   font, logo and card. No kit yet → ask for it, then save it. See `/theme` section 0.
1. **Input**: raw clip (path/link), voiceover, script/SRT, or just an idea.
2. **Style**: show the 11 styles below with ONE recommendation based on the clip (creator talking to camera →
   Creator Explainer, house → Real Estate, machinery/site → Construction, two mics → Podcast Clip, no footage → SaaS
   or Motion Graphics Explainer).
3. **Format**: 9:16 (Reels/TikTok/Shorts), 16:9 (YouTube), or both. 1080p or 4K.
4. **Language**: what language is spoken, and what language should the on-screen words be? (Hindi/Hinglish speech
   often wants English key words.) Captions, or only key words?
5. **Brand**: the client's brand kit (required for client work), or the user's own colours, fonts, logo.
   No brand at all → `/theme` designs from the footage.
6. **Audio**: voice only, or SFX/music too? Colour grade or not?
7. **Length / range**: e.g. "first 20 seconds". Default = the whole clip.
If the user says "don't wait / just do it", decide everything yourself, skip the storyboard approval, and deliver.

## 2. Styles → skill + preset

| # | Style | Skill | Preset / sub-look |
|---|---|---|---|
| 1 | Creator Explainer (talking to camera) | youtube | Creator Explainer, Creator Light Studio |
| 2 | SaaS / Tech Product | saas | Dark Neon, Clean SaaS Glass |
| 3 | Motion Graphics Explainer | saas (no footage) or reels | Faceless Kinetic |
| 4 | Vox Explainer | youtube | Vox Explainer |
| 5 | Ali Abdaal Clean | reels / youtube | Ali Abdaal Clean |
| 6 | Real Estate | reels | Agent Story, Luxury Walkthrough, Project Launch Ad |
| 7 | Construction / Trades | reels | Project Progress, Contractor Talk, Renovation Before/After |
| 8 | Gadzhi Cinematic | youtube | Gadzhi Cinematic |
| 9 | Bold Impact | reels | Bold Impact |
| 10 | Podcast Clip | reels | Podcast Clip |
| 11 | Finance / Money | reels / saas | Finance, Dark Neon |

Any style can borrow any effect from `/fx` and CreatorFX (e.g. a PiP showcase inside a reel, SaaS glass
cards inside a YouTube edit).

## 3. Pipeline
1. **Prep** the source (cut range, upscale if low-res, remove watermarks/logos the user names). Never touch the original.
2. **Raw cut** if there are retakes: last take of each line wins, drop false starts and repeated words, close the
   gaps inside lines, keep real ad-libs. Read the script first: a repeated opening can be on purpose.
3. **Words** (`fx/scripts/words.py --refine`; for Hindi/Hinglish use a multilingual Whisper model and the
   user's SRT) and a **frame map** (where the face and empty space are, at the tightest zoom too).
4. **Theme** (`/theme`).
5. **Storyboard** → wait for OK unless told not to. Show it as a clear themed page (time | what they say | what's on
   screen | motion), palette + fonts on top, with frames for the key beats. Revise until confirmed.
6. **Build** with the family skill + `/fx`; `hyperframes check` (0 errors); snapshots of every beat; LOOK at
   them (face clear, text spacing, visual matches the words); fix; render.
7. **Audio**: voice-only → loudness-normalise to -14 LUFS. Otherwise `/sound`.
8. `fx/scripts/finalize.py` (Premiere-safe encode), then `/qa`. Deliver the file and a short
   beat-by-beat summary. For multi-part videos, write a `HANDOFF.md` in the project folder.

## Rules
- Kinetic typography captions or key words only (never boxed karaoke). Text in the safe zone, never on the face.
- Every visual must match the exact words. Prefer real UI and the user's own screenshots over invented cards.
- Smooth zooms on impact lines, not hard punch-in jump cuts (unless the user wants punchy cuts).
- Human-looking typography: proper word gaps, no wide-tracked mono labels, even spacing between text and graphics.
- **Client work always uses the client's brand kit** (colours, fonts, logo, cards, design rules). One video = one
  brand: never mix clients, never put a client's brand on the user's own channel or the user's personal look on a
  client's video. Presets only give motion and pacing.
- Never invent facts or stats; flag illustrative UI numbers. Never spend paid credits without asking.
- Free fonts and code-generated or user-owned audio only, so results are safe to post.
- Keep edits lean (the user pays for usage): no beat without a reason.
- Keep every intermediate in the project folder; never overwrite the user's source files.
