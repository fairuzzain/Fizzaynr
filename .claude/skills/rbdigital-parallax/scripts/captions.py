"""Caption looks for craft parallax videos (imported by render.py).
scenes.json top level:  "caption_look": {"preset":"kertas","color":[r,g,b]}
ONE look per video; a different preset for every new video.
Styles: pill, paper, tape, comic, sticker, banner.  Anims: pop, slide, drop, fade, words.
Pos: top, top-left, top-right, mid-low.  Fonts are bundled in ../fonts (override with env FONT_DIR)."""
import random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = os.environ.get("FONT_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts"))
FONTS = {  # key: (file, variation or None, size multiplier)
    "bangers": ("Bangers-Regular.ttf", None, 1.5), "luckiest": ("LuckiestGuy-Regular.ttf", None, 1.2),
    "marker": ("PermanentMarker-Regular.ttf", None, 1.0), "caveat": ("CaveatBrush-Regular.ttf", None, 1.25),
    "patrick": ("PatrickHand-Regular.ttf", None, 1.2), "anton": ("Anton-Regular.ttf", None, 1.15),
    "baloo": ("Baloo2.ttf", b"ExtraBold", 1.1), "fredoka": ("Fredoka.ttf", b"Bold", 1.1),
    "poppins": ("Poppins-Bold.ttf", None, 1.0)}
PRESETS = {  # name: (style, font, anim)
    "kertas": ("paper", "caveat", "words"), "kertas2": ("paper", "patrick", "words"),
    "komik": ("comic", "bangers", "pop"), "komik2": ("comic", "luckiest", "pop"),
    "nota": ("tape", "marker", "drop"), "nota2": ("tape", "caveat", "drop"),
    "sticker": ("sticker", "fredoka", "pop"), "sticker2": ("sticker", "baloo", "pop"),
    "banner": ("banner", "anton", "slide"), "pill": ("pill", "poppins", "fade")}

_fc = {}
def font(key, px):
    k = (key, int(px))
    if k not in _fc:
        f, var, mul = FONTS[key]; ft = ImageFont.truetype(os.path.join(FD, f), int(px*mul))
        if var: ft.set_variation_by_name(var)
        _fc[k] = ft
    return _fc[k]

def wrap(d, text, ft, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur+" "+w).strip()
        if d.textlength(t, font=ft) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def resolve(scenes, video_cap=None):
    """ONE caption look for the whole video; missing preset -> random. Returns the look."""
    v = dict(video_cap or {}); name = v.pop("preset", None) or random.choice(list(PRESETS))
    st, fn, an = PRESETS[name]; look = {"style": st, "font": fn, "anim": an, "pos": "top", "color": [59, 42, 31]}
    look.update(v); look["preset"] = name
    for i, sc in enumerate(scenes):
        c = dict(look); c.update(sc.get("cap", {})); c.setdefault("rot", 0)
        if "rot" not in sc.get("cap", {}) and c["style"] in ("paper", "tape", "comic", "sticker"):
            c["rot"] = (-2 if i % 2 == 0 else 2)
        sc["cap"] = c
    return look

def layer(text, c, H, maxw, word_alpha=None, base=0.052):
    st, col = c["style"], tuple(c["color"]); px = H*base*c.get("scale", 1)
    if st == "banner": text = text.upper()
    ft = font(c["font"], px); tmp = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    lines = wrap(tmp, text, ft, maxw); asc, desc = ft.getmetrics(); lh = int((asc+desc)*1.05)
    tw = int(max(tmp.textlength(l, font=ft) for l in lines)); th = lh*len(lines)
    padx, pady = {"pill": (.9, .35), "paper": (1.0, .45), "tape": (1.0, .6), "comic": (.35, .25),
                  "sticker": (.45, .3), "banner": (1.2, .3)}[st]
    px_, py_ = int(px*padx), int(px*pady); bw, bh = tw+2*px_, th+2*py_; m = int(px*.8)
    im = Image.new("RGBA", (bw+2*m, bh+2*m)); d = ImageDraw.Draw(im); x0, y0 = m, m
    rnd = random.Random(sum(map(ord, text)))
    def shadow(shape_im, off, blur, op):
        a = shape_im.split()[3].point(lambda v: int(v*op)).filter(ImageFilter.GaussianBlur(blur))
        s = Image.new("RGBA", shape_im.size, (30, 20, 15, 0)); s.putalpha(a); out = Image.new("RGBA", shape_im.size)
        out.alpha_composite(s, (off, off)); out.alpha_composite(shape_im); return out
    if st == "pill":
        d.rounded_rectangle([x0, y0, x0+bw, y0+bh], int(bh*.45), fill=col+(225,)); tcol, stroke = (255, 255, 255), 0
    elif st in ("paper", "tape"):
        paper_col = (250, 244, 228) if st == "paper" else (255, 236, 160)
        n = 14; pts = [(x0+bw*k/n, y0+rnd.uniform(0, px*.12)) for k in range(n+1)]
        pts += [(x0+bw-rnd.uniform(0, px*.1), y0+bh*k/4) for k in range(1, 4)]
        pts += [(x0+bw*(n-k)/n, y0+bh-rnd.uniform(0, px*.12)) for k in range(n+1)]
        pts += [(x0+rnd.uniform(0, px*.1), y0+bh*(4-k)/4) for k in range(1, 4)]
        d.polygon(pts, fill=paper_col+(255,)); tcol, stroke = col, 0
        if st == "paper":
            d.line([(x0+px_*.6, y0+bh-py_*.55), (x0+bw-px_*.6, y0+bh-py_*.55)], fill=col+(150,), width=max(2, int(px*.06)))
    elif st == "banner":
        d.rectangle([x0, y0, x0+bw, y0+bh], fill=col+(240,))
        d.rectangle([x0, y0+bh-int(px*.12), x0+bw, y0+bh], fill=(255, 214, 90, 255)); tcol, stroke = (255, 255, 255), 0
    elif st == "comic": tcol, stroke = (255, 236, 90) if sum(col) < 300 else col, max(3, int(px*.11))
    else: tcol, stroke = col, max(5, int(px*.16))  # sticker
    k = 0
    for li, l in enumerate(lines):
        cx = x0+px_+(tw-tmp.textlength(l, font=ft))/2; ly = y0+py_+li*lh
        for w in l.split():
            a = 1 if word_alpha is None else word_alpha[k]; k += 1
            if a > 0:
                A = int(255*a)
                if st == "comic":
                    d.text((cx+px*.08, ly+px*.1), w, font=ft, fill=(25, 20, 30, int(A*.8)), stroke_width=stroke, stroke_fill=(25, 20, 30, int(A*.8)))
                    d.text((cx, ly), w, font=ft, fill=tcol+(A,), stroke_width=stroke, stroke_fill=(25, 20, 30, A))
                elif st == "sticker":
                    d.text((cx, ly), w, font=ft, fill=tcol+(A,), stroke_width=stroke, stroke_fill=(255, 255, 255, A))
                else: d.text((cx, ly), w, font=ft, fill=tuple(tcol[:3])+(A,))
            cx += tmp.textlength(w+" ", font=ft)
    if st == "tape":
        for tx, ang in ((x0-px*.2, -18), (x0+bw-px*1.6, 16)):
            t = Image.new("RGBA", (int(px*1.8), int(px*.55)), (235, 225, 200, 170)).rotate(ang, expand=True, resample=Image.BICUBIC)
            im.alpha_composite(t, (int(max(0, tx)), int(max(0, y0-px*.35))))
    im = shadow(im, int(px*.12), px*.15, .45 if st != "comic" else 0)
    if c.get("rot"): im = im.rotate(c["rot"], expand=True, resample=Image.BICUBIC)
    return im

_cache = {}
def ease_back(p):
    p = max(0, min(1, p)); s = 1.7; p -= 1; return p*p*((s+1)*p+s)+1

def draw(img, text, c, t0, t1, t, W, H, y_frac=None):
    """Composite caption onto img (RGBA) for time t within [t0,t1]."""
    if not text or t < t0: return
    anim = c["anim"]; p = (t-t0)/0.45; out = max(0, min(1, (t1-t)/0.3))
    maxw = W*(0.62 if W > H else 0.86); base = 0.052 if W > H else 0.034
    if anim == "words":
        n = len(text.split()); wa = [round(max(0, min(1, (t-t0-0.13*k)/0.18)), 1) for k in range(n)]
        key = (text, tuple(wa), c["style"], c["font"], c.get("rot"), c.get("scale", 1))
        L = _cache.get(key) or _cache.setdefault(key, layer(text, c, H, maxw, wa, base))
    else:
        key = (text, c["style"], c["font"], c.get("rot"), tuple(c["color"]), c.get("scale", 1))
        L = _cache.get(key) or _cache.setdefault(key, layer(text, c, H, maxw, None, base))
    sc, dx, dy, a = 1.0, 0, 0, min(1, max(0, p))
    if anim == "pop": sc = 0.55+0.45*ease_back(p)
    elif anim == "slide": dx = int((1-ease_back(p))*(-W*.35 if "right" not in c["pos"] else W*.35))
    elif anim == "drop": dy = int(-(1-ease_back(p))*H*.18)
    a *= out
    if a <= 0: return
    if sc != 1.0: L = L.resize((max(1, int(L.width*sc)), max(1, int(L.height*sc))), Image.BILINEAR)
    if a < 1: L = L.copy(); L.putalpha(L.split()[3].point(lambda v: int(v*a)))
    pos = c["pos"]; yc = H*(y_frac if y_frac is not None else (0.62 if pos == "mid-low" else 0.13))
    xc = {"top-left": W*.06+L.width/2, "top-right": W*.94-L.width/2}.get(pos, W/2)
    img.alpha_composite(L, (int(xc-L.width/2+dx), int(yc-L.height/2+dy)))
