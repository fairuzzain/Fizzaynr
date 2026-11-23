# Asset Sourcing

Dari mana mengambil aset di sandbox, dan apa yang tidak boleh diambil.

## Aturan jaringan

Sandbox ini **hanya bisa menjangkau GitHub dan package registry**. Host lain ditolak di level proxy (`connect_rejected`), dan tidak ada jalan memutar: ganti `curl` jadi `wget`, `requests`, atau `fetch` hasilnya sama.

Hasil tes langsung:

| Sumber | Status |
|---|---|
| `raw.githubusercontent.com` | **Bisa** |
| GitHub Releases | **Bisa** (lewat redirect 302) |
| `registry.npmjs.org` (paket apa pun) | **Bisa**, bypass proxy |
| `pypi.org`, `files.pythonhosted.org` | **Bisa**, bypass proxy |
| `jsr.io`, `crates.io`, `proxy.golang.org` | **Bisa**, bypass proxy |
| jsDelivr, unpkg, cdnjs | Ditolak |
| `fonts.gstatic.com` | Ditolak |
| `api.iconify.design` | Ditolak |
| Unsplash, Wikimedia, LottieFiles, Giphy | Ditolak |

**Daftar ini bisa berbeda tiap sesi.** User bisa melebarkannya di claude.ai Settings > Capabilities. Jadi: jangan hafalkan, **tes dulu** dengan `assets/check_net.sh`, lalu ikuti hasilnya. Jangan pernah mengulang request yang sudah ditolak, dan jangan laporkan penolakan proxy sebagai "server sedang down".

## Trik utama: CDN diblokir, paketnya ada di npm

Hampir semua aset yang biasa diambil dari CDN juga dipublikasikan ke npm. Sudah diuji di sandbox ini:

| Paket npm | Isi | Ukuran |
|---|---|---|
| `@phosphor-icons/core` | Ikon garis dan fill, 6 bobot. **Pilihan utama skill ini** | 40 MB |
| `@iconify-json/<set>` | Satu set Iconify dalam satu JSON. `mdi` 7.638 ikon, `lucide` 2.100 ikon. Iconify punya ratusan set | 0.7-4 MB per set |
| `simple-icons` | Logo resmi 3.467 merek, SVG monokrom | 26 MB |
| `@lobehub/icons-static-svg` | 994 logo produk AI (Claude, Google, OpenAI, Gemini, dan lain-lain) | 5 MB |
| `@fontsource/<font>` | Font Google dalam woff2, pengganti `fonts.gstatic` | kecil |
| `lottie-web` | Player animasi Lottie | 26 MB |
| `gsap` | Mesin animasi utama | kecil |

Pakai `assets/fetch_icons.sh` supaya tidak perlu ingat strukturnya.

```bash
bash assets/fetch_icons.sh phosphor regular arrow-right check play-circle
bash assets/fetch_icons.sh iconify lucide sparkles wand-2 clapperboard
bash assets/fetch_icons.sh brand google-color claude-color openai
bash assets/fetch_icons.sh simple instagram tiktok youtube
```

Semua hasil masuk ke `build/icon/` sebagai SVG siap dipakai `icon('nama', 24, '#fff')`.

### Catatan `@iconify-json`

Paket ini **bukan kumpulan file SVG**, melainkan satu `icons.json` berisi `body` dan ukuran. Harus dikonversi dulu:

```bash
node assets/iconify2svg.js lucide build/icon sparkles wand-2
```

Tanpa argumen nama, seluruh set dikonversi. Jangan lakukan itu untuk `mdi` (7.638 file).

## Format yang bisa diproses

| Format | Catatan |
|---|---|
| SVG | Dipakai sebagai CSS mask supaya bisa diwarnai. Ikon garis maupun fill sama-sama bisa |
| PNG, JPG, WebP | Lewat Pillow dan ffmpeg |
| GIF | Bisa dibaca, dipecah per frame, dan dibuat lewat ffmpeg. Perlakukan seperti klip video: ubah jadi image sequence |
| Lottie (JSON) | Bisa, dan **deterministik** kalau dipakai dengan benar. Lihat di bawah |
| Video | Selalu jadi image sequence, jangan tag `<video>` |

### Lottie

`assets/lottie.js` membungkus `lottie-web` supaya cocok dengan pipeline render per frame. Kuncinya `goToAndStop(frame, true)`, bukan autoplay. Sudah diverifikasi: frame yang sama menghasilkan piksel yang identik, jadi aman untuk render.

**Tapi untuk skill ini Lottie jarang dipakai.** Alasannya:

1. Hampir semua Lottie siap pakai bergaya kartun, dan itu melanggar aturan nomor 1 skill ini.
2. Seluruh halaman sudah memakai GSAP, yang lebih mudah dikunci ke waktu kata.
3. Lottie membawa SVG dengan palet sendiri yang sering bentrok dengan token warna.

Pakai Lottie hanya kalau user memberi file Lottie miliknya sendiri, atau untuk gerakan abstrak seperti garis, partikel halus, dan pulse. Untuk selain itu, bangun dengan GSAP.

## Yang tidak diambil, walaupun bisa

Ini batas kerja, bukan batas jaringan.

- **Foto orang publik.** Tidak diunduh dan tidak dipasang di video, baik sebagai salinan maupun sebagai tautan. Foto orang harus dari user.
- **Logo, karakter, atau maskot merek lain tidak digambar ulang.** Logo resmi dari `simple-icons` atau `@lobehub/icons-static-svg` boleh dipakai apa adanya untuk menyebut sebuah produk, dalam ukuran kecil. Logo milik user dipakai sebagaimana dikirim, jangan dimodifikasi.
- **UI produk orang lain tidak ditiru sebagai tiruan persis.** Rekonstruksi UI (resep nomor 8) dibuat ketika user sendiri yang memintanya untuk memperlihatkan alat yang ia pakai, memakai tangkapan layar dan media milik user, dengan tata letak yang netral. Jangan membuat halaman yang bisa disangka milik perusahaan itu.
- **Halaman atau dokumen yang menyamar jadi milik pihak lain.** Tidak dibuat dalam bentuk apa pun.

## Lisensi

Untuk kerja klien, pakai yang jelas bebas:

| Aset | Lisensi |
|---|---|
| Phosphor Icons | MIT |
| Lucide | ISC |
| Material Design Icons (`mdi`) | Apache 2.0 |
| Font di `@fontsource` | kebanyakan OFL, cek per font |
| GSAP core | lisensi standar GreenSock, bebas untuk kebanyakan pemakaian |
| `simple-icons` | CC0 untuk berkasnya, **tetapi merek dagangnya milik pemiliknya**. Boleh untuk merujuk produk, tidak boleh untuk menyiratkan dukungan atau kerja sama |

Stok foto berbayar tetap butuh lisensi walaupun file-nya bisa diunduh. Musik juga. Kalau user memberi aset berbayar, anggap ia sudah punya haknya, dan jangan mengambil tambahan sendiri.

## Urutan mencari aset

1. **Aset dari user.** Selalu didahulukan. Logo, foto, klip, tangkapan layar.
2. **Bangun dengan kode.** Grafik garis, bar, bingkai, mockup HP, rekonstruksi UI. Ini yang membuat gaya editorial terlihat mahal, dan tidak ada masalah lisensi.
3. **Ikon dari npm.** Phosphor dulu, baru set lain lewat Iconify.
4. **Logo merek dari npm**, hanya ketika sebuah produk memang disebut dalam naskah.
5. **Lottie**, hanya untuk kasus yang disebut di atas.

Kalau sebuah aset tidak ada di empat sumber pertama, hampir selalu jawabannya adalah membangunnya dengan kode, bukan mencari lebih jauh.
