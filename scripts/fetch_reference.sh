#!/usr/bin/env bash
# Download the reference cut for local comparison only (gitignored; not redistributed).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q yt-dlp >/dev/null 2>&1 || true
python3 -m yt_dlp -o "reference/ref.%(ext)s" --merge-output-format mp4 "${1:-https://www.instagram.com/p/Dd66aLqCbO6/}"
