#!/usr/bin/env python3
"""Caption otomatis: pecah words.json jadi caption per kata, pilih posisi yang tidak menutup wajah,
pilih alat kontras sesuai kecerahan latar, buat zoom berirama, dan SFX halus di kata kunci.

    python3 autocap.py <build> --list      # tampilkan kata bernomor, untuk memilih kata kunci
    python3 autocap.py <build>             # tulis <build>/captions.js

Diatur lewat <build>/capplan.json (semua opsional):
{
  "style": "pendek",            // "pendek" = 1-3 kata per caption, "sedang" = 3-6 kata, 2 baris
  "keys": {"12": "k1", "13": "k1", "40": "X", "57": "s", "88": "k2"},
                                // nomor kata -> kelas. s = kata kunci putih, k1 = aksen 1 (positif),
                                // k2 = aksen 2 (teknis/info), X = kata hantaman (maks 2 per video)
  "hook_end": 3.8,              // kata sebelum detik ini tampil sebagai JUDUL besar (hook)
  "skip": [[10.2, 14.0]],       // rentang yang teksnya ditampilkan scene buatan sendiri
  "breaks": [23, 40],           // paksa caption baru mulai di nomor kata ini
  "zoom": true,                 // zoom berirama (pilihan user)
  "scale": 1.0,                 // perbesar/perkecil semua caption
  "y": null                     // paksa posisi y semua caption (mis. 1400). Kosong = otomatis
}
Semua waktu di capplan.json memakai timeline SUMBER (sama dengan words.json).
"""
import argparse, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vision as V  # noqa: E402

SIZE = {"n": 52, "s": 98, "k1": 100, "k2": 100, "k": 92, "X": 190}
TITLE = {"n": 72, "s": 128, "k1": 132, "k2": 132, "k": 118, "X": 200}
WEAK = {"yang", "di", "ke", "dari", "dan", "untuk", "dengan", "atau", "itu", "ini", "si", "para", "the", "a", "an",
        "of", "to", "and", "or", "in", "on", "for", "with", "my", "your", "biar", "kalau", "tapi", "karena", "jadi"}
SAFE_W = 790          # lebar maksimal satu baris caption (safe zone 830 dikurangi margin)
BOTTOM_Y, TOP_Y, MID_Y = 1400, 330, 960


def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default


def char_factor(cls, mode):
    if cls == "n": return 0.56
    return {"serif": 0.50, "sans": 0.63, "custom": 0.62}.get(mode, 0.56)


def word_w(w, cls, size, mode):
    pad = 0.3 * size if cls == "k" else 0
    return len(w) * char_factor(cls, mode) * size + 0.24 * size + pad


def est_end(t, w, nxt):
    return min(nxt, t + 0.12 + 0.075 * len(w))


def out_time(s, pauses):
    return round(s + sum(l for at, l in pauses if s >= at - 1e-6), 3)


def frame_at(build, t_src, nframes):
    i = max(1, min(nframes, int(round(t_src * 30)) + 1))
    return V.read_image(os.path.join(build, "vf", "main", f"{i:04d}.jpg"))


def overlap(face, y0, y1):
    if not face: return 0.0
    x, y, w, h = face[:4]
    a = max(0, min(y + h, y1) - max(y, y0)) * max(0, min(x + w, 955) - max(x, 125))
    return a / max(1.0, w * h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    B = a.build
    words = load(os.path.join(B, "words.json"), None)
    if not words:
        sys.exit("words.json belum ada.")
    if a.list:
        lines, cur = [], []
        for i, (t, w) in enumerate(words):
            if cur and (t - est_end(words[i - 1][0], words[i - 1][1], t) > 0.35 or re.search(r"[.!?]$", words[i - 1][1])):
                lines.append(" ".join(cur)); cur = []
            if not cur: cur.append(f"[{t:6.2f}]")
            cur.append(f"{i}:{w}")
        if cur: lines.append(" ".join(cur))
        txt = "\n".join(lines)
        open(os.path.join(B, "words_list.txt"), "w").write(txt + "\n")
        print(txt)
        print(f"\n{len(words)} kata. Pilih kata kunci lalu tulis nomornya di capplan.json -> \"keys\".")
        return

    plan = load(os.path.join(B, "capplan.json"), {})
    proj = load(os.path.join(B, "project.json"), {})
    cuts = load(os.path.join(B, "cuts.json"), {})
    style = plan.get("style", "pendek")
    keys = {int(k): v for k, v in plan.get("keys", {}).items()}
    hook_end = float(plan.get("hook_end", 0) or 0)
    skip = [tuple(map(float, s)) for s in plan.get("skip", [])]
    breaks = set(int(b) for b in plan.get("breaks", []))
    zoom_on = plan.get("zoom", True)
    scale = float(plan.get("scale", 1.0))
    force_y = plan.get("y")
    mode = (proj.get("font") or {}).get("mode", "serif")
    pauses = sorted([float(x), float(y)] for x, y in proj.get("pauses", []))
    use_sfx = (proj.get("audio") or {}).get("sfx", True)
    nframes = len(glob.glob(os.path.join(B, "vf", "main", "*.jpg")))
    if nframes == 0:
        sys.exit("vf/main kosong. Jalankan frames.py dulu.")
    nX = sum(1 for v in keys.values() if v == "X")
    if nX > 2:
        print(f"PERINGATAN: {nX} kata hantaman (X). Lebih dari 2 per video terasa murah.")

    maxw, maxc, sil = (3, 20, 0.25) if style == "pendek" else (6, 34, 0.35)

    # ---------- 1. kelompokkan kata ----------
    groups, cur = [], []
    def in_skip(t): return any(s <= t < e for s, e in skip)
    for i, (t, w) in enumerate(words):
        if in_skip(t):
            if cur: groups.append(cur); cur = []
            continue
        if cur:
            pt, pw = words[cur[-1]]
            gap = t - est_end(pt, pw, t)
            chars = sum(len(words[j][1]) + 1 for j in cur) + len(w)
            brk = (i in breaks or gap > sil or re.search(r"[.!?]$", pw)
                   or (re.search(r"[,;:]$", pw) and len(cur) >= 2)
                   or len(cur) >= maxw or chars > maxc
                   or keys.get(i) == "X" or keys.get(cur[-1]) == "X"
                   or (hook_end and pt < hook_end <= t))
            if brk and not (gap > sil or re.search(r"[.!?,;:]$", pw)) and len(cur) >= 2 \
                    and words[cur[-1]][1].lower().strip(".,") in WEAK and keys.get(i) != "X":
                groups.append(cur[:-1]); cur = [cur[-1]]; brk = False
                if len(cur) >= maxw: brk = True
            if brk:
                groups.append(cur); cur = []
        cur.append(i)
    if cur: groups.append(cur)

    # ---------- 2. tata letak, posisi, kontras ----------
    out_lines, scrims, sfx_list, preview = [], [], [], []
    prev_pos, last_tick = None, -9.0
    n_top = n_bright = 0
    for gi, g in enumerate(groups):
        t0 = words[g[0]][0]
        tl_ = words[g[-1]][0]
        nxt = words[groups[gi + 1][0]][0] if gi + 1 < len(groups) else None
        end = est_end(tl_, words[g[-1]][1], nxt if nxt else tl_ + 2)
        hold = 0.5 if style == "pendek" else 0.7
        t1 = end + hold
        if nxt is not None and nxt - t1 < 0.9: t1 = nxt - 0.02
        if any(s < t1 and e > t0 for s, e in skip):
            t1 = min([s for s, e in skip if s > t0] + [t1])
        t1 = max(t1, tl_ + 0.45)
        if nxt is not None: t1 = min(t1, nxt - 0.02)   # caption tidak boleh menumpuk dengan berikutnya
        title = hook_end and t0 < hook_end
        S = TITLE if title else SIZE
        mid = (t0 + t1) / 2
        img = frame_at(B, mid, nframes)
        fs = V.faces(img) if img is not None else []
        fboxes = [f[:4] for f in fs[:3]]

        # posisi
        toks = [(words[j][1], keys.get(j, "n"), j) for j in g]
        est_h = 0
        has_big = any(c != "n" for _, c, _ in toks)
        est_h = (S["n"] * 1.1 + (S["k1"] * 1.0 if has_big else 0)) * scale
        if force_y:
            y = int(force_y); pos = "fixed"
        else:
            band = lambda yc: sum(overlap(f, yc - est_h / 2 - 20, yc + est_h / 2 + 20) for f in fboxes)
            cand = {"bottom": band(BOTTOM_Y), "top": band(TOP_Y) + 0.04}
            if len(fboxes) >= 2: cand["middle"] = band(MID_Y) + 0.02   # dua orang atas-bawah: garis tengah
            if prev_pos in cand and cand[prev_pos] < 0.15: pos = prev_pos
            else: pos = min(cand, key=cand.get)
            y = {"bottom": BOTTOM_Y, "top": TOP_Y, "middle": MID_Y}[pos]
            if pos == "bottom" and cand["bottom"] > 0.3: y = 1460
            if title and pos == "top": y = 360
        prev_pos = pos if pos != "fixed" else prev_pos
        if pos in ("top", "middle"): n_top += 1

        lum = V.luminance(img, y - est_h / 2 - 30, y + est_h / 2 + 30, 125, 955) if img is not None else 0.3
        bright = lum > 0.62
        mid_lum = 0.42 < lum <= 0.62
        if bright: n_bright += 1

        # kelas akhir: di latar terang, kata kunci jadi blok warna (bukan glow)
        def final_cls(c):
            if c == "n" or c == "X": return c
            if bright: return "k alt" if c == "k2" else "k"
            return c
        toks = [(w, final_cls(c), j) for w, c, j in toks]

        # pecah jadi baris: kata besar dapat baris sendiri, baris kepanjangan dipecah
        lines, curl = [], []
        def base(c): return c.split(" ")[0]
        for w, c, j in toks:
            big = base(c) != "n"
            if curl and (big != (base(curl[-1][1]) != "n")):
                lines.append(curl); curl = []
            curl.append((w, c, j))
        if curl: lines.append(curl)
        def lw(L, k=1.0): return sum(word_w(w, base(c), S[base(c)] * scale * k, mode) for w, c, j in L)
        fixed = []
        for L in lines:
            if lw(L) <= SAFE_W or len(L) == 1:
                fixed.append(L); continue
            # pecah seimbang
            best, bi = 1e9, 1
            for k in range(1, len(L)):
                d = max(lw(L[:k]), lw(L[k:]))
                if d < best: best, bi = d, k
            fixed += [L[:bi], L[bi:]]
        lines = fixed
        # gabung baris kecil berturutan kalau muat, maksimal 3 baris
        while len(lines) > 3:
            merged = False
            for k in range(len(lines) - 1):
                if base(lines[k][0][1]) == "n" and base(lines[k + 1][0][1]) == "n" and lw(lines[k] + lines[k + 1]) <= SAFE_W:
                    lines[k] = lines[k] + lines[k + 1]; del lines[k + 1]; merged = True; break
            if not merged: break
        # ukuran per kata: kecilkan kalau satu kata saja sudah terlalu lebar
        js_lines = []
        for L in lines:
            k = min(1.0, SAFE_W / max(1, lw(L)))
            row = []
            for w, c, j in L:
                b = base(c); sz = round(S[b] * scale * k)
                item = [w, out_time(words[j][0], pauses), c]
                if sz != SIZE[b]: item.append({"fontSize": f"{sz}px"})
                row.append(item)
            js_lines.append(row)
        if len(js_lines) > 1 and pos == "bottom":
            y = min(y, 1560 - int(est_h / 2) - 30)

        T0, T1 = out_time(t0, pauses), out_time(t1, pauses)
        out_lines.append(f"cap({T1}, {y}, {json.dumps(js_lines, ensure_ascii=False)});")
        if bright or mid_lum:
            scrims.append([pos, T0, T1, y])
        if use_sfx:
            for w, c, j in toks:
                b = base(c); tt = out_time(words[j][0], pauses)
                if b == "X": sfx_list.append(f"sfx({tt},'sub',.9);"); last_tick = tt
                elif b != "n" and tt - last_tick > 1.2: sfx_list.append(f"sfx({tt},'tick',.7);"); last_tick = tt
        preview.append(f"[{T0:6.2f}-{T1:6.2f}] {pos:6s} y={y} {'TERANG' if bright else ('sedang' if mid_lum else '      ')} "
                       + " | ".join(" ".join(f"{w.upper() if base(c) != 'n' else w}" for w, c, j in L) for L in lines))

    # gabung scrim berurutan supaya tidak berkedip
    sc_js, last = [], None
    for pos, s, e, y in scrims:
        if last and last[0] == pos and s - last[2] < 0.35:
            last[2] = e; last[3] = max(last[3], y) if pos == "bottom" else last[3]
        else:
            if last: sc_js.append(last)
            last = [pos, s, e, y]
    if last: sc_js.append(last)
    sc_lines = [(f"scrimT({s},{e});" if p == "top" else (f"scrimM({s},{e},{y});" if p == "middle" else f"scrimB({s},{e},{y});"))
                for p, s, e, y in sc_js]

    # ---------- 3. zoom berirama ----------
    zl = []
    if zoom_on:
        total_src = nframes / 30.0
        cps = [float(c) for c in cuts.get("cut_points", [])]
        bounds = set(round(c, 3) for c in cps)
        for gi, g in enumerate(groups[1:], 1):
            t = words[g[0]][0]; pt, pw = words[groups[gi - 1][-1]]
            if t - est_end(pt, pw, t) > 0.3: bounds.add(round(t - 0.02, 3))
        bounds = sorted(b for b in bounds if 0.5 < b < total_src - 0.5)
        segs, last_b, state = [], 0.0, 0
        for b in bounds:
            is_cut = any(abs(b - c) < 0.01 for c in cps)
            if b - last_b >= (0.8 if is_cut else 2.2):
                segs.append((last_b, b, state)); last_b = b; state ^= 1
        segs.append((last_b, total_src + 10, state))
        xwords = [words[j][0] for j, v in keys.items() if v == "X" and j < len(words)]
        for s, e, st in segs:
            img = frame_at(B, s + 0.05, nframes)
            fs = V.faces(img) if img is not None else []
            if fs:
                x, y_, w, h = fs[0][:4]; ox, oy = x + w / 2, y_ + h / 2
            else:
                ox, oy = 540, 860
            ox = int(min(780, max(300, ox))); oy = int(min(1300, max(500, oy)))
            sc = 1.0 if st == 0 else (1.18 if any(s <= xw < e for xw in xwords) else 1.12)
            if len(fs) >= 2: sc, ox, oy = min(sc, 1.06), 540, 960      # dua orang di layar: zoom tipis di tengah
            dr = 0.025 if st == 0 else 0.012
            zl.append([out_time(s, pauses), out_time(e, pauses) if e < total_src else 1e9, sc, ox, oy, dr])
        # jeda yang disisipkan: jangan zoom di frame beku
    js = ["/* Dibuat otomatis oleh autocap.py. Jangan edit file ini: ubah capplan.json lalu jalankan ulang. */"]
    if zl: js.append("setZoom(" + json.dumps(zl) + ");")
    js += sc_lines + out_lines + sfx_list
    open(os.path.join(B, "captions.js"), "w").write("\n".join(js) + "\n")
    open(os.path.join(B, "captions_preview.txt"), "w").write("\n".join(preview) + "\n")

    dropped = [w for t, w in words if in_skip(t)]
    print(f"captions.js: {len(groups)} caption ({style}), {n_top} di atas/tengah, {len(groups) - n_top} di bawah, "
          f"{n_bright} di latar terang, {len(sc_lines)} scrim, {len(zl)} segmen zoom, {len(sfx_list)} sfx.")
    if not V.available():
        print("Catatan: deteksi wajah tidak tersedia, semua caption di posisi default.")
    if dropped:
        print(f"Kata di rentang skip ({len(dropped)}) harus tampil lewat scene buatan sendiri:", " ".join(dropped[:40]))
    print("Pratinjau (lengkap di captions_preview.txt):")
    for p in preview[:12]: print("  " + p)
    if len(preview) > 12: print(f"  ... {len(preview) - 12} lagi")


if __name__ == "__main__":
    main()
