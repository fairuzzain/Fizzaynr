# Talking Head Edit

> **Dalam repo Fizzaynr:** skill ni dah disesuaikan — gambar guna ChatGPT images (`codex-image/openai_image.py`), VO/muzik/klip guna Nexabot, output dalam `runs/<skill>/<slug>`. Lihat seksyen *Repo setup* dalam `SKILL.md`. Keperluan di bawah ialah untuk versi asal.


Upload video talking head (satu atau banyak take) → Claude potong dead air/filler/take buruk, transcribe, cadang edit penuh (Auto) atau kau pilih dari 85 style (text behind body, karaoke, split screen, editorial, orbit, bento grid, checklist, HUD, paper cut, halftone...). Caption campur, zoom, effect, B-roll, muzik → MP4 9:16.

## Keperluan
- Claude dengan code execution **dan akses network ke npm + pip** (untuk HyperFrames, Chrome headless, faster-whisper). Claude Code paling stabil untuk video panjang.
- Node 22+ (Claude install sendiri kalau tiada).
- **Pilihan:** image generator untuk icon sheet / B-roll (Claude bagi prompt). Mode code-only percuma.
- **Pilihan:** letak `CLAUDE.md` dalam folder video dengan nama, handle, warna brand, font, logo — Claude akan guna.

## Cara install
- **Claude (claude.ai / app):** upload fail `.zip` ni sebagai custom skill dalam bahagian Skills di Settings. Pastikan code execution / file creation ON.
- **Claude Code:** extract folder ni ke `~/.claude/skills/` (nama folder kekal sama).

Lepas install, tak payah panggil nama skill — cakap je apa kau nak (contoh di bawah), Claude akan guna skill ni sendiri. Boleh juga taip `/rbdigital-videoedit`.

## Contoh guna
- (Upload video) "Edit video ni, kau buat je"
- (Upload 3 take) "Gabung take terbaik, style 1 + 19"
- "Tunjuk menu style"

## Nota
- Video ≤ 90s paling laju. Video panjang ambil masa render lebih.
- Rakaman iPhone (HDR) ditukar ke SDR secara automatik supaya overlay tak hilang.

## Lesen
Lihat `LICENSE.txt`. Output (video/prompt) milik kau, boleh guna komersial. Fail skill tak boleh dijual atau dikongsi semula.

Support: RB Digital Solution

## Kemaskini terbaru: Motion Pro + QA automatik
- **Peraturan motion overlay**: preset ease `E.land / E.snap / E.exit / E.settle`, caption pop tanpa lantun berlebihan, tiada apa membesar dari 0, cut on motion, transition besar hanya 2–3 kali.
- **`scripts/slop_lint.py --profile talking-head`**: tangkap scale-from-0, overlay fade-heavy, bounce berlebihan, label corner/kicker sebelum render.
- **`scripts/look.py`**: check Final.mp4 sebenar: video beku, end card ≤ 1.5s, durasi, audio, loudness -14 LUFS, contact sheet.
- **Font text belakang badan betul-betul bertukar**: `scripts/fonts.py` pasang font dari Font Library (sebelum ni font tak dipasang, jadi semua jatuh ke Poppins). 7 set font siap ikut mood, set berbeza setiap video.
