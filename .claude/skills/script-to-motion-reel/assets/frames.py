#!/usr/bin/env python3
"""Ubah klip video user jadi image sequence 30fps untuk vid() di scenes.js.

    python3 frames.py <build> --clip nama:file.mp4[:mulai[:durasi[:tinggi]]] [--clip ...]
    python3 frames.py <build> --wall g:folder_klip [--wall-dur 2.8] [--wall-h 480]

--clip  satu klip. mulai/durasi dalam detik (default: seluruh klip), tinggi default 960
        (480 untuk ubin kecil, 1280 untuk klip full layar).
--wall  semua video di folder jadi g01, g02, ... (untuk video wall), masing-masing --wall-dur detik.
Hasil: build/vf/<nama>/0001.jpg ... dan build/clips.json {nama: jumlah_frame}.
vid(parent, 'nama', null, t0, t1, ...) membaca jumlah frame dari clips.json, jadi tidak perlu dihitung.
Sebelum memilih rentang, cek teks tertanam dengan clipscan.py.
Tag <video> tidak dipakai karena tidak deterministik saat dirender per frame.
"""
import argparse, glob, json, os, shutil, subprocess, sys

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")
VEXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv")


def extract(B, name, src, start=None, dur=None, h=960):
    if not os.path.exists(src): sys.exit(f"Klip tidak ada: {src}")
    out = os.path.join(B, "vf", name)
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(out)
    cmd = [FF, "-nostdin", "-v", "error", "-y"]
    if start: cmd += ["-ss", str(start)]
    cmd += ["-i", src]
    if dur: cmd += ["-t", str(dur)]
    cmd += ["-an", "-vf", f"fps=30,scale=-2:{h}", "-q:v", "3", os.path.join(out, "%04d.jpg")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: sys.exit(f"Gagal mengekstrak {src}:\n{r.stderr[-500:]}")
    n = len(glob.glob(os.path.join(out, "*.jpg")))
    print(f"{name:10s} {n:5d} frame ({n/30:.1f} dtk)  <- {os.path.basename(src)}")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--clip", action="append", default=[])
    ap.add_argument("--wall")
    ap.add_argument("--wall-dur", type=float, default=2.8)
    ap.add_argument("--wall-h", type=int, default=480)
    a = ap.parse_args()
    B = os.path.abspath(a.build)
    cj = os.path.join(B, "clips.json")
    clips = json.load(open(cj)) if os.path.exists(cj) else {}
    for spec in a.clip:
        p = spec.split(":")
        if len(p) < 2: sys.exit(f"Format --clip salah: {spec} (nama:file[:mulai[:durasi[:tinggi]]])")
        name, src = p[0], p[1]
        start = float(p[2]) if len(p) > 2 and p[2] else None
        dur = float(p[3]) if len(p) > 3 and p[3] else None
        h = int(p[4]) if len(p) > 4 and p[4] else 960
        clips[name] = extract(B, name, src, start, dur, h)
    if a.wall:
        pre, folder = a.wall.split(":", 1)
        files = sorted(f for f in glob.glob(os.path.join(folder, "*")) if f.lower().endswith(VEXT))
        if not files: sys.exit(f"Tidak ada video di {folder}")
        for i, f in enumerate(files, 1):
            clips[f"{pre}{i:02d}"] = extract(B, f"{pre}{i:02d}", f, None, a.wall_dur, a.wall_h)
        print(f"video wall: {len(files)} klip unik ({pre}01..{pre}{len(files):02d}). Jangan tampilkan klip yang sama dua kali bersamaan.")
    json.dump(clips, open(cj, "w"), indent=1)
    print("-> clips.json diperbarui. Jalankan assemble.py lagi.")


if __name__ == "__main__":
    main()
