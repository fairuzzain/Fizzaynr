#!/usr/bin/env bash
# Connects NotebookLM to Claude Code (notebooklm-mcp-cli, MIT). Run on your own machine:
#   bash tools/setup_notebooklm.sh
# Needs uv (https://docs.astral.sh/uv/). Google cookies stay on this machine.
set -e
command -v uv >/dev/null || { echo "uv is missing: install it from https://docs.astral.sh/uv/ and rerun"; exit 1; }
command -v nlm >/dev/null || uv tool install notebooklm-mcp-cli
nlm login --check >/dev/null 2>&1 || nlm login          # opens a browser for one Google sign-in
claude mcp list 2>/dev/null | grep -q '^gemini-notebook-mcp:' \
  || claude mcp add --scope user gemini-notebook-mcp notebooklm-mcp
claude mcp list | grep gemini-notebook-mcp
echo 'Done. In Claude Code, ask: "List my notebooks", then ask a question and read the citations.'
