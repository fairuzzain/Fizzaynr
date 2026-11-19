# Toon Series Video

> **Dalam repo Fizzaynr:** skill ni dah disesuaikan — gambar guna ChatGPT images (`codex-image/openai_image.py`), VO/muzik/klip guna Nexabot, output dalam `runs/<skill>/<slug>`. Lihat seksyen *Repo setup* dalam `SKILL.md`. Keperluan di bawah ialah untuk versi asal.


Video kartun, explainer, dokumentari atau drama (1–3 minit) dari klip AI: Claude tulis skrip VO, prompt character sheet, prompt gambar + video 10s setiap scene. Kau generate klip, upload, Claude edit penuh: potong ikut VO, punch-in, crossfade, caption, muzik, SFX. 30 style — dari kartun sampai realistik (sinematik, arkib dokumentari, reenactment sejarah, true crime, drama keluarga Melayu, seram kampung), dengan preset Explainer / Dokumentari / Drama.

## Keperluan
- Claude dengan code execution (ffmpeg + Python; numpy hanya untuk `music.py`, ada alternatif tanpa numpy).
- Video generator yang buat klip ≤10s dari gambar (Google Flow / Gemini / Seedance dll.).
- **Pilihan:** connector ElevenLabs untuk VO sahaja. Takde → Claude bagi skrip VO, kau generate MP3 sendiri.
- **SFX percuma:** Claude jana bunyi asas dengan code (`scripts/sfx_gen.py`: angin, hujan, room tone, bandar, crowd, cengkerik, boom, whoosh, chime, crackle filem). Bunyi spesifik (ayam berkokok, sorakan, kuali) kau download percuma dari Pixabay Sound Effects, Freesound (CC0) atau Mixkit. Tiada kos kredit untuk SFX.

## Cara install
- **Claude (claude.ai / app):** upload fail `.zip` ni sebagai custom skill dalam bahagian Skills di Settings. Pastikan code execution / file creation ON.
- **Claude Code:** extract folder ni ke `~/.claude/skills/` (nama folder kekal sama).

Lepas install, tak payah panggil nama skill — cakap je apa kau nak (contoh di bawah), Claude akan guna skill ni sendiri. Boleh juga taip `/rbdigital-storyseries`.

## Contoh guna
- "Buat video kartun 1 minit pasal fotosintesis untuk budak, 16:9"
- "Dokumentari 2 minit sejarah Melaka, style arkib"
- "Drama pendek 1 minit pasal ayah dan anak, style drama keluarga Melayu"
- (Upload semua klip) "Ni klip dia, edit jadi video"

## Nota
- 30s ≈ 4 klip, 1 min ≈ 7 klip, 2 min ≈ 13 klip.
- Script render (`scripts/toon_build.py`), SFX percuma (`scripts/sfx_gen.py`) dan muzik placeholder (`scripts/music.py`) dah dibundle.
- `toon_build.py` kini jalan di Windows (path subtitle, font folder), sokong lower-third tahun/tempat untuk dokumentari, dan kekalkan puncak audio bawah -1 dB.

## Lesen
Lihat `LICENSE.txt`. Output (video/prompt) milik kau, boleh guna komersial. Fail skill tak boleh dijual atau dikongsi semula.

Support: RB Digital Solution
