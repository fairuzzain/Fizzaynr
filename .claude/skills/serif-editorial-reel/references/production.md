# Production

## Preflight

Selalu `bash assets/preflight.sh` sebelum apa pun. Script ini juga memasang yang bisa dipasang:

- **ffmpeg hilang** -> diambil dari npm (`ffmpeg-static`), bukan apt dan bukan CDN. Sudah diuji berhasil, menghasilkan ffmpeg 7.0.2 statik.
- **numpy / soundfile hilang** -> dipasang dari PyPI.
- **Chromium hilang** -> dicoba `npx playwright install chromium`, tapi host unduhannya (`cdn.playwright.dev`) biasanya diblokir. Kalau gagal, verdict jadi `BLOCKED` dan pekerjaan dihentikan. Ini satu-satunya syarat yang tidak bisa diakali dari dalam sesi.

Kalau preflight menulis `build/env.sh`, `source` file itu dulu supaya ffmpeg hasil npm terpakai.

## Setup environment

Sandbox hanya bisa akses GitHub + npm/pip.

```bash
mkdir -p build/{font,icon,vf} && cd build
npm i gsap @phosphor-icons/core      # font tidak perlu diunduh: font pack ada di assets/fonts/
cp node_modules/gsap/dist/gsap.min.js .
# font: setelah index.html dirakit -> python3 ../assets/fonts/fontpack.py css klasik . body=I key=PF mono=JB --inject index.html
pip install --break-system-packages sherpa-onnx soundfile numpy
python3 -m http.server 8770 &
```

Ikon dan logo diambil lewat helper, jangan salin manual:

```bash
bash assets/check_net.sh                                      # sekali di awal proyek
bash assets/fetch_icons.sh phosphor regular arrow-right check play-circle
bash assets/fetch_icons.sh brand google-color claude-color openai
```

CDN diblokir di sandbox, tapi hampir semua asetnya ada di npm. Daftar lengkap paket pengganti, dukungan Lottie dan GIF, serta catatan lisensi ada di `references/asset-sourcing.md`. Jangan gambar ulang logo merek.

Playwright chromium sudah terpasang. Jangan jalankan `playwright install`. Kalau `require('playwright')` gagal, pakai `NODE_PATH=/opt/npm-tools/node_modules`.

Jangan unduh foto orang dari web. Semua foto orang harus dari user.

## Video ke image sequence

Tag `<video>` tidak deterministik saat render per frame. Selalu konversi:

```bash
ffmpeg -nostdin -v error -y -i main.mp4 -vf "fps=30" -q:v 3 vf/main/%04d.jpg
ffmpeg -nostdin -v error -y -ss 8 -t 12 -i klip.mp4 -vf "fps=30,scale=-2:640" -q:v 4 vf/c1/%04d.jpg
ls vf/c1 | wc -l    # jumlah frame, dipakai sebagai argumen n
```

Video utama full resolusi, klip pendukung tinggi 640px sudah cukup karena tampil kecil di mockup HP.

## Word timing

Kalau user melampirkan SRT atau VTT, pakai `assets/srt2words.py` dan lewati seluruh bagian ini. Hemat 850 MB unduhan dan beberapa menit, dan ejaan nama produk dijamin benar karena tidak ditebak mesin.

`assets/wordtime.py` melakukan:

1. `ffmpeg -ar 16000 -ac 1` ke wav mono.
2. Silero VAD (threshold .5, min_silence .25, min_speech .1) memecah jadi segmen kalimat.
3. whisper-small int8 mentranskrip tiap segmen.
4. whisper-base int8 prefix decoding: decode potongan dari awal segmen sampai `t`, `t` maju tiap 0.15 dtk. Kata dianggap mulai saat pertama kali muncul di hasil, dikurangi 0.2 dtk. Pencocokan kata pakai `difflib` ratio >= 0.6 supaya tahan salah eja.
5. Peta senyap dari energi RMS per 20ms (< -38 dB, >= 0.1 dtk) dipakai untuk menggeser kata pertama setelah jeda ke tepat setelah senyap berakhir.
6. Kata yang menumpuk (< 0.13 dtk) disebar proporsional terhadap `len(kata)+1.5`.

Akurasi sekitar +-0.15 dtk. Cukup, karena animasi masuk 0.22-0.3 dtk menutupi selisihnya.

Kalau model gagal diunduh, cek nama aset di halaman release `k2-fsa/sherpa-onnx` tag `asr-models`.

## Audio

`assets/audio.py` menerima `sfx.json` (hasil `page.evaluate(()=>window.SFX)`), video sumber, dan menulis `mix.wav`.

Urutan: potong VO di titik `INS`, fade 15ms di titik potong, sisipkan hening `DUR` detik, sambung sisanya, tambah ekor. Lalu sintesis tiap SFX dari numpy dan tambahkan di level 0.32. Terakhir cek peak dan normalisasi kalau > 0.98.

Untuk klip yang audionya ikut dinyalakan, lewatkan `--clip file.wav --clip-at 46.0 --clip-len 4.95 --clip-gain -0.5`.

Bank SFX: `click pop whoosh swish thud ding tick type`. Semua disintesis, tidak ada unduhan. `whoosh` dimulai 0.15 dtk lebih awal dari waktu yang dicatat.

## Render

`assets/render.js start end out.mp4 [sfx.json]`

Buka halaman, tunggu `window.READY`, panggil `seek(f/30)` tiap frame, screenshot JPEG quality 94, pipe ke ffmpeg `libx264 -preset veryfast -crf 16`. Argumen keempat opsional: menulis `window.SFX` dan `window.TOTAL` ke file.

Jalankan dua separuh paralel. Sekitar 0.26-0.30 dtk per frame.

Encode akhir dengan `-preset medium -crf 20` untuk ukuran file yang wajar, dan `-movflags +faststart`.

## QA

`assets/qa.js` memeriksa:

| Cek | Lolos kalau |
|---|---|
| Safe zone | Semua elemen teks dan kartu di dalam x 40-1040, y 240-1552, dan tidak menyentuh rail kanan di bawah y 1150 |
| Overflow | `scrollHeight <= clientHeight` untuk tiap `.page`/container, `scrollWidth <= clientWidth` untuk tiap teks |
| Sinkron kata | `opacity == 1` pada `T(t_kata)+0.3` untuk semua kata yang punya `_t` |
| Frame kosong | Ada konten selain latar pada sampel tiap 0.25 dtk |
| Error halaman | Tidak ada `pageerror` dan tidak ada request gagal |

Lalu **selalu** lihat sendiri: snapshot ke JPEG, susun contact sheet dengan PIL, baca dengan Read. Pemeriksa otomatis tidak bisa menilai apakah komposisinya enak dilihat.

## Kesalahan yang pernah terjadi

- Caption rata tengah bergeser saat kata muncul satu per satu. Solusi: kata disembunyikan dengan `display:none` sampai waktunya, plus strut tak terlihat per baris.
- Kartu terlalu besar sehingga menabrak safe zone saat animasi masuk. Solusi: batasi lebar baris kartu dengan `max-width`, bukan mengecilkan tiap gambar satu-satu.
- Efek `fromTo` bocor di awal timeline. Solusi: `tl.set(el,{opacity:0},0)` sebelum `tl.to`.
- Kursor keluar layar karena posisi target diukur saat elemen masih ter-translate. Solusi: hardcode koordinat setelah dicek lewat snapshot.
- Jeda di tengah frasa mengalir terasa janggal. Solusi: jeda hanya di batas kalimat.
- ffmpeg di dalam `while read` memakan stdin. Solusi: `-nostdin`.
- `rm -rf` dengan glob diblokir. Solusi: folder baru per versi.
- Upload ke device > 30 MB gagal. Solusi: kirim lewat chat.
- Model HuggingFace tidak bisa diunduh. Solusi: sherpa-onnx dari GitHub releases.
