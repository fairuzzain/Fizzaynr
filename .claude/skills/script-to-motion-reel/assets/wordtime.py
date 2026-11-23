#!/usr/bin/env python3
"""Waktu per kata dari suara (dipakai kalau user tidak punya file subtitle).

  python3 wordtime.py <vo.mp3_atau_video> <out.json> [--lang id] [--models DIR]

--lang : kode bahasa video (id, en, ms, ...). "auto" = deteksi otomatis.
Keluaran: [[detik, "kata"], ...] di timeline VO asli.

Pertama kali dipakai di sebuah sesi, script ini memasang paket sherpa-onnx (sekitar 20 MB, dari PyPI)
dan mengunduh model sekitar 850 MB dari GitHub. Butuh beberapa menit; beri tahu user sebelumnya.
Model disimpan di ~/.cache/sherpa-models (atau dipakai ulang dari ~/.cache/dark-motion/models kalau sudah ada).
"""
import sys, os, json, re, difflib, subprocess, argparse
import numpy as np

try:
    import sherpa_onnx
except ImportError:
    print("memasang sherpa-onnx...", flush=True)
    for extra in (["--break-system-packages"], []):
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "sherpa-onnx", *extra]).returncode == 0:
            break
    try:
        import sherpa_onnx
    except ImportError:
        sys.exit("Paket pengenal suara tidak bisa dipasang (internet sesi ini dibatasi). Minta user mengirim file subtitle .srt.")

BASE = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models"

def ensure_models(d):
    os.makedirs(d, exist_ok=True)
    need = []
    if not os.path.exists(f"{d}/silero_vad.onnx"): need.append("silero_vad.onnx")
    for m in ("small", "base"):
        if not os.path.isdir(f"{d}/sherpa-onnx-whisper-{m}"): need.append(f"sherpa-onnx-whisper-{m}.tar.bz2")
    for f in need:
        print("unduh", f, flush=True)
        r = subprocess.run(["curl", "-sSL", "--fail", "--retry", "2", "-o", f"{d}/{f}", f"{BASE}/{f}"])
        if r.returncode != 0:
            sys.exit("Model pengenal suara tidak bisa diunduh (GitHub diblokir di sesi ini). Minta user mengirim file subtitle .srt.")
        if f.endswith(".tar.bz2"):
            subprocess.run(["tar", "xjf", f"{d}/{f}", "-C", d], check=True)

def rec(d, m, lang, threads):
    p = f"{d}/sherpa-onnx-whisper-{m}/{m}"
    return sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=p + "-encoder.int8.onnx", decoder=p + "-decoder.int8.onnx",
        tokens=p + "-tokens.txt", language=lang, task="transcribe", num_threads=threads)

def silences(a, sr, floor=-38.0, minlen=0.10):
    hop = int(.02 * sr)
    e = np.array([20*np.log10(np.sqrt(np.mean(a[i:i+hop]**2)) + 1e-9) for i in range(0, len(a)-hop, hop)])
    out, i, sil = [], 0, e < floor
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            if (j - i) * .02 >= minlen: out.append((round(i*.02, 2), round(j*.02, 2)))
            i = j
        else: i += 1
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--models", default=(os.path.expanduser("~/.cache/dark-motion/models")
                    if os.path.isdir(os.path.expanduser("~/.cache/dark-motion/models")) else os.path.expanduser("~/.cache/sherpa-models")))
    ap.add_argument("--lang", default="id")
    ap.add_argument("--threads", type=int, default=max(1, os.cpu_count() or 2)); ap.add_argument("--step", type=float, default=0)
    args = ap.parse_args()
    if args.lang == "auto": args.lang = ""

    ensure_models(args.models)
    raw = subprocess.run([os.environ.get("FFMPEG_BIN", "ffmpeg"), "-nostdin", "-v", "error", "-i", args.src,
                          "-vn", "-ar", "16000", "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).copy(); sr = 16000
    if args.step <= 0:
        args.step = 0.15 if len(a) / sr <= 75 else 0.2
    print(f"audio {len(a)/sr:.1f} dtk, perkiraan waktu proses {len(a)/sr*(2.2 if args.step < .2 else 1.7)/max(1,args.threads)*2/60:.0f}-"
          f"{len(a)/sr*(3.5 if args.step < .2 else 2.6)/max(1,args.threads)*2/60:.0f} menit", flush=True)

    # 1. VAD -> segmen kalimat
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = f"{args.models}/silero_vad.onnx"
    cfg.silero_vad.threshold = .5; cfg.silero_vad.min_silence_duration = .25
    cfg.silero_vad.min_speech_duration = .1; cfg.silero_vad.max_speech_duration = 20
    cfg.sample_rate = 16000
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=180)
    segs = []
    for i in range(0, len(a), 512):
        vad.accept_waveform(a[i:i+512])
        while not vad.empty():
            s = vad.front; segs.append((s.start/16000, len(s.samples)/16000)); vad.pop()
    vad.flush()
    while not vad.empty():
        s = vad.front; segs.append((s.start/16000, len(s.samples)/16000)); vad.pop()

    # 2. transkrip per segmen (whisper-small)
    R = rec(args.models, "small", args.lang, args.threads)
    SEG = []
    for st, du in segs:
        s = R.create_stream(); s.accept_waveform(16000, a[int(st*16000):int((st+du)*16000)]); R.decode_stream(s)
        txt = s.result.text.strip()
        if txt: SEG.append([round(st, 2), round(st+du, 2), txt])
    print(f"transkrip: {len(SEG)} kalimat. Menghitung waktu tiap kata...", flush=True)

    # 3. prefix decoding (whisper-base) -> waktu tiap kata
    B = rec(args.models, "base", args.lang, args.threads)
    norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    def dec(st, en):
        s = B.create_stream(); s.accept_waveform(16000, a[int(st*16000):int(en*16000)])
        B.decode_stream(s); return s.result.text

    res = []
    for st, en, txt in SEG:
        ref = [w for w in txt.split() if w]; rn = [norm(w) for w in ref]; n = len(ref)
        first = [None]*n; first[0] = st; cov = 0; t = st + .25
        while t <= en + .2 and cov < n:
            hyp = [h for h in (norm(w) for w in dec(st, t).split()) if h]
            j = k = 0; last = -1
            while j < n and k < len(hyp):
                if difflib.SequenceMatcher(None, rn[j], hyp[k]).ratio() >= .6:
                    last = max(last, j); j += 1; k += 1
                else: k += 1
            for i in range(cov, min(last+1, n)):
                if first[i] is None: first[i] = max(st, t - .2)
            cov = max(cov, last+1); t += args.step
        for i in range(n):
            if first[i] is None:
                prev = max(j for j in range(i) if first[j] is not None)
                nxt = [j for j in range(i+1, n) if first[j] is not None]
                tn = first[nxt[0]] if nxt else en
                first[i] = first[prev] + (tn-first[prev]) * (i-prev) / ((nxt[0] if nxt else n) - prev)
        for i in range(1, n): first[i] = max(first[i], first[i-1] + .05)
        for w, tt in zip(ref, first): res.append([round(tt, 2), w])
        print(f"  {st:6.1f} dtk: {txt[:70]}", flush=True)

    # 4. rapikan pakai peta senyap + sebar kata yang menumpuk
    SIL = silences(a, sr)
    t = [w[0] for w in res]; n = len(t); anch = [False]*n
    for s0, s1 in SIL:
        cand = [i for i in range(n) if t[i] >= s0 - .1]
        if not cand: continue
        i = cand[0]
        if t[i] - s1 < .6 and (i == 0 or t[i-1] < s0): t[i] = s1 + .02; anch[i] = True
    for i in range(n):
        if i == 0 or res[i][0] - res[i-1][0] > .5: anch[i] = True
    for i in range(1, n): t[i] = max(t[i], t[i-1] + .05)
    i = 0
    while i < n - 1:
        if t[i+1] - t[i] < .13:
            j = i + 1
            while j < n - 1 and t[j+1] - t[j] < .13 and not anch[j+1]: j += 1
            a0 = t[i]; b0 = (t[j+1] - .1) if (j+1 < n and t[j+1]-t[j] < 1.0) else (t[j] + .35)
            b0 = max(b0, t[j]); wts = [len(res[k][1]) + 1.5 for k in range(i, j+1)]
            acc = 0
            for k in range(i, j+1):
                t[k] = a0 + (b0-a0) * acc / sum(wts); acc += wts[k-i]
            i = j + 1
        else: i += 1

    out = [[round(t[k], 2), res[k][1]] for k in range(n)]
    json.dump(out, open(args.out, "w"), ensure_ascii=False)
    print("\n== HASIL ==")
    print(" ".join(f"{w}@{tt}" for tt, w in out))
    print(f"\n{len(out)} kata -> {args.out}")
    print("PERIKSA kata kunci tiap scene sebelum lanjut. ASR bisa salah pada nama produk.")

if __name__ == "__main__":
    main()
