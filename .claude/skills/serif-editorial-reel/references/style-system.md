# Style System

## Token warna

```json
{
  "ink":    "#ffffff",
  "red":    "#ff2f2f",
  "redDeep":"#c80c17",
  "green":  "#36f281",
  "bg":     "#0e0e11",
  "bgLift": "#26262e",
  "bgDeep": "#08080a"
}
```

**Arti warna, jangan dibalik:**

| Warna | Dipakai untuk |
|---|---|
| Merah `#ff2f2f` | Negatif, mahal, salah, larangan, peringatan, angka kerugian |
| Hijau `#36f281` | Positif, berhasil, murah, aman, hemat, centang, notifikasi sukses |
| Putih | Netral, kata kunci yang ditonjolkan tapi tidak bermuatan |

Latar utama bukan hitam murni. Untuk scene di atas video, latar adalah videonya sendiri yang di-grade gelap. Untuk scene tambahan tanpa video, pakai radial gradient `bgLift -> bg -> bgDeep` plus dua blob radial (satu aksen transparan 0.22-0.30, satu abu 0.35), grid 90px opacity 0.035 dengan mask radial, vignette, dan grain.

## Font

- **Inter** untuk caption biasa, UI, kartu. Bobot 400/500/600/700/800.
- **Playfair Display italic** untuk kata kunci dan judul. Bobot 700/800/900.
- **JetBrains Mono** untuk label kecil, lower third, log, timecode, kode. Bobot 400/500/700.

Unduh woff2 dari npm `@fontsource/inter`, `@fontsource/playfair-display`, `@fontsource/jetbrains-mono`. Daftarkan `@font-face` dan `await document.fonts.load()` sebelum `READY`.

## Kelas teks

| Kelas | Ukuran | Dipakai |
|---|---|---|
| `.n` | 44px Inter 600 | Kata biasa dalam caption |
| `.s` | 98px Playfair italic 800 putih | Kata kunci netral |
| `.r` | 100px Playfair italic 800 merah | Kata kunci negatif |
| `.g` | 100px Playfair italic 800 hijau | Kata kunci positif |
| `.R` | 170px Playfair italic 900 merah | Kata hantaman (satu per video, maksimal dua) |
| `.m` | 86px Playfair italic 800 di atas bar merah | Frasa yang di-highlight blok |

## Glow (wajib)

```css
.n { text-shadow: 0 0 10px rgba(255,255,255,.5), 0 1px 2px rgba(0,0,0,.95),
                  0 2px 14px rgba(0,0,0,.95), 0 0 36px rgba(0,0,0,.8); }
.s { text-shadow: 0 0 16px rgba(255,255,255,.6), 0 0 40px rgba(255,255,255,.25),
                  0 3px 14px rgba(0,0,0,.9), 0 0 46px rgba(0,0,0,.65); }
.r { text-shadow: 0 0 5px rgba(255,130,130,.95), 0 0 18px rgba(255,30,30,.9),
                  0 0 48px rgba(255,0,0,.65), 0 3px 12px rgba(0,0,0,.9), 0 0 60px rgba(0,0,0,.5); }
.g { text-shadow: 0 0 5px rgba(170,255,200,.95), 0 0 18px rgba(30,235,110,.85),
                  0 0 48px rgba(0,220,90,.55), 0 3px 12px rgba(0,0,0,.9), 0 0 60px rgba(0,0,0,.5); }
.R { text-shadow: 0 0 6px rgba(255,130,130,.95), 0 0 24px rgba(255,30,30,.9),
                  0 0 64px rgba(255,0,0,.7), 0 0 130px rgba(255,0,0,.4), 0 4px 16px rgba(0,0,0,.9); }
```

Polanya: **glow warna berlapis (dekat, sedang, jauh) + drop shadow gelap + halo gelap**. Halo gelap yang bikin teks tetap terbaca di atas wajah atau baju terang.

Tambahkan juga scrim radial di belakang area caption:

```css
radial-gradient(ellipse 640px 290px at 540px 940px,
  rgba(0,0,0,.58) 0%, rgba(0,0,0,.3) 55%, rgba(0,0,0,0) 100%)
```

## Komposisi artistik (bukan rata tengah)

Blok caption dengan ukuran campur **tidak boleh** rata tengah semua. Dua aturan:

**1. Geser tiap baris (zig-zag).** Tiap baris dapat offset x. Pola yang dipakai:

| Jumlah baris | Offset |
|---|---|
| 1 baris | `[0]` |
| 2 baris, baris besar di bawah | `[-46, 40]` |
| 2 baris, baris besar di atas | `[30, -46]` |
| 3 baris | `[-50, 0, 50]` atau variasi `[-80, 0, 80]` untuk kontras tinggi |

Blok yang didominasi satu kata raksasa boleh sampai `[-250, 0]`.

**2. Selipkan kata kecil ke pojok atas kata besar.** Kata `.n` yang berada sebelum kata besar pertama di baris kedua ke bawah diberi `align-self:flex-start` dan `margin-top: 0.16 x tinggi baris`. Efeknya kata kecil "menempel" di bahu kata besar, bukan sejajar tengahnya.

**3. Rapatkan jarak antar baris.** Baris yang mengandung teks besar diberi `margin-top: -0.13 x ukuran terbesar`. Baris kecil setelah baris raksasa diberi `margin-top: 2px`.

**4. Strut tak terlihat.** Tiap baris diberi span kosong (`​`) berukuran kelas terbesar di baris itu, `visibility:hidden`, supaya tinggi baris tidak melompat saat kata muncul satu per satu.

## Safe zone reels

```
Area teks aman     : x 70 - 1010,  y 260 - 1520
Rail tombol kanan  : x > 960 dan y > 1100  -> kosongkan
Strip bawah        : y > 1560              -> jangan taruh apa pun penting
Header atas        : y < 240               -> jangan taruh apa pun penting
```

Posisi baku: caption close-up `y = 945`, caption dengan kartu di bawah `y = 865`, caption wide shot `y = 1450`, bar CTA `y = 1428`.

Verifikasi otomatis dengan `assets/qa.js`, bukan dengan perkiraan mata.

## Mockup HP modern

Bukan kartu polos. Lapisannya dari luar ke dalam:

```
.phone  bezel gradien 150deg (#5a5a64 -> #24242a -> #0e0e11 -> #2c2c33 -> #5a5a64), radius 46px,
        shadow 0 44px 90px rgba(0,0,0,.75)
.rim    inset 3px, radius 43px, #050506
.screen inset 9px, radius 38px, overflow hidden  <- image sequence di sini
.island top 12px, 80x23px, radius 12px, hitam, center
.btn    tiga tombol samping tipis 4px gradien
.gloss  linear-gradient 135deg putih .2 -> transparan, overlay di layar
```

Rasio kartu 270x540 (1:2). Video 9:16 di-`object-fit:cover`, jadi terpotong sekitar 7% per sisi. Sebutkan ini ke user.

Untuk grid 3D: bungkus dalam `perspective: 1600px`, induk `transform-style: preserve-3d`, lalu animasikan `rotateX` dan `rotateY` pelan lewat `perFrame` (amplitudo 3-7 derajat, frekuensi 0.6-0.75). Tiap HP masuk dari bawah dengan `rotationX:-55, z:-200` lalu mendarat.

Tambahkan `sheen` (kilap diagonal) yang menyapu tiap kartu pada momen penekanan.

## Easing dan durasi

| Gerakan | Easing | Durasi |
|---|---|---|
| Kata `.n` masuk | `power2.out`, y 14 -> 0, blur 10 -> 0 | 0.22 |
| Kata besar masuk | `power3.out`, scale 1.35 -> 1, blur 16 -> 0 | 0.30 |
| Kata hantaman `.R` | `power3.out`, scale 1.5 -> 1, brightness 2.6 -> 1 | 0.34 |
| Kartu/panel masuk | `power3.out` | 0.45 - 0.80 |
| Keluar | `power2.in`, blur naik | 0.22 - 0.25 |
| Pop kecil | `back.out(1.6 - 2.2)` | 0.30 - 0.35 |
| Transisi besar | `power3.inOut` | 0.50 - 0.75 |

Kata masuk pada `T(t_kata) - 0.04` supaya animasi selesai tepat setelah kata terdengar.

## Dilarang

Emoji 3D, ikon bulat warna-warni, stiker, maskot, confetti, bintang, mata, tangan kartun, panah tebal melengkung, shadow ganda tebal, gradien pelangi, font display dekoratif, teks berkedip, elemen yang berputar penuh, bounce lebih dari satu pantulan.
