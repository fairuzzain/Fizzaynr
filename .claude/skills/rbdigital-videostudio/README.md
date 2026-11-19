# RB Digital Video Studio

Studio video pendek 9:16 dengan 110 style — cerita, edu, data, hook, tech, jualan, seni, dan 10 style 3D sebenar (Three.js). Dua mode:
- **A) Code only** — semua visual dibina dengan code (HyperFrames), tak perlu gambar. Claude jana VO sekali.
- **B) Flow** — Claude bagi prompt gambar Google Flow, kau generate & upload, Claude edit.

## Keperluan
- Claude dengan code execution **dan akses network ke npm** (HyperFrames + Chrome headless untuk Mode A).
- Mode B: akses Google Flow (atau image generator lain) untuk gambar.

## Cara install
- **Claude (claude.ai / app):** upload fail `.zip` ni sebagai custom skill dalam bahagian Skills di Settings. Pastikan code execution / file creation ON.
- **Claude Code:** extract folder ni ke `~/.claude/skills/` (nama folder kekal sama).

Lepas install, tak payah panggil nama skill — cakap je apa kau nak (contoh di bawah), Claude akan guna skill ni sendiri. Boleh juga taip `/rbdigital-videostudio`.

## Contoh guna
- "Buat video" → Claude tunjuk menu mode + 110 style, kau jawab contoh "A 46"
- "Buat video 5 fakta jerung, style scrapbook, mode B"
- "Video promo produk 3D pusing, mode A"

## Nota
- ★ dalam menu = **5 signature style** (Komik/manga, Polaroid siasatan, Scrapbook sticker, Kinetic typography, Kad flip reveal) — paling banyak diuji, hasil paling konsisten.
- 105 style lain ada resipi penuh dan boleh dibina, tapi hasil mungkin perlu 1–2 pusingan tweak.
- Style 75 (Paper cut parallax) perlukan skill berasingan **Craft Parallax Video**. Tanpa skill tu, Claude cadang style alternatif.

## Lesen
Lihat `LICENSE.txt`. Output (video/prompt) milik kau, boleh guna komersial. Fail skill tak boleh dijual atau dikongsi semula.

Support: RB Digital Solution

## Kemaskini terbaru: Motion Pro + QA automatik
- **Easing berukur** (`references/motion.md`): preset `E.land / E.snap / E.exit / E.settle`, timing dalam frame. Masuk perlahan bila sampai, keluar laju, overshoot jarang, tiada apa membesar dari 0, gerak bukan fade.
- **Hard cut on motion** jadi default; transition besar hanya 2–3 momen penting.
- **`scripts/slop_lint.py`**: tangkap pattern "video AI" (label corner, counter 02/05, timecode, progress bar, typewriter, terlalu banyak fade/bounce) sebelum render. Ikut style: elemen yang memang signature style (contoh timecode CCTV) tak dikira salah.
- **`scripts/look.py`**: check MP4 sebenar lepas render: frame mati, end card terlalu lama, durasi, audio, loudness, contact sheet.
