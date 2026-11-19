#!/usr/bin/env python3
"""Anti-slop + motion lint for HyperFrames compositions (RB Digital video skills).

Reads index.html (and compositions/*.html next to it) statically and flags the
patterns that make AI videos look like moving slide decks:

  chrome   C_COUNTER   "02 / 05" scene counters
           C_TIMECODE  fake timecodes / clocks
           C_PROGRESS  progress bars
           C_CORNER    small labels parked in a corner
           C_KICKER    small tracked-caps line (kicker) over a headline
           C_VIBECARD  "Good morning" / status-dot UI cards
  type     T_TYPEWRITER letter-by-letter typed text with a caret
  motion   M_SCALE0    things growing from scale 0
           M_FADES     too many opacity-only entrances (move, don't fade)
           M_OVERSHOOT too many back/elastic/bounce eases, or big overshoot
           M_EXIT      exits using an .out ease (exits should accelerate)
           M_PRESETS   ease presets (E / F helpers) missing

Some styles legitimately use an element (CCTV has a timecode, a quiz has a
counter). Pass --style <rbdigital-videostudio menu number> and those rules are
skipped for it.
--profile talking-head relaxes chrome rules to warnings (progress bar allowed).

Usage: python slop_lint.py index.html [--style 39] [--profile video|talking-head] [--json]
Exit 1 if any ERROR. The lint is a lead, not a verdict: it cannot see text drawn
inside canvas/SVG paths/images, and geometry is read from CSS only.
"""
import argparse, glob, json, os, re, sys
from html.parser import HTMLParser

# style number -> rules that are part of that style's signature
EXEMPT = {
    "C_TIMECODE": {7, 8, 13, 28, 44, 45, 48, 57, 60, 61, 65, 67, 68},
    "C_COUNTER": {28, 29, 39, 40, 41, 42, 43, 44, 67},
    "C_PROGRESS": {28, 29, 48, 49, 57, 60, 67},
    "C_CORNER": {4, 5, 7, 8, 44, 45, 57, 60, 61, 65, 67, 68, 72, 74, 76},
    "C_KICKER": {4, 5, 12, 73, 74, 76},
    "C_VIBECARD": {60, 72},
    "T_TYPEWRITER": {3, 7, 11, 15, 60, 61, 65, 72},
}
BOUNCY = {10, 32, 52, 63, 86, 96}  # overshoot is part of the signature -> warn only
PARTICLE = re.compile(r"spark|particle|confetti|burst|bubble|star|dot|pop|chip|ripple|dust|flake", re.I)
TRANSFORM_KEYS = re.compile(r"\b(x|y|xPercent|yPercent|scale|scaleX|scaleY|rotation|rotationX|rotationY|rotationZ|skewX|skewY|clipPath|z)\s*:")


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.els, self.scripts, self.styles = [], [], [], []
        self._mode = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self._mode = tag
            return
        if tag in ("br", "img", "meta", "link", "input", "source", "hr"):
            return
        el = {"tag": tag, "id": a.get("id", ""), "cls": a.get("class", ""), "style": a.get("style", ""),
              "text": "", "parent": self.stack[-1] if self.stack else None}
        self.els.append(el)
        self.stack.append(el)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._mode = None
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._mode == "script":
            self.scripts.append(data)
        elif self._mode == "style":
            self.styles.append(data)
        elif self.stack and data.strip():
            self.stack[-1]["text"] += data


def parse_css(css):
    rules = []
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        decl = {}
        for k, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", body):
            decl[k.strip().lower()] = v.strip()
        for s in sel.split(","):
            last = s.strip().split()[-1] if s.strip() else ""
            rules.append((last, decl))
    return rules


def decls_for(el, rules):
    d = {}
    ids = {"#" + el["id"]} if el["id"] else set()
    classes = {"." + c for c in el["cls"].split()}
    for last, decl in rules:
        toks = set(re.findall(r"[#.][\w-]+", last))
        if toks and toks <= (ids | classes):
            d.update(decl)
        elif last == el["tag"]:
            d.update(decl)
    for k, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", el["style"]):
        d[k.strip().lower()] = v.strip()
    return d


def px(v):
    if not v:
        return None
    m = re.match(r"\s*(-?[\d.]+)\s*(px)?\s*$", v)
    return float(m.group(1)) if m else None


def ls_tracked(v, fs):
    if not v:
        return False
    m = re.match(r"\s*(-?[\d.]+)\s*(em|px)?", v)
    if not m:
        return False
    n, unit = float(m.group(1)), m.group(2) or "px"
    return n >= 0.1 if unit == "em" else (n >= 3 or (fs and n / fs >= 0.1))


def call_objects(js, method):
    """Yield (target_src, first_obj_src, rest_src) for tl.<method>( ... ) calls."""
    for m in re.finditer(r"\.\s*" + method + r"\s*\(", js):
        i, depth, start = m.end(), 1, m.end()
        while i < len(js) and depth:
            c = js[i]
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
            i += 1
        body = js[start:i - 1]
        # split top-level args
        args, depth, cur = [], 0, ""
        for c in body:
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
            if c == "," and depth == 0:
                args.append(cur)
                cur = ""
            else:
                cur += c
        args.append(cur)
        objs = [x.strip() for x in args if x.strip().startswith("{")]
        yield args[0].strip(), objs


def main():
    ap = argparse.ArgumentParser(description="anti-slop + motion lint")
    ap.add_argument("html")
    ap.add_argument("--style", type=int, help="style menu number (enables that style's exemptions)")
    ap.add_argument("--profile", choices=["video", "talking-head"], default="video")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    files = [a.html] + sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(a.html)), "compositions", "*.html")))
    doc = Doc()
    for f in files:
        with open(f, encoding="utf-8", errors="ignore") as fh:
            doc.feed(fh.read())
    rules = parse_css("\n".join(doc.styles))
    js = "\n".join(doc.scripts)
    findings = []
    th = a.profile == "talking-head"
    if th:
        a.style = None  # talking-head menu numbers differ from the video menu; chrome rules are warn-only there

    def add(code, level, msg, where=""):
        if a.style is not None and a.style in EXEMPT.get(code, set()):
            return
        if th and code.startswith("C_"):
            if code == "C_PROGRESS":
                return
            level = "WARN"
        if th and code == "T_TYPEWRITER":
            level = "WARN"
        findings.append({"rule": code, "level": level, "msg": msg, "where": where[:90]})

    def label(el):
        return (("#" + el["id"]) if el["id"] else ("." + el["cls"].split()[0]) if el["cls"] else el["tag"])

    # ---------- chrome / layout ----------
    for el in doc.els:
        txt = " ".join(el["text"].split())
        name = (el["id"] + " " + el["cls"]).lower()
        if re.search(r"progress|prog-?bar|\bprog\b", name):
            add("C_PROGRESS", "ERROR", "progress bar on screen (page chrome)", label(el))
        if re.search(r"\b(caret|typewriter|type-cursor)\b", name):
            add("T_TYPEWRITER", "ERROR", "typewriter/caret element — reveal words or lines instead", label(el))
        if not txt:
            continue
        if re.fullmatch(r"(scene|part|step|bab)?\s*0?\d{1,2}\s*/\s*0?\d{1,2}", txt, re.I):
            add("C_COUNTER", "ERROR", f"scene counter '{txt}'", label(el))
            continue
        if len(txt) <= 14 and re.search(r"\b\d{1,2}:\d{2}(:\d{2})?([.:]\d{1,3})?\b", txt):
            add("C_TIMECODE", "ERROR", f"timecode/clock '{txt}'", label(el))
        if re.search(r"\b(good morning|welcome back|selamat pagi|selamat datang kembali)\b", txt, re.I):
            add("C_VIBECARD", "WARN", f"generic UI-card greeting '{txt[:30]}'", label(el))
        d = decls_for(el, rules)
        fs = px(d.get("font-size"))
        caps = d.get("text-transform", "").lower() == "uppercase" or (txt.isupper() and len(txt) > 3)
        tracked = ls_tracked(d.get("letter-spacing"), fs)
        small = fs is not None and fs <= 36
        if d.get("position") in ("absolute", "fixed") and small and len(txt) <= 32:
            t, b, l, r = (px(d.get(k)) for k in ("top", "bottom", "left", "right"))
            near_v = (t is not None and t <= 170) or (b is not None and b <= 170)
            near_h = (l is not None and l <= 170) or (r is not None and r <= 170)
            if near_v and near_h:
                add("C_CORNER", "ERROR" if (caps and tracked) else "WARN",
                    f"small label parked in a corner: '{txt[:28]}'", label(el))
                continue
        if small and caps and tracked and len(txt) <= 40:
            add("C_KICKER", "WARN", f"small tracked-caps line (kicker/label): '{txt[:28]}'", label(el))

    # ---------- typewriter in script ----------
    if re.search(r"textContent\s*=\s*[\w.$\[\]]+\.(slice|substring|substr)\(\s*0\s*,", js) or \
       re.search(r"\.(slice|substring|substr)\(\s*0\s*,[^)]*\)\s*[;\n]?[^\n]*textContent", js):
        add("T_TYPEWRITER", "ERROR", "text typed out character by character — reveal words/lines instead", "script")

    # ---------- motion ----------
    entries_t, entries_o, opacity_only_targets, transform_targets = 0, 0, [], set()
    scale0 = []
    for method in ("from", "fromTo"):
        for target, objs in call_objects(js, method):
            if not objs:
                continue
            start = objs[0]
            has_t = bool(TRANSFORM_KEYS.search(start))
            has_o = re.search(r"\b(opacity|autoAlpha)\s*:\s*0(\.0+)?\b", start)
            if has_t:
                entries_t += 1
                transform_targets.add(target)
            elif has_o:
                opacity_only_targets.append(target)
            if re.search(r"\bscale\s*:\s*0(\.0+)?\s*[,}]", start) and not PARTICLE.search(target):
                scale0.append(target)
    # an opacity tween riding along with a move on the same target is fine
    entries_o = sum(1 for t in opacity_only_targets if t not in transform_targets)
    if scale0:
        add("M_SCALE0", "ERROR" if len(scale0) > 1 else "WARN",
            f"{len(scale0)} element(s) grow from scale 0 — crash in from oversize or move in from the edge",
            ", ".join(sorted(set(scale0)))[:90])
    total_entries = entries_t + entries_o
    if total_entries >= 4 and entries_o:
        ratio = entries_t / entries_o
        if ratio < 1.5:
            add("M_FADES", "ERROR", f"fade-heavy: {entries_t} transform entries vs {entries_o} opacity-only (aim ≥ 4:1)")
        elif ratio < 4:
            add("M_FADES", "WARN", f"{entries_t} transform entries vs {entries_o} opacity-only (aim ≥ 4:1)")

    eases = re.findall(r"ease\s*:\s*[\"'`]([^\"'`]+)[\"'`]", js)
    eases += ["E." + e for e in re.findall(r"ease\s*:\s*E\.(\w+)", js)]
    over = [e for e in eases if re.match(r"(back|elastic|bounce)", e) or e == "E.settle"]
    big = [e for e in eases if (m := re.match(r"back\.\w+\(\s*([\d.]+)", e)) and float(m.group(1)) >= 2]
    big += [e for e in eases if e.startswith(("elastic", "bounce"))]
    bouncy = a.style in BOUNCY
    if len(eases) >= 5:
        share = len(over) / len(eases)
        if share > 0.30:
            add("M_OVERSHOOT", "WARN" if bouncy else "ERROR",
                f"{share*100:.0f}% of eases overshoot (back/elastic/bounce) — keep it to the hero, ~10%")
        elif share > 0.15:
            add("M_OVERSHOOT", "WARN", f"{share*100:.0f}% of eases overshoot — keep it near 10%, hero only")
    if big and not bouncy:
        add("M_OVERSHOOT", "WARN", f"{len(big)} large overshoot ease(s) ({', '.join(sorted(set(big)))[:50]}) — use E.settle / back.out(1.15)")

    bad_exit = 0
    for target, objs in call_objects(js, "to"):
        if not objs:
            continue
        o = objs[-1]
        if re.search(r"\b(opacity|autoAlpha)\s*:\s*0(\.0+)?\b", o) and \
           re.search(r"ease\s*:\s*(\"(power\d|expo|circ|sine|quad|cubic|quart|quint)[^\"]*\.out\"|'(power\d|expo|circ|sine)[^']*\.out'|E\.(land|soft|snap|settle))", o):
            bad_exit += 1
    if bad_exit:
        add("M_EXIT", "WARN", f"{bad_exit} exit(s) use an .out ease — exits should accelerate (E.exit / power2.in)")

    if not re.search(r"\bconst\s+E\s*=\s*\{", js):
        add("M_PRESETS", "WARN", "ease presets missing — paste the E / F block from references/motion.md")

    stats = {"transform_entries": entries_t, "opacity_only_entries": entries_o,
             "eases": len(eases), "overshoot_eases": len(over), "scale0": len(scale0), "files": len(files)}
    errors = [f for f in findings if f["level"] == "ERROR"]
    if a.json:
        print(json.dumps({"findings": findings, "stats": stats, "verdict": "FAIL" if errors else "PASS"}, indent=2))
    else:
        for f in sorted(findings, key=lambda f: f["level"] != "ERROR"):
            print(f"{f['level']:5s} {f['rule']:12s} {f['msg']}" + (f"  [{f['where']}]" if f["where"] else ""))
        print(f"stats  {entries_t} move entries / {entries_o} fade-only, "
              f"{len(over)}/{len(eases)} overshoot eases, {len(scale0)} scale-from-0")
        print("VERDICT:", "FAIL" if errors else ("PASS (with warnings)" if findings else "PASS"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
