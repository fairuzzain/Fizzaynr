#!/usr/bin/env python3
"""Lembar sampel klip pendukung: satu baris per klip, satu frame tiap N detik.

    python3 clipscan.py <out.jpg> klip1.mp4 klip2.mp4 ... [--every 2] [--h 200]

Dipakai SEBELUM memilih potongan klip untuk HP, dinding video, atau B-roll:
klip user sering berisi teks tertanam (caption lama, judul, watermark). Lihat lembarnya dengan Read,
lalu pilih rentang yang bersih dan ekstrak dengan frames.py --clips-only --clip nama:file:mulai:durasi.
Kolom ke-k di tiap baris = detik k*every. Daftar detik dicetak juga di terminal.
"""
import argparse, glob, os, shutil, subprocess, sys, tempfile

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")
FP = os.environ.get("FFPROBE_BIN", "ffprobe")


def dur(f):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--every", type=float, default=2.0)
    ap.add_argument("--h", type=int, default=200)
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="clipscan_")
    rows = []
    maxcols = 1
    for ci, f in enumerate(a.clips):
        D = dur(f)
        ts = [round(k * a.every, 2) for k in range(int(D // a.every) + 1) if k * a.every < D - .05] or [0.0]
        maxcols = max(maxcols, len(ts))
        for k, t in enumerate(ts):
            subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-ss", str(t), "-i", f, "-frames:v", "1",
                            "-vf", f"scale=-2:{a.h},pad=ceil(iw/2)*2:{a.h}:0:0:black",
                            os.path.join(tmp, f"r{ci:02d}_{k:03d}.jpg")])
        rows.append((f, D, ts))
    W = int(a.h * 9 / 16) + 2
    for ci, (f, D, ts) in enumerate(rows):
        ims = sorted(glob.glob(os.path.join(tmp, f"r{ci:02d}_*.jpg")))
        args = []
        for im in ims: args += ["-i", im]
        n = len(ims)
        fc = "".join(f"[{i}]scale={W}:{a.h}:force_original_aspect_ratio=decrease,pad={W}:{a.h}:(ow-iw)/2:0:black[v{i}];" for i in range(n))
        fc += "".join(f"[v{i}]" for i in range(n)) + (f"hstack={n}" if n > 1 else "null")
        if n < maxcols:
            fc += f",pad={W*maxcols}:{a.h}:0:0:black"
        subprocess.run([FF, "-nostdin", "-v", "error", "-y", *args, "-filter_complex", fc, os.path.join(tmp, f"row{ci:02d}.jpg")])
        print(f"baris {ci+1}: {os.path.basename(f)}  ({D:.1f} dtk)  kolom = detik {', '.join(str(t) for t in ts)}")
    rs = sorted(glob.glob(os.path.join(tmp, "row*.jpg")))
    args = []
    for r in rs: args += ["-i", r]
    fc = "".join(f"[{i}]" for i in range(len(rs))) + (f"vstack={len(rs)}" if len(rs) > 1 else "null")
    r = subprocess.run([FF, "-nostdin", "-v", "error", "-y", *args, "-filter_complex", fc, a.out], capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode != 0:
        sys.exit("Gagal membuat lembar: " + r.stderr[-400:])
    print("->", a.out, "| lihat dengan Read, pilih rentang tanpa teks tertanam")


if __name__ == "__main__":
    main()
