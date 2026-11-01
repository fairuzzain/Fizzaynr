#!/usr/bin/env bash
# Run Claude Code itself on the Sub2API Claude key instead of your Claude plan.
# Usage: bash tools/claude-sub2api.sh [claude args...]     (model: CLAUDE_SUB2API_MODEL, default claude-sonnet-4-6)
ROOT="$(git rev-parse --show-toplevel)"; set -a; [ -f "$ROOT/.env" ] && . "$ROOT/.env"; set +a
[ -n "$SUB2API_API_KEY" ] || { echo "SUB2API_API_KEY is not set in $ROOT/.env"; exit 1; }
export ANTHROPIC_BASE_URL="${SUB2API_ANTHROPIC_BASE_URL:-https://space.stationine.com}"
export ANTHROPIC_AUTH_TOKEN="$SUB2API_API_KEY"
export ANTHROPIC_MODEL="${CLAUDE_SUB2API_MODEL:-claude-sonnet-4-6}"
export ANTHROPIC_SMALL_FAST_MODEL="${CLAUDE_SUB2API_FAST_MODEL:-claude-haiku-4-5}"
exec claude "$@"
