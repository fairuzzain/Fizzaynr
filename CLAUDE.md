# Fizzaynr — skills repo

All skills live in `.claude/skills/` and are written to run **from this repo**, on Windows (Git Bash),
macOS or Linux. Paths are repo-relative by default; change them only through environment
variables (`.env` at the repo root, see `.env.example`) when the environment changes.

## Path convention (every skill)
- `ROOT` = repo root: `git rev-parse --show-toplevel`. Load overrides with
  `set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a`.
- Nexabot client: `${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}` (run with `bun`).
- Motion as Code kit: `${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}`; video-3d kit: `${VIDEO3D_KIT:-$ROOT/vendor/video-3d-kit}`.
- Skill scripts: `$ROOT/.claude/skills/<skill>/scripts`.
- Outputs: `${RUNS_DIR:-$ROOT/runs}/<skill>/<slug>` (git-ignored). Music: `${MUSIC_DIR:-$ROOT/assets/music}`.
- Never write machine-specific absolute paths (`C:\Users\...`, `D:\Motion Claude\...`) into skills.

## Bahasa (semua skill)
- **Bahasa utama: Bahasa Melayu Malaysia** untuk semua output dan perbualan: skrip, VO/TTS, dialog,
  caption, teks atas skrin, CTA, tajuk, kapsyen, soalan dan laporan kepada pengguna.
- Ejaan dan kosa kata Malaysia, bukan Indonesia (contoh: *tak, nak, awak, tengok, percuma, kat*;
  bukan *gak, mau, kamu, lihat, gratis, di sini*). Mata wang RM, format nombor `ms-MY`.
- Transkripsi/ASR dan TTS: kod bahasa `ms` secara default (`--lang ms`, `TTS_LANGUAGE=ms`).
- **VO/TTS: `python tools/tts.py --text-file skrip.txt --out <run>/vo.mp3 --words <run>/words.json`**
  (1) **Gemini TTS dahulu** (`GEMINI_API_KEY`, `gemini-3.8-flash-tts`, suara `Puck`); (2) **Nexabot
  `POST /api/v1/voice`** sebagai sandaran (suara ElevenLabs/MiniMax yang menyokong `ms`, default Adrian;
  pulangkan timestamp perkataan). `--provider nexabot` untuk paksa Nexabot.
  - Gemini membaca arahan gaya dengan kuat: hantar teks skrip sahaja. Tiada timestamp: dapatkan masa
    dengan `wordtime.py --lang ms` (semak; kalau tak stabil, agih masa ikut blok senyap).
  - Mode Nexabot `tts` biasa (suara Gemini Puck/Charon di Nexabot) menolak teks BM; suara pustaka
    ElevenLabs di luar senarai Nexabot gagal (500). Jangan guna suara `id-ID-*` (Indonesia).

## Defaults
- **Images: ChatGPT images** for every skill — `python "$ROOT/.claude/skills/codex-image/openai_image.py"`
  (gpt-image models, `OPENAI_IMAGE_API_KEY`). Nexabot `img` only if it fails twice.
- Video clips and music: Nexabot. TTS: `tools/tts.py` (Gemini first, Nexabot fallback). Do not switch to paid video connectors.
- Never put API keys in chat, print them, or commit `.env`.

## Use Claude Code as little as possible (delegate the writing)
Claude Code plans, runs commands, checks results and talks to the user. Bulk text work goes to
`python tools/llm.py` (ChatGPT first, then Claude via Sub2API on rate limits or errors):
- Drafting scripts, voiceovers, narration, captions, beat sheets, prompt lists, image/video prompts,
  translations, research summaries, rewrites — anything longer than a few lines.
- Write the brief to a file, run `python tools/llm.py --prompt-file brief.md --out <run>/draft.md`,
  then skim and fix only what is wrong; do not regenerate the whole thing in Claude Code.
- Keep skill rules in the brief: paste the relevant guideline text (style blocks, word limits,
  public-figure rules) into it so the delegate follows them.
- If both providers fail, say so in one line and only then write it yourself.
- `codex` / `codex --profile claude` (config in `config/codex/`) can take whole coding sub-tasks.
- To run Claude Code itself on the Sub2API key instead of the Claude plan: `bash tools/claude-sub2api.sh`.

## Before a run
`bash tools/check_env.sh` lists what is missing (kits in `vendor/`, keys, ffmpeg, bun, .venv).
If a skill's kit is missing, tell the user in one line what to install and stop.
