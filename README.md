# Fizzaynr

Claude Code skills, installed under `.claude/skills/` (auto-loaded as project skills when this repo is opened in Claude Code).

## Skills (21)
anidoodle · animated-chart · apple-launch-film · codex-image · collage-motion · launch-video · loop-cover · milestone-reveal · newsletter-promo · recap-reel · reel-export · title-sequence-3d · title-to-motion-video · travelcut · video-3d · video-3d-toons · vox · vox-colored · vox-colored-nexabot · watch · window-pass-through

## Project files
- `assets/style_reference_colored.png` and `guidelines/colored/` — used by `vox-colored-nexabot` (paths are relative to the repo root).

## Setup (any machine)
1. `cp .env.example .env` and add `NEXABOT_API_KEY`, `OPENAI_API_KEY`, `OPENAI_IMAGE_API_KEY`, `SUB2API_API_KEY` (only change other values when your environment changes).
2. Put the external kits in `vendor/` (see `vendor/README.md`) or point to them in `.env`.
3. Run `bash tools/check_env.sh` to see what is ready.

Outputs go to `runs/` (git-ignored). Path rules for all skills: see `CLAUDE.md`.

Images use ChatGPT (`codex-image/openai_image.py`); bulk writing goes to `tools/llm.py` (ChatGPT, then Claude via Sub2API). See `CLAUDE.md`.
