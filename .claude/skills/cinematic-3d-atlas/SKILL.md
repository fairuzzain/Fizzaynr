---
name: cinematic-3d-atlas
description: "Build cinematic 3D relief-map reels, geographic travel itineraries, topographic flyovers, and dark-mode route animations with high-retention shot rhythm, tactile elevation terrain, cloud parallax, glowing vector paths, floating data pins, and bold editorial typography. Based on the 10-second Atlas Reel Field Guide. Use whenever the user asks for '3d atlas reel', 'atlas reel', 'cinematic map', 'relief map video', 'topographic animation', '3d map flyover', 'route animation reel', 'geographic explainer map', 'cinematic 3d atlas', or wants to animate a geographic route or travel itinerary."
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Cinematic 3D Atlas Reel (Field Guide Motion System)

You are an elite cartographic motion director, 3D geographic cinematographer, and technical prompt engineer specializing in **cinematic 3D relief-map reels** and **tactile geographic route animations**.

This skill operationalizes the complete **Atlas Reel Field Guide**: a 10-second (24 fps), 6-phase cartographic motion system engineered from empirical motion design study. It combines tactile raised terrain, continuous camera glide, multi-depth cloud parallax, tactical dark-mode route UI, and a dramatic crimson-sea hero reveal.

---

## 0. The Golden Law: "Anchor Before Animate, Composite in Post"

> **"Create the terrain and camera motion first. Add exact labels, pins, and route graphics afterward. That keeps the map coherent and the typography readable."**

### Why Pure AI Video Fails on Maps
When video diffusion models (Veo, Kling, Seedance, Sora) are prompted to render maps with text and routes in one pass, they inevitably produce:
1. **Garbled AI Pseudo-Latin**: The reference video generated distorted gibberish (`"EUROPE ATLAS INOVERIZED IO-TANS RELIEF EDITION"`).
2. **Text Wobble & Boiling**: Letterforms distort, flicker, and warp between frames.
3. **Geographic Hallucination**: Distorted shorelines, misplaced cities (e.g. Rome floating in the Tyrrhenian Sea), or inverted peninsulas.

### The Hybrid Division of Labor
- **AI Engine (Nexabot / Veo / Gemini Omni Flash)**: Renders physical 3D relief elevation, directional sun-shading, volumetric atmosphere, smooth camera flyovers, and dramatic color transitions. Zero synthetic text.
- **Post-Compositing Engine (Editor / Remotion / HyperFrames / FFmpeg / PIL)**: Overlays exact spell-checked typography, verified coordinate pins, animated vector route strokes, and crisp editorial title cards.

---

## 1. The 4-Layer Visual Recipe

Every cinematic 3D atlas reel is built by stacking four strictly controlled visual planes:

```
┌─────────────────────────────────────────────────────────────┐
│ 04. MAP GRAPHICS & UI                                       │
│ Vector route paths, coordinate pins, HUD cards, title card  │
├─────────────────────────────────────────────────────────────┤
│ 03. ATMOSPHERE & CLOUD PARALLAX                             │
│ Soft semi-translucent cloud banks, independent depth drift  │
├─────────────────────────────────────────────────────────────┤
│ 02. CAMERA GLIDE                                            │
│ High oblique aerial opening, continuous forward dolly push  │
├─────────────────────────────────────────────────────────────┤
│ 01. 3D RELIEF TERRAIN                                       │
│ Raised mountain elevation, plausible coastlines, sun-shading│
└─────────────────────────────────────────────────────────────┘
```

1. **Relief Terrain (01)**: Exaggerated vertical relief (1.5×–2.5× elevation scale) highlights mountain ridges and rift valleys. Directional low-raking key light casts believable physical shadows across peaks. Coastlines and bathymetry remain strictly plausible.
2. **Camera Glide (02)**: Oblique viewing angle (~45°–60° pitch). Motion is unbroken and continuous: a forward dolly-in with a gentle diagonal drift toward the focal landmark. No erratic pans or 360° spins.
3. **Atmosphere (03)**: Soft, semi-transparent cloud layers drift across the lower atmosphere on an independent plane, creating stereoscopic parallax and casting soft ground shadows.
4. **Map Graphics (04)**: Crisp vector overlays added in post. Glowing cyan vector route paths (`#00F2FE`), floating locator pins with vertical stems, and a minimalist editorial title card.

---

## 2. The 10-Second Master Rhythm (00.0s – 10.0s @ 24 fps)

Every production reel follows this 6-phase timeline progression:

```
00.0s            02.2s          04.5s      05.4s     06.4s          08.2s          10.0s
  ├────────────────┼──────────────┼──────────┼─────────┼──────────────┼──────────────┤
  │    PHASE 1     │   PHASE 2    │ PHASE 3  │ PHASE 4 │   PHASE 5    │   PHASE 6    │
  │  Wide Aerial   │  Descend to  │ Map Mode │  Color  │  Dark Route  │  Final Red   │
  │    Reveal      │   Terrain    │  Reset   │  Title  │   UI Path    │ Hero Reveal  │
```

| Phase | Timecode | Frame Range | Visual Action & Motion | Post-Composite Graphics & UI |
|---|---|---|---|---|
| **Phase 1: Wide Aerial Reveal** | `00.0s – 02.2s` | Frames 0–53 | High-altitude oblique overview of region. Raised terrain, drifting clouds. Camera executes slow forward push + slight diagonal drift. | Wide sea/continent label (`MEDITERRANEAN SEA`) tracking slowly with perspective. |
| **Phase 2: Descend to Terrain** | `02.2s – 04.5s` | Frames 53–108 | Continuous dolly-in descent closer to the Alps/landmark mountains. Mountain relief becomes the tactile subject; clouds move with strong parallax. | Elevation metadata badge (`ALPS ELEVATION / 4,808M`) fades in and out. |
| **Phase 3: Map Mode Reset** | `04.5s – 05.4s` | Frames 108–130 | Landscape simplifies into a muted/dark slate contour map with topographic lines. Visual reset beat before data reveal. | Clean match-cut or dissolve morph. No glitch effects. |
| **Phase 4: Color Flash + Title** | `05.4s – 06.4s` | Frames 130–154 | Brief 2-frame optical exposure pulse cuts to a clean off-white title card (`#F8F7F4`) with bold black grotesque typography and red accent mark. | Manually verified, spell-checked title (e.g., `EUROPE ATLAS / MEDITERRANEAN EXPEDITION`). |
| **Phase 5: Dark Route UI** | `06.4s – 08.2s` | Frames 154–197 | Cut to tactical Dark Mode relief map (`#0E141B`). High-contrast cyan laser path (`#00F2FE`) traces along the terrain from start to waypoint. | Location pins drop in with subtle bounce; floating translucent metadata cards rise in sequence. |
| **Phase 6: Final Red Hero** | `08.2s – 10.0s` | Frames 197–240 | Return to textured relief. Sea/water bodies turn deep crimson red (`#8B0000`); coastlines and route ignite with incandescent ember edge-glow. | Clean white callout badges anchor onto 3 destination cities (`VENICE`, `ROME`, `ATHENS`). Frame settles into a stable hold for 1.8s. |

---

## 3. The 6-Step Production Workflow

```
[1. Plan Route] ➔ [2. Base Map] ➔ [3. Animate Camera] ➔ [4. Route Graphics] ➔ [5. Typography] ➔ [6. Sound & Export]
```

### Step 1: Plan the Route & Anchor Geometry
- Choose **1 distinct geographic region** (e.g. Southern Europe, Central Asian Silk Road, Scandinavia, Malay Peninsula).
- Select **3 anchor destinations** (e.g., Venice → Rome → Athens).
- Map 1 unbroken narrative itinerary connecting the anchors.

### Step 2: Create Base Keyframes (Nexabot `img` / Nano Banana Pro)
Generate 16:9 high-resolution keyframes without text or synthetic labels:
```bash
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" img "Cinematic 3D topographic relief map keyframe of [REGION]. High-altitude oblique view looking down at a 50-degree angle. Raised mountain elevation with realistic rocky ridges and believable coastlines. Low raking morning sunlight creates deep natural elevation shadows. Soft white cumulus cloud banks drift across the margins. Clean physical earth surface, completely text-free, 16:9." --aspect 2 --out base_terrain.png
  # For reference images / character consistency (GPT Image 2.5, 0.1 credit):
  bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" gpt-image "<prompt>" --media <ref.png> --aspect 5 --out <path>.png
```

### Step 3: Animate the Camera Glide (Nexabot `t2v` / `sfv` / Veo / Gemini Omni Flash)
Generate the 3 master video passes using the batch manifest `clips.json`:
- **Shot 01 (Phases 1 & 2)**: Wide aerial reveal descending to mountain terrain.
- **Shot 02 (Phase 5)**: Tactical dark-mode slate with glowing cyan vector trail.
- **Shot 03 (Phase 6)**: Crimson-sea hero highlight with incandescent shorelines.

Execute batch generation:
```bash
bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" batch clips.json --parallel 1
```

*Mandatory Clean-Up*: Remove the Gemini watermark from each clip before compositing:
```bash
ffmpeg -i shot01.mp4 -vf "delogo=x=1130:y=570:w=63:h=63" -c:a copy shot01_clean.mp4
ffmpeg -i shot02.mp4 -vf "delogo=x=1130:y=570:w=63:h=63" -c:a copy shot02_clean.mp4
ffmpeg -i shot03.mp4 -vf "delogo=x=1130:y=570:w=63:h=63" -c:a copy shot03_clean.mp4
```

### Step 4: Build Route Graphics
- Draw the vector path in your compositor (After Effects, Remotion, HyperFrames, or FFmpeg overlay).
- Apply a trim-path animation (start 0% to 100% between `06.4s` and `08.2s`).
- Color: Neon Cyan `#00F2FE` (3px core stroke, 8px outer soft glow at 60% opacity).
- Drop coordinate pins onto waypoint landmarks at the moment the route reaches them.

### Step 5: Add Clean Editorial Typography & Title Card
- **Phase 4 Title Card (`05.4s – 06.4s`)**: Off-white background (`#F8F7F4`), bold uppercase title (`#111315`), medium tracking (`+0.08em`), with a vermilion accent line (`#E63946`).
- **Phase 6 Hero Callouts (`08.2s – 10.0s`)**: High-contrast white pill badges with bold black lettering, thin pointer leader lines anchored to exact city coordinates.
- **Hold Duration**: Keep final callout badges stationary for at least 1.6–1.8 seconds. Never cut while labels are in motion.

### Step 6: Sound Design & Foley (Mandatory SFX Pipeline)
Execute through the 3-step SFX pipeline (`openverse-sfx` → `real-sfx` → `earshot`):
1. **Openverse Search**: Source CC0 recorded sounds:
   - Deep cinematic sub-rumble (45–60 Hz) for baseline scale.
   - Smooth airy wind whoosh for camera descent.
   - High-tech frequency sweep + relay click for map mode reset.
   - Clean tactile UI thud for title card impact.
   - Crisp mechanical clock ticks for pin drops.
   - Resonant cinematic sub-boom with warm string decay for the crimson hero reveal.
2. **Real-SFX Placement**: Position each sound effect at its exact millisecond cue frame; balance levels with `--duck` to preserve voiceover headroom.
3. **Earshot Verification**: Run `python -m earshot rank` and `earshot critique` to verify clean spectral balance and impact.

---

## 4. Quality Checklist: What Makes It Work

Before finalizing any 3D atlas reel, audit against these 5 pillars:

- [ ] **Geography**: Coastlines, peninsulas, mountain ranges, and city pin locations are verified against a real geographic map. No inverted or hallucinated landmasses.
- [ ] **Continuity**: The camera maintains one dominant vector heading (e.g. forward dolly-in with subtle diagonal drift). Never introduce sudden disorienting axis flips or rapid whip-pans.
- [ ] **Legibility**: One clean geometric sans/grotesk family (Inter, Neue Haas Grotesk, Roboto Mono). High contrast against relief terrain. Zero garbled AI glyphs.
- [ ] **Layering Order**: Strict depth hierarchy:
  `Terrain Elevation` ➔ `Drifting Atmosphere/Clouds` ➔ `Vector Route Path` ➔ `Pins & Cards` ➔ `Typography Callouts`.
- [ ] **Pacing Rhythm**: Every 1.0–2.0 seconds introduces a new visual state or information reveal (Wide ➔ Descent ➔ Map Mode ➔ Title Card ➔ Dark Route ➔ Crimson Hero).

---

## 5. Universal Prompt Template

Use this starter prompt template when directing Nexabot / Gemini Omni Flash / Veo:

```text
Cinematic 10-second 3D relief-map reel about [REGION]. Begins with a wide oblique aerial view at a 50-degree angle with soft drifting cloud decks, then glides smoothly toward [LANDMARK MOUNTAIN RANGE]. Briefly transitions to a simplified dark slate map, revealing a tactical route-planning view with a smoothly drawing cyan path and coordinate location pins, then finishes on a richly textured relief map where the sea turns deep crimson red with incandescent glowing shorelines around [ANCHOR PLACE 1], [ANCHOR PLACE 2], and [ANCHOR PLACE 3]. Continuous forward camera motion, plausible physical geography, directional low-raking elevation sunlight, restrained lighting, and minimal UI space. Clean terrain surface with no rendered text, no synthetic grids, 24fps.
```

---

## 6. Mandatory Workspace Rules & File Management

- **All AI Generation**: Exclusively through the user's Nexabot client (`bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}"`). Never call paid third-party APIs.
- **All SFX**: Exclusively through `openverse-sfx` ➔ `real-sfx` ➔ `earshot`.
- **Narration & Text**: English by default.
- **Google Drive Archival**: Every generated atlas reel must be synced immediately to Google Drive under:
  `AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>` (e.g., `AI VIDEO -> NOV 2026 -> Mediterranean 3D Atlas Reel`).

---

## 7. Supporting Resources in this Skill

- Detailed Design Study & Layer Breakdown: [references/atlas_field_guide.md](references/atlas_field_guide.md)
- Curated Regional Prompt Formulas: [references/prompt_playbook.md](references/prompt_playbook.md)
- Complete 10s Mediterranean Production Example: [examples/mediterranean_expedition_example.md](examples/mediterranean_expedition_example.md)
- Automation Manifest Generator Script: [scripts/create_atlas_manifest.py](scripts/create_atlas_manifest.py)
