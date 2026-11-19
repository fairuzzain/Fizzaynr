import numpy as np, math, random, subprocess, wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 24
PW = 960                      # panel display width
PCY = 980                     # panel centre y
F_SFX = 'Bangers-Regular.ttf'
F_TXT = 'ComicNeue-Bold.ttf'
RED = (220, 30, 40)

def ease_back(x, c=1.8):
    x = min(max(x, 0), 1); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

# ---------- backgrounds ----------
def speedlines(dark):
    bg = Image.new('RGB', (W, H), (15, 15, 15) if dark else (250, 248, 242))
    d = ImageDraw.Draw(bg); rng = random.Random(3 if dark else 4)
    cx, cy = W / 2, H / 2; col = (235, 235, 235) if dark else (205, 205, 200)
    for i in range(170):
        a = rng.uniform(0, 2 * math.pi); w = rng.uniform(0.004, 0.018)
        r0 = rng.uniform(380, 700); r1 = 1600
        pts = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
               (cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)),
               (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))]
        d.polygon(pts, fill=col)
    if not dark:  # halftone dots corner
        for y in range(0, H, 22):
            for x in range(0, W, 22):
                r = max(0, 5 - math.hypot(x - W / 2, y - H / 2) / 260) if False else 0
    return bg
BG = {'light': speedlines(False), 'dark': speedlines(True)}

# ---------- panels ----------
PAN = {}
for i in range(1, 9):
    im = Image.open(f'P{i}.png').convert('RGB')
    s = PW / im.width
    PAN[i] = im.resize((PW, round(im.height * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
SC = PW / 420  # panel-coord -> display scale (approx; all panels ~420 wide)

def fnt(p, s): return ImageFont.truetype(p, s)

def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if font.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

_bc = {}
def bubble(text, tail, maxw=440, size=50, shape='oval'):
    """returns (img, anchor_offset): tail = (dx,dy) from bubble centre to tail tip, display px"""
    k = (text, tail, maxw, size, shape)
    if k in _bc: return _bc[k]
    f = fnt(F_TXT, size); lines = wrap(text, f, maxw)
    lh = size * 1.12; tw = max(f.getlength(l) for l in lines); th = lh * len(lines)
    rx, ry = tw / 2 * 1.32 + 30, th / 2 * 1.45 + 26
    pad = int(max(abs(tail[0]), abs(tail[1])) + 40)
    Wd, Hd = int(2 * rx + 2 * pad), int(2 * ry + 2 * pad)
    im = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = Wd / 2, Hd / 2
    ang = math.atan2(tail[1], tail[0])
    tip = (cx + tail[0], cy + tail[1])
    def on_ell(a_, inset=0):
        return (cx + math.cos(a_) * (rx - inset), cy + math.sin(a_) * (ry - inset))
    da = 0.22 if shape == 'oval' else 0.18
    b0, b1 = on_ell(ang - da), on_ell(ang + da)
    i0, i1 = on_ell(ang - da, 14), on_ell(ang + da, 14)
    box = (cx - rx, cy - ry, cx + rx, cy + ry)
    if shape == 'oval':
        d.ellipse(box, fill='white', outline='black', width=6)
    else:
        pts = []
        for j in range(28):
            a_ = 2 * math.pi * j / 28; r = 1.0 if j % 2 == 0 else 0.86
            pts.append((cx + math.cos(a_) * rx * r * 1.06, cy + math.sin(a_) * ry * r * 1.08))
        d.polygon(pts, fill='white', outline='black', width=6)
    d.polygon([i0, i1, tip], fill='white')
    d.polygon([b0, b1, tip], fill='white')
    d.line([b0, tip], fill='black', width=6); d.line([b1, tip], fill='black', width=6)
    d.polygon([i0, i1, ((b0[0] + b1[0]) / 2 * 0.5 + tip[0] * 0.5, (b0[1] + b1[1]) / 2 * 0.5 + tip[1] * 0.5)], fill='white')
    y = cy - th / 2
    for l in lines:
        d.text((cx - f.getlength(l) / 2, y), l, font=f, fill='black'); y += lh
    _bc[k] = (im, (cx, cy)); return _bc[k]

_sc = {}
def sfx(text, size, fill=RED, stroke=(0, 0, 0), outer=(255, 255, 255)):
    k = (text, size, fill)
    if k in _sc: return _sc[k]
    f = fnt(F_SFX, size); sw = max(6, size // 12)
    b = f.getbbox(text, stroke_width=sw * 3)
    im = Image.new('RGBA', (b[2] - b[0] + 20, b[3] - b[1] + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = (-b[0] + 10, -b[1] + 10)
    d.text(o, text, font=f, fill=outer, stroke_width=sw * 3, stroke_fill=outer)
    d.text(o, text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    _sc[k] = im; return im

_nc = {}
def narr(text, size=54):
    if text in _nc: return _nc[text]
    f = fnt(F_TXT, size); lines = wrap(text, f, 860)
    lh = size * 1.15; tw = max(f.getlength(l) for l in lines)
    im = Image.new('RGBA', (int(tw + 60), int(lh * len(lines) + 40)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, im.width - 1, im.height - 1), fill=(255, 225, 60), outline='black', width=6)
    y = 20
    for l in lines: d.text(((im.width - f.getlength(l)) / 2, y), l, font=f, fill='black'); y += lh
    _nc[text] = im; return im

# ---------- timeline ----------
# panel: (id, t0, t1, bg, enter, base_rot)
PANELS = [
    (1, 0.0, 7.3, 'light', 'right', -1.5),
    (2, 7.3, 12.9, 'light', 'left', 1.5),
    (3, 12.9, 17.6, 'light', 'right', -1.2),
    (4, 17.6, 19.3, 'dark', 'slam', 2.0),
    (5, 19.3, 22.4, 'light', 'left', -1.0),
    (6, 22.4, 25.85, 'dark', 'slam', 1.5),
    (7, 25.85, 29.95, 'light', 'right', -1.5),
    (8, 29.95, 34.3, 'light', 'left', 1.2),
]
# items attached to panels, panel coords (420-wide space): kind, panel, t0, x, y, payload
ITEMS = [
    ('sfx', 1, 1.2, 360, 470, ('HAHA!', 110), -10),
    ('bub', 1, 3.3, 250, -10, ('Aku muda, sihat. Takaful? Tak perlu la!', (-150, 190), 'oval'), 0),
    ('bub', 2, 7.6, 290, 105, ('Jom ambil takaful, Ali!', (-170, 40), 'oval'), 0),
    ('bub', 2, 10.95, 250, 470, ('Nanti-nanti la bro.', (110, -150), 'oval'), 0),
    ('sfx', 3, 15.27, 330, 390, ('WOOSH!', 120), -12),
    ('sfx', 4, 17.64, 210, 470, ('KRAK!!', 250), -8),
    ('bill', 6, 23.2, 140, 360, None, -9),
    ('sfx', 6, 24.44, 250, -20, ('BELASAN RIBU?!', 150), -4),
    ('bub', 7, 26.0, 150, 60, ('Amir... aku nak daftar sekarang!', (80, 260), 'jag'), 0),
    ('bub', 8, 30.1, 150, 30, ('Boleh. Tapi yang ni kau bayar sendiri la bro.', (170, 230), 'oval'), 0),
    ('sfx', 8, 33.52, 330, 500, ('HEHE', 100), 8),
]
NARR = [(0.2, 7.1, 'Ni Ali.'), (7.47, 12.8, 'Kawan dia, Amir, dah banyak kali ajak.'),
        (12.98, 17.5, 'Satu hari, Ali main futsal...'), (19.5, 22.3, 'Masuk hospital. Kaki bersimen.'),
        (22.56, 25.7, 'Lepas tu dia tengok bil...')]
OUT_T = 34.3; DUR = 39.6
SHAKE = [(17.64, 0.5, 30), (24.44, 0.35, 14)]
FLASH = [17.64]

def bill_img():
    f1, f2 = fnt(F_TXT, 40), fnt(F_SFX, 92)
    im = Image.new('RGBA', (440, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((20, 10), 'BIL HOSPITAL', font=f1, fill=(40, 40, 40))
    d.line((20, 62, 420, 62), fill=(60, 60, 60), width=3)
    for i in range(3): d.line((20, 85 + i * 22, 300 - i * 50, 85 + i * 22), fill=(150, 150, 150), width=6)
    d.text((20, 150), 'RM 1X,XXX', font=f2, fill=RED)
    return im
BILL = bill_img()

def panel_layer(pid, t, t0):
    art = PAN[pid]; dur = [p for p in PANELS if p[0] == pid][0]
    z = 1 + 0.06 * min(max((t - t0) / (dur[2] - dur[1]), 0), 1)  # slow push-in
    w, h = art.size
    cw, ch = w / z, h / z
    crop = art.crop((int((w - cw) / 2), int((h - ch) / 2), int((w + cw) / 2), int((h + ch) / 2))).resize((w, h), Image.BILINEAR)
    M = 330
    L = Image.new('RGBA', (w + 2 * M, h + 2 * M), (0, 0, 0, 0))
    # drop shadow
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 110))
    L.alpha_composite(sh, (M + 16, M + 22))
    L.paste(crop, (M, M))
    ImageDraw.Draw(L).rectangle((M, M, M + w - 1, M + h - 1), outline='black', width=12)
    for kind, p, it0, x, y, pay, rot in ITEMS:
        if p != pid or t < it0: continue
        k = t - it0
        if kind == 'bub':
            img, (cx, cy) = bubble(pay[0], pay[1], shape=pay[2]); s = ease_back(k / 0.25)
        elif kind == 'sfx':
            img = sfx(*pay); cx, cy = img.width / 2, img.height / 2
            s = (1.8 - 0.8 * min(k / 0.18, 1)) if k < 0.18 else 1 + 0.05 * math.sin(k * 30) * math.exp(-k * 6)
        else:
            img = BILL; cx, cy = img.width / 2, img.height / 2; s = ease_out(k / 0.2)
        if rot or abs(s - 1) > 1e-3:
            img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            cx, cy = cx * s, cy * s
            if rot:
                ow, oh = img.size; img = img.rotate(rot, Image.BICUBIC, expand=True)
                cx += (img.width - ow) / 2; cy += (img.height - oh) / 2
        L.alpha_composite(img, (int(M + x * SC - cx), int(M + y * SC - cy)))
    return L, M

def place(frame, L, cx, cy, rot, scale=1.0):
    if scale < 0.02: return
    if abs(scale - 1) > 1e-3:
        L = L.resize((int(L.width * scale), int(L.height * scale)), Image.BILINEAR)
    if abs(rot) > 0.05: L = L.rotate(rot, Image.BICUBIC, expand=True)
    frame.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def compose(t):
    if t >= OUT_T:
        frame = BG['dark'].copy().convert('RGBA'); k = t - OUT_T
        L, M = panel_layer(7, 29.9, 25.85)
        L = L.crop((M - 20, M - 20, L.width - M + 40, L.height - M + 40))
        place(frame, L, W / 2, 780, -4, 0.55 * ease_back(k / 0.35))
        if k > 0.2:
            im = sfx('JANGAN TUNGGU', 150); s = ease_back((k - 0.2) / 0.25)
            place(frame, im, W / 2, 1320, -3, s)
        if k > 0.6:
            im = sfx('JADI ALI.', 170); place(frame, im, W / 2, 1480, -3, ease_back((k - 0.6) / 0.25))
        if t > 36.18:
            im = narr('Lindungi diri sebelum terlambat.', 52); place(frame, im, W / 2, 1680, 0, ease_back((t - 36.18) / 0.25))
        if t > DUR - 0.4:
            a = (t - (DUR - 0.4)) / 0.4; frame = Image.blend(frame, Image.new('RGBA', (W, H), (0, 0, 0, 255)), a)
        return frame.convert('RGB')
    idx = max(i for i, p in enumerate(PANELS) if p[1] <= t)
    pid, t0, t1, bg, enter, brot = PANELS[idx]
    frame = BG[bg].copy().convert('RGBA'); k = t - t0
    # outgoing panel
    if idx > 0 and k < 0.3 and enter != 'slam':
        pp = PANELS[idx - 1]; L, _ = panel_layer(pp[0], t, pp[1])
        dirx = -1 if enter == 'right' else 1
        place(frame, L, W / 2 + dirx * ease_out(k / 0.3) * 1400, PCY, pp[5] + dirx * 10 * ease_out(k / 0.3))
    L, _ = panel_layer(pid, t, t0)
    if enter == 'slam':
        s = 1.35 - 0.35 * ease_out(k / 0.15); place(frame, L, W / 2, PCY, brot, s)
    else:
        x = 1 - ease_back(k / 0.4); dirx = 1 if enter == 'right' else -1
        place(frame, L, W / 2 + dirx * x * 1300, PCY, brot + dirx * x * 12)
    for n0, n1, txt in NARR:
        if n0 <= t < n1:
            im = narr(txt); s = ease_back((t - n0) / 0.25) if t - n0 < 0.3 else 1
            if n1 - t < 0.15: s *= (n1 - t) / 0.15
            if s > 0.02: place(frame, im, W / 2, 1790, -1, s)
    out = frame.convert('RGB')
    for st, d, amp in SHAKE:
        if st <= t < st + d:
            a = amp * (1 - (t - st) / d); rr = random.Random(int(t * 48))
            dx, dy = int(rr.uniform(-a, a)), int(rr.uniform(-a, a))
            o2 = Image.new('RGB', (W, H), (15, 15, 15)); o2.paste(out, (dx, dy)); out = o2
    for fl in FLASH:
        if fl <= t < fl + 0.1: out = Image.blend(out, Image.new('RGB', (W, H), 'white'), 0.75)
    return out

EVENTS = dict(whoosh=[p[1] for p in PANELS[1:] if p[4] != 'slam'] + [OUT_T],
              slam=[17.64, 22.4, 24.44], pop=[it[2] for it in ITEMS if it[0] == 'bub'] + [36.18],
              sfx=[it[2] for it in ITEMS if it[0] == 'sfx' and it[2] not in (17.64, 24.44)])

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ts = [float(x) for x in sys.argv[1:]]
        S = Image.new('RGB', (270 * min(4, len(ts)), 480 * math.ceil(len(ts) / 4)), 'white')
        for i, t in enumerate(ts): S.paste(compose(t).resize((270, 480)), ((i % 4) * 270, (i // 4) * 480))
        S.save('grid.jpg'); sys.exit()
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                          '-pix_fmt', 'yuv420p', 'video.mp4'], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): p.stdin.write(compose(i / FPS).tobytes())
    p.stdin.close(); p.wait()
