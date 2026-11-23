#!/usr/bin/env python3
"""Rakit halaman video: template + mesin animasi + konfigurasi + caption + scene -> index.html.

    python3 assemble.py <folderBuild>

Membaca:
  <build>/project.json   pengaturan proyek (warna, font, glow, jeda, ekor, audio). Dibuat default kalau belum ada.
  <build>/vf/main/       frame video utama (jumlahnya dihitung otomatis)
  <build>/captions.js    hasil autocap.py (opsional)
  <build>/extra/*.js     helper tambahan (opsional)
  <build>/scenes.js      scene buatan sendiri (opsional)
  <build>/icon/*.svg     ikon tambahan; ikon bawaan diambil dari assets/vendor/icons.json
Cari nama ikon bawaan:  python3 assemble.py --icons [kata]
Menulis:
  <build>/index.html, <build>/font/ (font bawaan disalin otomatis)

Panjang video (TOTAL) dan peta waktu srcT() DIHITUNG di sini dari project.json,
dan mix.py membaca file yang sama. Jadi halaman dan audio selalu sinkron.
"""
import base64, glob, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")
sys.path.insert(0, os.path.join(HERE, "fonts"))
import fontpack  # noqa: E402  font pack bawaan: python3 fonts/fontpack.py list editorial, contoh: fonts/preview-editorial.jpg

DEFAULT = {
    "glow": True, "c1": "#86EF5A", "c2": "#3FA9FF",
    "font": {"mode": "sans", "file": None, "body": "inter"},
    "pauses": [], "tail": 0.0, "grain": "auto",
    "audio": {"sfx": True, "ambience": False, "music": None, "music_level": "pelan", "lufs": -14},
}


def load_project(build):
    p = os.path.join(build, "project.json")
    if not os.path.exists(p):
        json.dump(DEFAULT, open(p, "w"), indent=2)
        print("project.json belum ada, dibuat dengan nilai default:", p)
    d = json.load(open(p))
    out = json.loads(json.dumps(DEFAULT))
    for k, v in d.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict): out[k].update(v)
        else: out[k] = v
    return out


def timeline(build, proj):
    """Hitung jumlah frame, SRC_END, TOTAL, dan fungsi srcT() dari project.json."""
    main = proj.get("main", "main")
    frames = len(glob.glob(os.path.join(build, "vf", main, "*.jpg")))
    if frames == 0:
        sys.exit(f"Tidak ada frame di {build}/vf/{main}/. Jalankan frames.py dulu.")
    src_end = round(frames / 30, 3)
    pauses = sorted([float(a), float(b)] for a, b in proj.get("pauses", []))
    total = round(src_end + sum(b for _, b in pauses) + float(proj.get("tail", 0)), 3)
    # srcT(t): detik di SUMBER untuk detik t di HASIL. Jeda = frame dibekukan.
    lines = ["function srcT(t){", "  let s=t;"]
    shift = 0.0
    for at, ln in pauses:
        a_out = at + shift   # titik jeda di timeline hasil
        lines.append(f"  if(t>={a_out:.3f}&&t<{a_out + ln:.3f})return {at:.3f};")
        lines.append(f"  if(t>={a_out + ln:.3f})s=t-{shift + ln:.3f};")
        shift += ln
    lines.append(f"  return Math.min(Math.max(0,s),{src_end:.3f});")
    lines.append("}")
    return main, frames, src_end, total, pauses, "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--icons":     # daftar / cari nama ikon bawaan: assemble.py --icons [kata]
        names = sorted(json.load(open(os.path.join(VENDOR, "icons.json"))))
        q = sys.argv[2].lower() if len(sys.argv) > 2 else ""
        print(" ".join(n for n in names if q in n)); return
    build = sys.argv[1].rstrip("/")
    proj = load_project(build)
    main_dir, frames, src_end, total, pauses, srct = timeline(build, proj)

    # font bawaan -> build/font
    fdst = os.path.join(build, "font"); os.makedirs(fdst, exist_ok=True)
    for f in glob.glob(os.path.join(VENDOR, "fonts", "*.woff2")):
        d = os.path.join(fdst, os.path.basename(f))
        if not os.path.exists(d): shutil.copy(f, d)

    font = proj["font"]; mode = font.get("mode", "sans"); body = font.get("body", "inter")
    userfont = ""
    if font.get("preset"):
        # preset font pack (E1-E9): PB = teks biasa, PK = kata kunci (satu potongan, tanpa tebal/miring palsu)
        css, info = fontpack.build_css(font["preset"], build, {"body": "PB", "key": "PK"})
        st = info.get("key_style", "italic")
        upper = ":root[data-font=\"preset\"] .s,:root[data-font=\"preset\"] .k1,:root[data-font=\"preset\"] .k2,:root[data-font=\"preset\"] .X,:root[data-font=\"preset\"] .k{text-transform:uppercase}" if info.get("upper") else ""
        userfont = (css + f"\n:root[data-font=\"preset\"]{{--kf:PK,PF;--kfs:{st};--kw:400;--kwX:400;--kls:{'-.01em' if st == 'italic' else '-.02em'}}}"
                    + "\n:root[data-body=\"preset\"]{--bf:PB,I}\n" + upper)
        mode = "preset"; body = "preset" if font.get("preset_body", True) else body
        print(f"font: preset {info['no']} {info['label']} ({info.get('body')} + {info.get('key')})")
    elif mode == "custom" or body == "custom":
        ff = font.get("file")
        if not ff or not os.path.exists(os.path.join(build, ff)):
            print(f"PERINGATAN: font custom '{ff}' tidak ditemukan di folder build, kembali ke mode serif.")
            mode, body = "serif", "inter"
        else:
            fmt = {"ttf": "truetype", "otf": "opentype", "woff": "woff", "woff2": "woff2"}.get(ff.rsplit(".", 1)[-1].lower(), "truetype")
            userfont = (f"@font-face{{font-family:UF;src:url({ff}) format('{fmt}');font-weight:100 900;font-style:normal}}\n"
                        f"@font-face{{font-family:UF;src:url({ff}) format('{fmt}');font-weight:100 900;font-style:italic}}")

    a = proj.get("audio", {})
    config = "\n".join([
        f"const MAIN={json.dumps(main_dir)};",
        f"const MAIN_FRAMES={frames};",
        f"const SRC_END={src_end};",
        f"const TOTAL={total};",
        f"const PAUSES={json.dumps(pauses)};",
        f"const GLOW={'true' if proj.get('glow', True) else 'false'};",
        f"const C1={json.dumps(proj.get('c1', '#86EF5A'))}, C2={json.dumps(proj.get('c2', '#3FA9FF'))};",
        f"const FONT_MODE={json.dumps(mode)}, FONT_BODY={json.dumps(body)};",
        f"const GRAIN={json.dumps(proj.get('grain', 'auto'))};",
        f"const USE_SFX={'true' if a.get('sfx', True) else 'false'};",
        srct,
        "/* T(s): ubah detik SUMBER (dari transkrip/words.json) ke detik HASIL (setelah jeda disisipkan). */",
        "function T(s){let o=s;for(const[a,l] of PAUSES)if(s>=a-1e-6)o+=l;return +o.toFixed(3);}",
    ])

    def read_opt(p):
        return open(p).read() if os.path.exists(p) else ""

    captions = read_opt(os.path.join(build, "captions.js"))
    extra = "".join(open(p).read() + "\n" for p in sorted(glob.glob(os.path.join(build, "extra", "*.js"))))
    scenes = read_opt(os.path.join(build, "scenes.js"))
    if not scenes.strip():
        print("Catatan: scenes.js belum ada atau kosong. Halaman hanya berisi video + caption.")

    # ikon: yang dipakai di caption/scene, dari build/icon dulu, lalu ikon bawaan
    used = set(re.findall(r"""icon\(\s*['"]([\w-]+)['"]""", captions + extra + scenes))
    used |= set(re.findall(r"""chip\([^)]*?,\s*['"]([\w-]+)['"]\s*\)""", captions + extra + scenes))
    # chipC(p,x,y,teks,warna,ikon,t): ikon = argumen ke-6
    used |= set(re.findall(r"""chipC\((?:[^,()]*,){5}\s*['"]([\w-]+)['"]""", captions + extra + scenes))
    used |= {"plus"}   # dipakai helper plusSign() di template
    bundled = json.load(open(os.path.join(VENDOR, "icons.json")))
    icons, missing = {}, []
    for n in sorted(used | {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(build, "icon", "*.svg"))}):
        p = os.path.join(build, "icon", n + ".svg")
        if os.path.exists(p):
            icons[n] = base64.b64encode(open(p, "rb").read()).decode()
        elif n in bundled:
            icons[n] = base64.b64encode(bundled[n].encode()).decode()
        elif n in used:
            missing.append(n)
    icon_js = (
        "const ICONS=" + json.dumps(icons) + ";\n"
        "function icon(name,size,color='#fff'){const d=ICONS[name];"
        "if(!d){console.warn('ikon hilang:',name);return '';}"
        "return `<span class=\"ic\" style=\"width:${size}px;height:${size}px;background:${color};"
        "-webkit-mask-image:url(data:image/svg+xml;base64,${d})\"></span>`}\n"
    )

    s = open(os.path.join(HERE, "template.html")).read()
    engine = open(os.path.join(VENDOR, "motion.js")).read()
    for marker, payload in (("/* === USERFONT === */", userfont), ("/* === ENGINE === */", engine),
                            ("/* === CONFIG === */", config), ("/* === ICONS === */", icon_js),
                            ("/* === CAPTIONS === */", captions), ("/* === SCENES === */", extra + scenes)):
        if s.count(marker) != 1:
            sys.exit(f"penanda {marker} tidak ketemu tepat sekali di template")
        s = s.replace(marker, payload)

    out = os.path.join(build, "index.html")
    open(out, "w").write(s)
    print(f"{out}  {len(s)//1024} KB | frame sumber {frames} ({src_end} dtk) | jeda {sum(b for _, b in pauses):.2f} dtk"
          f" | ekor {float(proj.get('tail', 0)):.2f} dtk | TOTAL {total} dtk | {len(icons)} ikon")
    if missing:
        print("IKON TIDAK DITEMUKAN:", ", ".join(missing), "-> cari nama yang ada dengan: assemble.py --icons <kata>")


if __name__ == "__main__":
    main()
