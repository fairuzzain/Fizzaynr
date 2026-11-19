---
name: motion-clone
description: "Reconstruct reference videos into editable HyperFrames motion graphics projects using MotionClone. Use when the user shares a reference video link or file and asks to \"clone motion\", \"recreate motion\", \"rebuild this animation\", \"reverse-engineer video into code\", or invoke MotionClone. Rebuilds typography, shapes, and motion into an editable HyperFrames project."
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

# MotionClone

Reconstructs reference video into editable HyperFrames motion graphics.

## Project Location
Installed at: `${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/MotionClone`

## How to Run MotionClone
1. Open terminal and navigate to:
   `powershell
   cd "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/MotionClone"
   .\start.ps1
   `
2. The web interface opens at `http://127.0.0.1:4319`.
3. Upload a reference video (up to 120s, 250MB) or paste a public video link.
4. Click **Rebuild video**.
5. Once completed, compare the rebuilt animation side-by-side with the reference.
6. Download the editable HyperFrames project ZIP.

## Editing the Exported HyperFrames Project
1. Extract the project into its own folder.
2. Run `npm install`.
3. Modify copy, colors, typography, or timing in `project.json` or `scene-*.js`.
4. Preview with `npm run preview` and render final MP4 with `npm run render`.
