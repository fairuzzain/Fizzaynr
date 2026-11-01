"""Find the best 9:16 frame inside each photo: level, weigh, search, pick, show.

Usage: python autocrop.py <run_dir> [--plan crop_plan.json] [--only f02 f05] [--size 1080x1920]
Reads <run>/crop_plan.json (written by Claude after looking at every photo; boxes are NORMALISED
x0,y0,x1,y1 on the ORIGINAL upright photo <run>/photos/pNN.jpg, never on the contact sheet):
{"shots": [
  {"photo": "p03", "hero": [0.41, 0.30, 0.62, 0.88], "keep": [[0.70, 0.20, 0.95, 0.45]],
   "drop": "bin left, railing, empty sky", "people": true, "symmetric": false, "look": "left",
   "tilt": null, "pick": null, "box": null, "fit": "crop"}
]}
  hero      the subject the crop must keep (>= 97 %, people >= 99.5 %)
  keep      secondary subjects worth keeping (people: every keep box must be kept whole)
  people    true -> faces/heads never cut, headroom kept, group stays together
  symmetric true -> hero centred instead of on a thirds line
  look      "left" | "right": direction someone looks or walks -> leave space on that side
  tilt      null = auto (0.4-8 deg corrected), 0 = never rotate, number = rotate by that (deg, + = CCW)
  pick      1 | 2 | 3 = take that candidate instead of the top score (after looking at the sheet)
  box       manual 9:16 crop [x0, y0, x1, y1] normalised on the LEVELLED photo (overrides the search)
  fit       "crop" (default) | "blur" (whole photo over a blurred copy, for photos no 9:16 crop can save)
Frames are written in plan order: <run>/frames/fNN.png + frames/index.json (read by clean.py),
review sheets <run>/review/fNN.png (original | analysis | candidates 1-3) and fNN_ba.png (before | after).
"""
import argparse, json, math, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

AN = 1000  # analysis long side (px)


def font(size):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()


# ---------------------------------------------------------------- level
def estimate_tilt(gray):
    """Tilt in degrees (+ = the picture is rotated clockwise, correct with a CCW rotation of the same size)."""
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 60, 160)
    h, w = gray.shape
    lines = cv2.HoughLinesP(edges, 1, np.pi / 720, threshold=80, minLineLength=int(0.12 * max(h, w)), maxLineGap=8)
    if lines is None:
        return 0.0, 0
    dev, wt = [], []
    for x1, y1, x2, y2 in np.asarray(lines).reshape(-1, 4):
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if dy < 0 or (dy == 0 and dx < 0): dx, dy = -dx, -dy
        a = math.degrees(math.atan2(dy, dx))          # 0..180
        if a > 90: a -= 180                             # -90..90 for near-horizontal
        if abs(a) <= 10:
            dev.append(a); wt.append(L)
        else:
            av = math.degrees(math.atan2(dy, dx))       # near-vertical: 80..100
            if abs(av - 90) <= 10:
                dev.append(av - 90); wt.append(0.7 * L)
    if not dev:
        return 0.0, 0
    o = np.argsort(dev); d, c = np.array(dev)[o], np.cumsum(np.array(wt)[o])
    return float(d[np.searchsorted(c, c[-1] / 2)]), len(dev)


def rot_matrix(w, h, ang):
    return cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)


def warp_box(box, M):
    x0, y0, x1, y1 = box
    pts = np.array([[x0, y0, 1], [x1, y0, 1], [x0, y1, 1], [x1, y1, 1]], np.float64) @ M.T
    return [pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()]


# ---------------------------------------------------------------- weigh
def saliency(rgb):
    h, w = rgb.shape[:2]
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    sw = 64; sh = max(8, round(h * sw / w))
    small = cv2.resize(g, (sw, sh), interpolation=cv2.INTER_AREA)
    F = np.fft.fft2(small)
    logA = np.log(np.abs(F) + 1e-6)
    R = logA - cv2.blur(logA, (3, 3))
    sr = np.abs(np.fft.ifft2(np.exp(R + 1j * np.angle(F)))) ** 2
    sr = cv2.GaussianBlur(sr.astype(np.float32), (0, 0), 2.5)
    sr = cv2.resize(sr, (w, h), interpolation=cv2.INTER_LINEAR)
    lab = cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
    cc = np.linalg.norm(lab - lab.reshape(-1, 3).mean(0), axis=2)
    cc = cv2.GaussianBlur(cc, (0, 0), 8)
    n = lambda a: (a - a.min()) / (a.max() - a.min() + 1e-9)
    return 0.5 * n(sr) + 0.5 * n(cc)


def faces(rgb):
    try:
        cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        fs = cas.detectMultiScale(g, 1.1, 6, minSize=(max(16, g.shape[0] // 40),) * 2)
    except Exception:
        return []
    out = []
    for x, y, w, h in (fs if len(fs) else []):  # grow to the whole head
        out.append([x - 0.25 * w, y - 0.45 * h, x + 1.25 * w, y + 1.15 * h])
    return out


def inter(box, X, Y, w, h):
    ix = np.clip(np.minimum(box[2], X + w) - np.maximum(box[0], X), 0, None)
    iy = np.clip(np.minimum(box[3], Y + h) - np.maximum(box[1], Y), 0, None)
    return ix * iy


def rect_sum(II, X, Y, w, h):
    x0 = np.round(X).astype(int); y0 = np.round(Y).astype(int)
    x1 = np.round(X + w).astype(int); y1 = np.round(Y + h).astype(int)
    return II[y1, x1] - II[y0, x1] - II[y1, x0] + II[y0, x0]


# ---------------------------------------------------------------- search
def search(sal, valid, hero, keeps, facebx, opt):
    H, W = sal.shape
    II = cv2.integral(sal.astype(np.float64))
    IV = cv2.integral((1 - valid).astype(np.float64))
    total_mean = sal.mean() + 1e-9
    harea = max(1e-6, (hero[2] - hero[0]) * (hero[3] - hero[1]))
    hcx, hcy = (hero[0] + hero[2]) / 2, (hero[1] + hero[3]) / 2
    hmax = min(H, W * 16 / 9)
    cands = []
    for s in np.linspace(0.4, 1.0, 25):
        h = s * hmax; w = h * 9 / 16
        if w > W - 1 or h > H - 1:
            h = min(H - 1, (W - 1) * 16 / 9); w = h * 9 / 16
        xs = np.arange(0, W - w, max(2.0, (W - w) / 48)) if W - w > 2 else np.array([0.0])
        ys = np.arange(0, H - h, max(2.0, (H - h) / 48)) if H - h > 2 else np.array([0.0])
        X, Y = np.meshgrid(xs, ys); X, Y = X.ravel(), Y.ravel()
        ok = rect_sum(IV, X, Y, w, h) < 0.5
        if not ok.any(): continue
        X, Y = X[ok], Y[ok]
        cov = inter(hero, X, Y, w, h) / harea
        u, v = (hcx - X) / w, (hcy - Y) / h
        ut = np.array([0.5]) if opt["symmetric"] else np.array([1 / 3, 2 / 3])
        du = np.min(np.abs(u[:, None] - ut[None]), 1)
        dv = np.min(np.abs(v[:, None] - np.array([1 / 3, 0.5, 2 / 3])[None]), 1)
        comp = 1 - np.clip(np.hypot(du, 0.7 * dv) / 0.35, 0, 1)
        r = (hero[3] - hero[1]) / h
        size = np.clip(r / 0.35, 0, 1) - np.clip((r - 0.92) * 4, 0, 1)
        keep = np.ones_like(X); pen = np.zeros_like(X); need = np.ones_like(X, bool)
        if keeps:
            kc = np.stack([inter(k, X, Y, w, h) / max(1e-6, (k[2] - k[0]) * (k[3] - k[1])) for k in keeps])
            keep = kc.mean(0)
            pen -= 0.5 * ((kc > 0.05) & (kc < 0.9)).sum(0)
            if opt["people"]: need &= (kc >= 0.99).all(0)
        for f in facebx:
            fc = inter(f, X, Y, w, h) / max(1e-6, (f[2] - f[0]) * (f[3] - f[1]))
            pen -= 1.0 * ((fc > 0.05) & (fc < 0.95))
        if opt["people"]:
            pen -= 0.5 * (((hero[1] - Y) / h) < 0.03)
        if opt["look"] == "left": pen += 0.15 * np.sign(u - 0.5)
        if opt["look"] == "right": pen -= 0.15 * np.sign(u - 0.5)
        inside = rect_sum(II, X, Y, w, h)
        b = 0.035 * w
        inner = rect_sum(II, X + b, Y + b, w - 2 * b, h - 2 * b)
        dens_r = (inside / (w * h)) / total_mean
        dens = np.clip(np.log2(np.maximum(dens_r, 1e-6)), -1, 1) * 0.5 + 0.5
        ring = (inside - inner) / max(1e-6, w * h - (w - 2 * b) * (h - 2 * b))
        border = 1 - np.clip((ring / (inner / ((w - 2 * b) * (h - 2 * b)) + 1e-9)) / 1.5, 0, 1)
        score = 1.0 * comp + 0.7 * size + 0.6 * keep + 0.6 * dens + 0.8 * border + 0.25 * s + pen
        for i in range(len(X)):
            cands.append((float(score[i]), float(cov[i]), bool(need[i]), [float(X[i]), float(Y[i]), float(X[i] + w), float(Y[i] + h)]))
    if not cands:
        return [], "no valid 9:16 crop"
    thr = 0.995 if opt["people"] else 0.97
    good = [c for c in cands if c[1] >= thr and c[2]]
    note = ""
    if not good:
        best = max(c[1] for c in cands); thr = best - 0.02
        good = [c for c in cands if c[1] >= thr]
        note = f"hero only fits {best:.0%} in any 9:16 crop (or a keep box/group cannot stay whole) - check it, or use fit blur"
    good.sort(key=lambda c: -c[0])
    picks = []
    for c in good:
        if all(iou(c[3], p[3]) < 0.5 for p in picks): picks.append(c)
        if len(picks) == 3: break
    return picks, note


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    return i / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i + 1e-9)


def fit_box(box, W, H):
    """Make a normalised manual box 9:16 around its centre and keep it inside WxH (px)."""
    cx, cy = (box[0] + box[2]) / 2 * W, (box[1] + box[3]) / 2 * H
    h = min(max((box[3] - box[1]) * H, (box[2] - box[0]) * W * 16 / 9), H, W * 16 / 9); w = h * 9 / 16
    x0 = min(max(0, cx - w / 2), W - w); y0 = min(max(0, cy - h / 2), H - h)
    return [x0, y0, x0 + w, y0 + h]


def blurfit(im, W, H):
    s = max(W / im.width, H / im.height)
    bg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.6)
    s = min(W / im.width, H / im.height)
    fg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg


# ---------------------------------------------------------------- sheets
def panel(im, H):
    return im.resize((max(1, round(im.width * H / im.height)), H), Image.LANCZOS)


def draw_box(d, b, k, col, wdt, label=None, f=None):
    x0, y0, x1, y1 = [v * k for v in b]
    d.rectangle((x0, y0, x1, y1), outline=col, width=wdt)
    if label: d.text((x0 + 6, y0 + 4), label, fill=col, font=f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("--plan", default="crop_plan.json")
    ap.add_argument("--only", nargs="*"); ap.add_argument("--size", default="1080x1920")
    a = ap.parse_args()
    run = Path(a.run)
    OW, OH = map(int, a.size.split("x"))
    plan = json.loads((run / a.plan).read_text())["shots"]
    (run / "frames").mkdir(exist_ok=True); (run / "review").mkdir(exist_ok=True)
    idx_p = run / "frames/index.json"
    old = {f["frame"]: f for f in json.loads(idx_p.read_text())["frames"]} if idx_p.exists() and a.only else {}
    index = []
    for n, sh in enumerate(plan, 1):
        fname = f"f{n:02d}"
        if a.only and fname not in a.only:
            index.append(old.get(f"frames/{fname}.png", {"frame": f"frames/{fname}.png", "photo": sh["photo"]})); continue
        full = Image.open(run / "photos" / f"{sh['photo']}.jpg").convert("RGB")
        FW, FH = full.size
        k = AN / max(FW, FH)
        an = np.asarray(full.resize((round(FW * k), round(FH * k)), Image.LANCZOS))
        H, W = an.shape[:2]
        hero_n = sh.get("hero") or [0.25, 0.25, 0.75, 0.75]
        to_px = lambda b: [b[0] * W, b[1] * H, b[2] * W, b[3] * H]
        info = {"frame": f"frames/{fname}.png", "photo": sh["photo"], "source": str(run / "photos" / f"{sh['photo']}.jpg")}
        if sh.get("fit") == "blur":
            out = blurfit(full, OW, OH); out.save(run / "frames" / f"{fname}.png")
            info.update(fit="blur"); index.append(info)
            Image.fromarray(np.hstack([np.asarray(panel(full, 900)), np.asarray(panel(out, 900))])).save(run / "review" / f"{fname}_ba.png")
            print(f"{fname} <- {sh['photo']} blur-fit"); continue
        # level
        t_auto, nl = estimate_tilt(cv2.cvtColor(an, cv2.COLOR_RGB2GRAY))
        t = sh.get("tilt")
        if t is None: t = t_auto if 0.4 <= abs(t_auto) <= 8 else 0.0
        M = rot_matrix(W, H, t)
        lev = cv2.warpAffine(an, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0)) if t else an
        valid = cv2.warpAffine(np.ones((H, W), np.uint8), M, (W, H), flags=cv2.INTER_NEAREST, borderValue=0) if t else np.ones((H, W), np.uint8)
        valid = cv2.erode(valid, np.ones((5, 5), np.uint8))
        hero = warp_box(to_px(hero_n), M)
        keeps = [warp_box(to_px(b), M) for b in sh.get("keep", [])]
        sal = saliency(lev)
        wsal = sal.copy()
        for b, wgt in [(hero, 1.0)] + [(kb, 0.5) for kb in keeps]:
            x0, y0, x1, y1 = [int(round(v)) for v in b]
            wsal[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] += wgt
        wsal *= valid
        fb = faces(lev) if sh.get("people") else []
        opt = {"symmetric": bool(sh.get("symmetric")), "people": bool(sh.get("people")), "look": sh.get("look")}
        if sh.get("box"):
            picks, note = [(0.0, 1.0, True, fit_box(sh["box"], W, H))], "manual box"
        else:
            picks, note = search(wsal, valid, hero, keeps, fb, opt)
        if not picks:
            print(f"{fname} <- {sh['photo']}: {note}; use fit blur or a manual box", file=sys.stderr); continue
        pi = min(max(1, int(sh.get("pick") or 1)), len(picks)) - 1
        crop = picks[pi][3]
        # full-res crop from the levelled full photo
        Mf = rot_matrix(FW, FH, t)
        levf = Image.fromarray(cv2.warpAffine(np.asarray(full), Mf, (FW, FH), flags=cv2.INTER_LANCZOS4, borderValue=(0, 0, 0))) if t else full
        cf = [v / k for v in crop]
        cf = [max(0, cf[0]), max(0, cf[1]), min(FW, cf[2]), min(FH, cf[3])]
        cut = levf.crop(tuple(round(v) for v in cf))
        out = cut.resize((OW, OH), Image.LANCZOS)
        out.save(run / "frames" / f"{fname}.png")
        warn = []
        if cut.height < 700: warn.append(f"small crop ({cut.width}x{cut.height}px) - looser crop or warn the user")
        if note and note != "manual box": warn.append(note)
        info.update(tilt=round(t, 2), tilt_auto=round(t_auto, 2), lines=nl, pick=pi + 1,
                    crop_levelled=[round(c / v, 4) for c, v in zip(crop, (W, H, W, H))],
                    crop_px=[cut.width, cut.height], score=round(picks[pi][0], 3), hero_kept=round(picks[pi][1], 3),
                    candidates=[{"score": round(p[0], 3), "box": [round(c / v, 4) for c, v in zip(p[3], (W, H, W, H))]} for p in picks],
                    warnings=warn)
        index.append(info)
        # review sheet: original | analysis | candidates
        PH = 900; f1 = font(26); f2 = font(20)
        org = panel(full, PH); d = ImageDraw.Draw(org); ko = PH / FH
        draw_box(d, [v / k for v in to_px(hero_n)], ko, (255, 220, 0), 4, "hero", f2)
        for b in sh.get("keep", []): draw_box(d, [v / k for v in to_px(b)], ko, (0, 220, 255), 3, "keep", f2)
        heat = cv2.applyColorMap((sal * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)[:, :, ::-1]
        anim = Image.fromarray((0.55 * lev + 0.45 * heat).astype(np.uint8))
        anim = panel(anim, PH); d = ImageDraw.Draw(anim); ka = PH / H
        for f in fb: draw_box(d, f, ka, (255, 0, 200), 2)
        for i, p in enumerate(picks):
            draw_box(d, p[3], ka, (60, 255, 90) if i == pi else (255, 255, 255), 5 if i == pi else 2, f"{i + 1}  {p[0]:.2f}", f2)
        x0, y0, x1, y1 = [v * ka for v in crop]
        for j in (1, 2):
            d.line((x0 + (x1 - x0) * j / 3, y0, x0 + (x1 - x0) * j / 3, y1), fill=(60, 255, 90), width=1)
            d.line((x0, y0 + (y1 - y0) * j / 3, x1, y0 + (y1 - y0) * j / 3), fill=(60, 255, 90), width=1)
        d.rectangle((0, 0, anim.width, 34), fill=(0, 0, 0))
        d.text((8, 4), f"tilt {t:+.1f} deg (auto {t_auto:+.1f}, {nl} lines)", fill=(255, 255, 255), font=f2)
        tiles = [org, anim]
        for i, p in enumerate(picks):
            c = [v / k for v in p[3]]
            tile = panel(levf.crop(tuple(round(v) for v in c)), PH); d = ImageDraw.Draw(tile)
            d.rectangle((0, 0, tile.width, 40), fill=(0, 0, 0))
            d.text((8, 6), f"{i + 1}{'  PICK' if i == pi else ''}", fill=(60, 255, 90) if i == pi else (255, 255, 255), font=f1)
            tiles.append(tile)
        sheet = Image.new("RGB", (sum(t_.width for t_ in tiles) + 12 * (len(tiles) - 1), PH), (16, 16, 16))
        x = 0
        for t_ in tiles: sheet.paste(t_, (x, 0)); x += t_.width + 12
        sheet.save(run / "review" / f"{fname}.png")
        ba = Image.new("RGB", (org.width + 12 + panel(out, PH).width, PH), (16, 16, 16))
        ba.paste(panel(full, PH), (0, 0)); ba.paste(panel(out, PH), (org.width + 12, 0))
        ba.save(run / "review" / f"{fname}_ba.png")
        print(f"{fname} <- {sh['photo']} tilt {t:+.1f} crop {cut.width}x{cut.height} score {picks[pi][0]:.2f} pick {pi + 1}/{len(picks)}"
              + ("".join(f"\n   ! {w}" for w in warn)))
    idx_p.write_text(json.dumps({"size": [OW, OH], "aspect": "9:16" if OH > OW else "16:9", "frames": index}, indent=1))
    print(f"{len(index)} frames -> {run / 'frames'}; review sheets in {run / 'review'}", file=sys.stderr)


if __name__ == "__main__":
    main()
