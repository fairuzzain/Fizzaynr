# ACBEATZ / MH8 AI Music Production Suite

Universal AI Music Production skill compatible with:
- **Claude Code** (`~/.claude/skills/acbeatz-mh8`)
- **OpenAI Codex / ChatGPT Code** (`~/.codex/skills/acbeatz-mh8`)
- **Google Antigravity & Gemini CLI** (`~/.gemini/config/skills/acbeatz-mh8` & `~/.gemini/skills/acbeatz-mh8`)

## What This Skill Does
Constructs production-ready Suno prompts using the ACBEATZ MH8 framework:
- Hardware-modeled mastering chains (SSL 4000 G-Bus, Neve 88RS/1073, Pultec EQP-1A, API 2500, Manley)
- Drum architecture (MH8-PRO-DRUMS) and 808 sub-bass hooks (MH8-BASS-BANGERS)
- Low-end mono protection (`[Stereo Rule: Keep Bass Mono | sub centered]`)
- Vocal timbre profiles and section dynamics
- Structured lyric writing with syllable cadence (8–12 syllables) and phonetic rhyme families
- Validated style prompts under 1,000 characters

## File Structure
```
acbeatz-mh8/
├── SKILL.md            # Universal skill specification & instructions
├── CLAUDE.md           # Quick guide for Claude Code
├── AGENTS.md           # Quick guide for OpenAI Codex / ChatGPT Code
├── README.md           # This file
├── scripts/
│   └── mh8_tools.py    # Zero-dependency CLI for hook search & prompt validation
└── references/         # 7 core reference knowledge files
    ├── MH8-FuLL STACK=PRO-AI-MUSIC-PRODUCTION-BUNDLE_MASTER_2026-01-31.md
    ├── MH8 EXPANSION PK MASTERS SSL NEVE PULTECH API-2-1-2026.txt
    ├── MH8-BASS-BANGERS-PRO BASS PK V1.0.txt
    ├── MH8-PRO-DRUMS-250 + PACK-JSON- V3.0 Masters Series.txt
    ├── SUNO VOCAL REFRENCE UPLOADS INSTRUCTIONS + QUICK PROMPT INSTRUCTIONS.txt
    ├── Suno-knowledge files lyrics instructions.txt
    └── [Suno Knowledge files continued].txt
```
