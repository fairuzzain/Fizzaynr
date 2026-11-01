#!/usr/bin/env bash
# Reports which dependencies the skills in this repo can find. Usage: bash tools/check_env.sh
ROOT="$(git rev-parse --show-toplevel)"; cd "$ROOT"
set -a; [ -f .env ] && . ./.env; set +a
ok(){ printf '  [ok]   %s\n' "$1"; }; no(){ printf '  [MISS] %s  -> %s\n' "$1" "$2"; }
chk(){ [ -e "$2" ] && ok "$1 ($2)" || no "$1 ($2)" "$3"; }
cmd(){ command -v "$1" >/dev/null && ok "$1" || no "$1" "$2"; }
echo "Repo: $ROOT"
echo "Tools:"; cmd ffmpeg "install ffmpeg"; cmd ffprobe "install ffmpeg"; cmd python3 "install Python 3"; cmd node "install Node.js"; cmd bun "install bun (runs nexabot.ts)"
echo "Kits:"
chk "Nexabot client" "${NEXABOT_TS:-vendor/Motion_as_kit/nexabot/nexabot.ts}" "copy Motion_as_kit into vendor/ or set NEXABOT_TS"
chk "Motion as Code kit" "${MOTION_KIT:-vendor/Motion_as_kit}" "set MOTION_KIT"
chk "video-3d kit" "${VIDEO3D_KIT:-vendor/video-3d-kit}" "set VIDEO3D_KIT"
chk "vox (B&W) skill" "${VOX_SKILL:-.claude/skills/vox-video-nexabot/SKILL.md}" "add vox-video-nexabot skill (or use /vox-colored)"
echo "Keys:"
{ [ -n "$NEXABOT_API_KEY" ] || [ -f "${NEXABOT_KEY_FILE:-${MOTION_KIT:-vendor/Motion_as_kit}/.env.nexabot}" ]; } && ok "Nexabot key" || no "Nexabot key" "set NEXABOT_API_KEY in .env"
echo "Vox colored:"
chk "style reference" assets/style_reference_colored.png ""; chk "prompt guidelines" guidelines/colored ""
[ -n "$(ls -A "${MUSIC_DIR:-assets/music}" 2>/dev/null | grep -v .gitkeep)" ] && ok "music tracks" || no "music tracks (${MUSIC_DIR:-assets/music})" "add .mp3/.wav files"
{ [ -x .venv/bin/python ] || [ -x .venv/Scripts/python ]; } && ok ".venv" || no ".venv" "python -m venv .venv && <venv python> -m pip install requests python-dotenv faster-whisper"
echo "Images API (codex-image fallback):"
[ -n "$OPENAI_API_KEY" ] && ok "OPENAI_API_KEY" || no "OPENAI_API_KEY" "set it in .env"
echo "Codex CLI (optional, Windows):"
command -v codex >/dev/null && ok "codex CLI" || no "codex CLI" "install Codex CLI"
if [ -f ~/.codex/config.toml ]; then cmp -s ~/.codex/config.toml config/codex/config.toml && ok "~/.codex/config.toml matches repo" || no "~/.codex/config.toml differs from repo" "cp config/codex/config.toml ~/.codex/"; else no "~/.codex/config.toml" "cp config/codex/config.toml ~/.codex/"; fi
