#!/usr/bin/env python3
"""Rakit index.html dari template + brand.json + project.json + words.json + scenes.js.

    python3 assemble.py <build>

Yang dilakukan:
  - Warna brand -> CSS variable + turunan otomatis (accentHi, tint chip/badge, blob latar).
  - Font: font pack bawaan (assets/fonts/, 21 font OFL). brand.json "font_preset": "jakarta" / "S2"
    (daftar: python3 fonts/fontpack.py list stmr, contoh: fonts/preview-stmr.jpg). Tanpa preset: Poppins.
    Font lain: "font": "<nama Google Font>" (npm @fontsource) atau "font_files" (file milik user).
    Keluarga CSS: P = font utama, D = font display (angka besar / kata hantaman; sama dengan P kalau preset tidak punya).
  - GSAP: disalin dari cache (~/.cache/script-to-motion-reel). Kalau belum ada, dipasang dari npm sekali.
  - Ikon: setiap icon('nama', ...) di scenes.js ditulis ke build/icon/ dari Phosphor fill bawaan.
    Ikon yang sudah kamu taruh sendiri di build/icon/ tidak ditimpa.
  - Emoji 3D: setiap emoji('nama', ...) yang belum ada di build/img/ diunduh (fetch_emoji.py).
  - TOTAL = durasi VO + semua jeda + tail.
Jalankan ulang setiap kali scenes.js / brand.json / project.json / words.json berubah.
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")
sys.path.insert(0, os.path.join(HERE, "fonts"))
import fontpack  # noqa: E402
CACHE = os.path.expanduser("~/.cache/script-to-motion-reel")
FP = os.environ.get("FFPROBE_BIN", "ffprobe")

DEFAULT_BRAND = {
    "accent": "#c8101e", "bg": "#0e0e11", "ink": "#141414", "paper": "#ffffff",
    "font": "Poppins", "success": "#16a34a",
}


# ---------- warna ----------
def hx(c):
    c = c.strip().lstrip("#")
    if len(c) == 3: c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in rgb)


def mix(a, b, k):  # k=0 -> a, k=1 -> b
    return to_hex(tuple(x + (y - x) * k for x, y in zip(hx(a), hx(b))))


def rgba(c, a):
    r, g, b = hx(c); return f"rgba({r},{g},{b},{a})"


def lum(c):
    r, g, b = [v / 255 for v in hx(c)]
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def derive(b):
    b = dict(DEFAULT_BRAND, **b)
    acc, bg = b["accent"], b["bg"]
    b.setdefault("accentHi", mix(acc, "#ffffff", .22))
    b.setdefault("accentSoft", mix(acc, "#ffffff", .9))
    b.setdefault("bgDeep", mix(bg, "#000000", .35))
    b.setdefault("bgLift", mix(bg, "#ffffff", .07))
    b.setdefault("tint1", mix(acc, "#ffffff", .9))
    b.setdefault("tint2", mix(acc, "#ffffff", .76))
    b.setdefault("tint3", mix(acc, "#ffffff", .5))
    b.setdefault("chipInk", mix(acc, "#000000", .8))
    b.setdefault("accentShade", rgba(mix(acc, "#000000", .35), .22))
    b["dark"] = lum(bg) < .2
    if "blobs" not in b:
        gray = mix(bg, "#ffffff", .2)
        b["blobs"] = [rgba(gray, .75), "rgba(0,0,0,.85)", rgba(mix(acc, "#000000", .25), .42),
                      rgba(mix(bg, "#ffffff", .15), .7), rgba(mix(acc, "#000000", .45), .3)]
    return b


# ---------- font ----------
WEIGHTS = [("400", "normal"), ("500", "normal"), ("600", "normal"), ("700", "normal"), ("800", "normal"), ("900", "normal"),
           ("500", "italic"), ("600", "italic"), ("700", "italic"), ("800", "italic"), ("900", "italic")]


def npm_get(pkg):
    os.makedirs(CACHE, exist_ok=True)
    d = os.path.join(CACHE, "node_modules", pkg)
    if not os.path.isdir(d):
        if not os.path.exists(os.path.join(CACHE, "package.json")):
            open(os.path.join(CACHE, "package.json"), "w").write('{"name":"stmr-cache","private":true}')
        r = subprocess.run(["npm", "i", "-s", "--no-audit", "--no-fund", pkg], cwd=CACHE, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.isdir(d):
            return None
    return d


def fonts(B, brand):
    """-> (daftar @font-face, label, ada_display)"""
    fd = os.path.join(B, "font"); os.makedirs(fd, exist_ok=True)
    name = brand.get("font", "Poppins")
    preset = brand.get("font_preset")
    if not preset and not brand.get("font_files") and name.lower() == "poppins":
        preset = "poppins"
    if preset:
        css, info = fontpack.build_css(preset, B, {"main": "P", "display": "D"})
        lab = f"preset {info['no']} {info['label']}" + (f" (display {info['display']})" if info.get("display") else "")
        return css.split("\n"), lab, bool(info.get("display"))
    css = []
    ff = brand.get("font_files")  # {"700": "aset/font/Brand-Bold.ttf", "700italic": "..."}
    if ff:
        for key, rel in ff.items():
            src = os.path.join(B, rel)
            if not os.path.exists(src):
                print("PERINGATAN: file font tidak ada:", rel); continue
            w = re.sub(r"\D", "", key) or "400"; st = "italic" if "italic" in key else "normal"
            dst = os.path.basename(src); shutil.copy(src, os.path.join(fd, dst))
            css.append(f"@font-face{{font-family:P;src:url(font/{dst});font-weight:{w};font-style:{st}}}")
        return css, name + " (file user)", False
    slug = name.lower().replace(" ", "-")
    pk = [k for k, v in fontpack.CAT["families"].items() if k == slug]
    if pk:
        srcdir, label = os.path.join(HERE, "fonts"), f"{name} (font pack)"
    else:
        pkg = npm_get(f"@fontsource/{slug}")
        if not pkg:
            print(f"PERINGATAN: font '{name}' tidak bisa diunduh dari npm. Pakai Poppins. "
                  "Minta file .ttf/.otf ke user lalu isi brand.json -> font_files.")
            css, info = fontpack.build_css("poppins", B, {"main": "P"})
            return css.split("\n"), "Poppins (cadangan)", False
        srcdir, label = os.path.join(pkg, "files"), f"{name} (npm)"
    for sub in ("latin-ext", "latin"):
        for w, st in WEIGHTS:
            f = f"{slug}-{sub}-{w}-{st}.woff2"
            p = os.path.join(srcdir, f)
            if not os.path.exists(p) and st == "italic":
                p = os.path.join(srcdir, f"{slug}-{sub}-{w}-normal.woff2")  # font tanpa italic: pakai normal
            if os.path.exists(p):
                shutil.copy(p, os.path.join(fd, os.path.basename(p)))
                rng = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" if sub == "latin" else "U+0100-024F,U+0259,U+1E00-1EFF,U+20A0-20AB,U+20AD-20CF,U+2C60-2C7F,U+A720-A7FF"
                css.append(f"@font-face{{font-family:P;src:url(font/{os.path.basename(p)});font-weight:{w};font-style:{st};unicode-range:{rng}}}")
    if not css:
        sys.exit(f"Font '{name}' tidak punya file woff2 yang bisa dipakai.")
    return css, label, False


# ---------- GSAP ----------
def gsap(B):
    d = npm_get("gsap")
    if not d:
        sys.exit("GSAP belum ada dan tidak bisa dipasang dari npm (internet?). Jalankan preflight.sh.")
    shutil.copy(os.path.join(d, "dist", "gsap.min.js"), os.path.join(B, "gsap.min.js"))


# ---------- ikon & emoji ----------
def icons(B, code, extra):
    names = set(re.findall(r"icon\(\s*['\"]([a-z0-9-]+)['\"]", code)) | set(extra or [])
    bank = json.load(open(os.path.join(VENDOR, "icons-fill.json")))
    idir = os.path.join(B, "icon"); os.makedirs(idir, exist_ok=True)
    wrote, miss = 0, []
    for n in sorted(names):
        p = os.path.join(idir, n + ".svg")
        if n in bank:
            if not os.path.exists(p) or open(p).read() == bank[n] or os.path.getsize(p) == 0:
                open(p, "w").write(bank[n]); wrote += 1
        elif not os.path.exists(p):
            miss.append(n)
    if miss:
        print("PERINGATAN ikon tidak ada di Phosphor fill:", ", ".join(miss))
        for m in miss:
            near = [k for k in bank if m.split("-")[0] in k][:6]
            if near: print(f"   mirip '{m}':", ", ".join(near))
        print("   Ganti namanya, atau ambil dari set lain: bash $SK/assets/fetch_icons.sh ...")
    return len(names), miss


def emojis(B, code):
    names = sorted(set(re.findall(r"emoji\(\s*['\"]([a-z0-9_]+)['\"]", code)))
    idir = os.path.join(B, "img"); os.makedirs(idir, exist_ok=True)
    need = [n for n in names if not os.path.exists(os.path.join(idir, n + ".png"))]
    if need:
        subprocess.run([sys.executable, os.path.join(HERE, "fetch_emoji.py"), idir, *need])
    miss = [n for n in names if not os.path.exists(os.path.join(idir, n + ".png"))]
    if miss:
        print("PERINGATAN emoji belum ada:", ", ".join(miss))
    return len(names), miss


def probe(p):
    r = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: sys.exit(f"Tidak bisa membaca durasi VO: {p}")


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    B = os.path.abspath(sys.argv[1])
    J = lambda f, d=None: json.load(open(os.path.join(B, f))) if os.path.exists(os.path.join(B, f)) else d
    proj = J("project.json")
    if proj is None: sys.exit("project.json belum ada (lihat references/production.md).")
    brand = derive(J("brand.json", {}))
    words = J("words.json", [])
    sp = os.path.join(B, "scenes.js")
    code = open(sp, encoding="utf-8").read() if os.path.exists(sp) else "// scenes.js kosong\n"

    vo = os.path.join(B, proj["vo"])
    if not os.path.exists(vo): sys.exit(f"File VO tidak ada: {proj['vo']}")
    vo_dur = probe(vo)
    pauses = sorted([[float(a), float(b)] for a, b in proj.get("pauses", [])])
    tail = float(proj.get("tail", 2.0))
    total = round(vo_dur + sum(d for _, d in pauses) + tail, 3)

    clips = J("clips.json", {})
    css_font, font_label, has_disp = fonts(B, brand)
    gsap(B)
    n_ic, miss_ic = icons(B, code, proj.get("icons"))
    n_em, miss_em = emojis(B, code)

    keys = ["accent", "accentHi", "accentSoft", "bg", "bgDeep", "bgLift", "ink", "paper", "success",
            "tint1", "tint2", "tint3", "chipInk", "accentShade"]
    cssvars = "".join(f"--{k}:{brand[k]};" for k in keys if k in brand) + ("--fd:D,P;" if has_disp else "--fd:P;")
    cfg = {"brand": brand, "words": words, "pauses": pauses, "total": total, "clips": clips,
           "voDur": round(vo_dur, 3), "tail": tail}
    html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    html = (html.replace("/*__FONTFACE__*/", "\n".join(css_font))
                .replace("/*__CSSVARS__*/", cssvars)
                .replace("/*__CONFIG__*/", json.dumps(cfg, ensure_ascii=False))
                .replace("/*__SCENES__*/", code))
    open(os.path.join(B, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html siap | TOTAL {total:.2f} dtk (VO {vo_dur:.2f} + jeda {sum(d for _, d in pauses):.2f} + ekor {tail:.1f})")
    print(f"  font {font_label} | ikon {n_ic} | emoji {n_em} | klip {len(clips)} | kata {len(words)}")
    if miss_ic or miss_em:
        print("  ADA ASET YANG HILANG (lihat peringatan di atas). Halaman tetap dirakit.")


if __name__ == "__main__":
    main()
