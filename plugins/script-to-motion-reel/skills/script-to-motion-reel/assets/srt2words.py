#!/usr/bin/env python3
"""Ubah subtitle (.srt atau .vtt) jadi words.json, tanpa perlu ASR.

  python3 srt2words.py sub.srt words.json [--offset 0] [--report]

Kenapa ini ada: jalur ASR harus mengunduh model sekitar 850 MB tiap percakapan
baru dan bisa salah pada nama produk. Kalau user sudah punya subtitle, waktunya
dipakai langsung. Lebih cepat, dan ejaannya pasti benar.

Dua jenis subtitle ditangani otomatis:
  - Per kata (tiap cue satu kata)  -> waktunya dipakai apa adanya, paling akurat
  - Per baris (cue berisi kalimat) -> waktu dalam baris dibagi proporsional
    menurut panjang kata, dengan bobot len(kata)+1.5

Keluaran sama persis dengan wordtime.py: [[detik, "kata"], ...]
"""
import sys, re, json, argparse

TS = re.compile(r"(\d{1,2}):(\d{2}):(\d{2})[.,](\d{1,3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[.,](\d{1,3})")
TAG = re.compile(r"<[^>]+>")
SPK = re.compile(r"^\s*(?:-\s*)?[A-Z][A-Za-z0-9 _.'-]{0,24}:\s")

def secs(h, m, s, ms):
    return int(h)*3600 + int(m)*60 + int(s) + int(ms.ljust(3, "0"))/1000

def parse(path):
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    cues, lines, i = [], raw.split("\n"), 0
    while i < len(lines):
        m = TS.search(lines[i])
        if not m:
            i += 1; continue
        st = secs(*m.group(1, 2, 3, 4)); en = secs(*m.group(5, 6, 7, 8))
        i += 1; body = []
        while i < len(lines) and lines[i].strip() and not TS.search(lines[i]):
            body.append(lines[i]); i += 1
        txt = " ".join(body)
        txt = TAG.sub("", txt)
        txt = SPK.sub("", txt)
        txt = txt.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt and en > st: cues.append((st, en, txt))
    return cues

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--offset", type=float, default=0.0, help="geser semua waktu, detik")
    ap.add_argument("--report", action="store_true", help="cetak transkrip utuh untuk dicek")
    args = ap.parse_args()

    cues = parse(args.src)
    if not cues:
        sys.exit("Tidak ada cue yang terbaca. Pastikan file .srt atau .vtt yang benar.")

    # buang cue yang isinya sama persis dan beririsan (umum di subtitle YouTube)
    ded = []
    for st, en, tx in cues:
        if ded and ded[-1][2] == tx and st < ded[-1][1] + .05:
            ded[-1] = (ded[-1][0], max(ded[-1][1], en), tx); continue
        ded.append((st, en, tx))
    cues = ded

    perword = sum(1 for _, _, t in cues if len(t.split()) == 1) / len(cues) > .6

    words = []
    if perword:
        for st, en, tx in cues:
            for w in tx.split(): words.append([round(st, 2), w])
    else:
        for st, en, tx in cues:
            ws = tx.split()
            if not ws: continue
            wt = [len(w) + 1.5 for w in ws]; tot = sum(wt); span = max(en - st, .05)
            acc = 0.0
            for w, k in zip(ws, wt):
                words.append([round(st + span * acc / tot, 2), w]); acc += k

    words.sort(key=lambda x: x[0])
    for i in range(1, len(words)):
        if words[i][0] <= words[i-1][0]:
            words[i][0] = round(words[i-1][0] + .05, 2)
    if args.offset:
        words = [[round(t + args.offset, 2), w] for t, w in words]

    json.dump(words, open(args.out, "w"), ensure_ascii=False)

    jenis = "per kata" if perword else "per baris (waktu dibagi proporsional)"
    print(f"{len(cues)} cue, {len(words)} kata, jenis subtitle: {jenis}")
    print(f"mulai {words[0][0]:.2f} dtk, selesai {words[-1][0]:.2f} dtk -> {args.out}")
    if not perword:
        print("Catatan: batas kalimat akurat, kata di tengah baris hasil perkiraan.")
        print("Kalau ada caption yang terasa meleset, geser manual di words.json.")
    if args.report:
        print("\n== transkrip ==")
        print(" ".join(w for _, w in words))
        print("\n== 20 kata pertama dengan waktunya ==")
        print(" ".join(f"{w}@{t}" for t, w in words[:20]))

if __name__ == "__main__":
    main()
