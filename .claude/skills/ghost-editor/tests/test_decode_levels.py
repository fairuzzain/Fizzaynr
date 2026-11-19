#!/usr/bin/env python3
"""Colour-level test for the RGB frame decoder (matte.frames, cutout_fx.Background) and the cutout Writer.

    ~/.venvs/ghost-matte/bin/python tests/test_decode_levels.py      # KEEP=1 keeps the files (TEST_DIR=... to choose where)

swscale's default yuv->rgb path (ffmpeg 8.1 on arm64) reads tv-range footage 1-2 levels dark (Y=235 -> 253, not 255)
whenever the width is not a multiple of 16 (1080 and 540 are not; 320 decodes fine, so the test frame is 360 wide).
The cutout Writer encodes back exactly, so every matte.frames -> Writer pass darkened the clip for real (talk.mp4,
one pass: Y -0.9, RGB -1.0..-2.0 levels). A synthetic source with known Y/U/V planes (a flat grey ramp 16..235 over
coloured 8 px blocks, lossless ffv1) is decoded and compared with the BT.709 spec decode of those planes:
  1. matte.frames (full size and half size) and the backdrop video decode match the spec within 0.5 per channel;
  2. the grey ramp decodes to within 1 level everywhere (16 -> 0, 235 -> 255);
  3. a full-range (pc) source still decodes to spec;
  4. matte.frames -> cutout_fx.Writer (H.264, production crf) -> spec decode stays within 1 level of the source.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
tmp = Path(tempfile.mkdtemp(prefix="decode-levels-", dir=os.environ.get("TEST_DIR")))
sys.path.insert(0, str(REPO / "scripts"))
import numpy as np  # noqa: E402

import cutout_fx as C  # noqa: E402

M = C.M
W, H, N, FPS = 360, 640, 8, 30
RAMP = 32  # rows of flat grey at the top


def planes(full):
    """Y/U/V planes: a horizontal grey ramp (neutral chroma) over random 8 px colour blocks, legal for the range."""
    rng = np.random.default_rng(7)
    lo, hi, clo, chi = (0, 255, 16, 240) if full else (16, 235, 64, 192)
    Y = np.kron(rng.integers(lo, hi + 1, (H // 8, W // 8)), np.ones((8, 8)))
    U = np.kron(rng.integers(clo, chi + 1, (H // 8, W // 8)), np.ones((4, 4)))
    V = np.kron(rng.integers(clo, chi + 1, (H // 8, W // 8)), np.ones((4, 4)))
    Y[:RAMP] = np.round(np.linspace(lo, hi, W))[None]
    U[:RAMP // 2] = V[:RAMP // 2] = 128
    return Y.astype(np.uint8), U.astype(np.uint8), V.astype(np.uint8)


def spec(Y, U, V, full):
    """BT.709 decode of the planes by the book (nearest-neighbour chroma)."""
    Y, U, V = (p.astype(np.float64) for p in (Y, U, V))
    U, V = U.repeat(2, 0).repeat(2, 1), V.repeat(2, 0).repeat(2, 1)
    y, u, v = (Y / 255, (U - 128) / 255, (V - 128) / 255) if full else ((Y - 16) / 219, (U - 128) / 224, (V - 128) / 224)
    return np.clip(np.stack([y + 1.5748 * v, y - 0.1873 * u - 0.4681 * v, y + 1.8556 * u], -1) * 255, 0, 255)


def write_src(path, Y, U, V, full):
    raw = (Y.tobytes() + U.tobytes() + V.tobytes()) * N
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{W}x{H}", "-r", str(FPS),
                    "-color_range", "pc" if full else "tv", "-colorspace", "bt709", "-i", "-", "-c:v", "ffv1",
                    "-color_range", "pc" if full else "tv", "-colorspace", "bt709", "-color_primaries", "bt709",
                    "-color_trc", "bt709", str(path)], input=raw, check=True)


def decode(path, size=(W, H)):
    info = M.probe(str(path))
    return info, np.mean([f.astype(np.float64) for f in M.frames(str(path), info, 0, 0, size)], 0)


def worst(a, b):
    return max(abs((a - b)[..., c].mean()) for c in range(3))


for full in (False, True):
    rng_name = "pc" if full else "tv"
    Y, U, V = planes(full)
    S = spec(Y, U, V, full)
    src = tmp / f"src-{rng_name}.mkv"
    write_src(src, Y, U, V, full)
    info, rgb = decode(src)
    assert info["color_range"] == rng_name, info
    d = worst(rgb, S)
    assert d < 0.5, f"{rng_name}: matte.frames is {d:.2f} levels off the spec decode"
    ramp = np.abs(rgb[2:RAMP - 2] - S[2:RAMP - 2]).max()
    assert ramp <= 1.0, f"{rng_name}: grey ramp off by {ramp:.1f} (end points {rgb[4, 0]} {rgb[4, -1]})"
    _, half = decode(src, (W // 2, H // 2))
    dh = max(abs(half[..., c].mean() - S[..., c].mean()) for c in range(3))
    assert dh < 0.5, f"{rng_name}: half-size decode mean is {dh:.2f} levels off"
    bg = np.mean([f.astype(np.float64) for f in C.Background(str(src), W, H, N, FPS).frames], 0)
    db = worst(bg, S)
    assert db < 0.5, f"{rng_name}: backdrop video decode is {db:.2f} levels off"
    print(f"ok {rng_name} decode: frames {d:.2f}, ramp max {ramp:.1f}, half size {dh:.2f}, backdrop {db:.2f} levels from spec")

# round trip: tv-range source -> matte.frames -> cutout_fx.Writer -> spec decode of the written planes
Y, U, V = planes(False)
S = spec(Y, U, V, False)
info = M.probe(str(tmp / "src-tv.mkv"))
out = tmp / "roundtrip.mp4"
w = C.Writer(out, W, H, FPS)
for f in M.frames(str(tmp / "src-tv.mkv"), info, 0, 0, (W, H)):
    w.write(f)
w.close()
oi = M.probe(str(out))
assert oi["color_range"] == "tv", oi
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"], capture_output=True, check=True).stdout
fs = W * H * 3 // 2
assert len(raw) == fs * N, (len(raw), fs * N)
outs = []
for k in range(N):
    p = np.frombuffer(raw[k * fs:(k + 1) * fs], np.uint8)
    outs.append(spec(p[:W * H].reshape(H, W), p[W * H:W * H * 5 // 4].reshape(H // 2, W // 2), p[W * H * 5 // 4:].reshape(H // 2, W // 2), False))
dr = [(np.mean(outs, 0) - S)[..., c].mean() for c in range(3)]
assert max(abs(x) for x in dr) < 1.0, f"round trip moved the levels by R {dr[0]:+.2f} G {dr[1]:+.2f} B {dr[2]:+.2f}"
print(f"ok tv round trip (matte.frames -> Writer): R {dr[0]:+.2f} G {dr[1]:+.2f} B {dr[2]:+.2f} levels")
print("ALL OK", tmp)
if not os.environ.get("KEEP"):
    shutil.rmtree(tmp, ignore_errors=True)
