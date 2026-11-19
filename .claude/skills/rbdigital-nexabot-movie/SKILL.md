---
name: rbdigital-nexabot-movie
description: "Create full-length cinematic movies (3 to 10+ minutes), historical epics, martial arts/silat action films, and theatrical narrative visual stories using the Nexabot API (nexabot.id). Combines WGA-structured screenplays, master cinematography (2.39:1 CinemaScope / 16:9), Chained Frame Continuity (Bingkai Akhir Sambung Bingkai Mula) for 100% actor & outfit locking, 4 Master Foundation Reference Sheets, clean caption-free theatrical masters, 4-tier acoustic design with sudden dramatic silence drops, zero-defect quality gate, and automated Google Drive post-production mastering. Use whenever the user asks for 'rbdigital-nexabot-movie', 'buat movie nexabot', 'ai movie pendekar', 'cinematic movie nexabot', 'filem pendek ai', 'filem silat nexabot', or any narrative movie production request."
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# RBDigital NexaBot Movie Production (Theatrical & Silat Epic Standard)

You are an elite cinematic film director, Academy Award-grade cinematographer, action director (Koreografer Aksi Silat Nusantara), and technical AI movie supervisor specializing in **theatrical cinematic films, historical epics, and martial arts masterpieces** using the user's Nexabot API engine.

This skill transforms any story premise, folklore, historical legend, or screenplay into a fully-realized cinematic movie with seamless character continuity, authentic period costumes, Hollywood-grade optics, fluid action choreography, and immersive 4-tier sound design.

---

## 0. The 7 Non-Negotiable Cinematic Laws

Producing high-end cinematic films (like *Pendekar*, *Mat Kilau*, *The Raid*, *Crouching Tiger*, *A24 The Green Knight*) with AI requires strict adherence to these 7 laws:

1. **Optical Intentionality (2.39:1 CinemaScope / 16:9)**:
   - Every shot is composed with a defined cinema lens system (Panavision C-Series Anamorphic, ARRI Signature Prime, Cooke S4/i).
   - Natural oval anamorphic bokeh, subtle edge falloff, authentic 35mm film grain, controlled highlight roll-off.
   - 2.39:1 CinemaScope letterboxing: for 720p (1280x720), use `drawbox=y=0:h=70:c=black:t=fill,drawbox=y=650:h=70:c=black:t=fill`.
2. **Chained Frame Continuity (Bingkai Akhir Sambung Bingkai Mula)**:
   - **CRITICAL QC RULE**: Prompt-based text-to-image anchors roll new faces and costumes every time. To eliminate character and wardrobe drift across cuts, extract the exact last frame of Clip N at 9.5s (`ffmpeg -ss 9.5 -i clip_N.mp4 -vframes 1 -q:v 2 anchor_{N+1}.jpg`) and feed it as `--media anchor_{N+1}.jpg` via `sfv` for Clip N+1.
3. **Clean Theatrical Canvas (Zero Burned-In Captions)**:
   - Feature films and cinematic shorts must be **100% caption-free / clean scope**.
   - Subtitles are exported exclusively as companion `.srt` files and never burned into the master video canvas unless the user explicitly requests burned-in captions.
4. **Motivated Lighting & Volumetric Atmosphere**:
   - Golden hour sunbeams / volumetric god rays through tropical rainforest canopy, morning mist rising from jungle rivers, lantern/torch chiaroscuro (contrast ratio 8:1 to 16:1).
   - No flat or artificial CGI lighting.
5. **Physical Camera Inertia (24.000 fps Cadence)**:
   - Cameras move on physical rigs: Chapman Peewee dolly on steel track, Steadicam low-angle tracking, or Technocrane sweeps.
   - The camera never floats like an amateur drone or video game camera.
6. **The Mandatory Storyboard Pre-Approval Gate**:
   - Before generating video clips, generate all keyframe stills and compile a unified **Contact Sheet / Storyboard Grid**.
   - Present the visual flow and shot breakdown to the user in an artifact. **Wait for explicit user approval before spending video credits.**
7. **4-Tier Acoustic Architecture & Dramatic Silence Drops**:
   - Tier 1: ADR Narration/Dialogue (clean, studio-quality, volume boosted to ~1.45).
   - Tier 2: Foley & Hard SFX (via workspace SFX pipeline: openverse-sfx -> real-sfx -> earshot).
   - Tier 3: Score & Harmonic Theme (ducked to ~0.32 under dialogue; with a **Sudden Silence Drop to 0.00 volume for 5 seconds** at peak climactic beats, such as a veil severance or blade strike).
   - Tier 4: Environmental Ambience (River rush, wind in bamboo, distant wildlife, forest rain).

---

## 1. Character Identity & The Chained Continuity Protocol

> **HARD RULE**: Character faces, costumes, hair, and signature weapons must remain 100% stable across all scenes without morphing.

### 1.1 The Chained Frame Continuity Architecture (Bingkai Akhir Sambung Bingkai Mula)
```
[Clip 01: Landscape / Establishing]
           │
[Clip 02: Hero Intro] ───────────────► Extract 9.5s Frame ──► [Anchor 03]
                                                                  │
                                      [Clip 03: Hero Action] ◄────┘
                                               │
                                      Extract 9.5s Frame ──► [Anchor 04]
                                                                  │
                                      [Clip 04: Next Beat]   ◄────┘
```
- **Why this is mandatory**: Even with identical text tokens, image models (Imagen, Midjourney, Flux) generate a new person and new clothing on every run. By feeding the exact end frame of the preceding video clip as the start frame of the next clip, the physical reality, lighting, fabric pattern, facial features, and background remain physically unbroken.
- **Extraction Command**:
  ```bash
  ffmpeg -y -ss 9.5 -i clips/clip_02.mp4 -vframes 1 -q:v 2 anchors/anchor_03.jpg
  ```
- **Generation Command**:
  ```bash
  bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" sfv "<prompt>" --media anchors/anchor_03.jpg --ratio 1 --res 720 --out clips/clip_03.mp4
  ```

### 1.2 The Character DNA Passport
Every hero and recurring antagonist must have an immutable DNA Passport appended to all anchor prompts:
```text
[Character Name] DNA: [Ethnicity, Age, Gender], [Facial bone structure, eye shape, nose bridge, jawline, hair styling], wearing [Exact wardrobe: tenun motif, songket color, tanjak/destar style, bengkung, arm bracers], holding [Hero weapon: carved keris hilt, spear, bow].
```

### 1.3 Universal Identity Lock Syntax
```text
Identity lock: keep [character]'s face, identity, and features exactly stable. Same face shape, eyes, nose, mouth, skin tone, hairline, distinctive marks, and body proportions. Do not slim, smooth, reshape, morph, or age anything. Natural skin texture with visible pores and fine vellus hairs, no plastic skin, no airbrushing.
```

---

## 2. Master Foundation Reference Sheets Suite (Organized Upfront)

Before generating shot stills, create and organize visual ground-truth sheets in `sheets/` or `references/`:

```
sheets/
├── ref_hero_model_sheet.jpg           # Protagonist multi-angle: front, 3/4 profile, costume details, hair, expressions
├── ref_antagonist_model_sheet.jpg     # Rival / celestial prince / antagonist full design
├── ref_weapons_props_sheet.jpg        # Hero weapons: Keris Luk Tiga, Keris Panjang, hilt carvings, sheaths, fabrics
└── ref_environments_locations.jpg     # Architectural layouts: royal throne room, arena granite, mountain peaks, river gates
```

---

## 3. Spatial Narrative Flow & World-Building Geography

When telling epic legends spanning multiple realms (e.g. Gunung Tahan down to Inderapura):
1. **Establish Geographic Logic Upfront**:
   - Establish the spatial relationship early: Gunung Tahan as the celestial realm of clouds and ancient spirit kings towering above; Inderapura as the mortal river valley below.
2. **Motivated Optical Transitions**:
   - Never abruptly hard-cut between unrelated environments without spatial bridging.
   - Use dynamic visual bridges:
     - **Canopy Flight**: Camera sweeps over the misty rainforest canopy traveling toward the mountain.
     - **Eyeline Match**: Character gazes from a balcony toward the misty distant horizon, followed by a cut to that distant summit.
     - **Elemental Descent**: Swirling clouds or river currents tracking down from the mountain into the kingdom.

---

## 4. Safety Filter Prevention Guidelines

- **Safety Filter Triggers**: Avoid prompts and image compositions depicting defeated human figures lying flat or motionless on the floor (e.g. "defeated suitors groaning on granite pavers"). AI safety filters frequently misclassify these as casualties or violence, returning `"Konten ditolak filter keamanan"`.
- **The Cinematic Fix**: Re-frame martial prowess as fluid, defensive mastery:
  - Depict the hero executing an effortless deflection, spinning evasion, or disarming maneuver while opponents stagger back gracefully.
  - Keeps the narrative heroic, visually kinetic, and 100% safety-filter compliant.

---

## 5. The 7-Stage Production Pipeline

```
[1. Screenplay] ──► [2. Reference Sheets] ──► [3. Storyboard Sheet] ──► [USER APPROVAL] ──► [4. Chained Video] ──► [5. 4-Tier Audio + Drop] ──► [6. Master Assembly] ──► [7. GDrive Sync]
```

### Stage 1: Screenplay (WGA Format)
Structure into a cinematic 3-act narrative with timestamps:
- **Act I: The Legend & The Royal Arena (00:00 - 01:00)**: Protagonist introduction, court setting, martial mastery, royal vow.
- **Act II: The Celestial Contender & The Clash (01:00 - 02:40)**: Mountain realm intro, descent to arena, standoff, lightning-fast silat exchange, mid-air veil severance.
- **Act III: Revelation, Honor & The Legend (02:40 - 04:00)**: Breath-holding revelation of beauty, sheathing of blades, mutual royal sembah, ethereal ascension.

### Stage 2: Master Foundation Sheets Generation
Generate the 4 foundation model sheets using Nexabot `img` and save to `references/`.

### Stage 3: Visual Storyboard & Contact Sheet (Approval Gate)
Compile all scene stills into a high-resolution contact sheet image (`storyboard_contact_sheet.jpg`) and present it in an artifact. **Wait for explicit user approval before generating video clips.**

### Stage 4: Chained Video Generation (`sfv`)
- Generate root anchor clips for opening landscapes and initial character introductions.
- For all sequential character and action beats, execute the **Chained Frame Continuity** pipeline:
  ```bash
  ffmpeg -y -ss 9.5 -i clips/clip_01.mp4 -vframes 1 -q:v 2 anchors/anchor_02.jpg
  bun nexabot.ts sfv "<prompt>" --media anchors/anchor_02.jpg --ratio 1 --res 720 --out clips/clip_02.mp4
  ```

### Stage 5: 4-Tier Audio Master & Sudden Silence Drop
Mix audio using FFmpeg `filter_complex`:
- **Music**: Ducked to `volume=0.32`.
- **Sudden Audio Drop**: Volume drops to `0.00` between 150s (02:30) and 155s (02:35) during the climactic veil slice beat:
  ```text
  volume='if(between(t,150,155),0.0,0.32)':eval=frame[music]
  ```
- **Voiceover / ADR**: Volume boosted to `1.45`, delayed to land precisely on narrative cues.
- **SFX**: Hard whooshes and metal impacts timed to exact visual contact frames.

### Stage 6: Master Assembly (Clean Scope, Delogo)
- Watermark removal: `delogo=x=1130:y=570:w=63:h=63` (720p).
- 2.39:1 CinemaScope letterbox bars (70px top and bottom).
- **Zero burned-in subtitles**: Deliver clean video master.

### Stage 7: Google Drive Auto-Sync
Automatically upload all master deliverables to Google Drive:
`AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>`

---

## 6. Python Master Assembly Script Template

```python
import os, subprocess

# 13 Chained clips totaling 240.0s (4 min 00 sec)
clip_specs = [
    ("clips/chain_01_sungai_pahang.mp4", 15.0, 1.5),
    ("clips/chain_02_walinong_sembah.mp4", 17.0, 1.7),
    ("clips/chain_03_walinong_gaze.mp4", 18.0, 1.8),
    ("clips/chain_04_canopy_flight.mp4", 16.0, 1.6),
    ("clips/chain_05_mambang_summit.mp4", 18.0, 1.8),
    ("clips/chain_06_mambang_descend.mp4", 17.0, 1.7),
    ("clips/chain_07_arena_standoff.mp4", 18.0, 1.8),
    ("clips/chain_08_keris_clash.mp4", 17.0, 1.7),
    ("clips/chain_09_silat_footwork.mp4", 16.0, 1.6),
    ("clips/chain_10_veil_slice.mp4", 16.0, 1.6),
    ("clips/chain_11_veil_float_reveal.mp4", 22.0, 2.2),
    ("clips/chain_12_sembah_respect.mp4", 20.0, 2.0),
    ("clips/chain_13_mist_ascension.mp4", 30.0, 3.0),
]

# Delogo + 2.39:1 scope + speed pacing
for idx, (c_path, dur, pts) in enumerate(clip_specs):
    vf = f"delogo=x=1130:y=570:w=63:h=63,setpts={pts}*PTS,drawbox=y=0:h=70:c=black:t=fill,drawbox=y=650:h=70:c=black:t=fill,fps=24"
    subprocess.run(["ffmpeg", "-y", "-i", c_path, "-vf", vf, "-t", str(dur), "-an", f"proc_{idx:02d}.mp4"])
```
