# Poster Zoom Video

Upload satu gambar (poster, infografik, slide) → jadi video explainer: spotlight, tajuk 'slam', zoom satu-satu point, VO, muzik. Gambar asal TAK dilukis semula — setiap frame crop dari gambar kau.

## Keperluan
- Claude dengan code execution (ffmpeg + Python dah ada dalam sandbox).
- **Pilihan:** connector ElevenLabs untuk VO automatik. Takde connector → Claude render tanpa VO dan bagi skrip untuk kau generate sendiri.

## Cara install
- **Claude (claude.ai / app):** upload fail `.zip` ni sebagai custom skill dalam bahagian Skills di Settings. Pastikan code execution / file creation ON.
- **Claude Code:** extract folder ni ke `~/.claude/skills/` (nama folder kekal sama).

Lepas install, tak payah panggil nama skill — cakap je apa kau nak (contoh di bawah), Claude akan guna skill ni sendiri. Boleh juga taip `/rbdigital-posterzoom`.

## Contoh guna
- (Upload poster) "Buat zoom video guna gambar ni"
- (Upload infografik) "Gerak-gerak gambar ni, ada VO BM"
- "Buat versi 9:16 pulak"

## Nota
- Gambar resolusi tinggi (≥2000px lebar) bagi hasil paling tajam.
- VO ElevenLabs guna kredit akaun kau; Claude akan report kos.

## Lesen
Lihat `LICENSE.txt`. Output (video/prompt) milik kau, boleh guna komersial. Fail skill tak boleh dijual atau dikongsi semula.

Support: RB Digital Solution
