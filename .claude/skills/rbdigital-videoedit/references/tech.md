# Tech: command & resipi teknikal

## 0. Setup (senyap)

```bash
W=<scratchpad>/edit; mkdir -p $W && cd $W
ffmpeg -version | head -1; node -v   # node 22+
which hyperframes || npm i -g hyperframes
hyperframes browser ensure           # WAJIB, kalau tak Chrome tiada
hyperframes doctor | tail -20
# scaffold kosong (pilihan): HYPERFRAMES_SKIP_SKILLS=1 hyperframes init edit --example blank --resolution portrait --non-interactive
npm i gsap@3.14.2 @fontsource/poppins@5.2.6 --no-save --silent
mkdir -p vendor fonts && cp node_modules/gsap/dist/gsap.min.js vendor/
cp node_modules/@fontsource/poppins/files/poppins-latin-{600,700,800}-normal.woff2 fonts/
pip install faster-whisper soundfile --break-system-packages -q
```
- **Windows / PC user (Claude Code):** check Python dulu: `python --version` (atau `py --version`). Kalau tiada, atau keluar mesej Microsoft Store:
  ```powershell
  winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
  ```
  Shell lama tak nampak PATH baru → guna path penuh `"$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"` (Git Bash: `"$LOCALAPPDATA/Programs/Python/Python312/python.exe"`) atau suruh user buka semula Claude Code. Kemudian `python -m pip install faster-whisper soundfile` (tanpa `--break-system-packages` di Windows). winget tiada / gagal → minta user install dari python.org (tick "Add python.exe to PATH") dan TUNGGU, jangan teruskan.
  ffmpeg tiada → `winget install -e --id Gyan.FFmpeg --scope user`. Node tiada → `winget install -e --id OpenJS.NodeJS.LTS`.
- **JANGAN fallback ke ASR English-only** (Parakeet, Vosk English, model `*.en`) untuk video BM/rojak: hasil salah dengar teruk. Kalau faster-whisper tak boleh jalan, betulkan Python dulu, atau guna sherpa-onnx whisper (§3c), dan sebut dalam satu baris.
- **Font text belakang badan / headline (WAJIB setiap video):** lepas pilih font mix, pasang dengan satu command:
  `python <skill>/scripts/fonts.py anton bangers dela-gothic-one` (pin berat/italic: `playfair-display:900i`, `inter-tight:800`).
  Ia tulis `fonts/fonts.css` dengan class `.f-<nama>` (contoh `.f-anton`). Tambah `<link rel="stylesheet" href="fonts/fonts.css">` dalam `<head>`, letak class pada SETIAP big word ikut peranan (biasa / emosi / hook-CTA). Script exit 1 kalau ada font gagal → ganti dengan font lain dari Font Library, JANGAN biar jatuh ke Poppins.
- Font lain dari npm `@fontsource/<font>`, copy `.woff2` ke `fonts/`. Tiada URL CDN / http luar dalam HTML.
- Hanya satu fail HTML root dengan `data-composition-id` dalam folder projek (pindah versi lama keluar, kalau tak lint error `multiple_root_compositions`).

## 1. Prep footage

1. Convert .mov iPhone (HEVC, banyak stream): `ffmpeg -i in.mov -map 0:v:0 -map 0:a:0 -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac take.mp4`
2. Horizontal 16:9 → reframe 9:16 dengan `crop` ikut posisi muka (dari frame sheet).
3. Grade + bersih audio + PAKSA SDR (iPhone = HLG HDR; kalau tak, renderer masuk mode HDR dan SEMUA overlay hilang). Audio: highpass + denoise ringan sahaja, TIADA loudnorm (buat sekali di §5/§6).
```bash
F="eq=contrast=1.06:saturation=1.08:gamma=1.03:brightness=0.01,colorbalance=rs=0.02:bs=-0.03:rm=0.01:bm=-0.02,curves=master='0/0.02 0.25/0.23 0.5/0.52 0.75/0.78 1/0.97',unsharp=5:5:0.35,vignette=PI/8"
ffmpeg -i take.mp4 -t <end> -vf "$F" -c:v libx264 -crf 16 -pix_fmt yuv420p -g 15 -r 30 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -bsf:v h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1 \
  -c:a aac -b:a 192k -af "highpass=f=70,afftdn=nf=-30" footage.mp4
```
- Grade ikut style: Documentary = saturation 0.8 + grain (`noise=alls=12:allf=t`) + curves pudar; Cinematic = teal-orange + crop letterbox 2.35:1; VHS = saturation 1.3 + `rgbashift=rh=4:bh=-4` + noise; Editorial = warm lembut, saturation 1.05, highlight turun sikit; lain = grade default atas.
- Footage dah terang/tepu (cahaya ring light, kulit dah merah) → kurangkan: saturation 1.0, buang `rs/rm`.
- **Skin check**: before/after satu frame dengan `hstack`, Read. Kemudian sample kawasan pipi/dahi:
```python
from PIL import Image; import numpy as np, colorsys
im=np.asarray(Image.open("after.png").convert("RGB")).astype(float)/255
r,g,b=im[Y0:Y1, X0:X1].reshape(-1,3).mean(0)   # kotak kecil atas pipi dari frame sheet
h,s,v=colorsys.rgb_to_hsv(r,g,b); print(round(h*360),round(s,2),round(r/g,2))
```
  Kulit natural: hue ~15-30°, saturation 0.25-0.5, R/G ≤ ~1.35. Hue < 12° (merah jambu) atau saturation > 0.55 (oren) → turunkan saturation/`rs`, ulang.

## 2. Rough cut, nafas, cold open, multi-take

### 2a. Rough cut (dead air + filler + ulangan)
- Dead air: jarak antara perkataan >0.3-0.4s + `silencedetect`; simpan beat 0.15s sebelum punchline.
- Buang filler jelas (emm, aaa, err, salah sebut) dan **ayat berulang** (video AI/Gemini selalu ulang frasa: buang yang pertama, simpan versi lengkap). Jangan buang "kan", "so" kalau sebahagian ayat. JANGAN potong dalam perkataan.
- `trim/atrim` setiap segmen + `afade` 20-30ms + `concat`, `-r 30`. Kemudian **transcribe semula** untuk timing baru dan sahkan ayat sambung elok.

### 2b. Nafas
Calon nafas = jurang antara perkataan 0.15-0.8s yang ada bunyi (RMS -45 hingga -22 dBFS, bukan senyap penuh) dan bunyi "hiss" (energi tinggi atas 2kHz lebih besar dari bawah 500Hz).
- Jurang ≥ 0.35s dan memang dead air → potong terus dalam 2a (simpan 0.08s).
- Lain → turun -12dB, bukan buang: `volume=enable='between(t,A,B)':volume=0.25` (satu `volume` setiap nafas, rantai dengan koma). Nafas dalam satu ayat panjang biar.

### 2c. Cold open
Ayat hook terpilih [hs, he] (dari words.json, sempadan perkataan, tambah 0.05s kiri/kanan):
```bash
ffmpeg -i footage.mp4 -filter_complex \
 "[0:v]trim=HS:HE,setpts=PTS-STARTPTS[hv];[0:a]atrim=HS:HE,asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st=DUR_H-0.03:d=0.03[ha];\
  [hv][ha][0:v][0:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -r 30 ... footage_co.mp4
```
- Dalam komposisi: flash putih 2 frame + whoosh tepat pada sambungan, punch-in berbeza (hook 1.12, mula biasa 1.0) supaya nampak sengaja.
- Kalau ayat hook tu memang ada di tengah video, biasanya simpan juga di tempat asal (orang dengar dua kali = callback), kecuali dekat sangat dengan awal (< 8s) → buang yang asal.

### 2d. Multi-take cut (banyak fail / satu fail panjang dengan ayat diulang)
1. Normalise SEMUA fail: `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30` + grade + tag bt709 → `t01.mp4`, `t02.mp4`...
2. Transcribe setiap fail → segmen `{fail, start, end, teks}`.
3. Kesan ulangan: `difflib.SequenceMatcher` teks segmen berturutan (ratio > 0.6 = take ulang). Simpan take TERAKHIR (biasanya paling lancar) kecuali ada tanda gagap: perkataan terputus, "eh / sorry / ulang / jap", segmen < 60% panjang yang lain, ayat tak lengkap → guna take lain.
4. Buang segmen salah: ketawa, "ok cut", tengok skrin, senyap panjang.
5. Susun ikut urutan skrip (kalau ada), concat + crossfade audio 0.04s. Tukar angle/lokasi = jump cut → punch-in ringan atau whoosh kecil, dan guna J/L-cut (§2e).
6. Simpan `cutlist.json` (fail, in, out, teks). Transcribe semula hasil concat.

### 2e. J-cut / L-cut pada tukar take/angle
Bina video & audio dengan sempadan berbeza, total durasi sama. Untuk sempadan antara segmen A dan B pada masa T dalam output:
- **L-cut** (gambar lambat, suara B mula dulu atas muka A): video A dipanjangkan +0.13s (4 frame) ke dalam B, video B dipotong 0.13s di awal. Audio kekal sempadan asal.
- **J-cut** (gambar B masuk dulu, suara A habis atas gambar B): sebaliknya.
Implementasi: buat dua cutlist, `vcut` (in/out video dengan anjakan) dan `acut` (asal), concat video sahaja dan audio sahaja berasingan, kemudian `-map` kedua-duanya. Check jumlah durasi video == audio (±1 frame). Guna L-cut sebagai default; J-cut untuk masuk seksyen baru yang dia mula dengan soalan/“so…”.
Untuk B-roll dalam HyperFrames: suara memang jalan terus, jadi J/L-cut = offset `data-start` B-roll +0.1-0.2s dari sempadan ayat (lihat library.md B-roll).

## 3. Transcribe + alignment

### 3a. Utama: faster-whisper (word timestamp)
```python
from faster_whisper import WhisperModel
import json, wave, numpy as np
# ffmpeg -i footage.mp4 -ac 1 -ar 16000 a.wav
w = wave.open("a.wav"); audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
m = WhisperModel("medium", compute_type="int8")
segs, info = m.transcribe(audio, language="ms", word_timestamps=True, vad_filter=True)
words = [{"w": x.word.strip(), "s": round(x.start,2), "e": round(x.end,2)} for s in segs for x in s.words]
json.dump({"lang": info.language, "words": words}, open("words.json","w"), ensure_ascii=False, indent=1)
```
- Model: `medium` default; `large-v3` kalau PC laju / banyak salah dengar (lebih tepat untuk BM, ~2x lambat). Jangan `*.en`.
- Bagi numpy array, bukan path (elak error PyAV `metadata_errors`). `language="en"` kalau video BI; rojak berat → biar auto-detect dan bandingkan.
- Betulkan salah dengar ikut konteks & CLAUDE.md: "cloud"→Claude, "touch"→text, "tanya di bio"→tekan link di bio, prom→PROMPT, min→MINIT. Perkataan memang tak jelas → elak dalam caption, sebut dalam mesej akhir.

### 3b. Re-align teks yang dah dibetulkan (WAJIB untuk karaoke / word pop)
Whisper timestamp lari bila perkataan dibetulkan/digabung, dan BM rojak selalu drift. Align semula teks final ke audio:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --break-system-packages -q || pip install torch torchaudio --break-system-packages -q
pip install git+https://github.com/MahmoudAshraf97/ctc-forced-aligner.git --break-system-packages -q
```
```python
import torch, json
from ctc_forced_aligner import (load_audio, load_alignment_model, generate_emissions,
    preprocess_text, get_alignments, get_spans, postprocess_results)
model, tok = load_alignment_model("cpu", dtype=torch.float32)
wav = load_audio("a.wav", model.dtype, model.device)
em, stride = generate_emissions(model, wav, batch_size=4)
text = open("final_text.txt").read()            # teks dah dibetulkan, satu baris
ts, tx = preprocess_text(text, romanize=True, language="msa")
seg, sc, blank = get_alignments(em, ts, tok)
spans = get_spans(ts, seg, blank)
res = postprocess_results(tx, spans, stride, sc)   # [{"text","start","end"}...]
json.dump([{"w":r["text"],"s":round(r["start"],2),"e":round(r["end"],2)} for r in res], open("words_aligned.json","w"), ensure_ascii=False, indent=1)
```
- Kalau API lain sikit (versi baru), baca README pakej; idea sama: emissions → align → spans.
- Video > 60s: align per chunk ayat (potong ikut silencedetect) supaya laju & tak OOM.
- Check: 3 perkataan (awal/tengah/akhir) — dengar `atrim=s:e` setiap satu, mesti tepat perkataan tu.
- Tak boleh install (network block) → guna timestamp whisper 3a, dan untuk karaoke snap setiap perkataan ke onset tenaga terdekat (RMS naik > 6dB dalam tetingkap 20ms, ±0.12s). Sebut satu baris dalam mesej akhir.

### 3c. Fallback: sherpa-onnx (bila HuggingFace blocked)
```bash
pip install sherpa-onnx --break-system-packages -q
curl -sSL -o wm.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-medium.tar.bz2 && tar xjf wm.tar.bz2 && rm wm.tar.bz2
```
- Guna `medium-*.int8.onnx` (fp32 OOM). `language="ms"`.
- Timing: `silencedetect=n=-30dB:d=0.15` potong ayat, transcribe setiap chunk; perkataan dalam chunk diagih ikut panjang huruf, KEMUDIAN snap ke onset tenaga (cara 3b fallback). Tanpa snap, karaoke akan drift.

### 3d. Analyze
1. `ffprobe`: durasi, resolusi, orientasi, fps, audio.
2. Frame sheet: `fps=2,scale=180:-1,tile=10x4` (video > 60s: `fps=0.5`, max ~60 frame). Tengok posisi muka/kepala (muka subjek biasanya y 600-1400), tangan, ruang kosong kiri/kanan kepala (slot icon), cahaya, background, prop.
3. Kenal pasti: hook asal, ayat paling kuat untuk cold open, keyword setiap ayat, senarai/nombor, CTA, ayat untuk loop ending, perkataan untuk icon, ayat untuk B-roll, effect yang user sebut sendiri.

## 4. Cutout badan (style 1-6, 21, preset D, dan 3/11 jika perlu)

**Default: cutout segmen beat yang perlu sahaja** (text behind / icon / pop-out), bukan seluruh video. CPU ~1 frame/s pada 1080x1920 (5s ≈ 2.5 min, 20s ≈ 10 min; kali pertama + ~1 min download model).
- **Sisa meja/latar di bawah badan**: cutout selalu bawa sikit meja. Bila latar diganti / ada glow, mask bawah: `#cut{-webkit-mask-image:linear-gradient(180deg,#000 78%,transparent 84%);mask-image:...}` (laras % ikut paras meja dari frame sheet).
```bash
ffmpeg -ss A -t D -i footage.mp4 -c:v libx264 -crf 14 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -an seg_A.mp4
npx hyperframes remove-background seg_A.mp4 -o cut_A.webm --quality best   # run_in_background: true, tanpa timeout
```
- Jalan beberapa segmen selari (2-3 proses). `<video id=cutA src=cut_A.webm muted data-start=A>` dalam `#cam`, satu setiap beat.
- Satu klip panjang perlu cutout penuh → pecah 2 bahagian bertindih 0.5s, jalan selari, cantum:
```bash
ffmpeg -c:v libvpx-vp9 -i p1.webm -t 10 -c:v png -pix_fmt rgba p1.mov
ffmpeg -c:v libvpx-vp9 -i p2.webm -ss 0.5 -c:v png -pix_fmt rgba p2.mov
ffmpeg -i p1.mov -i p2.mov -filter_complex "[0][1]concat=n=2:v=1:a=0,format=yuva420p" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 24 -row-mt 1 cutout.webm
```
- Decode WebM alpha MESTI `-c:v libvpx-vp9` sebelum `-i`. Verify overlay atas `color=red`; frame count = segmen. Cutout gagal → text depan badan, sebut satu baris.

## 5. Audio (SFX + music, jana sendiri, percuma)

- SFX ffmpeg/numpy: whoosh (`anoisesrc` pink + highpass/lowpass + fade), pop (`sine=880:d=0.12`), chime (sine 1568/2093/2637 + adelay), typing click (`sine=2000:d=0.02`), news sting (sine 440→660 + `aecho`), tick (`sine=1200:d=0.015`), boom (sine 60Hz + `acrusher`). Sync dengan effect & setiap masuk B-roll. Jangan SFX sama dua kali berturut.
- Music (preset B/D/E atau add-on): beat 100bpm kick/hat/pad Am-F-C-G jana numpy. Cinematic/editorial: music minimum.
- **Silence sebelum punchline**: masa jana music, darab dengan envelope gain: 1 → 0 dalam 0.08s pada (P - 0.4s), kekal 0 sampai P, kemudian drop balik penuh tepat pada P (P = mula punch word), dengan hit/boom pada P. Max 2-3 kali.
- **Loop ending**: music berakhir pada bar penuh dan fade ≤ 0.3s; jangan tail panjang (video ulang terus ke hook).
- SFX boleh sebagai `<audio id=sfxN>` dalam komposisi (vol 0.35-0.8), ATAU mix selepas render bersama music. Mix (WAJIB format ni, loudnorm SEKALI di sini; versi lama pernah potong suara hujung sebab loudnorm tukar sample rate). Ganti DUR:
```bash
ffmpeg -y -i visual.mp4 -i music.wav -i sfx.wav -filter_complex "[0:a]aresample=44100,loudnorm=I=-15:TP=-2:LRA=9,aresample=44100,apad,atrim=0:DUR,asplit[v1][v2];[1:a]aresample=44100,volume=0.22,apad,atrim=0:DUR[m];[m][v2]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=300[md];[2:a]aresample=44100,volume=0.45,apad,atrim=0:DUR[s];[v1][md][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.85,atrim=0:DUR[a]" -map 0:v -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a aac -b:a 192k -movflags +faststart Final.mp4
```
- Lepas mix: `ffprobe` audio == video durasi; `ffmpeg -i Final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12` → Integrated -14 ±1 LUFS, True peak ≤ -1.5 dBTP (kalau tak, laras `volume` music/sfx atau limit). Transcribe 3s terakhir untuk sahkan CTA penuh.

## 6. QA → render

```bash
npx hyperframes lint            # 0 errors
python <skill>/scripts/slop_lint.py index.html --profile talking-head   # 0 ERROR
npx hyperframes snapshot -o snaps --no-end --at <masa setiap beat storyboard>
ffmpeg -pattern_type glob -i 'snaps/frame-*.png' -vf "scale=320:-1,tile=6x2" all.jpg   # Read
npx hyperframes render --output render.mp4 --sdr     # --sdr WAJIB; run_in_background, tunggu dengan loop pgrep
# tiada music/sfx mix luar → loudnorm sekali + re-encode:
ffmpeg -i render.mp4 -af "aresample=44100,loudnorm=I=-14:TP=-2:LRA=9,aresample=44100" -c:v libx264 -crf 18 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a aac -b:a 192k -movflags +faststart Final.mp4
# ada music → mix §5 dengan render.mp4 sebagai visual.mp4
python <skill>/scripts/look.py Final.mp4 --expect-duration <s> --audio --lufs -14 --max-end 1.5 --sheet chk.jpg   # QA gates + contact sheet render sebenar (overlay ADA?)
```
- Render ~6-12 min / 20s. `--debug` tunjuk "HDR auto-promotion" → footage belum retag bt709. Video panjang: kerja & preview seksyen demi seksyen.
- True peak lepas encode AAC boleh naik ~0.5dB atas target loudnorm, sebab tu TP=-2. Cantum banyak klip (compilation) → loudnorm sekali lagi atas hasil cantuman, check ebur128.
- Loop check: `ffmpeg -sseof -1 -i Final.mp4 ... ` + 1s pertama, concat, tonton/dengar sambungan.

## 7. Export tambahan

- **SRT** (untuk upload caption platform / YouTube): dari `words_aligned.json`, kumpul 3-6 perkataan atau putus pada jeda > 0.35s, max 2s setiap baris, format `HH:MM:SS,mmm`. Simpan `Final.srt`.
- **Cover**: frame paling ekspresif dalam hook (mata terbuka, mulut tak separuh sebut) + teks hook besar dalam safe zone tengah: snapshot HyperFrames pada masa tu, atau `ffmpeg -ss T -i Final.mp4 -frames:v 1 -q:v 2 cover.jpg`. 1080x1920.
- **Tanpa caption** (bila user minta, atau tawar dalam mesej akhir): salin index, tambah `<style>.cap,#captions{display:none!important}</style>`, render semula (masa render sama). Guna untuk repost/translate.

## 8. Rujukan masa render (anggaran)
| Kerja | 20s | 60s |
|---|---|---|
| Transcribe + align | 1-2 min | 3-5 min |
| Cutout segmen sahaja | 3-6 min | 5-15 min |
| Render HyperFrames | 6-12 min | 20-35 min |

## 9. Fallback FFmpeg-only (tanpa HyperFrames)

- Cut: `trim/atrim` + concat.
- Caption: fail `.ass` dari words_aligned.json (bold, outline, keyword warna, 2 style), burn `-vf ass=caps.ass`.
- Zoom: `zoompan` atau `crop`+`scale` ikut masa.
- Pop-up/icon/logo/B-roll: `overlay` dengan `enable='between(t,a,b)'`; PIP = scale video kecil + mask bulat.
- Music duck: `sidechaincompress`. Reframe 9:16: `crop` ikut posisi muka.
