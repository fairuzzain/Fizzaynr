import numpy as np, math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

W, H, FPS = 1080, 1920, 24
WW, WH = 1728, 3072                      # world (board) size
MARK = 'PermanentMarker-Regular.ttf'; TYPE = 'SpecialElite-Regular.ttf'
DUR = 41.6

def ease(x):
    x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ease_back(x, c=1.6):
    x = min(max(x, 0), 1); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- board ----------
BOARD = Image.open('bg.png').convert('RGB').resize((WW, WH), Image.LANCZOS)
BOARD = ImageEnhance.Brightness(BOARD).enhance(0.8)

# ---------- photos -> polaroids ----------
def quads(f):
    im = Image.open(f).convert('RGB')
    boxes = [(4, 4, 619, 619), (635, 4, 1250, 619), (4, 633, 619, 1250), (635, 633, 1250, 1250)]
    return [im.crop(b) for b in boxes]
PH = quads('s1.png') + quads('s2.png')
PS = 440
def polaroid(ph, seed):
    r = random.Random(seed); m, bot = 30, 120
    ph = ph.resize((PS, PS), Image.LANCZOS)
    ph = ImageEnhance.Contrast(ph).enhance(1.08)
    fr = Image.new('RGB', (PS + 2 * m, PS + m + bot), (236, 230, 214))
    n = (np.random.default_rng(seed).normal(0, 6, (fr.height, fr.width, 1))).astype(int)
    fr = Image.fromarray(np.clip(np.array(fr).astype(int) + n, 0, 255).astype(np.uint8))
    fr.paste(ph, (m, m))
    d = ImageDraw.Draw(fr)
    d.rectangle((m - 1, m - 1, m + PS, m + PS), outline=(60, 55, 50), width=2)
    img = fr.convert('RGBA')
    return img
POL = [polaroid(p, i) for i, p in enumerate(PH)]

def shadowed(img, off=(12, 18), blur=12, alpha=0.55):
    pad = 40
    c = Image.new('RGBA', (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh.putalpha(img.split()[3].point(lambda v: v * alpha))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)), (pad + off[0], pad + off[1]))
    c.alpha_composite(img, (pad, pad)); return c

def pin_img(col=(200, 25, 30)):
    s = 60; im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((14, 18, 50, 54), fill=(0, 0, 0, 120))
    d.ellipse((8, 8, 44, 44), fill=col + (255,), outline=(90, 10, 10, 255), width=2)
    d.ellipse((15, 13, 27, 23), fill=(255, 190, 190, 220))
    return im.filter(ImageFilter.GaussianBlur(0.6))
PIN = pin_img()

def note_img(text, size=46, color=(20, 18, 18), w=400, seed=0):
    f = ImageFont.truetype(MARK, size); r = random.Random(seed)
    words, lines, cur = text.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if f.getlength(t) <= w - 50 or not cur: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur)
    lh = size * 1.2; h = int(lh * len(lines) + 70)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for x in range(0, w + 1, 20): pts.append((x, r.uniform(0, 8)))
    for y in range(0, h + 1, 20): pts.append((w - r.uniform(0, 8), y))
    for x in range(w, -1, -20): pts.append((x, h - r.uniform(0, 8)))
    for y in range(h, -1, -20): pts.append((r.uniform(0, 8), y))
    d.polygon(pts, fill=(232, 222, 196, 255))
    y = 36
    for l in lines:
        d.text(((w - f.getlength(l)) / 2, y), l, font=f, fill=color); y += lh
    return im

RED = (170, 10, 15)
# photo slots: (index, t_pin, world x, y, rot)
PHOTOS = [
    (0, 0.25, 480, 480, -6), (1, 7.2, 1240, 540, 5), (2, 11.45, 490, 1190, 4), (3, 13.6, 1235, 1250, -5),
    (4, 19.28, 480, 1900, -3), (5, 22.78, 1245, 1960, 6), (6, 28.1, 500, 2600, 5), (7, 35.64, 1230, 2640, -4),
]
_NB = 590 / 2 + 15
NOTES = [  # text, t, x, y, rot, color
    ('RM300 / bulan??', 2.0, 480 + 150, 480 + _NB, 7, RED),
    ('JANGAN BUKA bilik belakang', 9.5, 1240 - 120, 540 + _NB + 10, -6, RED),
    ('3:00 AM ... tok tok tok', 15.1, 1235 - 130, 1250 + _NB + 10, 5, (20, 18, 18)),
    ('Siapa buka??', 21.85, 480 + 150, 1900 + _NB, -7, RED),
    ('Aku sorang je masa ni...', 30.66, 500 + 150, 2600 + _NB + 10, -4, (20, 18, 18)),
]

def pol_sprite(i, rot):
    return shadowed(POL[i]).rotate(rot, Image.BICUBIC, expand=True)
PSPR = {p[0]: pol_sprite(p[0], p[4]) for p in PHOTOS}
NSPR = [shadowed(note_img(n[0], color=n[5], seed=k), off=(6, 10), blur=6).rotate(n[4], Image.BICUBIC, expand=True) for k, n in enumerate(NOTES)]

def pin_pos(p):  # top-centre of polaroid in world coords (rotated)
    _, _, x, y, rot = p; h = POL[0].height
    a = math.radians(-rot); dx, dy = 0, -h / 2 + 30
    return (x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a))

# items with (t_start, duration, draw_fn(world_img, progress))
ITEMS = []
def draw_photo(p):
    spr = PSPR[p[0]]
    def f(img, k):
        s = 1.25 - 0.25 * ease(k); a = min(1, k * 2.5)
        im = spr if abs(s - 1) < 1e-3 else spr.resize((int(spr.width * s), int(spr.height * s)), Image.BILINEAR)
        if a < 1:
            im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
        img.alpha_composite(im, (int(p[2] - im.width / 2), int(p[3] - im.height / 2)))
        if k >= 1:
            px, py = pin_pos(p); img.alpha_composite(PIN, (int(px - 26), int(py - 26)))
    return f
def draw_note(n, spr):
    def f(img, k):
        s = ease_back(k)
        if s < 0.02: return
        im = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BILINEAR)
        img.alpha_composite(im, (int(n[2] - im.width / 2), int(n[3] - im.height / 2)))
        cx, cy = n[2], n[3] - spr.height / 2 + 40
        if k >= 1: img.alpha_composite(PIN, (int(cx - 26), int(cy - 26)))
    return f
def draw_string(a, b):
    def f(img, k):
        x0, y0 = a; x1, y1 = b; e = ease(k)
        d = ImageDraw.Draw(img)
        d.line((x0 + 4, y0 + 6, x0 + (x1 - x0) * e + 4, y0 + (y1 - y0) * e + 6), fill=(0, 0, 0, 90), width=7)
        d.line((x0, y0, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e), fill=(175, 20, 25, 255), width=6)
    return f

for i, p in enumerate(PHOTOS):
    ITEMS.append((p[1], 0.35, draw_photo(p)))
    if i > 0:
        ITEMS.append((p[1] + 0.45, 0.6, draw_string(pin_pos(PHOTOS[i - 1]), pin_pos(p))))
for n, spr in zip(NOTES, NSPR):
    ITEMS.append((n[1], 0.3, draw_note(n, spr)))
ITEMS.sort(key=lambda it: it[0] + it[1])

_states = {}
def base_state(t):
    done = [it for it in ITEMS if it[0] + it[1] <= t]
    k = len(done)
    if k not in _states:
        prev = max([j for j in _states if j < k], default=None)
        img = (_states[prev].copy() if prev is not None else BOARD.convert('RGBA'))
        for it in ITEMS[(prev or 0):k]: it[2](img, 1.0)
        _states[k] = img
    return _states[k], [it for it in ITEMS if it[0] <= t < it[0] + it[1]]

# ---------- camera ----------
def focus(i, vw=880):
    p = PHOTOS[i]; return (p[2] + 30, p[3] + 110, vw)
# keyframes: (t, cx, cy, view_width)
GX = PHOTOS[6][2] - POL[0].width / 2 + 30 + 0.40 * PS; GY = PHOTOS[6][3] - POL[0].height / 2 + 30 + 0.48 * PS  # ghost approx
CAM = [
    (0.0, 700, 600, 1400), (0.25, *focus(0, 900)), (6.9, *focus(0, 800)),
    (7.4, *focus(1, 900)), (11.1, *focus(1, 820)),
    (11.6, *focus(2, 900)), (13.3, *focus(2, 860)),
    (13.8, *focus(3, 900)), (18.9, *focus(3, 760)),
    (19.5, *focus(4, 900)), (22.4, *focus(4, 800)),
    (23.0, *focus(5, 900)), (27.8, *focus(5, 820)),
    (28.3, *focus(6, 900)), (29.4, *focus(6, 820)), (31.9, GX, GY, 460),
    (33.1, WW / 2, WH / 2, WW), (35.3, WW / 2, WH / 2, WW * 0.97),
    (36.4, *focus(7, 820)), (39.4, PHOTOS[7][2], PHOTOS[7][3] - 45, 470),
]
def cam(t):
    for (t0, *a), (t1, *b) in zip(CAM, CAM[1:]):
        if t0 <= t < t1:
            k = ease((t - t0) / (t1 - t0))
            # log-interp zoom for smoothness
            vw = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * k)
            return _clamp(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, vw)
    return _clamp(*CAM[-1][1:])
def _clamp(cx, cy, vw):
    vw = min(vw, WW); vh = vw * H / W
    return min(max(cx, vw / 2), WW - vw / 2), min(max(cy, vh / 2), WH - vh / 2), vw

# ---------- post fx ----------
rng = np.random.default_rng(5)
GRAIN = [Image.fromarray(rng.normal(128, 26, (H // 2, W // 2)).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
VIG = Image.fromarray((255 * np.clip(1.15 - 0.85 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2), 0.15, 1)).astype(np.uint8))
GLITCH = [(20.45, 0.35), (21.85, 0.2), (29.25, 0.5), (31.2, 0.15), (37.8, 0.4), (38.8, 0.25), (39.4, 0.3), (40.2, 0.25)]
FLASH = [0.25, 28.1]
DARK_END = 40.0

def glitch(img, t):
    r = random.Random(int(t * 24))
    a = np.array(img)
    sh = r.randint(8, 26)
    a[..., 0] = np.roll(a[..., 0], sh, 1); a[..., 2] = np.roll(a[..., 2], -sh, 1)
    for _ in range(r.randint(3, 7)):
        y = r.randint(0, H - 80); h = r.randint(10, 90)
        a[y:y + h] = np.roll(a[y:y + h], r.randint(-120, 120), 1)
    return Image.fromarray(a)

FINAL_TXT = 'Aku tak pernah ambil gambar ni.'
def typewriter(img, t):
    k = int(max(0, (t - 37.8) / 1.5) * len(FINAL_TXT))
    txt = FINAL_TXT[:k]
    if not txt: return img
    f = ImageFont.truetype(TYPE, 60); d = ImageDraw.Draw(img)
    words = txt
    lines = ['Aku tak pernah', 'ambil gambar ni.']
    shown, y = k, 1560
    for l in lines:
        s = l[:max(0, shown)]; shown -= len(l) + 1
        if s:
            w = f.getlength(l)
            d.rectangle(((W - w) / 2 - 20, y - 10, (W + w) / 2 + 20, y + 78), fill=(0, 0, 0))
            d.text(((W - w) / 2, y), s, font=f, fill=(235, 235, 225))
        y += 95
    return img

def compose(t):
    base, active = base_state(t)
    cx, cy, vw = cam(t); vh = vw * H / W
    x0, y0 = int(cx - vw / 2), int(cy - vh / 2)
    box = (x0, y0, int(x0 + vw), int(y0 + vh))
    # crop with padding for moving items
    if active:
        pad = 700
        bx = (max(0, box[0] - pad), max(0, box[1] - pad), min(WW, box[2] + pad), min(WH, box[3] + pad))
        region = base.crop(bx)
        for it in active:
            tmp = Image.new('RGBA', region.size, (0, 0, 0, 0))
            # draw in world coords shifted
            sub = _Shift(region, bx[0], bx[1])
            it[2](sub, (t - it[0]) / it[1])
        view = region.crop((box[0] - bx[0], box[1] - bx[1], box[2] - bx[0], box[3] - bx[1]))
    else:
        view = base.crop(box)
    img = view.convert('RGB').resize((W, H), Image.BILINEAR)
    # flicker / darkness
    lvl = 0.92 + 0.08 * math.sin(t * 7.3) * math.sin(t * 2.1)
    if 16.7 < t < 22.5 or 26.5 < t < 32.3: lvl *= 0.85 + 0.15 * (random.Random(int(t * 12)).random() > 0.15)
    img = ImageEnhance.Brightness(img).enhance(lvl)
    img = Image.composite(img, Image.new('RGB', (W, H), (0, 0, 0)), VIG)
    g = GRAIN[int(t * 24) % 6]
    img = ImageChops.overlay(img, Image.merge('RGB', (g, g, g))) if False else Image.blend(img, Image.merge('RGB', (g, g, g)), 0.07)
    for fl in FLASH:
        if fl <= t < fl + 0.35:
            img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 250)), 0.8 * (1 - (t - fl) / 0.35))
    if t >= DARK_END:
        img = Image.blend(img, Image.new('RGB', (W, H), 'black'), min(1, (t - DARK_END) / 0.6))
    for g0, d in GLITCH:
        if g0 <= t < g0 + d: img = glitch(img, t)
    if t >= 37.8: img = typewriter(img, t)
    return img

class _Shift:
    """proxy that lets draw fns use world coords on a cropped region"""
    def __init__(self, im, ox, oy): self.im, self.ox, self.oy = im, ox, oy
    def alpha_composite(self, src, dest): self.im.alpha_composite_safe(src, (dest[0] - self.ox, dest[1] - self.oy))

def _acs(self, src, dest):
    x, y = dest; sx0, sy0 = max(0, -x), max(0, -y)
    x, y = max(0, x), max(0, y)
    if sx0 >= src.width or sy0 >= src.height or x >= self.width or y >= self.height: return
    if sx0 or sy0: src = src.crop((sx0, sy0, src.width, src.height))
    self.alpha_composite(src, (x, y))
Image.Image.alpha_composite_safe = _acs

# string drawing uses ImageDraw on img directly -> support shift
_orig_draw_string = draw_string
def _draw_on(img):
    if isinstance(img, _Shift):
        d = ImageDraw.Draw(img.im); ox, oy = img.ox, img.oy
        class D:
            def line(self, xy, **kw): d.line(tuple(v - (ox if i % 2 == 0 else oy) for i, v in enumerate(xy)), **kw)
        return D()
    return ImageDraw.Draw(img)
def draw_string(a, b):  # noqa: F811 re-define with shift support
    def f(img, k):
        x0, y0 = a; x1, y1 = b; e = ease(k); d = _draw_on(img)
        d.line((x0 + 4, y0 + 6, x0 + (x1 - x0) * e + 4, y0 + (y1 - y0) * e + 6), fill=(0, 0, 0, 90), width=7)
        d.line((x0, y0, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e), fill=(175, 20, 25, 255), width=6)
    return f
ITEMS = []
for i, p in enumerate(PHOTOS):
    ITEMS.append((p[1], 0.35, draw_photo(p)))
    if i > 0: ITEMS.append((p[1] + 0.45, 0.6, draw_string(pin_pos(PHOTOS[i - 1]), pin_pos(p))))
for n, spr in zip(NOTES, NSPR): ITEMS.append((n[1], 0.3, draw_note(n, spr)))
ITEMS.sort(key=lambda it: it[0] + it[1])

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        ts = [float(x) for x in sys.argv[2:]]
        S = Image.new('RGB', (270 * min(4, len(ts)), 480 * math.ceil(len(ts) / 4)))
        for i, t in enumerate(ts): S.paste(compose(t).resize((270, 480)), ((i % 4) * 270, (i // 4) * 480))
        S.save('grid.jpg')
    else:
        a, b = int(sys.argv[1]), int(sys.argv[2])
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                              '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                              '-pix_fmt', 'yuv420p', f'part_{a:05d}.mp4'], stdin=subprocess.PIPE)
        for i in range(a, b): p.stdin.write(compose(i / FPS).tobytes())
        p.stdin.close(); p.wait()
