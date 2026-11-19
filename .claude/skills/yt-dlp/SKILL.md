---
name: yt-dlp
description: "Download video and audio streams from YouTube, Vimeo, Twitter/X, TikTok, and thousands of other platforms using yt-dlp. Use when the user asks to download a video, extract audio from a URL, download subtitles/captions, inspect stream formats, or retrieve video metadata."
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

# yt-dlp Video & Audio Downloader

Fast and flexible command-line media downloader for YouTube, Vimeo, TikTok, X/Twitter, Instagram, and 1,000+ sites.

## Common Operations

### 1. Download Best Quality Video (MP4)
```powershell
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b" --merge-output-format mp4 "<URL>" -o "%(title)s.%(ext)s"
```

### 2. Extract Audio (MP3 / WAV)
```powershell
# Extract MP3 (highest quality)
yt-dlp -x --audio-format mp3 --audio-quality 0 "<URL>" -o "%(title)s.%(ext)s"

# Extract WAV (lossless for video editing / Whisper)
yt-dlp -x --audio-format wav "<URL>" -o "%(title)s.%(ext)s"
```

### 3. Download Subtitles / Captions
```powershell
# List available subtitles
yt-dlp --list-subs "<URL>"

# Download auto-generated or manual subtitles (VTT / SRT) without downloading video
yt-dlp --write-auto-subs --write-subs --sub-lang "en,ms" --sub-format srt --skip-download "<URL>"
```

### 4. Inspect Available Formats
```powershell
yt-dlp -F "<URL>"
```

### 5. Download Clip Range (Time-sliced)
```powershell
yt-dlp --download-sections "*00:01:15-00:01:45" "<URL>" -o "clip.%(ext)s"
```
