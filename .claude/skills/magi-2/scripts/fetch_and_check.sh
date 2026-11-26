#!/usr/bin/env bash
# Download a finished MAGI-2 result and check it.
# Usage: fetch_and_check.sh <result_url> <out.mp4> [expect_audio:1|0] [expect_seconds]
set -euo pipefail
url="${1:?result url}"; out="${2:?output mp4}"; want_audio="${3:-1}"; want_sec="${4:-}"
mkdir -p "$(dirname "$out")"
curl -fsSL --retry 4 --retry-delay 3 -o "$out" "$url"
command -v ffprobe >/dev/null || { echo "ffprobe missing - saved $out without checks"; exit 0; }

v=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$out")
a=$(ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 "$out" | head -1)
d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$out")
IFS=, read -r w h fps <<<"$v"
echo "file: $out"; echo "video: ${w}x${h} @ ${fps}  duration: ${d}s  audio: ${a:-none}"

fail=0
short=$(( w < h ? w : h ))
[ "$short" -ge 1080 ] || { echo "WARN: short side ${short}px < 1080 (MAGI-2 is 1080p only)"; fail=1; }
if [ "$want_audio" = 1 ] && [ -z "$a" ]; then echo "WARN: no audio stream but generate_audio was on"; fail=1; fi
if [ -n "$want_sec" ]; then
  awk -v d="$d" -v w="$want_sec" 'BEGIN{exit !((d-w)>-0.6 && (d-w)<0.6)}' \
    || { echo "WARN: duration ${d}s, expected ~${want_sec}s"; fail=1; }
fi
[ "$fail" = 0 ] && echo "OK"
exit "$fail"
