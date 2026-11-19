# Library: caption, font, effect, icon, B-roll

## Caption Library (satu sistem: 1 utama + 1 emphasis, +1 khas hook/CTA)

**Style utama** untuk ayat biasa. **Style emphasis** untuk punch word / nombor / soalan: sebaik-baiknya dari keluarga font sama dengan utama, beza warna/saiz/box (contoh utama Bold Outline + emphasis Box Highlight). **Style khas** (pilihan) hanya untuk hook atau CTA. Tukar ikut seksyen, bukan setiap ayat. Style Menu yang ada caption sendiri (#7, #9, #21) = style utama.

| # | Style | Rupa | Bila guna |
|---|---|---|---|
| 1 | Bold Outline | Putih tebal, stroke hitam 12px, keyword kuning | Default ayat biasa |
| 2 | Karaoke Highlight | Semua perkataan nampak, perkataan semasa bertukar warna/membesar | Ayat panjang, tutorial |
| 3 | Word Pop | 1 perkataan sekali, scale 1.3->1 `E.snap` (6 f) | Hook, ayat laju, punch |
| 4 | Box Highlight | Keyword dalam kotak warna (bg kuning, teks hitam) | Keyword, harga, nombor |
| 5 | Neon Glow | Teks putih + glow warna brand | Tech/AI, mood malam |
| 6 | Pill Chip | Teks dalam pill gelap separa lutsinar | Clean/korporat, podcast |
| 7 | Typewriter | Huruf keluar satu-satu + cursor | Prompt, quote, definisi |
| 8 | Stacked Mixed Size | Baris atas kecil, keyword bawah besar 2x | Statement kuat, soalan |
| 9 | Handwritten | Caveat/Permanent Marker, sikit senget | Tips santai, personal |
| 10 | Gradient Fill | Teks gradient (kuning->oren) + stroke | "Wow", hasil, before/after |
| 11 | Shake/Glitch | Teks gegar + RGB split pendek | Masalah, "susah?" |
| 12 | Bounce Slide | Masuk dari bawah dengan bounce | CTA, senarai langkah |
| 13 | Serif Karaoke | Kotak brand kecil, serif 52px, perkataan belum sebut malap | Premium / editorial |

Contoh sistem: ayat biasa = Bold Outline, emphasis/nombor = Box Highlight, hook = Word Pop, CTA = Bounce Slide. Shake/Glitch hanya untuk 1-2 perkataan masalah, bukan seksyen penuh.
Posisi: y ≈ 1150-1320, 2-4 perkataan (BM perkataan panjang → max 3), tak tutup muka/mulut. Line break ikut frasa, bukan potong separuh frasa.

## Font Library (text belakang badan / headline; 2-3 font)

Semua dari `@fontsource/<nama>`. Satu font utama, satu kontras untuk perkataan emosi/twist, satu (pilihan) untuk hook/CTA.

| Font | Mood | Sesuai untuk |
|---|---|---|
| montserrat (900) | Moden, kemas | Default |
| anton | Tinggi, padat, berita | Perkataan panjang (BERJAM-JAM) |
| bebas-neue | Sinematik | Statement, tajuk filem |
| league-gothic | Sangat padat | Perkataan sangat panjang |
| archivo-black | Tebal, kuat | Punch word (JIMAT!, SEKARANG) |
| oswald | Tegas | Fakta, nombor |
| dela-gothic-one | Tebal gaya anime | Hook dramatik |
| rubik-mono-one | Geometri, tech | AI/tech |
| bangers | Komik | Lawak, WOW, BOOM |
| luckiest-guy | Comel, bulat | Santai, fun |
| titan-one | Bulat tebal | Produk, promo |
| righteous | Retro futuristik | Tech, gaming |
| black-ops-one | Stencil | Cabaran, "STOP!" |
| permanent-marker | Marker | Personal, tips, scrapbook |
| caveat | Tulisan tangan | Nota kecil, quote |
| special-elite | Typewriter | Documentary |
| vt323 | Pixel | VHS |
| playfair-display (900 italic) / instrument-serif | Elegan | Premium, editorial, kahwin, takaful |
| inter-tight (800) | Bold sans condensed | Penegasan editorial |
| bricolage-grotesque (800) | Moden indie | Brand kreatif |
| poppins (900) | Bulat moden | Corporate friendly |

Contoh mix: Hook "MINIT?!" = dela-gothic-one, biasa = anton, emosi "SUSAH?" = bangers, CTA "JOM!" = archivo-black.

**Set font siap (pilih ikut mood, TUKAR set setiap video baru):**

| Set | Biasa | Emosi / twist | Hook / CTA | Mood |
|---|---|---|---|---|
| A Viral | anton | bangers | dela-gothic-one | Lawak, hook kuat |
| B Premium | inter-tight:800 | playfair-display:900i | bebas-neue | Takaful, kewangan, kahwin |
| C Personal | archivo-black | permanent-marker | caveat | Tips, cerita, vlog |
| D Tech | rubik-mono-one | righteous | league-gothic | AI, app, gaming |
| E Berita | oswald | black-ops-one | anton | Fakta, amaran, "STOP!" |
| F Fun | titan-one | luckiest-guy | bangers | Produk, promo, santai |
| G Editorial | bricolage-grotesque:800 | instrument-serif | inter-tight:800 | Brand kreatif, edu |

**Wajib:** font betul-betul dipasang dengan `scripts/fonts.py` (lihat `tech.md` §0). Kalau tak dipasang, browser jatuh ke Poppins dan SEMUA perkataan nampak sama — ini punca "font sama je".
Saiz: lebar ≈ 0.68 × fontSize × bilangan huruf (Montserrat); anton/bebas/league-gothic ~0.45; dela-gothic-one ~0.85. Mesti muat 1000px. Sahkan dengan snapshot.

## Effect Library (ikut makna ayat, semua style)

| Bila dia sebut… | Effect |
|---|---|
| app/tool lama yang dia tak guna ("tak guna CapCut") | Ikon app rekaan (kotak bucu + huruf) muncul pop, garis merah pangkah `stroke-dashoffset` 0.25s + pop |
| arahan / prompt | Prompt box: kotak gelap/krim, header "✦ PROMPT AI", teks menaip + cursor, chips (9:16, Voiceover, Caption), butang GENERATE ✨, cursor SVG klik + percikan 6 titik, tick ✓ + chime |
| proses / "AI jana / dia render" | AI generating card: "🤖 AI sedang jana..." + progress bar + % counter (proxy tween `onUpdate`), label SCRIPT/VISUAL/VIDEO jadi hijau; atau blur BG + kad timeline (playhead bergerak) / kad fail "IMG_1234.MP4 · 1:16" |
| masa / durasi / nombor | Countdown chip ⏱ (proxy tween hh:mm:ss, border hijau bila habis) atau counter besar + tick SFX |
| "raw / take teruk / sebelum" | Footage dalam phone frame kecil (scale 0.4) + pill merah condong "BAD TAKE" (boleh frame dalam frame mengecil); before/after (BERJAM-JAM dipotong → MINIT JE) |
| "tak payah / tak pun" | Stamp "TAK PUN!" border hijau rotate -6deg, scale 3→1 power4.in + flash + shake |
| senarai / langkah | Checklist pill dengan strike merah / tick, step badge, Bounce Slide caption |
| "ramai orang / viral" | Video wall grid 3x4 thumbnail scroll perlahan atas latar brand |
| "plan / storyboard / sistem" | Kad dokumen gelap Ken Burns zoom ke satu baris, highlight kotak emas |
| perkataan kuat / emosi | Text behind head (font kontras, Font Library) |
| "lagi besar / upgrade" | Tajuk campur sans+serif + pill kecil satu-satu ("THAT'S · JUST · ONE · MORE") |
| "gelap / moody / terang" | Mood per seksyen (SKILL.md Asas komposisi) |
| "komen / link / follow" | Follow tap (butang merah "+ FOLLOW" → klik → "✓ FOLLOWING" + percikan), kad profile CTA |

Perlu screenshot / screen recording sebenar → minta dalam storyboard; tiada → bina versi rekaan generik dalam HTML. Lower third nama + handle kalau ada dalam CLAUDE.md.

## Icon sheet (style 6, preset D)
- Default: tulis SATU prompt icon sheet 4x4 (16 icon) dan jana sendiri dengan ChatGPT images: `python "$IMG" --prompt "<template>" --out "$R/icons/sheet.png" --aspect 1:1 --width 2048` (Nexabot `img --aspect 1` kalau gagal 2 kali). User boleh upload sheet sendiri.
- Template: `A sprite sheet of 16 separate 3D icons arranged in a clean 4x4 grid, glossy stylized 3D cartoon render, soft studio lighting, vibrant saturated colors, each icon isolated with wide empty spacing, plain pure white background (#FFFFFF), no ground shadows, no reflections, no text, no labels, no borders, no overlapping. Icons in order, row by row: 1. ... 16. ... Every icon fully visible, centered in its grid cell, crisp edges.` (Background putih kosong + takde bayang supaya cutout bersih.)
- Cutout icon: JANGAN AI remove-background (buang bahagian putih dalam icon). Guna **flood-fill putih dari tepi setiap cell** (whiteness distance < 40, alpha MinFilter 3 + GaussianBlur 1.2), crop bbox, pad segi empat, 400x400 PNG `icons/NN.png`. Contact sheet atas bg gelap untuk QA.

## B-roll (preset E / add-on)

**Bila:** cerita masalah/situasi, contoh/proses, hasil/before-after, senarai. BUKAN pada hook 2s pertama dan CTA (muka untuk trust/connect). Max ~40% durasi; setiap shot 1.2-3s; tukar ikut beat.

| Layout | Rupa | Bila |
|---|---|---|
| Full | B-roll penuh, suara jalan, caption kekal | Cerita masalah |
| Split | B-roll atas 55%, muka bawah 45% | Explain proses |
| PIP | B-roll penuh, muka bulatan 260px atas kanan (border kuning) | Demo screen |
| Montage | 3-4 gambar tukar laju ikut beat + flash putih 1 frame | Hasil |
| Card | B-roll dalam kad 85% lebar, tilt 3D, atas muka di-blur | Contoh, screenshot |

Treatment: Ken Burns (1.0→1.12 + pan), masuk whip/slide 0.2s + whoosh, keluar cut. Masuk/keluar guna J/L-cut: gambar B-roll masuk 0.1-0.2s SELEPAS ayat cerita mula (atau keluar 0.1-0.2s selepas muka dah bercakap semula), bukan tepat atas sempadan ayat. Masalah = desaturate + vignette; penyelesaian = terang + glow.

Sumber:
1. **ChatGPT images (default, aku jana):** SATU sheet 3x3 (9 frame 9:16), `python "$IMG" --prompt "<template>" --out "$R/broll/sheet.png" --aspect 9:16 --width 2160`; atau satu gambar per shot (`--aspect 9:16 --width 1080`) bila perlu kualiti penuh. Template: `A 3x3 grid storyboard sheet of 9 separate vertical 9:16 photographic frames, consistent cinematic style, realistic photo, Malaysian setting, soft natural light, thin pure white gutters between frames, no text, no captions, no borders, no logos. Frames in order: 1. ... 9. ...` (Gutter putih nipis supaya senang potong.) Potong grid ikut baris/lajur hampir putih, scale cover ke 1080x1920.
2. **Klip Nexabot (bila shot perlu bergerak):** `bun "$NB" sfv "<gerak kecil + kamera perlahan>" --media "$R/broll/bNN.png" --ratio 2 --res 1080 --out "$R/broll/bNN"` (0.15 kredit/klip), guna `muted`.
3. **Code-only (percuma):** mockup HyperFrames: laptop/phone UI prompt menaip, timeline editor, chat bubble, dashboard, notification bertimbun, kalendar penuh.
4. **Klip user:** `trim` bahagian terbaik, `muted`.

Build: `#broll` atas `#cam` bawah caption; setiap shot `<img>`/`<video muted>` `.clip` + data-start/duration. Split/PIP: `<video>` kedua (src sama, muted, data-media-start sama masa root) dalam container crop muka; video asal (audio) kekal main bawah. Text behind & icon OFF masa Full/Montage.
