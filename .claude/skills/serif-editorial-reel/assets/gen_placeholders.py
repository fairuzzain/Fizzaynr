#!/usr/bin/env python3
"""Aset palsu untuk menguji komponen tanpa bahan asli.

    python3 gen_placeholders.py <build> [detik=45]

Membuat:
  vf/main/     video utama palsu (gradien bergerak + tulisan WAJAH), <detik> dtk
  vf/c1..c6/   6 klip pendek 3 dtk (warna berbeda, bernomor)
  img/shot1..8.png   screenshot palsu 9:16
  img/avatar.png     foto profil palsu
Lalu salin examples/demo-scenes.js ke <build>/scenes.js dan jalankan build.py.
JANGAN dipakai untuk video user: ini hanya untuk uji.
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")
COLS = [(255, 70, 70), (60, 200, 120), (70, 140, 255), (250, 180, 40), (190, 90, 255), (40, 210, 220), (255, 120, 190), (150, 150, 160)]


def font(sz):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz)
            except OSError: pass
    return ImageFont.load_default()


def card(w, h, col, text, sub=""):
    im = Image.new("RGB", (w, h), (12, 12, 16)); d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h; d.line([(0, y), (w, y)], fill=tuple(int(c * (0.25 + 0.55 * (1 - k)) + 10 * k) for c in col))
    d.ellipse([w * .2, h * .18, w * .8, h * .18 + w * .6], outline=(255, 255, 255), width=max(2, w // 120))
    f = font(max(18, w // 7)); tw = d.textlength(text, font=f); d.text(((w - tw) / 2, h * .62), text, font=f, fill=(255, 255, 255))
    if sub:
        f2 = font(max(12, w // 16)); tw = d.textlength(sub, font=f2); d.text(((w - tw) / 2, h * .62 + w // 6), sub, font=f2, fill=(230, 230, 230))
    return im


def seq(src_png, out_dir, secs, h=None):
    os.makedirs(out_dir, exist_ok=True)
    vf = "hue=H=t*0.9,scale=%s,fps=30" % ("1080:1920" if not h else f"{int(h*9/16)//2*2}:{h}")
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-loop", "1", "-i", src_png, "-t", str(secs), "-vf", vf, "-q:v", "4",
                    os.path.join(out_dir, "%04d.jpg")], check=True)


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    B = sys.argv[1]; secs = float(sys.argv[2]) if len(sys.argv) > 2 else 45
    os.makedirs(os.path.join(B, "img"), exist_ok=True); tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "main.png"); card(1080, 1920, (120, 110, 140), "WAJAH", "video utama palsu").save(p)
    seq(p, os.path.join(B, "vf", "main"), secs)
    for i in range(6):
        p = os.path.join(tmp, f"c{i+1}.png"); card(540, 960, COLS[i], f"KLIP {i+1}").save(p)
        seq(p, os.path.join(B, "vf", f"c{i+1}"), 3, 640)
    for i in range(8):
        card(540, 960, COLS[i], f"SHOT {i+1}", "screenshot palsu").save(os.path.join(B, "img", f"shot{i+1}.png"))
    av = Image.new("RGB", (300, 300), (230, 80, 110)); ImageDraw.Draw(av).ellipse([90, 60, 210, 180], fill=(255, 225, 210)); av.save(os.path.join(B, "img", "avatar.png"))
    print(f"placeholder siap di {B}: vf/main ({secs:.0f} dtk), vf/c1..c6, img/shot1..8.png, img/avatar.png")


if __name__ == "__main__":
    main()
