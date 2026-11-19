#!/usr/bin/env python3
"""Build a HyperFrames mascot-explainer project from video.json.

  python build.py video.json <project_dir>

Writes <project_dir>/index.html (all scenes + lip-synced mascot + GSAP timeline),
copies the mascot pack into assets/mascot/, installs fonts (fonts.py) and GSAP
(vendor/), and writes events.json (SFX cue list for audio.py).
See references/video-json.md for the full schema.
"""
import html, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import mascot_svg  # noqa: E402

FPS = 30
SHAPES = list("ABCDEFGHX")
POSES = ["base", "think", "point", "phone", "thumbs"]
THEME = {}
THEME_SKIP = {"label", "mood", "fonts", "tiles"}


def fam(spec):
    return "F " + spec.split(":")[0].replace("-", " ").title()


def load_theme(cfg):
    themes = json.load(open(os.path.join(SKILL, "templates", "themes.json")))
    name = cfg.get("theme", "editorial")
    if name not in themes:
        sys.exit(f"unknown theme '{name}'. Themes: {', '.join(themes)}")
    th = dict(themes[name])
    th.update(cfg.get("theme_override", {}))
    if cfg.get("accent"):
        th["accent"] = cfg["accent"]
    css = ";".join(f"--{k}:{v}" for k, v in th.items() if k not in THEME_SKIP)
    f = th["fonts"]
    css += (f';--disp:"{fam(f["disp"])}",sans-serif;--sans:"{fam(f["sans"])}",sans-serif;'
            f'--serif:"{fam(f["serif"])}",serif;--mono:"{fam(f["mono"])}",monospace;--serif-weight:400')
    return name, th, css

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s), quote=False)


def rich(s):
    """*text* -> <em> (serif italic accent); **text** -> <b class=red>."""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r'<b class="red">\1</b>', s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def F(n):
    return n / FPS


def r2(x):
    return round(float(x), 3)


class TL:
    """Collects GSAP timeline lines + SFX events."""

    def __init__(self):
        self.lines, self.events = [], []

    def add(self, js):
        self.lines.append(js)

    def ev(self, t, kind, **kw):
        self.events.append(dict(t=r2(t), type=kind, **kw))

    # standard motions (references/motion.md)
    kit = "move"

    def enter(self, sel, t, dy=60, dx=0, dur=11, ease="E.land"):
        k, T = self.kit, r2(t)
        if k == "blur":
            self.add(f'tl.fromTo("{sel}",{{x:{dx or -24},y:{dy * 0.3},filter:"blur(16px)"}},{{x:0,y:0,filter:"blur(0px)",duration:F({dur + 2}),ease:E.land}},{T});')
        elif k == "pop":
            self.add(f'tl.fromTo("{sel}",{{scale:.7,y:{dy * 0.4}}},{{scale:1,y:0,duration:F({dur + 2}),ease:"back.out(1.6)"}},{T});')
        elif k == "wipe":
            self.add(f'tl.fromTo("{sel}",{{clipPath:"inset(-10% 100% -10% -10%)",rotation:-1.5}},{{clipPath:"inset(-10% -10% -10% -10%)",rotation:0,duration:F({dur + 3}),ease:E.move}},{T});')
        elif k == "scan":
            self.add(f'tl.fromTo("{sel}",{{clipPath:"inset(-10% -10% 100% -10%)",x:{dx * 0.5}}},{{clipPath:"inset(-10% -10% -10% -10%)",x:0,duration:F({dur}),ease:"steps(6)"}},{T});')
        elif k == "rise":
            self.add(f'tl.fromTo("{sel}",{{y:{abs(dy) * 1.6 + 40},rotation:-5}},{{y:0,rotation:0,duration:F({dur + 3}),ease:E.land}},{T});')
        elif k == "slide":
            self.add(f'tl.fromTo("{sel}",{{x:{dx or -90}}},{{x:0,duration:F({dur}),ease:E.land}},{T});')
        elif k == "slam":
            self.add(f'tl.fromTo("{sel}",{{scale:1.5,rotation:-5}},{{scale:1,rotation:0,duration:F(8),ease:E.snap}},{T});')
        elif k == "soft":
            self.add(f'tl.fromTo("{sel}",{{y:{dy * 0.5}}},{{y:0,duration:F({dur + 8}),ease:E.soft}},{T});')
        else:
            self.add(f'tl.fromTo("{sel}",{{x:{dx},y:{dy}}},{{x:0,y:0,duration:F({dur}),ease:{ease}}},{T});')
        self.add(f'tl.fromTo("{sel}",{{opacity:0}},{{opacity:1,duration:F({12 if k == "soft" else 6}),ease:E.land}},{T});')

    def crash(self, sel, t, scale=1.8, dur=9, ease="E.snap"):
        if self.kit in ("soft", "blur", "wipe", "scan"):
            return self.enter(sel, t, dy=40)
        if self.kit == "pop":
            self.add(f'tl.fromTo("{sel}",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:F(12),ease:"back.out(2)"}},{r2(t)});')
            return
        self.add(f'tl.fromTo("{sel}",{{scale:{scale},opacity:0}},{{scale:1,opacity:1,duration:F({dur}),ease:{ease}}},{r2(t)});')

    def exit(self, sel, t, dy=-40, dur=7):
        self.add(f'tl.to("{sel}",{{y:{dy},opacity:0,duration:F({dur}),ease:E.exit}},{r2(t)});')

    def set(self, sel, props, t):
        self.add(f'tl.set("{sel}",{props},{r2(t)});')


# ---------------------------------------------------------------- visuals
def v_timeline(sid, v, t0, dur, tl):
    rows = ""
    pal = [["#8E9BF0", "#E2A27F"], ["#92D69A", "#B983E6", "#92D69A"], ["#EC7F96", "#86C9E3", "#92E3EE"]]
    for r in range(3):
        bars, x = "", 6 + r * 3
        for g, cols in enumerate(pal):
            w = 9 + (r + g) % 3 * 3
            for c in cols:
                bars += f'<i style="left:{x}%;width:{w}%;background:{c}"></i>'
                x += w
            x += 6
        rows += f'<div class="trk" id="{sid}-trk{r}">{bars}</div>'
    tl.add(f'tl.fromTo("#{sid}-ph",{{xPercent:28}},{{xPercent:62,duration:{r2(max(1, dur - 0.5))},ease:"none"}},{r2(t0 + 0.3)});')
    for r in range(3):
        tl.add(f'tl.fromTo("#{sid}-trk{r}",{{x:{(-1) ** r * 30}}},{{x:0,duration:F(16),ease:E.land}},{r2(t0 + 0.3 + r * 0.08)});')
    return (f'<div class="win"><div class="wbar"><span class="dots"><i></i><i></i><i></i></span><b>{esc(v.get("title", "Editor"))}</b>'
            f'<span class="wlab">{esc(v.get("label", "timeline"))}</span></div><div class="tlbody">{rows}<div class="phw" id="{sid}-ph"><div class="ph"></div></div></div></div>')


def v_numcards(sid, v, t0, dur, tl):
    cols = v.get("cols", 3)
    out = ""
    for i, it in enumerate(v["items"]):
        n, txt = it[0], it[1]
        out += f'<div class="ncard" id="{sid}-n{i}"><b>{esc(n)}</b><span>{esc(txt)}</span></div>'
        tl.enter(f"#{sid}-n{i}", t0 + 0.25 + i * F3(v), dy=50)
        tl.ev(t0 + 0.25 + i * F3(v), "pop", g=0.25)
    return f'<div class="ngrid" style="grid-template-columns:repeat({cols},1fr)">{out}</div>'


def F3(v):
    return v.get("stagger", 0.12)


def v_tiles(sid, v, t0, dur, tl):
    cols = v.get("cols", 4)
    out = ""
    for i, it in enumerate(v["items"]):
        pal = THEME["tiles"][i % len(THEME["tiles"])]
        txt, bg, fg = (it + pal)[:3] if isinstance(it, list) else (it, pal[0], pal[1])
        out += f'<div class="tile" id="{sid}-t{i}" style="background:{bg};color:{fg}">{esc(txt)}</div>'
        tl.enter(f"#{sid}-t{i}", t0 + 0.3 + (i % cols) * 0.05 + (i // cols) * 0.1, dy=40, dur=10)
    tl.ev(t0 + 0.3, "pop", g=0.3)
    for (ht, idx) in v.get("highlight", []):
        tl.add(f'tl.fromTo("#{sid}-t{idx}",{{scale:1}},{{scale:1.08,duration:F(7),ease:E.snap}},{r2(t0 + ht)});')
        tl.set(f"#{sid}-t{idx}", '{className:"tile on"}', t0 + ht)
        tl.ev(t0 + ht, "click")
    return f'<div class="tgrid" style="grid-template-columns:repeat({cols},1fr)">{out}</div>'


def v_phone(sid, v, t0, dur, tl):
    chips = "".join(f'<div class="chip" id="{sid}-c{i}">{esc(c)}</div>' for i, c in enumerate(v.get("chips", [])))
    big_at = v.get("big_at", 1.2)
    for i in range(len(v.get("chips", []))):
        tl.enter(f"#{sid}-c{i}", t0 + 0.6 + i * 0.12, dx=-40, dy=0, dur=9)
    if v.get("big"):
        tl.crash(f"#{sid}-big", t0 + big_at, scale=2.4)
        tl.ev(t0 + big_at, "slam", g=0.35)
    tl.add(f'tl.fromTo("#{sid}-face",{{scale:1.0}},{{scale:1.12,duration:{r2(dur)},ease:"none"}},{r2(t0)});')
    face = '<div class="pface" id="%s-face">%s</div>' % (sid, MINI_FACE)
    return (f'<div class="phwrap"><div class="pcard"><span class="rec">● REC</span>{face}'
            f'<div class="pbig" id="{sid}-big">{esc(v.get("big", ""))}</div>'
            f'<div class="pcap">{esc(v.get("caption", ""))}</div></div><div class="chips">{chips}</div></div>')


MINI_FACE = ('<svg viewBox="0 0 200 200"><circle cx="100" cy="92" r="52" fill="#E8B48A" stroke="#1b1b1b" stroke-width="5"/>'
             '<path d="M50 80 Q52 34 100 32 Q150 34 150 82 Q130 56 100 60 Q72 56 50 80Z" fill="#23201F"/>'
             '<circle cx="82" cy="94" r="6" fill="#1b1b1b"/><circle cx="118" cy="94" r="6" fill="#1b1b1b"/>'
             '<path d="M82 120 Q100 132 118 120" fill="none" stroke="#1b1b1b" stroke-width="5" stroke-linecap="round"/>'
             '<path d="M30 200 Q40 150 100 146 Q160 150 170 200Z" fill="#26304F" stroke="#1b1b1b" stroke-width="5"/></svg>')


def v_list(sid, v, t0, dur, tl):
    items = v["items"]
    step = v.get("step", max(0.4, (dur - 1.0) / max(1, len(items))))
    rows = "".join(f'<div class="lrow" id="{sid}-r{i}"><b>{i + 1}</b><span>{esc(x)}</span></div>' for i, x in enumerate(items))
    side = "".join(f'<div class="{"s1" if i == 0 else "s2"}" id="{sid}-s{i}">{esc(s)}</div>' for i, s in enumerate(v.get("side", [])))
    for i in range(len(v.get("side", []))):
        tl.crash(f"#{sid}-s{i}", t0 + 0.4 + i * 0.2, scale=1.8)
    for i in range(len(items)):
        tt = t0 + 0.5 + i * step
        tl.set(f"#{sid}-r{i}", '{className:"lrow on"}', tt)
        if i > 0:
            tl.set(f"#{sid}-r{i - 1}", '{className:"lrow"}', tt)
        tl.add(f'tl.fromTo("#{sid}-r{i}",{{x:-14}},{{x:0,duration:F(8),ease:E.land}},{r2(tt)});')
        tl.ev(tt, "click", g=0.2)
    return f'<div class="lcard"><div class="lrows">{rows}</div><div class="lside">{side}</div></div>'


def v_landscape(sid, v, t0, dur, tl):
    layers = [
        ("#E9A06F", "M0 300 L120 170 L230 260 L360 130 L480 250 L600 160 L760 290 L800 300 Z"),
        ("#C9784F", "M0 300 L90 220 L200 290 L320 200 L450 300 Z M380 300 L520 210 L640 280 L800 230 L800 300 Z"),
        ("#8E4F33", "M0 300 L0 270 Q200 230 400 268 Q600 300 800 262 L800 300 Z"),
    ]
    svg = ""
    for i, (c, d) in enumerate(layers):
        svg += f'<g id="{sid}-l{i}"><path d="{d}" fill="{c}" transform="translate(0 40)"/></g>'
        tl.add(f'tl.fromTo("#{sid}-l{i}",{{x:{-20 * (i + 1)}}},{{x:{20 * (i + 1)},duration:{r2(dur)},ease:"none"}},{r2(t0)});')
    tl.add(f'tl.fromTo("#{sid}-sun",{{y:30}},{{y:-10,duration:{r2(dur)},ease:"none"}},{r2(t0)});')
    if v.get("tree", True):
        svg += f'<path id="{sid}-tree" d="M560 300 L600 200 L640 300Z" fill="#3A2416" transform="translate(0 40)"/>'
        tl.crash(f"#{sid}-tree", t0 + dur * 0.45, scale=1.6)
    return (f'<div class="lscape"><svg viewBox="0 0 800 340" preserveAspectRatio="xMidYMid slice">'
            f'<rect width="800" height="340" fill="#F6D7B0"/><circle id="{sid}-sun" cx="520" cy="110" r="44" fill="#FFF3C4"/>{svg}</svg></div>')


def v_filmstrip(sid, v, t0, dur, tl):
    cols = ["#F2D64B", "#6E86F2", "#8FD39B", "#B57BEB", "#F08A3B", "#EC6F8F", "#5BC8D6"]
    frames = v.get("frames", [f"BABAK {i}" for i in range(1, 7)])
    fr = "".join(f'<div class="fr" style="background:{cols[i % len(cols)]}"><b>{esc(f)}</b><i></i></div>' for i, f in enumerate(frames))
    tl.add(f'tl.fromTo("#{sid}-strip",{{x:0}},{{x:{-130 * max(0, len(frames) - 2)},duration:{r2(max(1, dur - 0.3))},ease:"power1.inOut"}},{r2(t0 + 0.2)});')
    return f'<div class="film"><div class="holes"></div><div class="strip" id="{sid}-strip">{fr}</div><div class="holes"></div></div>'


def typed(sid, text, t0, tl, cps=22, cls="ch"):
    """Per-character spans revealed in order (UI typing mockup, not a headline)."""
    out = ""
    for i, ch in enumerate(text):
        out += f'<span class="{cls}" id="{sid}-{i}">{esc(ch) if ch != " " else "&nbsp;"}</span>'
        tl.set(f"#{sid}-{i}", "{opacity:1}", t0 + i / cps)
    tl.ev(t0, "typing", d=r2(len(text) / cps))
    return out, t0 + len(text) / cps


def v_prompt(sid, v, t0, dur, tl):
    t = t0 + 0.5
    lines = ""
    for li, line in enumerate(v["lines"]):
        spans, t = typed(f"{sid}-p{li}", line, t, tl, cps=v.get("cps", 26))
        lines += f"<div>{spans}</div>"
        t += 0.15
    copy_at = t0 + v.get("copy_at", min(dur - 0.6, t - t0 + 0.3))
    tl.set(f"#{sid}-copy", '{className:"copy ok"}', copy_at)
    tl.add(f'tl.fromTo("#{sid}-copy",{{scale:1.25}},{{scale:1,duration:F(8),ease:E.snap}},{r2(copy_at)});')
    tl.ev(copy_at, "click")
    return (f'<div class="win"><div class="wbar"><span class="dots"><i></i><i></i><i></i></span><b>{esc(v.get("file", "prompt.txt"))}</b>'
            f'<span class="wlab">{esc(v.get("label", "copy · paste"))}</span></div>'
            f'<div class="pbody">{lines}<div class="copy" id="{sid}-copy">Copy</div></div></div>')


def v_window(sid, v, t0, dur, tl):
    rows = ""
    for i, r in enumerate(v.get("rows", [])):
        a, b = (r + [""])[:2] if isinstance(r, list) else (r, "")
        rows += f'<div class="wrow" id="{sid}-w{i}"><span>{esc(a)}</span><b>{esc(b)}</b></div>'
        tl.enter(f"#{sid}-w{i}", t0 + 0.45 + i * 0.12, dx=-30, dy=0, dur=9)
    return (f'<div class="win"><div class="wbar"><span class="dots"><i></i><i></i><i></i></span><b>{esc(v.get("title", "App"))}</b>'
            f'<span class="wlab">{esc(v.get("label", ""))}</span></div><div class="wbody">{rows}</div></div>')


def v_checklist(sid, v, t0, dur, tl):
    rows = ""
    for i, it in enumerate(v["items"]):
        at, txt = (it[0], it[1]) if isinstance(it, list) else (0.5 + i * 0.8, it)
        rows += f'<div class="ck" id="{sid}-k{i}"><i id="{sid}-ki{i}"></i><span>{esc(txt)}</span></div>'
        tl.enter(f"#{sid}-k{i}", t0 + 0.3 + i * 0.1, dx=-30, dy=0, dur=9)
        tl.set(f"#{sid}-ki{i}", '{className:"on"}', t0 + at)
        tl.add(f'tl.fromTo("#{sid}-ki{i}",{{scale:1.6}},{{scale:1,duration:F(8),ease:E.snap}},{r2(t0 + at)});')
        tl.ev(t0 + at, "ding")
    return f'<div class="cklist">{rows}</div>'


def v_price(sid, v, t0, dur, tl):
    new_at = v.get("new_at")
    if v.get("new") and new_at is not None:
        tl.add(f'tl.fromTo("#{sid}-strike",{{scaleX:0}},{{scaleX:1,duration:F(7),ease:E.snap}},{r2(t0 + new_at)});')
        tl.crash(f"#{sid}-new", t0 + new_at + 0.15, scale=2.2)
        tl.add(f'tl.to("#{sid}-old",{{scale:.55,y:-50,duration:F(9),ease:E.move}},{r2(t0 + new_at)});')
        tl.ev(t0 + new_at + 0.15, "slam")
    newh = f'<div class="pnew" id="{sid}-new">{esc(v.get("new", ""))}</div>' if v.get("new") else ""
    return (f'<div class="price"><span class="ptag">{esc(v.get("tag", "LAUNCHING"))}</span>'
            f'<div class="pold" id="{sid}-old">{esc(v.get("old", ""))}<i id="{sid}-strike"></i></div>{newh}</div>')


def v_comment(sid, v, t0, dur, tl, mascot_thumb):
    at = t0 + v.get("at", 0.6)
    spans, tend = typed(f"{sid}-kw", v.get("keyword", "VIDEO"), at, tl, cps=8, cls="kw")
    tl.crash(f"#{sid}-heart", tend + 0.3, scale=2.4)
    tl.ev(tend + 0.3, "pop")
    tl.enter(f"#{sid}-dm", tend + 0.7, dy=30)
    tl.ev(tend + 0.7, "ding")
    return (f'<div class="cbox"><div class="av">{mascot_thumb}</div><div class="cmain"><small>{esc(v.get("handle", "kau · baru je"))}</small>'
            f'<div class="ctext">{spans}<span class="ibeam"></span></div></div><div class="heart" id="{sid}-heart">♥</div></div>'
            f'<div class="dm" id="{sid}-dm">{esc(v.get("dm", "→ terus ke DM"))}</div>')


def v_text(sid, v, t0, dur, tl):
    words = v.get("big", [])
    out = ""
    for i, w in enumerate(words):
        red = w.startswith("*") and w.endswith("*")
        out += f'<span class="{"red" if red else ""}" id="{sid}-b{i}">{esc(w.strip("*"))}</span> '
        tl.crash(f"#{sid}-b{i}", t0 + 0.2 + i * 0.25, scale=2.0)
        tl.ev(t0 + 0.2 + i * 0.25, "slam", g=0.3)
    return f'<div class="bigtext">{out}</div>'


VISUALS = dict(timeline=v_timeline, numcards=v_numcards, tiles=v_tiles, phone=v_phone, list=v_list,
               landscape=v_landscape, filmstrip=v_filmstrip, prompt=v_prompt, window=v_window,
               checklist=v_checklist, price=v_price, text=v_text)


# ---------------------------------------------------------------- theme kit: decorations + transitions
def deco_html(names, sid, t0, dur, tl):
    out = []
    D = r2(dur)
    for n in names:
        if n == "brackets":
            out.append(f'<div class="dk dk-brackets" id="{sid}-dk-br"><i></i><i></i><i></i><i></i></div>')
            tl.add(f'tl.fromTo("#{sid}-dk-br",{{scale:1.06,opacity:0}},{{scale:1,opacity:1,duration:F(10),ease:E.land}},{r2(t0)});')
        elif n == "scanlines":
            out.append(f'<div class="dk dk-scan" id="{sid}-dk-sc"></div>')
            tl.add(f'tl.fromTo("#{sid}-dk-sc",{{y:0}},{{y:40,duration:{D},ease:"none"}},{r2(t0)});')
        elif n == "blobs":
            for i, (x, y, r) in enumerate([(8, 18, 220), (78, 8, 160), (62, 58, 260)]):
                out.append(f'<div class="dk dk-blob b{i}" id="{sid}-dk-b{i}" style="left:{x}%;top:{y}%;width:{r}px;height:{r}px"></div>')
                tl.add(f'tl.fromTo("#{sid}-dk-b{i}",{{y:0,scale:1}},{{y:{-30 + i * 20},scale:1.08,duration:{D},ease:"sine.inOut"}},{r2(t0)});')
        elif n == "sparkles":
            for i, (x, y) in enumerate([(12, 30), (86, 22), (70, 48), (20, 52)]):
                out.append(f'<div class="dk dk-spark" id="{sid}-dk-s{i}" style="left:{x}%;top:{y}%">✦</div>')
                tl.add(f'tl.fromTo("#{sid}-dk-s{i}",{{rotation:0,scale:.6,opacity:0}},{{rotation:90,scale:1,opacity:1,duration:{D},ease:"sine.inOut"}},{r2(t0 + i * 0.15)});')
        elif n == "doodles":
            out.append(f'<svg class="dk dk-arrow" id="{sid}-dk-ar" viewBox="0 0 200 120"><path d="M10 20 C 70 10, 120 40, 150 90 M150 90 l-28 -6 M150 90 l4 -28" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
            tl.add(f'tl.to("#{sid}-dk-ar path",{{strokeDashoffset:0,duration:F(18),ease:E.move}},{r2(t0 + 0.6)});')
            out.append(f'<div class="dk dk-star" id="{sid}-dk-st">★</div>')
            tl.add(f'tl.fromTo("#{sid}-dk-st",{{rotation:-20,opacity:0}},{{rotation:10,opacity:1,duration:{D},ease:"sine.inOut"}},{r2(t0)});')
        elif n == "code":
            lines = ["const tip = await claude.ask(topic)", "if (penat) tidur.awal()", "render({ fps: 30 })", "// rbdigital-mascotexplainer"]
            body = "".join(f"<div>{esc(l)}</div>" for l in lines)
            out.append(f'<div class="dk dk-code" id="{sid}-dk-cd">{body}</div>')
            tl.add(f'tl.fromTo("#{sid}-dk-cd",{{y:30}},{{y:-30,duration:{D},ease:"none"}},{r2(t0)});')
        elif n == "cursor":
            out.append(f'<div class="dk dk-cursor" id="{sid}-dk-cu"></div>')
            k = 0.0
            while k < dur:
                tl.set(f"#{sid}-dk-cu", "{opacity:0}", t0 + k + 0.4)
                tl.set(f"#{sid}-dk-cu", "{opacity:1}", t0 + k + 0.8)
                k += 0.8
        elif n == "sun":
            out.append(f'<div class="dk dk-sun" id="{sid}-dk-sun"><i></i><i></i><i></i><i></i></div>')
            tl.add(f'tl.fromTo("#{sid}-dk-sun",{{y:60,rotation:0}},{{y:-20,rotation:8,duration:{D},ease:"none"}},{r2(t0)});')
        elif n == "dots":
            out.append(f'<div class="dk dk-dots" id="{sid}-dk-dt"></div><div class="dk dk-bar" id="{sid}-dk-bar"></div>')
            tl.add(f'tl.fromTo("#{sid}-dk-dt",{{x:0}},{{x:-40,duration:{D},ease:"none"}},{r2(t0)});')
            tl.add(f'tl.fromTo("#{sid}-dk-bar",{{scaleY:0}},{{scaleY:1,duration:F(12),ease:E.move}},{r2(t0 + 0.1)});')
        elif n == "burst":
            pts = " ".join(f"{100 + (95 if i % 2 == 0 else 62) * __import__('math').cos(i * 3.14159 / 10):.0f},{100 + (95 if i % 2 == 0 else 62) * __import__('math').sin(i * 3.14159 / 10):.0f}" for i in range(20))
            out.append(f'<svg class="dk dk-burst" id="{sid}-dk-bu" viewBox="0 0 200 200"><polygon points="{pts}"/></svg>')
            tl.add(f'tl.fromTo("#{sid}-dk-bu",{{rotation:-20,scale:1.3}},{{rotation:15,scale:1,duration:{D},ease:"none"}},{r2(t0)});')
        elif n == "speed":
            out.append(f'<div class="dk dk-speed" id="{sid}-dk-sp"></div>')
            tl.add(f'tl.fromTo("#{sid}-dk-sp",{{x:0}},{{x:-120,duration:{D},ease:"none"}},{r2(t0)});')
        elif n == "leaves":
            for i, (x, y, rot) in enumerate([(84, 6, 20), (4, 60, -30)]):
                out.append(f'<svg class="dk dk-leaf" id="{sid}-dk-l{i}" style="left:{x}%;top:{y}%" viewBox="0 0 100 160"><path d="M50 150 C10 110 5 50 50 8 C95 50 90 110 50 150 Z M50 150 L50 20" /></svg>')
                tl.add(f'tl.fromTo("#{sid}-dk-l{i}",{{rotation:{rot}}},{{rotation:{rot + 10},duration:{D},ease:"sine.inOut"}},{r2(t0)});')
        elif n == "caution":
            out.append(f'<div class="dk dk-caution" id="{sid}-dk-ca"></div>')
            tl.add(f'tl.fromTo("#{sid}-dk-ca",{{x:0}},{{x:-112,duration:{D},ease:"none"}},{r2(t0)});')
    return f'<div class="deco">{"".join(out)}</div>' if out else ""


def transition(kind, t, tl):
    """Overlay transition across the cut at time t (#tx layer, above everything)."""
    T = r2(t)
    if kind == "flash":
        tl.add(f'tl.fromTo("#tx-flash",{{opacity:1}},{{opacity:0,duration:F(5),ease:E.exit,immediateRender:false}},{T});')
    elif kind == "glitch":
        for i in range(3):
            tl.add(f'tl.set("#tx-g{i}",{{opacity:1,x:{[-60, 40, -20][i]}}},{r2(t - F(2))});')
            tl.add(f'tl.set("#tx-g{i}",{{x:{[30, -50, 60][i]}}},{r2(t)});')
            tl.add(f'tl.set("#tx-g{i}",{{opacity:0}},{r2(t + F(3))});')
    elif kind == "circle":
        tl.add(f'tl.fromTo("#tx-panel",{{clipPath:"circle(0% at 85% 85%)"}},{{clipPath:"circle(150% at 85% 85%)",duration:F(8),ease:E.throw}},{r2(t - F(8))});')
        tl.add(f'tl.fromTo("#tx-panel",{{clipPath:"circle(150% at 15% 15%)"}},{{clipPath:"circle(0% at 15% 15%)",duration:F(9),ease:E.land,immediateRender:false}},{T});')
    elif kind == "push":
        tl.add(f'tl.fromTo("#tx-panel",{{xPercent:-100}},{{xPercent:0,duration:F(7),ease:E.throw}},{r2(t - F(7))});')
        tl.add(f'tl.fromTo("#tx-panel",{{xPercent:0}},{{xPercent:100,duration:F(8),ease:E.land,immediateRender:false}},{T});')
    elif kind == "page":
        tl.add(f'tl.fromTo("#tx-page",{{xPercent:110,rotation:6}},{{xPercent:0,rotation:0,duration:F(8),ease:E.throw}},{r2(t - F(8))});')
        tl.add(f'tl.fromTo("#tx-page",{{xPercent:0,rotation:0}},{{xPercent:-110,rotation:-6,duration:F(9),ease:E.land,immediateRender:false}},{T});')
    elif kind == "scan":
        tl.add(f'tl.fromTo("#tx-panel",{{yPercent:-100}},{{yPercent:0,duration:F(6),ease:"steps(5)"}},{r2(t - F(6))});')
        tl.add(f'tl.fromTo("#tx-panel",{{yPercent:0}},{{yPercent:100,duration:F(6),ease:"steps(5)",immediateRender:false}},{T});')
    elif kind == "blinds":
        tl.add(f'tl.fromTo("#tx-blinds i",{{scaleY:0}},{{scaleY:1,duration:F(6),ease:E.throw,stagger:F(1)}},{r2(t - F(9))});')
        tl.add(f'tl.fromTo("#tx-blinds i",{{scaleY:1}},{{scaleY:0,duration:F(7),ease:E.land,stagger:F(1),immediateRender:false}},{T});')
    elif kind == "burst":
        tl.add(f'tl.fromTo("#tx-burst",{{scale:.2,rotation:0,opacity:1}},{{scale:9,rotation:40,opacity:1,duration:F(8),ease:E.throw,immediateRender:false}},{r2(t - F(8))});')
        tl.add(f'tl.fromTo("#tx-burst",{{opacity:1}},{{opacity:0,duration:F(5),ease:E.exit,immediateRender:false}},{T});')
    elif kind == "veil":
        tl.add(f'tl.fromTo("#tx-veil",{{opacity:0}},{{opacity:.9,duration:F(8),ease:E.move}},{r2(t - F(8))});')
        tl.add(f'tl.fromTo("#tx-veil",{{opacity:.9}},{{opacity:0,duration:F(12),ease:E.soft,immediateRender:false}},{T});')
    return kind != "cut"


TX_HTML = ('<div id="tx"><div id="tx-flash"></div><div id="tx-panel"></div><div id="tx-page"></div><div id="tx-veil"></div>'
           '<div id="tx-blinds">' + "<i></i>" * 8 + '</div><svg id="tx-burst" viewBox="0 0 200 200"><polygon points="100,0 120,70 200,60 135,110 170,190 100,140 30,190 65,110 0,60 80,70"/></svg>'
           '<div id="tx-g0" class="txg"></div><div id="tx-g1" class="txg"></div><div id="tx-g2" class="txg"></div></div>')


# ---------------------------------------------------------------- mascot
def load_pack(spec, proj):
    """Returns (mode, info). mode 'svg' (built-in) or 'png' (pack folder with mascot.json)."""
    if not spec or spec == "generic":
        return "svg", {}
    path = spec if os.path.isabs(spec) else os.path.join(os.getcwd(), spec)
    if not os.path.isdir(path):
        alt = os.path.join(SKILL, "assets", "mascot", spec)
        path = alt if os.path.isdir(alt) else path
    mj = os.path.join(path, "mascot.json")
    if not os.path.isfile(mj):
        sys.exit(f"mascot pack not found: {mj}")
    info = json.load(open(mj))
    dst = os.path.join(proj, "assets", "mascot")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(path, dst)
    from PIL import Image
    import numpy as np
    info["_size"] = {p: Image.open(os.path.join(path, f)).size for p, f in info["poses"].items()}
    # sink: how much of the pose (fraction of its height) goes below the frame edge, so the
    # mascot looks cut off by the frame instead of floating. Auto: a figure whose bottom row is
    # already cut flat (waist cut by the image edge) needs little; a rounded/full bottom needs more.
    if "sink" not in info:
        fr = []
        for f in info["poses"].values():
            al = np.asarray(Image.open(os.path.join(path, f)).convert("RGBA"))[..., 3] > 128
            ys = np.where(al.any(1))[0]
            if not len(ys):
                continue
            rows = al[ys[0]:ys[-1] + 1].sum(1)
            fr.append(rows[-3:].mean() / max(1, rows.max()))
        flat = (sum(fr) / len(fr)) if fr else 1
        info["sink"] = 0.04 if flat > 0.55 else 0.16
    return "png", info


BOX = {"16x9": (780, 880), "9x16": (640, 720)}  # #mascot box in templates/style.css


def mascot_html(mode, info, colors, fmt="16x9"):
    poses = []
    if mode == "svg":
        for p in POSES:
            svg = mascot_svg.pose_svg(p, colors)
            mouths = "".join(f'<g class="mth" data-m="{s}" style="opacity:{1 if s == "X" else 0}">{mascot_svg.mouth_svg(s)}</g>' for s in SHAPES)
            svg = svg.replace('<g id="mouth-slot" transform="translate(300 338)"></g>',
                              f'<g transform="translate(300 338)">{mouths}</g>')
            poses.append(f'<div class="pose" data-pose="{p}" style="opacity:0">{svg}</div>')
        return "".join(poses), POSES
    names = list(info["poses"].keys())
    for p in names:
        W, H = info["_size"][p]
        mouths = info["mouths"].get(p, info["mouths"]) if isinstance(next(iter(info["mouths"].values())), dict) else info["mouths"]
        cx, cy, mw = info["anchor"][p]
        imgs = ""
        skin = info.get("patch", {}).get(p)
        if skin:  # paint over the mouth drawn in the pose image
            pw, ph = mw * 1.25, mw * 0.8
            imgs += (f'<i class="mpatch" style="left:{100 * (cx - pw / 2) / W:.3f}%;top:{100 * (cy - ph / 2) / H:.3f}%;'
                     f'width:{100 * pw / W:.3f}%;height:{100 * ph / H:.3f}%;'
                     f'background:radial-gradient(ellipse at center,{skin} 58%,transparent 72%)"></i>')
        for s in SHAPES:
            if s not in mouths:
                continue
            imgs += (f'<img class="mth" data-m="{s}" src="assets/mascot/{mouths[s]}" '
                     f'style="left:{100 * (cx - mw / 2) / W:.3f}%;top:{100 * cy / H:.3f}%;width:{100 * mw / W:.3f}%;'
                     f'transform:translateY(-50%);opacity:{1 if s == "X" else 0}">')
        # the pose box gets exactly the image's aspect (so mouth % anchors match the drawing),
        # bottom-aligned to the frame, then pushed down by "sink" so it is cut off by the edge
        bw, bh = BOX.get(fmt, BOX["16x9"])
        k = min(bw / W, bh / H)
        pw_px, ph_px = W * k, H * k
        sink = float(info.get("sink", 0.04))
        poses.append(f'<div class="pose png" data-pose="{p}" style="opacity:0;width:{pw_px:.1f}px;height:{ph_px:.1f}px;'
                     f'transform:translateY({100 * sink:.1f}%)">'
                     f'<img class="pbase" src="assets/mascot/{info["poses"][p]}">{imgs}</div>')
    return "".join(poses), names


def mascot_thumb(mode, info):
    if mode == "svg":
        return mascot_svg.pose_svg("base").replace('<g id="mouth-slot" transform="translate(300 338)"></g>',
                                                   f'<g transform="translate(300 338)">{mascot_svg.mouth_svg("X")}</g>')
    p = info.get("avatar_pose") or next(iter(info["poses"]))
    W, H = info["_size"][p]
    cx, cy, mw = info["anchor"][p]
    box = 84
    sc = box / (mw * 2.4)
    left, top = box / 2 - cx * sc, box / 2 - (cy - mw * 0.45) * sc
    return (f'<img src="assets/mascot/{info["poses"][p]}" style="position:absolute;max-width:none;'
            f'width:{W * sc:.1f}px;height:{H * sc:.1f}px;left:{left:.1f}px;top:{top:.1f}px;margin:0">')


# ---------------------------------------------------------------- main build
def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cfg = json.load(open(sys.argv[1]))
    proj = sys.argv[2]
    os.makedirs(os.path.join(proj, "assets"), exist_ok=True)
    base = os.path.dirname(os.path.abspath(sys.argv[1]))

    fmt = cfg.get("format", "16x9")
    W, H = (1920, 1080) if fmt == "16x9" else (1080, 1920)
    scenes = cfg["scenes"]

    # timing
    timing = None
    if cfg.get("timing"):
        timing = json.load(open(os.path.join(base, cfg["timing"])))
        if len(timing["scenes"]) != len(scenes):
            print(f"WARN timing has {len(timing['scenes'])} scenes, video.json has {len(scenes)}: extra scenes use 'dur'")
    t = 0.0
    for i, s in enumerate(scenes):
        if timing and i < len(timing["scenes"]):
            s["_t0"], s["_t1"] = timing["scenes"][i]["start"], timing["scenes"][i]["end"]
        else:
            s["_t0"], s["_t1"] = t, t + float(s.get("dur", 4))
        t = s["_t1"]
    total = r2(scenes[-1]["_t1"] + float(cfg.get("outro", 0.8)))

    global THEME
    theme_name, THEME, theme_css = load_theme(cfg)
    mode, pack = load_pack(cfg.get("mascot", "generic"), proj)
    m_html, pose_names = mascot_html(mode, pack, cfg.get("mascot_colors"), fmt)
    if mode == "png":
        print(f"mascot sink {pack.get('sink')} (set \"sink\" in mascot.json to override: 0 = bottom edge of the image sits on the frame edge)")
    thumb = mascot_thumb(mode, pack)

    tl = TL()
    kit = THEME.get("kit", {})
    tl.kit = cfg.get("enter", kit.get("enter", "move"))
    used_tr = set()
    body = []
    pose_track = []
    for i, s in enumerate(scenes):
        sid = f"s{i + 1}"
        t0, t1 = s["_t0"], s["_t1"]
        dur = t1 - t0
        bg = s.get("bg", "cream")
        parts = []
        # topbar
        parts.append(f'<div class="top"><span>{esc(s.get("top", ""))}</span><span>{esc(cfg.get("brand", ""))}</span></div>')
        # leads (one or several over time)
        leads = s.get("lead", [])
        if isinstance(leads, str):
            leads = [[0, leads]]
        for li, (lt, txt) in enumerate(leads):
            parts.append(f'<div class="lead" id="{sid}-lead{li}">{rich(txt)}</div>')
            tl.enter(f"#{sid}-lead{li}", t0 + lt, dy=36)
            if li > 0:
                tl.exit(f"#{sid}-lead{li - 1}", t0 + lt - F(8))
        # title
        has_title = bool(s.get("title"))
        if has_title:
            words = ""
            for wi, w in enumerate(s["title"]):
                red = w.startswith("*") and w.endswith("*")
                words += f'<span class="{"red" if red else ""}" id="{sid}-tw{wi}">{esc(w.strip("*"))}</span> '
                if wi == 0:
                    tl.enter(f"#{sid}-tw{wi}", t0 + 0.1, dx=-80, dy=0, dur=10)
                else:
                    tl.crash(f"#{sid}-tw{wi}", t0 + 0.1 + wi * 0.12, scale=1.7)
            badge = f'<span class="badge" id="{sid}-bd">{esc(s["badge"])}</span>' if s.get("badge") else ""
            if badge:
                tl.add(f'tl.fromTo("#{sid}-bd",{{y:50,rotation:-12,opacity:0}},{{y:0,rotation:0,opacity:1,duration:F(10),ease:E.settle}},{r2(t0 + 0.35)});')
            parts.append(f'<div class="title">{words}{badge}</div>')
            tl.ev(t0 + 0.2, "slam", g=0.25)
        # visual
        v = s.get("visual")
        if v:
            fn = VISUALS.get(v["type"])
            vd = float(v.get("delay", 0))  # visual appears later in the scene
            if v["type"] == "comment":
                inner = v_comment(sid, v, t0, dur, tl, thumb)
            elif fn:
                inner = fn(sid, v, t0 + vd, dur - vd, tl)
            else:
                sys.exit(f"unknown visual type {v['type']}")
            parts.append(f'<div class="vis {"low" if not has_title else ""} vt-{v["type"]}" id="{sid}-vis">{inner}</div>')
            if v["type"] in ("numcards", "checklist", "text"):
                tl.set(f"#{sid}-vis", "{opacity:1}", t0)
            else:
                tl.enter(f"#{sid}-vis", t0 + vd + 0.25, dy=80, dur=13, ease="E.soft")
                tl.ev(t0 + vd + 0.25, "pop", g=0.2)
            tl.add(f'tl.fromTo("#{sid}-vis",{{scale:1}},{{scale:1.025,duration:{r2(dur)},ease:"none"}},{r2(t0)});')
        # pill
        if s.get("pill"):
            p = s["pill"]
            at = t0 + p.get("at", 0.9)
            parts.append(f'<div class="pill" id="{sid}-pill"><b>{esc(p.get("num", ""))}</b>{rich(p.get("text", ""))}</div>')
            tl.enter(f"#{sid}-pill", at, dx=-60, dy=0, dur=10)
            tl.ev(at, "pop", g=0.3)
        # progress
        if s.get("progress"):
            p = s["progress"]
            at = t0 + p.get("at", 1.0)
            parts.append(f'<div class="prog"><small>{esc(p.get("text", ""))}</small><div class="bar"><i id="{sid}-bar"></i></div></div>')
            tl.add(f'tl.fromTo("#{sid}-bar",{{scaleX:0}},{{scaleX:1,duration:{r2(max(0.6, dur - (at - t0) - 0.3))},ease:E.move}},{r2(at)});')
        # sticker (torn paper)
        if s.get("sticker"):
            p = s["sticker"]
            at = t0 + p.get("at", 1.0)
            parts.append(f'<div class="torn" id="{sid}-st"><small>{esc(p.get("small", ""))}</small><b>{esc(p.get("big", ""))}</b></div>')
            tl.add(f'tl.fromTo("#{sid}-st",{{scale:2.3,rotation:-14,opacity:0}},{{scale:1,rotation:-4,opacity:1,duration:F(9),ease:E.snap}},{r2(at)});')
            tl.ev(at, "slam", g=0.45)
        # scene background drift + entry whoosh
        tl.add(f'tl.fromTo("#{sid}-bg",{{backgroundPosition:"40% 30%"}},{{backgroundPosition:"60% 50%",duration:{r2(dur)},ease:"none"}},{r2(t0)});')
        if i > 0:
            tr = s.get("transition", kit.get("transition", "cut"))
            used_tr.add(tr)
            if transition(tr, t0, tl):
                tl.ev(t0 - 0.15, "whoosh", g=0.4)
            else:
                tl.ev(t0, "whoosh")
        # poses
        ps = s.get("pose", "point")
        if isinstance(ps, str):
            ps = [[0, ps]]
        for pt, pn in ps:
            pose_track.append((t0 + pt, pn))
        body.append(f'<div id="{sid}" class="clip scene" data-start="{r2(t0)}" data-duration="{r2(dur if i < len(scenes) - 1 else total - t0)}" data-track-index="0">'
                    f'<div class="bg bg-{bg}" id="{sid}-bg"></div>{deco_html(s.get("deco", kit.get("deco", [])), sid, t0, dur, tl)}<div class="col">{"".join(parts)}</div></div>')

    # transition layer initial state (kept out of CSS transforms so GSAP owns them)
    init = {"push": ('#tx-panel', '{xPercent:-100,opacity:1}'), "scan": ('#tx-panel', '{yPercent:-100,opacity:1}'),
            "circle": ('#tx-panel', '{opacity:1}'), "page": ('#tx-page', '{xPercent:110,opacity:1}'),
            "blinds": ('#tx-blinds i', '{scaleY:0,opacity:1}')}
    for tk in used_tr:
        if tk in init:
            tl.lines.insert(0, f'tl.set("{init[tk][0]}",{init[tk][1]},0);')
    # mascot pose track
    pose_track.sort()
    last = None
    for pt, pn in pose_track:
        if pn not in pose_names:
            print(f"WARN pose '{pn}' not in pack {pose_names}; using {pose_names[0]}")
            pn = pose_names[0]
        if pn == last:
            continue
        tl.set(".pose", "{opacity:0}", pt)
        tl.set(f'.pose[data-pose={pn}]', "{opacity:1}", pt)
        if last is not None:
            tl.add(f'tl.fromTo("#mascot",{{y:26,scale:.975}},{{y:0,scale:1,duration:F(10),ease:E.settle}},{r2(pt)});')
        last = pn
    # mouth track
    ncues = 0
    if cfg.get("cues"):
        cues = json.load(open(os.path.join(base, cfg["cues"])))["mouthCues"]
        off = float(cfg.get("vo_offset", 0))
        prev = "X"
        for c in cues:
            v = c["value"]
            if v == prev:
                continue
            tl.set(".mth", "{opacity:0}", c["start"] + off)
            tl.set(f'.mth[data-m={v}]', "{opacity:1}", c["start"] + off)
            prev = v
            ncues += 1
    # idle bob
    reps = int(total / 1.7) + 1
    tl.add(f'tl.fromTo("#mbob",{{y:0,rotation:-0.6}},{{y:-9,rotation:0.6,duration:1.7,ease:"sine.inOut",repeat:{reps},yoyo:true}},0);')

    css = open(os.path.join(SKILL, "templates", "style.css")).read()
    kits_css = open(os.path.join(SKILL, "templates", "kits.css")).read()
    html_doc = f'''<!doctype html>
<html lang="ms" data-resolution="{"landscape" if fmt == "16x9" else "portrait"}"><head><meta charset="UTF-8">
<meta name="viewport" content="width={W}, height={H}">
<link rel="stylesheet" href="fonts/fonts.css">
<script src="vendor/gsap.min.js"></script>
<style>:root{{--W:{W}px;--H:{H}px;{theme_css}}}
{css}
{kits_css}</style></head>
<body class="{"land" if fmt == "16x9" else "port"} th-{theme_name} lay-{kit.get("layout", "left")}">
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{"".join(body)}
<div id="mascot"><div id="mbob">{m_html}</div></div>
{TX_HTML}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const FPS = 30, F = n => n / FPS;
const E = {{land:"power3.out", soft:"power2.out", snap:"expo.out", settle:"back.out(1.15)", exit:"power2.in", throw:"power4.in", move:"power2.inOut", drift:"none"}};
const tl = gsap.timeline({{paused:true}});
{chr(10).join(tl.lines)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
'''
    open(os.path.join(proj, "index.html"), "w").write(html_doc)
    tl.events.sort(key=lambda e: e["t"])
    json.dump({"duration": total, "music": cfg.get("music", kit.get("music", "lofi")), "events": tl.events}, open(os.path.join(proj, "events.json"), "w"), indent=0)

    # vendor + fonts (once)
    vend = os.path.join(proj, "vendor", "gsap.min.js")
    if not os.path.isfile(vend):
        os.makedirs(os.path.dirname(vend), exist_ok=True)
        r = subprocess.run("npm pack gsap@3.14.2 --silent", shell=True, cwd=proj, capture_output=True, text=True)
        tgz = os.path.join(proj, r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else ""
        import tarfile
        with tarfile.open(tgz) as tf:
            m = tf.getmember("package/dist/gsap.min.js")
            with tf.extractfile(m) as src, open(vend, "wb") as out:
                out.write(src.read())
        os.remove(tgz)
    stamp = os.path.join(proj, "fonts", ".theme")
    if not os.path.isfile(os.path.join(proj, "fonts", "fonts.css")) or not os.path.isfile(stamp) or open(stamp).read() != theme_name:
        fl = list(dict.fromkeys(THEME["fonts"].values()))
        r = subprocess.run([sys.executable, os.path.join(HERE, "fonts.py")] + fl, cwd=proj, capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode:
            sys.exit("font install failed: " + r.stdout + r.stderr)
        open(stamp, "w").write(theme_name)
    print(f"OK {proj}/index.html  {W}x{H}  {total}s  {len(scenes)} scenes  theme={theme_name}  mascot={mode}  mouth changes={ncues}  sfx events={len(tl.events)}")


if __name__ == "__main__":
    main()
