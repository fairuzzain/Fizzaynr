#!/usr/bin/env bash
# Join clips into one film, re-encoded to the first clip's size/fps so mismatched clips still join.
# Usage: join.sh <out.mp4> <clip1.mp4> <clip2.mp4> [...]
set -euo pipefail
out="${1:?out.mp4}"; shift; [ "$#" -ge 2 ] || { echo "need 2+ clips"; exit 1; }
IFS=, read -r W H FPS < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$1")
args=(); f=""; i=0
for c in "$@"; do
  args+=(-i "$c")
  if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$c" | grep -q .; then a="[$i:a]aresample=48000,aformat=channel_layouts=stereo[a$i];"
  else a="anullsrc=r=48000:cl=stereo,atrim=duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$c")[a$i];"; fi
  f+="[$i:v]scale=$W:$H:force_original_aspect_ratio=decrease,pad=$W:$H:(ow-iw)/2:(oh-ih)/2,fps=$FPS,setsar=1,format=yuv420p[v$i];$a"
  i=$((i+1))
done
cat=""; for ((k=0;k<i;k++)); do cat+="[v$k][a$k]"; done
ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${cat}concat=n=$i:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
  -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k -movflags +faststart "$out"
echo "joined $i clips -> $out ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out") s)"
