#!/usr/bin/env python3
"""Usulkan dua warna aksen dari footage, sudah dicerahkan supaya terbaca di latar gelap.

    python3 palette.py <build>

Cara kerjanya: ambil 12 frame, buang piksel kulit, abu-abu, terlalu gelap, dan terlalu terang,
kelompokkan warna yang tersisa, pilih dua kelompok yang paling menonjol dan berbeda hue-nya,
lalu naikkan kecerahan dan saturasinya. Kalau footage hampir tanpa warna, pakai default netral.
Hasilnya usulan. Kalau user memberi warna brand, warna brand yang menang.
"""
import colorsys, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vision as V  # noqa: E402

DEFAULT = ("#86EF5A", "#3FA9FF")


def main():
    B = sys.argv[1]
    files = sorted(glob.glob(os.path.join(B, "vf", "main", "*.jpg")))
    if not files or not V.available():
        print("C1", DEFAULT[0], "C2", DEFAULT[1], "(default netral)"); return
    import numpy as np, cv2
    px = []
    for f in files[:: max(1, len(files) // 12)][:12]:
        im = cv2.resize(cv2.imread(f), (108, 192))
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).reshape(-1, 3).astype(float)
        h, s, v = hsv[:, 0] * 2, hsv[:, 1] / 255, hsv[:, 2] / 255
        skin = (h < 50) & (s > .15) & (s < .7) & (v > .25)
        ok = (s > .35) & (v > .2) & (v < .97) & ~skin
        px.append(hsv[ok])
    px = np.concatenate(px) if px else np.zeros((0, 3))
    if len(px) < 300:
        print("C1", DEFAULT[0], "C2", DEFAULT[1], "(footage hampir tanpa warna, pakai default netral)"); return
    hue = px[:, 0] * 2
    hist, edges = np.histogram(hue, bins=24, range=(0, 360), weights=px[:, 1])
    order = np.argsort(hist)[::-1]
    picks = []
    red = lambda c: c >= 340 or c < 18     # merah hanya kalau user minta: terasa "bahaya/murah" kalau dipakai sebagai aksen
    order = [b for b in order if not red((edges[b] + edges[b + 1]) / 2)] + [b for b in order if red((edges[b] + edges[b + 1]) / 2)]
    for b in order:
        c = (edges[b] + edges[b + 1]) / 2
        if red(c) and len(picks) < 2 and hist[b] > 0: continue
        if all(min(abs(c - p), 360 - abs(c - p)) > 50 for p in picks):
            picks.append(c)
        if len(picks) == 2: break
    while len(picks) < 2: picks.append((picks[0] + 180) % 360 if picks else 120)
    out = []
    for hdeg in picks:
        r, g, b = colorsys.hls_to_rgb(hdeg / 360, 0.66, 0.9)   # terang dan jenuh: terbaca di latar gelap
        out.append("#%02X%02X%02X" % (int(r * 255), int(g * 255), int(b * 255)))
    print("C1", out[0], "C2", out[1], f"(hue {picks[0]:.0f} dan {picks[1]:.0f} dari footage)")
    print("C1 dipakai untuk positif/pilihan, C2 untuk info/teknis. Tukar kalau terasa lebih cocok.")


if __name__ == "__main__":
    main()
