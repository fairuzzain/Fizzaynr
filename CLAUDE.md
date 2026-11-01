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

## Defaults
- Images: Nexabot `img`; `codex-image` only as fallback (reference images, key sheets, Nexabot failure).
  The fallback runs `.claude/skills/codex-image/openai_image.py` (Images API, `OPENAI_API_KEY`,
  provider `space.stationine.com`). Codex CLI (`config/codex/config.toml`) is Windows-only and
  cannot use that key (no chat model on it).
- Video clips and music: Nexabot. Do not switch to paid video connectors.
- Never put API keys in chat or commit `.env`.

## Before a run
`bash tools/check_env.sh` lists what is missing (kits in `vendor/`, keys, ffmpeg, bun, .venv).
If a skill's kit is missing, tell the user in one line what to install and stop.
