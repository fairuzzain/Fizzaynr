# Produksi: format file, helper, masalah umum

## Susunan folder kerja

```
<folder proyek>/build/
  env.sh            dari preflight.sh (source di setiap shell baru)
  STATE.md          catatan lanjutan
  aset/             VO, klip, gambar, font, SFX milik user (salin ke sini, path relatif dari build/)
  brand.json        warna + font
  project.json      VO, jeda, ekor, audio
  words.json        [[detik_VO_asli, "kata"], ...]
  scenes.js         SATU-SATUNYA file kode yang ditulis per proyek
  clips.json        dari frames.py
  img/ icon/ font/ vf/ gsap.min.js     diisi assemble.py / frames.py
  index.html        hasil assemble.py
  seg/ mix.wav      kerja render_all.py
  out/Reel_V<N>.mp4 hasil
  versi/V<N>/       salinan sumber sebelum revisi
```

## brand.json

| Kunci | Wajib | Isi |
|---|---|---|
| `accent` | ya | warna utama brand |
| `bg` | ya | latar gelap berwarna (bukan #000) |
| `ink`, `paper` | tidak | teks gelap di scene terang (default #141414), putih |
| `font_preset` | tidak | preset font pack: poppins (S1), jakarta (S2), montserrat (S3), urbanist (S4), jakarta-anton (S5), poppins-unbounded (S6) |
| `font` | tidak | nama font (default Poppins). Dicari di font pack dulu, lalu npm @fontsource |
| `font_files` | tidak | `{"700": "aset/font/X-Bold.ttf", "800italic": "aset/font/X-XBI.ttf"}` file milik user |
| `success` | tidak | hijau tombol sukses |
| `accentHi`, `accentSoft`, `bgDeep`, `bgLift`, `tint1-3`, `chipInk`, `accentShade`, `blobs` | tidak | turunan; dihitung otomatis, isi hanya kalau guideline menentukan |

## project.json

```json
{
  "title": "Promo kelas AI",
  "vo": "aset/vo.mp3",
  "pauses": [[17.67, 3.0], [24.10, 1.0]],
  "tail": 2.0,
  "icons": ["crown"],
  "audio": {
    "sfx": true,
    "sfx_source": "skill",
    "sfx_dir": "aset/sfx",
    "sfx_files": {"whoosh": "aset/sfx/transisi.mp3"},
    "sfx_gain": 1.0,
    "music": "aset/musik.mp3",
    "music_level": "pelan",
    "lufs": -14
  }
}
```

- `pauses`: `[detik VO asli, durasi hening]`, dari `gaps.py`. Dipakai sama persis oleh halaman (`T()`) dan audio.
- `icons`: ikon tambahan yang namanya dibentuk dinamis di kode (assemble hanya mendeteksi `icon('nama'...)` literal).
- `sfx_source: "synth"` = abaikan SFX bawaan skill. `sfx_dir` / `sfx_files` selalu menang.

## Tanda tangan helper (template.html)

| Helper | Catatan |
|---|---|
| `at(frasa, n=1)` | waktu final kata/frasa ke-n; tanda baca dan huruf besar diabaikan |
| `W(i)`, `T(t)` | kata indeks i; detik VO asli → final |
| `scene(t0, t1, cls, css)` | div layar penuh, tampil t0-t1 |
| `stack([el,...], yTengah, gap)` | susun teks yang berkaitan jadi satu blok rapat di yTengah (gap px / array; default 0,22 x tinggi, maks 36) |
| `A(parent, x, y, html, cls, css)` | elemen dengan titik tengah di (x, y) |
| `line(parent, x, y, [[teks, t, style]], css)` + `wordsIn(el, kind)` | baris kata, tiap kata masuk di waktunya |
| `hlOn(span, t, bg='#fff', col=ACC)` | kata kunci jadi pil |
| `inA(el, t, kind, dur)` / `outA(el, t, kind, dur)` | masuk: blur pop zoom slam right drop fade; keluar: blur up left shrink |
| `shake(t, amp=18, d=.35)` | getar kamera |
| `float(el, amp, phase)` | mengambang sinus |
| `count(el, t, dur, sampai, dari=0, {fmt, tick})` | angka berjalan, format 1.483 |
| `typeText(el, t, teks, jeda=.079, caret=true, caretSampai)` | mengetik + SFX type; mengembalikan waktu selesai |
| `cursorPath([[t,x,y],...], hideAt)` + `click(t, x, y, parent)` | kursor + cincin klik + SFX click |
| `whiteRise(parent, t, d=.38, warna)` | panel bergelombang naik (scene terang) + whoosh |
| `vid(parent, 'nama', null, t0, t1, css, loop, rate)` | image sequence dari frames.py |
| `phone(parent, x, y, lebar=520)` | `{el, screen}` mockup HP |
| `mergeTo(parent, t, htmlA, htmlB, htmlC, {y, gap, w, h})` | A + B = C, `{A,B,P,C,end}` |
| `bigArrow(parent, x, y, t, {dir, size})` | panah ajakan solid memantul |
| `sfx(t, jenis, gain=1)` | click pop bubble whoosh swish thud ding tick type riser error |
| `perFrame.push(t => ...)` | apa pun yang dihitung per frame (fase label, putaran ikon) |

Variabel: `tl` (timeline GSAP paused), `TOTAL`, `ACC`, `ACC_HI`, `INK`, `PAPER`, `RED` (= accent, nama lama).

## Masalah umum

| Gejala | Penyebab | Perbaikan |
|---|---|---|
| `HALAMAN ERROR ... at(): "x" tidak ada` | kata tidak sama dengan words.json | cek ejaan/kemunculan ke-n, atau perbaiki teks words.json |
| Elemen terlihat sebelum waktunya | `fromTo` kedua pada properti yang sama merender langsung | `tl.set(el,{opacity:0},0)` + `immediateRender:false` |
| `vid(): klip belum diekstrak` | frames.py belum dijalankan / nama beda | jalankan frames.py, lalu assemble |
| Ikon kotak kosong | nama ikon salah | baca saran "mirip" dari assemble.py |
| Emoji GAGAL | nama folder Fluent beda | cek nama di github.com/microsoft/fluentui-emoji |
| `BELUM SELESAI` | batas waktu perintah | jalankan render_all yang sama lagi |
| SFX terlalu dekat dengan VO | file SFX user keras | `audio.sfx_gain` 0.6-0.8 |
| Render jalan tapi gambar hitam | font/gambar belum termuat | pastikan semua `img` ada; jalankan snap.js untuk melihat |
