#!/usr/bin/env python3
"""Fetch fonts from npm @fontsource into the project and write fonts/fonts.css.

Usage (run inside the HyperFrames project folder):
  python <skill>/scripts/fonts.py anton dela-gothic-one bangers
Each font gets a CSS class .f-<name> (e.g. .f-anton) and a family name you can
use directly ("F Anton"). Picks the heaviest latin weight available (900→400)
unless you pin one: anton:400, playfair-display:900i (i = italic).
Exits 1 if any font failed, so a failed download never silently falls back
to the default font.
"""
import glob, json, os, re, shutil, subprocess, sys, tarfile, tempfile

WEIGHTS = ["900", "800", "700", "600", "500", "400"]


def fetch(name, pin, tmp):
    r = subprocess.run(["npm", "pack", f"@fontsource/{name}", "--silent", "--pack-destination", tmp],
                       capture_output=True, text=True)
    tgz = (r.stdout.strip().splitlines() or [""])[-1]
    path = os.path.join(tmp, tgz)
    if r.returncode != 0 or not os.path.isfile(path):
        return None, f"npm pack failed: {r.stderr.strip()[:120]}"
    with tarfile.open(path) as t:
        members = [m for m in t.getmembers() if m.name.endswith(".woff2") and "-latin-" in m.name
                   and "-latin-ext-" not in m.name]
        style = "italic" if pin and pin.endswith("i") else "normal"
        weights = [pin.rstrip("i")] if pin else WEIGHTS
        for w in weights:
            for m in members:
                if m.name.endswith(f"-latin-{w}-{style}.woff2"):
                    os.makedirs("fonts", exist_ok=True)
                    dst = os.path.join("fonts", f"{name}-{w}-{style}.woff2")
                    with t.extractfile(m) as src, open(dst, "wb") as out:
                        shutil.copyfileobj(src, out)
                    return (dst, w, style), None
        have = sorted({re.sub(r".*-latin-(\d+)-(\w+)\.woff2", r"\1 \2", m.name) for m in members})
        return None, f"no latin {weights} {style} file (has: {', '.join(have)[:80]})"


def main():
    names = sys.argv[1:]
    if not names:
        print(__doc__)
        sys.exit(2)
    tmp = tempfile.mkdtemp()
    css, ok, bad = [], [], []
    for spec in names:
        name, _, pin = spec.partition(":")
        res, err = fetch(name, pin or None, tmp)
        if not res:
            bad.append(f"{name}: {err}")
            continue
        dst, w, style = res
        fam = "F " + name.replace("-", " ").title()
        css.append(f'@font-face{{font-family:"{fam}";src:url("{os.path.basename(dst)}") format("woff2");'
                   f'font-weight:{w};font-style:{style};font-display:block}}\n'
                   f'.f-{name}{{font-family:"{fam}";font-weight:{w};font-style:{style}}}\n')
        ok.append({"font": name, "family": fam, "class": f".f-{name}", "weight": w, "style": style, "file": dst})
    if css:
        with open("fonts/fonts.css", "w") as fh:
            fh.write("".join(css))
    for o in ok:
        print(f"OK   {o['class']:24s} family \"{o['family']}\" {o['weight']} {o['style']}  {o['file']}")
    for b in bad:
        print("FAIL " + b)
    if ok:
        print('Add to <head>: <link rel="stylesheet" href="fonts/fonts.css">  then put the class on each big word.')
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
