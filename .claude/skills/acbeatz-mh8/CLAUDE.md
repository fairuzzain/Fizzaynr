# ACBEATZ / MH8 AI Music Production Suite (Claude Code Guide)

This skill equips Claude Code with the ACBEATZ MH8 production framework for Suno (v3/v3.5/v4/v5/v6).

## Activation Triggers
Activate this skill whenever the user asks for:
- Suno prompts, style tags, or bracket hooks
- Song lyrics, rhyming schemes, or song arrangements
- Mix and mastering chains (SSL, Neve, Pultec, API)
- Drum profiles (MH8-PRO-DRUMS) and 808/bass bangers (MH8-BASS-BANGERS)
- Vocal timbre profiles and section dynamics

## Core Rules for Claude
1. **Style Box Limit**: Always keep the Suno Style Box text under **1,000 characters**.
2. **Bracket Hook Metatags**: Use modular bracket tags:
   `[Genre: Subgenre] [Vocal: Delivery] [Drums: Profile] [Bass: Profile] [Stereo Rule: Keep Bass Mono | sub centered] [EQ: Directives] [Master: Hardware Chain & LUFS]`
3. **Low-End Mono Protection**: Always include `[Stereo Rule: Keep Bass Mono | sub centered]` to ensure mono-compatibility on phones, laptops, and club systems.
4. **Structured Lyrics**: Group lyrics using explicit section tags (`[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Guitar Solo]`, `[Outro]`, `[End]`) with consistent 8–12 syllable meters.
5. **Language Consistency**: Match the requested language 100% (Bahasa Melayu baku if Malay, English if English).

## Helper Tool
Run validation or search hooks directly in the terminal:
```bash
python scripts/mh8_tools.py search "<keyword>"
python scripts/mh8_tools.py validate "<style_prompt>"
```
