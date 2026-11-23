#!/usr/bin/env python3
"""Usulkan brand.json dari logo / gambar brand user (untuk user yang tidak punya brand guideline).

    python3 palette.py logo.png [gambar2.jpg ...] [--write <build>/brand.json]

Cara kerjanya: kecilkan gambar, buang piksel transparan, abu-abu, terlalu gelap/terang,
kelompokkan menurut hue, ambil warna paling menonjol sebagai accent. Latar tetap gelap
berwarna (charcoal yang sedikit diwarnai accent), sesuai gaya skill ini.
Hasilnya USULAN: tunjukkan ke user dan minta persetujuan singkat sebelum dipakai.
Kalau gambar hampir tanpa warna, usulkan accent merah bawaan (#c8101e).
"""
import colorsys, json, subprocess, sys, os
import numpy as np

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")


def pixels(path):
    r = subprocess.run([FF, "-nostdin", "-v", "error", "-i", path, "-vf", "scale=160:-1", "-frames:v", "1",
                        "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        print("lewati (tidak terbaca):", path); return np.zeros((0, 3))
    a = np.frombuffer(r.stdout, np.uint8).reshape(-1, 4).astype(float)
    return a[a[:, 3] > 200][:, :3] / 255


def main():
    args = sys.argv[1:]
    out = None
    if "--write" in args:
        i = args.index("--write"); out = args[i + 1]; del args[i:i + 2]
    if not args: sys.exit(__doc__)
    px = np.concatenate([pixels(p) for p in args]) if args else np.zeros((0, 3))
    hls = np.array([colorsys.rgb_to_hls(*c) for c in px]) if len(px) else np.zeros((0, 3))
    ok = (hls[:, 2] > .35) & (hls[:, 1] > .18) & (hls[:, 1] < .85) if len(hls) else np.zeros(0, bool)
    if ok.sum() < 50:
        acc = "#c8101e"; why = "gambar hampir tanpa warna, pakai accent bawaan"
    else:
        h = hls[ok]
        hist, edges = np.histogram(h[:, 0] * 360, bins=36, range=(0, 360), weights=h[:, 2])
        b = int(np.argmax(hist)); sel = h[(h[:, 0] * 360 >= edges[b]) & (h[:, 0] * 360 < edges[b + 1])]
        hue, light, sat = float(np.median(sel[:, 0])), float(np.median(sel[:, 1])), float(np.median(sel[:, 2]))
        light = min(max(light, .38), .55); sat = max(sat, .65)
        r, g, bb = colorsys.hls_to_rgb(hue, light, sat)
        acc = "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(bb * 255)); why = f"hue {hue*360:.0f} dari gambar"
    r, g, bb = [int(acc[i:i + 2], 16) for i in (1, 3, 5)]
    bg = "#%02x%02x%02x" % tuple(round(14 * .9 + c * .035) for c in (r, g, bb))
    brand = {"accent": acc, "bg": bg, "ink": "#141414", "paper": "#ffffff", "font": "Poppins", "success": "#16a34a"}
    print(json.dumps(brand, indent=1)); print("alasan:", why)
    print("Warna turunan (accentHi, tint chip, blob latar) dihitung otomatis oleh assemble.py.")
    if out:
        json.dump(brand, open(out, "w"), indent=1); print("->", out)


if __name__ == "__main__":
    main()
