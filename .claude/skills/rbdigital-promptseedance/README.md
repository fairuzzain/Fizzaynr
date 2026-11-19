# Seedance Prompt Writer

> **Dalam repo Fizzaynr:** skill ni dah disesuaikan — gambar guna ChatGPT images (`codex-image/openai_image.py`), VO/muzik/klip guna Nexabot, output dalam `runs/<skill>/<slug>`. Lihat seksyen *Repo setup* dalam `SKILL.md`. Keperluan di bawah ialah untuk versi asal.


Tulis prompt video Seedance 2.5 yang siap copy-paste: logline, style, character lock, beat ikut saat dengan kamera + bunyi. Kalau ada watak, dia bagi prompt **character sheet** dulu supaya watak konsisten.

## Keperluan
- Claude (mana-mana plan). Takde code / connector diperlukan.
- Akaun Seedance 2.5 (Dreamina / CapCut / platform lain yang ada Seedance) untuk generate video.
- Image generator pilihan kau (Google Flow, ChatGPT, Gemini dll.) untuk character sheet.

## Cara install
- **Claude (claude.ai / app):** upload fail `.zip` ni sebagai custom skill dalam bahagian Skills di Settings. Pastikan code execution / file creation ON.
- **Claude Code:** extract folder ni ke `~/.claude/skills/` (nama folder kekal sama).

Lepas install, tak payah panggil nama skill — cakap je apa kau nak (contoh di bawah), Claude akan guna skill ni sendiri. Boleh juga taip `/rbdigital-promptseedance`.

## Contoh guna
- "Buat prompt seedance 15s, budak lelaki kejar layang-layang atas bumbung"
- "Prompt seedance 30s iklan kedai kopi, gaya sinematik"
- (Upload hasil video) "Video ni watak bertukar tengah jalan, betulkan prompt"

## Nota
- Prompt tak pernah sebut nama brand / watak / studio berhak cipta — semua dijadikan description generik (selamat untuk komersial).
- Set aspect ratio dalam tool Seedance sendiri; prompt tak ubah ratio.

## Lesen
Lihat `LICENSE.txt`. Output (video/prompt) milik kau, boleh guna komersial. Fail skill tak boleh dijual atau dikongsi semula.

Support: RB Digital Solution
