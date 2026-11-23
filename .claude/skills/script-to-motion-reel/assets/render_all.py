#!/usr/bin/env python3
"""Render penuh dengan SATU perintah: info halaman -> audio -> frame paralel -> sambung -> file final.

    python3 render_all.py <build> [--out <file.mp4>] [--max-minutes 8] [--workers N] [--max-mb 29]

- Bisa DILANJUT: kalau terhenti (batas waktu perintah, batas pemakaian, koneksi), jalankan perintah
  yang sama lagi. Potongan yang sudah jadi tidak dirender ulang.
- --max-minutes: berhenti dengan rapi sebelum batas waktu perintah tercapai, lalu cetak
  "BELUM SELESAI". Jalankan lagi sampai muncul "SELESAI".
- File final dijaga di bawah --max-mb (default 29 MB, batas kirim file di chat). --max-mb 0 = tanpa batas (crf 18).
- Kalau halaman (index.html) berubah, potongan lama otomatis dibuang.
"""
import argparse, glob, hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.environ.get("FFMPEG_BIN", "ffmpeg")
FP = os.environ.get("FFPROBE_BIN", "ffprobe")
LIMIT_MB = 29.0
CHUNK = 240


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe_dur(p, stream="v"):
    r = sh([FP, "-v", "error", "-select_streams", f"{stream}:0", "-show_entries", "stream=duration", "-of", "csv=p=0", p])
    try: return float(r.stdout.strip().split("\n")[0])
    except Exception:
        r = sh([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p])
        return float(r.stdout.strip() or 0)


def page_hash(B):
    h = hashlib.sha1(open(os.path.join(B, "index.html"), "rb").read())
    for f in ("project.json", "clips.json"):
        pj = os.path.join(B, f)
        if os.path.exists(pj): h.update(open(pj, "rb").read())
    return h.hexdigest()[:16]


def final_encode(src_v, wav, out, dur):
    if LIMIT_MB <= 0:
        r = sh([FF, "-nostdin", "-v", "error", "-y", "-i", src_v, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                "-movflags", "+faststart", out])
        if r.returncode != 0: sys.exit("Encode final gagal:\n" + r.stderr[-800:])
        return os.path.getsize(out) / 1e6, "crf18"
    target = LIMIT_MB * 0.97 * 1e6 * 8
    vb = int(min(12e6, (target / dur) - 160e3) * 0.98)
    common = ["-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", "-pix_fmt", "yuv420p",
              "-x264-params", "aq-mode=3"]
    if vb < 900e3:
        print(f"PERINGATAN: video {dur:.0f} dtk sangat panjang untuk batas 30 MB, kualitas akan turun.")
    r = sh([FF, "-nostdin", "-v", "error", "-y", "-i", src_v, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
            "-preset", "medium", "-crf", "20", "-maxrate", str(vb), "-bufsize", str(vb * 2)] + common + [out])
    if r.returncode != 0:
        sys.exit("Encode final gagal:\n" + r.stderr[-800:])
    mb = os.path.getsize(out) / 1e6
    if mb <= LIMIT_MB:
        return mb, "crf20"
    vb2 = int(vb * LIMIT_MB / mb * 0.94)
    print(f"File {mb:.1f} MB, diencode ulang dua tahap ke {vb2/1e6:.2f} Mbps supaya di bawah {LIMIT_MB:.0f} MB...")
    log = out + ".2pass"
    sh([FF, "-nostdin", "-v", "error", "-y", "-i", src_v, "-c:v", "libx264", "-preset", "medium", "-b:v", str(vb2),
        "-pass", "1", "-passlogfile", log, "-x264-params", "aq-mode=3", "-an", "-f", "mp4", os.devnull])
    r = sh([FF, "-nostdin", "-v", "error", "-y", "-i", src_v, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
            "-preset", "medium", "-b:v", str(vb2), "-pass", "2", "-passlogfile", log] + common + [out])
    for f in glob.glob(log + "*"): os.remove(f)
    if r.returncode != 0:
        sys.exit("Encode dua tahap gagal:\n" + r.stderr[-800:])
    return os.path.getsize(out) / 1e6, "2pass"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--out")
    ap.add_argument("--max-minutes", type=float, default=8.0)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--max-mb", type=float, default=29.0)
    a = ap.parse_args()
    global LIMIT_MB
    LIMIT_MB = a.max_mb
    B = os.path.abspath(a.build)
    t_start = time.time()
    if not os.path.exists(os.path.join(B, "index.html")):
        sys.exit("index.html belum ada. Jalankan assemble.py dulu.")
    url = "file://" + os.path.join(B, "index.html")
    seg = os.path.join(B, "seg"); os.makedirs(seg, exist_ok=True)
    h = page_hash(B); hp = os.path.join(seg, "hash.txt")
    if not os.path.exists(hp) or open(hp).read().strip() != h:
        for f in glob.glob(os.path.join(seg, "*")): os.remove(f)
        open(hp, "w").write(h)
        print("Halaman baru atau berubah: mulai render dari awal.")

    info_p = os.path.join(seg, "info.json")
    if not os.path.exists(info_p):
        r = sh(["node", os.path.join(HERE, "render.js"), "--info", info_p, url])
        print(r.stdout.strip());
        if r.returncode != 0:
            sys.exit("Halaman gagal dibuka:\n" + r.stderr[-1500:])
    info = json.load(open(info_p))
    if info.get("errors"):
        print("PERINGATAN dari halaman:", " | ".join(info["errors"][:5]))
    total = float(info["total"]); nfr = int(round(total * 30))

    wav = os.path.join(B, "mix.wav")
    if not os.path.exists(os.path.join(seg, "mix.done")):
        r = sh([sys.executable, os.path.join(HERE, "mix.py"), B])
        print(r.stdout.strip())
        if r.returncode != 0:
            sys.exit("Audio gagal dirakit:\n" + r.stderr[-1500:])
        open(os.path.join(seg, "mix.done"), "w").write("ok")

    chunks = [(s, min(nfr, s + CHUNK)) for s in range(0, nfr, CHUNK)]
    name = lambda s: os.path.join(seg, f"c_{s:06d}.mp4")
    todo = [c for c in chunks if not os.path.exists(name(c[0]))]
    workers = a.workers or max(1, min(4, (os.cpu_count() or 2) // 2))
    if todo:
        print(f"Render {len(todo)} dari {len(chunks)} potongan ({nfr} frame, {total:.1f} dtk), {workers} paralel...")
        sys.stdout.flush()
    running, done_n, t_first = [], len(chunks) - len(todo), None
    deadline = t_start + a.max_minutes * 60
    while todo or running:
        while todo and len(running) < workers and time.time() < deadline:
            s, e = todo.pop(0)
            p = subprocess.Popen(["node", os.path.join(HERE, "render.js"), str(s), str(e), name(s), url],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            running.append((p, s, time.time()))
        if not running:
            break
        time.sleep(1.0)
        for item in running[:]:
            p, s, ts = item
            if p.poll() is not None:
                running.remove(item)
                outp = p.stdout.read()
                if p.returncode != 0 or not os.path.exists(name(s)):
                    print(f"Potongan mulai frame {s} gagal:\n{outp[-800:]}")
                    sys.exit("Render berhenti karena error halaman. Perbaiki lalu jalankan lagi.")
                done_n += 1
                if t_first is None: t_first = time.time() - ts
                left = len(todo) + len(running)
                eta = (t_first * left / workers) / 60 if t_first else 0
                print(f"RENDER {100 * done_n // len(chunks)}% ({done_n}/{len(chunks)} potongan)"
                      + (f", sisa sekitar {eta:.0f} menit" if left else ""))
                sys.stdout.flush()
    if done_n < len(chunks):
        print(f"BELUM SELESAI: {done_n}/{len(chunks)} potongan. Jalankan perintah yang sama lagi untuk melanjutkan.")
        sys.exit(10)

    fin = os.path.join(seg, "final.txt")
    if os.path.exists(fin) and os.path.exists(open(fin).read().strip()) and not a.out:
        print(f"SUDAH SELESAI sebelumnya: {open(fin).read().strip()} (halaman tidak berubah sejak render terakhir)")
        return
    lst = os.path.join(seg, "list.txt")
    open(lst, "w").write("".join(f"file '{name(s)}'\n" for s, e in chunks))
    vid = os.path.join(seg, "video.mp4")
    r = sh([FF, "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    if r.returncode != 0:
        sys.exit("Gagal menyambung potongan:\n" + r.stderr[-800:])

    out = a.out
    if not out:
        od = os.path.join(B, "out"); os.makedirs(od, exist_ok=True)
        n = 1
        while os.path.exists(os.path.join(od, f"Reel_V{n}.mp4")): n += 1
        out = os.path.join(od, f"Reel_V{n}.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    print("Encode final..."); sys.stdout.flush()
    mb, how = final_encode(vid, wav, out, total)
    vd, ad = probe_dur(out, "v"), probe_dur(out, "a")
    ok = abs(vd - total) < 0.15 and abs(ad - vd) < 0.15 and (LIMIT_MB <= 0 or mb <= LIMIT_MB)
    open(fin, "w").write(os.path.abspath(out))
    print(f"{'SELESAI' if ok else 'SELESAI DENGAN CATATAN'}: {out}")
    print(f"  ukuran {mb:.1f} MB ({how}) | video {vd:.2f} dtk | audio {ad:.2f} dtk | TOTAL halaman {total:.2f} dtk")
    if not ok:
        print("  PERIKSA: panjang video/audio tidak cocok atau ukuran melebihi batas.")


if __name__ == "__main__":
    main()
