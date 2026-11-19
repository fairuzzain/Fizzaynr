# Craft Parallax Video

Video parallax 3 lapis (background + watak + foreground) gaya kraf: paper cut, claymation, 3D animated, felt, fabric, knit, kayu, miniature, origami, cardboard dan lain-lain. Kamera bergerak, depth of field, partikel, transition, caption, muzik + SFX — semua dirender dengan script yang dah dibundle.

## Keperluan
- Claude dengan code execution (Python: Pillow, numpy, scipy — biasanya dah ada).
- Image generator pilihan kau (Google Flow, ChatGPT, Gemini dll.) — Claude bagi prompt, kau generate & upload.

## Cara install
- **Claude (claude.ai / app):** upload fail `.zip` ni sebagai custom skill dalam bahagian Skills di Settings. Pastikan code execution / file creation ON.
- **Claude Code:** extract folder ni ke `~/.claude/skills/` (nama folder kekal sama).

Lepas install, tak payah panggil nama skill — cakap je apa kau nak (contoh di bawah), Claude akan guna skill ni sendiri. Boleh juga taip `/rbdigital-parallax`.

## Contoh guna
- "Buat video paper cut parallax 30s pasal kisah semut dan belalang"
- "Video claymation parallax 15s untuk promo kedai kek"
- "Diorama felt, 9:16, mood ceria"

## Nota
- Background gambar watak sengaja hijau/magenta supaya cut-out bersih — jangan tukar.
- 9 font dibundle dalam `fonts/` (lesen dalam `fonts/licenses/`).

## Lesen
Lihat `LICENSE.txt`. Output (video/prompt) milik kau, boleh guna komersial. Fail skill tak boleh dijual atau dikongsi semula.

Support: RB Digital Solution
