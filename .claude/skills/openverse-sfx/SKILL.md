---
name: openverse-sfx
description: Search and download free sound effects (5M+ CC-licensed sounds, mostly Freesound) from the Openverse API with no key. Use whenever a motion video, reel, explainer or edit needs a whoosh, hit, riser, pop, click, chime, typing, ambience or any recorded SFX, before generating one. Step 1 of the sound pipeline - Openverse -> real-sfx (placement and levels) -> earshot (judge, or make in code what is missing).
---
> [!IMPORTANT]
> **Mandatory Google Drive Sync Across All Video Skills**:
> Every video generated (AI video, music video, commercial, explainer, reel, story clip, reverse video, or motion graphic) MUST be organized and uploaded to **Google Drive** immediately upon generation/assembly.
> 
> **Hierarchy Structure:**
> `AI VIDEO` -> `<MONTH YYYY>` -> `<PROJECT TITLE>` (e.g. `AI VIDEO` -> `NOV 2026` -> `<PROJECT TITLE>`)
> 
> **Required Folder Assets:**
> - Final rendered/assembled video(s) (master MP4, compressed versions)
> - Source clips, assets, and raw recordings
> - Audio / VO files (`.wav`, `.mp3`)
> - Subtitle/caption files (`.ass`, `.srt`, `.json`)
> - Prompt manifests, batch files, and storyboard contact sheets
> - Generation / assembly scripts (`.py`, `.ts`, `.js`, `.html`)
> 
> **CLI Upload Commands:**
> `gdrive mutate mkdir "<PROJECT TITLE>" --parent <MONTH_FOLDER_ID>`
> `gdrive mutate upload "<FILE>" --parent <PROJECT_FOLDER_ID>`

# openverse-sfx

Script: `python -I "$ROOT/.claude/skills/openverse-sfx/openverse_sfx.py"` (no install, stdlib only).

```
openverse_sfx.py search "rising whoosh" --n 10 --max-dur 4      # list: duration, licence, title, id, tags
openverse_sfx.py get "rising whoosh" --n 3 --max-dur 4 --out <project>/sfx/whoosh
openverse_sfx.py id <uuid> --out <project>/sfx/whoosh              # one picked result
```

- Default licence filter is **cc0** (no credit needed). `--license commercial` adds CC-BY etc.; then credit
  the creators from `CREDITS.txt`, which every download appends to.
- Search is keyword-based and loose ("punchy whoosh" can return a snare): `search` first, read titles and tags,
  then `id` the right ones. Use concrete words (`swoosh`, `impact`, `riser`, `sub boom`, `mouse click`).
- Anonymous limit is roughly 100 requests a day; the API is sometimes slow (script retries 3x, 60 s each).
- Judge candidates with earshot (`earshot rank "<what you need>" <folder> --top 5`) instead of guessing from names.
- Shared starter library (registered in real-sfx as `openverse`): `${SFX_DIR:-$ROOT/assets/sfx}/<type>/`. Add
  good downloads there by type folder, then `python scripts/build_index.py` in the real-sfx skill folder.

## Pipeline
1. **Openverse** - find and download the recordings (this skill).
2. **real-sfx** - find the moments in the video, place each sound on its exact frame at the right level, mix.
3. **earshot** - check picks and the final mix; `earshot sfx` / `forge` only for a sound Openverse cannot supply.
