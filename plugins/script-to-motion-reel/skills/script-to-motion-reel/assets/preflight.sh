#!/usr/bin/env bash
# Cek dan siapkan mesin. Jalankan SEBAGAI LANGKAH PERTAMA, dari folder proyek (bisa ditulisi):
#
#   bash <folder-skill>/assets/preflight.sh [folderBuild]
#
# Yang bisa dipasang akan dipasang sendiri. Font Poppins, ikon Phosphor fill, dan SFX bawaan
# sudah ikut di dalam skill. GSAP dipasang sekali ke ~/.cache/script-to-motion-reel.
# Baris terakhir selalu:  VERDICT: READY | READY_NO_ASR | BLOCKED
# Sesudahnya:  source <folderBuild>/env.sh   (memberi $SK, $PY, $BUILD, $CHROME_BIN, ...)
set -uo pipefail
SK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="${1:-build}"
mkdir -p "$BUILD" 2>/dev/null || { echo "Folder kerja tidak bisa ditulisi. Pindah ke folder lain lalu ulangi."; echo "VERDICT: BLOCKED"; exit 1; }
BUILD="$(cd "$BUILD" && pwd)"
CACHE="$HOME/.cache/script-to-motion-reel"
ENVF="$BUILD/env.sh"; : > "$ENVF"
OK=1; ASR=1; NOTE=()
say()  { printf "%-22s %s\n" "$1" "$2"; }
have() { command -v "$1" >/dev/null 2>&1; }
net()  { c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$1" 2>/dev/null); case "$c" in 2*|3*) return 0;; *) return 1;; esac; }

echo "=== Script to Motion Reel: cek mesin ==="
echo "export SK='$SK'" >> "$ENVF"
echo "export BUILD='$BUILD'" >> "$ENVF"
say "folder skill" "$SK"
say "folder kerja" "$BUILD"

NET_NPM=0; NET_PYPI=0; NET_GH=0
net "https://registry.npmjs.org/" && NET_NPM=1
net "https://pypi.org/simple/numpy/" && NET_PYPI=1
net "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx" && NET_GH=1
say "internet" "npm=$([ $NET_NPM = 1 ] && echo ya || echo tidak) pypi=$([ $NET_PYPI = 1 ] && echo ya || echo tidak) github=$([ $NET_GH = 1 ] && echo ya || echo tidak)"

# --- Node ---
if have node; then say "node" "ADA ($(node -v))"; else say "node" "TIDAK ADA"; OK=0; NOTE+=("Node.js belum terpasang (https://nodejs.org)."); fi

# --- Python + numpy ---
PY=""
for cand in python3 python; do have "$cand" && "$cand" -c "import numpy" >/dev/null 2>&1 && { PY=$(command -v "$cand"); break; }; done
if [ -z "$PY" ] && have python3 && [ $NET_PYPI = 1 ]; then
  python3 -m pip install -q --break-system-packages numpy >/dev/null 2>&1 || python3 -m pip install -q --user numpy >/dev/null 2>&1
  python3 -c "import numpy" >/dev/null 2>&1 && PY=$(command -v python3)
fi
if [ -n "$PY" ]; then say "python + numpy" "ADA ($("$PY" -V 2>&1 | cut -d' ' -f2))"; echo "export PY='$PY'" >> "$ENVF"
else say "python + numpy" "TIDAK ADA"; OK=0; NOTE+=("Python 3 dengan numpy belum ada (pip install numpy)."); fi

# --- ffmpeg ---
if have ffmpeg && have ffprobe; then say "ffmpeg" "ADA"
elif [ $NET_NPM = 1 ] && have npm; then
  mkdir -p "$CACHE" && (cd "$CACHE" && [ -f package.json ] || echo '{"name":"stmr-cache","private":true}' > package.json; npm i -s --no-audit --no-fund ffmpeg-static ffprobe-static >/dev/null 2>&1)
  FF=$(cd "$CACHE" && node -e "try{process.stdout.write(require('ffmpeg-static'))}catch(e){}" 2>/dev/null)
  FPB=$(cd "$CACHE" && node -e "try{process.stdout.write(require('ffprobe-static').path)}catch(e){}" 2>/dev/null)
  if [ -n "$FF" ] && [ -x "$FF" ] && [ -n "$FPB" ]; then
    echo "export FFMPEG_BIN='$FF'" >> "$ENVF"; echo "export FFPROBE_BIN='$FPB'" >> "$ENVF"
    echo "export PATH=\"$(dirname "$FF"):$(dirname "$FPB"):\$PATH\"" >> "$ENVF"; say "ffmpeg" "TERPASANG (npm)"
  else say "ffmpeg" "GAGAL dipasang"; OK=0; NOTE+=("ffmpeg tidak ada (Mac: brew install ffmpeg)."); fi
else say "ffmpeg" "TIDAK ADA"; OK=0; NOTE+=("ffmpeg tidak ada (Mac: brew install ffmpeg)."); fi

# --- Playwright + Chromium ---
mkdir -p "$CACHE"; [ -f "$CACHE/package.json" ] || echo '{"name":"stmr-cache","private":true}' > "$CACHE/package.json"
PWM=""
for m in playwright playwright-core "$CACHE/node_modules/playwright-core" "$BUILD/.tools/node_modules/playwright-core"; do
  if node -e "require('$m')" >/dev/null 2>&1; then PWM="$m"; break; fi
done
if [ -z "$PWM" ] && [ $NET_NPM = 1 ] && have npm; then
  (cd "$CACHE" && npm i -s --no-audit --no-fund playwright-core >/dev/null 2>&1)
  node -e "require('$CACHE/node_modules/playwright-core')" >/dev/null 2>&1 && PWM="$CACHE/node_modules/playwright-core"
fi
CHROME=""
if [ -n "$PWM" ]; then
  CHROME=$(node -e "try{const p=require('$PWM').chromium.executablePath();if(require('fs').existsSync(p))process.stdout.write(p)}catch(e){}" 2>/dev/null)
fi
if [ -z "$CHROME" ]; then
  for root in "$HOME/Library/Caches/ms-playwright" "$HOME/.cache/ms-playwright"; do
    [ -d "$root" ] || continue
    p=$(find "$root" -maxdepth 6 -type f \( -name chrome-headless-shell -o -name headless_shell -o -name "Google Chrome for Testing" -o -name chrome \) 2>/dev/null | sort -r | head -1)
    [ -n "$p" ] && [ -x "$p" ] && { CHROME="$p"; break; }
  done
fi
if [ -z "$CHROME" ] && [ -n "$PWM" ] && [ $NET_NPM = 1 ]; then
  TO=""; have timeout && TO="timeout 300"; $TO node "$(dirname "$(node -e "process.stdout.write(require.resolve('$PWM'))")")/cli.js" install chromium-headless-shell >/dev/null 2>&1 || true
  CHROME=$(node -e "try{const p=require('$PWM').chromium.executablePath();if(require('fs').existsSync(p))process.stdout.write(p)}catch(e){}" 2>/dev/null)
fi
if [ -n "$PWM" ]; then PWM=$(node -e "process.stdout.write(require.resolve('$PWM'))" 2>/dev/null || echo "$PWM"); fi
if [ -n "$PWM" ] && [ -n "$CHROME" ]; then
  say "browser render" "ADA"; echo "export PW_MODULE='$PWM'" >> "$ENVF"; echo "export CHROME_BIN='$CHROME'" >> "$ENVF"
else say "browser render" "TIDAK ADA"; OK=0; NOTE+=("Browser untuk merender (Playwright Chromium) belum ada."); fi

# --- GSAP (mesin animasi) ---
if [ -f "$CACHE/node_modules/gsap/dist/gsap.min.js" ]; then say "gsap" "ADA"
elif [ $NET_NPM = 1 ] && have npm; then
  (cd "$CACHE" && npm i -s --no-audit --no-fund gsap >/dev/null 2>&1)
  if [ -f "$CACHE/node_modules/gsap/dist/gsap.min.js" ]; then say "gsap" "TERPASANG"; else say "gsap" "GAGAL"; OK=0; NOTE+=("GSAP tidak bisa dipasang dari npm."); fi
else say "gsap" "TIDAK ADA"; OK=0; NOTE+=("GSAP belum ada dan internet ke npm mati."); fi

# --- Pengenal suara (hanya kalau user tidak punya subtitle) ---
if [ $NET_GH = 1 ] && { [ $NET_PYPI = 1 ] || "${PY:-python3}" -c "import sherpa_onnx" >/dev/null 2>&1; }; then
  say "pengenal suara" "BISA (dipasang otomatis saat dibutuhkan)"
else ASR=0; say "pengenal suara" "TIDAK BISA -> butuh file subtitle .srt dari user"; fi

# --- Disk dan CPU ---
AVAIL=$(df -Pm "$BUILD" | awk 'NR==2{print $4}')
if [ "${AVAIL:-0}" -ge 3000 ]; then say "disk kosong" "${AVAIL} MB"; else say "disk kosong" "${AVAIL} MB, KURANG"; OK=0; NOTE+=("Butuh minimal 3 GB kosong."); fi
say "cpu" "$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo ?) inti"

# --- Berkas bawaan skill ---
for f in template.html assemble.py mix.py render_all.py vendor/icons-fill.json fonts/fontpack.json fonts/poppins-latin-700-normal.woff2; do
  [ -f "$SK/assets/$f" ] || { OK=0; NOTE+=("Berkas skill tidak lengkap: assets/$f. Pasang ulang skill-nya."); }
done
say "SFX bawaan" "$(ls "$SK/assets/sfx" 2>/dev/null | tr '\n' ' ')"

echo
if [ ${#NOTE[@]} -gt 0 ]; then printf '%s\n' "${NOTE[@]}" | sed 's/^/  - /'; echo; fi
if [ "$OK" -eq 0 ]; then
  echo "MESIN INI BELUM BISA MERENDER VIDEO. Jangan lanjut. Sampaikan ke user apa yang kurang (daftar di atas) dengan bahasa biasa."
  echo "VERDICT: BLOCKED"; exit 1
fi
echo "Siap. Jalankan:  source $ENVF"
if [ "$ASR" -eq 0 ]; then
  echo "Tanpa pengenal suara: minta file subtitle .srt dari user (misalnya caption otomatis CapCut, ekspor .srt)."
  echo "VERDICT: READY_NO_ASR"; exit 0
fi
echo "VERDICT: READY"
