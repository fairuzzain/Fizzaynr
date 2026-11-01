# Codex CLI config (used by the `codex-image` skill)

`config.toml` points Codex at the `space.stationine.com` provider (model `gpt-5.5`). No keys are stored here.

Install on a machine (once, or again when the environment changes):

```bash
mkdir -p ~/.codex && cp config/codex/config.toml ~/.codex/config.toml          # macOS / Linux / Git Bash
```
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex" | Out-Null
Copy-Item config\codex\config.toml "$env:USERPROFILE\.codex\config.toml"      # Windows PowerShell
```

Then sign in once with `codex login` (`requires_openai_auth = true`). Auth is stored in
`~/.codex/auth.json` on that machine, never in this repo. Keep a backup of your old
`~/.codex/config.toml` if you had one.
