---
name: vox-history
description: Vox History (Nexabot + Gemini Voice + QA Gatekeeper) - produce cinematic Vox-style historical, documentary, ancient battle, and civilization explainer videos with strict cultural/religious guardrails, zero anachronisms, zero stray numbers, authentic period accuracy, Google Gemini voice narration (Fenrir), automated 4-gate quality auditing, and "jana sampai sempurna" enforcement.
argument-hint: "[historical topic, e.g. Perang Uhud, Tamadun Melaka, Roman Empire]"
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Vox History (Cinematic Historical Diorama)

The dedicated Vox skill for **History, Ancient Battles, Civilizations, Biographies, and Islamic/World Heritage Documentaries**.

Unlike modern news/economic Vox videos, `/vox-history` strips out modern infographic clutter (no random stat numbers, barcodes, or code tags like `24014D`), strictly enforces historical and cultural authenticity, uses cinematic full-bleed diorama framing (no cardboard shoebox borders), applies strict typography lock, and gates every render through the **Video QA Auditor** until 100% defect-free ("Jana Sampai Sempurna").

---

## Key Differences: `/vox` vs `/vox-history`

| Feature | `/vox` (Original News/Econ) | `/vox-history` (History & Heritage) |
|---|---|---|
| **Topic Focus** | Current events, inflation, politics, US/world news | Ancient history, battles, civilizations, Islamic history, biographies |
| **Numbers & Text** | Giant stat numbers ("4.1%", "$100B"), ticker counters | Clean historical tablets/banners, strictly NO floating stat codes or random numbers |
| **Cultural & Religious Guardrails** | Secular / modern journalism standards | Strict authentic markers (desert stones/cairns for Islamic history; NO crosses/cemetery headstones) |
| **Geographic Accuracy** | Modern urban / geopolitical maps | Period-accurate terrain, props, and flora (NO American cacti in Arabian deserts) |
| **Framing** | Paper diorama cutouts | Full-bleed 16:9 cinematic diorama (NO cardboard shoebox outer frames) |
| **Typography Control** | Headlines & stat labels | Character-by-character locked spelling (prevents AI typos like "4QET") |
| **Voiceover Engine** | Nexabot TTS (English) | `gemini_tts.py` for pure Bahasa Melayu Malaysia, Nexabot TTS for English (voice `Fenrir`/`Charon`) |
| **Pacing & Outro** | Fast-paced journalistic cut | Solemn pacing with natural sentence pauses, 2.5–3.0s outro hold, and smooth 1.8s fade-to-black |
| **Quality Standard** | Standard visual inspection | Strict 4-Gate Quality Audit + "Jana Sampai Sempurna" (re-roll until 100% flawless) |
| **Google Drive Sync** | Local runs directory | Automated organization & sync to Google Drive (`AI VIDEO -> <MONTH YYYY> -> <TITLE>`) |

---

## Production Workflow (7 Steps)

### Step 1: Historical Research & Scriptwriting
1. Research the historical event thoroughly using primary records and verified historical accounts.
2. In Islamic history:
   * **Prophet Muhammad SAW and Sahabah must NEVER be depicted visually** (use banners, desert topography, arrows, terrain, or symbolic artifacts).
   * Grave sites and memorials must strictly feature **plain uncarved desert stones, sand mounds, and stone cairns**.
3. Narration Script:
   * **Mandatory Language Consistency Lock:** 100% mengikut bahasa input/tajuk. Jika tajuk Bahasa Melayu, keseluruhan skrip, VO, on-screen text, dan label WAJIB 100% Bahasa Melayu baku (sarikata/caption JANGAN dimasukkan melainkan diminta secara eksplisit) (tiada bahasa rojak). Jika tajuk English, gunakan 100% English sepenuhnya.
   * Short, dignified sentences (~60–80 words for a 35–45s short).
   * Save to `script.json`.

### Step 2: Voiceover Generation
1. Generate with voice `Fenrir` (deep, solemn, cinematic) or `Charon`. Malay uses the command below; English uses `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" tts "<text>" --voice Fenrir --out audio/chapter_01.wav`:
   ```bash
   python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/gemini_tts.py" --file script.txt --voice Fenrir --out audio/chapter_01.wav
   ```
2. Add natural head breath (0.8s) and tail breathing pause (2.5s) using `pad_audio.py` to prevent abrupt cuts.
3. Align word timestamps using local faster-whisper into `audio/chapter_01.words.json`.

### Step 3: Scene Segmentation
1. Split narration into 5 to 7 meaningful historical beats (each clip 3.5s to 6.5s).
2. Every cut must align with the natural pause between sentences.
3. Save to `segments.json` and `plan.json`.

### Step 4: Prompt Engineering with Strict Guardrails (Gate 1)

Every clip prompt must enforce the **Clean Historical Style Suffix**:
```text
Style: Aged-print collage rendered as a deep 3D paper diorama: cream and tea-stained parchment paper textures,
black-and-white halftone cutout terrain and historical figures with rough white keylines and offset red marker strokes,
condensed bold headline caps, desaturated archival palette of cream, warm grey, desert tan and ink black with one hot red accent,
visible print grain and halftone dots. Cutouts are physical paper layers separated in real space, strong shallow depth of field.
Single cinematic full-bleed 16:9 frame, edge-to-edge composition, no cardboard box borders, no outer frames, no grid layout, no watermark.
```

**Mandatory AVOID Block in Every Video Clip:**
```text
AVOID: NO random numbers, NO stat signs, NO floating codes, NO '24014D', NO cacti in Arabia,
NO crosses, NO crucifix, NO Christian tombstones, NO cemetery headstones, NO church symbols, NO religious icons,
no cardboard box borders, no outer frames, no flat single-plane composition, no static locked-off camera,
no glossy plastic CG (depth stays papercraft), no human face closeups of holy figures,
no warped or gibberish text, no typos (e.g. no '4QET'), no new text appearing, no invented logos,
no watermarks, no music, no soundtrack, no voice-over, no narration, no lyrics
```

**Typography Lock Rule:**
If a scene includes text (e.g. a tablet or banner), explicitly state:
`This frame has exactly ONE text element, '<EXACT_TEXT>', spelled exactly: [spell out letters/digits]. NO other text, NO typos.`

### Step 5: Keyframe Generation & Image Audit (Gate 2)
1. Generate keyframes:
   ```bash
   python generate.py images <run_dir>
   ```
2. Inspect every keyframe using `read_file` or `qc_gatekeeper.py`:
   * Zero typos or weird scrambled letters.
   * Zero random stat numbers or floating code labels.
   * Zero anachronisms (correct flora, weapons, and architecture).
   * Zero cardboard box outer borders (must be full-bleed 16:9).
3. **If defective:** Edit prompt to block the anomaly and re-generate image (`--force --only <clip_id>`). Do NOT proceed to video until the image is 100% clean.

### Step 6: Video Clip Generation & 1-FPS Strip Audit (Gate 3)
1. Generate video clips via Nexabot Veo (`sfv` start-frame to video):
   ```bash
   python generate.py videos <run_dir>
   ```
2. Extract 1 FPS strips for every clip:
   ```bash
   python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/qc_gatekeeper.py" strip <clip_path.mp4>
   ```
3. Inspect frames 4 through 10:
   * Ensure no objects melt, morph into weird shapes, or hallucinate text/numbers.
   * Ensure characters do not move mouths/lip-sync when unnarrated.
   * Choose the optimal clean range (`src` offset and `speed`).
4. **If defective:** Re-prompt with surgical negative blockers and re-roll the clip.

### Step 7: Master Assembly, Outro & Drive Sync (Gate 4)
1. Assemble master video with `assemble_perfect.py`:
   * **No-Caption Rule:** JANGAN bakar (burn-in) sebarang sarikata ke atas video melainkan diminta oleh pengguna.
   * 0.5s fade-in from black.
   * Frame-accurate cuts on sentence pauses.
   * **2.5s to 3.0s outro settle hold** after the last word.
   * **1.8s smooth video fade-out to black**.
   * **2.5s gentle audio decay/fade-out**.
   * Clean delogo watermark filter (`delogo=x=1130:y=570:w=63:h=63`).
2. Verify final render:
   ```bash
   python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/qc_gatekeeper.py" audit-video <final.mp4>
   ```
3. Auto-sync the entire project to Google Drive:
   * Target folder: `AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>`.
   * Files: `final.mp4`, all `.mp4` clips, all `.png` keyframes, `chapter_01.wav`, `script.json`, `plan.json`.
