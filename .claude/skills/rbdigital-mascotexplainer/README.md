# RB Digital Mascot Explainer

Video explainer / promo tanpa muka: motion graphic gaya editorial (krim & coklat, tajuk Anton, aksen serif italic merah, mockup app) + maskot kartun yang **mulut ikut suara** (Rhubarb lip-sync), SFX dan muzik lo-fi. 16:9 atau 9:16. Render dengan HyperFrames.

## Keperluan
- Claude dengan code execution (Claude app) atau Claude Code di PC/Mac.
- Python 3, Node 22+, ffmpeg, HyperFrames, Rhubarb — Claude pasang sendiri masa guna kali pertama. PC/Mac: run `SETUP-WINDOWS.bat` / `SETUP-MAC.command` dari kit setup RB Digital sekali untuk siap semua.
- Akaun ElevenLabs untuk VO (Claude bagi skrip, kau generate & upload MP3).

## Cara install
- **Claude app:** Settings → Skills → upload zip ni.
- **Claude Code:** extract ke `~/.claude/skills/` (Windows: `C:\Users\<nama>\.claude\skills\`).
Taip `/rbdigital-mascotexplainer` atau cakap je "buat video explainer dengan maskot".

## Maskot
- Default: maskot generik (dilukis dengan code).
- Maskot sendiri: Claude bagi 2 prompt gambar (pose + bentuk mulut), kau generate & upload, Claude siapkan pack. Lihat `references/mascot-pack.md`.

## Contoh guna
- "Buat video promo 16:9 untuk produk aku, CTA komen VIDEO"
- "Video Reels 9:16, 5 langkah guna ChatGPT, maskot aku"
