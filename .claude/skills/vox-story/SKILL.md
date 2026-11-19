---
name: vox-story
description: Vox Story (Nexabot + Gemini Voice + QA Gatekeeper) - produce captivating story-driven narrative videos using the full-color Vox Colored vintage diorama style for ANY topic (legendary folklore, true crime, corporate scandals, viral current events, mystery, survival stories, and biographies) with dramatic pacing, expressive Google Gemini voices (Aoede/Fenrir), and automated "jana sampai sempurna" quality control.
argument-hint: "[story subject, e.g. Sumpahan Mahsuri, Kisah Kejatuhan Enron, Misteri MH370, Hang Tuah vs Hang Jebat]"
---
> [!IMPORTANT]
> **Mandatory Daily Nexabot API Check:** Before generating any assets with Nexabot, run:
> `bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" check`
> This verifies active endpoints, models, and pricing against https://nexabot.id/developers and /api/v1/modes.


# Vox Story (Narrative Storytelling in Vox-Colored Aesthetic)

**`/vox-story`** turns ANY subject into a dramatic, emotionally compelling narrative video using the **`vox-colored`** vintage paper diorama aesthetic (hand-tinted full-color, archival textures, layered cutouts with white keylines and red marker accents, deep 3D diorama space).

It is purpose-built for **storytelling across all genres**:
1. **Kisah Lagenda & Mitos:** Sumpahan Mahsuri, Hang Tuah & Hang Jebat, Puteri Gunung Ledang, Raja Bersiong, Sang Kelembai, Trojan War, Atlantis, Norse & Greek mythology.
2. **Isu Semasa & Skandal Sensasi:** Skandal 1MDB, kejatuhan Enron/Theranos, misteri kehilangan MH370, krisis kapal Titan, perang teknologi AI, fenomena viral global.
3. **Kisah Sebenar, Biografi & Misteri:** True crime, kisah kelangsungan hidup (*survival stories*), kisah jatuh bangun jutawan/tokoh, ekspedisi hilang di Amazon/Himalaya.

---

## The Vox Suite Division

| Skill | Focus | Visual Style | Default Voice |
|---|---|---|---|
| **`/vox`** | News, politics & economics explainers | Black & white archival diorama + giant stat numbers | English / Nexabot |
| **`/vox-colored`** | General explainers in color | Full-color hand-tinted vintage collage | English / Nexabot |
| **`/vox-history`** | Strict ancient battles, civilizations & Islamic history | Solemn monochrome archival diorama, strict religious guardrails | Google Gemini `Fenrir` |
| **`/vox-story`** | **Dynamic storytelling (legends, mysteries, true crime, current stories)** | **Full-color vintage diorama (`vox-colored`), rich palette, dramatic lighting** | **Google Gemini `Aoede` (folklore/drama) or `Fenrir` (epic/mystery)** |

---

## The 4-Beat Narrative Story Arc

Every `/vox-story` follows a proven dramatic storytelling structure:

```
[ BEAT 1: THE HOOK & MYSTIQUE (0s – 8s) ]
↳ Buka dengan misteri, soalan provokatif, atau detik ketegangan awal.
  (Contoh: "Sebuah pulau yang aman, tiba-tiba dilanda kutukan darah selama tujuh keturunan...")

[ BEAT 2: THE ASCENT & CHARACTERS (8s – 18s) ]
↳ Bina dunia, perkenalkan watak atau isu teras, dan timbulkan konflik yang mula meruncing.
  (Contoh: Fitnah mula berbisik di istana, dendam yang tersembunyi mula menyala.)

[ BEAT 3: THE CLIMAX & TURNING POINT (18s – 28s) ]
↳ Titik puncak konflik: pengkhianatan terbongkar, tragedi berlaku, atau detik takdir berubah.
  (Contoh: Tusukan keris yang mengalirkan darah putih, mengesahkan kebenaran yang terlambat.)

[ BEAT 4: THE ECHO & LEGACY (28s – 38s) ]
↳ Penyelesaian, kesan abadi, dan mesej mendalam yang meninggalkan kesan kepada penonton.
  (Contoh: Pulau itu sepi ditelan zaman, membuktikan bahawa fitnah lebih tajam daripada mata pedang.)
```

---

## Production Workflow (7 Steps)

### Step 1: Story Selection & Scripting
* **Mandatory Language Consistency Lock:** Tulis skrip penceritaan dramatik 100% mengikut bahasa tajuk/arahan. Jika tajuk Bahasa Melayu, skrip, VO, dan teks visual WAJIB 100% Bahasa Melayu baku (sarikata/caption JANGAN dimasukkan melainkan diminta secara eksplisit) (tiada rojak). Jika tajuk English, gunakan 100% English sepenuhnya.
* Gunakan gaya penceritaan yang bertenaga, bersahaja tetapi puitis dan penuh emosi.
* Jumlah kata: ~70–90 patah perkataan (sesuai untuk video pendek 35–45 saat).
* Simpan dalam `script.json`.

### Step 2: Voiceover Generation
Pilih suara mengikut nada cerita:
* **`Aoede`**: Kisah lagenda, mitos, cerita rakyat, drama beremosi (wanita ekspresif).
* **`Fenrir`**: Kisah misteri berat, peperangan epik, true crime, krisis mendalam (lelaki sinematik).
* **`Fola`**: Kisah inspirasi, perjuangan tokoh, kisah kemanusiaan (wanita jernih & mesra).
* **`Charon`**: Dokumentari penyiasatan, skandal korporat, penceritaan neutral (lelaki dalam & berwibawa).

Jana dengan skrip. VO Melayu guna arahan di bawah. VO Inggeris guna Nexabot TTS (`Fola` tiada dalam senarai suaranya, jadi guna `Leda`):
`bun "${NEXABOT_TS:-$ROOT/vendor/Motion_as_kit/nexabot/nexabot.ts}" tts "<teks>" --voice Aoede --out audio/chapter_01.wav`

```bash
python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/gemini_tts.py" --file script.txt --voice Aoede --out audio/chapter_01.wav
```
Tambah ruang nafas 0.8s di awal dan 2.5s di akhir melalui `pad_audio.py` untuk mengelakkan cut tergantung.

### Step 3: Segmentation & Timeline Alignment
* Bahagikan skrip kepada 5–7 babak dramatik mengikut jeda ayat.
* Pastikan setiap babak menonjolkan satu visual hero yang kuat.
* Simpan dalam `segments.json` dan `plan.json`.

### Step 4: Prompt Engineering Gaya Vox-Colored (Gate 1)

Setiap klip imej menggunakan formula gaya **`vox-colored`**:

```text
SHOT: [Deskripsi pembukaan babak, watak hero, latar belakang, dan 1 teks label dramatik].
STYLE: Vintage documentary collage in hand-tinted color, built as a deep 3D paper diorama.
Materials: photo cutouts of characters, landscapes and artifacts printed as colorized vintage photographs
(soft hand-tinted color, warm skin tones, faded teal, olive, ochre and brick tones, visible halftone dots and print grain),
each with a rough white keyline and an offset hot-red marker stroke behind it; aged cream ledger paper, yellowed newsprint,
color-tinted archival maps, torn paper edges. Headline caps in ink black on torn cream labels, or white on hot-red torn labels,
with hand-drawn red underlines and arrows. Palette: aged cream #EFE4CC, archival tan #C9BB9C, ink black #1A1A1A,
hot red #C0392B, mustard #D9A441, faded teal #4F8A8B, cobalt accent #2F5DA8.
Deep 3D diorama, strong shallow depth of field, foreground elements close to the lens.
Single cinematic full-bleed 16:9 frame, edge-to-edge, no cardboard box borders, no outer frames, no watermark.
```

**Sekatan Larangan (AVOID Block):**
```text
AVOID: NO random numbers, NO barcode labels, NO floating code tags (no '24014D'),
NO cardboard shoebox outer frames, NO modern anachronisms in historical/legendary tales,
NO plastic CG, no morphing or melting bodies, no moving mouths or lip-sync when unnarrated,
no typos (strict spelling lock), no watermarks, no music, no voice-over
```

**Kunci Teks (Text Lock):**
Jika ada teks label pada keratan kertas (contoh: tajuk lagenda, tahun, nama watak), nyatakan:
`This frame has exactly ONE text element, '<EXACT_TEXT>', spelled exactly: [eja huruf demi huruf]. NO other text, NO typos.`

### Step 5: Keyframe Generation & Image Audit (Gate 2)
* Jana imej keyframe melalui Nexabot:
  ```bash
  python generate.py images <run_dir>
  ```
* Semak setiap gambar:
  - Warna vintaj ceria dan harmoni (*hand-tinted color*).
  - Watak dan objek bertepi putih (*white keyline*) kemas.
  - Ejaan teks tepat 100%.
  - Tiada bingkai kotak kadbod atau kesan pelik.
* Jika ada sebarang cacat cela: Perkemas prompt dan jana semula serta-merta ("Jana Sampai Sempurna").

### Step 6: Video Clip Generation & 1-FPS Strip Audit (Gate 3)
* Jana video melalui Nexabot Veo (`sfv`):
  ```bash
  python generate.py videos <run_dir>
  ```
* Ekstrak jalur 1 FPS:
  ```bash
  python "${MOTION_KIT:-$ROOT/vendor/Motion_as_kit}/qc_gatekeeper.py" strip <clip_path.mp4>
  ```
* Semak saat 4 hingga 10 untuk memastikan tiada perubahan bentuk aneh (*morphing*), tiada teks hallucinated, dan tiada mulut menyanyi/bercakap tanpa suara.

### Step 7: Master Assembly, Outro & Google Drive Sync (Gate 4)
* Cantum video melalui `assemble_perfect.py`:
  - Masuk dari hitam (*fade-in* 0.5s).
  - Cantuman tepat pada jeda ayat.
  - **Outro settle hold 2.5s – 3.0s** selepas kata terakhir tamat.
  - **Visual fade-out ke hitam 1.8s**.
  - **Muzik fade-out 2.5s**.
  - Penapis pemadam watermark Gemini (*delogo*).
* Selaraskan projek secara automatik ke Google Drive:
  - Direktori: `AI VIDEO -> <MONTH YYYY> -> <PROJECT TITLE>`.
