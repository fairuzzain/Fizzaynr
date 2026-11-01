# Codex CLI config

`config.toml` has two profiles on the `space.stationine.com` provider; keys are read from the
environment (put them in the repo `.env`, never in this file):

| Command | Model | Key |
|---|---|---|
| `codex` | `gpt-5.5` (ChatGPT) | `OPENAI_API_KEY` |
| `codex --profile claude` | `claude-sonnet-4-6` (Sub2API) | `SUB2API_API_KEY` |

Install (back up your old `~/.codex/config.toml` first):

```bash
mkdir -p ~/.codex && cp config/codex/config.toml ~/.codex/config.toml         # macOS / Linux / Git Bash
set -a; . ./.env; set +a                                                      # load the keys
```
```powershell
Copy-Item config\codex\config.toml "$env:USERPROFILE\.codex\config.toml"     # Windows PowerShell
```

Images do not go through Codex: they use `.claude/skills/codex-image/openai_image.py`
(`OPENAI_IMAGE_API_KEY`).
