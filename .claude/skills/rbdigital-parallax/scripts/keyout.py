#!/usr/bin/env python3
"""Chroma-key a character/fg sheet and split it into separate cut-outs.
Usage:
  python3 keyout.py c1.png --key green   --split x  --prefix p     -> p1_cut.png p2_cut.png p3_cut.png
  python3 keyout.py f1.png --key magenta --split y  --prefix f1_   -> f1_1_cut.png f1_2_cut.png
  --split x|y            auto-split on empty gaps (default x).  --cuts 0,850,1700,2560 to set the cut lines by hand.
  --start 4              number the outputs from 4 (second character sheet -> p4..p6)
  --key green|magenta    green (#00FF00) by default; magenta (#FF00FF) when the sheet has leaves/plants/green items.
Always writes <name>_contact.png (cut-outs on a contrasting checker) -> LOOK at it before rendering."""
import sys, argparse, numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import binary_opening, label

ap = argparse.ArgumentParser(); ap.add_argument("img"); ap.add_argument("--key", default="green")
ap.add_argument("--split", default="x"); ap.add_argument("--cuts"); ap.add_argument("--prefix"); ap.add_argument("--min_part", type=float, default=.05); ap.add_argument("--start", type=int, default=1)
A = ap.parse_args()
im = Image.open(A.img).convert("RGB"); a = np.asarray(im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
mx, mn = a.max(2), a.min(2)
if A.key == "green":  # generators give muted green (~140,190,100) + soft shadows: key by hue, not by pure #00FF00
    d = g-np.maximum(r, b); bg = ((d > 19) & (mx-mn > 42) & (g > 35)) | ((d > 7) & (mx < 120))
else:                 # magenta: R and B both well above G
    d = np.minimum(r, b)-g; bg = ((d > 25) & (mx-mn > 42) & (np.maximum(r, b) > 60)) | ((d > 9) & (mx < 120))
fgm = binary_opening(~binary_opening(bg, iterations=1), iterations=2)  # no hole filling: gaps between arms/legs stay open

def parts(mask, axis):
    occ = mask.any(axis=0 if axis == "x" else 1); n = len(occ)
    if A.cuts: cuts = [int(v) for v in A.cuts.split(",")]; return list(zip(cuts[:-1], cuts[1:]))
    segs, s, gap = [], None, max(12, n//80)
    i = 0
    while i < n:
        if occ[i] and s is None: s = i
        if not occ[i] and s is not None:
            j = i
            while j < n and not occ[j]: j += 1
            if j-i >= gap or j == n: segs.append((s, i)); s = None
            i = j; continue
        i += 1
    if s is not None: segs.append((s, n))
    big = max(e-b_ for b_, e in segs); return [(b_, e) for b_, e in segs if e-b_ > .15*big]

alpha = Image.fromarray((fgm*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
al = np.asarray(alpha).astype(int); out = a.copy()
edge = (al > 0) & (al < 250) | (np.asarray(alpha.filter(ImageFilter.MinFilter(7))) < 250) & (al > 0)
if A.key == "green": out[..., 1] = np.where(edge, np.minimum(g, np.maximum(r, b)+12), g)        # despill
else:
    sp = np.clip(np.minimum(r, b)-g-12, 0, None); out[..., 0] = np.where(edge, r-sp, r); out[..., 2] = np.where(edge, b-sp, b)
rgba = np.dstack([np.clip(out, 0, 255), al]).astype(np.uint8)

pre = A.prefix or A.img.rsplit(".", 1)[0]+"_"; files = []
for k, (s0, e0) in enumerate(parts(fgm, A.split), A.start):
    sub = rgba[:, s0:e0] if A.split == "x" else rgba[s0:e0]; m = sub[..., 3] > 128
    lab, n = label(m)
    if n > 1:  # drop stray patches: keep components >= min_part of the largest
        sz = np.bincount(lab.ravel())[1:]; keep = np.isin(lab, 1+np.where(sz >= A.min_part*sz.max())[0])
        near = np.asarray(Image.fromarray(keep.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5))) > 0  # keep soft edges
        sub = sub.copy(); sub[..., 3] = np.where(near, sub[..., 3], 0)
    p = Image.fromarray(sub); bb = p.getbbox()
    if not bb: continue
    p = p.crop(bb); f = f"{pre}{k}_cut.png"; p.save(f); files.append(f)
    print(f, p.size, f"coverage={(np.asarray(p)[..., 3] > 128).mean():.2f}")
if not files: sys.exit("EMPTY: nothing left after keying - check --key or regenerate with a cleaner background")
# contact sheet on a checker in a colour that is NOT the key colour, so halos show up
ims = [Image.open(f) for f in files]; th = 420; ims = [i.resize((max(1, int(i.width*th/i.height)), th)) for i in ims]
Wc = sum(i.width for i in ims)+20*(len(ims)+1); sheet = Image.new("RGB", (Wc, th+40))
c1, c2 = ((255, 0, 255), (60, 60, 60)) if A.key == "green" else ((0, 220, 0), (60, 60, 60))
ck = np.indices((th+40, Wc)).sum(0)//24 % 2; sheet = Image.fromarray(np.where(ck[..., None] == 0, c1, c2).astype(np.uint8))
x = 20
for i in ims: sheet.paste(i, (x, 20), i); x += i.width+20
cf = A.img.rsplit(".", 1)[0]+"_contact.png"; sheet.save(cf); print("contact sheet:", cf)
