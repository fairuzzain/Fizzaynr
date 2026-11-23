#!/usr/bin/env bash
# Cek sumber mana yang bisa dijangkau dari sandbox ini.
# Jalankan SEKALI di awal proyek. Jangan mengulang request yang sudah ditolak.
set -u
probe() {
  printf "%-26s " "$1"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$2" 2>/dev/null)
  case "$code" in
    2*|3*) echo "BISA ($code)" ;;
    000)   echo "DITOLAK (proxy menolak koneksi)" ;;
    *)     echo "gagal ($code)" ;;
  esac
}
echo "=== Sumber yang dipakai skill ini ==="
probe "GitHub raw"      "https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/star.svg"
probe "GitHub releases" "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx"
probe "npm registry"    "https://registry.npmjs.org/gsap"
probe "PyPI"            "https://pypi.org/simple/numpy/"
echo
echo "=== Biasanya ditolak, cek kalau-kalau dilebarkan ==="
probe "jsDelivr"        "https://cdn.jsdelivr.net/npm/gsap@3.12.5/package.json"
probe "unpkg"           "https://unpkg.com/gsap@3.12.5/package.json"
probe "Google Fonts"    "https://fonts.googleapis.com/css2?family=Inter"
probe "Iconify API"     "https://api.iconify.design/mdi/home.svg"
echo
echo "Catatan: daftar izin diatur user di claude.ai Settings > Capabilities."
echo "Kalau sebuah host ditolak, pakai paket npm-nya. Lihat references/asset-sourcing.md"
