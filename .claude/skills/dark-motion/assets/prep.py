#!/usr/bin/env python3
"""Persiapan video: gabung part, jadikan vertikal 1080x1920, bersihkan suara.

Langkah 1, analisis saja (cepat, tidak mengubah apa pun):
    python3 prep.py <build> --analyze video1.mp4 [video2.mp4 ...]

Langkah 2, proses (setelah user memilih bentuk vertikal kalau videonya horizontal):
    python3 prep.py <build> video1.mp4 [video2.mp4 ...] [--mode track|fit|stack] [--denoise auto|on|off]
                    [--trim mulai:selesai] [--max 180]

Bentuk vertikal untuk video horizontal (ini soal selera, TANYAKAN ke user):
  track : potong 9:16 yang mengikuti wajah, seperti kamera yang menoleh. Wajah besar, sedikit lebih lembut.
  fit   : video utuh di tengah, atas-bawah diisi versi blur. Tidak ada yang terpotong.
  stack : dua orang ditumpuk atas-bawah (podcast 2 orang). Bagian yang hanya berisi satu orang
          otomatis memakai mode track.

Hasil:
  <build>/src/main.mp4     video kerja 1080x1920 30fps
  <build>/src/info.json    durasi, part, bentuk, status pembersihan suara
"""
import argparse, json, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vision as V  # noqa: E402

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")
FP = os.environ.get("FFPROBE_BIN", "ffprobe")
W, H, FPS = 1080, 1920, 30


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit("Perintah gagal:\n" + " ".join(cmd[:8]) + " ...\n" + r.stderr[-1500:])
    return r


def probe(path):
    r = subprocess.run([FP, "-v", "error", "-show_streams", "-show_format", "-of", "json", path], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"File tidak bisa dibaca sebagai video: {path}")
    d = json.loads(r.stdout)
    vs = [s for s in d["streams"] if s.get("codec_type") == "video"]
    a = any(s.get("codec_type") == "audio" for s in d["streams"])
    if not vs:
        sys.exit(f"Tidak ada gambar video di {path}")
    v = vs[0]
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = int(v.get("tags", {}).get("rotate", rot) or rot)
    if abs(rot) % 180 == 90:
        w, h = h, w
    dur = float(d["format"].get("duration") or v.get("duration") or 0)
    return {"file": path, "w": w, "h": h, "dur": round(dur, 3), "audio": a,
            "size_mb": round(os.path.getsize(path) / 1e6, 1)}


def orient(w, h):
    r = w / float(h)
    return "vertical" if r < 0.8 else ("landscape" if r > 1.2 else "square")


def audio_mono(path, sr=16000):
    raw = subprocess.run([FF, "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def noise_stats(x, sr=16000):
    if len(x) < sr:
        return {"noise_db": -90.0, "speech_db": -90.0, "snr": 0.0}
    hop = int(.05 * sr)
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(e + 1e-9)
    n, s = float(np.percentile(db, 8)), float(np.percentile(db, 92))
    return {"noise_db": round(n, 1), "speech_db": round(s, 1), "snr": round(s - n, 1)}


def needs_denoise(ns):
    """Bising latar terdengar kalau jarak suara-bising kecil. Diukur relatif, jadi tidak terpengaruh volume."""
    return ns["snr"] < 36


def loudness(path):
    r = subprocess.run([FF, "-nostdin", "-hide_banner", "-i", path, "-vn", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    for line in r.splitlines()[::-1]:
        line = line.strip()
        if line.startswith("I:"):
            try:
                return float(line.split()[1])
            except Exception:
                pass
    return None


def sample_frames(path, every=0.2, width=640):
    """Ambil frame kecil tiap `every` detik lewat satu proses ffmpeg. Kembalikan (waktu, gambar)."""
    p = probe(path); w, h = p["w"], p["h"]
    sw = width; sh = int(round(h * sw / w / 2) * 2)
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-i", path, "-vf", f"fps={1/every},scale={sw}:{sh}",
                             "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    n = sw * sh * 3; i = 0
    while True:
        buf = proc.stdout.read(n)
        if len(buf) < n:
            break
        yield i * every, np.frombuffer(buf, np.uint8).reshape(sh, sw, 3), sw / float(w)
        i += 1
    proc.wait()


def face_track(path, every=0.2):
    """Daftar [t, [(cx, cy, w, h)...]] dalam koordinat video asli."""
    out = []
    for t, img, k in sample_frames(path, every):
        fs = V.faces(img, max_w=img.shape[1])
        out.append([t, [((x + w / 2) / k, (y + h / 2) / k, w / k, h / k) for x, y, w, h, s in fs[:4]]])
    return out


# ---------------- analisis ----------------
def analyze(build, files):
    parts = [probe(f) for f in files]
    total = round(sum(p["dur"] for p in parts), 2)
    o = orient(parts[0]["w"], parts[0]["h"])
    mixed = len({orient(p["w"], p["h"]) for p in parts}) > 1
    # wajah: 16 sampel tersebar
    counts, xs = [], []
    if V.available():
        for p in parts:
            step = max(0.5, p["dur"] / max(1, round(16 * p["dur"] / max(total, 1))))
            for t, img, k in sample_frames(p["file"], step):
                fs = V.faces(img, max_w=img.shape[1])
                counts.append(len(fs))
                xs += [((x + w / 2) / img.shape[1]) for x, y, w, h, s in fs[:3]]
    typical = int(np.median(counts)) if counts else -1
    spread = round(float(np.ptp(xs)), 2) if len(xs) > 1 else 0.0
    ns = noise_stats(np.concatenate([audio_mono(p["file"]) for p in parts if p["audio"]] or [np.zeros(1, np.float32)]))
    info = {"parts": parts, "total": total, "orientation": o, "mixed_orientation": mixed,
            "faces_typical": typical, "faces_spread": spread, "audio": ns,
            "noisy": needs_denoise(ns)}
    os.makedirs(os.path.join(build, "src"), exist_ok=True)
    json.dump(info, open(os.path.join(build, "src", "analysis.json"), "w"), indent=2)

    print("=== ANALISIS VIDEO ===")
    for p in parts:
        print(f"- {os.path.basename(p['file'])}: {p['dur']} dtk, {p['w']}x{p['h']} ({orient(p['w'], p['h'])}), {p['size_mb']} MB"
              + ("" if p["audio"] else ", TANPA SUARA"))
    print(f"Total durasi : {total} dtk")
    print(f"Bentuk       : {o}" + (" (part beda bentuk, disamakan ke part pertama)" if mixed else ""))
    print(f"Wajah        : biasanya {typical} orang di layar" + (f", sebaran horizontal {spread}" if typical >= 1 else "")
          if typical >= 0 else "Wajah        : deteksi wajah tidak tersedia, posisi caption pakai default aman")
    print(f"Suara        : bising latar {ns['noise_db']} dB, jarak suara-bising {ns['snr']} dB"
          + (" -> akan dibersihkan ringan" if info["noisy"] else " -> bersih"))
    print()
    if o != "vertical":
        print("PERLU DITANYAKAN KE USER: videonya horizontal. Pilihan bentuk vertikal:")
        print("  track = ikuti wajah (wajah besar, sedikit lebih lembut)")
        print("  fit   = video utuh di tengah, atas-bawah blur (tidak ada yang terpotong)")
        if typical >= 2 and spread > 0.3:
            print("  stack = dua orang ditumpuk atas-bawah (cocok, terdeteksi 2 orang berjauhan)")
        else:
            print("  stack = dua orang ditumpuk atas-bawah (hanya kalau memang ada 2 orang)")
    if typical >= 2:
        print("PERLU DITANYAKAN KE USER: ada lebih dari satu orang. Mau diberi label nama? Kalau ya, nama dan perannya.")
    if total > 180:
        print(f"PERHATIAN: video {total} dtk, lebih dari batas 180 dtk. Tanyakan bagian mana yang dipakai (--trim).")
    if min(p["h"], p["w"]) < 720:
        print("PERHATIAN: resolusi rendah, hasil akan terlihat lembut. Sampaikan ke user.")


# ---------------- proses ----------------
def join(build, parts, canvas, trim):
    """Samakan ukuran, fps, dan volume tiap part, lalu sambung jadi satu."""
    cw, ch = canvas
    args = [FF, "-nostdin", "-v", "error", "-y"]
    fc = []
    for i, p in enumerate(parts):
        args += ["-i", p["file"]]
    offsets, acc = [], 0.0
    for i, p in enumerate(parts):
        lu = loudness(p["file"]) if p["audio"] else None
        g = 0.0 if lu is None or lu < -70 else max(-12.0, min(12.0, -18.0 - lu))
        if orient(p["w"], p["h"]) == orient(cw, ch):
            fc.append(f"[{i}:v]scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},setsar=1,fps={FPS},format=yuv420p[v{i}]")
        else:   # part beda bentuk: utuh di tengah dengan latar blur, jangan di-zoom paksa
            fc.append(f"[{i}:v]split[p{i}][q{i}];[p{i}]scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},"
                      f"gblur=sigma=30,eq=brightness=-0.15[bg{i}];[q{i}]scale={cw}:{ch}:force_original_aspect_ratio=decrease[fg{i}];"
                      f"[bg{i}][fg{i}]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={FPS},format=yuv420p[v{i}]")
        if p["audio"]:
            fc.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g:.2f}dB,apad=whole_dur={p['dur']}[a{i}]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{p['dur']}[a{i}]")
        offsets.append({"file": os.path.basename(p["file"]), "start": round(acc, 3), "dur": p["dur"], "gain_db": round(g, 1)})
        acc += p["dur"]
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=1[v][a]")
    out = os.path.join(build, "src", "joined.mp4")
    cmd = args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]"]
    if trim:
        a, b = trim
        cmd += ["-ss", str(a), "-to", str(b)]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", out]
    run(cmd)
    return out, offsets


def smooth_path(samples, every, total, Wsrc, crop_w):
    """Jalur kamera virtual yang tenang: ikuti wajah utama, abaikan gerakan kecil."""
    n = len(samples)
    cx = np.full(n, np.nan)
    prev = None
    for i, (t, fs) in enumerate(samples):
        if not fs:
            continue
        cand = fs[0]
        if prev is not None and len(fs) > 1:
            near = min(fs, key=lambda f: abs(f[0] - prev))
            if cand[2] * cand[3] < 1.8 * near[2] * near[3]:
                cand = near
        cx[i] = cand[0]; prev = cand[0]
    if np.all(np.isnan(cx)):
        return None
    idx = np.arange(n); ok = ~np.isnan(cx)
    cx = np.interp(idx, idx[ok], cx[ok])
    # median lalu gaussian
    k = 7
    pad = np.pad(cx, k // 2, mode="edge")
    cx = np.array([np.median(pad[i:i + k]) for i in range(n)])
    sig = 0.7 / every
    r = int(sig * 3)
    ker = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); ker /= ker.sum()
    cx = np.convolve(np.pad(cx, r, mode="edge"), ker, mode="valid")
    # per frame dengan zona mati + kecepatan maksimum
    nf = int(round(total * FPS))
    tgt = np.interp(np.arange(nf) / FPS, idx * every, cx)
    cam = np.zeros(nf); cam[0] = tgt[0]
    dz, vmax = 0.06 * Wsrc, 0.35 * Wsrc / FPS
    moving = False
    for i in range(1, nf):
        d = tgt[i] - cam[i - 1]
        if abs(d) > dz:
            moving = True
        if moving:
            step = np.clip(d * 0.12, -vmax, vmax)
            cam[i] = cam[i - 1] + step
            if abs(d) < dz * 0.25:
                moving = False
        else:
            cam[i] = cam[i - 1]
    return np.clip(cam - crop_w / 2, 0, Wsrc - crop_w)


def two_person_runs(samples, every, Ws, min_run=1.5):
    """Tandai bagian video yang berisi dua orang berjauhan. Kembalikan daftar (mulai, selesai, boxes)."""
    flags, pairs = [], []
    for t, fs in samples:
        ok, pr = False, None
        if len(fs) >= 2:
            big = fs[0][2]
            cand = [f for f in fs[:4] if f[2] > 0.4 * big]
            cand.sort(key=lambda f: f[0])
            if len(cand) >= 2 and cand[-1][0] - cand[0][0] > 0.25 * Ws:
                ok, pr = True, (cand[0], cand[-1])
        flags.append(ok); pairs.append(pr)
    n = len(flags)
    if n == 0:
        return []
    w = max(1, int(round(0.7 / every)))
    sm = [sum(flags[max(0, i - w):i + w + 1]) * 2 > len(flags[max(0, i - w):i + w + 1]) for i in range(n)]
    runs, i = [], 0
    while i < n:
        j = i
        while j < n and sm[j] == sm[i]: j += 1
        runs.append([sm[i], i, j]); i = j
    # bagian terlalu pendek ikut tetangganya, supaya tidak berganti-ganti terus
    changed = True
    while changed and len(runs) > 1:
        changed = False
        for k, r in enumerate(runs):
            if (r[2] - r[1]) * every < min_run:
                nb = runs[k - 1] if k > 0 else runs[k + 1]
                r[0] = nb[0]; changed = True
        merged = []
        for r in runs:
            if merged and merged[-1][0] == r[0]: merged[-1][2] = r[2]
            else: merged.append(list(r))
        if len(merged) == len(runs): break
        runs = merged
    out = []
    for flag, i0, i1 in runs:
        if not flag: continue
        L = [pairs[i] for i in range(i0, i1) if pairs[i]]
        if not L: continue
        boxes = []
        for side in (0, 1):
            cx = float(np.median([p[side][0] for p in L])); cy = float(np.median([p[side][1] for p in L]))
            fw = float(np.median([p[side][2] for p in L]))
            boxes.append((cx, cy, fw))
        out.append((i0 * every, i1 * every, boxes))
    return out


def panel_crop(img, cx, cy, fw, Ws, Hs):
    """Potong 9:8 di sekitar satu wajah: kepala dan bahu, wajah di 42% dari atas."""
    ch = float(np.clip(fw * 3.4, Hs * 0.42, Hs * 0.95)); cw = ch * 9 / 8
    if cw > Ws: cw = Ws; ch = cw * 8 / 9
    x = int(np.clip(cx - cw / 2, 0, Ws - cw)); y = int(np.clip(cy - 0.42 * ch, 0, Hs - ch))
    return img[y:y + int(ch), x:x + int(cw)]


def reframe_python(src, out, afilter, total, mode):
    """track: kamera virtual yang mengikuti wajah. stack: dua orang atas-bawah, otomatis
    beralih ke track di bagian yang hanya berisi satu orang."""
    import cv2
    p = probe(src); Ws, Hs = p["w"], p["h"]
    crop_w = int(round(Hs * 9 / 16 / 2) * 2)
    every = 0.2
    samples = face_track(src, every) if V.available() else []
    x0 = smooth_path(samples, every, total, Ws, crop_w) if samples else None
    nf = int(round(total * FPS)) + 2
    if x0 is None:
        print("Tidak ada wajah terdeteksi, pakai potongan tengah.")
        x0 = np.full(nf, (Ws - crop_w) / 2)
    runs = two_person_runs(samples, every, Ws) if mode == "stack" else []
    if mode == "stack":
        secs = sum(e - s for s, e, b in runs)
        print(f"bagian dua orang: {secs:.1f} dtk dari {total:.1f} dtk"
              + ("" if secs else " (tidak ada, seluruh video memakai mode ikuti wajah)"))
    dec = subprocess.Popen([FF, "-nostdin", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a", "-af", afilter,
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "256k", "-shortest", out], stdin=subprocess.PIPE)
    n = Ws * Hs * 3; i = 0; ri = 0
    while True:
        buf = dec.stdout.read(n)
        if len(buf) < n:
            break
        img = np.frombuffer(buf, np.uint8).reshape(Hs, Ws, 3)
        t = i / FPS
        while ri < len(runs) and t >= runs[ri][1]: ri += 1
        if ri < len(runs) and runs[ri][0] <= t < runs[ri][1]:
            panels = [cv2.resize(panel_crop(img, cx, cy, fw, Ws, Hs), (W, H // 2), interpolation=cv2.INTER_LANCZOS4)
                      for cx, cy, fw in runs[ri][2]]
            frame = np.vstack(panels)
            frame[H // 2 - 2:H // 2 + 2] = 0      # garis pemisah tipis
        else:
            x = int(round(x0[min(i, len(x0) - 1)]))
            frame = cv2.resize(img[:, x:x + crop_w], (W, H), interpolation=cv2.INTER_LANCZOS4)
        enc.stdin.write(np.ascontiguousarray(frame).tobytes())
        i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    if enc.returncode != 0:
        sys.exit("Gagal menulis video vertikal.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build"); ap.add_argument("files", nargs="+")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--mode", choices=["track", "fit", "stack"])
    ap.add_argument("--denoise", choices=["auto", "on", "off"], default="auto")
    ap.add_argument("--trim", help="mulai:selesai dalam detik, pada video yang sudah disambung")
    ap.add_argument("--max", type=float, default=180)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.build, "src"), exist_ok=True)
    if a.analyze:
        return analyze(a.build, a.files)

    parts = [probe(f) for f in a.files]
    o = orient(parts[0]["w"], parts[0]["h"])
    total = sum(p["dur"] for p in parts)
    trim = None
    if a.trim:
        s, e = (float(v) for v in a.trim.split(":")); trim = (s, e); total = e - s
    if total > a.max + 0.5:
        sys.exit(f"Video {total:.1f} dtk, lebih dari batas {a.max:.0f} dtk. Tanyakan ke user bagian mana yang dipakai, lalu pakai --trim.")
    if o != "vertical" and not a.mode:
        sys.exit("Video horizontal: tanyakan dulu ke user bentuk vertikalnya (track / fit / stack), lalu jalankan dengan --mode.")

    canvas = (W, H) if o == "vertical" else ((1920, 1080) if o == "landscape" else (1080, 1080))
    print("menyambung dan menyamakan part..."); sys.stdout.flush()
    joined, offsets = join(a.build, parts, canvas, trim)
    jd = probe(joined)["dur"]

    ns = noise_stats(audio_mono(joined))
    den = a.denoise == "on" or (a.denoise == "auto" and needs_denoise(ns))
    nf = max(-80, min(-20, ns["noise_db"] + 3))
    afilter = "highpass=f=70" + (f",afftdn=nr=10:nf={nf:.0f}:tn=1" if den else "")

    out = os.path.join(a.build, "src", "main.mp4")
    mode = "vertical" if o == "vertical" else a.mode
    print(f"membuat video vertikal (mode {mode})..."); sys.stdout.flush()
    common = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k"]
    if mode == "vertical":
        run([FF, "-nostdin", "-v", "error", "-y", "-i", joined, "-c:v", "copy", "-af", afilter, "-c:a", "aac", "-b:a", "256k", out])
    elif mode == "fit":
        fc = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40,"
              f"eq=brightness=-0.18:saturation=0.8[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={FPS}[v]")
        run([FF, "-nostdin", "-v", "error", "-y", "-i", joined, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
             "-af", afilter] + common + [out])
    else:
        reframe_python(joined, out, afilter, jd, mode)

    md = probe(out)["dur"]
    info = {"duration": md, "orientation_in": o, "mode": mode, "parts": offsets, "trim": trim,
            "denoise": {"applied": den, **ns}}
    json.dump(info, open(os.path.join(a.build, "src", "info.json"), "w"), indent=2)
    os.remove(joined)
    print(f"SELESAI: {out}  {md} dtk, mode {mode}, pembersihan suara {'YA' if den else 'tidak perlu'}")
    if len(offsets) > 1:
        print("Awal tiap part di video gabungan (untuk --offset srt2words kalau SRT per part):",
              ", ".join(f"{p['file']}@{p['start']}" for p in offsets))


if __name__ == "__main__":
    main()
