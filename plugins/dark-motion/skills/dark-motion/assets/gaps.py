#!/usr/bin/env python3
"""Cari titik hening di suara untuk menyisipkan jeda (project.json -> pauses).

    python3 gaps.py <build> [--from 12] [--to 18] [--min .08] [--db -40]

Jeda yang disisipkan di tengah bunyi memotong kata. Jangan menebak posisinya dari words.json:
ukur dengan alat ini, lalu pakai detik "taruh jeda di" sebagai detik pertama di pauses.

Waktu memakai timeline SUMBER (sama dengan words.json / words_list.txt).
Panjang jeda yang dianjurkan:
  - hasil penggabungan / transformasi (A + B = C) : 1,5 - 2,0 dtk per hasil
  - kartu yang perlu dibaca (perbandingan, daftar)  : 1,5 - 2,5 dtk
  - napas sebelum penutup                           : 0,6 - 1,0 dtk
"""
import argparse, json, os, subprocess, sys
import numpy as np

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=1e9)
    ap.add_argument("--min", type=float, default=.08, help="panjang hening minimal (dtk)")
    ap.add_argument("--db", type=float, default=None, help="ambang hening (dBFS). Default: otomatis dari level suara")
    a = ap.parse_args()
    src = os.path.join(a.build, "src", "main.mp4")
    if not os.path.exists(src):
        sys.exit("src/main.mp4 belum ada.")
    raw = subprocess.run([FF, "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    hop = 320  # 20 ms
    n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    d = 20 * np.log10(e + 1e-9)
    thr = a.db if a.db is not None else float(np.percentile(d[d > -90], 70)) - 28
    quiet = d < thr

    words = []
    wp = os.path.join(a.build, "words.json")
    if os.path.exists(wp):
        words = json.load(open(wp))

    def near(t):
        prev = [w for w in words if w[0] <= t]
        nxt = [w for w in words if w[0] > t]
        return (prev[-1][1] if prev else "-"), (nxt[0][1] if nxt else "-")

    print(f"ambang hening {thr:.0f} dBFS | rentang {a.t0:.2f}-{min(a.t1, n/50):.2f} dtk")
    i0, i1 = int(a.t0 * 50), min(n, int(a.t1 * 50))
    i = i0; found = 0
    while i < i1:
        if quiet[i]:
            j = i
            while j < i1 and quiet[j]: j += 1
            ln = (j - i) / 50
            if ln >= a.min:
                mid = (i + j) / 2 / 50
                p, q = near(mid)
                print(f"  hening {i/50:6.2f}-{j/50:6.2f} ({ln:.2f} dtk)  taruh jeda di {mid:.2f}   [{p} | {q}]")
                found += 1
            i = j
        else:
            i += 1
    if not found:
        print("  tidak ada hening yang cukup panjang. Turunkan --min atau naikkan --db.")


if __name__ == "__main__":
    main()
