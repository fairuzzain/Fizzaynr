#!/usr/bin/env python3
"""Ubah video kerja jadi image sequence untuk halaman render.

    python3 frames.py <build> [--clip nama:file.mp4[:mulai:durasi]] ... [--clips-only] [--clip-h 640]

Selalu menulis:
  <build>/vf/main/0001.jpg ...   video utama, 1080x1920
  <build>/vf/blur/0001.jpg ...   versi blur kecil, untuk latar bgBlur() yang sinkron dengan video utama
Opsional --clip: klip pendukung dari user jadi <build>/vf/<nama>/ (tinggi 640, cukup untuk tampil kecil).
  --clips-only : HANYA mengekstrak klip, vf/main dan vf/blur tidak disentuh. WAJIB dipakai kalau efek
                 sudah dibakar ke vf/main (bake.py glitch/grade), supaya efeknya tidak tertimpa.
  --clip-h N   : tinggi frame klip (default 640). 960 untuk klip yang tampil besar (kartu/HP utama),
                 534 cukup untuk ubin dinding video.
Pilih potongan klip yang BERSIH dari teks tertanam: cek dulu dengan clipscan.py.

Tag <video> tidak dipakai karena tidak bisa dikunci per frame saat render.
Jalankan ulang setiap kali src/main.mp4 berubah (misalnya setelah cuts.py).
"""
import argparse, glob, os, shutil, subprocess, sys

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")


def ext(src, dst, vf, q, extra=()):
    if os.path.isdir(dst): shutil.rmtree(dst)
    os.makedirs(dst)
    r = subprocess.run([FF, "-nostdin", "-v", "error", "-y", *extra, "-i", src, "-vf", vf, "-q:v", str(q),
                        os.path.join(dst, "%04d.jpg")], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Gagal mengekstrak frame:\n" + r.stderr[-800:])
    return len(glob.glob(os.path.join(dst, "*.jpg")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--clip", action="append", default=[], help="nama:file[:mulai:durasi]")
    ap.add_argument("--clips-only", action="store_true", help="jangan sentuh vf/main dan vf/blur")
    ap.add_argument("--clip-h", type=int, default=640)
    a = ap.parse_args()
    src = os.path.join(a.build, "src", "main.mp4")
    if not a.clips_only:
        if not os.path.exists(src):
            sys.exit("src/main.mp4 belum ada. Jalankan prep.py dulu.")
        n = ext(src, os.path.join(a.build, "vf", "main"), "fps=30,scale=1080:1920", 3)
        nb = ext(src, os.path.join(a.build, "vf", "blur"), "fps=30,scale=540:960,gblur=sigma=18", 6)
        print(f"vf/main: {n} frame ({n/30:.2f} dtk) | vf/blur: {nb} frame")
        if os.path.exists(os.path.join(a.build, "baked.txt")):
            print("PERINGATAN: vf/main baru saja dibuat ulang, efek yang dibakar sebelumnya (lihat baked.txt) HILANG. Bakar ulang.")
    for c in a.clip:
        parts = c.split(":")
        name, f = parts[0], parts[1]
        extra = []
        if len(parts) >= 4: extra = ["-ss", parts[2], "-t", parts[3]]
        k = ext(f, os.path.join(a.build, "vf", name), f"fps=30,scale=-2:{a.clip_h}", 4, extra)
        print(f"vf/{name}: {k} frame  -> pakai vid(parent,'{name}',{k},t0,t1) atau bgVideo(t0,t1,'{name}',{k})")


if __name__ == "__main__":
    main()
