#!/usr/bin/env python3
"""Unduh emoji 3D Microsoft Fluent (lisensi MIT) dari GitHub ke folder img/.

    python3 fetch_emoji.py <build>/img rocket face_with_spiral_eyes thumbs_up brick collision

Nama = nama emoji Fluent dalam huruf kecil dengan garis bawah (lihat daftar di
https://github.com/microsoft/fluentui-emoji/tree/main/assets). Hasil: img/<nama>.png,
dipakai lewat emoji('<nama>', ukuran). assemble.py memanggil ini otomatis untuk emoji yang belum ada.
Emoji yang punya warna kulit otomatis memakai versi Default.
"""
import os, subprocess, sys
from urllib.parse import quote

BASE = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets"


def candidates(n):
    words = n.split("_")
    dirs = {" ".join(words).capitalize(), " ".join(w.capitalize() for w in words), " ".join(words)}
    for d in dirs:
        yield f"{d}/3D/{n}_3d.png"
        yield f"{d}/Default/3D/{n}_3d_default.png"


def get(url, out):
    r = subprocess.run(["curl", "-sL", "--fail", "--max-time", "20", "-o", out, url])
    return r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 1000


def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    out_dir = sys.argv[1]; os.makedirs(out_dir, exist_ok=True)
    bad = []
    for n in sys.argv[2:]:
        out = os.path.join(out_dir, n + ".png")
        if os.path.exists(out): print("ada  ", n); continue
        ok = False
        for rel in candidates(n):
            if get(f"{BASE}/{quote(rel)}", out):
                ok = True; break
        if ok: print("ok   ", n)
        else:
            if os.path.exists(out): os.remove(out)
            bad.append(n); print("GAGAL", n)
    if bad:
        print("Emoji tidak ketemu:", ", ".join(bad))
        print("Cek nama persisnya di github.com/microsoft/fluentui-emoji/tree/main/assets (nama folder -> huruf kecil, spasi jadi _).")


if __name__ == "__main__":
    main()
