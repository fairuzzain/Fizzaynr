#!/usr/bin/env python3
"""Joins a film's clips and sets its loudness (references/clips.md, Assembly). Standard library, ffmpeg and ffprobe; faster-whisper
when it is installed (it picks the room tone for --fill).

  python3 assemble.py join script.json --clips <dir> -o joined.mp4 [--mute k2:0-2.04 …] [--fill]
  python3 assemble.py loudness joined.mp4 -o film.mp4

join: every clip of script.json in film order, cut from <dir>/<id>.mp4 (a part, "make": "part", from the take of its "of"): its
`kept` ranges, or else its first end - start seconds. The picture is cut by frames (trim) and the sound by samples at 48 kHz (atrim,
2,000 samples a frame), every range joined by the concat filter and encoded once (libx264 crf 17, yuv420p, 24 fps, AAC 192k 48 kHz
stereo). Each clip cut to its own file and joined with -c copy pushes the sound 23-43 ms later at every seam; this keeps every clip
in sync and the film exactly its frames. It prints each clip's place in the film and the film's frames and seconds.
  --mute k2:0-2.04  silences seconds of a clip's take (its own seconds, as `kept` counts them), sample-exact; repeat it, or give
                    several spans at once: k2:0-2.04,9.5-10. A part's id names its clip's take.
  --fill            fills every muted span with its clip's room tone instead of silence: a 1.5 s stretch of the same take (1.0 or
                    0.5 s if none) clear of its muted spans and, with faster-whisper, of every word it hears by 0.3 s; the
                    quietest steady one (lowest mean + 2 x spread of its 100 ms levels) on which whisper, sound tags on, writes
                    nothing ("(sighs)" and the like pass it over); without faster-whisper, the quietest steady one. A stretch whose
                    loudest 100 ms is more than 6 dB over its median holds a knock or a clatter and is never room tone (with whisper
                    on, one film's fill passed over two hum stretches whisper tagged and took a bell's knocks, looped every 1.5 s;
                    when whisper writes on every steady stretch, the quietest steady one is used and the printout says so). Nor is
                    a stretch whose median 100 ms is more than 10 dB over the take's quiet floor (the 20th percentile of the take's
                    100 ms levels, digital silence left out): a line or music, however steady (without whisper, a small tick ruled
                    out every quiet stretch of one take and its fill took a spoken line, -19.9 dB). With no stretch left it refuses
                    and says why. Looped with
                    50 ms equal-power crossfades and played at the stretch's own level, moved toward the quiet floor of the film's
                    second before and second after the span (the 20th percentile of their 100 ms levels against the stretch's
                    own; a side with no sound, at the film's edge, left out) by at most 6 dB either way, the floors printed;
                    crossfaded 50 ms into the clip's own sound on each side. (The mean level of a neighbouring second is set
                    by its loudest moment: a whoosh beside the span raised the fill 20 dB. A line or music that fills the
                    neighbouring second still reads as its floor; the bound holds that to 6 dB.)

loudness: the two loudnorm passes made safe. Pass 1 measures at I -14, TP -2.0. While the measured peak leaves no room for the gain
(input_tp + (-14 - input_i) > -2.0, so loudnorm would run dynamic), the sound is raised by the shortfall + 0.5 dB into a limiter
held at the first measured peak, and measured again; a measured LRA over 11 sets the LRA target to it + 0.1 (loudnorm runs linear
only within it). Each round measures with 3 s of silence after the sound: measuring, loudnorm counts its last 3 s twice, and a film
that ends loud came out 0.7 dB quiet without it. The limiter runs with latency=1: without it the sound comes out 1 ms (its attack)
late. Pass 2 applies it linear, the picture copied, the sound cut to the picture's frames x 2,000 samples (atrim=end_sample). The
encoded file is measured: when the AAC encode raised its true peak over -1.5 dBTP (0.3-0.7 dB on most films, 1.3 dB on a
hard-limited one), it all runs again at a TP target lowered by the excess + 0.2 dB, at most 3 encodes. It prints each round, and
refuses (exit 1, no film written) when pass 2 does not print "linear" or the encoded file misses I -14 +-0.5 LUFS or, after 3
encodes, TP -1.5 dBTP.
"""
import argparse
import array
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile

FPS = 24
RATE = 48000
SPF = RATE // FPS          # 2,000 samples a frame
FADE = 0.05                # room tone loop and fill crossfades, seconds
VIDEO = ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS)]
AUDIO = ["-c:a", "aac", "-b:a", "192k", "-ar", str(RATE), "-ac", "2"]
TARGET_I, TARGET_TP, TARGET_LRA = -14.0, -2.0, 11.0
BAR_I, BAR_TP = 0.5, -1.5  # the encoded file: I within 0.5 LU of -14, true peak at most -1.5 dBTP
ROOM_TONE = (1.5, 1.0, 0.5)  # stretch lengths tried, seconds
FILL_MOVE = 6.0            # the fill moves at most this many dB from its stretch's own level toward the neighbours' floor
WORD_MARGIN = 0.3          # a room tone stretch keeps this far from any word whisper hears
TRANSIENT = 6.0            # a stretch whose loudest 100 ms is this many dB over its median holds a knock: never room tone
OVER_FLOOR = 10.0          # a stretch whose median 100 ms is this many dB over the take's quiet floor is a line or music
BLANK = re.compile(r"\[\s*blank\s*_?\s*audio\s*\]", re.I)  # whisper's tag for a stretch with no sound


def fail(message):
    print(f"REFUSED: {message}")
    sys.exit(1)


def run(cmd, what):
    p = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, text=True)
    if p.returncode:
        fail(f"{what}: ffmpeg failed:\n" + "\n".join(p.stderr.strip().splitlines()[-12:]))
    return p


def probe(path):
    p = run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", path], f"probe {path}")
    streams = json.loads(p.stdout).get("streams", [])
    pick = lambda kind: next((s for s in streams if s.get("codec_type") == kind), None)
    return pick("video"), pick("audio")


def frames_of(path):
    p = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets",
             "-of", "csv=p=0", path], f"count frames of {path}")
    return int(p.stdout.strip().strip(",") or 0)


def rate_of(video):
    num, _, den = video.get("r_frame_rate", "0/1").partition("/")
    return float(num) / float(den or 1)


def frame(seconds):
    return int(math.floor(seconds * FPS + 0.5 + 1e-6))


def pcm(path, cache={}):
    """A file's sound as 16-bit mono samples at 48 kHz, as aresample=48000 makes them (the same sample positions as the join)."""
    if path not in cache:
        out = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"],
                             capture_output=True, stdin=subprocess.DEVNULL).stdout
        a = array.array("h")
        a.frombytes(out[:len(out) // 2 * 2])
        if sys.byteorder == "big":
            a.byteswap()
        cache[path] = a
    return cache[path]


def level(samples):
    """RMS in dB below full scale; None for no samples."""
    if not len(samples):
        return None
    power = sum(x * x for x in samples) / len(samples)
    return 10 * math.log10(power / 32768.0 ** 2) if power > 0 else -240.0


def floor(samples, back=False):
    """The quiet floor: the 20th percentile (linear between ranks) of the levels of whole 100 ms blocks, counted from the end when
    back; None for less than 100 ms."""
    step = RATE // 10
    n = len(samples) // step
    if not n:
        return None
    start = len(samples) - n * step if back else 0
    return p20(level(samples[start + k * step:start + (k + 1) * step]) for k in range(n))


def p20(levels):
    """The 20th percentile (linear between ranks) of levels; None for none."""
    v = sorted(levels)
    if not v:
        return None
    pos = 0.2 * (len(v) - 1)
    i = int(pos)
    return v[i] + (v[min(i + 1, len(v) - 1)] - v[i]) * (pos - i)


# ---------- the clips in film order ----------

def take_of(k):
    """The clip whose take an entry shows: a part's `of`, else the entry itself."""
    return k.get("of") if k.get("make") == "part" else k.get("id")


def kept_ranges(k):
    kept = k.get("kept")
    return [] if not kept else kept if isinstance(kept, list) else [kept]


def plan(script):
    """One range per kept range, in film order: {id, take, a, b (frames of the take), film (its first film frame)}. Each range's
    frames are counted on the film's own frame grid (round(film seconds x 24)), so the film is exactly its planned frames."""
    parts, notes, film, previous = [], [], 0, None
    for k in sorted(script.get("clips", []), key=lambda c: c.get("start", 0)):
        if previous is not None and abs(k["start"] - previous) > 1e-6:
            notes.append(f'clip {k["id"]} starts at {k["start"]} s, the clip before it ends at {previous} s')
        t = k["start"]
        for g in kept_ranges(k) or [{"from": 0, "to": k["end"] - k["start"]}]:
            n = frame(t + g["to"] - g["from"]) - frame(t)
            a = frame(g["from"])
            parts.append({"id": k["id"], "take": take_of(k), "a": a, "b": a + n, "film": film})
            film += n
            t += g["to"] - g["from"]
        if abs(t - k["end"]) > 0.5 / FPS:
            notes.append(f'clip {k["id"]}: its kept seconds add up to {t - k["start"]:g}, its window {k["start"]}-{k["end"]} to '
                         f'{k["end"] - k["start"]:g}')
        previous = k["end"]
    return parts, notes


def parse_mutes(specs, script):
    """--mute k2:0-2.04[,a-b…] -> {take: [(from, to), …]} in the take's own seconds."""
    takes = {k["id"]: take_of(k) for k in script.get("clips", [])}
    mutes = {}
    for spec in specs or []:
        cid, _, spans = spec.partition(":")
        if cid not in takes or not spans:
            fail(f"--mute {spec}: write <clip id>:<from>-<to>[,<from>-<to>…] with an id of script.json")
        for span in spans.split(","):
            try:
                lo, hi = (float(x) for x in span.split("-"))
            except ValueError:
                fail(f"--mute {spec}: {span} is not <from>-<to> in seconds")
            if not 0 <= lo < hi:
                fail(f"--mute {spec}: {span} is empty or negative")
            mutes.setdefault(takes[cid], []).append((lo, hi))
    for take, spans in mutes.items():  # merge spans that touch or overlap (each fill needs its own 2 x 50 ms around it)
        spans.sort()
        merged = [list(spans[0])]
        for lo, hi in spans[1:]:
            if lo <= merged[-1][1] + 2 * FADE:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        mutes[take] = [tuple(m) for m in merged]
    return mutes


def part_mutes(part, mutes):
    """The take's muted spans that fall in this range, in the range's own seconds."""
    a, b = part["a"] / FPS, part["b"] / FPS
    return [(max(lo, a) - a, min(hi, b) - a) for lo, hi in mutes.get(part["take"], []) if min(hi, b) > max(lo, a)]


# ---------- room tone (--fill) ----------

def whisper():
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    return WhisperModel("small", device="cpu", compute_type="int8")


def heard(model, path, lo=None, hi=None, tags=False):
    """What whisper hears in a file or a stretch of it: [(start, end, text)]. tags=True lets it write sound tags ("(sighs)")."""
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "a.wav")
        cut = ["-ss", f"{lo:.3f}", "-to", f"{hi:.3f}"] if lo is not None else []
        run(["ffmpeg", "-v", "error", "-y", "-i", path] + cut + ["-vn", "-ac", "1", "-ar", "16000", wav], "cut for whisper")
        options = {"suppress_tokens": []} if tags else {}
        segments, _ = model.transcribe(wav, word_timestamps=True, vad_filter=False, condition_on_previous_text=False, **options)
        return [(w.start, w.end, w.word.strip()) for s in segments for w in (s.words or []) if w.word.strip()]


def room_tone(path, take, spans, model):
    """The take's room tone: (from, to) seconds, its dB, its floor and how it was chosen. Candidates keep clear of the take's muted
    spans, its first and last 0.1 s, digital silence and (with whisper) every word heard with 0.3 s around it; the quietest steady
    stretch (lowest mean + 2 x spread of its 100 ms levels) wins, and with whisper the first candidate on which it writes nothing,
    sound tags included."""
    x = pcm(path)
    step = RATE // 10
    db = [level(x[i:i + step]) for i in range(0, len(x) - step + 1, step)]
    quiet = p20(v for v in db if v >= -90)  # the take's quiet floor, digital silence left out
    tenths = lambda lo, hi, margin: range(max(0, int((lo - margin) * 10)), int(math.ceil((hi + margin) * 10)))
    banned = set(i for i, v in enumerate(db) if v < -90 or i in (0, len(db) - 1))
    for lo, hi in spans:
        banned.update(tenths(lo, hi, 0.1))
    said = set()
    for w0, w1, _ in heard(model, path) if model else []:
        said.update(tenths(w0, w1, WORD_MARGIN))

    def stretches(out):  # (score, first tenth, tenths), quietest and steadiest first, at the longest length that has any
        for seconds in ROOM_TONE:
            n = int(seconds * 10)
            found = []
            for i in range(len(db) - n + 1):
                if not any(j in out for j in range(i, i + n)):
                    v = db[i:i + n]
                    if max(v) - statistics.median(v) > TRANSIENT:  # a knock or a clatter inside it: never room tone
                        continue
                    if statistics.median(v) > quiet + OVER_FLOOR:  # a line or music, steady as it is: never room tone
                        continue
                    mean = sum(v) / n
                    found.append((mean + 2 * math.sqrt(sum((u - mean) ** 2 for u in v) / n), i, n))
            if found:
                return sorted(found)
        return []

    found = stretches(banned | said)
    how = "no word heard near it" if model else "faster-whisper not installed: the quietest steady stretch"
    if not found and said:
        found, how = stretches(banned), "whisper hears words all through the take: the quietest steady stretch"
    if not found:
        fail(f"{take}: no {ROOM_TONE[-1]} s outside its muted spans is room tone: each holds a knock (its loudest 100 ms more than "
             f"{TRANSIENT:g} dB over its median) or a line or music (its median more than {OVER_FLOOR:g} dB over the take's quiet "
             f"floor, {'-' if quiet is None else f'{quiet:.1f}'} dB): mute it without --fill")
    pick = found[0]
    if model:  # the first of the five best places on which whisper, sound tags on, writes nothing
        tried, clean, rejected = [], None, []
        for cand in found:
            if any(abs(cand[1] - t[1]) < cand[2] for t in tried):
                continue
            tried.append(cand)
            text = " ".join(w for _, _, w in heard(model, path, cand[1] / 10, (cand[1] + cand[2]) / 10, tags=True))
            text = BLANK.sub("", text).strip()  # whisper's own tag for no sound counts as nothing
            if not text:
                clean = cand
                break
            rejected.append(f'{cand[1] / 10:.1f}-{(cand[1] + cand[2]) / 10:.1f} s "{text}"')
            if len(tried) == 5:
                break
        if clean:
            pick, how = clean, how + ", whisper (sound tags on) writes nothing on it"
        else:
            how += ", whisper writes something on every quiet place: the quietest steady one"
        if rejected:
            how += " (passed over: " + ", ".join(rejected) + ")"
    _, i, n = pick
    lo, hi = i / 10, (i + n) / 10
    stretch = x[int(lo * RATE):int(hi * RATE)]
    return lo, hi, level(stretch), floor(stretch), how


def film_sound(parts, files, mutes, t0, t1):
    """The film's sound (before any fill) over film seconds [t0, t1), muted spans left out; empty if nothing is there."""
    samples = array.array("h")
    for p in parts:
        ps, pe = p["film"] / FPS, (p["film"] + p["b"] - p["a"]) / FPS
        lo, hi = max(t0, ps), min(t1, pe)
        if hi <= lo:
            continue
        x, base = pcm(files[p["take"]]), p["a"] * SPF - p["lead"]
        keep = [(lo - ps, hi - ps)]
        for m0, m1 in part_mutes(p, mutes):  # cut the muted spans out of the stretch
            keep = [piece for a, b in keep for piece in ((a, min(b, m0)), (max(a, m1), b)) if piece[1] > piece[0]]
        for a, b in keep:  # rounded, not cut: one sample short drops a whole 100 ms block from the floor
            samples.extend(x[max(0, base + round(a * RATE)):max(0, base + round(b * RATE))])
    return samples


def envelope(a, b, d1, d2, inside):
    """Equal-power gain of the clip's own sound (inside=0) or of the fill (inside=1) around a span [a, b] of part seconds, with
    crossfades of d1 before a and d2 after b."""
    up, down = ("cos", "sin") if inside == 0 else ("sin", "cos")
    outside = 1 - inside
    return (f"if(lt(t,{a - d1:.6f}),{outside},if(lt(t,{a:.6f}),{up}(PI/2*(t-{a - d1:.6f})/{max(d1, 1e-6):.6f}),"
            f"if(lt(t,{b:.6f}),{inside},if(lt(t,{b + d2:.6f}),{down}(PI/2*(t-{b:.6f})/{max(d2, 1e-6):.6f}),{outside}))))")


# ---------- join ----------

def join(args):
    with open(args.script) as f:
        script = json.load(f)
    parts, notes = plan(script)
    if not parts:
        fail(f"{args.script} has no clips")
    mutes = parse_mutes(args.mute, script)
    takes = []
    for p in parts:
        if p["take"] not in takes:
            takes.append(p["take"])
    files, info = {}, {}
    for take in takes:
        path = os.path.join(args.clips, f"{take}.mp4")
        if not os.path.exists(path):
            other = sorted(f for f in os.listdir(args.clips) if os.path.splitext(f)[0] == take)
            if not other:
                fail(f"{take}: no {take}.mp4 (or {take}.<ext>) in {args.clips}")
            path = os.path.join(args.clips, other[0])
        video, audio = probe(path)
        if not video:
            fail(f"{path} has no picture")
        files[take], info[take] = path, (video, audio, frames_of(path))
    for take in mutes:
        if take not in files:
            fail(f"--mute names {take}, which is not in the film")
    size = (info[takes[0]][0]["width"], info[takes[0]][0]["height"])
    for p in parts:
        video, audio, count = info[p["take"]]
        if p["b"] > count:
            fail(f'clip {p["id"]}: frames {p["a"]}-{p["b"]} of {p["take"]}, which has {count} frames')
        p["lead"] = 0
        if audio:  # the take's sound starts this many samples after its picture
            p["lead"] = round((float(audio.get("start_time", 0) or 0) - float(video.get("start_time", 0) or 0)) * RATE)
            have = float(audio.get("duration", 0) or 0) * RATE + p["lead"]
            if have < p["b"] * SPF:
                notes.append(f'clip {p["id"]}: its sound ends at {have / RATE:.3f} s, before frame {p["b"]}: silence after it')
    model = whisper() if args.fill and mutes else None
    tones = {}
    if args.fill:
        for take, spans in mutes.items():
            tones[take] = room_tone(files[take], take, spans, model)

    inputs = {take: i for i, take in enumerate(takes)}
    graph, pads, lines = [], [], []
    for n, p in enumerate(parts):
        i, (video, audio, _) = inputs[p["take"]], info[p["take"]]
        fix = "" if abs(rate_of(video) - FPS) < 1e-3 else f"fps={FPS},"
        if fix:
            notes.append(f'{p["take"]} runs at {video.get("r_frame_rate")} fps: converted to {FPS} before cutting')
        scale = ""
        if (video["width"], video["height"]) != size:
            scale = (f",scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease,"
                     f"pad={size[0]}:{size[1]}:(ow-iw)/2:(oh-ih)/2,setsar=1")
            notes.append(f'{p["take"]} is {video["width"]}x{video["height"]}: fitted into {size[0]}x{size[1]}')
        graph.append(f"[{i}:v]{fix}trim=start_frame={p['a']}:end_frame={p['b']},setpts=PTS-STARTPTS{scale}[v{n}]")
        s0, s1 = p["a"] * SPF - p["lead"], p["b"] * SPF - p["lead"]
        head = f"[{i}:a]aresample={RATE},aformat=sample_fmts=fltp:channel_layouts=stereo"
        if s0 < 0:  # the sound starts after the picture: silence before it
            head += f",adelay=delays={-s0}S:all=1"
            s0, s1 = 0, s1 - s0
        if not audio:
            head = f"anullsrc=r={RATE}:cl=stereo"
        sound = f"{head},apad,atrim=start_sample={s0}:end_sample={s1},asetpts=PTS-STARTPTS"
        spans = part_mutes(p, mutes)
        length = (p["b"] - p["a"]) / FPS
        film0 = p["film"] / FPS
        line = (f'{p["id"]:6} {os.path.basename(files[p["take"]]):10} frames {p["a"]}-{p["b"]} ({(p["b"] - p["a"]) / FPS:.3f} s) '
                f'-> film {film0:.3f}-{film0 + length:.3f} s, frames {p["film"]}-{p["film"] + p["b"] - p["a"]}')
        lines.append(line)
        if spans and not args.fill:
            gain = "*".join(f"(1-between(t,{a:.6f},{b:.6f}))" for a, b in spans)
            graph.append(f"{sound},aeval=exprs='val(ch)*{gain}':c=same[a{n}]")
            for a, b in spans:
                lines.append(f"         muted {a + p['a'] / FPS:.3f}-{b + p['a'] / FPS:.3f} s of {p['take']} (film {film0 + a:.3f}-{film0 + b:.3f} s)")
        elif spans:
            r0, r1, rdb, rfloor, how = tones[p["take"]]
            own, fills = [], []
            for j, (a, b) in enumerate(spans):
                d1, d2 = min(FADE, a), min(FADE, length - b)
                before = floor(film_sound(parts, files, mutes, film0 + a - 1, film0 + a), back=True)
                after = floor(film_sound(parts, files, mutes, film0 + b, film0 + b + 1))
                near = [v for v in (before, after) if v is not None]
                toward = sum(near) / len(near) - rfloor if near else 0.0
                gain = max(-FILL_MOVE, min(FILL_MOVE, toward))
                total = int(round((b + d2 - (a - d1)) * RATE))
                piece = int(round((r1 - r0) * RATE))
                copies = max(1, int(math.ceil((total - FADE * RATE) / (piece - FADE * RATE))))
                loop = [f"[{i}:a]aresample={RATE},aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=start_sample={int(r0 * RATE)}:"
                        f"end_sample={int(r0 * RATE) + piece},asetpts=PTS-STARTPTS[t{n}_{j}_{c}]" for c in range(copies)]
                graph.extend(loop)
                chain = f"[t{n}_{j}_0]"
                for c in range(1, copies):
                    graph.append(f"{chain}[t{n}_{j}_{c}]acrossfade=ns={int(FADE * RATE)}:c1=qsin:c2=qsin[x{n}_{j}_{c}]")
                    chain = f"[x{n}_{j}_{c}]"
                graph.append(f"{chain}atrim=end_sample={total},volume={gain:.2f}dB,adelay=delays={int(round((a - d1) * RATE))}S:all=1,"
                             f"apad,atrim=end_sample={(p['b'] - p['a']) * SPF},aeval=exprs='val(ch)*{envelope(a, b, d1, d2, 1)}':c=same"
                             f"[f{n}_{j}]")
                fills.append(f"[f{n}_{j}]")
                own.append(envelope(a, b, d1, d2, 0))
                show = lambda v: "-" if v is None else f"{v:.1f}"
                held = f", held at {FILL_MOVE:g} dB" if abs(toward) > FILL_MOVE else ""
                lines.append(f"         muted {a + p['a'] / FPS:.3f}-{b + p['a'] / FPS:.3f} s of {p['take']} (film {film0 + a:.3f}-"
                             f"{film0 + b:.3f} s), filled with its room tone {r0:.1f}-{r1:.1f} s ({how}; {rdb:.1f} dB), "
                             f"{gain:+.1f} dB{held}: floors (20th percentile of 100 ms levels) stretch {rfloor:.1f}, second before "
                             f"{show(before)}, after {show(after)} dB")
            graph.append(f"{sound},aeval=exprs='val(ch)*{'*'.join(own)}':c=same[o{n}]")
            graph.append(f"[o{n}]{''.join(fills)}amix=inputs={1 + len(fills)}:normalize=0:duration=first[a{n}]")
        else:
            graph.append(f"{sound}[a{n}]")
        pads.append(f"[v{n}][a{n}]")
    total = sum(p["b"] - p["a"] for p in parts)
    graph.append(f"{''.join(pads)}concat=n={len(parts)}:v=1:a=1[v][a]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for take in takes:
        cmd += ["-i", files[take]]
    cmd += ["-filter_complex", ";".join(graph), "-map", "[v]", "-map", "[a]"] + VIDEO + AUDIO + ["-movflags", "+faststart", args.o]
    for line in lines:
        print(line)
    for note in notes:
        print(f"note: {note}")
    run(cmd, f"join into {args.o}")
    made = frames_of(args.o)
    _, audio = probe(args.o)
    sound = float(audio.get("duration", 0)) if audio else 0
    print(f"{args.o}: {made} frames = {made / FPS:.3f} s at {FPS} fps; sound {sound:.4f} s at {RATE} Hz "
          f"(planned {total} frames = {total / FPS:.3f} s)")
    if made != total:
        fail(f"{args.o} has {made} frames, not the planned {total}")
    return 0


# ---------- loudness ----------

def loudnorm(src, chain, what):
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-map", "0:a:0", "-af", chain, "-f", "null", "-"], what)
    blocks = re.findall(r"\{[^{}]*\}", p.stderr)
    if not blocks:
        fail(f"{what}: loudnorm printed no measurement")
    return json.loads(blocks[-1])


def rounds(src, tp_target):
    """The measuring rounds: (pre-stage filters, LRA target, the last measurement), the last one fit to run linear."""
    target = lambda lra: f"loudnorm=I={TARGET_I}:TP={tp_target:g}:LRA={lra:g}"
    pre, gain, lra, limit = "", 0.0, TARGET_LRA, None
    for n in range(1, 11):
        # apad: measuring (dynamic mode), loudnorm counts its last 3-s lookahead twice, so a film that ends loud read up to
        # 0.9 dB hot and came out 0.6-0.7 dB quiet; 3 s of silence after the sound (under every gate) makes the count exact
        m = loudnorm(src, (pre + "," if pre else "") + "apad=pad_dur=3," + target(lra) + ":print_format=json", f"round {n}")
        i, tp, mlra = float(m["input_i"]), float(m["input_tp"]), float(m["input_lra"])
        short = tp + (TARGET_I - i) - tp_target
        state = f"short by {short:.2f} dB" if short > 0 else (f"fits; LRA {mlra:.2f} > {lra:g}" if mlra > lra else "fits")
        print(f"round {n}: pre-gain {gain:.2f} dB -> I {i:.2f} LUFS, TP {tp:.2f} dBTP, LRA {mlra:.2f} LU, thresh "
              f"{float(m['input_thresh']):.2f}: {state}")
        if short > 0:
            if limit is None:  # the limiter holds the peaks at the first measured peak
                limit = min(1.0, max(0.0625, 10 ** (tp / 20)))
            gain += short + 0.5
            # latency=1: without it alimiter delays the sound by its attack (1 ms)
            pre = f"volume={gain:.2f}dB,alimiter=limit={limit:.4f}:attack=1:release=50:level=false:latency=1"
            continue
        if mlra > lra:
            lra = math.ceil(round((mlra + 0.1) * 10, 6)) / 10
            if lra > 50:
                fail(f"LRA {mlra:.2f} is past loudnorm's largest target (50): it can only run dynamic")
            continue
        return pre, target(lra), m
    fail("10 rounds and the peak still leaves no room: look at the mix")


def loudness(args):
    video, audio = probe(args.input)
    if not video or not audio:
        fail(f"{args.input} needs a picture and a sound")
    frames, fps = frames_of(args.input), rate_of(video)
    end = int(round(frames * RATE / fps))
    print(f"{args.input}: {frames} frames = {frames / fps:.3f} s; the sound is cut to {end} samples at {RATE} Hz")
    base, ext = os.path.splitext(args.o)
    temp = f"{base}.partial{ext}"
    tp_target = TARGET_TP
    for attempt in range(1, 4):
        print(f"-- TP target {tp_target:g} dBTP")
        pre, target, m = rounds(args.input, tp_target)
        chain = (pre + "," if pre else "") + (
            f"{target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
            f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json,"
            f"aresample={RATE},aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=end_sample={end}")
        print(f"pass 2: -af \"{chain}\"")
        p = run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", args.input, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
                 "-af", chain] + AUDIO + ["-movflags", "+faststart", temp], "pass 2")
        blocks = re.findall(r"\{[^{}]*\}", p.stderr)
        m2 = json.loads(blocks[-1]) if blocks else {}
        kind = m2.get("normalization_type")
        print(f'pass 2: "normalization_type" : "{kind}" (its own input I {m2.get("input_i")}, output I {m2.get("output_i")}, '
              f'output TP {m2.get("output_tp")})')
        if kind != "linear":
            os.remove(temp)
            fail(f"pass 2 ran {kind}, not linear: no film written")
        # the encoded file, measured to 0.01 dB (ebur128 prints 0.1, so a peak of -1.46 would print -1.5 and pass)
        e = loudnorm(temp, "apad=pad_dur=3,loudnorm=I=-14:TP=-2:LRA=11:print_format=json", "measure the encoded file")
        got_i, got_tp, got_lra = float(e["input_i"]), float(e["input_tp"]), float(e["input_lra"])
        _, a2 = probe(temp)
        made = frames_of(temp)
        print(f"{args.o}: I {got_i:.2f} LUFS, TP {got_tp:.2f} dBTP, LRA {got_lra:.1f} LU (the encoded AAC); {made} frames = "
              f"{made / fps:.3f} s; sound {float(a2.get('duration', 0)):.4f} s")
        if abs(got_i - TARGET_I) > BAR_I:
            os.replace(temp, f"{base}.refused{ext}")
            fail(f"the encoded file measures I {got_i} LUFS (bar: {TARGET_I} +-{BAR_I}); kept as {base}.refused{ext}")
        if got_tp <= BAR_TP:
            os.replace(temp, args.o)
            return 0
        # the AAC encode raised the peak past the bar (0.3-0.5 dB on most films, 1.3 on a hard-limited one): lower the target
        tp_target = round(tp_target - (got_tp - BAR_TP) - 0.2, 1)
        print(f"TP {got_tp} dBTP is over {BAR_TP}: the encode added {got_tp - float(m2.get('output_tp', tp_target)):.1f} dB to "
              f"pass 2's peak; again at TP {tp_target:g}")
    os.replace(temp, f"{base}.refused{ext}")
    fail(f"3 encodes and the true peak is still over {BAR_TP} dBTP; kept as {base}.refused{ext}")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="step")
    j = sub.add_parser("join", help="the clips of script.json, cut by frames and samples, joined, encoded once")
    j.add_argument("script")
    j.add_argument("--clips", required=True, help="the folder of the clips' takes, <id>.mp4")
    j.add_argument("-o", required=True, help="the joined film")
    j.add_argument("--mute", action="append", help="<clip>:<from>-<to>[,…] in the take's own seconds")
    j.add_argument("--fill", action="store_true", help="fill muted spans with the clip's room tone")
    l = sub.add_parser("loudness", help="the iterated two-pass loudnorm, linear, picture copied")
    l.add_argument("input")
    l.add_argument("-o", required=True)
    args = ap.parse_args(argv[1:])
    if args.step == "join":
        return join(args)
    if args.step == "loudness":
        return loudness(args)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
