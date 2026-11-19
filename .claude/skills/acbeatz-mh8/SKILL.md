---
name: acbeatz-mh8
description: ACBEATZ / MH8 AI Music Production Suite. Constructs professional Suno style prompts using bracket metatags, hardware mastering chains (SSL, Neve, Pultec, API), drum & 808 bass packs, vocal timbre profiling, and structured lyric engineering.
---

# ACBEATZ / MH8 AI Music Production Suite

The ACBEATZ / MH8 suite provides structured, studio-grade AI music production architecture for Suno (v3/v4/v5/v6). It utilizes deterministic bracket hooks, console-modeled mastering chains, dedicated bass/drum sound modules, and vocal timbre engineering to produce clean, punchy, translation-safe audio.

---

## 1. Quick Prompt & Style Box Architecture

Suno's Style Box has a strict limit of **< 1,000 characters**. Construct prompts using modular bracket hooks:

### Standard Blueprint
```text
[Genre: Subgenre] [Vocal: Delivery & Chain] [Drums: MH8 Drum Profile] [Bass: MH8 Bass Profile] [Stereo Rule: Keep Bass Mono | sub centered] [EQ: Clarity & Low-End Directives] [Master: Hardware Chain & LUFS Target]
```

### Example Style Prompts
- **Modern Radio Pop**:
  `[Pop: Modern Radio] [Vocal: Up Front | de-ess smooth | short plate] [Drums: Punchy | tight transient] [Bass: Clean | smooth | stable] [Stereo Rule: Keep Bass Mono | sub centered] [EQ: Remove Mud | 200–400Hz cleanup] [EQ: Air Boost | 10k+ sparkle] [Master: SSL 4000 G-Bus Glue | Target -14 LUFS | True Peak -1.0dB]`

- **Aggressive 808 Trap**:
  `[Trap: Modern] [Vocal: Autotune Hard | stylized effect] [Kick: Trap Bounce] [808: Glide | sliding notes | tune to song key] [Sidechain: Kick To Bass | clear groove] [EQ: Tight Low End | reduce boom | clean sub] [Stereo Rule: Keep Bass Mono | sub centered] [Master: Loud Modern | Target -10 LUFS | True Peak -1.0dB]`

- **Lo-Fi Study Beats**:
  `[Lo-Fi: Dusty Vinyl] [Vocal: Intimate Close | dry | breath detail] [Drums: Dry Tight | modern | close] [Bass: Clean | smooth | stable] [Saturation: Tape | warm glue | soft peaks] [EQ: Dark Top End | smoother | less fizz] [Reverb: Short Room | tight space] [Master: Streaming | Target -14 LUFS | True Peak -1.0dB]`

- **Festival EDM / Melodic Drop**:
  `[EDM: Festival] [Build: Snare Roll] [Drop: Beat Switch] [Sidechain: Pumping | EDM-style movement] [Stereo: Wide Chorus | widen backs + pads] [Transient Shaper: More Attack | punch up] [Clipper: Transparent | protect peaks] [Master: Club Loud | Target -8 LUFS | True Peak -0.8dB]`

---

## 2. Hardware Mastering Chains & Loudness Targets

Use brand-name hardware modeling hooks in the style prompt to shape tonal balance:

### Hardware Console Chains
- **SSL 4000 G-Bus Glue**:
  `[Master: SSL 4000 G-Bus Glue | 4:1 Ratio | 30ms Attack | Auto Release | 2dB Gain Reduction]`
- **Neve 88RS / 1073 Warmth**:
  `[Master: Neve Console Warmth | Transformer Harmonics | Smooth Low-Mids | Round Highs]`
- **Pultec EQP-1A Low-End & Air**:
  `[EQ: Pultec Low End Trick | 60Hz Boost + Attenuate | 16kHz Silk Air Boost]`
- **API 2500 Punch**:
  `[Master: API 2500 Thrust | Loud Punch | Medium Attack | Fast Release | Hard Knee]`
- **Manley Tube Polish**:
  `[Manley Massive Passive: Broad Tone | gentle | hi-fi] [Manley Vari-Mu: Glue | slow | smooth]`

### Target Loudness Standards
- **Streaming Platforms (Spotify, Apple Music, YouTube)**:
  `[Master: Streaming | Target -14 LUFS | True Peak -1.0dB]`
- **Loud Modern (Pop, Trap, Hip-Hop, Modern Rock)**:
  `[Master: Loud Modern | Target -10 LUFS | True Peak -1.0dB]`
- **Club / Festival Loud (EDM, Techno, Bass House)**:
  `[Master: Club Loud | Target -8 LUFS | True Peak -0.8dB]`

---

## 3. MH8 Sound Modules: Bass & Drums

### MH8-BASS-BANGERS (808 & Sub Systems)
- **Stereo Mono Rule (Mandatory)**: `[Stereo Rule: Keep Bass Mono | sub centered]`
- `[808: Glide | sliding notes | tune to song root]`
- `[808: Short Tight | punchy transient]`
- `[808: Saturated | warm tape harmonics | audible on mobile]`
- `[Low-end Sidechain: Kick To Bass | 2–4dB ducking | clean transient punch]`
- `[Bass: Mid Bass Forward | audible on phone speakers]`

### MH8-PRO-DRUMS
- `[Drums: Punchy | tight transient]`
- `[Drums: Boom Bap | dusty | snare-forward]`
- `[Drums: Drill Hats | sliding | sharp rolls]`
- `[Kick: Click Attack | cut through mix]`
- `[Snare: Cracked | high snap | rimshot layer]`
- `[Drum Bus: Parallel Smash | 10:1 Ratio | blend 20% for body]`

---

## 4. Vocal Timbre Profiles & Extraction

When shaping vocals or referencing vocal stems:
- **Intimate Pop / Indie**: `[Vocal: Intimate Close | dry | breath detail | subtle de-ess]`
- **Airy Radio Hook**: `[Vocal: Airy Pop | clean highs | tight comp | short plate]`
- **Heavy Stylized / Autotune**: `[Vocal: Autotune Hard | stylized effect | doubler width]`
- **Soul / Gospel Power**: `[Vocal: Belt Pop | big chorus | controlled dynamics | gospel stack]`
- **Warm Narrative**: `[Vocal: Baritone Warm | thick chest resonance | forward]`

---

## 5. Structured Lyrics Engineering

When writing or structuring song lyrics:
1. **Explicit Section Tags**:
   `[Intro: 4 Bars]`, `[Verse 1]`, `[Pre-Chorus: Build]`, `[Chorus: Full Send]`, `[Post-Chorus]`, `[Verse 2]`, `[Bridge: Contrast]`, `[Drop: Beat Switch]`, `[Guitar Solo]`, `[Outro: Hard Stop]`, `[End]`.
2. **Meter & Syllable Discipline**:
   - 8–12 syllables per line for pop/rock melodic balance.
   - Match syllable count across paired rhyming lines for consistent rhythm.
3. **Phonetic Hook Vowel Holds**:
   - Use long, resonant vowel families for chorus hooks: `-ight` (light, flight), `-ove` (love, above), `-ain` (rain, pain), `-ore` (roar, more), `-ear` (clear, fear).
4. **Performance Annotations**:
   - `(ad-lib: echo)`, `(whisper)`, `[Beat Switch]`, `[Silence Before Drop]`.

---

## 6. Helper CLI Tool (`mh8_tools.py`)

The skill provides a fast search and prompt validation CLI:

```powershell
# Search for bracket hooks:
python "$ROOT/.claude/skills/acbeatz-mh8/scripts/mh8_tools.py" search "pultec"
python "$ROOT/.claude/skills/acbeatz-mh8/scripts/mh8_tools.py" search "808 glide"
python "$ROOT/.claude/skills/acbeatz-mh8/scripts/mh8_tools.py" search "master"

# Validate a Suno style prompt:
python "$ROOT/.claude/skills/acbeatz-mh8/scripts/mh8_tools.py" validate "[Pop: Modern] [Master: SSL 4000 G-Bus Glue] [Stereo Rule: Keep Bass Mono]"
```

---

## 7. Knowledge Base References

The 7 core music production reference files are preserved in `references/`:
1. `MH8-FuLL STACK=PRO-AI-MUSIC-PRODUCTION-BUNDLE_MASTER_2026-01-31.md` (Master hook catalog, styles, mixing chains)
2. `MH8 EXPANSION PK MASTERS SSL NEVE PULTECH API-2-1-2026.txt` (Console mastering chains)
3. `MH8-BASS-BANGERS-PRO BASS PK V1.0.txt` (808 and sub-bass library)
4. `MH8-PRO-DRUMS-250 + PACK-JSON- V3.0 Masters Series.txt` (Drum sound sets)
5. `SUNO VOCAL REFRENCE UPLOADS INSTRUCTIONS + QUICK PROMPT INSTRUCTIONS.txt` (Vocal timbre guidance)
6. `Suno-knowledge files lyrics instructions.txt` (9 lyrical style templates)
7. `[Suno Knowledge files continued].txt` (Rhyme families & phonetic notes)
