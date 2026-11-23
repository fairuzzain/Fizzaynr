---
name: vox
description: The ONE Vox video skill - Vox-style cinematic diorama explainer made with Nexabot (TTS, img keyframes, Veo sfv clips, ffmpeg cut). Use for ANY Vox request - "buat video gaya Vox", "vox video", "vox collage", "explainer video", "news video", "why does X happen". Points to the vox-video-nexabot skill.
argument-hint: "[story/topic, number of chapters 1-4]"
---

# Vox video (Nexabot, cinematic diorama)

> **Bahasa utama: Bahasa Melayu Malaysia.** Semua output skill ini (skrip, VO/TTS, dialog, caption,
> teks atas skrin, CTA, tajuk, kapsyen media sosial) dan semua soalan serta laporan kepada pengguna
> ditulis dalam Bahasa Melayu Malaysia: ejaan, kosa kata dan loghat Malaysia, bukan Bahasa Indonesia.
> Bahasa lain hanya jika pengguna memintanya. Prompt untuk model imej/video boleh kekal dalam Bahasa
> Inggeris, tetapi teks yang diucapkan atau dipaparkan di dalamnya tetap Bahasa Melayu. Peraturan ini
> mengatasi mana-mana default bahasa lain dalam fail ini. Lihat `CLAUDE.md` → Bahasa.

This is the only Vox skill. Do not use any vox-collage / vox-explainer / vox-diorama-axcel /
collage-broll skill even if one is still listed.

Read `${VOX_SKILL:-<repo root>/.claude/skills/vox-video-nexabot/SKILL.md}` in full and follow it exactly
(work from the repo root), passing on the user's arguments.

If that file does not exist (the black-and-white `vox-video-nexabot` skill is not in this repo yet),
say so in one line and offer `/vox-colored` (same pipeline, colored look) instead. Do not improvise
the black-and-white style from memory.
