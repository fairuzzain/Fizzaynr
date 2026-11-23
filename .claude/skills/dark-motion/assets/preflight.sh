#!/usr/bin/env bash
# Cek dan siapkan mesin. Jalankan SEBAGAI LANGKAH PERTAMA, dari folder kerja yang bisa ditulisi:
#
#   bash <folder-skill>/assets/preflight.sh [folderBuild]
#
# Yang bisa dipasang akan dipasang sendiri. Font, mesin animasi, ikon, dan model wajah sudah ikut
# di dalam skill, jadi skill tetap jalan walaupun internet sesi dimatikan.
# Baris terakhir selalu:  VERDICT: READY | READY_NO_ASR | BLOCKED
# Sesudahnya:  source <folderBuild>/env.sh   (memberi $SK, $PY, $CHROME_BIN, dll.)
set -uo pipefail
SK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="${1:-build}"
mkdir -p "$BUILD" 2>/dev/null || { echo "Folder kerja tidak bisa ditulisi. Pindah ke folder lain (mis. cd ~) lalu ulangi."; echo "VERDICT: BLOCKED"; exit 1; }
BUILD="$(cd "$BUILD" && pwd)"
ENVF="$BUILD/env.sh"; : > "$ENVF"
OK=1; ASR=1; NOTE=(); USERMSG=()
say()  { printf "%-22s %s\n" "$1" "$2"; }
have() { command -v "$1" >/dev/null 2>&1; }
net()  { c=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$1" 2>/dev/null); case "$c" in 2*|3*) return 0;; *) return 1;; esac; }

echo "=== Dark Motion: cek mesin ==="
echo "export SK='$SK'" >> "$ENVF"
echo "export BUILD='$BUILD'" >> "$ENVF"
say "folder skill" "$SK"

# --- jaringan (dicek sekali, dipakai untuk memutuskan apa yang bisa dipasang) ---
NET_NPM=0; NET_PYPI=0; NET_GH=0
net "https://registry.npmjs.org/" && NET_NPM=1
net "https://pypi.org/simple/numpy/" && NET_PYPI=1
net "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx" && NET_GH=1
say "internet" "npm=$([ $NET_NPM = 1 ] && echo ya || echo tidak) pypi=$([ $NET_PYPI = 1 ] && echo ya || echo tidak) github=$([ $NET_GH = 1 ] && echo ya || echo tidak)"

# --- 1. Node ---
if have node; then say "node" "ADA ($(node -v))"
else say "node" "TIDAK ADA"; OK=0; NOTE+=("Node.js tidak tersedia."); fi

# --- 2. Python + numpy + OpenCV ---
PY=""
for cand in python3 python; do have "$cand" && "$cand" -c "import numpy" >/dev/null 2>&1 && { PY=$(command -v "$cand"); break; }; done
if [ -z "$PY" ] && have python3; then
  if [ $NET_PYPI = 1 ]; then python3 -m pip install -q --break-system-packages numpy >/dev/null 2>&1 || python3 -m pip install -q numpy >/dev/null 2>&1; fi
  python3 -c "import numpy" >/dev/null 2>&1 && PY=$(command -v python3)
fi
if [ -n "$PY" ]; then
  say "python" "ADA ($("$PY" -V 2>&1 | cut -d' ' -f2))"
  echo "export PY='$PY'" >> "$ENVF"
  if ! "$PY" -c "import cv2" >/dev/null 2>&1 && [ $NET_PYPI = 1 ]; then
    "$PY" -m pip install -q --break-system-packages opencv-python-headless >/dev/null 2>&1 || "$PY" -m pip install -q opencv-python-headless >/dev/null 2>&1
  fi
  if "$PY" -c "import cv2" >/dev/null 2>&1; then say "deteksi wajah" "ADA"
  else say "deteksi wajah" "tidak ada (caption pakai posisi default, mode 'track' jadi potong tengah)"; fi
else
  say "python + numpy" "TIDAK ADA"; OK=0; NOTE+=("Python dengan numpy tidak tersedia.")
fi

# --- 3. ffmpeg ---
if have ffmpeg && have ffprobe; then say "ffmpeg" "ADA"
elif [ $NET_NPM = 1 ] && have npm; then
  mkdir -p "$BUILD/.tools" && (cd "$BUILD/.tools" && npm i -s --no-audit --no-fund ffmpeg-static ffprobe-static >/dev/null 2>&1)
  FF=$(cd "$BUILD/.tools" && node -e "try{process.stdout.write(require('ffmpeg-static'))}catch(e){}" 2>/dev/null)
  FPB=$(cd "$BUILD/.tools" && node -e "try{process.stdout.write(require('ffprobe-static').path)}catch(e){}" 2>/dev/null)
  if [ -n "$FF" ] && [ -x "$FF" ] && [ -n "$FPB" ]; then
    echo "export FFMPEG_BIN='$FF'" >> "$ENVF"; echo "export FFPROBE_BIN='$FPB'" >> "$ENVF"
    echo "export PATH=\"$(dirname "$FF"):$(dirname "$FPB"):\$PATH\"" >> "$ENVF"
    say "ffmpeg" "TERPASANG"
  else say "ffmpeg" "GAGAL dipasang"; OK=0; NOTE+=("ffmpeg tidak tersedia."); fi
else say "ffmpeg" "TIDAK ADA"; OK=0; NOTE+=("ffmpeg tidak tersedia dan internet untuk memasangnya mati."); fi

# --- 4. Playwright + Chromium (untuk merender halaman jadi video) ---
PWM=""
for m in playwright playwright-core /opt/npm-tools/node_modules/playwright /opt/npm-tools/node_modules/playwright-core "$BUILD/.tools/node_modules/playwright-core"; do
  if node -e "require('$m')" >/dev/null 2>&1; then PWM="$m"; break; fi
done
if [ -z "$PWM" ] && [ $NET_NPM = 1 ] && have npm; then
  mkdir -p "$BUILD/.tools" && (cd "$BUILD/.tools" && npm i -s --no-audit --no-fund playwright-core >/dev/null 2>&1)
  node -e "require('$BUILD/.tools/node_modules/playwright-core')" >/dev/null 2>&1 && PWM="$BUILD/.tools/node_modules/playwright-core"
fi
CHROME=""
if [ -n "$PWM" ]; then
  CHROME=$(node -e "try{const p=require('$PWM').chromium.executablePath();if(require('fs').existsSync(p))process.stdout.write(p)}catch(e){}" 2>/dev/null)
fi
for c in "$CHROME" /usr/bin/chromium /usr/bin/chromium-browser /usr/bin/google-chrome /usr/bin/google-chrome-stable; do
  [ -n "$c" ] && [ -x "$c" ] && { CHROME="$c"; break; }
done
if [ -z "$CHROME" ]; then
  for root in "$HOME/.cache/ms-playwright" "$HOME/Library/Caches/ms-playwright"; do
    [ -d "$root" ] || continue
    p=$(find "$root" -maxdepth 5 -type f \( -name headless_shell -o -name chrome \) 2>/dev/null | head -1)
    [ -n "$p" ] && [ -x "$p" ] && { CHROME="$p"; break; }
  done
fi
if [ -z "$CHROME" ] && [ -n "$PWM" ]; then
  # hanya berhasil kalau internet sesi dibuka untuk semua domain
  timeout 180 node "$(dirname "$(node -e "process.stdout.write(require.resolve('$PWM'))")")/cli.js" install chromium >/dev/null 2>&1 || true
  CHROME=$(node -e "try{const p=require('$PWM').chromium.executablePath();if(require('fs').existsSync(p))process.stdout.write(p)}catch(e){}" 2>/dev/null)
fi
if [ -n "$PWM" ]; then PWM=$(node -e "process.stdout.write(require.resolve('$PWM'))" 2>/dev/null || echo "$PWM"); fi
if [ -n "$PWM" ] && [ -n "$CHROME" ]; then
  say "browser render" "ADA"
  echo "export PW_MODULE='$PWM'" >> "$ENVF"; echo "export CHROME_BIN='$CHROME'" >> "$ENVF"
else
  say "browser render" "TIDAK ADA"; OK=0; NOTE+=("Browser untuk merender video tidak tersedia.")
fi

# --- 5. Pengenal suara (opsional: hanya kalau user tidak punya subtitle) ---
if [ $NET_GH = 1 ] && { [ $NET_PYPI = 1 ] || "${PY:-python3}" -c "import sherpa_onnx" >/dev/null 2>&1; }; then
  say "pengenal suara" "BISA (dipasang otomatis saat dibutuhkan)"
else ASR=0; say "pengenal suara" "TIDAK BISA (internet dibatasi) -> butuh file subtitle .srt dari user"; fi

# --- 6. Disk dan CPU ---
AVAIL=$(df -Pm "$BUILD" | awk 'NR==2{print $4}')
if [ "${AVAIL:-0}" -ge 4000 ]; then say "disk kosong" "${AVAIL} MB"
else say "disk kosong" "${AVAIL} MB, KURANG"; OK=0; NOTE+=("Butuh minimal 4 GB kosong."); fi
say "cpu" "$(nproc 2>/dev/null || echo ?) inti"

# --- 7. Berkas bawaan skill ---
for f in vendor/motion.js vendor/fonts/inter-latin-700-normal.woff2 template.html; do
  [ -f "$SK/assets/$f" ] || { OK=0; NOTE+=("Berkas skill tidak lengkap: assets/$f. Upload ulang ZIP skill."); }
done

echo
if [ ${#NOTE[@]} -gt 0 ]; then printf '%s\n' "${NOTE[@]}" | sed 's/^/  - /'; echo; fi
if [ "$OK" -eq 0 ]; then
  cat <<'MSG'
MESIN INI BELUM BISA MERENDER VIDEO. Jangan lanjut.
Sampaikan ke user dengan bahasa biasa, kurang lebih:
  "Fitur untuk mengolah file belum aktif di akun kamu. Buka Settings > Capabilities,
   nyalakan 'Create and edit files' (di sebagian tampilan disebut 'Code execution'),
   lalu mulai chat baru dan kirim videonya lagi. Kalau akunmu akun kantor (Team/Enterprise),
   minta admin menyalakannya."
Kalau yang kurang hanya ffmpeg/Python/browser padahal fitur sudah aktif, tambahkan:
  "Di halaman yang sama, nyalakan juga 'Allow network egress' (akses internet untuk memasang alat)."
MSG
  echo "VERDICT: BLOCKED"; exit 1
fi
echo "Siap. Jalankan:  source $ENVF"
if [ "$ASR" -eq 0 ]; then
  echo "Tanpa pengenal suara: minta user file subtitle .srt/.vtt (bisa dibuat dengan fitur teks/caption otomatis di CapCut atau aplikasi edit lain, lalu diekspor sebagai .srt)."
  echo "VERDICT: READY_NO_ASR"; exit 0
fi
echo "VERDICT: READY"
