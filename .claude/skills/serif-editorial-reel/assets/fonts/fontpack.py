#!/usr/bin/env python3
"""Font pack bawaan skill: 21 keluarga font OFL + preset pasangan font.

    python3 fontpack.py list [stmr|editorial]                     daftar preset (S1-S6 untuk Script to Motion, E1-E9 untuk Serif Editorial / Dark Motion)
    python3 fontpack.py css <preset> <build> body=I key=PF   salin file ke <build>/font/ dan tulis <build>/fonts.css
    python3 fontpack.py css <preset> <build> body=I key=PF mono=JB --inject <build>/index.html [--upper ".s,.r"]
        sekaligus mengganti baris @font-face keluarga I/PF/JB di halaman itu dengan font preset
        (--upper: selector kata kunci yang dijadikan HURUF BESAR kalau presetnya meminta, mis. E7 Tegas)

Peran dan nama keluarga CSS-nya ditentukan skill pemanggil:
  main=P     satu keluarga lengkap (400-900, normal + italic asli)            -> Script to Motion
  display=D  satu potongan font untuk angka besar / kata hantaman             -> Script to Motion
  body=I     teks biasa, semua bobot yang ada                                 -> Serif Editorial / Dark Motion
  key=PF     kata kunci: SATU potongan (bobot + gaya dari preset) didaftarkan
             untuk bobot 100-900 dan gaya normal + italic, supaya browser tidak membuat
             tebal/miring palsu apa pun yang diminta template
  mono=JB    JetBrains Mono
Preview semua preset: preview-stmr.jpg dan preview-editorial.jpg di folder ini. Tunjukkan ke user saat bertanya font.
Font lain (Google Font apa pun, atau file .ttf/.otf milik user) tetap bisa dipakai lewat cara masing-masing skill.
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = [HERE, os.path.join(HERE, "..", "vendor", "fonts")]   # pack + font bawaan lama skill
CAT = json.load(open(os.path.join(HERE, "fontpack.json")))


def find(slug, w, st):
    fn = f"{slug}-latin-{w}-{st}.woff2"
    for d in DIRS:
        p = os.path.join(d, fn)
        if os.path.exists(p): return p
    return None


def faces(slug, fam, build, single=None):
    """-> daftar @font-face. single=(w, st): satu potongan untuk semua bobot/gaya."""
    fd = os.path.join(build, "font"); os.makedirs(fd, exist_ok=True)
    out = []
    if single:
        w, st = single
        p = find(slug, w, st) or find(slug, w, "normal")
        if not p: raise SystemExit(f"File font {slug} {w} {st} tidak ada di pack.")
        shutil.copy(p, fd)
        for style in ("normal", "italic"):
            out.append(f"@font-face{{font-family:{fam};src:url(font/{os.path.basename(p)});font-weight:100 900;font-style:{style}}}")
        return out
    for w in (400, 500, 600, 700, 800, 900):
        for st in ("normal", "italic"):
            p = find(slug, w, st)
            if p:
                shutil.copy(p, fd)
                out.append(f"@font-face{{font-family:{fam};src:url(font/{os.path.basename(p)});font-weight:{w};font-style:{st}}}")
    if not out: raise SystemExit(f"Keluarga {slug} tidak ada di pack.")
    return out


def build_css(preset, build, roles):
    """roles: {"main": "P", "display": "D", "body": "I", "key": "PF", "mono": "JB"} -> (css, info)"""
    pr = CAT["presets"].get(preset) or next((v for v in CAT["presets"].values() if v["no"].lower() == str(preset).lower()), None)
    if not pr: raise SystemExit(f"Preset '{preset}' tidak ada. Lihat: python3 fontpack.py list")
    css, info = [], {"label": pr["label"], "no": pr["no"], "upper": bool(pr.get("upper"))}
    if "main" in roles and pr.get("main"):
        css += faces(pr["main"], roles["main"], build); info["main"] = CAT["families"][pr["main"]]
    if "display" in roles:
        if pr.get("display"):
            slug, w, st = pr["display"]; css += faces(slug, roles["display"], build, (w, st))
            info["display"] = CAT["families"][slug]
        else:
            info["display"] = None
    if "body" in roles and pr.get("body"):
        css += faces(pr["body"], roles["body"], build); info["body"] = CAT["families"][pr["body"]]
    if "key" in roles and pr.get("key"):
        slug, w, st = pr["key"]; css += faces(slug, roles["key"], build, (w, st))
        info["key"] = CAT["families"][slug]; info["key_style"] = st; info["key_weight"] = w
    if "mono" in roles:
        css += faces("jetbrains-mono", roles["mono"], build)
    return "\n".join(css), info


def main():
    a = sys.argv[1:]
    if not a or a[0] not in ("list", "css"): sys.exit(__doc__)
    if a[0] == "list":
        want = a[1] if len(a) > 1 else None
        for k, v in CAT["presets"].items():
            if want and v["for"] != want: continue
            print(f"{v['no']:3s} {k:18s} {v['label']:20s} {v['desc']}")
        return
    if len(a) < 3: sys.exit(__doc__)
    opt = {}
    for flag in ("--inject", "--upper"):
        if flag in a:
            i = a.index(flag); opt[flag] = a[i + 1]; del a[i:i + 2]
    preset, build = a[1], a[2]
    roles = dict(x.split("=", 1) for x in a[3:]) or {"body": "I", "key": "PF", "mono": "JB"}
    css, info = build_css(preset, build, roles)
    if info.get("upper") and opt.get("--upper"):
        css += "\n" + opt["--upper"] + "{text-transform:uppercase}"
    open(os.path.join(build, "fonts.css"), "w").write(css + "\n")
    if opt.get("--inject"):
        import re
        hp = opt["--inject"]; html = open(hp, encoding="utf-8").read()
        fams = "|".join(re.escape(f) for f in roles.values())
        pat = re.compile(r"@font-face\{font-family:(?:" + fams + r");[^}]*\}\n?")
        m = pat.search(html)
        if not m: sys.exit(f"Tidak ada @font-face untuk {list(roles.values())} di {hp}")
        html = html[:m.start()] + "/*FONTPACK*/" + pat.sub("", html[m.start():], count=0)
        html = html.replace("/*FONTPACK*/", css + "\n", 1)
        open(hp, "w", encoding="utf-8").write(html)
        print(f"@font-face di {hp} diganti dengan preset.")
    print(f"{info['no']} {info['label']} -> {build}/fonts.css + {build}/font/")
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
