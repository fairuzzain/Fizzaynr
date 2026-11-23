#!/usr/bin/env bash
# Ikon TAMBAHAN dari npm ke build/icon/ sebagai SVG (butuh internet).
# Phosphor FILL sudah ikut di skill dan ditulis otomatis oleh assemble.py; skrip ini hanya untuk
# bobot lain, set lain (lucide), atau logo merek kecil (LobeHub / simple-icons).
#
#   bash fetch_icons.sh phosphor regular arrow-right check play-circle
#   bash fetch_icons.sh phosphor fill   sparkle paper-plane-tilt
#   bash fetch_icons.sh iconify  lucide sparkles wand-2 clapperboard
#   bash fetch_icons.sh brand    google-color claude-color openai
#   bash fetch_icons.sh simple   instagram tiktok youtube
#
# Hasil dipakai lewat icon('nama', ukuran, warna) di template.
set -euo pipefail
OUT="${ICON_OUT:-${BUILD:-build}/icon}"
mkdir -p "$OUT"
MODE="${1:-}"; shift || true

npm_need() { [ -d "node_modules/$1" ] || npm i -s --no-audit --no-fund "$1"; }

case "$MODE" in
  phosphor)
    WEIGHT="${1:-regular}"; shift || true
    npm_need "@phosphor-icons/core"
    SRC="node_modules/@phosphor-icons/core/assets/$WEIGHT"
    [ -d "$SRC" ] || { echo "bobot '$WEIGHT' tidak ada. Pilih: thin light regular bold fill duotone"; exit 1; }
    for n in "$@"; do
      f="$SRC/$n.svg"; [ -f "$f" ] || f="$SRC/$n-$WEIGHT.svg"
      if [ -f "$f" ]; then cp "$f" "$OUT/$n.svg"; echo "ok  $n"
      else echo "TIDAK ADA  $n"; ls "$SRC" | grep -i "${n%%-*}" | head -5 | sed 's/^/     mirip: /'; fi
    done ;;
  iconify)
    SET="${1:-}"; shift || true
    [ -n "$SET" ] || { echo "sebutkan set, misalnya lucide atau mdi"; exit 1; }
    npm_need "@iconify-json/$SET"
    node "$(dirname "$0")/iconify2svg.js" "$SET" "$OUT" "$@" ;;
  brand)
    npm_need "@lobehub/icons-static-svg"
    SRC="node_modules/@lobehub/icons-static-svg/icons"
    for n in "$@"; do
      if [ -f "$SRC/$n.svg" ]; then cp "$SRC/$n.svg" "$OUT/$n.svg"; echo "ok  $n"
      else echo "TIDAK ADA  $n"; ls "$SRC" | grep -i "${n%%-*}" | head -5 | sed 's/^/     mirip: /'; fi
    done ;;
  simple)
    npm_need "simple-icons"
    SRC="node_modules/simple-icons/icons"
    for n in "$@"; do
      if [ -f "$SRC/$n.svg" ]; then cp "$SRC/$n.svg" "$OUT/$n.svg"; echo "ok  $n"
      else echo "TIDAK ADA  $n"; ls "$SRC" | grep -i "${n%%-*}" | head -5 | sed 's/^/     mirip: /'; fi
    done ;;
  *)
    sed -n '2,12p' "$0"; exit 1 ;;
esac
echo "-> $OUT"
