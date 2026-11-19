---
name: whisper
description: "Transcribe audio and video files into text, subtitles (SRT, VTT), or word-level timestamped JSON using OpenAI Whisper and faster-whisper. Use when user asks to transcribe audio, generate subtitles, extract speech to text, generate word timestamps, or run whisper."
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

# Whisper Speech Recognition & Subtitle Generator

Transcribe spoken speech from video or audio files locally with high accuracy and word-level timestamps.

## CLI Usage (OpenAI Whisper)

Make sure `PYTHONIOENCODING=utf-8` is set:

```powershell
# Transcribe to SRT and VTT
whisper "input.mp4" --model base --output_format srt --output_dir "./subtitles"

# Transcribe with word timestamps (JSON)
whisper "input.wav" --model small --word_timestamps True --output_format json --output_dir "./build"

# Transcribe specific language (e.g. English or Malay)
whisper "audio.mp3" --model medium --language en
```

## Python API (faster-whisper - 4x faster)

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5, word_timestamps=True)

print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    for word in segment.words:
        print(f"  {word.start:.2f}s - {word.end:.2f}s: {word.word}")
```

## Model Selection
- **tiny / base**: Extremely fast, low memory (~1GB RAM), great for quick drafts and clear audio.
- **small / medium**: High accuracy for conversational speech and background music.
- **large-v3**: Maximum accuracy, multi-lingual, and accents.
