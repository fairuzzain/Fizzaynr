# Style System

Semua angka di sini default. Jawaban user di pertanyaan selera selalu menang.

## Warna

```json
{ "ink": "#ffffff", "bg": "#0e0e11", "bgLift": "#26262e", "bgDeep": "#08080a" }
```

Dua warna aksen, `C1` dan `C2`, dipilih per proyek di `project.json` (`c1`, `c2`) dan tersedia sebagai `C1`/`C2` di JS dan `var(--c1)`/`var(--c2)` di CSS. **Jangan hardcode warna aksen di scene.**

### Memilih aksen

- **User memberi warna brand** → pakai, tapi cek kontrasnya di latar gelap. Warna brand yang gelap (navy, maroon) dicerahkan untuk teks, dan versi aslinya dipakai untuk blok atau garis.
- **"Dari video"** → jalankan `palette.py`. Usulannya sudah dicerahkan dan menghindari merah. Kalau hasilnya terasa tidak cocok dengan suasana video, boleh disesuaikan.
- **Netral** → `C1 = #86EF5A` (hijau limau), `C2 = #3FA9FF` (biru).

Yang menentukan warna adalah **keterbacaan di latar tempat teks berdiri**, bukan kecocokan dengan satu objek di footage. Warna asli dari footage hampir selalu terlalu gelap untuk dipakai sebagai teks.

### Arti warna

| Warna | Dipakai untuk |
|---|---|
| `C1` | Positif, berhasil, pilihan yang benar, centang |
| `C2` | Netral-teknis, informasi, label, kategori |
| Putih | Kata kunci tanpa muatan |
| Merah `#ff2f2f` | **Hanya** kalau user minta, atau isinya memang soal kerugian/larangan. Merah yang ditabur di banyak tempat membuat video terlihat murah |

Tulisan di atas blok warna (`.k`) otomatis gelap kalau aksennya terang, dan putih kalau aksennya gelap.

## Latar scene

**Tidak pernah warna rata.** Tiga helper:

| Helper | Isi | Kapan |
|---|---|---|
| `bgBlur(t0,t1,{over})` | Footage utama yang sama, diblur, selalu sinkron | Paling sering. Murah, menyatu, tidak ada masalah lisensi |
| `bgPhoto(t0,t1,src,{over,from,to})` | Foto dengan zoom pelan 1,0 → 1,08 | Foto produk/lokasi dari user |
| `bgVideo(t0,t1,dir,n,{over,blur})` | Klip pendukung (image sequence) | Klip dari user |

Overlay 80-90% (`over: .8-.9`). Di bawah 80% teks mulai sulit dibaca; di atas 90% latarnya tidak ada gunanya.

## Huruf

Tiga keluarga bawaan (sudah ada di skill, tidak perlu internet):
- **Inter** untuk teks biasa, UI, kartu. Bobot 400-900.
- **Playfair Display italic** untuk kata kunci dan judul di mode serif. Bobot 700/800/900.
- **JetBrains Mono** untuk label kecil, lower third, chip, timecode.

Mode kata kunci diatur di `project.json` → `font.mode`:

| Mode | Kata kunci | Cocok untuk |
|---|---|---|
| `serif` | Playfair Display italic 800 | Elegan, sinematik, personal branding (bukan default; default Dark Motion = `sans`) |
| `sans` | Inter 900, rapat | Modern, tegas, bisnis, teknologi |
| `custom` | Font dari user (`font.file`, mis. `aset/brand.ttf`) | Brand dengan font sendiri. `font.body: "custom"` kalau teks biasa juga pakai font itu |

Dalam scene, pakai kelas yang sudah ada supaya mode font berlaku otomatis. Jangan menulis `font-family` langsung kecuali untuk mono (`JB`). Nama keluarga di halaman: `I` (Inter), `PF` (Playfair), `JB` (JetBrains Mono); **`Inter` tidak dikenal** dan jatuh ke serif. Untuk teks biasa di scene: `fontFamily:'var(--bf),sans-serif'`.

## Kelas teks caption

| Kelas | Ukuran default | Dipakai |
|---|---|---|
| `n` | 52px, teks biasa | Kata biasa |
| `s` | 98px, kata kunci putih | Penekanan netral |
| `k1` | 100px, warna `C1` | Kata kunci positif |
| `k2` | 100px, warna `C2` | Kata kunci info/teknis |
| `k` / `k alt` | 92px, **tulisan di atas blok `C1` / `C2`** | Kata kunci di latar terang (autocap memilih otomatis) |
| `X` | 190px | Kata hantaman, maksimal dua per video |
| `mono` | (atur sendiri) | Label, chip |

`ab` adalah kelas posisi untuk helper `A()` dan `P()`. **Bukan kelas teks**, jangan dipakai sebagai gaya.

## Tiga alat kontras

Dipilih menurut latar di belakang teks, bukan selera. autocap memilihnya otomatis untuk caption dengan mengukur kecerahan pita tempat caption berdiri. Scene buatan sendiri mengikuti tabel ini.

| Latar | Alat |
|---|---|
| Gelap (overlay 80-90%, malam, bayangan) | Glow berlapis + bayangan gelap (kalau glow dipilih user), atau bayangan saja |
| Sedang | Gradien gelap memudar di belakang teks, tanpa glow |
| Terang atau ramai (langit, dinding putih, lantai terang) | Gradien gelap memudar + **kata kunci di blok warna solid** + teks putih tebal |

### Gradien gelap memudar

Bukan kotak hitam: hitam di tepi layar lalu memudar bertahap sampai transparan, dengan tujuh titik berhenti. Gradien dua titik (`black → transparent`) membentuk pita yang terlihat jelas di layar HP.

```js
scrimT(t0,t1)          // untuk teks di atas
scrimB(t0,t1,yTeks)    // untuk teks di bawah
scrimM(t0,t1,yTeks)    // pita di tengah (caption di garis tengah dua panel)
```

Gradien muncul 0,18 detik sebelum teks dan hilang 0,14 detik sebelum teks hilang.

### Blok warna

Pengganti glow yang jauh lebih kuat di footage terang. Blok yang bersebelahan diberi sudut membulat hanya di sisi luar (`kk(kata, t, ukuran, posisi)`: posisi 1 = kiri, 2 = kanan, 3 = sendiri), dan baris berisi blok diberi jarak 10-16px supaya tidak saling menempel.

## Komposisi teks

1. **Zig-zag** untuk blok berukuran campur (otomatis di `cap()`). Baris berisi blok warna tidak digeser.
2. **Rapatkan jarak antar baris** yang berisi teks besar (otomatis).
3. **Strut tak terlihat** di tiap baris supaya tinggi baris tidak melompat saat kata muncul satu per satu (otomatis).
4. **Satu ide per layar.** Maksimal 3 baris pendek.

## Posisi dan safe zone

```
Area aman : x 125 - 955,  y 150 - 1560
```

Batas bawah 1560, bukan 1720: di bawahnya ada caption dan tombol aplikasi. Posisi baku: caption atas `YT = 300`, caption bawah `YC = 1400`, garis tengah dua panel `960`. autocap memilih di antara ketiganya supaya tidak menutupi wajah. Verifikasi dengan `qa.js`, jangan dikira-kira.

## Mockup HP

`phone(parent)` membuat HP modern berlapis (bezel gradien, rim, layar, dynamic island, tombol samping, kilap). Rasio 270x540 (1:2). Video 9:16 di dalamnya terpotong sekitar 7% per sisi; sebutkan ke user kalau isinya penting. Dua HP sejajar muat dengan skala 1,2 di x 332 dan 748; satu HP muat sampai skala 1,35-1,5.

## Easing dan durasi

| Gerakan | Easing | Durasi |
|---|---|---|
| Kata biasa masuk | `power2.out`, y 14 → 0, blur 10 → 0 | 0,22 |
| Kata besar masuk | `power3.out`, scale 1,35 → 1, blur 16 → 0 | 0,30 |
| Kata hantaman | `power3.out`, scale 1,5 → 1, brightness 2,6 → 1 | 0,34 |
| Kartu/panel masuk | `power3.out` | 0,45-0,80 |
| Keluar | `power2.in`, blur naik | 0,18-0,25 |
| Pop kecil | `back.out(1.6-2.2)` | 0,30-0,35 |
| Transisi besar | `power3.inOut` | 0,50-0,75 |

Kata masuk 0,04 detik sebelum diucapkan supaya animasinya selesai tepat saat kata terdengar (otomatis di `cap()`).

## Grain

Grain membuat file jauh lebih besar (yang bergerak sekitar 4x, yang diam sekitar 2x), padahal hasil akhir harus di bawah 30 MB. `project.json` → `grain: "auto"` (default) memakai grain diam hanya untuk video sampai 30 detik, dan mematikannya untuk yang lebih panjang. Tekstur film untuk hook lebih baik dibakar ke beberapa detik pertama saja lewat `bake.py`.

## Logo, gambar, dan panah

- **Logo user:** dibangun ulang (simbol di-blend `screen` + teks diketik ulang dengan gradien warna logo), tidak pernah ditempel utuh di masker lingkaran/kotak. Resep O1.
- **Gambar dari user:** pinggirannya diperiksa dulu. Bingkai putih, sudut membulat, dan ikon tombol dari screenshot aplikasi dipotong sebelum dipakai.
- **Panah ajakan:** panah lurus datar solid dua warna (`bigArrow`), tebal dan jelas. Ini satu-satunya panah tebal yang boleh; panah tebal melengkung tetap dilarang.
- **Klip contoh video:** di dalam mockup HP (`phoneTrio`), bukan potongan full layar yang menutupi wajah.

## Dilarang

Emoji 3D, ikon bulat warna-warni, stiker, maskot, confetti, bintang, mata, tangan kartun, panah tebal melengkung (panah lurus solid untuk CTA boleh, lihat di atas), logo utuh di dalam piringan/kotak, bayangan ganda tebal, gradien pelangi, font dekoratif, teks berkedip, elemen berputar penuh tanpa alasan, bounce lebih dari satu pantulan, dan layar warna rata sebagai latar scene.
