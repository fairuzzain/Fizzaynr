#!/usr/bin/env python3
"""Rapikan waktu kata + potong jeda (jump cut). SELALU dijalankan setelah word timing.

    python3 cuts.py <build> --level tidak|halus|sedang|agresif

Yang dikerjakan:
  1. Rapikan waktu kata ke awal bunyi sebenarnya (selalu, termasuk level "tidak").
     Waktu dari ASR maupun SRT sering meleset 0,3-1 detik pada kata pertama setelah jeda.
  2. Potong jeda panjang sesuai level (ini soal selera, TANYAKAN ke user):
       tidak   : tidak ada yang dipotong
       halus   : jeda > 0,9 dtk dipendekkan jadi 0,35 dtk
       sedang  : jeda > 0,55 dtk jadi 0,22 dtk, plus buang "eee/emm" yang tertranskrip
       agresif : jeda > 0,35 dtk jadi 0,12 dtk, plus buang "eee/emm" (gaya cepat ala short)
  3. Tulis ulang video kerja dan words.json supaya semuanya pakai timeline baru.

Membaca : <build>/src/main.mp4, <build>/words.json
Menulis : <build>/src/main.mp4 (versi terpotong; aslinya disimpan sebagai main_full.mp4)
          <build>/words.json   (aslinya disimpan sebagai words_full.json)
          <build>/cuts.json    (titik potong di timeline baru, dipakai autocap untuk zoom penyamar)
"""
import argparse, json, os, re, shutil, subprocess, sys
import numpy as np

FF = os.environ.get("FFMPEG_BIN", "ffmpeg")
FP = os.environ.get("FFPROBE_BIN", "ffprobe")
LEVELS = {"tidak": None, "halus": (0.9, 0.35, False), "sedang": (0.55, 0.22, True), "agresif": (0.35, 0.12, True)}
FILLER = re.compile(r"^(e+h*m*|e+m+|h+m+|u+m+|u+h+|a+h+|anu|ehem|eee+)[.,!?…]*$", re.I)
HOP = 0.01


def energy(path):
    raw = subprocess.run([FF, "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    hop = 160
    n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    return 20 * np.log10(e + 1e-6), len(x) / 16000.0


def runs(mask):
    """Rentang [mulai, selesai) dari nilai True berurutan, dalam indeks frame 10 ms."""
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]: j += 1
            out.append((i, j)); i = j
        else:
            i += 1
    return out


def snap(words, db):
    """Geser kata ke awal bunyi terdekat."""
    thr = max(np.percentile(db, 90) - 22, -60)
    voiced = db > thr
    out = []
    for k, (t, w) in enumerate(words):
        nxt = words[k + 1][0] if k + 1 < len(words) else t + 1.0
        prv = out[-1][0] if out else -1.0
        i = min(int(t / HOP), len(db) - 1)
        if not voiced[i]:
            # maju sampai bunyi mulai, tapi jangan melewati kata berikutnya
            while i < len(db) - 1 and not voiced[i] and (i * HOP) < nxt - 0.05: i += 1
        else:
            # mundur ke awal bagian bersuara kalau kata ini kata pertama setelah jeda
            j = i
            while j > 0 and voiced[j - 1] and (t - (j - 1) * HOP) < 0.35: j -= 1
            if j > 0 and not voiced[j - 1] and j * HOP > prv + 0.12:
                i = j
        nt = round(max(i * HOP, prv + 0.05), 2)
        out.append([nt, w])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--level", choices=list(LEVELS), default="sedang")
    a = ap.parse_args()
    B = a.build
    src = os.path.join(B, "src", "main.mp4")
    wp = os.path.join(B, "words.json")
    if not os.path.exists(wp):
        sys.exit("words.json belum ada. Jalankan srt2words.py atau wordtime.py dulu.")
    full = os.path.join(B, "src", "main_full.mp4")
    wfull = os.path.join(B, "words_full.json")
    # selalu mulai dari versi utuh, supaya cuts.py aman dijalankan ulang dengan level lain
    if os.path.exists(full): shutil.copy(full, src)
    else: shutil.copy(src, full)
    if os.path.exists(wfull): shutil.copy(wfull, wp)
    else: shutil.copy(wp, wfull)

    words = json.load(open(wp))
    db, dur = energy(src)
    words = snap(words, db)
    lv = LEVELS[a.level]
    if lv is None:
        json.dump(words, open(wp, "w"), ensure_ascii=False)
        json.dump({"level": "tidak", "segments": [[0, dur]], "cut_points": [], "removed": 0}, open(os.path.join(B, "cuts.json"), "w"))
        print(f"Waktu {len(words)} kata dirapikan. Tidak ada jeda yang dipotong (level: tidak).")
        return

    min_sil, keep, fill = lv
    thr = max(np.percentile(db, 90) - 26, -58)
    sp = db > thr
    # tutup lubang kecil di tengah ucapan, buang bunyi sangat pendek
    for s, e in runs(~sp):
        if (e - s) * HOP < 0.08 and s > 0: sp[s:e] = True
    for s, e in runs(sp):
        if (e - s) * HOP < 0.05: sp[s:e] = False
    # kata dianggap ucapan juga, supaya kata pelan tidak ikut terpotong
    for k, (t, w) in enumerate(words):
        nx = words[k + 1][0] if k + 1 < len(words) else t + 0.4
        s, e = int(t / HOP), int(min(nx, t + 0.45) / HOP)
        sp[s:e] = True

    remove = []
    sil = runs(~sp)
    for s, e in sil:
        t0, t1 = s * HOP, e * HOP
        if s == 0:                          # hening di awal video
            if t1 > 0.12: remove.append((0.0, t1 - 0.12))
            continue
        if e >= len(sp):                    # hening di akhir
            if t1 - t0 > 0.35: remove.append((t0 + 0.35, dur))
            continue
        if t1 - t0 > min_sil:
            remove.append((t0 + keep / 2, t1 - keep / 2))
    removed_words = []
    if fill:
        for k, (t, w) in enumerate(words):
            if FILLER.match(w.strip()):
                nx = words[k + 1][0] if k + 1 < len(words) else t + 0.5
                if nx - t <= 0.9:
                    remove.append((max(0, t - 0.02), nx - 0.03)); removed_words.append(w)
    # gabung rentang yang beririsan
    remove.sort(); merged = []
    for s, e in remove:
        if e - s < 0.04: continue
        if merged and s <= merged[-1][1] + 0.06: merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else: merged.append((s, e))
    total_rm = sum(e - s for s, e in merged)
    if total_rm < 0.25:
        json.dump(words, open(wp, "w"), ensure_ascii=False)
        json.dump({"level": a.level, "segments": [[0, dur]], "cut_points": [], "removed": 0}, open(os.path.join(B, "cuts.json"), "w"))
        print(f"Waktu {len(words)} kata dirapikan. Jeda di video ini sudah pendek, tidak ada yang perlu dipotong.")
        return
    keep_seg, cur = [], 0.0
    for s, e in merged:
        if s - cur > 0.06: keep_seg.append((round(cur, 3), round(s, 3)))
        cur = e
    if dur - cur > 0.06: keep_seg.append((round(cur, 3), round(dur, 3)))

    # render: trim tiap bagian + fade 6 ms supaya tidak ada bunyi klik
    lines = []
    for i, (s, e) in enumerate(keep_seg):
        d = e - s
        lines.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}];")
        lines.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={max(0, d - 0.006):.3f}:d=0.006[a{i}];")
    lines.append("".join(f"[v{i}][a{i}]" for i in range(len(keep_seg))) + f"concat=n={len(keep_seg)}:v=1:a=1[v][a]")
    script = os.path.join(B, "src", "_cuts.txt")
    open(script, "w").write("\n".join(lines))
    tmp = os.path.join(B, "src", "_cut.mp4")
    r = subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", full, "-filter_complex_script", script, "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "256k", tmp], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Gagal memotong video:\n" + r.stderr[-1200:])
    os.replace(tmp, src); os.remove(script)

    # petakan ulang waktu kata
    def remap(t):
        acc = 0.0
        for s, e in keep_seg:
            if t < s: return None
            if t <= e: return acc + (t - s)
            acc += e - s
        return None
    nw = []
    for t, w in words:
        m = remap(t)
        if m is None or (fill and FILLER.match(w.strip())): continue
        nw.append([round(m, 2), w])
    for i in range(1, len(nw)):
        if nw[i][0] <= nw[i - 1][0]: nw[i][0] = round(nw[i - 1][0] + 0.05, 2)
    json.dump(nw, open(wp, "w"), ensure_ascii=False)
    cp, acc = [], 0.0
    for s, e in keep_seg[:-1]:
        acc += e - s; cp.append(round(acc, 3))
    json.dump({"level": a.level, "segments": keep_seg, "cut_points": cp, "removed": round(total_rm, 2),
               "removed_words": removed_words}, open(os.path.join(B, "cuts.json"), "w"))
    newdur = sum(e - s for s, e in keep_seg)
    print(f"SELESAI: {len(cp)} potongan, {total_rm:.1f} dtk jeda dibuang. Durasi {dur:.1f} -> {newdur:.1f} dtk.")
    if removed_words:
        print("Kata pengisi yang dibuang:", " ".join(removed_words))
    print("Lanjutkan dengan frames.py (frame lama sudah tidak berlaku).")


if __name__ == "__main__":
    main()
