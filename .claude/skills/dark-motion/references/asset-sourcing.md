# Asset Sourcing

Dari mana aset diambil, dan apa yang tidak boleh diambil.

## Urutan mencari aset

1. **Aset dari user.** Selalu didahulukan. Simpan di `build/aset/`.
2. **Potong dari footage user sendiri.** Wajah, tangan, latar, detail dari close-up, versi blur (`bgBlur`). Paling menyatu dan bebas masalah lisensi.
3. **Bangun dengan kode.** Grafik, bar, bingkai, mockup HP, rekonstruksi UI, kartu, gelombang suara.
4. **Berkas bawaan skill** (lihat di bawah): ikon garis, font.
5. **Ambil dari internet** hanya untuk yang memang milik publik dan hanya kalau internet sesi terbuka: logo resmi produk, ikon tambahan.
6. **Kotak berlabel** sebagai pilihan terakhir, dan selalu dilaporkan ke user sebagai placeholder.

Kalau sebuah aset tidak ada di empat sumber pertama, hampir selalu jawabannya membangunnya dengan kode, bukan mencari lebih jauh.

## Berkas bawaan (tidak butuh internet)

| Folder | Isi |
|---|---|
| `assets/vendor/motion.js` | Mesin animasi |
| `assets/vendor/fonts/` | Inter, Playfair Display italic, JetBrains Mono (latin + latin-ext) |
| `assets/vendor/icons.json` | ±200 ikon garis Phosphor, masing-masing juga versi `-fill`. Termasuk ikon platform (`instagram-logo`, `tiktok-logo`, `youtube-logo`, `whatsapp-logo`, ...) |
| `assets/vendor/models/` | Model deteksi wajah (YuNet, Haar) |

Ikon dipakai lewat `icon('nama', ukuran, warna)`. Cari nama ikon dengan `$PY $SK/assets/assemble.py --icons <kata>` (tanpa kata = semua). Ikon dari `build/icon/` (kalau ada) menang atas ikon bawaan dengan nama yang sama.

## Internet: cek, jangan diasumsikan

Akses internet berbeda tiap akun dan pengaturan. Preflight sudah mencetak status npm, PyPI, dan GitHub. Ikuti hasilnya. Jangan mengulang permintaan yang sudah ditolak, dan jangan melaporkan penolakan sebagai "server sedang down".

Kalau npm terbuka, ikon dan logo tambahan bisa diambil:

```bash
bash $SK/assets/fetch_icons.sh phosphor regular rocket-launch    # ikon garis lain
bash $SK/assets/fetch_icons.sh iconify  lucide sparkles           # set Iconify
bash $SK/assets/fetch_icons.sh brand    claude-color openai        # logo produk AI berwarna
bash $SK/assets/fetch_icons.sh simple   notion figma               # logo merek umum, monokrom
```

Hasilnya masuk `build/icon/` dan otomatis ikut di halaman.

## Logo produk

1. `simple-icons` (merek umum) atau `@lobehub/icons-static-svg` (produk AI) lewat fetch_icons.sh.
2. Ikon resmi dari situs produknya, kalau internet terbuka untuk situs itu.
3. **Jangan digambar ulang.** Kalau tidak bisa diambil, tulis nama produknya dalam huruf mono, dan sebutkan ke user.

## Foto dan video pendukung

- **Foto orang tidak diunduh dari web.** Semua foto orang dari user atau dipotong dari footage user.
- Latar, tekstur, dan objek: bangun dengan kode atau pakai footage user yang diblur. Kalau user ingin foto stok, minta ia mengirimkannya.
- Foto user yang kecil di-upscale dengan `lanczos` + `unsharp` sebelum dipakai besar.
- Klip pendukung dari user dijadikan image sequence: `frames.py build --clip nama:file.mp4[:mulai:durasi]`.

## Format yang bisa diproses

| Format | Catatan |
|---|---|
| SVG | Dipakai sebagai mask CSS supaya bisa diwarnai |
| PNG, JPG, WebP | Langsung, atau diolah lewat ffmpeg/OpenCV |
| PNG/WebP beralpha | Untuk potongan orang dan objek 3D |
| GIF | Dipecah per frame seperti video |
| Video | Selalu jadi image sequence, bukan tag `<video>` |
| Font TTF/OTF/WOFF2 | Font brand dari user (`project.json` → `font`) |
| MP3/WAV/M4A | Musik dari user (`project.json` → `audio.music`) |

## Yang tidak diambil, walaupun bisa

- **Foto orang publik.** Tidak diunduh dan tidak dipasang.
- **Logo, karakter, atau maskot merek lain tidak digambar ulang.** Logo resmi boleh dipakai kecil untuk menyebut sebuah produk. Logo milik user dipakai sebagaimana dikirim.
- **UI produk orang lain tidak ditiru persis.** Rekonstruksi UI dibuat dengan tata letak netral, hanya untuk memperlihatkan alat yang user pakai. Jangan membuat tampilan yang bisa disangka milik perusahaan itu.
- **Musik dari internet.** Tidak diambil. Musik hanya dari file user, atau disarankan ditambahkan di aplikasi Instagram/TikTok.

Kalau aset dari user berisiko (seragam instansi, senjata, logo program pemerintah, wajah orang lain), **sebutkan sekali** risikonya untuk pembatasan platform, beri saran, lalu ikuti keputusan user.

## Lisensi

| Aset | Lisensi |
|---|---|
| Mesin animasi `motion.js` | Bagian dari skill ini |
| Inter, Playfair Display, JetBrains Mono | SIL Open Font License 1.1 (boleh dibundel, tidak boleh dijual sebagai font tersendiri) |
| Phosphor Icons | MIT |
| YuNet (OpenCV Zoo) | MIT |
| `simple-icons` | CC0 untuk berkasnya; **merek dagangnya tetap milik pemiliknya** |

Logo boleh dipakai untuk merujuk sebuah produk, tidak untuk menyiratkan dukungan atau kerja sama. Aset berbayar dari user dianggap sudah ia miliki haknya; jangan mengambil tambahan sendiri.
