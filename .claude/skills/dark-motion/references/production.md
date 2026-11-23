# Production

Detail teknis tiap langkah. SKILL.md berisi alurnya; file ini berisi format, opsi, dan cara memperbaiki masalah.

## Struktur folder kerja

```
build/
  env.sh            dari preflight: SK, PY, BUILD, CHROME_BIN, PW_MODULE (source di setiap shell baru)
  STATE.md          catatan progres untuk melanjutkan pekerjaan
  src/main.mp4      video kerja 1080x1920 30fps (setelah prep dan cuts)
  src/main_full.mp4 versi sebelum potong jeda (supaya cuts.py bisa diulang dengan level lain)
  src/info.json     hasil prep: part, mode, pembersihan suara
  words.json        [[detik, "kata"], ...] di timeline video kerja
  words_list.txt    transkrip bernomor (autocap --list)
  cuts.json         titik potong (dipakai autocap untuk zoom penyamar)
  project.json      pengaturan proyek (warna, huruf, jeda, ekor, audio)
  capplan.json      rencana caption (kata kunci, hook, skip, gaya)
  captions.js       hasil autocap, JANGAN diedit manual
  scenes.js         scene buatan sendiri
  extra/*.js        helper tambahan (opsional, mis. ENV gelombang suara)
  aset/             aset dari user (foto, logo, musik, font)
  icon/*.svg        ikon tambahan (opsional; ikon bawaan otomatis tersedia)
  vf/main, vf/blur  image sequence video utama dan versi blur
  vf/<klip>         image sequence klip pendukung
  index.html        halaman hasil assemble.py
  seg/              potongan render (otomatis)
  out/Reel_V<N>.mp4 hasil akhir
  versi/V<N>/       salinan scenes.js, capplan.json, project.json sebelum revisi
```

## project.json

```json
{
  "c1": "#86EF5A", "c2": "#3FA9FF",
  "glow": true,
  "font": { "mode": "sans", "file": null, "body": "inter" },
  "pauses": [[36.75, 2.0]],
  "tail": 4.0,
  "grain": "auto",
  "audio": { "sfx": true, "ambience": true, "music": null, "music_level": "pelan", "lufs": -14 }
}
```

| Kunci | Arti |
|---|---|
| `c1`, `c2` | Warna aksen (hex) |
| `glow` | Teks menyala di latar gelap |
| `font.mode` | `sans` (default) / `serif` / `custom` / `preset` (otomatis kalau `font.preset` diisi, mis. `{"preset": "tegas"}`). Untuk `custom`, `font.file` = path relatif di folder build (mis. `aset/brand.ttf`), `font.body` = `inter` atau `custom` |
| `pauses` | Jeda yang disisipkan: `[detik_sumber, panjang]`. Frame dibekukan, suara hening. Untuk scene yang butuh waktu baca |
| `tail` | Detik tambahan setelah video sumber habis (scene penutup). Frame terakhir dibekukan |
| `grain` | `auto` (default; diam ≤ 30 dtk, mati di atasnya), `static`, `move`, `off` |
| `audio.sfx` | SFX aktif; `false` = tanpa SFX sama sekali |
| `audio.sfx_source` | `"skill"` (default) = 9 SFX bawaan di `assets/sfx/` (tick=click, air=pop, sweep=whoosh, key=typing, conf=notification, sub=punch; glitch dan rise sintetis); `"synth"` = semua SFX halus sintetis |
| Jenis SFX tambahan | Untuk scene buatan sendiri, `sfx(t, jenis)` juga menerima `pop`, `bubble`, `whoosh`, `swish`, `click`, `error`, `thud`, `ding`, `type` (nama sama dengan Script to Motion dan Serif Editorial Reel). `error` hanya untuk hal negatif/gagal |
| `audio.sfx_dir` | Folder SFX milik user (relatif di folder build, mis. `aset/sfx`). File dipetakan menurut nama: bubble → `bubble`, click/klik → `tick`, pop → `air`, swipe/whoosh → `sweep`, typing/keyboard → `key`, notif/ding/chime → `conf`, boom/impact/hit/punch → `sub`, glitch → `glitch`, rise/riser → `rise`, error/wrong → `error`. Jenis tanpa file memakai SFX bawaan. Log mix mencetak `SFX dipakai: ...` |
| `audio.sfx_files` | Pemetaan manual, menang atas `sfx_dir`: `{"tick":"aset/sfx/klik.mp3"}` |
| `audio.ambience` | Pad sangat pelan di ekor/penutup |
| `audio.music` | Path musik dari user (relatif di folder build). Diulang, fade, dan otomatis mengecil saat ada suara |
| `audio.music_level` | `pelan` (20 dB di bawah suara) atau `sedang` (15 dB di bawah) |
| `audio.lufs` | Target kenyaringan, -14 cocok untuk Instagram/TikTok/YouTube Shorts |

**Panjang video dan peta waktu dihitung dari file ini** oleh assemble.py (halaman) dan mix.py (audio). Karena keduanya membaca file yang sama, halaman dan audio tidak bisa tidak sinkron. Setelah mengubah `pauses` atau `tail`, jalankan ulang `autocap.py` (posisi caption ikut bergeser) dan `assemble.py`.

## capplan.json

```json
{
  "style": "pendek",
  "keys": { "12": "k1", "13": "k1", "40": "X", "57": "s", "88": "k2" },
  "hook_end": 3.8,
  "skip": [[10.2, 14.0]],
  "breaks": [23, 40],
  "zoom": true,
  "scale": 1.0,
  "y": null
}
```

| Kunci | Arti |
|---|---|
| `style` | `pendek` (1-3 kata, maks ~20 huruf) atau `sedang` (3-6 kata, dua baris) |
| `keys` | Nomor kata (dari `words_list.txt`) → kelas: `s`, `k1`, `k2`, `X`. Di latar terang otomatis jadi blok warna |
| `hook_end` | Detik sumber akhir kalimat pembuka; kata sebelumnya tampil sebagai judul besar |
| `skip` | Rentang detik sumber yang teksnya ditampilkan scene buatan sendiri |
| `breaks` | Paksa caption baru dimulai di nomor kata ini |
| `zoom` | Zoom berirama: bergantian 1,0 dan 1,12 di titik potong dan awal kalimat; 1,18 kalau ada kata hantaman; 1,06 di tengah kalau ada dua orang |
| `scale` | Perbesar/perkecil semua caption (mis. 0,9 kalau ada teks terpotong) |
| `y` | Paksa posisi semua caption; `null` = otomatis menghindari wajah |

Semua waktu di capplan.json memakai timeline **sumber**, sama dengan words.json dan words_list.txt.

## Persiapan video (prep.py)

- Part disambung sesuai urutan argumen. Volume tiap part disamakan dulu (target -18 LUFS, maksimal ±12 dB), lalu final dinormalkan ke -14 LUFS di mix.py.
- Part yang bentuknya beda dengan part pertama (mis. satu klip vertikal di antara video horizontal) ditaruh utuh di tengah dengan latar blur, bukan di-zoom paksa.
- Rotasi dari HP dibaca otomatis.
- `--trim mulai:selesai` memotong video gabungan. Batas default 180 detik (`--max`).
- Pembersihan suara otomatis kalau jarak suara-bising di bawah 36 dB: filter highpass + pengurang bising ringan. `--denoise off` kalau hasilnya terasa aneh (suara jadi "berair").

### Bentuk vertikal untuk video horizontal

| Mode | Cara kerja | Kelebihan | Kekurangan |
|---|---|---|---|
| `track` | Potongan 9:16 bergerak mengikuti wajah utama, dengan zona mati supaya kamera tidak goyang | Wajah besar, terasa seperti video vertikal asli | Gambar diperbesar ~1,8x, sedikit lebih lembut. Dua orang berjauhan tidak bisa masuk sekaligus |
| `fit` | Video utuh di tengah, atas-bawah diisi versi blur | Tidak ada yang terpotong, ketajaman asli | Wajah lebih kecil; ruang atas-bawah perlu diisi teks/grafik |
| `stack` | Dua panel 9:8 atas-bawah, masing-masing berpusat di satu wajah. Bagian yang hanya berisi satu orang otomatis memakai `track` | Paling cocok untuk podcast 2 orang | Butuh dua wajah yang terdeteksi jelas |

Tanpa OpenCV, deteksi wajah mati: `track` jadi potongan tengah dan caption memakai posisi default.

## Waktu kata

**Dari subtitle** (`srt2words.py`): subtitle per kata dipakai apa adanya; subtitle per baris dibagi proporsional menurut panjang kata (batas kalimat akurat, kata di tengah baris perkiraan). `--offset` menggeser semua waktu, untuk SRT per part.

**Dari suara** (`wordtime.py`): VAD → transkrip whisper-small per kalimat → waktu per kata lewat prefix decoding whisper-base → dirapikan dengan peta senyap. Paket dan model (~850 MB) dipasang/diunduh sekali per sesi ke `~/.cache/dark-motion/models`. Waktu proses kira-kira 2 menit per menit audio di mesin 2 inti, ditambah unduhan.

`--lang`: `id`, `en`, `ms`, atau `auto`. Transkrip otomatis hanya untuk **waktu**; teks yang tampil boleh diperbaiki di words.json (jangan ubah angka waktunya).

**Perapian waktu (cuts.py, selalu):** kata yang jatuh di bagian sunyi digeser maju ke awal bunyi; kata pertama setelah jeda yang terlambat ditarik mundur ke awal bunyinya. Ini memperbaiki meleset 0,3-1 detik yang umum terjadi.

## Potong jeda (cuts.py)

| Level | Jeda yang dipotong | Disisakan | Kata pengisi ("eee", "emm") |
|---|---|---|---|
| `tidak` | - | - | tidak |
| `halus` | > 0,9 dtk | 0,35 dtk | tidak |
| `sedang` | > 0,55 dtk | 0,22 dtk | dibuang kalau tertranskrip |
| `agresif` | > 0,35 dtk | 0,12 dtk | dibuang kalau tertranskrip |

Hening di awal dipangkas sampai 0,12 detik, di akhir sampai 0,35 detik. Tiap sambungan diberi fade audio 6 ms supaya tidak ada bunyi klik. cuts.py selalu mulai dari versi utuh, jadi aman dijalankan ulang dengan level lain (lalu ulangi frames.py dan autocap.py). Transkrip otomatis sering tidak menuliskan "eee", jadi pembuangan kata pengisi bergantung pada transkripnya.

Potongan jeda membuat wajah "melompat". Zoom berirama di autocap sengaja berganti skala tepat di titik potong untuk menyamarkannya; ini teknik standar editing talking head.

## Caption otomatis (autocap.py)

1. **Pengelompokan:** pecah di jeda, akhir kalimat, koma (kalau sudah ≥ 2 kata), batas jumlah kata/huruf, kata hantaman, dan batas hook. Kata sambung tidak dibiarkan menggantung di akhir caption.
2. **Posisi:** deteksi wajah pada frame di tengah durasi caption, lalu pilih pita (bawah 1400 / atas 330 / tengah 960 kalau ada dua wajah) yang paling sedikit menutupi wajah. Posisi sebelumnya dipertahankan selama masih aman, supaya caption tidak melompat-lompat.
3. **Kontras:** ukur kecerahan pita (persentil 80). Terang (> 0,62) → gradien gelap + kata kunci jadi blok warna. Sedang → gradien gelap saja. Gelap → tanpa tambahan.
4. **Ukuran:** baris dipecah supaya lebarnya ≤ 790 px; kata yang terlalu panjang diperkecil.
5. **Zoom dan SFX:** seperti dijelaskan di capplan.json. SFX `tick` di kata kunci (jarak minimal 1,2 dtk), `sub` di kata hantaman.

`captions_preview.txt` berisi semua caption dengan posisi dan status latar. Untuk mengubah, edit capplan.json lalu jalankan ulang.

## Halaman dan mesin animasi

`assemble.py` menyisipkan mesin animasi bawaan (`vendor/motion.js`), konfigurasi dari project.json, ikon yang dipakai, captions.js, extra/*.js, dan scenes.js ke template. Halaman dibuka langsung lewat `file://`, tanpa server.

Mesin animasi memakai gaya pemanggilan GSAP (subset), tapi deterministik untuk render per frame:
- `tl.to / from / fromTo / set`, posisi angka, `"+=1"`, `"<"`, `">"`, label; `duration`, `ease`, `delay`, `stagger`, `repeat`, `yoyo`, `keyframes`, `attr`, `autoAlpha`, `onUpdate`.
- Ease: `none`, `power0-4`, `sine`, `expo`, `circ`, `back(s)`, `elastic(a,p)`, `bounce`, `steps(n)`, masing-masing `.in/.out/.inOut`.
- Sebelum `fromTo`/`from` mulai, nilai "from" sudah berlaku. Tidak perlu `tl.set(el,{opacity:0},0)` lagi, walaupun tidak salah.
- `onStart`/`onComplete` tidak dipakai; gunakan `onUpdate` atau `perFrame`.
- `gsap.to()` di luar timeline diabaikan; selalu `tl.to(..., detik)`.
- Jangan menulis `style.transform` manual pada elemen yang juga di-tween transform-nya.

Video selalu dalam bentuk image sequence, bukan tag `<video>`, karena tag video tidak bisa dikunci per frame saat render. Gambar besar di scene dimuat lewat `pre(src)` supaya sudah siap sebelum frame pertama.

## Render (render_all.py)

1. Membaca TOTAL dan daftar SFX dari halaman.
2. Merakit audio (mix.py).
3. Merender potongan 240 frame secara paralel (sebanyak inti CPU, maksimal 3). Tiap potongan baru muncul sebagai file kalau selesai utuh.
4. Menyambung, lalu encode final dengan `aq-mode=3` (bagus untuk adegan gelap) di bawah 29 MB: CRF 20 dengan batas bitrate, dan kalau masih kebesaran, diulang dua tahap ke bitrate target.
5. Mengecek panjang video, audio, dan ukuran file.

`--max-minutes` (default 8) membuatnya berhenti rapi sebelum batas waktu perintah. Jalankan lagi sampai `SELESAI`. Kalau index.html atau project.json berubah, potongan lama otomatis dibuang. Kalau tidak ada yang berubah, perintah itu hanya mencetak file yang sudah jadi.

Perkiraan waktu di mesin 2 inti: sekitar 5 menit per menit video. Ukuran tanpa grain sekitar 11 MB per 30 detik, jadi video di atas ~80 detik mulai dikompres lebih kuat supaya muat 29 MB.

## Bakar efek ke frame (bake.py)

Efek yang harus menyatu dengan gambar (grain, glitch, pemisahan RGB, garis scan, pendaran) dikerjakan dengan OpenCV langsung di file frame, bukan lapisan CSS.

```bash
$PY $SK/assets/bake.py grade  build/vf/main build/vf/main --range 0:120 --soft --glow --scan --grain 9 --open 0.42 --zoom 0.55:1.18
$PY $SK/assets/bake.py glitch build/vf/main build/vf/main --at 1789 --width 15 --ca 30
$PY $SK/assets/bake.py matte  build/vf/main build/vf/fg   --range 280:353 --model <u2net_human_seg.onnx>
```

Warna blok mosaik glitch mengikuti `--c1`/`--c2` dalam urutan **B G R** (mis. aksen `#FFB547` → `--c1 71 181 255`); samakan dengan warna proyek.

Mode `matte` (potong orang dari latar) butuh `onnxruntime` dan model 176 MB dari GitHub Releases rembg (`u2net_human_seg.onnx`); pakai hanya kalau resepnya benar-benar butuh. Setelah membakar efek, **jangan** jalankan frames.py tanpa `--clips-only` lagi, karena akan menimpa hasilnya. bake.py mencatat setiap efek ke `build/baked.txt`; kalau frames.py memang perlu diulang, jalankan ulang baris-baris di file itu.

## Klip pendukung (clipscan.py + frames.py --clips-only)

```bash
$PY $SK/assets/clipscan.py build/scan.jpg a.mp4 b.mp4 --every 2           # satu baris per klip, kolom = detik
$PY $SK/assets/frames.py build --clips-only --clip-h 960 --clip ugc:a.mp4:0:4.5   # HP utama / kartu besar
$PY $SK/assets/frames.py build --clips-only --clip-h 534 --clip w1:b.mp4:8:4.5    # ubin dinding video
```

Pilih rentang yang bebas teks tertanam di **seluruh** 4-5 detiknya (teks sering muncul hanya di sebagian detik). Potongan footage utama user (misalnya PART 1 untuk kartu "video mentah") juga diekstrak lewat `--clip` dari file part aslinya, bukan dari `vf/main`, karena `vf/main` bisa berisi efek yang dibakar.

## Jeda untuk dicerna (gaps.py)

```bash
$PY $SK/assets/gaps.py build --from 14 --to 17 [--min .08]
```

Mencetak tiap rentang hening dengan saran "taruh jeda di X" dan kata sebelum/sesudahnya. Isi `project.json` → `pauses` dengan `[X, panjang]`. Patokan panjang: 1,5-2,0 dtk per hasil penggabungan (N1), 1,5-2,5 dtk untuk kartu bacaan. Di scenes.js, awal jeda di detik hasil = `T(X-0,01)+0,01`; jeda sebelumnya ikut menggeser semua waktu sesudahnya, jadi selalu pakai `T()` untuk detik ucapan.

## Objek 3D

Untuk objek yang harus benar-benar tiga dimensi, render dengan three.js (`npm i three`, butuh internet) jadi urutan PNG transparan, lalu pakai sebagai `vid(..., 'png')`. Chromium dijalankan dengan SwiftShader, jadi WebGL jalan tanpa GPU. `MeshPhysicalMaterial` + `RoomEnvironment` sudah cukup untuk hasil mengilap. Jarang dibutuhkan; kartu, mockup, dan teks biasanya cukup.

## Masalah umum dan perbaikannya

| Gejala | Penyebab biasa | Perbaikan |
|---|---|---|
| Halaman error saat dibuka | Salah ketik di scenes.js | Pesan errornya dicetak oleh render/qa/snap; perbaiki baris itu |
| `ikon hilang: nama` | Nama ikon tidak ada | Cari nama yang ada: `$PY $SK/assets/assemble.py --icons <kata>`, atau ambil dengan fetch_icons.sh |
| Ikon di chip tidak muncul | Nama ikon hanya ada di variabel, bukan literal | Tulis nama ikon sebagai string langsung di `icon('...')`, `chip(...,'ikon')` atau `chipC(...,'ikon',t)` supaya assemble.py menemukannya |
| Teks scene tampil serif | `font:'... Inter'` | Pakai `var(--bf)` / kelas `n`; nama keluarga di halaman `I`, `PF`, `JB` |
| Efek glitch hilang setelah menambah klip | frames.py tanpa `--clips-only` | Bakar ulang dari `build/baked.txt`, lain kali pakai `--clips-only` |
| SFX user tidak terdengar | `sfx_dir` salah atau nama file tidak cocok pola | Cek log `SFX dipakai:`; pakai `sfx_files` untuk pemetaan manual |
| Caption terpotong di tepi | Kata panjang di font sans/custom | `capplan.json` → `scale: 0.9`, atau `breaks` |
| Caption menutupi wajah | Wajah tidak terdeteksi (menunduk, profil) | `capplan.json` → `y`, atau `breaks` supaya caption pindah |
| Kata muncul telat/cepat | Waktu subtitle per baris adalah perkiraan | Geser waktu kata itu di words.json, lalu autocap + assemble |
| Audio dan video tidak sama panjang | Hampir tidak mungkin lagi karena keduanya membaca project.json | Jalankan ulang render_all.py; kalau tetap, cek pesan mix.py |
| File final lebih dari 29 MB | Tidak terjadi; encode dua tahap menjamin | Kalau kualitas terlalu turun untuk video panjang, matikan grain dan kurangi scene yang penuh gerak |
| Render terhenti di tengah | Batas waktu perintah | Jalankan perintah yang sama lagi |
| `BLOCKED` di preflight | Fitur file/kode belum aktif | Sampaikan pesan dari preflight ke user |
| Transkrip kosong/aneh | Bahasa salah, atau audio sangat bising | `--lang` yang benar; minta subtitle dari user |
