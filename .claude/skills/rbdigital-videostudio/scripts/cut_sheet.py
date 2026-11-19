"""Cut individual stickers out of a sticker-sheet image.

Usage:
  python cut_sheet.py SHEET.jpg OUT_DIR --names A1,A2,A3,... [--cols 4] [--rows 4]

Handles three background types automatically:
  - fake transparency checkerboard (Flow/Imagen often bakes this in)
  - solid colour background (e.g. green/grey)
  - plain white (works only if stickers have a shadow/dark outline; prefer non-white bg)
Stickers are sorted row by row (top-left first) and named in the order of --names.
Also writes OUT_DIR/_check.png (all cutouts on magenta) for visual verification.
"""
import argparse, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument('sheet'); ap.add_argument('out')
ap.add_argument('--names', required=True)
ap.add_argument('--rows', type=int, default=0, help='grid rows (for sorting); 0 = auto')
ap.add_argument('--min_area', type=int, default=2500)
args = ap.parse_args()
names = args.names.split(',')

im = Image.open(args.sheet).convert('RGB')
a = np.array(im).astype(int)
Hh, Ww = a.shape[:2]
mn = a.min(-1); chroma = a.max(-1) - a.min(-1)

edge = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
edge_chroma = (edge.max(1) - edge.min(1)).mean(); edge_lum = edge.mean()
if edge_chroma < 12 and edge_lum < 190:
    mode = 'checker/grey'
    m = (mn > 175) | (chroma > 35)
elif edge_lum > 235 and edge_chroma < 12:
    mode = 'white'
    m = (a.mean(-1) < 238) | (chroma > 20)  # relies on shadow/outline
else:
    mode = 'solid-colour'
    bgc = np.median(edge, 0)
    m = np.linalg.norm(a - bgc, axis=-1) > 60
print('background mode:', mode)

m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = ndi.binary_fill_holes(m)
m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
lab, n = ndi.label(m)
objs = ndi.find_objects(lab)
items = []
for i, s in enumerate(objs):
    area = (lab[s] == i + 1).sum()
    if area < args.min_area: continue
    cy = (s[0].start + s[0].stop) / 2; cx = (s[1].start + s[1].stop) / 2
    items.append([cy, cx, i + 1, s])

# row grouping
rows = args.rows or max(1, round(len(items) ** 0.5))
band = Hh / rows
items.sort(key=lambda it: (int(it[0] // band), it[1]))
print(f'found {len(items)} stickers, {len(names)} names')
if len(items) != len(names):
    print('WARNING: count mismatch — check _check.png and fix names/rows/min_area')

import os; os.makedirs(args.out, exist_ok=True)
check = Image.new('RGB', (1024, 1024), (255, 0, 255))
cols = max(1, int(np.ceil(len(items) / rows)))
cell = 1024 // max(rows, cols)
for k, (nm, (cy, cx, l, s)) in enumerate(zip(names, items)):
    mask = cv2.GaussianBlur((lab == l).astype(np.uint8) * 255, (3, 3), 0)
    rgba = np.dstack([np.array(im), mask])
    y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
    sp = Image.fromarray(rgba[y0:y1, x0:x1])
    sp.save(f'{args.out}/{nm}.png')
    t = sp.copy(); t.thumbnail((cell - 12, cell - 12))
    check.paste(t, ((k % cols) * cell + 6, (k // cols) * cell + 6), t)
    print(nm, x1 - x0, y1 - y0)
check.save(f'{args.out}/_check.png')
