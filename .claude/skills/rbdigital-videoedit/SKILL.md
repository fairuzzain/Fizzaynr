---
name: "rbdigital-videoedit"
description: "Edit talking-head videos (one or many takes) into polished 9:16 shorts: auto-analyze and propose a full edit plan, or pick from 85 styles (text behind body, karaoke, split screen, editorial, orbit, bento grid, checklist, HUD, paper cut, halftone, before/after...); cuts, captions, zooms, effects, B-roll, music; renders MP4 with HyperFrames. Use when the user uploads a talking video to edit."
---

# Talking Head Edit (Auto + Menu)

User upload video talking head (satu atau BANYAK take) → pilih MODE → prep, potong, transcribe → storyboard untuk approve → bina HyperFrames → QA → render MP4 9:16. Balas ikut bahasa user (default BM rojak), ringkas.

**Fail rujukan (baca bila perlu sahaja, jangan semua sekali):**
- `assets/previews/menu-style-1..7.jpg`: sheet gambar contoh 85 style (grid ikut kategori, nombor sama dengan Menu). Hantar bila tunjuk Menu.
- `references/styles.md`: menu 85 style + resipi style 1-21 + preset Auto. Baca bila tunjuk Menu atau build style 1-21.
- `references/styles-extra.md`: resipi style 22-85 + peraturan umum (3D, morph, pra-render). Baca bila build salah satu style 22-85.
- `references/library.md`: Caption Library, Font Library, Effect Library, icon sheet, B-roll. Baca masa tulis cadangan/storyboard.
- `references/tech.md`: semua command (setup, prep, grade, multi-take, transcribe + alignment, cutout, audio mix, render, export, fallback FFmpeg). Baca masa build.

## Pilih mode (soalan pertama)

Tanya satu soalan (AskUserQuestion kalau ada):
- **Auto (Recommended)**: aku analyze, cadang style, caption, font, effect, B-roll dalam SATU mesej. Kau reply OK atau ubah.
- **Menu**: aku tunjuk 85 style ikut kategori (dari `references/styles.md`, sebagai text, nombor + 1 baris), kau pilih nombor (boleh campur 2-3).
  - **Gambar contoh dulu:** setiap kali tunjuk Menu, JANGAN hantar terus dari folder skill (folder plugin/skill ialah folder dalaman app, viewer tak boleh buka → "Couldn't load this preview"). SALIN dulu ke folder kerja, kemudian hantar salinan:
    `mkdir -p previews && cp <skill>/assets/previews/menu-style-*.jpg previews/` (folder `/mnt/user-data/outputs/` kalau wujud, atau folder kerja/scratchpad semasa). Hantar 7 salinan tu dalam SATU SendUserFile (ikut nombor, path penuh salinan), caption: "Contoh visual 85 style, pilih nombor". Lepas tu baru senarai text.
  - Kalau SendUserFile tiada (Claude Code terminal): bagi path penuh folder `assets/previews/` supaya user boleh buka sendiri, kemudian terus bagi text menu.

Skip soalan bila jelas:
- Sebut nombor/nama style ("buat 1+19", "editorial") → Menu, terus guna.
- "kau buat je / auto / buat yang sesuai" → Auto, skip pause approval (sebut pilihan yang dibuat).
- Tiada jawapan / tiada orang → Auto.

Pause dibenarkan hanya: (1) mode/style, (2) approve storyboard. "Terus render / tak payah storyboard" → skip (2). Effect yang dia sebut dalam video ("zoom kat tangan aku", "make it moody") → buat dalam mode apa pun.

**Mula kerja senyap (setup, prep, transcribe, analyze) SEMENTARA tunggu jawapan** supaya tak buang masa.

## Aliran kerja

0. **Setup** senyap (`tech.md` §0). Windows: pastikan Python + faster-whisper ada (install via winget, §0) SEBELUM transcribe; jangan guna model English-only untuk BM. Baca `CLAUDE.md` dalam folder video kalau ada (nama, brand, warna, font, logo, handle). HyperFrames langsung tak jalan → fallback FFmpeg (`tech.md` §9), sebut satu baris.
1. **Prep**: convert, reframe 9:16, grade, PAKSA SDR bt709 (`tech.md` §1). Audio: highpass + denoise ringan sahaja, **jangan loudnorm di sini** (loudnorm sekali je, masa mix akhir).
2. **Rough cut / multi-take** (`tech.md` §2): dead air, filler, ayat berulang, take buruk, nafas.
3. **Transcribe + align** (`tech.md` §3): word timestamp tepat, betulkan salah dengar, kemudian **re-align teks yang dah dibetulkan** supaya karaoke tak drift.
4. **Analyze**: ffprobe + frame sheet. Kenal pasti hook, ayat paling kuat, keyword, senarai/nombor, CTA, ayat untuk B-roll, perkataan untuk icon, posisi muka & ruang kosong kepala.
5. **Cadangan (Auto) / Storyboard (semua mode)**: format bawah. Mulakan cutout (`tech.md` §4) di background SEMENTARA tunggu approve.
6. **Build** komposisi (struktur §Asas komposisi + resipi `styles.md` + `library.md`).
7. **Audio**: SFX + music jana sendiri, mix sekali (`tech.md` §5).
8. **QA → render → export** (`tech.md` §6-7, checklist QA bawah). Sebelum render: `slop_lint.py`. Lepas render: `look.py` gates, FAIL wajib betulkan.
9. **Hantar** (format bawah).

## Craft editing (WAJIB, semua style)

Ni yang beza edit biasa dengan edit pro. Ikut setiap video:

1. **Cold open.** Cari ayat paling kuat/mengejutkan dalam SELURUH video (nombor besar, hasil, kontroversi, soalan tajam). Kalau bukan ayat pertama, salin 1.5-3s ayat tu ke 0:00 sebagai hook, kemudian whoosh/flash → video mula seperti biasa. Hook mesti faham tanpa konteks. Sebut dalam cadangan: "Hook asal: … → cadang cold open: …".
2. **Pattern interrupt setiap 2-4s.** Sesuatu mesti berubah: punch-in, tukar caption style, B-roll, effect, angle. Tiada 5s statik.
3. **J-cut / L-cut.** Bila masuk/keluar B-roll atau tukar take/angle, audio seterusnya masuk 3-6 frame (0.1-0.2s) SEBELUM gambar (J-cut), atau audio lama tertinggal sekejap selepas gambar tukar (L-cut). Cut terus audio+video serentak hanya untuk jump cut dalam ayat sama.
4. **Silence sebelum punchline.** 0.3-0.5s sebelum punch word: music duck ke 0 (atau berhenti), caption kosong / satu perkataan, kemudian punch + SFX + music drop balik. Max 2-3 kali satu video.
5. **Breath control.** Nafas antara ayat: kurangkan -12dB atau potong kalau ada dead air; JANGAN buang semua nafas (bunyi robot). Nafas dalam ayat dibiarkan.
6. **Pacing ikut emosi.** Bahagian masalah/cerita: cut lebih rapat, B-roll. Bahagian penting/ikhlas (testimoni, nasihat): biar bernafas, kurang effect, muka penuh.
7. **Loop ending.** Ayat/visual akhir sambung balik ke hook (contoh hook "Aku tak edit langsung…", akhir "…sebab tu aku tak edit langsung."), atau end card pendek ≤1.5s supaya video ulang licin. Cadang ayat loop dalam cadangan kalau skrip tak ada.
8. **Satu sistem caption.** 1 style utama + 1 style emphasis (warna/saiz/box dari keluarga font sama). Style ke-3 hanya untuk hook atau CTA. Tukar ikut seksyen, bukan setiap ayat.
9. **Effect ikut makna**, max satu effect "besar" setiap ~3s; hook (0-3s) paling kuat; bagi satu "twist" kalau sesuai.

## Motion overlay (WAJIB, override ease dalam resipi style)

Semua overlay (caption, text behind, icon, kad, badge, B-roll, banner) bergerak ikut peraturan ni. Signature style kekal, cuma CARA bergerak ikut sini.

```js
// tampal atas script timeline. 30 fps, tulis masa dalam FRAME
const FPS = 30, F = n => n / FPS;
const E = {
  land:   "power3.out",     // DEFAULT masuk: perlahan bila sampai (10-12 f)
  soft:   "power2.out",     // kad besar, B-roll, panel (12-16 f)
  snap:   "expo.out",       // keyword, nombor, punch word (6-9 f)
  settle: "back.out(1.15)", // lean kecil lewat — HERO sahaja
  exit:   "power2.in",      // keluar laju (6-9 f)
  throw:  "power4.in",      // keluar kuat sebelum cut (5-7 f)
  move:   "power2.inOut",   // #cam pindah antara dua posisi
};
```

1. **Masuk perlahan bila sampai, keluar laju.** Masuk guna `E.land`/`E.snap`, keluar guna `E.exit`/`E.throw`. Jangan `.out` untuk keluar.
2. **Overshoot jarang.** Max ~1 dalam 10 gerakan, hero sahaja (`E.settle`). Tiada `elastic`, `bounce`, `back.out(2+)`. Caption pop: `scale 1.25→1` dengan `E.snap`, bukan melantun. Kecuali style yang signature dia memang kenyal (62 Claymorphism, 51 Product Assembly snap): kekal, tapi pada momen hero sahaja.
3. **Tiada apa membesar dari 0.** Bukan `scale:0→1`. Masuk dari saiz besar (`scale 1.6-3 → 1`, `E.snap`), dari tepi frame, atau mask/wipe. Percikan/spark dikecualikan.
4. **Gerak, bukan fade.** Masuk dengan transform; opacity ikut sekejap (5-7 f) bersama gerakan. Nisbah ≥ 4 transform : 1 fade sahaja.
5. **Cut on motion.** Tukar take/B-roll = hard cut semasa sesuatu bergerak (punch-in `#cam` `E.snap` tepat pada cut). Transition besar (whip, flash, zoom-through) hanya 2-3 kali: hook → isi, reveal, isi → CTA. Tiada fade hitam / dissolve antara beat.
6. **Tiada frame mati.** Video beku = bug (`look.py` tangkap). Jeda sengaja (silence sebelum punchline) ≤ 0.5s, max 2-3.
7. **Anti-slop:** tiada label kecil parked kat corner, kicker tracked-caps atas headline, kad UI generik ("Good morning" + status dot), headline typewriter huruf demi huruf (kecuali style memang typing). Progress bar dibenarkan (retention), tapi nipis.

Timing biasa: masuk 10-12 f, keyword 6-9 f, keluar 6-9 f, stagger 2-4 f, end card ≤ 1.5s.

## Mode Auto: cadangan (satu mesej, lepas analyze)

- **Ringkasan**: durasi asal → anggaran lepas cut, topik, hook asal → cold open dicadang, CTA, ayat loop, kualiti shot & audio.
- **Isu dikesan**: ejaan, pause total, filler, ulangan, take buruk, hook lemah, muka terlalu tepi, bunyi bising, skin tone.
- **Preset style** A-F (`styles.md`), cadang satu, tanda Recommended. Boleh cadang nombor Menu kalau lebih sesuai.
- **Caption system**: style utama + emphasis (+ khas hook/CTA) dari `library.md`.
- **Font mix text belakang badan**: satu "Set font siap" dari `library.md` (atau mix sendiri 2-3 font) ikut mood topik, sebut font mana untuk perkataan mana. **Set mesti berbeza dari video sebelum dalam chat yang sama**, dan jangan Poppins/Montserrat sahaja.
- **B-roll plan** (kalau E): shot + layout + sumber (1 user generate, 2 connector image-gen kalau ada, 3 code-only, 4 klip user). Tak jawab → 3 (percuma).
- **Beat sheet**: format storyboard.
- **Bonus**: 1 tajuk alternatif hook, caption post + 5 hashtag, cadangan frame cover.
- **Asset perlu**: icon sheet, B-roll sheet, logo, screenshot. Music jana sendiri, jangan tunggu.

Tutup: "Reply OK untuk build semua, atau bagi nombor beat yang nak ubah/buang."

## Storyboard (sebelum build, semua mode)

Hantar dengan SendUserMessage sebagai jadual, satu baris setiap beat (2-4s):

| # | Masa | Ayat (ringkas) | Visual / effect | Teks atas skrin (font) | Caption | Audio |
|---|---|---|---|---|---|---|
| 1 | 0:00-0:02 | "Aku tak edit langsung…" (cold open) | Text behind | AKU TAK EDIT (dela-gothic-one) | Word Pop | whoosh, music mula |

Atas jadual: mode/style, palette (hex), font mix, caption system, durasi asal → final, take/ayat dibuang, cold open & loop. Akhir: "OK aku render, atau nak tukar beat mana?" Tunggu (kecuali dia suruh terus / tiada orang → teruskan dan sebut).

## Asas komposisi (semua style)

```
#root (data-composition-id=main, 1080x1920)
  #ground  (class=clip, background penuh; nampak bila cam mengecil / swap)
  #cam  (transform-origin 50% 45%; SEMUA scale/rotate/zoom muka di sini)
    #stage (overflow hidden)
      <video id=vid src=footage.mp4 data-has-audio=true>   (opacity 0 untuk Background Swap)
      #tint (mood)
      #behind [text / icon belakang badan]
      <video id=cut src=cutout.webm muted>                 (style cutout sahaja)
      [icon depan badan]
  #broll (bawah caption)
  [motion graphics, caption, badge, pop-up, kad, banner]
  #flash, #fade, progress bar
  <audio id=sfxN class=clip ...>
```
- `#vid` dan `#cut` dalam `#cam` yang sama supaya zoom/shake sentiasa sync.
- Punch-in: `#cam` scale 1.08-1.15 pada keyword dan setiap cut (sembunyi jump cut), max 1 setiap ~3-5s. Footage 1080p: jangan lebih 1.2 (pecah).
- Blur BG bila kad UI masuk: `#stage` `blur(14px) brightness(.8)` 0.3s, balik 0 bila keluar.
- Mood per seksyen: `#tint` (multiply/soft-light, #0d1a14 opacity 0→0.45) + `#stage` brightness/saturate bila dia sebut "moody/gelap"; "terang" sebaliknya.
- Warna default: coral #e2674f, gelap #211816, putih #fffaf7, keyword #ff8a6f (atau brand dari CLAUDE.md).

**Safe zone 9:16 (Reels/TikTok/Shorts):**
- Atas: tiada teks penting dalam 0-190px (bar username/tab).
- Bawah: tiada teks dalam 1536-1920px (20% bawah: caption post, butang).
- Kanan: tiada teks dalam x > 940px dari y 900 ke bawah (butang like/komen/share).
- Caption utama y ≈ 1150-1320, tak tutup muka/mulut. Text behind boleh lebih tinggi (ia memang belakang kepala).

## Peraturan lint HyperFrames / GSAP

- Setiap `<audio>`/`<video>` WAJIB ada `id` (kalau tak, senyap dalam render).
- Jangan CSS `transform` pada elemen yang GSAP animate (`gsap_css_transform_conflict`); center guna `left:0;right:0;margin:0 auto;width:fit-content`.
- Beberapa `fromTo` pada elemen sama → `immediateRender:false` pada yang kemudian.
- `fromTo` yang mula hidden mesti ada `opacity:1` dalam destination; caption `tl.set(opacity:0)` masa tamat.
- Burst/percikan: `tl.set(el,{opacity:1},t)` + `tl.to(el,{opacity:0},t)`, elemen berasingan setiap burst.
- Tiada random / Date: array tetap (`rotation:(i)=>[-7,5,-4,8][i]`).
- Background penuh pada elemen `class="clip"`, bukan `#root`.
- Daftar: `window.__timelines=window.__timelines||{}; window.__timelines['main']=tl;`
- Flex child SVG: `flex:0 0 70px`.
- Hanya satu fail HTML root dengan `data-composition-id` dalam folder projek.
- Font & GSAP local (`vendor/`, `fonts/`), tiada URL http luar.
- Lint baca HTML secara statik: `window.__timelines['main']=tl` mesti ada dalam `<script>` inline (bukan dalam fail .js luar sahaja).
- Media sama src+start+duration lebih dari sekali (clone, outline, glitch) → setiap `<video>` ada `id` unik DAN fail berbeza (hard link `cut_c1.webm`, `cut_c2.webm`), kalau tak lint `duplicate_media_discovery_risk` / video beku.
- Caption perkataan yang di-scale (karaoke) → `.w{display:inline-block;margin:0 10px}` supaya tak bertindih bila membesar.

## QA checklist (sebelum hantar)

- Hook: cold open faham tanpa konteks, effect paling kuat dalam 0-3s.
- Setiap beat ada effect dia; tiada 4s+ statik; max satu effect besar / ~3s.
- J/L-cut pada setiap masuk/keluar B-roll & tukar take; tiada audio pop/klik pada cut.
- Karaoke highlight ikut sebutan (check 3 titik: awal, tengah, akhir; drift ≤ 2 frame).
- Elemen belakang badan betul-betul di belakang (jari/tangan depan); text behind tak terpotong tepi.
- Font text behind: snapshot pada 2-3 big word dan pastikan font nampak BERBEZA (bukan semua Poppins fallback). `fonts.py` mesti exit 0.
- Caption tak bertindih / tak tutup muka; safe zone (atas, bawah, kanan); ejaan betul.
- Skin tone natural (tak oren/merah jambu) dalam frame before/after.
- Tiada take ulang tertinggal (dengar transcript final); nafas tak hilang semua.
- Audio: loudness akhir -14 LUFS (±1), true peak ≤ -1.5; CTA penuh di hujung; loop licin.
- Overlay ADA dalam render sebenar (contact sheet Final.mp4, bukan snapshot je).
- `python <skill>/scripts/slop_lint.py index.html --profile talking-head` → 0 ERROR (scale-from-0, fade-heavy, overshoot berlebihan). WARN = tengok semula.
- `python <skill>/scripts/look.py Final.mp4 --expect-duration <s> --audio --lufs -14 --max-end 1.5 --sheet chk.jpg` → semua PASS: tiada frame beku > 0.4s (jeda sengaja: `--allow-still <masa>`), end card ≤ 1.5s, durasi betul, audio ada, loudness -14 ±1. Sebut nombor dalam mesej akhir satu baris.

## Hantar

SendUserFile `Final.mp4` + `Final.srt` + `cover.jpg` dalam satu panggilan (`tech.md` §7) + caption 1 baris (mode/style, resolusi, durasi). Mesej akhir ringkas:
- Effect apa masuk mana, cold open & loop, take/ayat dibuang.
- Satu perkara perlu confirm (perkataan tak jelas / handle / screenshot kurang).
- Tawar satu style lain untuk dicuba atas video sama, dan versi tanpa caption (untuk repost/translate).
- Kos servis berbayar + baki (tiada → cakap tiada).

Simpan versi v1, v2... Terima note satu baris satu perubahan dengan masa → ubah, snapshot, hantar versi baru. Tawar simpan effect yang menjadi sebagai template.

## Peraturan ringkas

- Caption: 1 utama + 1 emphasis (+1 khas hook/CTA). Text belakang badan ≥2 font, dipasang dengan `scripts/fonts.py` (class `.f-<nama>` pada setiap big word), set berbeza setiap video.
- B-roll bukan pada hook & CTA, max ~40% durasi, campur 2-3 layout, masuk/keluar dengan J/L-cut.
- Punch-in pada setiap cut, max 1 setiap ~3-5s. Tak pernah potong dalam perkataan.
- Loudnorm sekali sahaja (masa mix akhir).
- Music/SFX hanya dari fail user atau jana sendiri; jangan muat turun bahan berhak cipta. Jangan logo brand sebenar tanpa fail user.
- Image prompt untuk user generate sendiri secara default; connector image-gen berbayar (cth OpenRouter) hanya bila user minta DAN connector tu ada, laporkan kos + baki.
