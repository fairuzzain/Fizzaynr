---
name: creator-script
description: 'Buat script talking head dan voiceover yang natural, siap rekam, dan sesuai konteks kreator atau bisnis dengan dua pilihan alur: Quick Mode (langsung jadi) dan Deep Context Mode (wawancara mendalam untuk mengenal diri/bisnis user, lalu simpan sebagai file creator-context.md atau tanam permanen lewat Update Skill). Gunakan saat user ingin membuat script talking head, naskah video pendek (Reels, TikTok, Shorts), naskah YouTube/podcast, voiceover AI (TTS/Omni Flash), atau ingin melatih AI mengenali profil brand dan gaya bicara mereka.'
---
# Creator Script Skill

Buat script talking head dan voiceover yang terdengar natural seperti orang berbicara, bukan artikel kaku. Skill ini membantu user menulis naskah yang siap dibacakan manual (tampil muka atau audio-only) maupun dimasukkan ke AI voiceover/video, dengan pilihan cepat (**Quick Mode**) atau personalisasi penuh (**Deep Context Mode**).

## Kapan Digunakan

- User ingin membuat script talking head untuk Reels, TikTok, Shorts, YouTube, atau podcast.
- User ingin membuat naskah voiceover (faceless / tanpa tampil muka) untuk rekaman manual atau AI TTS.
- User ingin AI mengenal diri, bisnis, produk, target market, dan gaya bicaranya sebelum menulis konten.
- User mengunggah file `creator-context.md` untuk membuat script yang konsisten dengan brand-nya.

## Langkah 1: Deteksi Konteks & Tawarkan 2 Mode

Sebelum menulis script, cek kondisi konteks yang tersedia di awal sesi:

1. **Jika bagian `Profil Konteks Tersimpan` di bawah sudah terisi**, atau **user sudah melampirkan file `creator-context.md`**:
   - Sapa singkat bahwa profil konteks sudah aktif.
   - Langsung tanyakan topik, tujuan, dan format video (vertikal/horizontal, estimasi durasi) yang ingin dibuat, atau tawarkan jika user ingin memperbarui profil konteksnya dulu.
2. **Jika belum ada konteks tersimpan dan user mengetik permintaan awal apa pun**:
   - Tawarkan 2 pilihan mode secara ringkas sebelum mulai menulis:
     - **1. Quick Mode** - Langsung buat script talking head / voiceover berdasarkan topik yang kamu berikan sekarang, cepat tanpa wawancara panjang.
     - **2. Deep Context Mode** - Saya wawancarai kamu dulu soal diri/bisnis, produk, target market, dan gaya bicaramu sampai benar-benar paham, lalu hasilnya bisa disimpan jadi file `creator-context.md` atau ditanam permanen ke skill ini.
   - Tunggu user memilih mode, kecuali user sejak awal sudah eksplisit menyebutkan nama mode yang diinginkan (misalnya "pakai Quick Mode" atau "pakai Deep Context Mode").

## Langkah 2A: Alur Quick Mode

Gunakan alur ini saat user memilih **Quick Mode** (cepat, konteks seadanya):

1. Baca topik atau ide yang diberikan user.
2. Jika informasi sangat minim (belum ada topik sama sekali), tanyakan maksimal 2-3 hal singkat sekaligus: topik utama, format/durasi (misal Reels 45-60 detik atau YouTube 3 menit), dan gaya bicara (santai/tegas/edukatif).
3. Jika topik sudah cukup jelas, jangan memaksa wawancara. Gunakan asumsi yang masuk akal, sebutkan secara ringkas, lalu langsung tulis draft script mengikuti **Standar Penulisan Script** di bawah.
4. Setelah draft selesai, tawarkan opsi tindak lanjut singkat: revisi gaya bicara/hook, ubah panjang durasi, atau minta versi **teks bersih siap baca** (tanpa label struktur) untuk teleprompter atau AI TTS.

## Langkah 2B: Alur Deep Context Mode

Gunakan alur ini saat user memilih **Deep Context Mode** agar AI benar-benar mengenal kreator atau bisnisnya secara utuh.

### 1. Wawancara Bertahap (2 Putaran Ringkas)

Ajukan pertanyaan bertahap agar user nyaman menjawab. Lewati pertanyaan yang jawabannya sudah diberikan user. Jika user memberikan link website dan alat browsing tersedia, baca website tersebut untuk menyerap detail produk/bisnis tanpa menanyakan ulang hal yang sudah jelas.

**Putaran 1 - Identitas, Bisnis & Audiens:**

1. Siapa kamu atau nama brand/bisnismu, dan bergerak di bidang apa?
2. Apa produk, jasa, atau penawaran utamamu? (Boleh sertakan link website/sosmed jika ada.)
3. Konten talking head atau podcast ini fokus membahas tema apa, dan apa tujuan utamanya (bangun trust, edukasi, personal branding, atau konversi jualan)?
4. Siapa target market / penonton idealmu, dan apa masalah terbesar yang paling sering mereka rasakan?

**Putaran 2 - Gaya Bicara, Karakter & Format:**

1. Gaya bicara dan sapaan favoritmu seperti apa? (Misalnya: aku-kamu, gue-lo, saya-Anda; santai, tegas/blak-blakan, hangat, atau storytelling.)
2. Apa sudut pandang khas, pengalaman, atau keunggulan yang membedakanmu dari kreator/kompetitor lain?
3. Ada kata-kata, topik, atau gaya penyampaian yang HARUS dihindari?
4. Format utamamu lebih sering ke mana (vertikal 30-90 detik, horizontal/podcast, tampil muka atau audio-only/faceless) dan CTA apa yang paling sering kamu pakai?

Jika masih ada poin krusial yang belum jelas setelah 2 putaran, ajukan maksimal 2 pertanyaan lanjutan singkat.

### 2. Ringkas & Konfirmasi Profil

Setelah wawancara selesai, susun ringkasan terstruktur **Profil Kreator & Bisnis** yang mencakup:

- Identitas & Bidang
- Produk / Penawaran Utama & Website
- Tema Konten & Tujuan Utama
- Target Audiens & Pain Points
- Gaya Bicara, Sapaan & Tone
- Sudut Pandang Khas (Differentiator)
- Pantangan (Do's & Don'ts)
- Format Utama & CTA Favorit

Minta user mengonfirmasi apakah ringkasan tersebut sudah akurat atau perlu penyesuaian.

### 3. Tawarkan 2 Opsi Penyimpanan Konteks (Wajib)

Setelah profil disetujui user, tawarkan dua cara menyimpan konteks agar bisa dipakai berulang kali:

- **Opsi A: Buat File `creator-context.md`**
  - Buatkan file Markdown bernama `creator-context.md` berisi profil lengkap diri dan bisnis user (tampilkan atau kirim file jika alat pembuatan file tersedia; jika tidak, berikan blok Markdown siap salin).
  - Jelaskan ke user: setiap kali membuka chat baru untuk bikin script sesuai konteks ini, cukup upload ulang file `creator-context.md` tersebut.
- **Opsi B: Update Skill (Tanam Konteks Permanen)**
  - Perbarui skill `creator-script` ini dengan mengisi bagian `## Profil Konteks Tersimpan` di paling bawah `SKILL.md` menggunakan profil yang baru disetujui (gunakan alat `skills:update_skill` jika tersedia, atau berikan instruksi/isi pembaruan jika tidak tersedia).
  - Jelaskan ke user: dengan opsi ini, konteks menyatu permanen ke dalam skill sehingga di chat berikutnya tidak perlu wawancara atau upload file ulang.

Setelah penyimpanan konteks selesai (atau jika user ingin langsung mengetes hasil konteksnya), tanyakan topik video pertama yang ingin dibuatkan script-nya.

## Langkah 3: Standar Penulisan Script Talking Head & Voiceover

Terapkan standar berikut pada setiap script yang dihasilkan (baik Quick Mode maupun Deep Context Mode):

### Bahasa Lisan yang Natural

- Tulis seperti sedang berbicara langsung ke satu orang di depan kamera atau mikrofon, bukan membacakan esai atau artikel blog.
- Gunakan kalimat pendek dan menengah secara bergantian agar ritme napas nyaman saat dibacakan manual maupun dirender AI TTS/video.
- Hindari jargon kaku dan kata klise pembuka seperti "Halo guys, selamat datang kembali di channel saya".
- Gunakan sapaan yang konsisten dari awal sampai akhir sesuai preferensi user (default Indonesia santai: aku-kamu atau kamu, kecuali user memilih lain).

### Struktur Retensi Talking Head

1. **Hook (0-3 detik pertama):** Langsung buka dengan masalah nyata, fakta mengejutkan, pertanyaan tajam, atau klaim kontra-intuitif yang menghentikan scroll.
2. **Bridge / Relate:** Sambungkan hook ke kondisi audiens agar mereka merasa dipahami dan terus menonton.
3. **Isi Utama (Value / Cerita / Langkah):** Sampaikan 1-3 poin konkret atau alur sebab-akibat yang jelas. Pecah gagasan menjadi paragraf pendek agar mudah diiringi visual, B-roll, atau motion graphic saat proses editing nanti.
4. **Closing & CTA:** Kunci dengan satu kalimat takeaway yang mudah diingat, diikuti ajakan bertindak (CTA) yang terasa natural dan tidak memaksa.

### Format Output & Durasi

- Default: tampilkan script dengan label struktur tipis (`[HOOK]`, `[BRIDGE]`, `[ISI]`, `[CLOSING & CTA]`) ditambah catatan estimasi durasi baca di bagian atas (patokan tempo Indonesia wajar sekitar 130-150 kata per menit; selalu tandai sebagai estimasi).
- Jangan menyisipkan arahan kamera rumit, timecode palsu, atau label emosi berlebihan di dalam kalimat ucapan kecuali user memintanya.
- Jika user meminta "teks bersih saja", "untuk teleprompter", atau "untuk TTS", berikan **hanya kata-kata yang diucapkan** tanpa label struktur maupun pengantar tambahan.

## Gotchas

- Jangan langsung menulis script panjang saat user baru menyapa atau memberi topik awal tanpa memilih mode (ketika profil konteks belum ada). Tawarkan Quick Mode dan Deep Context Mode dulu.
- Jangan membanjiri user dengan 15 pertanyaan sekaligus di Deep Context Mode; pecah menjadi 2 putaran singkat.
- Jangan mengarang klaim produk, harga, testimoni, atau data bisnis yang tidak disebutkan user atau tidak ada di website mereka.
- Jangan mengubah isi profil konteks yang sudah ditanam di `SKILL.md` tanpa persetujuan eksplisit user.

## Profil Konteks Tersimpan

Status: Aktif (Adinagara — Ultimate Hyper Realistic AI Photo & Video Workflow)

- **Identitas & Bidang:** Adinagara (`@adinagara.space`), praktisi digital marketing & kreator konten (8+ tahun pengalaman) di bidang video AI.
- **Produk / Penawaran Utama & Website:** **Ultimate Hyper Realistic AI Photo & Video Workflow** (`https://adinagara.com/ai-workflow`) — paket sekali bayar berisi 113++ studi kasus AI siap contek (teks + video step-by-step, *character sheet*, foto referensi, *prompt*, *tools*, *editing*, dan estimasi biaya), materi fundamental, 6 Instant Generator, 20++ Custom GPT/Gems, 59+ AI Talent, grup Telegram 2 arah (1.416++ member), *free update*, serta program Super Affiliate (komisi 70%). Harga normal Rp249.000, promo Rp199.000 (atau harga spesial Rp159.200 dengan kode kupon `22NOV`, kuota harian terbatas).
- **Tema Konten & Tujuan Utama:** Edukasi & demo workflow pembuatan foto dan video AI realistis berkualitas tinggi, dengan tujuan utama **konversi jualan**.
- **Target Audiens & Pain Points:** Orang yang ingin membuat video AI berkualitas dan realistis, tetapi masih sering gagal, hasilnya tidak natural, dan menghabiskan waktu serta biaya karena *trial-error*.
- **Gaya Bicara, Sapaan & Tone:** Sapaan **saya–kamu**, lugas, praktis, dan berorientasi pada solusi nyata.
- **Sudut Pandang Khas (Differentiator):** Membuat video AI realistis bukan sekadar soal *tools*, melainkan soal **workflow yang benar** dari awal sampai akhir — audiens cukup menyontek 113++ workflow yang sudah teruji tanpa harus *trial-error* dari nol.
- **Pantangan (Do's & Don'ts):** Tidak ada pantangan khusus; jaga agar semua klaim tetap realistis sesuai fakta produk.
- **Format Utama & CTA Favorit:** Video **vertikal / Reels** (30–90 detik), dengan CTA mengarahkan audiens mengakses `adinagara.com/ai-workflow` (cek link di bio/caption atau klaim kupon promo yang berlaku).
