#!/usr/bin/env python3
"""Bakar efek ke frame, dan buat matte orang. Butuh opencv-python; mode matte butuh onnxruntime.

Filter yang harus MENYATU dengan gambar dikerjakan di sini, bukan sebagai lapisan CSS:
filter CSS mahal saat render per frame, dan hasilnya terlihat seperti lapisan yang ditempel.

    # grade sinematik + opening + glitch burst, frame 0-117
    python3 bake.py grade  vf/src vf/main --range 0:118 --soft --glow --scan --grain 11 \
        --burst 0:0.62:1 --burst 3.0:0.26:0.95 --open 0.42 --zoom 0.55:1.22

    # transisi glitch di sekitar satu titik potong
    python3 bake.py glitch vf/src vf/main --at 1789 --width 19 --ca 38

    # matte orang (PNG/WebP beralpha) untuk ditaruh di depan grafik
    python3 bake.py matte  vf/src vf/fg --range 280:353 --model u2net_human_seg.onnx

Frame yang tidak dibakar cukup di-symlink ke folder aslinya:
    for i in $(seq 119 2002); do n=$(printf %04d $i); ln -sf "$SRC/$n.jpg" "$DST/$n.jpg"; done

Model matte (176 MB, sekali unduh):
    https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx
"""
import argparse, os, sys
import cv2
import numpy as np

W, H, FPS = 1080, 1920, 30


def parse_pair(s, n=2, cast=float):
    return [cast(v) for v in s.split(":")[:n]]


def burst_energy(t, bursts):
    e = 0.0
    for at, dur, amp in bursts:
        if at <= t < at + dur:
            e = max(e, amp * (1 - (t - at) / dur) ** .7)
    return e


def grade(a):
    lo, hi = parse_pair(a.range, 2, int)
    bursts = [parse_pair(b, 3) for b in a.burst]
    c1 = np.array(a.c1, np.float32)
    c2 = np.array(a.c2, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - .42 * np.clip(((xx - W / 2) / (W * .72)) ** 2 + ((yy - H / 2) / (H * .72)) ** 2, 0, 1)[..., None]
    scan = (1 - .075 * ((yy.astype(int) % 4) < 2).astype(np.float32))[..., None] if a.scan else 1.0
    zoom_t, zoom_s = parse_pair(a.zoom, 2) if a.zoom else (0, 1)

    for i in range(lo, hi):
        t = (i - lo) / FPS
        rng = np.random.default_rng(1000 + i)
        im = cv2.imread(f"{a.src}/{i + 1:04d}.jpg").astype(np.float32)
        e = burst_energy(t, bursts)

        if zoom_t and t < zoom_t:
            z = 1 + (zoom_s - 1) * (1 - t / zoom_t) ** 2
            M = np.array([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z)]], np.float32)
            im = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        if a.soft:                      # melembutkan tampilan plastik tanpa menghilangkan detail
            im = im * .45 + cv2.GaussianBlur(im, (0, 0), 1.5) * .55
        if a.glow:                      # pendaran halus di area terang
            g = cv2.GaussianBlur(np.clip(im - 150, 0, 255), (0, 0), 22)
            im = 255 - (255 - im) * (255 - g * .55) / 255
        lum = im.mean(2, keepdims=True)
        im = lum + (im - lum) * a.sat
        im = (im - 128) * a.contrast + 124
        im[..., 0] += 5                 # bayangan sedikit biru

        wob = np.sin(np.arange(H) * .018 + t * 7) * 1.4 + np.sin(np.arange(H) * .11 + t * 19) * .6
        band = (t * 520) % (H + 300) - 150
        off = wob + np.exp(-((np.arange(H) - band) / 34) ** 2) * 16 + rng.normal(0, .35, H)
        if e > .02:
            for _ in range(int(5 + e * 26)):
                y = rng.integers(0, H); h = int(rng.integers(8, 34 + int(e * 120)))
                off[y:y + h] += rng.uniform(-1, 1) * 150 * e

        maps = xx + off[:, None].astype(np.float32)
        ca = a.ca0 + e * a.ca
        out = np.zeros_like(im)
        for ch, d in ((0, ca), (1, 0), (2, -ca)):
            out[..., ch] = cv2.remap(im[..., ch], maps + d, yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        if e > .15:
            for _ in range(int(2 + e * 12)):
                bw, bh = int(rng.integers(90, 520)), int(rng.integers(12, 70 + int(e * 90)))
                x, y = int(rng.integers(0, W - bw)), int(rng.integers(0, H - bh))
                roi = out[y:y + bh, x:x + bw]
                s = max(1, int(rng.integers(10, 30)))
                roi = cv2.resize(cv2.resize(roi, (max(1, bw // s), max(1, bh // s)), interpolation=cv2.INTER_AREA),
                                 (bw, bh), interpolation=cv2.INTER_NEAREST)
                if rng.random() < .55:
                    roi = roi * .55 + (c1 if rng.random() < .5 else c2) * .45
                out[y:y + bh, x:x + bw] = roi

        if a.grain:
            gr = cv2.resize(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (W, H))
            out = out + gr[..., None] * (a.grain + e * 18)
        out = out * scan * vig

        if a.open and t < a.open:       # sinyal menyala per baris dari hitam
            p = t / a.open
            mask = (rng.random(H // 26 + 1) < p ** .8).astype(np.float32).repeat(26)[:H][:, None, None]
            out = out * mask + (1 - p) ** 2 * 70 * mask

        cv2.imwrite(f"{a.dst}/{i + 1:04d}.jpg", np.clip(out, 0, 255).astype(np.uint8),
                    [cv2.IMWRITE_JPEG_QUALITY, a.q])
    print("grade", hi - lo, "frame")


def glitch(a):
    """Transisi glitch di sekitar satu titik potong. Intensitas berbentuk segitiga."""
    c1, c2 = np.array(a.c1, np.float32), np.array(a.c2, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    half = a.width / 2
    for f in range(a.at - int(half), a.at + int(half) + 1):
        e = max(0.0, 1 - abs(f - a.at) / half) ** .8
        rng = np.random.default_rng(5000 + f)
        src = f"{a.src}/{f:04d}.jpg"
        if not os.path.exists(src):
            continue
        im = cv2.imread(src).astype(np.float32)
        off = np.zeros(H)
        for _ in range(int(5 + e * 30)):
            y = rng.integers(0, H); h = int(rng.integers(8, 30 + int(e * 150)))
            off[y:y + h] += rng.uniform(-1, 1) * 190 * e
        maps = xx + off[:, None].astype(np.float32)
        ca = 3 + e * a.ca
        out = np.zeros_like(im)
        for ch, d in ((0, ca), (1, 0), (2, -ca)):
            out[..., ch] = cv2.remap(im[..., ch], maps + d, yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        for _ in range(int(e * 14)):
            bw, bh = int(rng.integers(90, 560)), int(rng.integers(12, 70 + int(e * 100)))
            x, y = int(rng.integers(0, W - bw)), int(rng.integers(0, H - bh))
            roi = out[y:y + bh, x:x + bw]
            s = int(rng.integers(12, 32))
            roi = cv2.resize(cv2.resize(roi, (max(1, bw // s), max(1, bh // s)), interpolation=cv2.INTER_AREA),
                             (bw, bh), interpolation=cv2.INTER_NEAREST)
            if rng.random() < .5:
                roi = roi * .55 + (c1 if rng.random() < .5 else c2) * .45
            out[y:y + bh, x:x + bw] = roi
        gr = cv2.resize(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (W, H))
        out = out + gr[..., None] * (e * 24)
        if abs(f - a.at) <= 1:
            out = out * 1.2 + 16
        dst = f"{a.dst}/{f:04d}.jpg"
        if os.path.islink(dst):
            os.remove(dst)
        cv2.imwrite(dst, np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, a.q])
    print("glitch", a.width, "frame di sekitar", a.at)


def matte(a):
    """Potong orang dari frame. Rata-rata 3 frame supaya tepinya tidak bergetar."""
    import onnxruntime as ort
    sess = ort.InferenceSession(a.model, providers=["CPUExecutionProvider"])
    name = sess.get_inputs()[0].name
    lo, hi = parse_pair(a.range, 2, int)
    frames, alphas = list(range(lo, hi)), []
    for f in frames:
        im = cv2.imread(f"{a.src}/{f + 1:04d}.jpg")
        x = cv2.cvtColor(cv2.resize(im, (320, 320), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        x = ((x - [.485, .456, .406]) / [.229, .224, .225]).transpose(2, 0, 1)[None].astype(np.float32)
        o = sess.run(None, {name: x})[0][0, 0]
        o = (o - o.min()) / (o.max() - o.min() + 1e-9)
        alphas.append(cv2.resize(o, (W, H), interpolation=cv2.INTER_CUBIC))
    for k, f in enumerate(frames):
        al = np.mean(alphas[max(0, k - 1):k + 2], axis=0)
        al = (np.clip((al - .22) / .5, 0, 1) * 255).astype(np.uint8)
        im = cv2.imread(f"{a.src}/{f + 1:04d}.jpg")
        cv2.imwrite(f"{a.dst}/{k + 1:04d}.webp", np.dstack([im, al]), [cv2.IMWRITE_WEBP_QUALITY, 92])
    print("matte", len(frames), "frame ->", a.dst, "(pakai vid(...,'webp'))")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["grade", "glitch", "matte"])
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--range", default="0:1", help="frameAwal:frameAkhir (0-based, akhir eksklusif)")
    ap.add_argument("--burst", action="append", default=[], help="detik:panjang:kekuatan")
    ap.add_argument("--open", type=float, default=0.0, help="detik transisi sinyal menyala")
    ap.add_argument("--zoom", default="", help="detik:skalaAwal")
    ap.add_argument("--soft", action="store_true"); ap.add_argument("--glow", action="store_true")
    ap.add_argument("--scan", action="store_true"); ap.add_argument("--grain", type=float, default=0)
    ap.add_argument("--sat", type=float, default=.82); ap.add_argument("--contrast", type=float, default=1.1)
    ap.add_argument("--ca", type=float, default=30, help="pemisahan RGB saat burst")
    ap.add_argument("--ca0", type=float, default=4.5, help="pemisahan RGB dasar")
    ap.add_argument("--at", type=int, default=0); ap.add_argument("--width", type=int, default=19)
    ap.add_argument("--model", default="u2net_human_seg.onnx")
    ap.add_argument("--q", type=int, default=93)
    ap.add_argument("--c1", type=float, nargs=3, default=[90, 239, 134], help="aksen 1 dalam BGR")
    ap.add_argument("--c2", type=float, nargs=3, default=[255, 169, 63], help="aksen 2 dalam BGR")
    a = ap.parse_args()
    os.makedirs(a.dst, exist_ok=True)
    {"grade": grade, "glitch": glitch, "matte": matte}[a.mode](a)
    # catat efek yang dibakar ke vf/main, supaya frames.py bisa memperingatkan kalau vf/main dibuat ulang
    dst = os.path.normpath(a.dst)
    if os.path.basename(dst) == "main" and os.path.basename(os.path.dirname(dst)) == "vf":
        build = os.path.dirname(os.path.dirname(dst))
        with open(os.path.join(build, "baked.txt"), "a") as f:
            f.write("bake.py " + " ".join(sys.argv[1:]) + "\n")


if __name__ == "__main__":
    main()
