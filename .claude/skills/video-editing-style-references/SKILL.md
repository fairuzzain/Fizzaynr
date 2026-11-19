---
name: video-editing-style-references
description: "Reference guide and production recipes for 15 signature video editing styles across YouTube and Instagram (Vox, Johnny Harris, MagnatesMedia, Iman Gadzhi, Ali Abdaal, Imperial, Maximize, Devin Jatho, Arsacre, Natt Jongsala, GRAWX, Sam Kolder, Kurzgesagt, LEMMiNO, Metr Media). Use when asked to emulate, recreate, or style a video after any of these creators or channels."
---

# 15 Video Editing Style References & Directing Recipes

This skill encodes the visual grammar, pacing, typography, color grading, sound design, and composition rules for 15 top video editing styles across YouTube and Instagram.

---

## The 15 Signature Styles Matrix

| Creator / Brand | Core Genre & Editing Formula | Pacing & Motion | Typography & Graphics | Audio & SFX |
| :--- | :--- | :--- | :--- | :--- |
| **Vox** | Journalistic explainer, layered collages, archival diorama | Measured, steady, logical beat-driven | Clean sans-serif, highlighted text, animated 2D maps, newspaper clippings | Subtle paper rustles, camera clicks, subdued ambient beds |
| **Johnny Harris** | Visual journalism, hand-crafted paper cutouts, 3D camera maps | Kinetic, organic, zoom-punch cuts | Hand-drawn marker underlines, vintage maps, distressed borders, tape textures | Analog projector hum, typewriter clicks, deep resonant hits |
| **MagnatesMedia** | Cinematic business thriller / corporate rise & fall | Dramatic, tension-building, slow creeps to sudden drops | Gold/white serif titles, glowing drop shadows, dark vignettes | Deep sub-bass rumbles, orchestral brass, ticking clocks, metallic whooshes |
| **Iman Gadzhi** | High-production personal brand, luxury noir, motivational | Fast-paced retention cuts, whip pans, dynamic scales | Bold condensed grotesque, glowing accents, 3D text tracking | Crisp riser sweeps, high-impact thuds, modern trap/chillhop beats |
| **Ali Abdaal** | Clean educational, friendly productivity, bright studio | Conversational, smooth, punchy visual punch-ins | Bright colorful callouts, pastel cards, Notion-style UI cards, clean popups | Playful UI pops, gentle bells, upbeat background lo-fi |
| **Imperial** | Dark historical / investigative expose, atmospheric mystery | Slow ominous zooms, deliberate pauses, tension holds | Minimalist white serifs, red accent lines, redacted document overlays | Low drone ambiances, muffled heartbeats, distant wind |
| **Maximize** | Modern entrepreneurial breakdowns, retention-focused reels | High BPM cuts, speed ramps, kinetic scale pops | Neon accent text, stat badges, animated line graphs | Punchy swooshes, cash register rings, snappy snap sounds |
| **Devin Jatho** | Short-form social retention, hook-driven, high-energy | Under 1.5s cut interval, continuous motion loops | Huge screen-filling kinetic text, emoji popups, glowing bounding boxes | Rapid-fire whooshes, glitch impacts, viral audio accents |
| **Arsacre** | Aesthetic auteur editing, music-video transitions, fluid cuts | Frame-perfect beat matching, speed ramps, seamless whip cuts | Custom editorial fonts, motion-tracked floating labels, film overlays | Bass-boosted drops, reversed audio risers, immersive stereo panning |
| **Natt Jongsala** | Kinetic camera craft, seamless transitions, visual choreography | Fluid match cuts, rotation whip zooms, speed ramps | Minimal clean tracking text, sleek transparent HUD elements | Rhythmic foley, whip-pan swooshes, sharp impact snaps |
| **GRAWX** | High-octane motion graphics, cyberpunk / dark tech aesthetic | Aggressive, glitch cuts, explosive transitions | 3D extruded typography, neon wireframes, HUD overlays, glitch typography | Cyber risers, digital distortions, sub-bass braams, heavy gun-cock impacts |
| **Sam Kolder** | Cinematic travel epic, spiritual journey, sublime landscapes | Speed-ramp flow, sky match-cuts, drone reveal sweeps | Cinematic widescreen letterbox, understated centered tracking text | Ambient nature soundscapes, epic melodic risers, emotive piano/hybrid build |
| **Kurzgesagt** | Vector animation, cosmic philosophy, existential science | Smooth 60fps easing, playful morphs, geometric reveals | Custom bold rounded geometric fonts, vibrant pastel vector diagrams | Whimsical melodic synth score, duck quacks, cosmic whooshes, warm narration |
| **LEMMiNO** | Minimalist forensic documentary, investigative precision | Restrained, clinical, contemplative slow pan/tilts | Stark white sans-serif (Helvetica/Neue Haas), precise latitude/longitude, timer counters | Eerie ambient soundscapes, minimal bass pulses, distant radio static |
| **Metr Media** | Clean tech & business editorial, structured documentary | Smooth corporate rhythm, balanced b-roll interleaving | Modern corporate grid layout, subtle infographic charts, polished lower-thirds | Polished corporate acoustic/electronic bed, warm subtle whooshes |

---

## How to Apply Any Style to Your Video Project

When applying one of these styles:
1. **Pacing**: Follow the cut frequency (e.g., Devin Jatho <1.5s vs LEMMiNO 4-8s).
2. **Visual Treatment**: Align grading (warm vintage for Johnny Harris, dark high-contrast for MagnatesMedia/Iman Gadzhi, vibrant pastel for Kurzgesagt).
3. **Sound Design**: Always run audio through the mandatory SFX pipeline (`openverse-sfx` -> `real-sfx` -> `earshot`) matching the specific creator's sonic signature.
4. **Voice-Over Match**:
   - For Vox / Johnny Harris / MagnatesMedia / LEMMiNO: Lock **`Fenrir`** (`-i "Serious, commanding, cinematic documentary tone"`).
   - For Ali Abdaal / Devin Jatho / Maximize: Lock **`Fola`** or **`Puck`** (`-i "Bright, crisp, confident, engaging tone"`).
