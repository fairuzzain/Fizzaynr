"""Scrapbook sticker video engine (9:16, stop-motion feel).

A storyboard script imports this module, sets backgrounds/assets, defines scenes
and elements, then calls run(). See examples/scrapbook/shark_storyboard.py.

API
  setup(assets_dir, backgrounds={'blue': 'path.jpg', ...}, font=None)
  scene(t0, t1, bg_key)                        # background for a time range; slide transition + whoosh
  el(sprite('A1', width), x, y, t0, t1, rot=0, anim='pop'|'slam'|'fall'|'word')
  caption(['WORD', 'WORD'], y, t0, t1, size, color, step=0.22, rot=0, maxw=820)   # word-by-word, auto wrap, centred
  text_sprite('text', size, color)             # single text sticker, use with el()
  preview([t, ...], 'grid.jpg')                # contact sheet of frames
  run('out.mp4', dur, vo='vo.mp3' or None, music=True)
Coordinates are element CENTRES on a 1080x1920 canvas. Elements pop out automatically at t1.
"""
import numpy as np, math, random, subprocess, os, wave, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 24
NAVY, RED, YEL = (22, 40, 82), (214, 40, 40), (240, 170, 0)
_FONT_DEFAULT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
CFG = dict(assets='assets', font=_FONT_DEFAULT)
BG, SCENES, ELS, POPS, WHOOSH = {}, [], [], [], []
_cache = {}
random.seed(7)


def _load_bg(f):
    im = Image.open(f).convert('RGB')
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def setup(assets_dir, backgrounds, font=None):
    CFG['assets'] = assets_dir
    if font: CFG['font'] = font
    for k, p in backgrounds.items(): BG[k] = _load_bg(p)


def _with_shadow(img):
    pad = 40
    c = Image.new('RGBA', (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh.putalpha(img.split()[3].point(lambda v: v * 0.38))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)), (pad + 10, pad + 16))
    c.alpha_composite(img, (pad, pad))
    return c


def sprite(name, w):
    k = (name, w)
    if k not in _cache:
        im = Image.open(os.path.join(CFG['assets'], f'{name}.png')).convert('RGBA')
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        _cache[k] = _with_shadow(im)
    return _cache[k]


def text_sprite(txt, size, color):
    k = ('T', txt, size, color)
    if k not in _cache:
        f = ImageFont.truetype(CFG['font'], size)
        sw = max(8, size // 7)
        b = f.getbbox(txt, stroke_width=sw)
        im = Image.new('RGBA', (b[2] - b[0] + 4, b[3] - b[1] + 4), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((-b[0] + 2, -b[1] + 2), txt, font=f, fill=color,
                                stroke_width=sw, stroke_fill=(255, 253, 245))
        _cache[k] = _with_shadow(im)
    return _cache[k]


def _ease_back(x):
    x = min(max(x, 0), 1); c = 2.2
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def el(img, x, y, t0, t1, rot=0, anim='pop'):
    ELS.append(dict(img=img, x=x, y=y, t0=t0, t1=t1, rot=rot, anim=anim, seed=random.random() * 1000))
    POPS.append((t0, anim))


def caption(words, y, t0, t1, size, color, step=0.22, rot=0, maxw=820):
    sps = [text_sprite(w, size, color) for w in words]
    gap = -80 + size * 0.28
    lines, cur, cw = [], [], 0
    for s in sps:
        if cur and cw + gap + s.width > maxw + 80:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (gap if cur else 0) + s.width; cur.append(s)
    lines.append((cur, cw))
    lh = (sps[0].height - 80) * 1.08
    i = 0
    for li, (ln, lw) in enumerate(lines):
        x = W / 2 - lw / 2
        for s in ln:
            el(s, x + s.width / 2, y + li * lh, t0 + i * step, t1, rot=rot + random.uniform(-3, 3), anim='word')
            x += s.width + gap; i += 1


def scene(t0, t1, bg):
    SCENES.append((t0, t1, bg))
    if t0 > 0: WHOOSH.append(t0)


def _state(e, t):
    if t < e['t0'] or t >= e['t1']: return None
    k = t - e['t0']; out = e['t1'] - t
    r = random.Random(e['seed'] + math.floor(t * 12))  # stop-motion boil on twos
    jr, jx, jy = r.uniform(-1.6, 1.6), r.uniform(-3, 3), r.uniform(-3, 3)
    s, dy, rot, a = 1, 0, 0, e['anim']
    if a in ('pop', 'word'):
        d = 0.35 if a == 'pop' else 0.25
        s = _ease_back(k / d); rot = (1 - min(k / d, 1)) * -25
    elif a == 'slam':
        x = min(k / 0.22, 1)
        s = 1.9 - 0.9 * x if x < 1 else 1 + 0.06 * math.sin((k - 0.22) * 40) * math.exp(-(k - 0.22) * 10)
    elif a == 'fall':
        dy = -(1 - _ease_back(min(k / 0.45, 1))) * 900
    if out < 0.2: s *= max(out / 0.2, 0)
    if s <= 0.02: return None
    return s, jx, jy + dy, jr + rot


def compose(t):
    si = max(i for i, sc in enumerate(SCENES) if sc[0] <= t)
    st, en, bg = SCENES[si]
    frame = BG[bg].copy()
    if si > 0 and t - st < 0.3:
        frame = BG[SCENES[si - 1][2]].copy()
        frame.paste(BG[bg], (int(W * (1 - _ease_back((t - st) / 0.3))), 0))
    frame = frame.convert('RGBA')
    for e in ELS:
        stt = _state(e, t)
        if not stt: continue
        s, dx, dy, dr = stt
        im = e['img']
        if abs(s - 1) > 1e-3:
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        ang = e['rot'] + dr
        if abs(ang) > 0.05: im = im.rotate(ang, Image.BICUBIC, expand=True)
        px, py = int(e['x'] + dx - im.width / 2), int(e['y'] + dy - im.height / 2)
        if -im.width < px < W and -im.height < py < H:
            frame.alpha_composite(im, (px, py))
    return frame.convert('RGB')


def preview(times, out='grid.jpg', per_row=4):
    rows = math.ceil(len(times) / per_row)
    S = Image.new('RGB', (270 * min(per_row, len(times)), 480 * rows), 'white')
    for i, t in enumerate(times):
        S.paste(compose(t).resize((270, 480)), ((i % per_row) * 270, (i // per_row) * 480))
    S.save(out); return out


# ---------------- audio ----------------
SR = 44100


def _audio(dur, vo=None, music=True):
    N = int(dur * SR); rng = np.random.default_rng(1); out = np.zeros(N)

    def add(sig, t, g):
        i = int(t * SR); j = min(N, i + len(sig))
        if j > i: out[i:j] += sig[:j - i] * g

    def pluck(f, d, dec=0.996):
        p = int(SR / f); buf = rng.uniform(-1, 1, p); n = int(d * SR); y = np.zeros(n)
        for i in range(n):
            y[i] = buf[i % p]; buf[i % p] = dec * 0.5 * (buf[i % p] + buf[(i + 1) % p])
        return y

    if music:  # cheerful C-G-Am-F plucked arpeggio, 112 bpm
        mus = np.zeros(N); b = 60 / 112; note = lambda m: 440 * 2 ** ((m - 69) / 12)
        chords = [[48, 60, 64, 67, 72], [43, 59, 62, 67, 71], [45, 60, 64, 69, 72], [41, 60, 65, 69, 72]]
        cache = {}; t = 0; k = 0
        def madd(sig, t, g):
            i = int(t * SR); j = min(N, i + len(sig)); mus[i:j] += sig[:j - i] * g
        while t < dur - 0.5:
            ch = chords[(k // 8) % 4]; m = ch[[1, 3, 2, 4, 1, 3, 2, 4][k % 8]]
            if m not in cache: cache[m] = pluck(note(m), 0.8)
            madd(cache[m], t, 0.18)
            if k % 8 in (0, 4):
                if ch[0] not in cache: cache[ch[0]] = pluck(note(ch[0]), 1.2, 0.998)
                madd(cache[ch[0]], t, 0.28)
            n = int(0.03 * SR); madd(rng.normal(0, 1, n) * np.exp(-np.linspace(0, 8, n)), t + b / 4, 0.03)
            t += b / 2; k += 1
        fl = int(1.5 * SR); mus[-fl:] *= np.linspace(1, 0, fl)
        out += mus * (0.35 if vo else 1.0)

    g = 0.6 if vo else 1.0
    def pop(f0, f1, d=0.09):
        n = int(d * SR); tt = np.arange(n) / SR
        return np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, n)) / SR) * np.exp(-tt * 40)
    def slam():
        n = int(0.25 * SR); tt = np.arange(n) / SR
        return np.sin(2 * np.pi * np.cumsum(np.linspace(180, 50, n)) / SR) * np.exp(-tt * 18) + rng.normal(0, 0.4, n) * np.exp(-tt * 40)
    for t, a in POPS:
        if a == 'pop': add(pop(500, 1100), t, 0.5 * g)
        elif a == 'word': add(pop(900, 1500, 0.05), t, 0.2 * g)
        elif a == 'slam': add(slam(), t, 0.6 * g)
        elif a == 'fall': add(pop(1400, 700, 0.04), t + 0.4, 0.15 * g)
    for t in WHOOSH:
        n = int(0.4 * SR); w = np.convolve(rng.normal(0, 1, n), np.ones(30) / 30, 'same')
        add(w * np.sin(np.linspace(0, np.pi, n)) ** 2 * 3, t - 0.1, 0.5 * g)
    if vo:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vo, '-ac', '1', '-ar', str(SR), '_vo.wav'], check=True)
        with wave.open('_vo.wav') as f: v = np.frombuffer(f.readframes(f.getnframes()), np.int16) / 32768
        add(v / np.abs(v).max() * 0.85, 0, 1.0)
    out /= max(1, np.abs(out).max() / 0.95)
    with wave.open('_audio.wav', 'w') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((out * 32767).astype(np.int16).tobytes())
    return '_audio.wav'


def run(out, dur, vo=None, music=True):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                          '-pix_fmt', 'yuv420p', '_video.mp4'], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(compose(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    a = _audio(dur, vo, music)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '_video.mp4', '-i', a, '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', out], check=True)
    return out
