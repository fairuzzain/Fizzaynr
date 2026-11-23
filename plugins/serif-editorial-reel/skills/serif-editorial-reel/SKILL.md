---
name: "serif-editorial-reel"
description: "Bikin reel vertikal 1080x1920 bergaya editorial dari video talking + VO: scene motion graphic gelap dan terang (kertas krem) yang selang-seling, tipografi serif italic ala majalah, caption per kata yang dikunci ke ucapan (menyala di latar gelap, tinta gelap di latar terang), grafik garis tipis, mockup HP 3D, rekonstruksi UI, aman dari safe zone reels. Pakai saat user menyebut serif editorial, minta reel bergaya editorial/majalah, atau minta mengedit video talking head/podcast jadi reel motion graphic yang mencampur scene gelap dan terang."
---

# Serif Editorial Reel

Skill ini mengubah **satu video orang berbicara** (podcast, talking head, UGC) menjadi reel vertikal 1080x1920 30fps dengan motion graphic kelas atas: gelap, sinematik, teks menyala, animasi halus, tanpa satu pun elemen yang terlihat kartun.

Skill ini berlaku untuk topik apa pun (edukasi, produk, jasa, cerita, promosi). Isi scene selalu diturunkan dari naskah dan aset user, bukan dari contoh bawaan.

**Aturan paling penting: setiap kata muncul tepat saat diucapkan.** Semua yang lain mengikuti itu.

**Cara bicara ke user:** bahasa simpel, langsung ke inti, tanpa istilah teknis kalau tidak perlu. User biasanya bukan orang teknis. Kalau permintaannya tidak masuk akal atau tidak akan berhasil, bilang langsung.

---

## 0. Preflight, lalu intake

**Langkah pertama, sebelum apa pun:**

```bash
bash assets/preflight.sh
```

Script ini memeriksa ffmpeg, Node, Chromium, paket Python, jaringan, dan sisa disk. Yang bisa dipasang otomatis akan dipasang sendiri (ffmpeg diambil dari npm kalau hilang). Baris terakhirnya salah satu dari:

| Verdict | Artinya |
|---|---|
| `READY` | Lanjut normal |
| `READY_NO_ASR` | GitHub diblokir, model ASR tidak bisa diunduh. **Wajib minta file SRT ke user** |
| `BLOCKED` | Mesin tidak mendukung. **Berhenti**, sampaikan ke user dengan bahasa biasa, jangan coba cara lain |

Kalau `BLOCKED`, jangan buang waktu mencari akal. Penyebab paling umum adalah Chromium tidak ada dan host unduhannya diblokir, dan itu tidak bisa diperbaiki dari dalam sesi.

Kalau preflight menulis `build/env.sh`, jalankan `source build/env.sh` sebelum memakai ffmpeg.

---

## Intake (satu batch, di awal)

Cek apa yang sudah dikirim, lalu **tanya semua yang kurang dalam satu pesan** (pakai pilihan ganda kalau bisa). Jangan menanyakan hal baru di tengah pengerjaan: itu bikin bolak-balik dan buang waktu user.

Checklist intake:

- **Video utama** (orang berbicara, sudah ada audionya). Wajib. Tanyakan apakah ada caption yang sudah menempel di video; kalau ada, minta versi tanpa caption.
- **File SRT atau VTT** (**selalu tanyakan**). Kalau ada, jalur ASR tidak dipakai sama sekali.
- **Video referensi editing** (opsional tapi sangat membantu).
- **Aset pendukung**: video/foto contoh, screenshot, foto profil, logo. Minta nama file yang jelas.
- **Video mana yang dipilih**: kalau ada folder berisi kumpulan video dan scene butuh memilih beberapa, **tampilkan daftarnya dan tanya dulu**. Jangan memilih sendiri.
- **Video unggulan** (kalau ada satu yang harus disorot).
- **Naskah/brief**: bagian mana muncul di kalimat apa, kata kunci yang ditonjolkan, dan **kata CTA persis** seperti yang user mau.
- **Nama/handle/angka** yang harus akurat (akun, nama produk, harga, persentase). Jangan dikarang.
- **Font** (preset E1-E9 dari font pack bawaan, tunjukkan gambar `assets/fonts/preview-editorial.jpg`; default E1 Klasik Serif = Inter + Playfair italic). Atau font brand dari file .ttf/.otf milik user.
- **Sound effect**: 9 SFX bawaan / folder SFX milik user / sintetis / tanpa (default bawaan).
- **Lokasi hasil**: kalau user punya struktur folder (misalnya satu folder bahan dan satu folder hasil), ikuti. Satu video = satu folder baru di folder hasil.

Kalau user tidak ada di tempat: ambil keputusan terbaik, tulis asumsinya di atas hasil kerja.

Buat task list: preflight -> pelajari referensi -> word timing -> rencana scene -> **gerbang 1 (papan konsep)** -> build HTML -> **gerbang 2 (contact sheet)** -> audio+SFX -> render -> QA -> kirim.

---

## 0b. Dua gerbang persetujuan sebelum render (wajib)

Render itu mahal (menit dan token). Salah konsep yang baru ketahuan setelah render adalah pemborosan terbesar. Karena itu ada dua gerbang:

**Gerbang 1: papan konsep (sebelum scene dikode).**
Buat frame statis (HTML mock sederhana + screenshot) untuk **1 frame per tipe scene yang berbeda**. Kalau ada pilihan gaya (misalnya cara membingkai wajah), tampilkan 2-3 alternatif dan biarkan user memilih. Tunggu persetujuan.

**Gerbang 2: contact sheet (setelah scene dikode, sebelum render).**
Ambil screenshot key frame tiap scene lewat `seek(t)`, gabungkan jadi **satu gambar contact sheet** (lebih murah daripada banyak gambar terpisah). Untuk scene yang inti-nya gerakan (checklist animatif, zoom-through, carousel), tambahkan strip 3 frame: awal, tengah, akhir. Kirim ke user dan tunggu "oke" sebelum render.

Batas yang harus dijelaskan ke user: frame diam tidak menunjukkan timing dan suara, jadi tetap ada kemungkinan revisi gerakan setelah render. Kalau user bilang "langsung render aja", lewati gerbang.

---

## 1. Pelajari video referensi (kalau ada)

```bash
ffmpeg -nostdin -v error -y -i ref.mp4 -vf "fps=4,scale=270:-2" ref/%03d.jpg
```

Susun contact sheet (PIL, 8 kolom, label detik) dan **lihat sendiri dengan Read**. Ambil frame resolusi penuh di 4-5 momen penting untuk membaca detail tipografi.

Yang dicatat: ukuran dan bobot caption, kata kunci diperlakukan bagaimana, warna aksen, kekuatan glow, ritme potongan, ada tidaknya lower third, cara transisi.

Hasil pembacaan ini **menimpa** default di bawah kalau berbeda.

---

## 2. Hukum visual (jangan dilanggar)

Baca `references/style-system.md` untuk angka lengkapnya. Intinya:

1. **Tidak ada aset kartun.** Dilarang: emoji 3D, ikon bulat warna-warni, stiker, maskot, confetti, bintang, mata, dan Lottie bergaya kartun. Yang boleh: garis tipis, ikon garis monokrom (Phosphor regular/bold) dipakai kecil, bentuk geometris sederhana, mockup perangkat, UI yang direkonstruksi.
2. **Teks di latar gelap wajib ber-glow.** Teks putih: glow putih tipis + drop shadow gelap. Teks aksen: glow warna berlapis. Di **scene terang** tidak ada glow: tinta gelap + bayangan lembut (otomatis lewat class `lt` / `light:true`).
2a. **Campur gelap dan terang (ciri khas Serif Editorial).** Selang-seling scene motion graphic gelap dengan scene terang (`lightBg`, kertas krem atau putih) supaya ritmenya hidup: kira-kira 1 dari 3 scene MG terang, tidak pernah dua scene terang berturut-turut lebih dari 6 dtk, dan scene paling dramatis (kata hantaman, penutup) tetap gelap. Font default **Serif italic** (preset E1). Ini pembeda dari Dark Motion yang selalu gelap dan default Sans.
2b. **Teks yang berkaitan = SATU blok rapat (jangan "social distancing").** Kalimat yang dibaca berurutan, misalnya "Di kelas ini ada" + "100+" + "video dibedah", disusun sebagai satu blok di satu titik tengah dengan `stack()`, bukan disebar ke atas-tengah-bawah layar. Jarak antar-baris di dalam blok 12-36 px (sekitar 0,1-0,3 x tinggi huruf baris yang lebih kecil); angka/kata raksasa diberi `lineHeight:'.9'` supaya kotak hurufnya tidak menambah jarak. Ruang kosong ada di LUAR blok. Jarak antar-blok yang beda ide minimal 2x jarak di dalam blok. Cek di contact sheet: kalau mata harus melompat dari satu baris ke baris berikutnya, rapatkan.
3. **Komposisi teks artistik.** Kalau satu blok punya ukuran campur, baris tidak boleh rata tengah semua. Baris digeser kiri-kanan (zig-zag) dan kata kecil diselipkan ke pojok atas kata besar.
4. **Safe zone.** Teks dan objek penting hanya di area: **kiri 125px, kanan 125px (x 125-955), atas 150px (y mulai 150), bawah 200px (y sampai 1720)**. Lebar maksimum elemen sejajar 830px. Cek otomatis dengan `assets/qa.js` (sudah memakai angka ini) sebelum render, jangan dikira-kira. Kartu yang sedang animasi masuk/keluar boleh melewati batas beberapa frame. Latar penuh layar (video blur, overlay) tidak termasuk aturan ini.
5. **Contoh video selalu di mockup HP modern**, bukan kartu polos. Pakai `.phone` di template. Skala diperbesar sebesar mungkin yang masih muat di safe zone.
6. **Warna punya arti.** Merah untuk negatif/mahal/salah, hijau untuk positif/berhasil/murah, putih untuk netral.
7. **Animasi simpel tapi mahal.** Satu gerakan per elemen, easing benar, durasi 0.22-0.45 dtk. Tanpa bounce berlebihan, tanpa putar-putar, tanpa kedip. Untuk daftar/checklist: animasi masuk bertahap (flip/blur-in), garis penghubung yang tergambar, progress bar, centang. Daftar statis terasa murah.
8. **Jangan ada kebocoran visual.** Teks di footage latar (caption, watermark) tidak boleh terbaca: blur kuat. Raw footage tidak boleh terlihat menumpuk dengan latar motion graphic saat transisi.

---

## 2b. Wajah talking head, grade, dan bingkai

**Grade wajah (default, jangan diganti kalau user tidak minta):**
- Denoise **ringan** (`hqdn3d` kecil). **Jangan smoothing berat**: wajah terlihat plastik dan user akan menolaknya.
- Kurangi magenta/biru, hangatkan kulit, gamma sekitar 1.2, vignette halus, noise film tipis.
- Tujuan: kualitas wajah dan motion graphic **tidak timpang**. Kalau raw footage lighting-nya jelek, grade-lah yang menyamakan, bukan menyembunyikan wajah.

**Bagian video yang tidak menampilkan wajah:**
- Ambil audionya saja. Videonya diganti latar motion graphic.
- Latar MG memakai footage relevan yang diblur kuat (boxblur besar) dengan overlay hitam 80-90%, supaya tidak kosong dan teks tidak bentrok.
- Daftarkan jendela waktu `face:[[a,b],...]` (wajah tampil). Selain itu = MG. `bgMotion` yang mengurus sisanya.

**Bingkai wajah:** default penuh layar. Kalau user ingin wajah lebih kecil, tawarkan 2-3 opsi di gerbang 1 (mis. kartu kaca 9:16, mockup HP dengan UI Reels, viewfinder REC). **Pertahankan rasio 9:16**, jangan 3:4.

**Transisi masuk ke wajah (default):** zoom-through. Dunia MG membesar (sekitar 1.4x) dengan blur sebelum cut, wajah masuk dari skala sekitar 0.55 ke 1. Cadangan: hard cut + flash putih tipis. **Dilarang fade silang** antara wajah dan latar MG.

---

## 2c. Komponen siap pakai (generik, isi diambil dari naskah user)

`assets/components.js` berisi 14 komponen yang sudah teruji. Semua teks, gambar, folder frame, dan waktu adalah **parameter**; tidak ada konten bawaan. Setiap scene menerima `light:true` (scene terang) dan `wipe:'up'|'circle'`. Helper tambahan: `stack()` (blok teks rapat), `media()`, `phoneAt()`, `TX()`, `lightBg()`, dan caption terang `cap(..., {light:true})`.

| Fungsi | Untuk apa |
|---|---|
| `bgMotion` | Jendela WAJAH vs MG, zoom-through, latar MG dari footage blur |
| `sceneSearchHook` | Hook pertanyaan: kolom search, hasil dicoret, tanda tanya besar |
| `sceneProfile` | UI profil akun media sosial di HP, username disorot, scroll |
| `sceneCollage` | Hingga 12 HP 3D memenuhi layar, tanda di tiap HP |
| `sceneCarousel` | HP bergeser, satu dipilih, deretan langkah |
| `sceneAnnotate` | HP membesar, grid + scan, label menarik garis (maks 4) |
| `sceneChecklist` | HP + kartu checklist animatif (maks 6) dengan garis penghubung dan centang |
| `sceneFilmstrip` | Deretan frame dengan playhead, awal sampai akhir |
| `sceneBrowser` | Jendela browser berisi video atau gambar |
| `sceneWall` | Dinding screenshot besar, lalu HP fokus (opsional) |
| `scenePhoneFocus` | Satu HP besar dengan pill |
| `sceneTryFail` | Prompt mengetik, generate, hasil glitch, lencana error |
| `sceneCommentCTA` | Kolom komentar mengetik kata, kirim, tombol "klik link" |
| `sceneClosing` | Penutup: video blur + overlay + kata CTA raksasa |

Contoh pemakaian semuanya: `examples/demo-scenes.js`. Parameter lengkap: `references/scene-recipes.md` (bagian "Komponen siap pakai").

Aturan pakai:
- **Ganti semua placeholder** dengan konten user. Jangan menyisakan teks contoh.
- Pakai hanya komponen yang dibutuhkan naskah. Jangan memakai semuanya hanya karena ada.
- Label dan sub-teks yang dikarang sendiri dilaporkan ke user di ringkasan akhir.
- Hapus screenshot duplikat sebelum masuk `sceneWall`.
- Kalau naskah butuh pola yang belum ada, bangun dari resep di `references/scene-recipes.md`, lalu pertimbangkan menambahkannya ke `components.js`.

---

### Sumber aset

Sandbox hanya bisa menjangkau **GitHub dan package registry**. CDN (jsDelivr, unpkg, cdnjs), Google Fonts, Iconify API, Unsplash, dan sejenisnya ditolak proxy. Jangan buang waktu menabraknya.

```bash
bash assets/check_net.sh                                      # cek sekali di awal
bash assets/fetch_icons.sh phosphor regular arrow-right check # ikon garis
bash assets/fetch_icons.sh iconify lucide sparkles            # set Iconify lewat npm
bash assets/fetch_icons.sh brand google-color claude-color    # logo produk
```

Komponen memakai ikon: `arrow-down`, `check`, `x`, `magnifying-glass`, `link-simple`, `paper-plane-tilt`, `sparkle`, `chat-circle-text`, `file-text`, `image`, `code`, `lightning`, `coins`, `plus`, `list`, `seal-check`, `squares-four`, `play`, `repeat`, `user-square`, `house`. Ambil semuanya di awal dengan `fetch_icons.sh phosphor regular ...`.

Urutan mencari aset: **aset dari user -> bangun dengan kode -> ikon dari npm -> logo dari npm**.

**Jangan membuat tampilan yang terikat satu platform** (logo/nama produk tertentu) kalau user bilang konteksnya bisa untuk banyak platform. Pakai tampilan generik.

Selengkapnya: `references/asset-sourcing.md`.

---

## 3. Word timing (inti kualitas)

Dua jalur. **Selalu cek dulu apakah user punya subtitle**, karena jalur A jauh lebih murah.

### Jalur A: dari SRT atau VTT (dipakai kalau ada)

```bash
python3 assets/srt2words.py sub.srt words.json --report
```

Tidak ada unduhan model, selesai dalam hitungan detik. Subtitle per kata dipakai apa adanya. Per baris, waktu di dalam baris dibagi proporsional menurut panjang kata. Kalau ada caption yang terasa meleset, geser angkanya langsung di `words.json`.

### Jalur B: ASR (kalau tidak ada subtitle)

```bash
python3 assets/wordtime.py src/video.mp4 words.json
```

Model sekitar 850 MB diunduh ulang tiap sesi baru. Tidak ada akses HuggingFace.

Hasilnya `words.json` = `[[detik, "kata"], ...]`. **Cetak tabelnya dan periksa kata kunci tiap scene.** Transkrip ASR hanya untuk waktu; teks yang dipakai adalah transkrip user kalau ada.

Tidak ada cara mendengarkan audio. Validasi hanya lewat angka. Jangan pernah mengaku sudah "mendengar".

---

## 4. Jeda dan scene tambahan

VO asli sering terlalu rapat. **Tambahkan jeda hanya kalau benar-benar perlu** (misalnya scene butuh waktu agar terbaca). Sisipkan hening di batas kalimat, **jangan di tengah frasa yang mengalir**.

Tentukan daftar jeda **sebelum** menulis scene, lalu tulis semua waktu scene langsung di timeline final:

```js
const INS=45.3, DUR=6.5;              // sisipkan 6.5 dtk hening mulai detik 45.3 (0,0 kalau tidak ada)
const T = t => t>=INS ? +(t+DUR).toFixed(3) : t;
```

Semua waktu caption dibungkus `T()`. Waktu scene yang murni ada di dalam sisipan ditulis apa adanya.

Pola yang terbukti: scene tambahan tanpa VO diletakkan di sisipan, video latar dibekukan, audio VO dipotong dan disambung dengan hening. Setelah ada jeda, **mintalah user mendengarkan bagian itu sekali**, karena kita tidak bisa mendengar.

---

## 5. Build

Isi `build/project.json` (main, ins, dur, tail, zoom, scrim_from, font_preset; semua opsional, lihat kepala `assets/build.py`). Jumlah frame dan panjang video dihitung otomatis. Tulis scene proyek di `build/scenes.js` memakai komponen dan `cap()`. Lalu rakit:

```bash
python3 assets/build.py build      # template + components.js + build/scenes.js -> build/index.html (+ gsap, ikon, font preset)
node assets/sheet.js build/sheet.jpg 2.0,5.5,9.0 5 "file://$PWD/build/index.html"   # contact sheet
node assets/qa.js "file://$PWD/build/index.html"
```

Untuk uji komponen tanpa bahan asli: `python3 assets/gen_placeholders.py build 62`, lalu pakai `examples/demo-scenes.js` sebagai `scenes.js`.

**Font:** `build.py` memasang preset dari `project.json` → `font_preset` (default `klasik` = Inter + Playfair italic). `python3 assets/fonts/fontpack.py list editorial` menampilkan semua preset. Kata kunci memakai satu potongan font preset untuk semua bobot dan gaya, jadi tidak ada tebal atau miring palsu.

**Video jadi image sequence, wajib.** Jangan pakai tag `<video>`.

```bash
ffmpeg -nostdin -v error -y -i src/main.mp4 -vf "fps=30" -q:v 3 vf/main/%04d.jpg
ffmpeg -nostdin -v error -y -ss 8 -t 12 -i src/klip1.mp4 -vf "fps=30,scale=-2:640" -q:v 4 vf/c1/%04d.jpg
```

Folder `vf/` **dipakai bersama** antar versi (symlink), supaya tidak ekstrak ulang tiap revisi.

Aturan build:
- Bangun bertahap: struktur dulu, lalu scene satu per satu, cek snapshot tiap 2-3 scene.
- Satu ide per layar. Teks maksimal 3 baris pendek.
- Scene saling overlap 0.05-0.15 dtk supaya tidak ada frame kosong.
- Efek yang tidak boleh terlihat di awal (flash, cincin, kursor, panel) harus `tl.set(el,{opacity:0},0)` dulu.
- Koordinat target kursor di-hardcode setelah diukur lewat snapshot, bukan `getBoundingClientRect()` saat elemen masih bergerak.
- Hati-hati bug JS umum: `'<i>'.repeat(n)` tanpa kurung, sisa koma setelah `Object.assign` diedit, dan komentar yang memuat penutup komentar.
- Server lokal (`python3 -m http.server`) bisa mati di antara fase; kalau `ERR_CONNECTION_REFUSED`, nyalakan lagi.

---

## 6. Audio dan SFX

```bash
python3 assets/audio.py build/sfx.json src/video.mp4 build/mix.wav
```

Script ini menyisipkan hening sesuai jeda, memasang SFX, dan mencampurnya dengan VO. **SFX bawaan: 9 file di `assets/sfx/`** (click, pop, bubble-pop, whoosh, swipe, punch, notification, typing, error), dipakai otomatis; tick dibuat dari click. Pilihan: `--sfx-dir <folder>` untuk SFX milik user (dipetakan dari nama file, menang atas bawaan), `--sfx-source synth` untuk SFX sintetis saja. Cek baris `SFX dipakai:` di log. Tanyakan pilihan SFX ini di intake (bawaan / folder milikmu / sintetis / tanpa).

**Level SFX tidak tetap.** Ukur RMS VO dulu. VO normal: level SFX 0.32. VO pelan (RMS sekitar -24 dB atau lebih rendah): turunkan SFX ke sekitar 0.2 (`--sfx-level 0.2`) dan **normalisasi akhir ke sekitar -14 LUFS** (`loudnorm`) supaya cocok untuk Instagram.

SFX per aksi: `pop` objek muncul, `bubble` chip/daftar beruntun, `whoosh` panel/transisi (puncak file diletakkan tepat di waktu aksi), `swish` teks menyapu, `thud` slam/impak (file punch), `ding` sukses, `error` hal negatif/gagal, `click` klik, `type` mengetik (huruf yang rapat digabung jadi satu potongan suara ketik), `tick` counter.

**Default tanpa musik.** Tambahkan hanya kalau diminta.

Kalau ada klip yang audionya ikut dinyalakan: fade in 0.25-0.5 dtk, fade out 0.35-0.6 dtk, **tidak tumpang tindih dengan VO**.

Verifikasi dengan angka: panjang audio = panjang video, `max|x| < 0.98`, RMS SFX di bawah RMS VO.

---

## 7. Render

Bagi jadi **3 segmen paralel**:

```bash
N=$(python3 -c "print(round(TOTAL*30))"); S=$((N/3))
node assets/render.js 0 $S seg/a.mp4 sfx.json URL &
node assets/render.js $S $((2*S)) seg/b.mp4 sfx.json URL &
node assets/render.js $((2*S)) $N seg/c.mp4 sfx.json URL &
wait
printf "file 'seg/a.mp4'\nfile 'seg/b.mp4'\nfile 'seg/c.mp4'\n" > list.txt
ffmpeg -nostdin -y -f concat -safe 0 -i list.txt -c copy seg/v.mp4
ffmpeg -nostdin -y -i seg/v.mp4 -i mix.wav -c:v libx264 -preset medium -crf 20 \
  -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart out/Reel_V1.mp4
```

Jalankan di background dan cek berkala. Selalu `-nostdin` pada ffmpeg di dalam loop shell.

---

## 8. QA wajib (jangan dilewati)

```bash
node assets/qa.js URL        # safe zone + overflow + sinkron kata + frame kosong
```

Catatan: frame "kosong" di jendela wajah tanpa caption itu normal; perbaiki dengan menambah caption bila perlu. Isi HP yang tergulir keluar layar tidak dihitung sebagai pelanggaran.

Lalu **lihat sendiri**: snapshot di awal/tengah/akhir tiap scene dan 0.3 dtk setelah tiap kata kunci, susun contact sheet, baca dengan Read.

Daftar periksa:
1. Tidak ada elemen keluar safe zone (x 125-955, y 150-1720).
2. Tidak ada teks terpotong (`scrollWidth > clientWidth`).
3. Tidak ada frame kosong (sampel tiap 0.25 dtk).
4. Tidak ada kata telat: opacity kata kunci = 1 pada `T(t_kata)+0.1`.
5. Nama, handle, angka, harga, persentase, dan kata CTA sama persis dengan input user.
6. Audio: panjang sama, tidak clipping, SFX tidak menutupi VO.
7. Semua teks ber-glow dan terbaca di latar paling terang.
8. Tidak ada elemen yang sudah terlihat sebelum waktunya.
9. Tidak ada teks footage latar yang terbaca.
10. Tidak ada teks placeholder dari komponen yang tersisa.

Perbaiki semua temuan lalu render ulang. Jangan kirim yang masih cacat.

---

## 9. Pengiriman (satu video saja)

**Kirim satu file saja: versi penuh (kualitas asli), lewat chat.** Jangan membuat atau mengirim versi kompres. Dua versi membingungkan user.

- User mengunduh sendiri dari chat. Itu tidak masalah.
- Folder hasil (kalau user punya struktur folder hasil): satu folder baru per video, berisi **hanya file pendukung**: SRT, `CATATAN.txt`, dan folder project. Jangan taruh video kompres di sana. Di CATATAN tulis bahwa video final ada di chat.
- Penamaan: `Reel_V<N>.mp4` untuk tiap versi.
- Ringkasan akhir 3-5 baris: apa hasilnya, di mana filenya, dan daftar **pilihan yang saya buat sendiri** (teks contoh, label, sub-teks, urutan) supaya user tahu mana yang boleh diganti. Tambahkan pengingat "dengarkan audionya sekali, saya tidak bisa mendengar".

---

## 10. Revisi

User biasanya memberi revisi bernomor dengan screenshot bertanda.

1. Jawab **per nomor**: selesai / sebagian / tidak disarankan (dengan alasan jujur dan rekomendasi jelas).
2. Salin build ke folder versi baru (`cp -r build2 build3`), jangan timpa.
3. Terapkan lewat skrip patch Python yang `assert` tiap pola ketemu tepat sekali, supaya tidak ada perubahan yang diam-diam gagal.
4. Kalau jeda berubah: ubah daftar jeda, hitung ulang, render ulang audio dan SFX.
5. Kalau revisi mengubah konsep visual (bukan sekadar angka/teks), **ulangi gerbang 2** dulu sebelum render.
6. Render ulang, QA ulang pada scene yang berubah plus dua scene tetangga.
7. Kirim `Reel_V<N>.mp4` (versi penuh saja) + ringkasan perubahan, bukan cerita teknis.

---

## 11. Batasan (jujur ke user)

- Tidak bisa mendengar audio. Sinkron dan level hanya diverifikasi lewat angka dan visual.
- Frame diam di storyboard tidak menunjukkan gerakan dan timing.
- Transkrip hasil ASR bisa salah pada nama produk dan istilah asing. Minta user mengecek bagian yang meragukan.
- Pemakaian bisa terhenti di tengah proses karena batas penggunaan; setelah reset, user perlu mengirim pesan lanjut.
- Resolusi aset user menentukan ketajaman.
- Sesi cloud bersifat sementara. Simpan folder build (tanpa `vf/`) kalau diminta.

---

## Berkas pendukung

| Berkas | Isi |
|---|---|
| `references/style-system.md` | Token warna, tipografi, glow, komposisi artistik, safe zone, mockup HP |
| `references/scene-recipes.md` | Resep scene + tabel parameter komponen siap pakai |
| `references/asset-sourcing.md` | Host yang bisa dijangkau, paket npm pengganti CDN, Lottie, GIF, lisensi |
| `references/production.md` | Setup environment, word timing, audio, render, QA secara rinci |
| `assets/template.html` | Kerangka halaman (punya penanda COMPONENTS dan SCENES) |
| `assets/components.js` | 14 komponen generik (bgMotion + 13 scene) |
| `assets/build.py` | Rakit template + components.js + scenes.js jadi index.html |
| `assets/gen_placeholders.py` | Aset palsu untuk uji komponen |
| `examples/demo-scenes.js` | Contoh pemakaian semua komponen |
| `assets/preflight.sh` | **Dijalankan paling awal.** Cek dan pasang mesin, beri verdict |
| `assets/srt2words.py` | Ubah SRT atau VTT jadi `words.json` |
| `assets/check_net.sh` | Cek sumber mana yang bisa dijangkau |
| `assets/fetch_icons.sh` | Ambil ikon dan logo dari npm |
| `assets/iconify2svg.js` | Ubah set `@iconify-json/*` jadi SVG |
| `assets/lottie.js` | Pembungkus lottie-web deterministik |
| `assets/sheet.js`, `assets/snap.js`, `assets/_chrome.js` | Contact sheet, snapshot, pencari browser render (dipakai render.js/qa.js) |
| `assets/vendor/icons-regular.json` | 1.512 ikon garis Phosphor regular bawaan (ditulis otomatis oleh build.py, tanpa internet) |
| `assets/wordtime.py` | VAD + whisper prefix decoding |
| `assets/fonts/` | Font pack (21 font OFL) + `fontpack.py` (preset E1-E9) + `preview-editorial.jpg` |
| `assets/audio.py` | Sisip jeda, SFX (milik user → 9 bawaan → sintetis), mix |
| `assets/sfx/` | 9 SFX bawaan: click, pop, bubble-pop, whoosh, swipe, punch, notification, typing, error |
| `assets/render.js` | Renderer Playwright paralel |
| `assets/qa.js` | Pemeriksa safe zone, overflow, sinkron kata, frame kosong |