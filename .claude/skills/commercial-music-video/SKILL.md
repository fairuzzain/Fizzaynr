---
name: commercial-music-video
description: Produce commercial-grade cinematic music videos from a song, character sheet, and storyboard with mandatory automated quality inspection to ensure zero defects, zero lip-sync, exact song pacing, and Google Drive upload. Use whenever the user asks for "buat video klip", "commercial music video", "video muzik komersial", "recreate music video from storyboard", or calls /music-video.
argument-hint: "[song.m4a] [character reference] [storyboard reference]"
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Commercial Music Video (Cinematic Music Video with Zero-Defect Inspection)

Produces full-length commercial music videos (up to 5+ minutes) matching the highest production standards.

```
NB="${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"
S="$ROOT/.claude/skills/commercial-music-video/scripts"
```

## Core Production Rules

1. **Strictly Zero Lip-Sync (No Mouth Singing):**
   - Characters do NOT sing or mouth lyrics. Mouth remains naturally closed or in subtle emotional poise.
   - **No-Caption / No-Lyric Overlay Rule:** JANGAN masukkan teks lirik atau sarikata pada skrin melainkan diminta secara khusus oleh pengguna.
   - The narrative is carried by cinematic acting: gaze, micro-expressions, posture, symbolic actions (e.g. pulling ropes, gripping helm, holding chest, turning to horizon), and camera motion.

1b. **Mandatory Face & Character Identity Lock:**
   - In all keyframe prompts and video clip generation: `Identity lock: keep [character]'s face, identity, and features exactly as in the character sheet reference. Same face shape, eyes, nose, mouth, skin tone, hairline, freckles and marks; don't slim, smooth, reshape or age anything.`
   - Follow single-variable changes (Face Codes) across shots: change only pose, expression, or background between shots while locking character identity.

1c. **Mandatory 2-Step Reference Sheet Architecture:**
   - Whenever creating a character sheet: Never text-to-turnaround directly. Wajib ikuti 2 langkah:
     1. **Master Portrait:** Jana potret tunggal (4:5, 85mm lens, neutral studio, closed mouth) & luluskan dahulu sebagai sauh visual rasmi.
     2. **Turnaround / Model Sheet:** Gunakan potret yang telah diluluskan itu sebagai input imej rujukan visual untuk menjana turnaround 4-sudut (Front, Left Profile, Back, Right Profile, 16:9).
     3. **Fallback:** Jika grid multi-panel berlaku morphing/cacat, jana setiap sudut berasingan lalu cantumkan (stitch) dalam editor.

2. **Accurate Song Musical Timing (No Rigid 10s Blocks):**
   - Transcribe and segment the audio using Whisper (`song_transcription.json`).
   - Map scenes to actual musical phrasing (Intro, Verse, Pre-Chorus, Chorus Drop, Bridge, Solo, Climax, Outro).

3. **Mandatory Visual Storyboard & Approval Gate:**
   - Compile all scene concepts into a **Storyboard Whole Image** contact sheet and detailed shot timeline table.
   - **STOP AND WAIT FOR USER APPROVAL** before generating any AI video clips.

4. **Mandatory Quality Inspection & Zero-Defect Audit:**
   - Run `python $S/inspect_clips.py <clip_path>` on EVERY generated clip before assembly.
   - Extract 1 fps contact strips to verify facial anatomy, limb stability, and text-free cleanliness.
   - Automatically determine the **Clean Range** (`0s - 5s`) to skip late Veo hallucinations (stray text, numbers, or morphing).
   - If any clip shows severe deformation or open mouth singing, re-prompt and re-generate immediately.

5. **Gemini Watermark Removal:**
   - 720×1280 (Vertical 9:16): `delogo=x=565:y=1125:w=68:h=68`
   - 1080×1920 (Vertical 9:16): `delogo=x=855:y=1695:w=95:h=95`
   - 1280×720 (Landscape 16:9): `delogo=x=1130:y=570:w=63:h=63`

6. **Dual Deliverables (<20 MB Phone + Master):**
   - Master Full Quality MP4.
   - Phone Version strictly under **20 MB** with `-movflags +faststart`.
   - Contact Sheet showing all unique shots.
   - Immediate automatic sync to Google Drive.

---

## Step-by-Step Workflow

### Step 1: Ingest Assets & Map Audio Beats
- Ingest the audio file (e.g. `song.m4a`).
- Transcribe and measure timestamps with Whisper.
- Download / analyze Character Sheet and Storyboard images.

### Step 2: Storyboard Whole Image & Approval Gate
- Write scene-by-scene breakdown matching the song's musical timeline.
- Generate `storyboard_whole_image.png` combining all scene thumbnails.
- Create or update artifact with `RequestFeedback: true`.
- **Wait for explicit user approval ("Approved" / "Proceed").**

### Step 3: Nexabot Batch Generation
- Prepare `clips.json` with detailed cinematic prompts:
  * Specify character appearance from Character Sheet.
  * Explicitly include: `"completely silent closed lips, cinematic acting, 8k realism, 35mm lighting"`.
  * Mode `t2v` or `sfv`, `ratio: 2` (9:16 vertical), `resolution: 720` or `1080`.
- Run dry run first: `bun $NB batch clips.json --dry`.
- Execute batch: `bun $NB batch clips.json --parallel 4`.

### Step 4: Automated Defect Inspection & Delogo
```bash
python $S/inspect_clips.py videos/
```
- Inspect contact strips in `qa_inspections/`.
- Verify:
  - [x] Zero lip-sync (closed lips)
  - [x] Face & limb stability (no deformities)
  - [x] Clean delogo watermark area
  - [x] No stray AI text/number hallucinations
- Apply delogo filter to all approved clips to create `*_clean.mp4`.

### Step 5: Assembly & Dual Render
- Assemble shots according to approved timestamps using ffmpeg concat.
- Apply speed adjustment (`setpts`) to fit exact duration while staying within the verified clean range.
- Mux with original song audio (`-shortest`, `+faststart`).
- Render Master and compressed Phone version (<20 MB).
- Generate final 21+ shot contact sheet.

### Step 6: Google Drive Auto-Sync
- Upload Master, Phone version, and Contact Sheet to the user's project folder.
- Sync to hierarchy: `AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>`.
