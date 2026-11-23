#!/usr/bin/env bash
# Cek mesin sebelum mulai. Jalankan SEBAGAI LANGKAH PERTAMA, sebelum apa pun.
# Yang bisa dipasang otomatis akan dipasang. Yang tidak bisa dilaporkan jelas,
# supaya user tahu dalam 10 detik, bukan setelah 10 menit menunggu.
#
#   bash assets/preflight.sh [folderBuild]
#
# Baris terakhir selalu: VERDICT: READY | READY_NO_ASR | BLOCKED
set -uo pipefail
BUILD="${1:-build}"
mkdir -p "$BUILD"
ENVF="$BUILD/env.sh"; : > "$ENVF"
OK=1; ASR=1; NOTE=()

say()  { printf "%-28s %s\n" "$1" "$2"; }
have() { command -v "$1" >/dev/null 2>&1; }

echo "=== Serif Editorial Reel: cek mesin ==="

# --- 1. Node dan npm: tidak bisa di-bootstrap sendiri ---
if have node && have npm; then say "node" "ADA ($(node -v))"
else say "node / npm" "TIDAK ADA"; OK=0; NOTE+=("Node.js tidak tersedia dan tidak bisa dipasang dari dalam."); fi

# --- 2. Python ---
if have python3; then say "python3" "ADA ($(python3 -V 2>&1 | cut -d' ' -f2))"
else say "python3" "TIDAK ADA"; OK=0; NOTE+=("Python 3 tidak tersedia."); fi

# --- 3. ffmpeg: kalau hilang, pasang dari npm (bukan apt, bukan CDN) ---
if have ffmpeg; then say "ffmpeg" "ADA ($(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3))"
else
  say "ffmpeg" "tidak ada, coba pasang dari npm..."
  if have npm && npm i -s --no-audit --no-fund ffmpeg-static ffprobe-static >/dev/null 2>&1; then
    FF=$(node -e "try{process.stdout.write(require('ffmpeg-static'))}catch(e){}" 2>/dev/null)
    FP=$(node -e "try{process.stdout.write(require('ffprobe-static').path)}catch(e){}" 2>/dev/null)
    if [ -n "$FF" ] && [ -x "$FF" ]; then
      echo "export FFMPEG_BIN='$FF'" >> "$ENVF"
      [ -n "$FP" ] && echo "export FFPROBE_BIN='$FP'" >> "$ENVF"
      echo "export PATH=\"\$(dirname '$FF'):\$PATH\"" >> "$ENVF"
      say "ffmpeg" "TERPASANG via npm ($($FF -version 2>/dev/null | head -1 | cut -d' ' -f3))"
      NOTE+=("ffmpeg dipasang dari npm. Jalankan: source $ENVF sebelum perintah ffmpeg.")
    else say "ffmpeg" "GAGAL dipasang"; OK=0; NOTE+=("ffmpeg tidak tersedia dan gagal dipasang."); fi
  else say "ffmpeg" "GAGAL dipasang"; OK=0; NOTE+=("ffmpeg tidak tersedia dan gagal dipasang."); fi
fi

# --- 4. Chromium untuk Playwright: TIDAK bisa dipasang kalau CDN diblokir ---
CHROME=""
for p in "$(node -e "try{process.stdout.write(require('playwright').chromium.executablePath())}catch(e){}" 2>/dev/null)" \
         "$(node -e "try{process.stdout.write(require('playwright').chromium.executablePath())}catch(e){}" 2>/dev/null)" \
         "$(command -v chromium || true)" "$(command -v chromium-browser || true)" \
         "$(command -v google-chrome || true)"; do
  [ -n "$p" ] && [ -x "$p" ] && CHROME="$p" && break
done
if [ -z "$CHROME" ]; then   # Mac/Linux lokal: Chromium Playwright yang sudah pernah terunduh
  for root in "$HOME/Library/Caches/ms-playwright" "$HOME/.cache/ms-playwright"; do
    [ -d "$root" ] || continue
    p=$(find "$root" -maxdepth 6 -type f \( -name chrome-headless-shell -o -name headless_shell -o -name "Google Chrome for Testing" \) 2>/dev/null | sort -r | head -1)
    [ -n "$p" ] && [ -x "$p" ] && { CHROME="$p"; break; }
  done
fi
if [ -z "$CHROME" ]; then
  CHROME=$(NODE_PATH=/opt/npm-tools/node_modules node -e "try{process.stdout.write(require('playwright').chromium.executablePath())}catch(e){}" 2>/dev/null)
  [ -n "$CHROME" ] && [ -x "$CHROME" ] && echo "export NODE_PATH=/opt/npm-tools/node_modules" >> "$ENVF"
fi
# modul playwright untuk render.js/qa.js/sheet.js (dicari oleh _chrome.js)
PWC="$HOME/.cache/serif-editorial-reel"
if ! node -e "require('playwright')" >/dev/null 2>&1 && ! node -e "require('$HOME/.cache/script-to-motion-reel/node_modules/playwright-core')" >/dev/null 2>&1 \
   && ! node -e "require('$PWC/node_modules/playwright-core')" >/dev/null 2>&1; then
  mkdir -p "$PWC"; [ -f "$PWC/package.json" ] || echo '{"name":"serif-editorial-cache","private":true}' > "$PWC/package.json"
  (cd "$PWC" && npm i -s --no-audit --no-fund playwright-core gsap >/dev/null 2>&1)
fi
[ -n "$CHROME" ] && [ -x "$CHROME" ] && echo "export CHROME_BIN='$CHROME'" >> "$ENVF"
if [ -n "$CHROME" ] && [ -x "$CHROME" ]; then say "chromium" "ADA"
else
  say "chromium" "TIDAK ADA"
  if curl -s -o /dev/null -w "" --max-time 10 "https://cdn.playwright.dev/" 2>/dev/null; then
    say "chromium" "coba unduh..."; npx -y playwright install chromium >/dev/null 2>&1 && CHROME=ok
  fi
  if [ "${CHROME:-}" != "ok" ]; then
    OK=0; NOTE+=("Chromium tidak ada dan host unduhannya diblokir. Render tidak bisa jalan di mesin ini.")
  fi
fi

# --- 5. Paket Python ---
MISS=""
for m in numpy soundfile; do python3 -c "import $m" 2>/dev/null || MISS="$MISS $m"; done
if [ -n "$MISS" ]; then
  say "python pkg" "pasang:$MISS"
  pip install --break-system-packages -q $MISS >/dev/null 2>&1 \
    && say "python pkg" "TERPASANG" \
    || { say "python pkg" "GAGAL"; OK=0; NOTE+=("numpy/soundfile gagal dipasang. PyPI mungkin diblokir."); }
else say "python pkg" "ADA (numpy, soundfile)"; fi

# --- 6. Jaringan ---
probe(){ c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 12 "$1" 2>/dev/null); case "$c" in 2*|3*) return 0;; *) return 1;; esac; }
if probe "https://registry.npmjs.org/gsap"; then say "npm registry" "BISA"
else say "npm registry" "DITOLAK"; OK=0; NOTE+=("npm tidak bisa dijangkau, gsap dan font tidak bisa diambil."); fi
if probe "https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/star.svg"; then say "GitHub" "BISA"
else say "GitHub" "DITOLAK"; ASR=0; NOTE+=("GitHub diblokir, model ASR tidak bisa diunduh. WAJIB pakai jalur SRT."); fi

# --- 7. Disk ---
AVAIL=$(df -Pm . | awk 'NR==2{print $4}')
if [ "${AVAIL:-0}" -ge 3000 ]; then say "disk kosong" "${AVAIL} MB"
else say "disk kosong" "${AVAIL} MB, KURANG"; OK=0; NOTE+=("Butuh minimal 3 GB kosong untuk image sequence."); fi

echo
if [ ${#NOTE[@]} -gt 0 ]; then printf '%s\n' "${NOTE[@]}" | sed 's/^/  - /'; echo; fi

if [ "$OK" -eq 0 ]; then
  cat <<'MSG'
MESIN INI TIDAK MENDUKUNG.

Sampaikan ke user, dalam bahasa biasa:
  "Sesi ini tidak punya alat yang dibutuhkan untuk merender video.
   Coba mulai percakapan baru dengan code execution aktif di
   Settings > Capabilities, lalu upload videonya lagi."

Jangan lanjut ke langkah berikutnya. Jangan coba cara lain.
MSG
  echo "VERDICT: BLOCKED"; exit 1
fi

if [ "$ASR" -eq 0 ]; then
  echo "SIAP, tapi tanpa ASR. Minta user melampirkan file SRT atau VTT,"
  echo "lalu pakai: python3 assets/srt2words.py sub.srt words.json"
  echo "VERDICT: READY_NO_ASR"; exit 0
fi

echo "SIAP. Lanjut ke word timing."
echo "Kalau user melampirkan SRT, pakai srt2words.py (lebih cepat, tidak perlu unduh model)."
echo "VERDICT: READY"
