---
name: "script-to-motion-reel"
description: "Buat video motion graphic vertikal 1080x1920 (reel/promo) dari MP3 voiceover + transkrip + brand guideline + folder aset, dengan animasi kinetic yang dikunci ke tiap kata VO: kinetic typography, emoji 3D sebagai metafora, panel putih bergelombang, chip glossy, counter, mockup HP, kursor + klik, CTA komentar. Perkakas siap pakai (template, rakit, render yang bisa dilanjut, mixer -14 LUFS dengan SFX bawaan atau milik user, QA otomatis, contact sheet). Pakai saat user minta video motion graphic, reel promo, atau kinetic typography dari voiceover/naskah, atau menyebut script to motion."
---

# Script to Motion Reel

Skill ini membuat video motion graphic vertikal (9:16, 1080x1920, 30fps) gaya "kinetic typography + mockup + metafora" dari bahan:

1. **MP3 voiceover** + **transkrip TXT** (atau subtitle .srt)
2. **Brand guideline** (warna, font, logo, gaya)
3. **Folder aset** (video/gambar/screenshot, nama file jelas)

Hasil referensi (V6, 86,9 detik, 18 scene) adalah promo kelas AI berwarna charcoal+merah. Warna/font itu hanya contoh; semua harus diambil dari brand guideline user.

Prinsip utama: **setiap kata penting muncul tepat saat diucapkan**, setiap elemen punya SFX, tidak ada glitch/teks terpotong, dan hasilnya terasa dibuat motion designer profesional (bukan slideshow).

`SK` = folder tempat SKILL.md ini berada. Folder skill hanya dibaca; semua pekerjaan dilakukan di folder kerja proyek. Semua script dipanggil dengan path lengkap `$SK/assets/...`.

## Cara bicara ke user

- Bahasa Indonesia sederhana, langsung ke inti, ramah.
- User biasanya **bukan orang teknis**. Jangan tampilkan perintah, path, atau istilah seperti "render chunk", "LUFS", "words.json". Katakan artinya: "videonya sedang dirakit, sekitar 3 menit lagi".
- Kabar progres singkat di titik penting saja, dengan perkiraan waktu kalau langkahnya lama.
- Kalau permintaan user akan membuat hasil jelek atau tidak akan berhasil, bilang sekali dengan alasan dan saran, lalu ikuti keputusannya.
- Tidak bisa mendengar audio. Jangan pernah mengaku sudah "mendengar".

## Alur kerja

Buat task list ini di awal:
**cek lanjutan → preflight → intake (satu pesan) → timing VO → rencana scene → aset → bangun scene → gerbang contact sheet → render → QA → kirim.**
Langkah terakhir sebelum kirim selalu QA visual.

---

## 0. Cek lanjutan

Kalau `build/STATE.md` sudah ada di folder kerja, ini pekerjaan yang terputus (batas pemakaian, koneksi, atau user bilang "lanjut"). Baca file itu, bilang "saya lanjutkan dari bagian X", lalu teruskan dari langkah yang belum selesai. Jangan menanyakan ulang pilihan yang sudah tercatat.

Perbarui `build/STATE.md` setiap kali satu langkah selesai:

```
# STATE
langkah selesai: preflight, intake, timing, rencana scene
berikutnya: aset (frames.py klip ugc, cinematic)
proyek: promo kelas AI, VO 86 dtk, jeda +9 dtk
pilihan user: brand dari guideline (accent #c8101e), Poppins, SFX bawaan skill, tanpa musik, CTA komentar "MAU"
catatan: "1.483+ member" harus persis; handle @namauser
```

## 1. Preflight

Folder kerja: kalau user punya folder proyek (mis. satu folder bahan dan satu folder hasil), ikuti strukturnya; satu video = satu folder baru di folder hasil. Kalau tidak, buat folder proyek baru yang bisa ditulisi.

```bash
SK="<folder tempat SKILL.md ini>"
cd "<folder proyek>"
bash "$SK/assets/preflight.sh" build
source build/env.sh          # memberi $SK, $PY, $BUILD, $CHROME_BIN. Ulangi di setiap shell baru.
```

| Verdict | Artinya |
|---|---|
| `READY` | Lanjut normal |
| `READY_NO_ASR` | Pengenal suara tidak bisa dipasang. **Minta file subtitle .srt** (caption otomatis CapCut, ekspor .srt) |
| `BLOCKED` | **Berhenti.** Sampaikan yang kurang dengan bahasa biasa |

Font pack (21 font, 6 preset), ikon Phosphor fill (1.512 ikon), dan 9 SFX bawaan sudah ikut di skill. GSAP dan Playwright dipasang sekali ke `~/.cache/script-to-motion-reel`.

## 2. Intake: semua pertanyaan dalam SATU pesan

Cek dulu apa yang sudah dikirim user. Lalu tanyakan **semua yang kurang dalam satu pesan**, sebagai pilihan bernomor dengan default yang ditandai. User boleh menjawab singkat ("2b, sisanya default") atau "default semua". Kalau ada alat pilihan ganda, boleh dipakai (maks 4 pertanyaan per panggilan). **Jangan menanyakan hal baru di tengah pengerjaan**, kecuali sesuatu yang tidak bisa ditebak.

**Bahan (minta hanya yang belum ada):**
- MP3 VO + transkrip. **Selalu tanyakan file subtitle .srt** (lebih cepat, ejaan pasti benar). Kalau tidak ada keduanya, transkrip dibuat dari suara.
- Folder aset. Konvensi nama: `video-<topik>.mp4`, `grid-*.mp4` (video wall), `logo.png`, `screenrecord-*.mp4`, `profil.png`, `screenshot-*.png`. Kalau folder aset sudah ada, **lihat isinya sendiri** (`clipscan.py` untuk klip, lembar gambar untuk foto) lalu sebutkan aset mana cocok untuk bagian mana. Jangan minta kirim ulang yang sudah ada. Kalau folder berisi banyak video dan scene harus memilih beberapa, tampilkan daftarnya dan tanya.
- Hal spesifik: handle IG/nama/angka (mis. "1.483+ member"), kata CTA persis, badge/label wajib. **Jangan dikarang.**

**Pilihan (selalu ditanyakan, dengan default):**

| # | Pertanyaan | Pilihan | Default |
|---|---|---|---|
| 1 | Warna | dari brand guideline / usulkan dari logo (`palette.py`) / merah-charcoal bawaan | brand guideline kalau ada, kalau tidak dari logo |
| 2 | Font | preset S1-S6 dari font pack (tunjukkan gambar `assets/fonts/preview-stmr.jpg`) / font brand (nama Google Font atau kirim .ttf/.otf) | S1 Poppins Klasik |
| 3 | Sound effect | SFX bawaan skill / SFX dari folder milikmu / sintetis saja / tanpa | bawaan skill (kalau user punya folder SFX, sarankan itu) |
| 4 | Musik | tanpa (tambah sendiri di IG/TikTok, paling aman hak cipta) / dari file milikmu, pelan / sedang | tanpa |
| 5 | Penutup | ajak komentar kata tertentu (sebutkan) / ajak follow / "link di bio" / tanpa | ajak komentar |
| 6 | Pratinjau sebelum render | lihat contact sheet dulu / langsung render | lihat dulu |
| 7 | Ukuran file | di bawah 29 MB (bisa dikirim lewat chat) / kualitas penuh tanpa batas | di bawah 29 MB |

Kalau user tidak menjawab atau bilang "langsung saja": pakai default, tulis asumsinya di awal pesan berikutnya. Setelah dijawab, tulis ringkasan pilihan ke `build/STATE.md`.

## 3. Brand

Tulis `build/brand.json`. Hanya warna inti yang wajib; turunannya (accentHi, tint chip/badge, bayangan, 5 blob latar) dihitung otomatis oleh `assemble.py`, jadi **jangan hard-code warna di tengah scene**: pakai `var(--accent)`, `ACC`, `ACC_HI`, `INK`, `PAPER`.

```json
{"accent": "#c8101e", "bg": "#0e0e11", "ink": "#141414", "paper": "#ffffff", "font": "Poppins", "success": "#16a34a"}
```

- User tanpa guideline: `$PY $SK/assets/palette.py logo.png --write build/brand.json` mengusulkan accent dari logo + latar charcoal berwarna. Tunjukkan ke user, minta persetujuan singkat.
- **Font pack bawaan** (`assets/fonts/`, 21 font OFL, offline): `"font_preset": "jakarta"` (atau nomornya, `"S2"`). Daftar: `$PY $SK/assets/fonts/fontpack.py list stmr`; contoh tampilan semua preset: `assets/fonts/preview-stmr.jpg` (kirim gambar ini ke user saat bertanya font). Preset S5/S6 punya font display untuk angka besar dan kata hantaman.
- Font lain: `"font": "Sora"` (dari font pack kalau ada, kalau tidak diunduh dari npm @fontsource) atau `"font_files": {"700": "aset/font/Brand-Bold.ttf", "800italic": "..."}` untuk file milik user (font berbayar hanya untuk proyek user, jangan dimasukkan ke skill).
- Di kode, font utama selalu `P`. Font display dipakai lewat class `disp` atau `fontFamily:'var(--fd)'` (sama dengan P kalau preset tidak punya display). Anton/Bebas: tulis kata dalam HURUF BESAR.
- Background utama **bukan hitam murni**; gelap berwarna dengan radial gradient + blob melayang (sudah ada di template). Kalau brand terang, balik logikanya: scene "utama" terang (`whiteRise`), scene "kontras" gelap.
- Logo user dipakai apa adanya (jangan digambar ulang). Jangan pernah menggambar ulang logo merek lain; pakai logo asli dari user atau ikon generik.

Format lengkap `brand.json` dan `project.json`: `references/production.md`.

## 4. Timing VO (inti kualitas)

Tujuan: `build/words.json` = `[[detik, "kata"], ...]` di timeline VO **asli**.

**Jalur A, dari subtitle (selalu dicek dulu, paling cepat):**
```bash
$PY $SK/assets/srt2words.py sub.srt build/words.json --report
```

**Jalur B, dari suara (kalau tidak ada subtitle):**
```bash
$PY $SK/assets/wordtime.py build/aset/vo.mp3 build/words.json --lang id
```
Pertama kali mengunduh model sekitar 850 MB (beberapa menit, beri tahu user). Model disimpan di cache, jadi proyek berikutnya tidak mengunduh ulang.

Setelah itu: cocokkan teks dengan transkrip user (transkrip user yang benar; ASR/SRT hanya untuk waktu). Perbaiki salah dengar dengan mengubah **teks** di words.json, **waktunya jangan diubah**. Periksa kata kunci tiap scene (kata yang akan di-highlight).

Tidak ada cara mendengarkan audio. Validasi hanya lewat angka. Jangan mengaku sudah "mendengar".

## 5. Rencana scene + jeda

Sebelum build panjang, kirim **rencana scene** ke user (tabel ringkas: waktu | kalimat VO | visual), pilih dari katalog di `references/scene-catalog.md`. Kalau user bilang "langsung aja", lanjut tanpa menunggu.

VO asli sering terlalu rapat untuk animasi kompleks. Sisipkan jeda hening:
- Setelah kata yang memicu visual besar (klip contoh 2-3 dtk supaya sempat tampil; setelah daftar bonus 2-4 dtk; sebelum CTA 1-2 dtk).
- **Jangan** di tengah frasa yang mengalir (mis. "ada kalanya kita mentok"): terasa janggal. Jeda hanya di batas kalimat/frasa.
- Jeda tubuh scene: 2 dtk setelah kalimat demo/screen record, 0,5-1 dtk antar-poin biasa.

**Jangan menebak posisi jeda.** Cari titik yang benar-benar hening:
```bash
$PY $SK/assets/gaps.py build --from 14 --to 18      # daftar hening + "taruh jeda di ..."
```
Tulis ke `project.json` → `"pauses": [[17.67, 3.0], [24.1, 1.0]]` (detik VO asli, durasi). Halaman (`T()`, `at()`) dan audio (`mix.py`) menyesuaikan sendiri. Revisi jeda = ubah angka ini saja, lalu assemble + render ulang. Ekor setelah kata terakhir: `"tail": 2.0`.

## 6. Aset

```bash
# klip pendukung: cek teks tertanam dulu (caption lama, watermark), lihat lembarnya dengan Read
$PY $SK/assets/clipscan.py build/scan.jpg aset/video-ugc.mp4 aset/video-cinematic.mp4 --every 2
# ekstrak HANYA rentang yang bersih jadi image sequence (tinggi 960 untuk kartu/HP, 480 untuk ubin, 1280 full layar)
$PY $SK/assets/frames.py build --clip ugc:aset/video-ugc.mp4:2:4.5 --clip cine:aset/video-cinematic.mp4:0:5
$PY $SK/assets/frames.py build --wall g:aset/grid --wall-dur 2.8      # video wall: g01..gNN, klip unik
```

- **Emoji 3D** (Microsoft Fluent): cukup tulis `emoji('rocket', 220)` di scene; `assemble.py` mengunduh yang belum ada ke `build/img/`. Nama = nama folder Fluent, huruf kecil, spasi jadi `_` (`face_with_spiral_eyes`, `thumbs_up`, `brick`, `collision`, `wastebasket`, `locked`, `unlocked`, `party_popper`, `racing_car`).
- **Ikon UI**: Phosphor fill sudah bawaan; cukup tulis `icon('check-circle', 36, '#fff')`. assemble.py menulis SVG yang dipakai dan menyarankan nama mirip kalau salah. Ikon lain / logo merek kecil: `bash $SK/assets/fetch_icons.sh brand telegram` (LobeHub), tetap sebagai ikon kecil, bukan meniru layarnya.
- **Gambar user**: salin ke `build/img/`. Periksa pinggiran screenshot (bingkai putih, sudut membulat, tombol di pojok) dan potong bersih dengan `ffmpeg -vf crop=...`. Screenshot kecil ditampilkan kecil.
- Jangan unduh foto orang publik dari web. Foto profil harus dari user.

## 7. Bangun scene

Tulis **hanya** `build/scenes.js`. Kerangka halaman, background hidup, grain, semua helper, dan `seek()` sudah ada di `assets/template.html` (jangan disalin, jangan diubah per proyek). Lalu:

```bash
$PY $SK/assets/assemble.py build                       # -> build/index.html, cetak TOTAL
node $SK/assets/snap.js build/snaps 3.2 9.0 14.5 --url "file://$BUILD/index.html"   # lihat sendiri tiap 2-3 scene
```

**Waktu di scenes.js selalu waktu FINAL.** Ambil dari kata, bukan angka manual:
- `at('UGC')`, `at('private group')`, `at('video', 2)` = waktu final kata/frasa (kemunculan ke-n). Error jelas kalau kata tidak ada.
- `W(12)` = waktu final kata indeks ke-12; `T(17.4)` = detik VO asli → final.
Karena semuanya lewat `T()`, revisi jeda tidak perlu menggeser angka di scene.

**Helper yang tersedia** (detail tanda tangan di `references/production.md`):

| Kelompok | Helper |
|---|---|
| Dasar | `scene(t0,t1)`, `mk()`, `A(parent,x,y,html,cls,css)` (posisi = titik tengah), `stack([el,..], yTengah, gap)` (blok teks rapat), `C(el)`, `icon()`, `emoji()`, class `disp` (font display) |
| Teks | `line(parent,x,y,[[teks,t,style],...],css)` + `wordsIn(el,kind)`, `hlOn(span,t)`, `typeText(el,t,teks)` |
| Gerak | `inA(el,t,kind)` (blur, pop, zoom, slam, right, drop, fade), `outA(el,t,kind)` (blur, up, left, shrink), `shake(t)`, `float(el,amp,ph)`, `perFrame.push(t=>...)` |
| Komponen | `whiteRise(parent,t)`, `count(el,t,dur,sampai)`, `cursorPath()` + `click()`, `vid(parent,'nama',null,t0,t1,css,loop,rate)`, `phone(parent,x,y,w)`, `mergeTo(...)` (A + B = C), `bigArrow(parent,x,y,t,{dir})` |
| Suara | `sfx(t,'jenis',gain)`: click, pop, bubble, whoosh, swish, thud, ding, tick, type, riser, error |

Kalau scenes.js error, render dan QA berhenti dengan pesan `HALAMAN ERROR` beserta barisnya.

## 8. Bahasa gerak (wajib ditiru agar "rasa"-nya sama)

**Tipografi**
- Kalimat biasa: 56-76px, bobot 600, sering *italic*. Kata kunci: bobot 800-900, ukuran 1,3-2x, warna accent / putih di atas pil accent. Angka besar: 360px/900 dengan letter-spacing negatif.
- Teks maksimal 2-3 baris pendek per layar. Satu ide per layar. Pusat sumbu x = 540.
- **Teks yang berkaitan = SATU blok rapat (jangan "social distancing").** Kalimat yang dibaca berurutan, misalnya "Di kelas ini ada" + "100+" + "video dibedah", disusun sebagai satu blok di satu titik tengah dengan `stack()`, bukan disebar ke atas-tengah-bawah layar. Jarak antar-baris di dalam blok 12-36 px (sekitar 0,1-0,3 x tinggi huruf baris yang lebih kecil); angka/kata raksasa diberi `lineHeight:'.9'` supaya kotak hurufnya tidak menambah jarak. Ruang kosong ada di LUAR blok. Jarak antar-blok yang beda ide minimal 2x jarak di dalam blok. Cek di contact sheet: kalau mata harus melompat dari satu baris ke baris berikutnya, rapatkan.
- Teks ditaruh pada zona aman: x 60-1020, y 140-1780. Jangan taruh teks penting di bawah y=1700 (UI platform menutupi).

**Aturan waktu**
- Kata muncul pada `at(kata) - 0,05` (animasi masuk 0,38 dtk selesai tepat setelah kata diucapkan). Kata kunci boleh didahului 0,05-0,1 dtk.
- Setiap kata/elemen masuk dengan `inA`; keluar `outA` 0,15-0,25 dtk sebelum scene berikut. Scene saling overlap 0,05-0,15 dtk agar tidak ada frame kosong.
- Efek yang tidak boleh terlihat sebelum waktunya (flash, ring, cincin CTA): `tl.set(el,{opacity:0},0)` lalu `tl.fromTo(...,{immediateRender:false})` atau `tl.to`.
- Hold: setelah visual besar (demo klip, daftar bonus) beri jeda 2-3 dtk lewat `pauses`, bukan dengan memperlambat animasi.
- Easing: `power3.out` masuk, `power2.in` keluar, `back.out(1.5-2.5)` untuk pop, `power4.in` untuk slam, `power3.inOut` untuk transisi besar.

**SFX per aksi**: pop saat objek muncul, bubble untuk chip/daftar yang muncul beruntun (selang-seling dengan pop supaya tidak monoton), whoosh saat panel/transisi, swish saat teks menyapu, thud saat slam/impak (+ `shake`), ding saat sukses, error saat hal negatif/gagal (label murahan masuk tong sampah, tanda silang), click saat klik kursor, type saat mengetik, tick saat counter, riser sebelum reveal besar (opsional).

**Pergantian tema**: selang-seling scene gelap (bg hidup) dan scene terang (`whiteRise`, teks `INK`, aksen accent) setiap 1-3 kalimat agar ritme tidak monoton. Semua scene terang diawali `whiteRise` dan diakhiri `outA` semua elemen.

**Gerak halus tambahan**: elemen mengambang (`float(el,amp,phase)`), ikon berputar pelan lewat `perFrame`, kartu foto memakai Ken Burns (`scale 1 -> 1.08` selama scene), glow radial di belakang kartu penting.

**Hook 5 detik pertama** wajib dipikirkan: emoji ekspresif + kalimat hook per kata dengan 1-2 kata kunci di pil, atau satu angka/benda yang langsung menjelaskan masalah.

## 9. SFX dan audio

`mix.py` (dipanggil otomatis oleh render_all) merakit: VO (level bicara diseragamkan) + jeda + SFX dari `sfx()` di halaman + musik (opsional), lalu dinormalkan ke **-14 LUFS** (standar IG/TikTok/Shorts).

Sumber tiap jenis SFX, yang pertama ada dipakai:
1. `project.json` → `audio.sfx_files` (pemetaan manual)
2. `project.json` → `audio.sfx_dir` (folder SFX user, dipetakan dari nama file: whoosh/transition, swipe/swish, impact/boom/punch/thud, riser, notif/ding, click, pop, bubble, typing, tick, error/wrong)
3. **SFX bawaan skill** (`assets/sfx/`, 9 file): click, pop, bubble (bubble-pop), whoosh (puncaknya diletakkan tepat di waktu aksi), swish (swipe), thud (punch), ding (notification), error, type (typing; event ketik yang rapat digabung jadi satu potongan suara ketik), tick (dari click 10x)
4. Sintetis (riser, dan semua jenis kalau `audio.sfx_source: "synth"`)

Cek sumber yang akan dipakai: `$PY $SK/assets/mix.py --list build`. Level SFX menyesuaikan level VO secara otomatis; kalau log berkata SFX terlalu dekat dengan VO, turunkan `audio.sfx_gain` (mis. 0.7).

**Musik: default tanpa musik.** Hanya kalau diminta: `audio.music` (file user) + `music_level` pelan/sedang; otomatis diulang, fade in 1 dtk / out 3 dtk, dan mengecil saat VO bicara.

## 10. Gerbang: contact sheet

Render itu lama. Sebelum render, kirim satu contact sheet dan tunggu persetujuan (kecuali user memilih "langsung render").

```bash
node $SK/assets/sheet.js build/sheet.jpg 1.2,4.5,8.0,12.4,18.0,24.0 5 "file://$BUILD/index.html"
```

- Satu frame per scene, di detik saat scene sudah tampil penuh. Maks 5-6 kolom. **Lihat sendiri dengan Read sebelum dikirim.**
- Untuk scene yang intinya gerakan (counter, carousel, A + B = C), tambah strip 3 frame: awal, tengah, akhir.
- Di pesan yang sama: daftar scene (detik, apa yang muncul), aset pengganti yang kamu buat sendiri, kata yang meragukan, perkiraan lama render.
- Sampaikan batasnya: gambar diam tidak menunjukkan gerakan dan suara.

## 11. Render

```bash
$PY $SK/assets/render_all.py build --max-minutes 8            # tambah --max-mb 0 kalau user pilih kualitas penuh
```

Satu perintah: audio, render paralel per potongan, sambung, encode final (di bawah 29 MB kecuali `--max-mb 0`). Kalau keluar `BELUM SELESAI`, **jalankan perintah yang sama lagi**; potongan yang sudah jadi tidak diulang. Kalau halaman berubah, potongan lama otomatis dibuang. Hasil: `build/out/Reel_V<N>.mp4`.

Perkiraan di Mac 10 inti: sekitar 6-7 detik proses per detik video (87 dtk ≈ 9-10 menit). Beri tahu user sebelum mulai; jalankan di background untuk video >60 dtk.

## 12. QA wajib sebelum kirim (jangan lewati)

```bash
node $SK/assets/qa.js "file://$BUILD/index.html"
for t in 2 10 20 30; do ffmpeg -nostdin -v error -y -ss $t -i build/out/Reel_V1.mp4 -frames:v 1 -vf scale=360:-2 build/qa_$t.jpg; done
```

qa.js memeriksa: safe zone teks (x 60-1020, y 140-1700), teks terpotong oleh induknya, kata telat (setiap kata dari `line()` harus tampil 0,45 dtk setelah waktunya), frame kosong (sampel tiap 0,25 dtk), dan error halaman. Temuan yang hanya muncul 1-2 kali saat animasi masuk/keluar masih wajar; elemen dekoratif yang sengaja melewati tepi diberi `el.dataset.qaSkip=''`.

Lalu **lihat sendiri frame dari MP4 hasil** (gabungkan jadi satu lembar, baca dengan Read). Daftar periksa:
1. Tidak ada elemen keluar zona aman, tidak ada teks terpotong atau saling menempel.
1b. Teks yang berkaitan tampil sebagai satu blok rapat (tidak berjauhan).
2. Tidak ada frame kosong, tidak ada elemen yang muncul sebelum waktunya.
3. Sinkron kata: kata kunci tampil tepat saat diucapkan.
4. Audio: panjang sama dengan video, tidak clipping, SFX tidak menutupi VO (render_all dan mix.py sudah mengecek).
5. **Nama/angka/teks user** (handle IG, "1.483+", kata CTA) sama persis dengan input.
6. Tidak ada teks footage latar (watermark, caption lama) yang terbaca, tidak ada placeholder tertinggal.
7. Perbaiki semua temuan lalu render ulang; jangan kirim yang masih ada cacat.

## 13. Katalog scene

Resep lengkap (pemicu kata → visual) ada di **`references/scene-catalog.md`**. Pakai sebagai pustaka; pilih dan gabungkan sesuai script:
hook + emoji ekspresif · kartu video → background · judul mask-reveal · counter + video wall · carousel kategori · mockup HP · tong sampah · gembok · screen record chat · metafora tabrakan · profil sosial · bonus tools · kartu mini-app · pertanyaan penutup · CTA minimalis · **A + B = C** (`mergeTo`) · **panah ajakan** (`bigArrow`).

## 14. Kesalahan yang pernah terjadi (jangan ulangi)

- Mengukur posisi target kursor saat kartu masih ter-translate → kursor keluar layar. Hardcode koordinat target setelah dicek lewat snapshot.
- Scene terang mulai terlalu awal / flash putih muncul sebelum waktunya → `tl.set` untuk start, mulai scene tepat di `at(kata_pemicu)`.
- Cincin CTA tampil di awal → `tl.set(opacity:0)` dulu.
- Teks chip terpotong dan kartu meluber → perkecil font/padding, persingkat label; qa.js menangkapnya.
- Foto profil miring/tertimpa gelembung → crop ulang di tengah.
- Jeda di tengah frasa mengalir terasa aneh → jeda hanya di titik hening dari `gaps.py`.
- Menulis waktu scene sebagai angka mentah → revisi jeda menggeser semuanya. Selalu `at()` / `T()`.
- Klip dengan caption lama/watermark ikut tampil → `clipscan.py` dulu, ekstrak rentang bersih saja.
- `<video>` tidak deterministik saat render per frame → image sequence (`frames.py`).
- ffmpeg di dalam `while read` memakan stdin → `-nostdin`.
- File >30 MB gagal dikirim lewat chat → render_all menjaga di bawah 29 MB.

## 15. Alur revisi

User biasanya memberi revisi bernomor, kadang dengan screenshot.

1. Jawab **per nomor**: selesai / sebagian / tidak disarankan (dengan alasan jujur).
2. Sebelum mengubah, simpan versi lama: salin `scenes.js`, `project.json`, `brand.json`, `words.json` ke `build/versi/V<N>/`.
3. Ubah di sumbernya: scene → `scenes.js`; jeda/ekor/audio → `project.json`; warna/font → `brand.json`; teks kata → `words.json` (waktu jangan diubah).
4. Kalau konsep visual berubah, ulangi gerbang contact sheet.
5. `assemble.py` → `render_all.py` (otomatis jadi `Reel_V<N+1>.mp4`) → QA pada scene yang berubah plus 2 scene tetangga.
6. Kirim file baru + ringkasan 3-5 baris per nomor. Jangan menceritakan langkah teknis.

## 16. Batasan (jujur ke user)

- Tidak bisa mendengar audio; sinkron dan level hanya diverifikasi dengan angka dan visual. Minta user mendengarkan sekali, terutama bagian yang diberi jeda.
- Contact sheet tidak menunjukkan gerakan dan timing.
- Adegan metafora yang unik untuk satu script tetap dibuat per proyek (sekitar 30% pekerjaan). Komponen umum (bg, teks kinetic, kartu video, counter, daftar, CTA, SFX, pipeline) dipakai ulang (sekitar 70%).
- Resolusi aset user menentukan ketajaman; screenshot kecil ditampilkan kecil.
- Transkrip dari suara bisa salah pada nama dan istilah asing.
- Pekerjaan bisa terhenti karena batas pemakaian; setelah reset, user cukup mengetik "lanjut".

## 17. Penutup tiap pengerjaan

Kirim **satu file** video (`Reel_V<N>.mp4`), lalu 3-5 baris: durasi, apa yang dibuat, asumsi yang diambil (aset pengganti, warna dari logo, teks contoh), pengingat "tolong dengarkan audionya sekali, saya tidak bisa mendengar", dan 1 langkah lanjutan yang nyata. Gaya bahasa: Indonesia sederhana, langsung ke inti, tanpa basa-basi.

---

## Berkas pendukung

| Berkas | Isi |
|---|---|
| `references/scene-catalog.md` | 17 resep scene + contoh kode helper baru |
| `references/production.md` | Format brand.json / project.json, susunan folder build, tanda tangan helper, masalah umum |
| `assets/preflight.sh` | Cek dan siapkan mesin, beri verdict |
| `assets/srt2words.py` | Subtitle .srt/.vtt → waktu per kata |
| `assets/wordtime.py` | Waktu per kata dari suara (sherpa-onnx, dipasang saat dibutuhkan) |
| `assets/gaps.py` | Cari titik hening untuk `pauses` |
| `assets/palette.py` | Usulan brand.json dari logo |
| `assets/clipscan.py` | Lembar sampel klip untuk memilih rentang tanpa teks tertanam |
| `assets/frames.py` | Klip → image sequence + `clips.json`; video wall |
| `assets/fetch_emoji.py` | Emoji 3D Fluent (dipanggil otomatis oleh assemble) |
| `assets/fetch_icons.sh`, `iconify2svg.js` | Ikon tambahan dari npm (bobot/set lain, logo merek kecil) |
| `assets/template.html` | Kerangka halaman, background hidup, semua helper |
| `assets/assemble.py` | Rakit template + brand + project + words + scenes → index.html |
| `assets/mix.py` | Audio final: VO, jeda, SFX (user / bawaan / sintetis), musik + ducking, -14 LUFS |
| `assets/render_all.py`, `render.js`, `_chrome.js` | Render satu perintah, paralel, bisa dilanjut |
| `assets/qa.js`, `sheet.js`, `snap.js` | Pemeriksa otomatis, contact sheet, snapshot |
| `assets/sfx/` | 9 SFX bawaan: click, pop, bubble-pop, whoosh, swipe, punch, notification, typing, error |
| `assets/fonts/` | Font pack: 21 font OFL, `fontpack.py` (preset S1-S6), `preview-stmr.jpg`, lisensi |
| `assets/vendor/` | Ikon Phosphor fill (MIT) |
