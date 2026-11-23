#!/usr/bin/env python3
"""Rakit template + components.js + build/scenes.js jadi build/index.html.

    python3 build.py <build>

Membaca <build>/project.json (semua opsional):
  {
    "main": "main",                     folder vf/<main> berisi frame video utama (30 fps)
    "ins": 45.3, "dur": 6.5,            sisipkan DUR detik hening mulai detik INS (0, 0 = tidak ada)
    "tail": 0.8,                        ekor setelah VO habis
    "duration": 30,                     hanya kalau TIDAK ada video utama (reel full motion graphic)
    "zoom": [[0, 5.03, 1.0, 540, 1060, 0.06], [5.03, 999, 1.05, 600, 470, 0.02]],
    "scrim_from": 5.03,                 scrim gelap di bawah caption aktif mulai detik ini
    "font_preset": "klasik"             preset font pack (E1-E9): python3 fonts/fontpack.py list editorial
  }
Yang dikerjakan:
  - konfigurasi proyek ditulis ke blok CONFIG di template (jumlah frame dan VEND dihitung dari vf/<main>)
  - CLIPS = jumlah frame tiap folder vf/*, jadi media({dir:'c1'}) tidak perlu n
  - components.js dan scenes.js disisipkan
  - gsap.min.js disalin (cache npm), ikon garis Phosphor yang dipakai ditulis ke build/icon/
  - font preset dipasang ke halaman (file ke build/font/), tanpa internet
Jalankan ulang setiap kali scenes.js atau project.json berubah.
"""
import glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHES = [os.path.expanduser("~/.cache/serif-editorial-reel"), os.path.expanduser("~/.cache/script-to-motion-reel")]


def gsap(B):
    for c in [os.path.join(B, "node_modules")] + [os.path.join(x, "node_modules") for x in CACHES]:
        p = os.path.join(c, "gsap", "dist", "gsap.min.js")
        if os.path.exists(p):
            shutil.copy(p, os.path.join(B, "gsap.min.js")); return
    c = CACHES[0]; os.makedirs(c, exist_ok=True)
    if not os.path.exists(os.path.join(c, "package.json")):
        open(os.path.join(c, "package.json"), "w").write('{"name":"serif-editorial-cache","private":true}')
    r = subprocess.run(["npm", "i", "-s", "--no-audit", "--no-fund", "gsap"], cwd=c, capture_output=True, text=True)
    p = os.path.join(c, "node_modules", "gsap", "dist", "gsap.min.js")
    if r.returncode != 0 or not os.path.exists(p):
        sys.exit("GSAP tidak ada dan tidak bisa dipasang dari npm. Cek internet / jalankan preflight.sh.")
    shutil.copy(p, os.path.join(B, "gsap.min.js"))


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    B = os.path.abspath(sys.argv[1])
    pj = os.path.join(B, "project.json")
    proj = json.load(open(pj)) if os.path.exists(pj) else {}
    main_dir = proj.get("main", "main")
    frames = len(glob.glob(os.path.join(B, "vf", main_dir, "*.jpg")))
    if frames:
        vend = round(frames / 30, 3)
    elif proj.get("duration"):
        vend = float(proj["duration"]); frames = 1
        print("Catatan: tanpa video utama (full motion graphic). Pakai bgMotion([]) atau latar sendiri.")
    else:
        sys.exit(f"Tidak ada frame di vf/{main_dir}/ dan project.json tidak punya 'duration'.")
    ins, dur, tail = float(proj.get("ins", 0)), float(proj.get("dur", 0)), float(proj.get("tail", .8))
    total = round(vend + dur + tail, 3)
    zoom = proj.get("zoom") or [[0, total + 1, 1.0, 540, 900, .04]]
    clips = {os.path.basename(d): len(glob.glob(os.path.join(d, "*.jpg"))) for d in sorted(glob.glob(os.path.join(B, "vf", "*"))) if os.path.isdir(d)}
    cfg = "\n".join([
        "/* ==== CONFIG START (diisi build.py dari project.json) ==== */",
        f"const MAIN={json.dumps(main_dir)};",
        f"const MAIN_FRAMES={frames};",
        f"const VEND={vend};",
        f"const INS={ins}, DUR={dur};",
        f"const TAIL={tail};",
        "const TOTAL=+(VEND+DUR+TAIL).toFixed(3);",
        "const T=t=>(DUR&&t>=INS)?+(t+DUR).toFixed(3):t;",
        f"const SCRIM_FROM={float(proj.get('scrim_from', 0))};",
        f"const ZOOM={json.dumps(zoom)};",
        f"const CLIPS={json.dumps(clips)};",
        "/* ==== CONFIG END ==== */"])

    html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    html = re.sub(r"/\* ==== CONFIG START.*?/\* ==== CONFIG END ==== \*/", lambda m: cfg, html, flags=re.S)
    comp = open(os.path.join(HERE, "components.js"), encoding="utf-8").read()
    sp = os.path.join(B, "scenes.js")
    scenes = open(sp, encoding="utf-8").read() if os.path.exists(sp) else ""
    if not scenes.strip(): print("Catatan: scenes.js kosong; halaman hanya berisi video.")
    for marker, payload in (("/* === COMPONENTS === */", comp), ("/* === SCENES === */", scenes)):
        if marker not in html: sys.exit(f"Penanda {marker} tidak ada di template.")
        html = html.replace(marker, payload, 1)
    out = os.path.join(B, "index.html")
    open(out, "w", encoding="utf-8").write(html)

    gsap(B)
    # ikon garis (Phosphor regular bawaan) yang dipakai
    bank = json.load(open(os.path.join(HERE, "vendor", "icons-regular.json")))
    used = set(re.findall(r"icon\(\s*['\"]([a-z0-9-]+)['\"]", html)) | {"check", "x"}   # check/x dipakai badgeIcon()
    idir = os.path.join(B, "icon"); os.makedirs(idir, exist_ok=True)
    miss = []
    for n in sorted(used):
        p = os.path.join(idir, n + ".svg")
        if os.path.exists(p): continue
        if n in bank: open(p, "w").write(bank[n])
        else: miss.append(n)
    if miss: print("PERINGATAN ikon tidak ada di Phosphor regular:", ", ".join(miss))
    # font preset
    preset = proj.get("font_preset", "klasik")
    r = subprocess.run([sys.executable, os.path.join(HERE, "fonts", "fontpack.py"), "css", preset, B,
                        "body=I", "key=PF", "mono=JB", "--inject", out, "--upper", ".s,.r,.g,.R,.m .tx"], capture_output=True, text=True)
    if r.returncode != 0: sys.exit("Font preset gagal dipasang:\n" + r.stderr[-600:] + r.stdout[-300:])
    label = json.loads(r.stdout.strip().splitlines()[-1])
    print(f"index.html siap | TOTAL {total:.2f} dtk (video {vend:.2f} + jeda {dur:.2f} + ekor {tail:.2f}) | "
          f"font {label['no']} {label['label']} | ikon {len(used)} | klip {len(clips)}")


if __name__ == "__main__":
    main()
