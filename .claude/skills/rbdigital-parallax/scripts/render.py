#!/usr/bin/env python3
"""3-layer craft parallax renderer (bg + character cut-outs + fg border) with camera moves,
depth of field, idle animation, particles, texture overlay, style transitions and captions.

Usage:  python3 render.py scenes.json               full render -> C["out"] + events.json (for SFX)
        python3 render.py scenes.json --preview 6   contact sheet of 6 frames -> preview.png (fast)

scenes.json (only "scenes", "duration" required; everything else has defaults):
{ "size":[720,1280], "fps":30, "duration":30, "out":"video.mp4", "style":"paper",
  "caption_look":{"preset":"kertas","color":[59,42,31]},
  "fg_w":1.55, "fg_drop":0.18,                      # 16:9 -> 1.12 / 0.48
  # optional overrides of the style defaults (see STYLE):
  "transition":"torn", "texture":"paper", "particles":"dust", "dof":1.6, "stopmo":false,
  "scenes":[ {"bg":"b1.png","fg":"f1_cut.png",
              "chars":[{"file":"p1_cut.png","x":0.55,"h":0.54,"idle":"breathe"}],
              "start":0.0,"end":5.5,"cam":"push","dir":1,"caption":"Bermula dari dapur",
              "particles":"confetti"} ],
  "tagline":{"lines":["Mulakan langkah anda","hari ini."],"start":27.2,"y":0.76} }
cam: push | pull | pan | tilt | reveal | still   (default rotates push, pan, tilt, pull, pan, reveal)
idle: breathe | sway | bounce | none            (default breathe + light sway)
transition: crossfade | slide | torn | page      particles: dust | confetti | sparkle | none
texture: paper | fabric | none                   Scenes overlap ~0.6 s; the overlap is the transition."""
import sys, os, json, math, random, subprocess, numpy as np
from PIL import Image, ImageFilter, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import captions as CAP

STYLE = {  # transition, texture, particles, dof (bg blur px @720w), stopmo
    "paper": ("torn", "paper", "dust", 1.6, False), "clay": ("crossfade", "none", "dust", 2.0, True),
    "3d": ("crossfade", "none", "sparkle", 2.2, False), "felt": ("page", "fabric", "dust", 1.6, False),
    "fabric": ("page", "fabric", "dust", 1.6, False), "knit": ("page", "fabric", "dust", 1.6, False),
    "wood": ("slide", "none", "dust", 1.8, False), "mini": ("crossfade", "none", "dust", 3.0, False),
    "origami": ("slide", "paper", "confetti", 1.4, False), "cardboard": ("slide", "paper", "dust", 1.4, False),
    "bricks": ("slide", "none", "sparkle", 1.6, False), "lowpoly": ("crossfade", "none", "sparkle", 1.4, False),
    "voxel": ("slide", "none", "sparkle", 1.4, False), "watercolor": ("crossfade", "paper", "dust", 1.2, False)}
CAMS = ["push", "pan", "tilt", "pull", "pan", "reveal"]

C = json.load(open(sys.argv[1])); W, H = C.get("size", [720, 1280]); FPS = C.get("fps", 30); DUR = C["duration"]
PREVIEW = int(sys.argv[sys.argv.index("--preview")+1]) if "--preview" in sys.argv else 0
tr0, tex0, par0, dof0, sm0 = STYLE.get(C.get("style", "paper"), STYLE["paper"])
TRANS, TEX, PART = C.get("transition", tr0), C.get("texture", tex0), C.get("particles", par0)
DOF, STOPMO = C.get("dof", dof0)*W/720, C.get("stopmo", sm0)
U = W/720  # pixel unit
ease = lambda p: .5-.5*math.cos(math.pi*max(0, min(1, p)))
S = C["scenes"]; LOOK = CAP.resolve(S, C.get("caption_look")); print("caption look:", LOOK["preset"], "| transition:", TRANS,
                                                                       "| texture:", TEX, "| particles:", PART, "| stopmo:", STOPMO)

def shadow_of(im, blur, op):
    a = im.split()[3].point(lambda v: int(v*op)).filter(ImageFilter.GaussianBlur(blur))
    s = Image.new("RGBA", im.size, (40, 25, 20, 0)); s.putalpha(a); return s

def with_shadow(im, blur, op, dx, dy):
    """one RGBA canvas = soft drop shadow + image (so each frame needs ONE transform per layer)"""
    m = int(40*U); can = Image.new("RGBA", (im.width+2*m, im.height+2*m))
    can.alpha_composite(shadow_of(im, blur, op), (m+int(dx), m+int(dy))); can.alpha_composite(im, (m, m)); return can

# ---------- preload + pre-scale every layer once (speed) ----------
L = []
for i, sc in enumerate(S):
    sc.setdefault("cam", CAMS[i % len(CAMS)]); sc.setdefault("dir", 1 if i % 2 == 0 else -1)
    bg = Image.open(sc["bg"]).convert("RGB"); k = max(W/bg.width, H/bg.height)*1.15
    bg = bg.resize((int(bg.width*k), int(bg.height*k)), Image.LANCZOS)
    if DOF > 0: bg = bg.filter(ImageFilter.GaussianBlur(DOF))
    chars = []
    for c in sc.get("chars", []):
        im = Image.open(c["file"]).convert("RGBA"); im = im.crop(im.getbbox())
        hh = int(H*c.get("h", .54)*1.2)  # 20 % headroom for zoom
        im = im.resize((int(im.width*hh/im.height), hh), Image.LANCZOS)
        chars.append({"im": with_shadow(im, 12*U, .45, 14*U, 16*U), "c": c, "ax": im.width/2+int(40*U), "ay": im.height+int(40*U)})
    fg = None
    if sc.get("fg"):
        f = Image.open(sc["fg"]).convert("RGBA"); f = f.crop(f.getbbox()); fw = int(W*C.get("fg_w", 1.55)*1.15)
        f = f.resize((fw, int(f.height*fw/f.width)), Image.LANCZOS)
        fg = {"im": with_shadow(f, 8*U, .35, 10*U, 12*U), "ax": f.width/2+int(40*U), "ay": f.height+int(40*U), "h": f.height}
    L.append({"bg": bg, "chars": chars, "fg": fg})

# ---------- camera ----------
def camera(sc, p):
    """returns zoom z, offset ox, oy (px, applied 1:1 to the character layer)"""
    d, cam = sc["dir"], sc["cam"]
    if cam == "push": return 1+.07*p, d*(p-.5)*.08*W, 0
    if cam == "pull": return 1.07-.07*p, d*(p-.5)*.08*W, 0
    if cam == "pan": return 1.03, d*(p-.5)*.14*W, 0
    if cam == "tilt": return 1.04, 0, (p-.5)*.10*H
    if cam == "reveal": return 1.12-.12*p, d*(p-.5)*.05*W, (1-p)*.05*H
    return 1.0, 0, 0

def place(lay, x, y, s, img, rot=0, sy=1.0, sx=1.0):
    """draw layer dict (im, anchor ax/ay = bottom-centre of the object) scaled by s (sx/sy) and rotated rot deg,
    anchor landing on (x, y). One affine transform, only the on-screen box is sampled."""
    im, ax, ay = lay["im"], lay["ax"], lay["ay"]; kx, ky = s*sx, s*sy
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    fwd = lambda px, py: (x+c*(px-ax)*kx+si*(py-ay)*ky, y-si*(px-ax)*kx+c*(py-ay)*ky)
    pts = [fwd(px, py) for px, py in ((0, 0), (im.width, 0), (0, im.height), (im.width, im.height))]
    x0, y0 = max(0, int(min(p[0] for p in pts))), max(0, int(min(p[1] for p in pts)))
    x1, y1 = min(W, int(max(p[0] for p in pts))+1), min(H, int(max(p[1] for p in pts))+1)
    if x1 <= x0 or y1 <= y0: return
    # inverse: src = anchor + S^-1 R^-1 (dst - (x, y)),  dst = box + (x0, y0)
    a, b = c/kx, -si/kx; d, e = si/ky, c/ky
    ox, oy = x0-x, y0-y
    coeff = (a, b, ax+a*ox+b*oy, d, e, ay+d*ox+e*oy)
    img.alpha_composite(im.transform((x1-x0, y1-y0), Image.AFFINE, coeff, Image.BILINEAR), (x0, y0))

# ---------- particles ----------
rng = random.Random(7)
PS = [dict(x=rng.random(), y=rng.random(), v=rng.uniform(.4, 1), s=rng.uniform(.6, 1.4), ph=rng.uniform(0, 6.28),
           col=rng.choice([(236, 72, 96), (255, 196, 61), (72, 160, 220), (120, 200, 120), (250, 140, 60), (180, 110, 220)]))
      for _ in range(28)]
def particles(img, kind, t):
    if kind in (None, "none"): return
    d = ImageDraw.Draw(img, "RGBA")
    for q in PS:
        if kind == "dust":
            y = (q["y"]-t*.025*q["v"]) % 1; x = q["x"]+.015*math.sin(t*.8+q["ph"]); r = 2.2*U*q["s"]
            a = int(70+50*math.sin(t*1.5+q["ph"]))
            d.ellipse([x*W-r, y*H-r, x*W+r, y*H+r], fill=(255, 250, 235, max(0, a)))
        elif kind == "confetti":
            y = (q["y"]+t*.09*q["v"]) % 1.05-.03; x = q["x"]+.03*math.sin(t*1.3+q["ph"])
            ang = t*3*q["v"]+q["ph"]; w2, h2 = 5*U*q["s"], 9*U*q["s"]*abs(math.cos(ang*1.7))+1
            ca, sa = math.cos(ang), math.sin(ang)
            pts = [(x*W+ca*dx-sa*dy, y*H+sa*dx+ca*dy) for dx, dy in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))]
            d.polygon(pts, fill=q["col"]+(230,))
        elif kind == "sparkle":
            tw = max(0, math.sin(t*2.2*q["v"]+q["ph"]))**6
            if tw < .05: continue
            x, y, r = q["x"]*W, q["y"]*H*.8, 9*U*q["s"]*tw; a = int(220*tw)
            d.polygon([(x, y-r), (x+r*.22, y-r*.22), (x+r, y), (x+r*.22, y+r*.22), (x, y+r), (x-r*.22, y+r*.22), (x-r, y), (x-r*.22, y-r*.22)],
                      fill=(255, 250, 220, a))

# ---------- texture + vignette (one multiplier map) ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = 1-.28*np.clip(((xx/W-.5)**2+(yy/H-.5)**2)*2.2-.12, 0, 1)
nr = np.random.default_rng(3)
if TEX == "paper":
    g = np.array(Image.fromarray((nr.random((H//2, W//2))*255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1)), np.float32)/255
    fib = np.array(Image.fromarray((nr.random((H//8, W//8))*255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32)/255
    MUL = vig*(0.965+.05*g+.02*fib)
elif TEX == "fabric":
    weave = (np.sin(xx*1.9/U)*np.sin(yy*1.9/U))*.5+.5
    MUL = vig*(0.97+.035*weave+.015*nr.random((H, W)))
else: MUL = vig
MUL = MUL[..., None].astype(np.float32)

# ---------- one scene frame ----------
EV = []
def render_scene(i, t):
    sc = S[i]; st, en = sc["start"], sc["end"]; ta = t
    if STOPMO: ta = math.floor(t*12)/12
    p = ease((ta-st)/(en-st)); z, ox, oy = camera(sc, p); Ly = L[i]
    if STOPMO:
        jr = random.Random(int(ta*12)); ox += jr.uniform(-1.5, 1.5)*U; oy += jr.uniform(-1.5, 1.5)*U
    # bg: affine sample, half parallax
    b = Ly["bg"]; zb = z; fb = .5
    cx, cy = b.width/2, b.height/2
    coeff = (1/zb, 0, cx-(W/2+ox*fb)/zb, 0, 1/zb, cy-(H/2+oy*fb)/zb)
    img = b.transform((W, H), Image.AFFINE, coeff, Image.BILINEAR).convert("RGBA")
    if sc.get("particles", PART) == "dust": particles(img, "dust", ta)  # dust lives in the air behind the characters
    # characters: full parallax, stronger zoom
    zc = 1+(z-1)*1.5; intro = (1-ease(min(1, (ta-st)/.6)))
    for j, ch in enumerate(Ly["chars"]):
        c = ch["c"]; idle = c.get("idle", "auto"); rot, sy, sx, hop = 0, 1, 1, 0
        if idle in ("breathe", "auto"): s_ = math.sin(2*math.pi*ta/2.6+j); sy, sx = 1+.014*s_, 1-.006*s_
        if idle in ("sway", "auto"): rot = (1.8 if idle == "sway" else .8)*math.sin(2*math.pi*ta/3.4+j*1.3)
        if idle == "bounce": hop = abs(math.sin(math.pi*ta/.55+j))*.012*H
        bx, by = c.get("x", .5)*W, H*.95; sc_ = zc/1.2*(1-.04*intro)
        x = W/2+(bx-W/2)*zc+ox; y = H/2+(by-H/2)*zc+oy-hop+intro*40*U
        place(ch, x, y, sc_, img, rot, sy, sx)
    # fg border: strongest parallax + own drift
    if Ly["fg"] is not None:
        f = Ly["fg"]; zf = 1+(z-1)*2.2; fwid = W*C.get("fg_w", 1.55)*zf
        drift = -sc["dir"]*(p-.5)*(fwid-W)*.45
        fh = f["h"]/1.15*zf; fy = H-fh+fh*C.get("fg_drop", .18)+oy*1.8
        place(f, W/2+ox*1.8+drift, fy+fh, zf/1.15, img)
    kind = sc.get("particles", PART)
    if kind in ("confetti", "sparkle"): particles(img, kind, ta)
    CAP.draw(img, sc.get("caption", ""), sc["cap"], st+.35, en, t, W, H)
    tg = C.get("tagline")
    if tg and i == len(S)-1:
        tc = dict(LOOK, rot=0, scale=1.3, **tg.get("cap", {}))
        CAP.draw(img, " ".join(tg["lines"]), tc, tg["start"], DUR, t, W, H, y_frac=tg.get("y"))
    a = np.asarray(img.convert("RGB"), np.float32)
    if STOPMO: a *= random.Random(int(ta*12)+99).uniform(.985, 1.015)
    return a

# ---------- transitions ----------
TORN = {}
def transition(A, B, q, d, kind, key):
    q = ease(q)
    if kind == "crossfade": return A*(1-q)+B*q
    if d < 0: return transition(A[:, ::-1], B[:, ::-1], q, 1, kind, key)[:, ::-1]  # mirror = same move from the other side
    X = xx[..., None]
    if kind == "slide":  # B slides in from the right, A slides away and darkens, soft shadow on A at B's edge
        off, sA = int((1-q)*W), int(q*.3*W); out = np.empty_like(A)
        out[:, :W-sA] = A[:, sA:]; out[:, W-sA:] = A[:, -1:]
        out *= 1-.35*q
        sh = np.clip(1-(off-X)/(40*U), 0, 1)*(X < off); out *= 1-.45*sh
        if off < W: out[:, off:] = B[:, :W-off]
        return out
    if kind == "torn":  # A is ripped away along a jagged edge, white paper fibres on the rim
        if key not in TORN:
            r = np.random.default_rng(key); n = np.cumsum(r.normal(0, 1, H)); n = (n-n.mean())/(np.abs(n).max()+1e-6)
            TORN[key] = (n*.05*W+np.repeat(r.normal(0, .006*W, H//6+1), 6)[:H])[:, None, None].astype(np.float32)
        e = q*W*1.25-.12*W+TORN[key]
        rim = (X >= e) & (X < e+9*U); shd = np.clip(1-(X-e)/(28*U), 0, 1)*(X >= e)
        out = np.where(X < e, B, A*(1-.25*shd)); return np.where(rim, out*.25+np.array([247, 242, 230], np.float32)*.75, out)
    if kind == "page":  # page lifts from the right edge, curled light backside, shadow on the page below
        e = (1-q)*W*1.15
        back = (X < e) & (X > e-.06*W); shB = np.clip(1-(X-e)/(.12*W), 0, 1)*(X >= e)
        out = np.where(X >= e, B*(1-.45*shB), A); hl = np.clip(1-(e-X)/(.06*W), 0, 1)
        return np.where(back, A*(1-hl*.6)+np.array([250, 246, 236], np.float32)*hl*.6, out)
    return A*(1-q)+B*q

def frame(t):
    act = [i for i, sc in enumerate(S) if sc["start"] <= t < sc["end"] or (i == len(S)-1 and t >= sc["start"])]
    if not act: act = [len(S)-1]
    if len(act) == 1: out = render_scene(act[0], t)
    else:
        i = act[-1]; a, b = render_scene(i-1, t), render_scene(i, t)
        q = (t-S[i]["start"])/max(.01, S[i-1]["end"]-S[i]["start"]); out = transition(a, b, q, S[i]["dir"], S[i].get("transition", TRANS), i)
    fade = min(1, t/.4, (DUR-t)/.5)
    return np.clip(out*MUL*fade, 0, 255).astype(np.uint8)

if PREVIEW:
    ts = [DUR*(k+.5)/PREVIEW for k in range(PREVIEW)]
    ts = sorted(set(ts+[S[i]["start"]+.3*(S[i-1]["end"]-S[i]["start"]) for i in range(1, len(S))]))[:max(PREVIEW, 6)+len(S)]
    th = [Image.fromarray(frame(t)).resize((W//3, H//3)) for t in ts]; cols = min(6, len(th)); rows = math.ceil(len(th)/cols)
    sheet = Image.new("RGB", (cols*(W//3+8), rows*(H//3+8)), (255, 0, 255))
    for k, im in enumerate(th): sheet.paste(im, ((k % cols)*(W//3+8), (k//cols)*(H//3+8)))
    sheet.save("preview.png"); print("OK preview.png", [round(t, 1) for t in ts]); sys.exit()

# SFX events for mix.py
for i in range(1, len(S)):
    k = S[i].get("transition", TRANS); EV.append({"t": round(S[i]["start"], 2), "kind": "paper" if k in ("torn", "page") else "whoosh"})
for sc in S:
    if sc.get("caption") and LOOK["anim"] in ("pop", "drop", "slide"): EV.append({"t": round(sc["start"]+.35, 2), "kind": "pop"})
if C.get("tagline"): EV.append({"t": round(C["tagline"]["start"], 2), "kind": "chime"})
json.dump(sorted(EV, key=lambda e: e["t"]), open(C.get("events", "events.json"), "w"), indent=0)

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", C.get("out", "video.mp4")], stdin=subprocess.PIPE)
def _job(n): return frame(n/FPS).tobytes()
import multiprocessing as mp
NF = int(DUR*FPS); procs = max(1, min(8, (os.cpu_count() or 2)))
if procs > 1:  # frames are independent -> render in parallel (fork shares the preloaded layers), keep order
    with mp.get_context("fork").Pool(procs) as pool:
        for buf in pool.imap(_job, range(NF), chunksize=8): ff.stdin.write(buf)
else:
    for n in range(NF): ff.stdin.write(_job(n))
ff.stdin.close(); ff.wait(); print("OK", C.get("out", "video.mp4"), "| events:", C.get("events", "events.json"))
