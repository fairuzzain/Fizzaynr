---
name: dark-motion
description: "Edit video orang berbicara (talking head, podcast, UGC; vertikal maupun horizontal) jadi reel vertikal 1080x1920 bertema gelap dengan motion graphic modern non-kartun: caption per kata yang dikunci ke suara, potong jeda otomatis, zoom berirama, latar blur, scene grafis, SFX halus, lalu dirender jadi MP4 di bawah 30 MB. Semua hal soal selera (warna, font, glow, potongan jeda, musik, penutup) ditanyakan dulu ke user. Pakai saat user minta mengedit video jadi reel, short, atau TikTok, menambah caption atau animasi ke video podcast/talking head, atau membuat motion graphic dari rekaman orang berbicara."
---

# Dark Motion

> **Bahasa utama: Bahasa Melayu Malaysia.** Semua output skill ini (skrip, VO/TTS, dialog, caption,
> teks atas skrin, CTA, tajuk, kapsyen media sosial) dan semua soalan serta laporan kepada pengguna
> ditulis dalam Bahasa Melayu Malaysia: ejaan, kosa kata dan loghat Malaysia, bukan Bahasa Indonesia.
> Bahasa lain hanya jika pengguna memintanya. Prompt untuk model imej/video boleh kekal dalam Bahasa
> Inggeris, tetapi teks yang diucapkan atau dipaparkan di dalamnya tetap Bahasa Melayu. Peraturan ini
> mengatasi mana-mana default bahasa lain dalam fail ini. Lihat `CLAUDE.md` → Bahasa.

Skill ini mengubah **rekaman orang berbicara** jadi video vertikal 1080x1920 30fps yang gelap, bersih, dan terasa mahal. Animasinya halus dan tidak ada satu pun elemen kartun. Topiknya bebas: isi layar selalu diturunkan dari ucapan dan aset user, bukan dari contoh di skill ini.

**Yang tetap, apa pun permintaannya:** tema gelap, tanpa elemen kartun, animasi simpel tapi rapi, dan setiap kata muncul tepat saat diucapkan.

**Pembeda dari Serif Editorial Reel:** Dark Motion = **"dark vibe" penuh**: SEMUA latar gelap (footage blur gelap, foto/video ber-overlay hitam, `gfxBg`), tidak pernah ada scene terang/putih atau panel kertas; huruf default **Sans** tebal modern (Inter 900). Serif Editorial Reel yang memakai campuran scene gelap dan terang dengan huruf default Serif italic. Jangan membuat hasil Dark Motion mirip Serif Editorial Reel.

**Yang mengikuti user (selalu ditanyakan dulu):** warna, gaya huruf, glow, potongan jeda, kepadatan caption, zoom, suara tambahan, penutup, dan bentuk vertikal untuk video horizontal.

## Cara bicara ke user

- Pakai bahasa user. Simpel, langsung ke inti, ramah.
- User biasanya **bukan orang teknis**. Jangan tampilkan perintah, nama file, path, atau istilah seperti "render chunk", "LUFS", "words.json". Katakan apa artinya: "videonya sedang dirakit, sekitar 6 menit lagi".
- Kabar progres singkat di titik penting saja, dengan perkiraan waktu kalau langkahnya lama.
- Kalau permintaan user akan membuat hasil jelek atau tidak akan berhasil, bilang sekali dengan alasan dan saran, lalu ikuti keputusannya.
- Kamu tidak bisa mendengar audio. Jangan pernah mengaku sudah "mendengar".

## Alur kerja

Buat task list ini di awal:
**cek lanjutan → preflight → terima & analisis video (+ lihat folder aset user) → pertanyaan (satu pesan) → siapkan video & klip → caption otomatis → scene → gerbang contact sheet → render → QA → kirim.**

`SK` = folder tempat SKILL.md ini berada. Folder skill hanya-baca; semua pekerjaan dilakukan di folder kerja yang bisa ditulisi. Semua script dipanggil dengan path lengkap `$SK/assets/...`.

---

## 0. Cek lanjutan

Kalau `build/STATE.md` sudah ada di folder kerja, ini pekerjaan yang terputus (batas pemakaian, koneksi, atau user bilang "lanjut"). Baca file itu, bilang ke user "saya lanjutkan dari bagian X", lalu teruskan dari langkah yang belum selesai.

Perbarui `build/STATE.md` setiap kali satu langkah selesai. Isinya singkat:

```
# STATE
langkah selesai: preflight, analisis, pertanyaan, prep, timing, cuts, frames
berikutnya: caption otomatis
video: 2 part, horizontal -> mode track, 142 dtk -> 126 dtk setelah potong jeda
pilihan user: warna dari video (C1 #.., C2 #..), sans, glow ya, jeda sedang, caption pendek, zoom ya, SFX, CTA komentar "MAU"
catatan: nama "Rizky" harus persis; angka "37%"
```

Kalau sandbox ternyata baru (file hilang), minta user mengirim ulang videonya. Pilihan-pilihannya diambil dari percakapan, jangan ditanyakan ulang.

## 1. Preflight

```bash
SK="<folder tempat SKILL.md ini>"     # kalau tidak tahu: SK=$(dirname "$(find / -path '*/dark-motion/SKILL.md' 2>/dev/null | head -1)")
mkdir -p ~/dm && cd ~/dm
bash "$SK/assets/preflight.sh" build
source build/env.sh          # memberi $SK, $PY, $BUILD, dll. Ulangi di setiap perintah shell baru.
```

| Verdict | Artinya |
|---|---|
| `READY` | Lanjut normal |
| `READY_NO_ASR` | Pengenal suara tidak bisa dipasang. **Minta file subtitle .srt/.vtt** ke user (bisa dibuat dengan fitur caption otomatis di CapCut atau aplikasi edit lain, lalu diekspor .srt) |
| `BLOCKED` | **Berhenti.** Sampaikan pesan yang dicetak script, dengan bahasa biasa |

Font, mesin animasi, ikon, dan model deteksi wajah sudah ikut di dalam skill. Skill tetap jalan walaupun internet sesi dimatikan; yang butuh internet hanya pengenal suara (kalau user tidak punya subtitle).

## 2. Terima dan analisis video

**Kalau user belum mengirim video:** minta videonya, dan sebutkan dua batas ini sekaligus supaya tidak gagal upload:
- Maksimal **30 MB per file**. Kalau lebih besar: potong jadi beberapa bagian (skill akan menyambungnya), atau ekspor ulang di 720p.
- Maksimal **3 menit** total per video.

Lalu analisis semua part, sesuai urutan yang user maksud:

```bash
$PY $SK/assets/prep.py build --analyze "video1.mp4" "video2.mp4"
```

Hasilnya: durasi, bentuk (vertikal/horizontal), jumlah wajah, dan kondisi suara. Baris `PERLU DITANYAKAN` dimasukkan ke pesan pertanyaan di langkah 3. Kalau lebih dari 3 menit, tanyakan bagian mana yang dipakai (atau tawarkan memilihkan bagian terkuat setelah transkrip ada).

## 3. Satu pesan berisi semua pertanyaan

Tanyakan **semuanya dalam satu pesan**, sebagai pilihan bernomor dengan default yang ditandai. User boleh menjawab singkat ("1b 4a, sisanya default") atau "default semua". Kalau ada alat pilihan ganda di sesi ini, boleh dipakai (maksimal 4 pertanyaan per panggilan). **Jangan menanyakan hal baru di tengah pengerjaan**, kecuali sesuatu yang tidak bisa ditebak.

**Selera (selalu ditanyakan):**

| # | Pertanyaan | Pilihan | Default |
|---|---|---|---|
| 1 | Warna aksen | dari video / warna brand (sebutkan) / netral (hijau limau + biru) | dari video |
| 2 | Gaya huruf kata kunci | **sans tebal modern** / serif miring elegan / **preset dari font pack** (sarankan yang sans: E7 Tegas, E8 Teknologi, E9 Modern Bulat; tunjukkan `assets/fonts/preview-editorial.jpg`) / font brand (kirim file .ttf/.otf) | sans tebal |
| 3 | Teks menyala (glow) | ya, di latar gelap / polos berbayang | ya |
| 4 | Potong jeda | halus / sedang / agresif (gaya cepat) / jangan dipotong | sedang |
| 5 | Kepadatan caption | pendek 1-3 kata / sedang 3-6 kata | pendek |
| 6 | Zoom berirama (menyamarkan potongan, menjaga perhatian) | ya / tidak | ya |
| 7 | Suara tambahan | **SFX bawaan** (9 file: click, pop, bubble pop, whoosh, swipe, punch, notification, typing, error) / SFX halus sintetis / **SFX dari folder milikmu** / SFX + musik dari file milikmu / tanpa | SFX bawaan (kalau user punya folder SFX: sarankan folder itu) |
| 8 | Penutup | ajak komentar kata tertentu (sebutkan katanya) / ajak follow / "link di bio" / "klik link di bawah" / tanpa ajakan | tanpa ajakan |
| 9 | Bagian **full motion graphic** (tanpa wajah) | tidak ada, wajah + scene sesekali / sebutkan part atau rentang detik (mis. "part 2 dan 3") | tidak ada |
| 10 | Aset di folder proyek (logo, screenshot, foto, klip) | boleh dipakai kalau cocok dengan ucapan / jangan dipakai | boleh |

Catatan untuk nomor 7: sarankan musik ditambahkan sendiri di aplikasi Instagram/TikTok karena paling aman soal hak cipta. Skill tidak mengambil musik dari internet. Kalau user memilih folder SFX miliknya, salin ke `build/aset/sfx/` dan isi `project.json` → `audio.sfx_dir` (lihat production.md); jenis yang tidak ada filenya memakai SFX bawaan, dan itu disebutkan ke user. Kalau user memilih SFX halus sintetis: `audio.sfx_source: "synth"`.

Catatan untuk nomor 9: "full motion graphic" berarti wajah **tidak tampil** di rentang itu, latarnya `gfxBg()` (grid halus + cahaya bergerak), bukan wajah yang diblur. Catat rentangnya per part di STATE.md; jangan menebak part mana yang dimaksud. Kalau user menyebut part, waktu mulai tiap part dicetak oleh prep.py.

**Hanya kalau relevan (dari hasil analisis):**
- Video horizontal → bentuk vertikal: **ikuti wajah** (wajah besar, sedikit lebih lembut) / **utuh di tengah** dengan latar blur (tidak ada yang terpotong) / **dua orang atas-bawah** (podcast 2 orang; bagian satu orang otomatis ikuti wajah). Rekomendasikan satu sesuai analisis.
- Lebih dari satu orang → mau diberi label nama? Kalau ya: nama dan perannya. **Jangan mengarang nama.**

**Konten:**
- File subtitle .srt kalau punya (lebih cepat dan ejaan pasti benar). Kalau tidak ada, skill membuat sendiri dari suara (beberapa menit).
- Nama, merek, angka, atau istilah yang harus ditulis persis.
- Aset opsional yang membuat video terasa milik user: foto produk, screenshot, logo, contoh hasil, klip pendukung.

**Kalau user sudah punya folder aset** (gambar, klip, SFX di folder proyek), lihat isinya sendiri sebelum bertanya: buat lembar gambar dan `clipscan.py` untuk klip, lalu sebutkan di pesan pertanyaan aset mana yang cocok untuk bagian mana. Jangan minta user mengirim ulang yang sudah ada.

Kalau user tidak menjawab atau bilang "langsung saja": pakai default, dan tulis asumsinya di awal pesan berikutnya.

Setelah dijawab, tulis ringkasan pilihan user ke `build/STATE.md`.

## 4. Siapkan video

Tanpa interaksi dengan user. Sebelum mulai, beri perkiraan waktu (sekitar 1-2 menit per menit video, ditambah beberapa menit kalau transkrip dibuat dari suara).

```bash
# a. gabung part, jadikan 1080x1920, bersihkan suara bising
$PY $SK/assets/prep.py build "video1.mp4" "video2.mp4" [--mode track|fit|stack] [--trim mulai:selesai]

# b. waktu tiap kata: dari subtitle user, ATAU dari suara
$PY $SK/assets/srt2words.py sub.srt build/words.json --report
$PY $SK/assets/wordtime.py build/src/main.mp4 build/words.json --lang ms     # ms (default, Bahasa Melayu), en, id, ... atau auto

# c. rapikan waktu kata + potong jeda (SELALU dijalankan, level dari jawaban user)
$PY $SK/assets/cuts.py build --level sedang          # tidak | halus | sedang | agresif

# d. jadikan image sequence
$PY $SK/assets/frames.py build

# e. klip pendukung: cek dulu teks tertanam, lalu ekstrak HANYA potongan yang bersih
$PY $SK/assets/clipscan.py build/scan.jpg klip1.mp4 klip2.mp4 --every 2      # lihat dengan Read
$PY $SK/assets/frames.py build --clips-only --clip-h 960 --clip ugc:klip1.mp4:0:4.5 --clip com:klip2.mp4:8:4.5
```

**Klip pendukung:** klip user sering membawa caption lama, judul, atau watermark di beberapa detik saja. Selalu jalankan `clipscan.py`, pilih rentang tanpa teks, dan ekstrak 4-5 detik per potongan. Klip yang teksnya ada di hampir semua detik tidak dipakai. Selalu `--clips-only` setelah ada efek yang dibakar ke `vf/main` (bake.py mencatatnya di `build/baked.txt`; frames.py tanpa `--clips-only` akan menimpanya). `--clip-h 960` untuk klip di HP utama/kartu besar, 534 untuk ubin dinding video.

**Gambar user:** periksa pinggirannya sebelum dipakai. Screenshot dari aplikasi sering membawa bingkai putih, sudut membulat, atau ikon tombol di pojok; potong dengan `ffmpeg -vf crop=...` sampai bersih. Logo diproses sesuai resep O1 (scene-recipes.md), jangan ditempel utuh.

Setelah b: baca transkripnya. Teks yang tampil harus sesuai ucapan; perbaiki salah dengar (nama produk, istilah asing, angka) dengan mengubah teks di `words.json` saja, **waktunya jangan diubah**. Kalau user memberi naskah, pakai ejaan dari naskah. Kata yang meragukan dicatat untuk disebut di gerbang contact sheet, bukan ditebak diam-diam.

Kalau SRT dibuat per part, pakai `--offset` dengan waktu mulai part yang dicetak prep.py.

Laporkan ke user dalam 1-2 kalimat: durasi akhir, berapa detik jeda yang dipotong, dan apakah suaranya dibersihkan.

## 5. Kata kunci dan caption otomatis

```bash
$PY $SK/assets/autocap.py build --list       # transkrip bernomor
$PY $SK/assets/palette.py build              # usulan warna aksen dari footage (kalau user memilih "dari video")
```

Tulis `build/project.json` dari jawaban user, dan `build/capplan.json` dari isi transkrip. Formatnya lengkap di `references/production.md`. Pilih kata kunci dengan sengaja:
- Sekitar satu kata kunci per 4-8 detik: kata yang membawa makna, angka, nama, atau emosi. Bukan kata sambung.
- `k1` untuk hal positif, berhasil, pilihan; `k2` untuk info, teknis, kategori; `s` untuk penekanan netral; `X` (kata hantaman) **maksimal dua per video**.
- `hook_end` = akhir kalimat pembuka. Kata-katanya tampil sebagai judul besar.
- `skip` = rentang yang teksnya ditampilkan oleh scene buatan sendiri.

```bash
$PY $SK/assets/autocap.py build
```

autocap memilih posisi caption yang tidak menutupi wajah (atas, bawah, atau garis tengah untuk dua orang), memasang gradien gelap dan blok warna di latar terang, membuat zoom berirama tepat di titik potong, dan menambah SFX halus di kata kunci. Baca pratinjaunya. Kalau ada yang janggal, ubah `capplan.json` lalu jalankan ulang. **Jangan mengedit `captions.js` dengan tangan.**

## 6. Scene

Caption + zoom sudah membuat video layak tonton. Scene grafis adalah lapisan yang membuatnya terasa *diedit*. Tulis di `build/scenes.js` memakai helper template. Resepnya ada di `references/scene-recipes.md`, aturan visualnya di `references/style-system.md`.

**Ritme:** satu scene khusus kira-kira tiap 5-10 detik, di momen yang memang punya isi (angka, daftar, perbandingan, alat, kutipan). Sisanya cukup caption dan zoom. Untuk video panjang (di atas 90 detik), batasi sekitar 12-15 scene dan pakai resep yang ringan.

**Waktu:** semua waktu di scenes.js memakai detik **hasil**. Kalau mengambil detik dari transkrip, bungkus dengan `T()`: `grp(T(12.4), T(16.6))`. Kalau sebuah scene butuh waktu baca tanpa suara, tambahkan jeda di `project.json` → `pauses`. Halaman dan audio menyesuaikan sendiri. Untuk scene penutup setelah kalimat terakhir, isi `project.json` → `tail` (3-6 detik).

**Jeda untuk dicerna:** animasi transformasi (A + B = C), kartu perbandingan, atau daftar yang padat butuh waktu tanpa suara. Jangan menebak posisi jeda: cari titik yang benar-benar hening dengan `gaps.py`, lalu taruh jeda di detik yang disarankannya. Patokan panjang: 1,5-2,0 dtk per hasil penggabungan, 1,5-2,5 dtk untuk kartu yang perlu dibaca. Setelah mengubah `pauses`: autocap lalu assemble. Di dalam scenes.js, awal jeda di detik hasil = `T(detik_sebelum_jeda)+0,01`; semua aksi yang terjadi selama jeda diberi waktu relatif dari situ.

```bash
$PY $SK/assets/gaps.py build --from 14 --to 17      # daftar hening + "taruh jeda di ..."
```

**Bagian full motion graphic** (jawaban nomor 9): satu `gfxBg(t0,t1)` untuk seluruh rentang, dipanggil **sebelum** scene di rentang itu, dan rentang caption-nya masuk `skip` kalau teksnya sudah dibawa scene. Mulai tepat setelah kata terakhir part sebelumnya, selesai tepat sebelum kata pertama part sesudahnya. Jangan memecahnya per scene: celah sekecil apa pun membuat wajah berkedip di antara scene. Di rentang ini setiap kalimat tetap punya visual (HP berisi klip, kartu, logo, angka), tidak boleh ada layar yang hanya berisi latar.

```bash
$PY $SK/assets/assemble.py build
node $SK/assets/snap.js build/snaps 3.2 9.0 14.5 --url "file://$BUILD/index.html"   # lihat sendiri tiap 2-3 scene
```

### Hukum visual (ringkas, detailnya di style-system.md)

1. **Tidak ada elemen kartun.** Dilarang: emoji 3D, ikon bulat warna-warni, stiker, maskot, confetti, bintang, mata, tangan kartun. Boleh: garis tipis, ikon garis monokrom ukuran kecil, bentuk geometris, mockup perangkat, UI yang direkonstruksi.
2a. **Latar selalu gelap.** Tidak ada scene putih/terang, panel kertas, atau kartu putih besar yang memenuhi layar. Kartu dan chip boleh terang kecil di atas latar gelap. Kalau footage user terang, gelapkan dengan overlay/scrim.
2. **Latar scene tidak pernah warna rata.** Pakai `bgBlur()` (footage sendiri diblur, paling sering), `bgPhoto()`, `bgVideo()`, `videoWall()` (dinding klip user), atau `gfxBg()` (untuk bagian full motion graphic), selalu dengan overlay gelap. Pengecualian hanya untuk hentakan yang disengaja (misalnya roda angka di layar hitam).
3. **Tidak ada ruang nganggur yang tidak disengaja.** Kosong hanya untuk jeda dramatis atau momen wajah.
4. **Teks harus kontras dengan latar di belakangnya.** Glow hanya di latar gelap; di latar terang pakai gradien gelap yang memudar plus blok warna. Untuk caption, autocap sudah melakukannya; scene buatan sendiri wajib mengikuti aturan yang sama.
5. **Safe zone:** teks dan objek penting di x 125-955, y 150-1560.
6. **Gambar user yang jelek atau ramai dibangun ulang** sebagai UI bersih (panel, kartu, daftar). Isinya diambil dari gambar aslinya.
7. **Animasi simpel tapi rapi:** satu gerakan per elemen, 0,22-0,45 detik, tanpa bounce berlebihan. Kilatan, getaran layar, dan zoom menghentak maksimal dua kali per video.
8. **Warna punya arti:** C1 positif/pilihan, C2 info/teknis. Merah hanya kalau user minta atau isinya memang soal kerugian/larangan.
9. **Tidak ada kebocoran:** teks bawaan di footage latar (watermark, caption lama) tidak boleh terbaca. Wajah tidak boleh menumpuk transparan dengan latar grafis saat transisi.
10. **Klip pendukung tampil di dalam frame HP**, bukan dipotong full layar menutupi wajah: `phoneTrio()` (tengah besar, dua samping miring, muncul bergantian di kata yang relevan). Full layar hanya kalau user memintanya.
11. **Logo tidak pernah ditempel utuh di lingkaran atau kotak hitam.** Bangun ulang: simbolnya dipisah dan latar hitamnya dihilangkan lewat blend, teksnya diketik ulang dengan gradien warna logo, dan tiap baris muncul saat nama brand diucapkan (`logoBuild()`, resep O1).
12. **Panah ajakan harus tegas:** panah datar solid dua warna yang memantul (`bigArrow()`), bukan ikon garis tipis. Ikon garis tetap dipakai untuk label kecil dan chip.
13. **Alur atau proses yang diucapkan berurutan ditampilkan sebagai penggabungan "A + B = C"** (resep N1): dua kartu dengan tanda plus, meluncur dan bertabrakan, lalu hasilnya lahir dengan kilatan. Hasil tiap tahap memakai aset asli user; kalau hasil akhirnya video, putar potongan video user sendiri di kartu itu. Tahap kedua boleh menggabungkan hasil tahap pertama dengan bahan berikutnya.
14. **Scene angka atau daftar diberi dinding video bergulir di latar** (`videoWall()`) kalau user punya klip yang relevan; blur wajah hanya kalau tidak ada klip.
16. **Teks yang berkaitan = SATU blok rapat (jangan "social distancing").** Kalimat yang dibaca berurutan, misalnya "Di kelas ini ada" + "100+" + "video dibedah", disusun sebagai satu blok di satu titik tengah dengan `stack()`, bukan disebar ke atas-tengah-bawah layar. Jarak antar-baris di dalam blok 12-36 px (sekitar 0,1-0,3 x tinggi huruf baris yang lebih kecil); angka/kata raksasa diberi `lineHeight:'.9'` supaya kotak hurufnya tidak menambah jarak. Ruang kosong ada di LUAR blok. Jarak antar-blok yang beda ide minimal 2x jarak di dalam blok. Cek di contact sheet: kalau mata harus melompat dari satu baris ke baris berikutnya, rapatkan.
15. **Tidak ada layar kosong di awal scene.** Begitu sebuah scene menggantikan wajah, elemen utamanya sudah muncul dalam 0,3 dtk; jangan menunggu kata berikutnya sambil hanya menampilkan latar dan label kecil. Kalau kata pemicunya masih jauh, tampilkan dulu elemen pembuka (judul kecil, kartu kosong yang menunggu, atau elemen dari scene sebelumnya yang bertahan).

### Hook 5 detik pertama

Wajib dipikirkan. Pilih minimal satu: **judul besar** (kalimat pembuka sebagai judul, sudah otomatis lewat `hook_end`), **efek pembuka** (glitch atau sinyal menyala yang dibakar ke frame), atau **visual masalah** (satu angka atau benda yang langsung menjelaskan masalah). Lebih baik gabungkan dua.

## 7. Gerbang: contact sheet

Render itu lama. Sebelum render, **selalu** kirim satu contact sheet dan tunggu persetujuan.

```bash
node $SK/assets/sheet.js build/sheet.jpg 1.2,6.5,11.0,18.4,24.0 5 "file://$BUILD/index.html"
```

- Satu frame per scene, di detik saat scene sudah tampil penuh. Maksimal 5-6 kolom. Lihat sendiri dengan Read sebelum dikirim.
- Di pesan yang sama: daftar scene (satu baris per scene: detik, apa yang muncul), aset pengganti yang kamu buat sendiri, kata yang meragukan, dan perkiraan lama render.
- Sampaikan batasnya: gambar diam tidak menunjukkan gerakan dan suara.
- Kalau user bilang "langsung render aja", lewati gerbang ini.

## 8. Render

```bash
$PY $SK/assets/render_all.py build --max-minutes 8
```

Satu perintah: audio (suara + SFX + musik + jeda; SFX bawaan atau milik user dipakai otomatis, cek baris `SFX dipakai:` di log), render paralel, sambung, encode final **di bawah 29 MB**. Kalau keluar `BELUM SELESAI`, **jalankan perintah yang sama lagi**; bagian yang sudah jadi tidak diulang. Ulangi sampai `SELESAI`.

Perkiraan: sekitar 5 menit per menit video di mesin 2 inti. Beri tahu user sebelum mulai.

## 9. QA

```bash
node $SK/assets/qa.js "file://$BUILD/index.html"
for t in 2 10 20 30; do ffmpeg -nostdin -v error -y -ss $t -i build/out/Reel_V1.mp4 -frames:v 1 -vf scale=360:-2 build/qa_$t.jpg; done
```

qa.js memeriksa safe zone, teks terpotong, kata telat, frame kosong, dan error halaman. Lalu **lihat sendiri frame dari MP4 hasil** (gabungkan jadi satu lembar dan baca dengan Read).

Daftar periksa:
1. Tidak ada elemen keluar safe zone.
2. Tidak ada teks terpotong atau saling menempel; teks yang berkaitan tampil sebagai satu blok rapat.
3. Tidak ada kata telat atau elemen yang muncul sebelum waktunya.
4. Caption tidak menutupi wajah.
5. Nama, angka, dan kata CTA sama persis dengan input user.
6. Semua teks terbaca di latar paling terang yang dilewatinya.
7. Tidak ada teks footage latar yang terbaca.
8. Tidak ada placeholder yang tertinggal.
9. Ukuran file di bawah 29 MB; panjang audio sama dengan video (render_all sudah mengecek).

Perbaiki semua temuan, render ulang, baru kirim.

## 10. Kirim

Kirim **satu file** lewat cara normal sesi ini untuk menyerahkan file ke user. Nama file `Reel_V<N>.mp4`. Ringkasan akhir 3-5 baris:
- apa hasilnya (durasi, gaya),
- pilihan yang kamu buat sendiri (aset pengganti, teks contoh, warna dari video),
- pengingat: "tolong dengarkan audionya sekali, saya tidak bisa mendengar."

## 11. Revisi

User biasanya memberi revisi bernomor, kadang dengan screenshot.

1. Jawab **per nomor**: selesai / sebagian / tidak disarankan (dengan alasan jujur).
2. Sebelum mengubah, simpan versi lama: salin `scenes.js`, `capplan.json`, `project.json` ke `build/versi/V<N>/`.
3. Ubah di sumbernya: caption lewat `capplan.json` + autocap, scene lewat `scenes.js`, warna/font/jeda/audio lewat `project.json`, potongan jeda lewat cuts.py (lalu frames.py dan autocap lagi).
4. Kalau konsep visual berubah, ulangi gerbang contact sheet.
5. `assemble.py` → `render_all.py` (otomatis render ulang karena halaman berubah, hasilnya `Reel_V<N+1>.mp4`) → QA pada bagian yang berubah plus tetangganya.
6. Kirim file baru + ringkasan perubahan per nomor, bukan cerita teknis.

**Pola revisi yang sudah pernah terjadi** (cegah sejak versi pertama):

| Keluhan user | Penyebab | Yang dilakukan dari awal |
|---|---|---|
| "Tampilkan video-videonya di frame HP" | Klip dipotong full layar | `phoneTrio()` untuk contoh video |
| "Masih ada bagian putihnya" | Screenshot dipakai apa adanya | Potong pinggiran UI sebelum dipakai |
| "Logo jangan dibikin bulat / jelek" | Logo utuh dimasker lingkaran | `logoBuild()` dengan simbol + teks diketik ulang |
| "Panahnya jelek" | Ikon garis tipis | `bigArrow()` |
| "Tampilkan video di background" (scene angka) | Latar hanya blur | `videoWall()` dari klip user |
| "Part X dan Y full motion graphic" | Tidak ditanyakan di awal | Pertanyaan nomor 9; satu `gfxBg()` per rentang |
| "Gabungkan jadi ..., lalu jadi ..." | Langkah alur hanya didaftar | Resep N1, bertahap, hasil memakai aset/klip user |
| "Tambah jeda supaya bisa dicerna" | Animasi padat tanpa waktu napas | `gaps.py` + `pauses` 1,5-2 dtk per hasil |
| SFX yang dipakai bukan milik user | Mixer hanya SFX sintetis | `audio.sfx_dir` |

## 12. Batasan, sampaikan jujur

- Tidak bisa mendengar audio; sinkron dan level hanya diverifikasi lewat angka.
- Contact sheet tidak menunjukkan gerakan dan timing.
- Transkrip otomatis bisa salah pada nama dan istilah asing.
- Batas 30 MB membuat video yang lebih panjang dari sekitar 90 detik sedikit lebih lembut gambarnya.
- Mode "ikuti wajah" memperbesar potongan video horizontal, jadi gambarnya lebih lembut dari aslinya.
- Pekerjaan bisa terhenti karena batas pemakaian; setelah reset, user cukup mengetik "lanjut".

---

## Berkas pendukung

| Berkas | Isi |
|---|---|
| `references/style-system.md` | Warna, mode huruf, kelas teks, tiga alat kontras, komposisi, safe zone, mockup HP, easing, larangan |
| `references/scene-recipes.md` | Resep scene menurut pola ucapan: angka, daftar, perbandingan, alat, kutipan, cerita, penekanan, penutup |
| `references/production.md` | Format project.json dan capplan.json, detail tiap alat, jeda dan ekor, render, ukuran file, masalah umum |
| `references/asset-sourcing.md` | Urutan mencari aset, berkas bawaan, ikon, logo, batas dan lisensi |
| `assets/preflight.sh` | Cek dan siapkan mesin, beri verdict |
| `assets/prep.py` | Analisis; gabung part; jadikan vertikal (track/fit/stack); bersihkan suara |
| `assets/srt2words.py` | Subtitle .srt/.vtt jadi waktu per kata |
| `assets/wordtime.py` | Waktu per kata dari suara (pasang sendiri saat dibutuhkan) |
| `assets/cuts.py` | Rapikan waktu kata + potong jeda |
| `assets/frames.py` | Video jadi image sequence (utama + blur + klip); `--clips-only` untuk menambah klip tanpa menimpa efek yang dibakar |
| `assets/clipscan.py` | Lembar sampel klip pendukung untuk memilih potongan tanpa teks tertanam |
| `assets/gaps.py` | Cari titik hening untuk menyisipkan jeda (`pauses`) |
| `assets/palette.py` | Usulan warna aksen dari footage |
| `assets/autocap.py` | Caption otomatis, posisi anti-wajah, kontras, zoom berirama, SFX kata kunci |
| `assets/assemble.py` | Rakit template + konfigurasi + caption + scene jadi index.html |
| `assets/template.html` | Kerangka halaman dan semua helper scene, termasuk `gfxBg`, `phoneTrio`, `videoWall`, `imgCard`, `mergeTo`, `popIn`, `plusSign`, `chipC`, `logoBuild`, `bigArrow` |
| `assets/render_all.py` | Render satu perintah, bisa dilanjut, hasil < 29 MB |
| `assets/mix.py` | Audio final: suara, jeda, SFX (milik user → 9 SFX bawaan → sintetis), musik + ducking, -14 LUFS |
| `assets/sfx/` | 9 SFX bawaan: click, pop, bubble-pop, whoosh, swipe, punch, notification, typing, error |
| `assets/qa.js`, `sheet.js`, `snap.js` | Pemeriksa otomatis, contact sheet, snapshot |
| `assets/bake.py` | Bakar glitch/grain/scan ke frame; potong orang dari latar |
| `assets/fetch_icons.sh` | Ikon/logo tambahan dari npm (butuh internet, opsional) |
| `assets/vendor/` | Mesin animasi, font, ikon, model wajah bawaan. Lisensi di `vendor/LICENSES.md` |
| `assets/fonts/` | Font pack (21 font OFL) + `fontpack.py` (preset E1-E9) + `preview-editorial.jpg`. Pakai: `project.json` → `"font": {"preset": "tegas"}` |
