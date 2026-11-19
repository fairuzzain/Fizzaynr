#!/usr/bin/env python3
"""Mechanical checks for each step of a film. Each prints the reasons a step's output is refused (quoting what to fix) and exits 1,
or prints PASS and exits 0. Standard library only.

  python3 checks.py script        script.json [--faces N]        (the script and its clip plan)
  python3 checks.py plan          plan.json script.json          (viewer plan: {"items": [...]})
  python3 checks.py effects       effects.json script.json
  python3 checks.py sheet         sheet-prompt.txt [--photo] [--stylized] [--2d]
  python3 checks.py location      location-prompt.txt
  python3 checks.py master        master-prompt.txt              (3D and 2D: the style master)
  python3 checks.py prop          prop-prompt.txt [--2d]         (a prop sheet; in live action written from words, seedream_v5_pro)
  python3 checks.py plate         plate-prompt.txt               (2D: a background plate, plate-<location>-<n>.txt; any style: a
                                                                 frame plate, named for its frame id: plate-k1@0.3-morning.txt
                                                                 makes frame:k1@0.3/morning)
  python3 checks.py clip          clip-prompt.txt script.json k1 (a clip's prompt, against plan.json beside script.json and the
                                                                 prompt of the clip before it beside this one; a narrated or
                                                                 sung film's clip also prints its lines in the clip's own seconds,
                                                                 and any clip the warnings it does not refuse on)

An image prompt of a 3D or 2D film adds --style <its style file, styles/<template>.md>: the style file's style block must be in it
word for word (references/style-master.md, The style block in every image).
"""
import json
import os
import re
import sys

MAX_LINE_WORDS = {"dialogue": 10, "thought": 10, "sung": 11, "narration": 20}  # lip-synced lines go robotic past 10
WORDS_PER_MINUTE = (70, 110) # dialogue: at least 70 a minute of talk time (each clip less its 4-s tail, the film less the hook's
                             # 1.5 s), at most 110 a minute of the film; counted on the whole film, 0 of 15 scripts held every rule
NARRATION_PER_MINUTE = (160, 175)  # narration lines (references/formats.md)
SUNG_PER_MINUTE = {"seed_audio": (60, 100),           # sung slowly, about 80-100 words a minute
                   "elevenlabs_music_v2": (85, 110)}  # 102-111 words a minute at 76 BPM (references/formats.md)
FORMATS = ("dialogue", "storytime", "song", "talking-object", "inside-body")
NARRATED = {"storytime": ("narration",), "song": ("sung",), "inside-body": ("narration",)}
LINE_TAIL = 4                # a line ends at least 4 s before its clip ends: the model delivers lines up to 1.5 s late
SHORTEST_SHOT = 1.5          # a shot on screen; shorter ones were dropped or blurred
CUT_MARGIN = 0.8             # the model's cuts land up to 0.8 s off the written seconds (95% of 261 shots), so a shot that must last n s on screen
                             # is written n + 0.8 (references/clips.md, Cutting the film into clips)
LAST_SHOT_MARGIN = 1.8       # a clip's last shot after a spoken line came out up to 1.8 s short (95% of 23 clips; 0.57 s without speech)
ENDING_SECONDS = 4           # the ending's action after the film's last line, on screen (the move, then its result)
ENDING_TOLERANCE = 0.3       # K2: a looked-at shot that starts up to 0.3 s before the last line's measured end counts from that end:
                             # whisper puts a last word's end up to 0.17 s past a cut it was voiced before
ENDING_LEAD = 1.0            # a beat that starts up to 1 s before the screenplay's ENDING heading is the ending's: a heading gives
                             # whole seconds
ENDING_LAST_BEAT = False     # with the film's last line in the last clip, its last beat alone must be 4 + 1.8 s (True), or the
                             # beats from the ENDING heading on, after the line, together (False)
INSERT_SECONDS = 2.8         # an insert is a physical action: 2 s on screen, written 2 + CUT_MARGIN (inserts written 2.3-2.4 s came
                             # out 1.67 s)
SPOKEN_RATE = 2.5            # words a second a spoken line is estimated at, or its speaker's own rate measured on their voice clip
                             # (cast[].wordsPerSecond) when that is slower: the own rate alone let 8 of 57 later lines run 0.5 s past
                             # their estimate, 2.5 alone 5
SPOKEN_RATES = (1.0, 6.0)    # a measured speaking rate outside these is a measuring error
SIDES_REFUSED = False        # a clip whose positions name two or more cast members but not who is on which side of whom: refused
                             # (True) or not checked: 3 of 43 such clips flipped sides, and 3 of 31 that named the side
LAST_LINE_GAP = 5            # the last line starts at least 5 s before the film ends
HOOK_ACTION = 1.5            # the hook's action lands before the first dialogue or thought line
CLIP_SECONDS = (4, 30)       # one seedance_2_5 generation
MAX_GENERATION = {"480p": 1, "720p": 1, "1080p": 2}  # an original is 0; below 1080p one level deep (references/clips.md)
ASPECT_RATIOS = ("9:16", "16:9", "1:1", "4:3", "3:4", "21:9")    # the clip model's shapes
NOT_480P = ()                # RES2: every style goes at the resolution the user picks; pixel art's 480p smear is told in the
                             # offer (styles/pixel-art.md), no longer refused
MAX_IMAGES, MAX_VIDEOS, MAX_VIDEO_SECONDS, MAX_AUDIOS = 9, 10, 30, 10
SONG_INTRO, SONG_OUTRO = 3, 8  # a made song's seconds before its first sung word and after its last (references/formats.md)
SUNG_CLIP, SUNG_SPLIT = 15, 6  # a sung film's clip over 15 s is split at a line's first word that leaves 6 s on each side
CAST_SIZE = (2, 6)
FRAME = re.compile(r"^frame:(\w+)@(\d+(?:\.\d+)?)(?:/([\w-]+))?$")  # a second edit of one frame takes a tag: frame:k1@0.3/morning
PLATE = re.compile(r"^(\w+)#(\d+)$")  # one background plate of a 2D location, numbered from 1
FRAME_PLATE = re.compile(r"^plate-(\w+)@(\d+(?:\.\d+)?)(?:-([\w-]+))?\.txt$")  # the edit's prompt file of frame:k1@0.3/morning:
                                                                            # plate-k1@0.3-morning.txt
NARRATION_RATE = 3.0           # words a second a narration line is estimated at when it has no endSeconds (takes ran 146-237 a minute)
SHOT_SIZES = (("extreme close-up", r"\bextreme close"), ("insert", r"\binsert\b"), ("medium close", r"\bmedium[- ]close"),
              ("medium-wide", r"\bmedium[- ](?:wide|long)\b"), ("medium", r"\bmedium\b"), ("close", r"\bclose(?:-up)?\b"),
              ("wide", r"\bwide\b|\b(?:long|full) shot\b"))  # the shot-size word of a beat's framing, the most specific first
SIZE_STEPS = ("extreme close-up", "close", "medium close", "medium", "medium-wide", "wide")  # one step apart reads as a jump
CLOSE_SHOTS = ("insert", "extreme close-up", "close")  # what a cut inside one continuous moment opens on (clips.md)
ENDING_AFTER = ("dialogue", "thought")  # the ending rule holds when the film's last line is spoken in its clip: a narration or song's
                             # last line is placed by its track, which no clip prompt can move
CONTINUOUS_REFUSED = False   # a fresh clip in the place and moment of the clip before that opens wider than a close-up: refused
                             # (True) or not checked: 28 of 40 such seams cut cleanly
SAME_VIEW_REFUSED = False    # two beats in a row on one subject from one view and size: printed as a warning (4 of 12 lost their cut)
POSTURE_REFUSED = True       # a cast member a beat names without a posture word: refused (25 of 30 such beats had none)
PIXEL_HEAD_REFUSED = False   # a pixel-art close-up without "head and shoulders": refused (True) or not checked: written with the
                             # words or without, 21% came back extreme close-ups
POSTURE = (r"\b(?:stand|stands|standing|stood|upright|sit|sits|sitting|seated|sat|kneel|kneels|kneeling|knelt|on (?:his|her|its|their) "
           r"knees|lie|lies|lying|lay|lays|walk|walks|walking|lean|leans|leaning|crouch\w*|squat\w*|perch\w*|hunch\w*|slump\w*|"
           r"sprawl\w*|curl\w*|reclin\w*|propped|bend|bends|bending|bent|straighten\w*|step|steps|stepping|stride\w*|strode|"
           r"run|runs|running|hurr\w+|rush\w*|climb\w*|jump\w*|hop|hops|hopping|danc\w+|pace|paces|pacing|tiptoe\w*|crawl\w*|"
           r"stumbl\w*|float\w*|hover\w*|hang|hangs|hanging|rest|rests|resting|rise|rises|rising|rose|stands?|gets? up|spins?|"
           r"spinning|cross(?:es|ing)|flops?|lands?|rolls? over|topples?|falls? (?:back|down|onto|into|on)|coming down|comes down|"
           r"on (?:his|her|its|their) back)\b")
# a character's posture words: every shot says each character's posture (clips.md, The clip's prompt)
TIME_JUMP = r"\b(?:next|following) (?:morning|day|night|evening|afternoon|week)\b|\b(?:hours?|days?|nights?|weeks?|months?|years?) later\b"
# iteration 4's checks.py fixes that held their tests (tests/checks in iter-4), each behind its own switch
QUOTES_NOT_PROPS = True      # C2: a prop named only inside a quoted line is not counted as named in the prompt
LABEL_ENDING = True          # C3: the master and a stylized character sheet may end with the user's product label sentence
POSTURE_CLAUSE = True        # C4: a clause opening on a posture word ("in silence, standing astride …") is the posture of the
                             # character the clause before it names, when it names only one
TIME_JUMP_WIDE = True        # C7: a clip whose stateIn names a new time jump opens on a wide or medium-wide beat
CROP_NOT_WIDE = True         # C8: a 2D first clip's wide beat that names a body crop ("from the chest up") is not its wide
AUDIO_AS_SENT = True         # C9: a take trimmed after it was made (`kept`) keeps the prompt it was sent with: its @Audio tags are
                             # not held to the voices its entry kept after the trim (a speaker's line cut out, their voice dropped)
TAKE_SHOTS_READ = True       # C11: a looked-at take's `shots`, through `kept`: every shot on screen at least SHORTEST_SHOT, and
                             # the last clip's ending counted from them
STOOP_POSTURE = True         # C12: "stoop" is a posture word
if STOOP_POSTURE:  # the verb only: "the stoop" is a place (one film's stoop)
    POSTURE = POSTURE[:-len(r")\b")] + r"|stoops|stooping|stooped)\b"
# iteration 5's checks.py fixes that held their tests (tests/K in iter-5), each behind its own switch
FRAME_VIEW_NAMED = True      # K1a: a frame plate takes the view of the beat it was taken from only when that beat names a view
SUBJECT_ON = True            # K1b: a beat's subject is whoever its framing is "on" ("close-up on <A>, … looks at <B>": A); the other
                             # names in its framing count only when it has no "on"
TAIL_MEASURED = True         # K1c: a line with measured endSeconds in a looked-at take (`shots` written) has no line tail, as in a
                             # clip with `kept`
ENDING_FROM_END = True       # K2: C11's ending, counted from the last line's measured end, counts a looked-at shot that starts up to
                             # ENDING_TOLERANCE before that end, from the end on
DIARY_DAYS = True            # K4b: in the body diary, C7 reads a new "day <n>" / "night <n>" in stateIn as a time jump
BACK_JUMP_READ = True        # K4c: a jump back in time ("<n> days earlier", "the night before", "flashback") is a time jump too
DEPICTION_NOT_SHOWN = True   # K6: the posture scan reads no name or tag in a depiction's description (a photo, portrait, picture…)
WIDE_OPEN = True             # K7a: "wide" in "wide open" is no shot size
TO_FEET = True               # K7b: "to <their> feet" is a posture
LENGTH_TENTHS = True         # K8a: durationSeconds may carry a tenth when a clip's `kept` leaves the film so
ASKED = True                 # AD: the user's asks (script.json `asked`) replace the defaults the checks hold: the voice's words a
                             # minute (within ASKED_PACE, never above its kind's top rate) and text on screen (`asked.texts`)
ASKED_PACE = 0.15
# iteration 6's checks.py fixes that held their tests (tests/H in iter-6), each behind its own switch
SOURCE_IN_TAKE = True        # H1: a video part (an extension's source, a reference video) hears the lines its take speaks inside
                             # its `from`-`to`, those being the take's own seconds, read through the take's `kept` ranges
BACK_JUMP = (r"\b(?:hours?|days?|nights?|weeks?|months?|years?) (?:earlier|before)\b|\b(?:night|day|morning|evening|afternoon|week|"
             r"year) before\b|\bearlier (?:that|the same) (?:day|morning|night|evening|afternoon)\b|\b(?:previous|prior) (?:day|night|"
             r"morning|evening|afternoon|week)\b|\bflash(?:es)?[- ]?back\b|\b(?:hours?|days?|weeks?|months?|years?) ago\b")
if BACK_JUMP_READ:  # K4c: the seam check's time-jump gate and C7 read a jump back as they read one forward
    TIME_JUMP = TIME_JUMP + "|" + BACK_JUMP
if TO_FEET:  # K7b: "gets to her feet", "scrambles to their feet"
    POSTURE = POSTURE[:-len(r")\b")] + r"|to (?:his|her|its|their) feet)\b"
if WIDE_OPEN:  # K7a: "pushes the window wide open" names no shot size
    SHOT_SIZES = tuple((n, r"\bwide\b(?!\s+open)|\b(?:long|full) shot\b") if n == "wide" else (n, p) for n, p in SHOT_SIZES)
BODY_CROP = r"\b(?:from (?:the |his |her |its |their )?(?:chest|waist|hips?|knees?|thighs?|shoulders?|neck|torso|belly)[- ]up|" \
            r"(?:chest|waist|hip|knee|thigh|shoulder)[- ]up|(?:chest|waist|hip|knee|thigh)[- ](?:high|length) (?:shot|framing)|" \
            r"head[- ]and[- ]shoulders)\b"  # C8: a body crop
YOUTH = r"\b(child|children|kid|kids|boy|boys|girl|girls|teen|teens|teenage|teenager|adolescent|minor|underage|schoolboy|schoolgirl)\b"
OWNED = r"\b(minecraft|creeper|skibidi|tralalero|tralala|tung tung|sahur|bombardiro|roblox|fortnite|mario|pikachu|spongebob)\b"


def words(text):
    return len(text.split())


def found(text, pattern, flags=re.I):
    """Every distinct match with a few words around it, so a refusal says exactly what to fix."""
    hits = []
    for m in re.finditer(pattern, text, flags):
        snippet = re.sub(r"\s+", " ", text[max(0, m.start() - 40): m.end() + 30]).strip()
        if f'"…{snippet}…"' not in hits:
            hits.append(f'"…{snippet}…"')
    return ", ".join(hits[:6]) if hits else None


def location_budget(duration):
    return 1 if duration <= 60 else 4 if duration <= 120 else 5


BODY_SIDE = r"(?!\s+(?:hands?|arms?|fist|foot|feet|legs?|knee|elbow|ear|eyes?|cheek|thumb|fingers?|palm|glove|sleeve|pocket)\b)"
LATERAL = r"\b(left|right)\b(?!\s+(?:in|at|on|by|behind|beside|next|up|there|here|away|now|before|after|over|under|below|above)\b)" \
    + BODY_SIDE  # a side, not "right in front of" nor a hand


def sides_said(text, names):
    """Whether `positions` say who is on which side of whom: a side taken from a cast member ("at her right", "on Ernie's left",
    "to the right of Darlene"; "its" is left out, as it names a prop: "the bowl to its right"), or two of them on opposite sides of
    one thing ("Doris in front of the table's left half and Loretta in front of its right half"). names: the cast's first names,
    lower case."""
    flat = " ".join(str(text).lower().replace("’", "'").split())
    who = "|".join(re.escape(n) for n in names) or "(?!)"
    if re.search(rf"\b(?:at|on|to|beside|by|against)\s+(?:his|her|their|(?:{who})'s)\s+(?:left|right)\b" + BODY_SIDE, flat) or \
            re.search(rf"\b(?:left|right)\s+of\s+(?:him|her|them|{who})\b", flat) or \
            re.search(rf"\b(?:{who})'s\s+(?:left|right)\b" + BODY_SIDE, flat):
        return True
    marks = sorted((m.start(), n) for n in names for m in re.finditer(rf"\b{re.escape(n)}\b", flat))
    sides = {"left": set(), "right": set()}
    for i, (at, name) in enumerate(marks):  # each cast member's stretch: from their name to the next one's
        for m in re.finditer(LATERAL, flat[at:marks[i + 1][0] if i + 1 < len(marks) else len(flat)]):
            sides[m.group(1)].add(name)
    return any(a != b for a in sides["left"] for b in sides["right"])


# ---------- script ----------

BEAT = re.compile(r"^[A-Z][A-Z0-9 —–-]*\((\d+):(\d{2})\)$")
CLIP_MARK = re.compile(r"^— CLIP (\S+) \((\d+):(\d{2}(?:\.\d+)?)\s*[–-]\s*(\d+):(\d{2}(?:\.\d+)?)\) — (\S+) —$")


def is_cue(line):
    """A speaker cue: a name in capitals (any alphabet), with an optional (V.O.), (NARRATION) or (SUNG)."""
    name = re.sub(r"\s*\(.*\)$", "", line)
    return 2 <= len(name) <= 31 and any(c.isalpha() for c in name) and name == name.upper() \
        and all(c.isalpha() or c in " .'’-" for c in name)


def screenplay_parts(screenplay):
    """Stage directions, spoken lines in order, clip markers and beat headings, told apart by the layout of script-format.md."""
    directions, spoken, marks, beats, in_dialogue = [], [], [], [], False
    for raw in screenplay.split("\n"):
        line = raw.strip()
        if not line:
            in_dialogue = False
            continue
        if CLIP_MARK.match(line):
            marks.append(CLIP_MARK.match(line).groups())
            continue
        if BEAT.match(line):
            beats.append(int(BEAT.match(line).group(1)) * 60 + int(BEAT.match(line).group(2)))
            continue
        if re.match(r"^(TITLE|Runtime)\b", line) or re.match(r"^— CLIP\b", line) or re.match(r"^CUT TO BLACK\.?$", line):
            continue
        if is_cue(line):
            in_dialogue = True
            continue
        if re.match(r"^\(.*\)$", line):
            continue
        if in_dialogue:
            spoken.append(line)
            continue
        directions.append(line)
    return directions, spoken, marks, beats


def ending_second(screenplay):
    """The film second of the screenplay's ENDING heading ("ENDING (0:50)", "ACT 2 — ENDING (1:50)"), or None."""
    found = [int(m.group(1)) * 60 + int(m.group(2)) for m in (BEAT.match(x.strip()) for x in str(screenplay).split("\n"))
             if m and "ENDING" in m.group(0)]
    return found[-1] if found else None


def mmss(seconds):
    """A film second as a screenplay marker writes it: 0:18, 0:18.4, 1:05.25."""
    m, s = divmod(round(seconds, 2), 60)
    whole, part = int(s), round(s - int(s), 2)
    return f"{int(m)}:{whole:02d}" + (f"{part:.2f}".rstrip("0")[1:] if part else "")


def stage_directions(screenplay):
    return screenplay_parts(screenplay)[0]


def plain(text):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s']", " ", text.lower().replace("’", "'"))).strip()


def generations(clips, props=()):
    """Each clip's generation (references/clips.md): an original is 0; whatever a clip is made from adds 1, a frame plate and a
    prop sheet made from a clip's frames (its sheetFrom) included. A part of a clip is that clip's own take."""
    by_id, generation = {k.get("id"): k for k in clips}, {}
    sheet_from = {p.get("id"): p.get("sheetFrom") for p in props if p.get("sheetFrom")}

    def gen(kid, path=()):
        if kid in generation:
            return generation[kid]
        k = by_id.get(kid)
        if k is None or kid in path:
            return 0
        if k.get("make") == "part":
            generation[kid] = gen(k.get("of"), path + (kid,))
            return generation[kid]
        g = 0
        if k.get("make") == "extend" and k.get("source", {}).get("clip") in by_id:
            g = gen(k["source"]["clip"], path + (kid,)) + 1
        for v in k.get("videos", []):
            if v.get("clip") in by_id:
                g = max(g, gen(v["clip"], path + (kid,)) + 1)
        for im in k.get("images", []):
            m = FRAME.match(im)
            source = m.group(1) if m else sheet_from.get(im)
            if source in by_id:
                g = max(g, gen(source, path + (kid,)) + 1)
        generation[kid] = g
        return g

    for k in clips:
        gen(k.get("id"))
    return generation


def kept_ranges(k):
    """`kept` is one {"from", "to"} range or a list of them, in order (references/clips.md, The clip entry)."""
    kept = k.get("kept")
    return [] if not kept else kept if isinstance(kept, list) else [kept]


def take_of(k):
    """The clip whose take an entry shows: a part's `of`, else the entry itself."""
    return k.get("of") if k.get("make") == "part" else k.get("id")


def windows(s, kid):
    """The film windows of clip kid's take: its own entry and every part of it, each as (film start, from, to) per kept range,
    `from` and `to` in the take's own seconds (a clip without `kept` shows its first end - start seconds)."""
    out = []
    for k in s.get("clips", []):
        if take_of(k) != kid:
            continue
        t = k.get("start", 0)
        for g in kept_ranges(k) or [{"from": 0, "to": k.get("end", 0) - k.get("start", 0)}]:
            out.append((t, g.get("from", 0), g.get("to", 0)))
            t += g.get("to", 0) - g.get("from", 0)
    return out


def to_clip(spans, second):
    """A film second in the take's own seconds, or None when the film does not show the take then."""
    return next((a + second - t for t, a, b in spans if t - 0.001 <= second <= t + b - a + 0.001), None)


def check_clips(s):
    r, clips = [], s.get("clips", [])
    by_id = {k.get("id"): k for k in clips}
    locations = {l.get("id") for l in s.get("locations", [])}
    plates = {l.get("id"): len(l.get("plates") or [None]) for l in s.get("locations", [])}
    cast = {c.get("id") for c in s.get("cast", [])}
    props = {p.get("id") for p in s.get("props", [])}
    forms = {f.get("id") for f in s.get("forms", [])}
    groups = {g.get("id") for g in s.get("groups", [])}
    sheet_from = {p.get("id"): p.get("sheetFrom") for p in s.get("props", []) + s.get("forms", []) if p.get("sheetFrom")}
    length = {k.get("id"): k.get("end", 0) - k.get("start", 0) for k in clips}
    # a clip's own generation: `generated` seconds, else the end of its last kept range, else its length in the film
    made = {k.get("id"): k.get("generated") or max([g.get("to", 0) for g in kept_ranges(k)] or [length[k.get("id")]]) for k in clips}
    made.update({k.get("id"): made[k.get("of")] for k in clips if k.get("make") == "part" and k.get("of") in made})
    if not clips:
        return ["the script has no clips"]
    t = 0
    for k in clips:
        if k.get("start") != t:
            r.append(f'clip {k.get("id")} starts at {k.get("start")}s; the clip before it ends at {t}s (no gap, no overlap)')
        kept = kept_ranges(k)
        if k.get("make") == "part" and not kept:
            r.append(f'clip {k.get("id")} is a part of {k.get("of")}: write its kept range(s), in the seconds of {k.get("of")}\'s take')
        elif kept:
            total = sum(g.get("to", 0) - g.get("from", 0) for g in kept)
            if abs(total - length[k.get("id")]) > 0.05:
                spans = ", ".join(f'{g.get("from")}-{g.get("to")}' for g in kept)
                r.append(f'clip {k.get("id")}: kept {spans}s add up to {total:g}s, not its {round(length[k.get("id")], 2):g}s in the film')
        elif not CLIP_SECONDS[0] <= length[k.get("id")] <= CLIP_SECONDS[1]:
            r.append(f'clip {k.get("id")} is {length[k.get("id")]}s; a clip is {CLIP_SECONDS[0]}-{CLIP_SECONDS[1]}s')
        if k.get("location") not in locations:
            r.append(f'clip {k.get("id")}: location {k.get("location")} is not a location id')
        t = k.get("end", t)
    if t != s.get("durationSeconds"):
        r.append(f'the clips end at {t}s; the film is {s.get("durationSeconds")}s')
    for f in s.get("forms", []):
        if f.get("of") not in cast and f.get("of") not in props:
            r.append(f'form {f.get("id")}: "of" {f.get("of")} is not a cast or prop id')
        if f.get("sheetFrom") is not None and f.get("sheetFrom") not in by_id:
            r.append(f'form {f.get("id")}: sheetFrom {f.get("sheetFrom")} is not a clip id')

    gen = generations(clips, s.get("props", []) + s.get("forms", [])).get
    deepest = MAX_GENERATION.get(s.get("resolution", "480p"), 1)

    for k in clips:
        kid, n = k.get("id"), length[k.get("id")]
        video_seconds, video_count = 0, 0
        if k.get("make") == "extend":
            src = k.get("source", {})
            if src.get("clip") not in by_id or src.get("clip") == kid:
                r.append(f'clip {kid}: the source {src.get("clip")} is not another clip')
            else:
                if not 0 <= src.get("from", -1) < src.get("to", -1) <= made[src["clip"]] or src["to"] - src["from"] < 2:
                    r.append(f'clip {kid}: source part {src.get("from")}-{src.get("to")}s must lie inside {src["clip"]} (0-{made[src["clip"]]}s) and last at least 2s')
                video_seconds += src.get("to", 0) - src.get("from", 0)
                video_count += 1
            if k.get("direction") not in ("forward", "backward"):
                r.append(f'clip {kid}: direction must be forward or backward')
        elif k.get("make") == "part":  # the rest of a clip's take after a remake placed inside it (clips.md, Cutting the film)
            of = by_id.get(k.get("of"))
            if of is None or k.get("of") == kid or of.get("make") == "part":
                r.append(f'clip {kid}: "of" {k.get("of")} is not another clip: a part shows more of one clip\'s take')
            elif any(not 0 <= g.get("from", -1) < g.get("to", -1) <= made[kid] for g in kept_ranges(k)):
                r.append(f'clip {kid}: its kept ranges must lie inside {k["of"]}\'s take (0-{made[kid]}s)')
            extra = [f for f in ("images", "videos", "voices", "track", "source", "generated", "shots") if k.get(f)]
            if extra:
                r.append(f"clip {kid} is a part of {k.get('of')}: it is cut from that take, not generated; its {', '.join(extra)} "
                         f"stay in {k.get('of')}'s entry")
            continue
        elif k.get("make") != "fresh":
            r.append(f'clip {kid}: make must be fresh, extend or part')
        for v in k.get("videos", []):
            if v.get("clip") not in by_id or v.get("clip") == kid:
                r.append(f'clip {kid}: reference video {v.get("clip")} is not another clip')
                continue
            if gen(v["clip"]) != 0:
                r.append(f'clip {kid}: reference video {v["clip"]} is generation {gen(v["clip"])}; a reference video is always an original (generation 0)')
            if not 0 <= v.get("from", -1) < v.get("to", -1) <= made[v["clip"]] or v["to"] - v["from"] < 2:
                r.append(f'clip {kid}: reference part {v.get("from")}-{v.get("to")}s must lie inside {v["clip"]} and last at least 2s')
            video_seconds += v.get("to", 0) - v.get("from", 0)
            video_count += 1
        if video_count > MAX_VIDEOS:
            r.append(f"clip {kid} sends {video_count} videos; at most {MAX_VIDEOS}")
        if video_seconds > min(MAX_VIDEO_SECONDS, made[kid]):
            r.append(f"clip {kid} sends {video_seconds}s of video; at most {min(MAX_VIDEO_SECONDS, made[kid])}s (30s and the clip's own generated length): trim it")
        images = k.get("images", [])
        sent = sum(plates.get(im, 1) for im in images)
        if sent > MAX_IMAGES:
            r.append(f"clip {kid} sends {sent} images (a 2D location sends each of its plates); at most {MAX_IMAGES}")
        for im in sorted({im for i, im in enumerate(images) if im in images[:i]}):
            r.append(f'clip {kid} sends "{im}" twice' + (f': a second edit of one frame is another image and takes a tag, "{im}/<tag>" '
                     "(frame:k1@0.3/morning)" if FRAME.match(im) else ""))
        for im in images:
            m = FRAME.match(im)
            if m:
                if m.group(1) not in by_id or take_of(by_id[m.group(1)]) == kid or not 0 <= float(m.group(2)) <= made[m.group(1)]:
                    r.append(f'clip {kid}: frame "{im}" is not a second inside another clip (the second counts from that '
                             "clip's first frame, never the film's)")
            elif PLATE.match(im):
                loc, n = PLATE.match(im).groups()
                if loc not in locations or not 1 <= int(n) <= plates.get(loc, 1):
                    r.append(f'clip {kid}: "{im}" is not a plate of a location (<location id>#<plate number from 1>)')
            elif im in sheet_from and sheet_from[im] == kid:
                r.append(f"clip {kid}: {im}'s sheet is made from this clip's own frames; it exists only after the clip")
            elif im in groups:
                r.append(f'clip {kid}: "{im}" is a group: a group has no sheet; the prompt writes it (clips.md, A crowd)')
            elif im not in locations and im not in cast and im not in props and im not in forms:
                r.append(f'clip {kid}: image "{im}" is not a location id, a plate (<location>#<n>), a cast id, a prop id or '
                         'frame:<clip>@<second>[/<tag>]')
        if gen(kid) > deepest:
            r.append(f"clip {kid} is generation {gen(kid)}; at {s.get('resolution', '480p')} at most {deepest}: make it fresh from the sheets, or take its sources from lower generations")
        # a looked-at take's shots: each measured shot's seconds in the take and its framing as seen (clips.md, The clip entry)
        shots, at = k.get("shots"), 0
        for sh in shots if isinstance(shots, list) else [] if shots is None else [None]:
            if not isinstance(sh, dict) or not isinstance(sh.get("from"), (int, float)) or not isinstance(sh.get("to"), (int, float)) \
                    or not str(sh.get("framing", "")).strip():
                r.append(f'clip {kid}: shots is a list of {{"from", "to", "framing"}}, each measured shot\'s seconds in the take and its '
                         'framing as seen ("medium-wide on Tess and Philo, the view of @Image1")')
                break
            if not at - 0.05 <= sh["from"] < sh["to"] <= made[kid] + 0.05:
                r.append(f'clip {kid}: shot {sh["from"]:g}-{sh["to"]:g} s must come after the shot before it and lie inside the take '
                         f'(0-{made[kid]:g} s), in the take\'s own seconds')
                break
            at = sh["to"]
        # who is on which side of whom (clips.md, The clip entry): one film's plant, whose side k4's positions left out, switched sides
        names = {plain(c.get("name", "")).split()[0]: c.get("name", "").split()[0] for c in s.get("cast", []) if plain(c.get("name", ""))}
        here = [n for n in names if re.search(rf"\b{re.escape(n)}\b", plain(k.get("positions", "")))]
        if SIDES_REFUSED and len(here) >= 2 and not sides_said(k.get("positions", ""), list(names)):
            r.append(f'clip {kid}: its positions place {" and ".join(names[n] for n in here)} but never say who is on which side of '
                     'whom: write it from a character ("<name> stands at <her> right", "<name> left of <name>"), and keep it across '
                     "clips unless a clip shows someone cross (clips.md, The clip entry: a plant whose side one clip's positions left out "
                     "switched sides in the last shot)")
        # C11: a looked-at take's shots, through `kept`, each on screen at least SHORTEST_SHOT (clips.md, Cutting the film into clips)
        if TAKE_SHOTS_READ and k.get("make") != "part" and take_shots(k):
            for a, b, framed, shown in on_screen(s, k):
                if 0.05 < shown < SHORTEST_SHOT - 0.01:
                    r.append(f'clip {kid}: its take, as looked at, shows the shot {a:g}-{b:g} s ("{framed[:50]}") for {shown:.2f} s in the '
                             f"film: a shot lasts at least {SHORTEST_SHOT:g} s on screen; trim it out through `kept` where it carries no "
                             "word and the beats around it hold, else remake that beat as a clip of its own (clips.md, Cutting the film "
                             "into clips: one ending's last shot came out 1.46 s, cut mid-action)")
    return r


def on_screen(s, k):
    """C11: each shot of clip k's take (its `shots`) with the seconds the film shows of it, through the `kept` ranges of the entry and
    of every part of the take: (from, to, framing, seconds on screen)."""
    spans = windows(s, k.get("id"))
    return [(a, b, framed, sum(max(0.0, min(b, y) - max(a, x)) for _, x, y in spans)) for a, b, framed in take_shots(k) or []]


def check_voices(s):
    """A clip in which a character speaks hears them: it is their voice clip, a video part it sends holds one of their lines, or it
    carries their voice sample (references/clips.md, Voices)."""
    r, clips, fmt = [], s.get("clips", []), s.get("format", "dialogue")
    lines = [l for l in s.get("lines", []) if l.get("kind", "dialogue") in ("dialogue", "thought")]
    narrators = {l.get("speaker") for l in s.get("lines", []) if l.get("kind") in ("narration", "sung")}
    cast = {c.get("id") for c in s.get("cast", [])}
    by_id = {k.get("id"): k for k in clips}
    gen, order = generations(clips, s.get("props", []) + s.get("forms", [])), {k.get("id"): i for i, k in enumerate(clips)}
    first = {c.get("id"): c["voiceFrom"] for c in s.get("cast", []) if c.get("voiceFrom")}
    take = {k.get("id"): take_of(k) for k in clips}  # a part's lines are its clip's take
    for k in sorted(clips, key=lambda k: (gen.get(k.get("id"), 0), order[k.get("id")])):
        for l in lines:
            if take.get(l.get("clip")) == k.get("id") and l.get("speaker") not in narrators:
                first.setdefault(l.get("speaker"), k.get("id"))

    def heard(part, speaker):
        k = by_id.get(part.get("clip"))
        if k is None:
            return False
        if SOURCE_IN_TAKE:  # H1: `from`-`to` are seconds of the clip's take; a line is placed in the take through its `kept` ranges
            kid = take_of(k)
            spans = windows(s, kid)
            said = (to_clip(spans, l.get("startSeconds", -1)) for l in lines
                    if l.get("speaker") == speaker and take.get(l.get("clip")) == kid)
            return any(t is not None and part.get("from", 0) <= t < part.get("to", 0) for t in said)
        a, b = k.get("start", 0) + part.get("from", 0), k.get("start", 0) + part.get("to", 0)
        return any(l.get("speaker") == speaker and l.get("clip") == k.get("id") and a <= l.get("startSeconds", -1) < b for l in lines)

    for k in clips:
        kid, voices = k.get("id"), k.get("voices", [])
        if k.get("make") == "part":
            continue
        speakers = {l.get("speaker") for l in lines if take.get(l.get("clip")) == kid}
        track = k.get("track")
        part = (track.get("to", 0) - track.get("from", 0)) if track else 0
        if track and fmt not in NARRATED:
            r.append(f"clip {kid}: a track part belongs only to a narrated format (formats.md); this film is {fmt}")
        if track and not 2 <= part <= 30:
            r.append(f"clip {kid}: its part of the track is {part}s; an audio reference is 2-30s")
        if len(voices) + bool(track) > MAX_AUDIOS:
            r.append(f"clip {kid} sends {len(voices) + bool(track)} audio references; at most {MAX_AUDIOS}")
        if voices and part + 3 * len(voices) > 30:
            r.append(f"clip {kid}: its track part ({part}s) and {len(voices)} voice samples of at least 3s pass 30s of audio")
        for v in voices:
            if v not in cast:
                r.append(f'clip {kid}: voice "{v}" is not a cast id')
            elif v not in speakers:
                r.append(f"clip {kid}: {v} does not speak in this clip; take their voice out of its voices")
            elif first.get(v) == kid:
                r.append(f"clip {kid} is {v}'s voice clip (the first made of their clips): it makes that voice, so {v} is not in its voices")
        parts = ([k["source"]] if k.get("make") == "extend" and k.get("source") else []) + k.get("videos", [])
        for sp in sorted(x for x in speakers if x in cast):
            if first.get(sp) == kid or sp in voices or any(heard(p, sp) for p in parts):
                continue
            source = "the narration track" if sp in narrators else f"their voice clip {first[sp]}"
            r.append(f"clip {kid}: {sp} speaks but is not heard in its videos; put {sp} in its voices (the sample comes from {source})")
    return r


def check_script(s, faces=0):
    r, cast = [], s.get("cast", [])
    ids = {c["id"] for c in cast}
    duration = s.get("durationSeconds")
    # K8a: a film whose `kept` trims leave it a fraction of a second over is that length, to a tenth (no second trim to a whole second)
    tenths = LENGTH_TENTHS and isinstance(duration, float) and any(k.get("kept") for k in s.get("clips", [])) \
        and abs(duration * 10 - round(duration * 10)) < 1e-6
    if not (isinstance(duration, int) or tenths) or duration < CLIP_SECONDS[0]:
        whole = "a whole number of seconds" + (" (a tenth when a clip's `kept` leaves the film so)" if LENGTH_TENTHS else "")
        return [f"durationSeconds must be {whole}, at least {CLIP_SECONDS[0]}; got {duration}"]
    fmt = s.get("format", "dialogue")
    if fmt not in FORMATS:
        r.append(f'format "{fmt}" is not one of {", ".join(FORMATS)} (formats.md)')
    diary = fmt == "inside-body" and any(l.get("kind") == "narration" for l in s.get("lines", []))
    smallest = 1 if diary else CAST_SIZE[0]
    if not smallest <= len(cast) <= CAST_SIZE[1]:
        r.append(f"cast has {len(cast)} characters; it must have {smallest}-{CAST_SIZE[1]}")
    if not str(s.get("style", "")).strip():
        r.append("style is missing: one line for the film's look (styles.md)")
    if not str(s.get("template", "")).strip():
        r.append("template is missing: the id of the film's style template (styles.md)")
    if s.get("aspectRatio", "9:16") not in ASPECT_RATIOS:
        r.append(f'aspectRatio "{s.get("aspectRatio")}" is not one of {", ".join(ASPECT_RATIOS)}')
    if s.get("template") in NOT_480P and s.get("resolution", "480p") == "480p":
        r.append(f'{s.get("template")} renders at 1080p (720p at the least): at 480p its wide shots smear (styles/{s.get("template")}.md)')
    if s.get("resolution", "480p") not in MAX_GENERATION:
        r.append(f'resolution "{s.get("resolution")}" is not one of {", ".join(MAX_GENERATION)}')
    for c in cast:
        if c.get("kind") == "human":
            if not isinstance(c.get("age"), int) or c["age"] < 18:
                r.append(f'{c.get("name")}: a human character\'s age must be a whole number of 18 or more, got {c.get("age")}')
            if c.get("gender") not in ("woman", "man"):
                r.append(f'{c.get("name")}: a human character\'s gender must be woman or man, got {c.get("gender")}')
        elif c.get("kind") == "other":
            if not str(c.get("form", "")).strip():
                r.append(f'{c.get("name")}: a non-human character needs its form (what it is)')
            if c.get("age") is not None and (not isinstance(c["age"], int) or c["age"] < 18):
                r.append(f'{c.get("name")}: drop the age, or give a whole number of 18 or more; no character is a child')
        else:
            r.append(f'{c.get("name")}: kind must be human or other, got {c.get("kind")}')
        if "wordsPerSecond" in c and not (isinstance(c["wordsPerSecond"], (int, float)) and
                                          SPOKEN_RATES[0] <= c["wordsPerSecond"] <= SPOKEN_RATES[1]):
            r.append(f'{c.get("name")}: wordsPerSecond {c["wordsPerSecond"]} is not a speaking rate ({SPOKEN_RATES[0]:g}-'
                     f'{SPOKEN_RATES[1]:g}): the words of their lines in their voice clip over those lines\' seconds, first word to '
                     "last (script-format.md)")
        fi = c.get("faceImage")
        if fi is not None and not (0 <= fi < faces):
            r.append(f'{c.get("name")}: faceImage {fi} does not exist')
    locations = s.get("locations", [])
    budget = 4 if fmt in ("storytime", "song") else location_budget(duration)
    if not 1 <= len(locations) <= budget:
        r.append(f"the film has {len(locations)} locations; a {duration}s {fmt} film has 1-{budget}")
    r += check_clips(s)
    r += check_voices(s)
    by_id = {k.get("id"): k for k in s.get("clips", [])}
    lines = s.get("lines", [])
    count = {kind: sum(words(l["text"]) for l in lines if l.get("kind", "dialogue") in kinds)
             for kind, kinds in (("spoken", ("dialogue", "thought")), ("narration", ("narration",)), ("sung", ("sung",)))}
    span = lambda rate: (round(duration * rate[0] / 60), round(duration * rate[1] / 60))
    song = "elevenlabs_music_v2" if (s.get("narrator") or {}).get("voiceId") == "elevenlabs_music_v2" else "seed_audio"
    asked = (s.get("asked") or {}) if ASKED else {}
    pace = asked.get("wordsPerMinute")
    if ASKED:
        r += check_asked(s, asked, duration)
    paced = isinstance(pace, (int, float)) and not isinstance(pace, bool) and pace > 0
    # AD: an asked pace holds the film's voice, its narration or else its dialogue, within ASKED_PACE, under its kind's top rate
    asked_span = lambda top: (round(duration * pace * (1 - ASKED_PACE) / 60),
                              min(round(duration * pace * (1 + ASKED_PACE) / 60), round(duration * top / 60)))
    for kind, rate in (("narration", NARRATION_PER_MINUTE), ("sung", SUNG_PER_MINUTE[song])):
        bounds = asked_span(rate[1]) if paced and kind == "narration" else span(rate)
        if count[kind] and not bounds[0] <= count[kind] <= bounds[1]:
            why = f" at the asked {pace:g} words a minute" if paced and kind == "narration" else ""
            r.append(f"the film has {count[kind]} {kind} words; a {duration}s film{why} has {bounds[0]}-{bounds[1]}")
    low, high = span(WORDS_PER_MINUTE)
    talk = sum(max(0.0, k["end"] - k["start"] - LINE_TAIL) for k in s.get("clips", [])) - HOOK_ACTION
    low = round(max(0.0, talk) * WORDS_PER_MINUTE[0] / 60)
    if count["narration"] or count["sung"]:
        low = 0
    elif paced:
        low, high = asked_span(WORDS_PER_MINUTE[1])
    if not low <= count["spoken"] <= high:
        if paced and not (count["narration"] or count["sung"]):
            r.append(f"dialogue is {count['spoken']} words; a {duration}s film at the asked {pace:g} words a minute has {low}-{high}")
        else:
            r.append(f"dialogue is {count['spoken']} words; a {duration}s film with {max(0.0, talk):g}s of talk time (each clip less "
                     f"its {LINE_TAIL}s tail, less the hook's {HOOK_ACTION}s) has {low}-{high}")
    previous, misplaced = -1, set()
    for l in lines:
        kind = l.get("kind", "dialogue")
        if kind not in MAX_LINE_WORDS:
            r.append(f'line "{l["text"][:40]}": kind {kind} is not dialogue, thought, narration or sung')
            continue
        if kind in ("narration", "sung") and kind not in NARRATED.get(fmt, ()):
            misplaced.add(kind)
        if l["speaker"] not in ids and not (l["speaker"] == "narrator" and kind == "narration" and diary):
            r.append(f'line "{l["text"][:40]}": speaker {l["speaker"]} is not a cast id')
        if l["startSeconds"] < previous:
            r.append(f'lines are not in time order at {l["startSeconds"]}s')
        previous = l["startSeconds"]
        most = MAX_LINE_WORDS[kind]
        if words(l["text"]) > most:
            r.append(f'line "{l["text"][:50]}" has {words(l["text"])} words; a {kind} line has at most {most}: split it' + (" into two lines with a visible action between them" if kind in ("dialogue", "thought") else ""))
        k = by_id.get(l.get("clip"))
        if k is None:
            r.append(f'line "{l["text"][:40]}": clip {l.get("clip")} is not a clip id')
            continue
        rate = speaking_rate(s, l["speaker"])
        end = l["startSeconds"] + words(l["text"]) / rate
        if not k["start"] <= l["startSeconds"] < k["end"]:
            r.append(f'line at {l["startSeconds"]}s is not inside its clip {k["id"]} ({k["start"]}-{k["end"]}s)')
        elif kind in ("dialogue", "thought") and not k.get("kept") and end > k["end"] - LINE_TAIL and not (
                TAIL_MEASURED and take_shots(k) and isinstance(l.get("endSeconds"), (int, float))):  # K1c: measured in a looked-at take
            whose = ", its speaker's rate measured on their voice clip" if rate != SPOKEN_RATE else ""
            r.append(f'line "{l["text"][:40]}" runs to {end:.1f}s (its words at {rate:g} a second{whose}); speech in clip '
                     f'{k["id"]} must end by {k["end"] - LINE_TAIL}s')
    for kind in sorted(misplaced):
        r.append(f"{kind} lines belong only to the formats that have them (formats.md); this film is {fmt}")
    if lines and lines[-1]["startSeconds"] > duration - LAST_LINE_GAP:
        r.append(f'the last spoken line starts at {lines[-1]["startSeconds"]}s; it must start by {duration - LAST_LINE_GAP}s')
    screenplay = s.get("screenplay", "")
    parts, spoken, marks, beats = screenplay_parts(screenplay)
    directions = "\n".join(parts)
    said = [plain(t) for t in spoken]
    planned = [plain(l.get("text", "")) for l in lines]
    if " ".join(said) != " ".join(planned):
        at = next((i for i, (a, b) in enumerate(zip(said, planned)) if a != b), min(len(said), len(planned)))
        got = spoken[at] if at < len(spoken) else "(nothing)"
        want = lines[at]["text"] if at < len(lines) else "(nothing)"
        r.append(f'the screenplay and lines differ at line {at + 1}: the screenplay says "{got[:50]}", lines say "{want[:50]}" (the same dialogue twice)')
    if beats != sorted(beats):
        r.append(f"beat headings are out of time order: {beats}")
    locations_by_id = {l.get("id") for l in s.get("locations", [])}
    for kid, m1, s1, m2, s2, loc in marks:
        k = by_id.get(kid)
        if k is None:
            r.append(f"the screenplay marks clip {kid}, which is not in clips")
        elif abs(int(m1) * 60 + float(s1) - k.get("start", 0)) > 0.05 or abs(int(m2) * 60 + float(s2) - k.get("end", 0)) > 0.05 or loc != k.get("location"):
            r.append(f"the screenplay's marker for {kid} ({m1}:{s1}-{m2}:{s2}, {loc}) disagrees with clips ({k.get('start')}-{k.get('end')}s, "
                     f"{k.get('location')}): write it \"— CLIP {kid} ({mmss(k.get('start', 0))}–{mmss(k.get('end', 0))}) — {k.get('location')} —\"")
        if loc not in locations_by_id:
            r.append(f"the screenplay's marker for {kid} names location {loc}, which is not in locations")
    if len(marks) != len(s.get("clips", [])):
        r.append(f"the screenplay has {len(marks)} clip markers; clips has {len(s.get('clips', []))}")
    talk = [l for l in lines if l.get("kind", "dialogue") in ("dialogue", "thought")]
    if talk and talk[0]["startSeconds"] < HOOK_ACTION:
        r.append(f"the first line starts at {talk[0]['startSeconds']}s; the hook's action lands first: start it at {HOOK_ACTION}s or later")
    track = (s.get("narrator") or {}).get("trackSeconds")
    if track is not None:
        if track > duration:
            r.append(f"the narration track runs {track}s, past the {duration}s film: speed it up, shorten its pauses or cut words (formats.md)")
        late = [l for l in lines if l.get("kind") in ("narration", "sung") and l["startSeconds"] >= track]
        if late:
            r.append(f'narration line "{late[0]["text"][:40]}" starts at {late[0]["startSeconds"]}s, after the {track}s track ends')
        sung = [l for l in lines if l.get("kind") == "sung"]
        unmeasured = [l for l in sung if not isinstance(l.get("endSeconds"), (int, float))]
        if unmeasured:
            r.append(f'sung line "{unmeasured[0]["text"][:40]}" has no endSeconds: once the song is made, every sung line takes its '
                     "start and end from the song's word times (formats.md, Sung story)")
        elif sung:
            if sung[0]["startSeconds"] > SONG_INTRO:
                r.append(f"the first sung word comes at {sung[0]['startSeconds']}s: cut the song's intro so it starts by {SONG_INTRO}s "
                         "(a film opened on 10 seconds with no word)")
            if duration - sung[-1]["endSeconds"] > SONG_OUTRO:
                r.append(f"the singing ends at {sung[-1]['endSeconds']}s of a {duration}s film: end the film within {SONG_OUTRO}s of "
                         "the last sung word, or make the song again")
            clips = s.get("clips", [])
            for i, k in enumerate(clips[1:], 1):
                cut = k.get("start", 0)
                inside = next((l for l in sung if l["startSeconds"] < cut - 0.1 and l["endSeconds"] > cut + 0.1), None)
                # a remake set inside a clip cuts where that take's own shots cut, inside a line or not (clips.md): the cut into
                # a part, and into the remake that sits before a part of the clip before it
                remake = i + 1 < len(clips) and clips[i + 1].get("make") == "part" and clips[i + 1].get("of") == take_of(clips[i - 1])
                if inside and k.get("make") != "part" and not remake:
                    r.append(f'the cut into clip {k.get("id")} at {cut}s falls inside the sung line "{inside["text"][:40]}" '
                             f'({inside["startSeconds"]}-{inside["endSeconds"]}s): cut between two lines or on a first word')
            for k in s.get("clips", []):
                a, b = k.get("start", 0), k.get("end", 0)
                cuts = [l["startSeconds"] for l in sung if a + SUNG_SPLIT <= l["startSeconds"] <= b - SUNG_SPLIT]
                if b - a > SUNG_CLIP and cuts:
                    c = min(cuts, key=lambda x: abs(x - (a + b) / 2))
                    r.append(f'clip {k.get("id")} runs {round(b - a, 2):g}s; a sung line starts at {c}s: cut it there into {round(c - a, 2):g}s and '
                             f'{round(b - c, 2):g}s (formats.md, Sung story: windows rounded to whole seconds gave one film a 21-second clip '
                             'beside a 7-second one)')
    # a narration line may carry endSeconds, its last word's end on the fitted track: `checks.py clip` prints its window to it
    told = [l for l in lines if l.get("kind") == "narration"]
    for i, l in enumerate(told):
        b, nxt = l.get("endSeconds"), told[i + 1]["startSeconds"] if i + 1 < len(told) else (track or duration)
        if b is not None and (not isinstance(b, (int, float)) or not l["startSeconds"] < b <= nxt + 0.05):
            r.append(f'narration line "{l["text"][:40]}": endSeconds {b} must fall after its start ({l["startSeconds"]}s) and by '
                     f"{'the next line' if i + 1 < len(told) else 'the end of the track'} ({nxt}s): it is the end of its last word "
                     "on the fitted track (formats.md)")
    similes = found(directions, r"\b(like a|like an|like the|like his|like her|like it|like someone|as if|as though|resembl\w+)\b")
    if similes:
        r.append(f"stage directions describe only what the camera sees, with no simile or comparison; found {similes}")
    narrator = found(screenplay, r"\b(RECAP)\b" if diary else r"\b(NARRATOR|RECAP)\b", 0)
    if narrator:
        r.append(f"no narrator or recap (a cast member's (V.O.) thought line is allowed); found {narrator}")
    cards = found(screenplay, r"\b(TITLE CARD|TEXT CARD|SUPER:|ON[- ]SCREEN TEXT|CAPTION:)") or found(screenplay, r"\bTHE END\b", 0)
    if cards:
        r.append(f"no title cards, captions or on-screen text; found {cards}" + (
            "; text the user asks to see goes in `asked.texts` and is laid over the film at assembly (script-format.md), never in "
            "the screenplay" if ASKED else ""))
    return r


def check_asked(s, asked, duration):
    """AD: script.json `asked`, the settings the user asked for in place of the skill's defaults (script-format.md)."""
    r = []
    if not isinstance(asked, dict):
        return ["asked must be an object: from, wordsPerMinute, texts (script-format.md)"]
    unknown = sorted(set(asked) - {"from", "wordsPerMinute", "texts"})
    if unknown:
        r.append(f"asked holds {unknown}; it holds from, wordsPerMinute and texts only (script-format.md)")
    if (asked.get("wordsPerMinute") is not None or asked.get("texts")) and not str(asked.get("from") or "").strip():
        r.append("asked.from is empty: write where each asked setting comes from, the user's words quoted or what their reference "
                 "measured; nothing goes in asked that they did not ask for")
    pace = asked.get("wordsPerMinute")
    if pace is not None and (isinstance(pace, bool) or not isinstance(pace, (int, float)) or pace <= 0):
        r.append(f"asked.wordsPerMinute is {pace!r}; it is a number of words a minute")
    texts = asked.get("texts") or []
    if not isinstance(texts, list):
        return r + ["asked.texts must be a list of {text, start, end, over}"]
    for i, t in enumerate(texts, 1):
        if not isinstance(t, dict) or not str(t.get("text") or "").strip():
            r.append(f"asked.texts {i}: write its exact words in text")
            continue
        a, b = t.get("start"), t.get("end")
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b)) or not 0 <= a < b <= duration:
            r.append(f'asked.texts {i} ("{t["text"][:30]}"): start and end are film seconds, 0 <= start < end <= {duration}')
        if t.get("over") not in ("picture", "black"):
            r.append(f'asked.texts {i} ("{t["text"][:30]}"): over is picture or black')
    return r


def check_plan(p, s):
    r, items = [], p.get("items", [])
    duration = s.get("durationSeconds", 0)
    by_id = {k.get("id"): k for k in s.get("clips", [])}
    most = 5 + max(0, (duration - 60) // 60)
    if not 3 <= len(items) <= most:
        r.append(f"the plan has {len(items)} items; a {duration}s film needs 3-{most}")
    for i, it in enumerate(items, 1):
        k = by_id.get(it.get("clip"))
        if k is None:
            r.append(f'item {i}: clip {it.get("clip")} is not a clip id')
        elif not k["start"] <= it["second"] < k["end"]:
            r.append(f'item {i}: second {it["second"]} is not inside clip {k["id"]} ({k["start"]}-{k["end"]}s)')
        if i > 1 and it["second"] < items[i - 2]["second"]:
            r.append(f"item {i} is out of story order")
        if re.search(r'"[^"]{3,}"', it.get("proof", "")):
            r.append(f"item {i}: the proof quotes dialogue; a proof is a shot that shows the point without words")
        if not re.search(r"\b(insert|close|extreme_close|medium|wide|full|over the shoulder|top-down|overhead)\b", it.get("proof", ""), re.I):
            r.append(f"item {i}: name the proof shot's framing (insert, close, medium, wide…)")
    if not any(it["second"] <= 10 for it in items):
        r.append("the first item (who the protagonist is and what they want) must land within the first 10 seconds")
    if not items or items[-1]["second"] < duration - 10:
        r.append(f"the last item must be the ending, at {duration - 10} seconds or later")
    return r


def check_effects(e, s):
    r, ids = [], {c["id"] for c in s.get("cast", [])}
    for fx in e.get("effects", []):
        if fx.get("owner") not in ids:
            r.append(f'effect "{fx.get("name")}": owner {fx.get("owner")} is not a cast id')
        for w in fx.get("words", []):
            if re.fullmatch(r"(nose|eyes?|hands?|skin|face|fingers?|teeth|hair)", w.strip(), re.I):
                r.append(f'effect "{fx.get("name")}": "{w}" names something ordinary; use distinctive words')
    return r


# ---------- images ----------

LABEL = r'Its label reads exactly "[^"]+".*no other text'  # the user's own product's closing sentence (style-master.md, Prop sheets)


def labelled(prompt):
    """C3: whether an image prompt ends with the user's product label sentence in place of the no-text sentence."""
    return LABEL_ENDING and bool(re.search(LABEL, prompt, re.S))


def check_sheet(prompt, photo=False, stylized=False, drawn=False, styled=False):
    r = check_names(prompt)
    scanned = re.sub(r'Its label reads exactly "[^"]+".*?no other text', "", prompt, flags=re.S) if labelled(prompt) else prompt
    negated = found(scanned.replace("No text, labels, logos or watermarks", ""), r"\b(no|without)\s+(?!text\b)[a-z]+", re.I)
    if negated:
        r.append(f"the image model draws every noun it reads: say what is there, never what is not; found {negated}")
    ages = [int(a or b) for a, b in re.findall(r"\b(\d{1,3})[- ]+(?:years?[- ]+old|y/?o)\b|\b(?:aged?|age of)\s*:?\s*(\d{1,3})\b", prompt, re.I)]
    if any(a < 18 for a in ages):
        r.append("every age in the prompt must be 18 or more")
    young = re.search(r"\b(young woman|young man)\b", prompt, re.I)
    if young:
        r.append(f'never write "{young.group(0)}"; the number says the age')
    if stylized:
        if not prompt.startswith("A character reference sheet of "):
            r.append('begin with exactly "A character reference sheet of "')
        cap = 4000 if drawn else 3500 if styled else 2600 if "film frames" in prompt else 2000
        if drawn and not all(v in prompt for v in ("profile left", "profile right", "The two profiles face opposite edges")):
            r.append('a 2D sheet shows nine views, each named by where it faces: "profile left, <their> nose pointing at the left edge of the sheet", "profile right…" and "The two profiles face opposite edges." (sheet-stylized.md, In a 2D film)')
        if len(prompt) > cap:
            r.append(f"the prompt is {len(prompt)} characters; keep it under {cap}")
        if "No text" not in prompt and not labelled(prompt):
            r.append('end with "No text, labels, logos or watermarks."')
        if photo and "the attached face photo" not in prompt:
            r.append('name the uploaded photo exactly as "the attached face photo" (sheet-stylized.md)')
        return r
    if not re.search(r"\b\d{2}-year-old\b", prompt):
        r.append('write the age as a number, e.g. "a 47-year-old man" or "a 24-year-old woman"')
    m = re.search(r"\b(adult|young adult|grown|mature|middle-aged)\b", prompt, re.I)
    if m:
        r.append(f'never write "{m.group(0)}"; the number says the age')
    if re.search(r"reference image \d|@|<<<|\[\[", prompt):
        r.append("no numbered reference images, @-tags or pointers")
    if photo and "the attached reference image" not in prompt.lower():
        r.append('name the face photo exactly as "the attached reference image"')
    if not photo and re.search(r"reference image|attached", prompt, re.I):
        r.append('no image is attached: never write "reference image" or "attached"')
    if len(prompt) > 3500:
        r.append(f"prompt is {len(prompt)} characters; keep it under 3500")
    return r


def check_location(prompt, styled=False):
    r = check_names(prompt)
    if not prompt.startswith("A two-panel location reference sheet of one and the same"):
        r.append('the prompt must begin with exactly "A two-panel location reference sheet of one and the same"')
    if not re.search(r"Both panels: perfectly level, zero Dutch angle, [^.,]{3,40} of open [a-z -]{3,20} before each lens, the midground [a-z -]{3,20} clear\.", prompt):
        r.append('the closing sentence "Both panels: perfectly level, zero Dutch angle, three metres of open floor before each lens, the midground floor clear." is missing, word for word (only the distance and the floor\'s name may change, to the scale and ground of the place)')
    if "No people, figures, silhouettes or animals anywhere" not in prompt:
        r.append('the empty-place sentence "No people, figures, silhouettes or animals anywhere, in windows and reflections too; the place stands empty." is missing: a character drawn into the sheet is doubled in every clip')
    if "Left panel, the master view:" not in prompt or "Right panel, the reverse angle:" not in prompt:
        r.append('write both panel paragraphs, beginning "Left panel, the master view:" and "Right panel, the reverse angle:"')
    cap = 7500 if styled else 6000 if "attached reference image" in prompt else 5500
    if len(prompt) > cap:
        r.append(f"the prompt is {len(prompt)} characters; at most {cap:,}. Cut about {len(prompt) - cap + 200}: shorten the place description and light paragraph, keep the required opening and closing words")
    if re.search(r"\b(image|photo|picture) \d", prompt, re.I):
        r.append("never follow image, photo or picture with a number")
    return r


def check_style(prompt, path):
    """The style file's style block, word for word (a <placeholder> in it matches the words written in its place)."""
    with open(path) as f:
        text = f.read()
    m = re.search(r"^## Style block\n(.*?)(?=^## )", text, re.S | re.M)
    if not m:
        return [f"{path} has no style block"]
    flat = " ".join(prompt.split())
    for sentence in re.split(r"(?<=[.;:])\s+", " ".join(m.group(1).split())):
        pattern = ".{1,80}?".join(re.escape(part) for part in re.split(r"<[^>]+>", sentence))
        if not re.search(pattern, flat):
            return [f'the style block of {path} is not in the prompt word for word; missing: "{sentence[:90]}" '
                    "(style-master.md, The style block in every image)"]
    return []


def check_names(prompt):
    """Youth words and known names are refused in every image prompt: moderation stops them, and no character is a child."""
    r = []
    if re.search(YOUTH, prompt, re.I):
        r.append(f'the word "{re.search(YOUTH, prompt, re.I).group(0)}" is refused (even in a negation): no character is a child')
    owned = re.search(OWNED, prompt, re.I)
    if owned:
        r.append(f'never name an existing character, game or brand ("{owned.group(0)}"); describe an original design')
    return r


def check_master(prompt):
    r = check_names(prompt)
    if len(prompt) > 6000:
        r.append(f"the master is {len(prompt)} characters; at most 6,000 (3,300-4,800 worked): cut repeated detail, keep the style block")
    if "No text" not in prompt and not labelled(prompt):
        r.append('end with "No text, labels, logos or watermarks.": named machines, packs and signs get printed words')
    return r


def check_prop(prompt, drawn=False):
    r = check_names(prompt)
    if drawn and "Six views" not in prompt:
        r.append('a 2D prop sheet shows six views, each named by where it faces (style-master.md, Prop sheets)')
    if not prompt.startswith("A prop reference sheet of "):
        r.append('begin with exactly "A prop reference sheet of "')
    if "No text" not in prompt and not re.search(r'Its label reads exactly "[^"]+".*no other text', prompt, re.S):
        r.append('end with "No text, labels, logos or watermarks.", or for the user\'s own product with its label: '
                 '"Its label reads exactly "<its words>", <its lettering>; no other text, logos or watermarks."')
    return r


def frame_plate(name):
    """The frame id a frame-plate edit's prompt file is named for (plate-k1@0.3-morning.txt: frame:k1@0.3/morning), or None."""
    m = FRAME_PLATE.match(os.path.basename(str(name or "")))
    return m and f"frame:{m.group(1)}@{m.group(2)}" + (f"/{m.group(3)}" if m.group(3) else "")


def check_plate(prompt, name=None):
    r = check_names(prompt)
    if frame_plate(name) and not prompt.startswith("Edit the attached reference image"):
        r.append(f'{os.path.basename(name)} is the edit of {frame_plate(name)}, a frame of the film: begin "Edit the attached '
                 'reference image, one frame of a <template name> film: remove …" (clips.md, References from the film\'s own frames)')
    if not re.search(r"\bno (other )?people, figures, silhouettes or animals anywhere", prompt, re.I):
        r.append('the empty-place sentence "No people, figures, silhouettes or animals anywhere, in windows and reflections too; '
                 'the place stands empty." (or, where a crowd stays, "<the crowd> stays exactly as it is; no other people, '
                 'figures, silhouettes or animals anywhere…") is missing: a character drawn into a plate is doubled in every clip')
    return r


BEAT_TIME = re.compile(r"^.{0,12}?(?<![\d.])(\d+(?:\.\d+)?)\s*(?:[-–]|to)\s*(\d+(?:\.\d+)?)\s*(?:s|sec|secs|seconds?)\b", re.M)


def timed_beats(prompt):
    """The prompt's timed beats, (from, to, text) in the clip's own seconds: each beat opens its paragraph with its seconds
    ("3.5-7 s: …"); a time inside a beat ("from 1 to 3 s she…") is not a beat."""
    return [(float(m.group(1)), float(m.group(2)), prompt[m.end():].split("\n")[0].lstrip(" :,)"))
            for m in BEAT_TIME.finditer(prompt) if float(m.group(2)) > float(m.group(1))]


def take_shots(k):
    """A looked-at take's shots, (from, to, framing as seen) in the take's own seconds, from its entry's `shots`; else None."""
    shots = (k or {}).get("shots")
    if not isinstance(shots, list):
        return None
    out = [(float(x["from"]), float(x["to"]), str(x.get("framing", ""))) for x in shots
           if isinstance(x, dict) and isinstance(x.get("from"), (int, float)) and isinstance(x.get("to"), (int, float))]
    return out or None


def framing_clause(text):
    """A beat's framing: its words up to the first colon or full stop ("over Gary's shoulder, …, on Denise", "wide shot facing …")."""
    return re.split(r"[:.]\s", text + " ", maxsplit=1)[0]


QUALIFIERS = {"far", "near", "front", "back", "left", "right", "open", "closed", "glass", "white", "black", "red", "blue", "green",
              "big", "little", "small", "tall", "other", "wide", "dark", "bright", "warm", "round", "low", "high", "old", "same",
              "whole", "main", "snowy", "empty", "dry", "long", "short", "this", "that", "of", "with", "and", "at", "on", "in", "by"}


def toward(phrase):
    """The landmark words a direction names, as keys ("back across the street to the snowy park": to:park; "the far end": to:far end),
    so "facing the houses", a plate "seen toward the houses" and a panel that "faces the row of red-brick houses" meet."""
    phrase = re.sub(r"^\W*back\b.*?\bto\b", "", str(phrase).strip(), flags=re.I)
    out, last = set(), None
    for w in plain(phrase).replace("'s", "").split()[:5]:
        if w in ("the", "its", "his", "her", "their", "a", "an", "toward", "towards", "facing", "seen", "looking", "from", "to"):
            continue
        if w in ("end", "side", "wall", "corner", "half") and last:
            out.add(f"{last} {w}")
        elif w not in QUALIFIERS:
            out.add(w)
        last = w
    return {f"to:{w}" for w in out}


def shown_images(s, k):
    """The images clip k sends, in the order its @Image tags count them: a 2D location as each of its plates (l1#1, l1#2…)."""
    plates = {l.get("id"): len(l.get("plates") or []) for l in s.get("locations", [])}
    out = []
    for im in k.get("images", []):
        out += [f"{im}#{n}" for n in range(1, plates[im] + 1)] if plates.get(im) else [im]
    return out


def faces_in(prompt, n):
    """What the reference sentence of @Image<n> says it faces: {"left": …, "right": …} for a location sheet's panels, and "" for a
    plate or a frame "seen toward" something."""
    said = re.search(rf"@Image{n}\s+is\b(.*?)(?=@Image\d+\s+is\b|\n|$)", prompt)
    said, out = said.group(1) if said else "", {}
    for side in ("left", "right"):
        m = re.search(rf"its {side} panel faces\s+(.{{0,60}}?)(?:[;,.]|\band\b|$)", said)
        if m:
            out[side] = toward(m.group(1))
    m = re.search(r"\b(?:toward|towards|facing)\s+(.{0,60}?)(?:[;,:.]|$)", said)
    if m and not out:
        out[""] = toward(m.group(1))
    return out


def image_view(s, k, prompt, n, panel=None, read=lambda name: None, depth=0):
    """The direction reference image n of clip k shows, as one key (two views are one when their keys are equal): a 2D plate by its
    number (l1#2); a location sheet by its panel (l1:left, the master view when none is named); a frame plate, any tag, by the view
    the beat it was taken from names (K1a: a beat that names none gives none), else, in 2D, the one plate the clip leaves out, else
    the frame itself."""
    shown = shown_images(s, k)
    if not 1 <= n <= len(shown):
        return None
    im = shown[n - 1]
    plates = {l.get("id"): l.get("plates") or [] for l in s.get("locations", [])}
    if PLATE.match(im):
        return im
    if im in plates:
        return f"{im}:{panel or 'left'}"
    f = FRAME.match(im)
    if not f:
        return None
    loc = k.get("location")
    seen = faces_in(prompt, n).get("")
    if seen:  # what its reference sentence says it is seen toward: a plate of the place, or a panel another reference faces
        found = {f"{loc}#{i}" for i, plate in enumerate(plates.get(loc) or [], 1) if seen & toward(plate)}
        for m in range(1, len(shown) + 1):
            for side, said in faces_in(prompt, m).items():
                if side and seen & said:
                    found.add(image_view(s, k, prompt, m, side, read, depth + 1))
        if len(found) == 1:
            return found.pop()
    missing = [f"{loc}#{i}" for i in range(1, len(plates.get(loc) or []) + 1) if f"{loc}#{i}" not in shown]
    if len(missing) == 1:  # 2D: the plate a frame plate stands in for is the one the clip leaves out
        return missing[0]
    by_id = {e.get("id"): e for e in s.get("clips", [])}
    src = by_id.get(f.group(1))
    if src is not None and depth < 3:  # else the view of the beat the frame was taken from, in its own clip
        own = by_id.get(take_of(src), src)
        source_prompt = read(f"clip-{take_of(src)}.txt") or ""
        source = take_shots(own) or timed_beats(source_prompt)
        beat = next((x for x in source if x[0] <= float(f.group(2)) < x[1]), source[-1] if source else None)
        got = beat and direction(beat[2], s, own, source_prompt, read, depth + 1)
        if got and got[0] and (got[1] or not FRAME_VIEW_NAMED):  # K1a: only a source beat that names its view gives it
            return got[0]
    return f"frame:{f.group(1)}@{f.group(2)}"


def direction(text, s, k, prompt, read=lambda name: None, depth=0):
    """The direction a beat's framing faces, as (key, named): "the view of @Image<n>" (or of its left or right panel); else "facing
    <a landmark>", matched to the plate, panel or frame the references say faces it; else the clip's first image (named False)."""
    clause = framing_clause(text)
    m = re.search(r"view of (?:the (left|right) panel of )?@Image(\d+)(?:'s (left|right) panel)?", clause) or \
        re.search(r"()@Image(\d+) seen straight on()", clause)  # a flat world's one backdrop (clips.md, In 2D)
    if m:
        return image_view(s, k, prompt, int(m.group(2)), m.group(1) or m.group(3) or None, read, depth), True
    names = {plain(c.get("name", "")).split()[0] for c in s.get("cast", []) if plain(c.get("name", ""))}
    m = re.search(r"\bfacing\s+(?!(?:the\s+)?(?:camera|lens|us|viewer|him|her|it|them|each other|one another)\b)(.{0,60}?)(?:[;,:.]|$)",
                  clause, re.I)
    if m and not names & set(plain(m.group(1)).split()[:2]):
        keys, found = toward(m.group(1)), set()
        plates = {l.get("id"): l.get("plates") or [] for l in s.get("locations", [])}
        for i, plate in enumerate(plates.get(k.get("location")) or [], 1):  # 2D: the plate that faces it
            if keys & toward(plate):
                found.add(f"{k.get('location')}#{i}")
        for n in range(1, len(shown_images(s, k)) + 1):  # the reference that says it faces it
            for side, said in faces_in(prompt, n).items():
                if keys & said and depth < 3:
                    found.add(image_view(s, k, prompt, n, side or None, read, depth + 1))
        found.discard(None)
        return (found.pop() if len(found) == 1 else " ".join(sorted(keys))), True
    return (image_view(s, k, prompt, 1, None, read, depth) if depth < 3 else None), False


def subjects(text, s, k):
    """Who and what a beat frames: whoever its framing is "on" (K1b: "close-up on <A>, … <A> looks at <B>": A), else the cast members
    and story props its framing clause names (by name or by @Image tag), else those the whole beat names, the shoulder's owner of an
    over-the-shoulder shot aside; forms count as what they are forms of."""
    clause = framing_clause(text)
    on = re.match(r"^[^,;:]*?\bon\s+([^,;:]*)", clause) if SUBJECT_ON else None  # K1b: who the shot is "on" ("close-up on
    # <A>, … <A> looks at <B>": A)
    owner = re.search(r"\bover (\w+)'s shoulder", clause, re.I)
    owner = owner and owner.group(1).lower()
    of = {f.get("id"): f.get("of") for f in s.get("forms", [])}
    where = plain(next((l.get("description", "") for l in s.get("locations", []) if l.get("id") == k.get("location")), ""))
    names = []
    for c in s.get("cast", []):
        first = plain(c.get("name", "")).split()[:1]
        if first and first[0] != owner:
            names.append((c.get("id"), rf"\b{re.escape(first[0])}\b"))
    heads = [plain(p.get("name", "")).split()[-1:] for p in s.get("props", [])]
    for p in s.get("props", []):
        name = re.sub(r"\s*\(.*?\)", "", plain(p.get("name", "")).replace("the ", "", 1) if plain(p.get("name", "")).startswith("the ")
                      else plain(p.get("name", "")))
        if name:
            names.append((p.get("id"), rf"\b{re.escape(name)}\b"))
            head = name.split()[-1]
            if len(name.split()) > 1 and heads.count([head]) == 1 and not re.search(rf"\b{re.escape(head)}\b", where):
                names.append((p.get("id"), rf"\bthe {re.escape(head)}\b"))
    tags = {n: im for n, im in enumerate(shown_images(s, k), 1)}

    def names_in(part):
        part = re.sub(r'"[^"]*"|“[^”]*”', '""', part)  # a name inside a spoken line is not in the shot
        found = {i for i, pat in names if re.search(pat, plain(part))}
        for n in re.findall(r"@Image(\d+)", part):
            im = tags.get(int(n))
            if im in {c.get("id") for c in s.get("cast", []) + s.get("props", [])} or im in of:
                found.add(of.get(im, im))
        return frozenset(of.get(x, x) for x in found)
    return (on and names_in(on.group(1))) or names_in(clause) or names_in(text)


def named(ids, s):
    """Cast and prop ids by their names, for a message: "Dana and the folding chair"."""
    names = {e.get("id"): e.get("name", e.get("id")) for e in s.get("cast", []) + s.get("props", [])}
    return " and ".join(sorted(str(names.get(i, i)) for i in ids))


def framing(text):
    """A beat's framing: "over <name>'s shoulder", else the shot-size word of its framing clause (up to its first colon or full
    stop), the most specific first."""
    clause = framing_clause(text)
    m = re.search(r"\bover (\w+)'s shoulder", clause, re.I)
    return f"over {m.group(1)}'s shoulder" if m else shot_size(text)


def shot_size(text):
    clause = framing_clause(text)
    return next((n for n, p in SHOT_SIZES if re.search(p, clause, re.I)), None)


def line_windows(s, kid):
    """Every narration or sung line the film plays while clip kid's take is on screen, as (line, film start, film end): a line ends
    at its endSeconds, else at NARRATION_RATE words a second and never past the next line's start."""
    told = [l for l in s.get("lines", []) if l.get("kind") in ("narration", "sung")]
    spans, out = windows(s, kid), []
    for i, l in enumerate(told):
        a, b = l.get("startSeconds", 0), l.get("endSeconds")
        if not isinstance(b, (int, float)):
            b = a + words(l.get("text", "")) / NARRATION_RATE
            if i + 1 < len(told):
                b = min(b, told[i + 1].get("startSeconds", b))
        if any(t < b and a < t + y - x for t, x, y in spans):
            out.append((l, a, b))
    return out


def clip_window(spans, a, b):
    """A line's film seconds as the clip's own, "?" where that end of it plays outside the clip's kept seconds."""
    x, y = to_clip(spans, a), to_clip(spans, b)
    return f'{"?" if x is None else f"{x:.2f}"}-{"?" if y is None else f"{y:.2f}"} s'


def told_lines(s, kid):
    """What `checks.py clip` prints for a narrated or sung film's clip: each line's first words and its window in the clip's own
    seconds, so the beats that show it are written at those seconds."""
    spans = windows(s, kid)
    rows = [f'  {clip_window(spans, a, b)}  "{" ".join(l.get("text", "").split()[:6])}…"' for l, a, b in line_windows(s, kid)]
    return ([f"The lines over clip {kid}, in its own seconds (? = outside its kept seconds); write the beat that shows each line at "
             "its seconds (formats.md):"] + rows) if rows else []


DEPICTION = r"\b(?:photo(?:graph)?s?|portraits?|pictures?|drawings?|paintings?|posters?)\b"  # K6: a depiction of someone
NUMBERS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen")


def diary_days(e):
    """K4b: the body diary's "day <n>" / "night <n>" a clip entry's stateIn names, as "day 3"."""
    out = set()
    for m in re.finditer(rf"\b(day|night)\s+(\d+|{'|'.join(NUMBERS)})\b", str(e.get("stateIn", "")), re.I):
        n = m.group(2).lower()
        out.add(f"{m.group(1).lower()} {NUMBERS.index(n) + 1 if n in NUMBERS else int(n)}")
    return out


def check_clip(prompt, s, kid, plan=None, read=lambda name: None):
    """A clip's prompt (references/clips.md, The clip's prompt) against its entry in script.json, the film's plan.json and the
    prompt of the clip before it (read("clip-<id>.txt"))."""
    r = check_names(prompt)
    by_id = {c.get("id"): c for c in s.get("clips", [])}
    k = by_id.get(kid)
    if k is None:
        return [f"clip {kid} is not in script.json"]
    if k.get("make") == "part":
        return [f"clip {kid} is a part of {k.get('of')}: it is cut from that clip's take and has no prompt of its own; check "
                f"clip-{k.get('of')}.txt"]
    style = str(s.get("style", "")).strip()
    if style and not prompt.startswith(style):
        r.append("begin with the film's style line, word for word (styles.md)")
    talk = [l for l in s.get("lines", []) if take_of(by_id.get(l.get("clip"), {})) == kid
            and l.get("kind", "dialogue") in ("dialogue", "thought")]
    if talk and "Every spoken line is in American English" not in prompt:
        r.append('a clip with speech says "Every spoken line is in American English, exactly the words in quotes; nobody speaks any other language." (one came back in another language)')
    if not (s.get("format") == "song" and k.get("track")) and "No music and no score." not in prompt:
        r.append('every clip says "No music and no score." (the video model adds a score of its own; music goes over the joined film)')
    said = plain(prompt)
    for l in talk:
        if plain(l["text"]) not in said:
            r.append(f'the line "{l["text"][:50]}" is not in the prompt word for word')
    plates = {l.get("id"): len(l.get("plates") or [None]) for l in s.get("locations", [])}
    sent = {"Image": sum(plates.get(im, 1) for im in k.get("images", [])),
            "Video": len(k.get("videos", [])) + (1 if k.get("make") == "extend" else 0),
            "Audio": len(k.get("voices", [])) + (1 if k.get("track") else 0)}
    if AUDIO_AS_SENT and kept_ranges(k):  # C9: a take trimmed after it was sent keeps the prompt it was sent with
        sent["Audio"] = max([sent["Audio"]] + [int(x) for x in re.findall(r"@Audio(\d+)", prompt)])
    for kind, n in sent.items():
        tags = [int(t) for t in re.findall(rf"@{kind}(\d+)", prompt)]
        if tags and max(tags) > n:
            r.append(f"the prompt names @{kind}{max(tags)} but the clip sends {n} {kind.lower()}{'s' if n != 1 else ''}")
    # each reference sentence names what its number sends: a reference added or dropped moves every tag after it
    names = {c.get("id"): c.get("name", "") for c in s.get("cast", []) + s.get("props", [])}
    names.update({f.get("id"): names.get(f.get("of"), "") for f in s.get("forms", [])})
    # a form may be named by its change instead: its `change` up to the first comma, semicolon or colon, word for word
    changed = {f.get("id"): plain(re.split(r"[,;:]", f.get("change") or "")[0]) for f in s.get("forms", [])}
    shown = []
    for im in k.get("images", []):
        shown += [im] * (1 if PLATE.match(im) else plates.get(im, 1))
    flat = " ".join(prompt.split())
    for n, im in enumerate(shown, 1):
        if not names.get(im):
            continue
        m = re.search(rf"@Image{n}\s+is\s+([^;.@]*)", flat)
        if not m:
            r.append(f'name each reference by its tag and name: "@Image{n} is {names[im]}, …" ({im} is image {n} the clip sends)')
        elif plain(names[im]) not in plain(m.group(1)) and not (changed.get(im) and changed[im] in plain(m.group(1))):
            by_change = f' (or, as a form, by its change: "@Image{n} is …{changed[im]}…")' if changed.get(im) else ""
            r.append(f'@Image{n} sends {im} ({names[im]}), but its sentence reads "{m.group(1)[:50].strip()}": write "@Image{n} is '
                     f'{names[im]}, <its look>"{by_change}, and renumber every tag after a reference added or dropped (clips.md, '
                     "Name the references by their tags)")
    # every prop the prompt names sends its sheet (clips.md, The clip's prompt)
    sent = set(k.get("images", []))
    sent |= {f.get("of") for f in s.get("forms", []) if f.get("id") in sent}
    drawn = any(l.get("plates") for l in s.get("locations", []) if l.get("id") == k.get("location"))  # 2D: still props sit in plates
    directed = plain(re.sub(r'"[^"]*"|“[^”]*”', " ", prompt)) if QUOTES_NOT_PROPS else said  # C2: a line's words are not shown
    for p in s.get("props", []):
        name = plain(p.get("name", ""))
        if name and not drawn and p.get("id") not in sent and re.search(rf"\b{re.escape(name)}\b", directed):
            r.append(f'the prompt names {p.get("name")} but the clip does not send its sheet: put {p.get("id")} in its images (sent '
                     "only the place and the characters, one clip drew a prop in its case as another object)")
    if k.get("make") == "fresh" and re.search(r"continu\w* from|previous (shot|clip)", prompt, re.I):
        r.append('a fresh clip never refers back ("continuing from…"): the model replays the old ending')
    if k.get("make") == "extend" and "@Video1" not in prompt:
        r.append('an extension names its source: "@Video1 is the clip being continued: keep …; this clip adds …"')
    if s.get("format") in ("storytime", "song", "inside-body") and not talk and not k.get("track") \
            and "without speaking" not in prompt:
        r.append('a clip with no on-screen line says "The characters act and react without speaking; no voice-over, no narration." (formats.md)')
    beats = timed_beats(prompt)
    if not beats:
        r.append('the prompt has no timed beat: each beat opens its own paragraph with its seconds ("3.5-7 s: <its framing>: <the '
                 'action>"); written inline, its beats, plan items and seam go unread (clips.md, The clip\'s prompt)')
    spans = windows(s, kid)  # only the beats' own seconds are shots: a time inside a beat ("from 1 to 2 s she sets…") is not one
    for a, b, text in beats:  # a shot lasts 1.5 s on screen, and the model's cuts land up to 0.8 s off the written seconds
        if re.search(r"\binsert\b", framing_clause(text), re.I) and b - a < INSERT_SECONDS - 0.01:
            r.append(f"the insert {a:g}-{b:g} s is written {b - a:.1f} s; an insert is a physical action, at least 2 s on screen, and the "
                     f"model's cuts land up to {CUT_MARGIN:g} s off, so write it at least {INSERT_SECONDS:g} s, or join it to the beat "
                     "beside it (clips.md, Cutting the film into clips: inserts written 2.3-2.4 s came out 1.67 s)")
        elif b - a < SHORTEST_SHOT + CUT_MARGIN - 0.01:
            r.append(f"the beat {a:g}-{b:g} s is written {b - a:.1f} s; a shot lasts at least {SHORTEST_SHOT:g} s on screen and the model's "
                     f"cuts land up to {CUT_MARGIN:g} s off, so write it at least {SHORTEST_SHOT + CUT_MARGIN:g} s (a physical action "
                     f"{2 + CUT_MARGIN:g}), or join it to the beat beside it (clips.md, Cutting the film into clips)")
    # a hard cut changes the shot size, the subject or the angle; a cut inside one continuous moment opens on a close insert
    # (clips.md, Cutting the film into clips): one film cut from over his shoulder on her to the same over-the-shoulder shot
    clips = s.get("clips", [])
    at = next(i for i, e in enumerate(clips) if e.get("id") == kid)
    prev = clips[at - 1] if at else None
    continued = k.get("make") == "extend" and (k.get("source") or {}).get("clip") == take_of(prev or {})
    when = lambda e: {m.group(0).lower() for m in re.finditer(TIME_JUMP, str(e.get("stateIn", "")), re.I)}
    if prev and beats and prev.get("location") == k.get("location") and not continued and not when(k) - when(prev):
        source = by_id.get(take_of(prev), prev)
        before_prompt = read(f"clip-{take_of(prev)}.txt") or ""
        # a take that was looked at is read as it came out, its `shots`, in place of its prompt's beats: a take that kept the
        # window view where its last beat asked for the door view passed a seam that turned her 180 degrees (clips.md, The clip entry)
        looked = take_shots(source)
        before, mine = looked or timed_beats(before_prompt), take_shots(k) or beats
        # the beats on screen at the seam: half a second in from each trim, as the model's cuts land up to that far off (clips.md)
        first = (kept_ranges(k) or [{"from": 0}])[0].get("from", 0) + 0.5
        opens = next((x for x in mine if x[0] <= first < x[1]), mine[0])
        shot, size, subject = framing(opens[2]), shot_size(opens[2]), subjects(opens[2], s, k)
        refused = False
        if before:
            last = (kept_ranges(prev) or [{"to": prev.get("end", 0) - prev.get("start", 0)}])[-1].get("to", 0) - 0.5
            ends = next((x for x in before if x[0] <= last < x[1]), before[-1])
            shot2, subject2 = framing(ends[2]), subjects(ends[2], s, source)
            faces = direction(opens[2], s, k, prompt, read)[0], direction(ends[2], s, source, before_prompt, read)[0]
            same = all(faces) and faces[0] == faces[1]
            turned = all(faces) and faces[0] != faces[1]  # both beats face somewhere, and the angle changes
            # one view in both beats, one size step apart: one film cut from a medium-wide of her walking to the curtains to a medium
            # of her at them, from the same view
            step = same and shot in SIZE_STEPS and shot2 in SIZE_STEPS and abs(SIZE_STEPS.index(shot) - SIZE_STEPS.index(shot2)) == 1
            # one subject in both: the same set of names, or one inside the other ("close-up on Pepper" and "close-up on Pepper, looking
            # up at Frank"; a two-shot named in either order)
            one = bool(subject and subject2 and subject & subject2)
            if shot and one and size != "insert" and ((shot == shot2 and not turned) or step):
                refused, take = True, "'s take, as looked at," if looked else ""
                r.append(f'the clip opens {shot} on {named(subject, s)} ({opens[0]:g}-{opens[1]:g} s), and clip '
                         f'{prev.get("id")}{take} ends {shot2} on the same{" from the same view" if step else ""} ("{ends[2][:50]}…"): at a '
                         "hard cut the two clips differ in shot size, subject or angle, and a cut inside one continuous moment opens on "
                         "a close insert (clips.md, Cutting the film into clips)")
        if not refused and size not in CLOSE_SHOTS and CONTINUOUS_REFUSED:
            r.append(f'the clip opens {shot or "with no shot size"} ({opens[0]:g}-{opens[1]:g} s: "{opens[2][:50]}…") in the place and '
                     f'the moment clip {prev.get("id")} ends in (the same location, and no time jump in its stateIn): a cut inside one '
                     "continuous moment opens the next clip on a close insert or a close-up of what the last shot was about, and a "
                     "cut to a new time names the jump in stateIn (clips.md, Cutting the film into clips: two films jumped at such a seam)")
    # C7: a cut to a new time opens wide, so the viewer sees the place again (clips.md, Cutting the film into clips); an after-state
    # clip that opens on a close insert of the changed thing follows its own rule (clips.md, One physical action per shot)
    # K4b: in the body diary, a new "day <n>" / "night <n>" is a time jump too
    jump = sorted(when(k) - when(prev))[:1] if prev else []
    if DIARY_DAYS and prev and not jump and s.get("format") == "inside-body" \
            and any(l.get("kind") == "narration" for l in s.get("lines", [])):  # the body diary (formats.md)
        jump = [f"{w}" for w in sorted(diary_days(k) - diary_days(prev))][:1]
    if TIME_JUMP_WIDE and prev and beats and jump:
        first = (kept_ranges(k) or [{"from": 0}])[0].get("from", 0) + 0.5
        opens = next((x for x in beats if x[0] <= first < x[1]), beats[0])
        size = shot_size(opens[2])
        forms = {f.get("id") for f in s.get("forms", [])}
        after_state = any(im in forms and im not in prev.get("images", []) for im in k.get("images", []))
        if size not in ("wide", "medium-wide") and not (after_state and size in CLOSE_SHOTS):
            r.append(f'its stateIn names a time jump ("{jump[0]}"), and the clip opens {size or "with no shot size"} '
                     f'({opens[0]:g}-{opens[1]:g} s: "{opens[2][:50]}…"): a cut to a new time opens wide or medium-wide, so the viewer '
                     "sees the place again (clips.md, Cutting the film into clips: a time jump opened on a close-up read as the same "
                     "moment)")
    r += same_view_pairs(beats, s, k, prompt, read) if SAME_VIEW_REFUSED else []
    r += missing_postures(beats, s, k) if POSTURE_REFUSED else []
    # pixel art: a close-up balloons its art pixels unless it stays at head and shoulders (styles/pixel-art.md)
    if s.get("template") == "pixel-art" and PIXEL_HEAD_REFUSED:
        cast_ids = {c.get("id") for c in s.get("cast", [])}
        for a, b, text in beats:
            if re.search(r"(?<!medium )(?<!medium-)\bclose[- ]?up\b", framing_clause(text), re.I) and subjects(text, s, k) & cast_ids \
                    and not re.search(r"\bhead[- ]and[- ]shoulders\b", text, re.I):
                r.append(f'the close-up {a:g}-{b:g} s does not say "head and shoulders": in pixel art a close-up is framed at head and '
                         "shoulders, or it comes back an extreme close-up with its art pixels ballooned (styles/pixel-art.md; one did, 20-px "
                         "pixels)")
    # 2D: the first clip in a place holds a wide shot of each plate it sends, as frame plates carry only what it framed (clips.md)
    plates = [im for im in shown_images(s, k) if PLATE.match(im)]
    first_here = next((e for e in s.get("clips", []) if e.get("location") == k.get("location")), {}).get("id") == kid
    if plates and first_here and not any(FRAME.match(im) for im in k.get("images", [])):
        for n, im in [(n, im) for n, im in enumerate(shown_images(s, k), 1) if PLATE.match(im)]:
            wide = [x for x in beats if shot_size(x[2]) in ("wide", "medium-wide") and direction(x[2], s, k, prompt, read) == (im, True)
                    and not (CROP_NOT_WIDE and re.search(BODY_CROP, x[2], re.I))]  # C8: "from the chest up" frames a person, not the room
            if not wide:
                r.append(f"the first clip in {im.split('#')[0]} has no wide or medium-wide beat with the view of @Image{n} ({im}): later "
                         "clips take their frame plates from it, and a plate carries only what its frame shows (clips.md, References from "
                         "the film's own frames; one film's hook went to the far side of an opening)")
    # every plan item in this clip is a beat held as long as its proof says, plus the cut margin (references/plan-and-effects.md)
    ids = {e.get("id") for e in s.get("clips", []) if take_of(e) == kid}
    for i, it in enumerate((plan or {}).get("items", []) if isinstance(plan, dict) else [], 1):
        held = re.search(r"\bheld (?:for )?(\d+(?:\.\d+)?)\s*(?:s|sec|secs|seconds?)\b", str(it.get("proof", "")))
        x = to_clip(spans, it["second"]) if it.get("clip") in ids and isinstance(it.get("second"), (int, float)) else None
        if x is None or not held:
            continue
        x = round(x, 2)  # film 92.6 in a clip from 90 is 2.5999999, which fell in the beat 0-2.6 and not the one from 2.6
        need = float(held.group(1)) + CUT_MARGIN
        beat = next(((a, b) for a, b, _ in beats if a <= x < b), None) or next(((a, b) for a, b, _ in beats if b == x), None)
        ways = (f"either write the beat that shows its proof at that second, at least {need:g} s long (its {held.group(1)} s held on "
                f"screen and {CUT_MARGIN:g} s for the cut; lengthen it or move it), or move the item's second in plan.json, with its "
                "held seconds, to the beat that shows it")
        if beat is None:
            r.append(f'plan item {i} lands at {x:g} s of this clip (film second {it["second"]}) in no timed beat: {ways} '
                     f'("{str(it.get("proof", ""))[:60]}…")')
        elif beat[1] - beat[0] < need - 0.01:
            r.append(f'plan item {i} lands in the beat {beat[0]:g}-{beat[1]:g} s ({beat[1] - beat[0]:g} s), but its proof is held '
                     f'{held.group(1)} s: {ways} ("{str(it.get("proof", ""))[:60]}…"; written shorter, a plan point shrank on screen)')
    # the ending: the last clip's beats after the film's last line run at least 4 s on screen, written 5.8 (clips.md)
    if clips and take_of(clips[-1]) == kid and beats:
        end = clips[-1]
        told = [l for l in s.get("lines", []) if isinstance(l.get("startSeconds"), (int, float))]
        last_line = max(told, key=lambda l: line_end(l, s), default=None)
        said_by = line_end(last_line, s) if last_line else None
        ranges, t = [], end.get("start", 0)
        for g in kept_ranges(end) or [{"from": 0, "to": end.get("end", 0) - end.get("start", 0)}]:
            ranges.append((t, g.get("from", 0), g.get("to", 0)))
            t += g.get("to", 0) - g.get("from", 0)
        here = said_by is not None and said_by > ranges[0][0]  # the film's last line is spoken in this clip
        x = to_clip(ranges, said_by) if here else ranges[0][1]
        # the ending is counted from the screenplay's ENDING heading: a reaction close-up after the last line is not the ending (one
        # film's smile, SPIKE in its screenplay, made a 4.8-s ending pass, and the ending came out 2.92 s)
        heading = ending_second(s.get("screenplay", ""))
        e = None if heading is None else ranges[0][1] if heading <= ranges[0][0] else to_clip(ranges, heading)
        if last_line is not None and last_line.get("kind", "dialogue") not in ENDING_AFTER:
            pass  # a narrated or sung film's last line ends where its track puts it (formats.md)
        elif x is not None:
            x = round(x, 2)
            start = x if e is None else max(x, round(e, 2) - ENDING_LEAD)
            after = sum(max(0, min(b, y) - max(a, w)) for a, b, _ in beats if a >= start - 0.01 for _, w, y in ranges)
            final = sum(max(0, min(beats[-1][1], y) - max(beats[-1][0], w)) for _, w, y in ranges)
            margin = LAST_SHOT_MARGIN if here else CUT_MARGIN  # no line in this clip
            where = (f"the film's last line ends at {x:.1f} s of this clip (its endSeconds, or its words at its speaker's rate "
                     f"spoken, {NARRATION_RATE:g} told)" if here else "the film's last line is in an earlier clip") + \
                ("" if e is None else f" and the screenplay's ENDING starts at film second {heading:g}, {e:.1f} s of this clip")
            looked = take_shots(by_id.get(take_of(end), end)) if TAKE_SHOTS_READ else None
            if looked:  # C11: a looked-at take's shots, as they came out, through `kept`: no margin for the cuts
                # K2: counted from the last line's measured end, a shot that starts up to ENDING_TOLERANCE before it counts from it on
                lead = ENDING_FROM_END and here and start <= x + 0.001 and isinstance(last_line.get("endSeconds"), (int, float))
                if lead:
                    shown = sum(max(0, min(b, y) - max(a, w, start)) for a, b, _ in looked if a >= start - ENDING_TOLERANCE - 0.001
                                for _, w, y in ranges)
                else:
                    shown = sum(max(0, min(b, y) - max(a, w)) for a, b, _ in looked if a >= start - 0.05 for _, w, y in ranges)
                if shown < ENDING_SECONDS - 0.01:
                    counted = "after it" if start <= x + 0.001 else "from the ENDING on"
                    if lead:
                        counted = (f"after its measured end (a shot that starts up to {ENDING_TOLERANCE:g} s before it counted from "
                                   "it)")
                    r.append(f"{where}; the take's shots, as looked at, that start {counted} run {shown:.2f} s on screen: the ending's "
                             f"action lasts at least {ENDING_SECONDS:g} s on screen, the move and then its result: remake the ending's "
                             "beats as a clip of their own (clips.md, Cutting the film into clips)")
            elif ENDING_LAST_BEAT and here and final < ENDING_SECONDS + LAST_SHOT_MARGIN - 0.01:
                r.append(f"{where}; the last beat, {beats[-1][0]:g}-{beats[-1][1]:g} s, runs {final:.1f} s: with the film's last line "
                         f"in this clip, the ending is its last shot, at least {ENDING_SECONDS:g} s on screen, written "
                         f"{ENDING_SECONDS + LAST_SHOT_MARGIN:g} s (clips.md, Cutting the film into clips: written 4.8 s after a line, one "
                         "ending came out 2.92 s)")
            elif after < ENDING_SECONDS + margin - 0.01:
                counted = "after it" if start <= x + 0.001 else "from the ENDING on"
                r.append(f"{where}; the beats that start {counted} run {after:.1f} s: the ending's action lasts at least "
                         f"{ENDING_SECONDS:g} s on screen, the move and then its result, so write {ENDING_SECONDS + margin:g} s of "
                         "ENDING beats after the last line; a reaction before the ENDING does not count (an earlier line, or longer "
                         "ENDING beats; clips.md, Cutting the film into clips: a clip's last shot after a line came out up to 1.8 s "
                         "short, and one ending, written 4.8 s after a reaction close-up, 2.92 s)")
        elif said_by is not None:
            r.append(f"the film's last line ends at film second {said_by:.1f}, after this last clip's kept seconds: the ending's action "
                     f"after it lasts at least {ENDING_SECONDS:g} s on screen, written {ENDING_SECONDS + LAST_SHOT_MARGIN:g} s")
    return r


def speaking_rate(s, speaker):
    """A speaker's words a second: their wordsPerSecond, measured on their voice clip, when it is slower than SPOKEN_RATE, else
    SPOKEN_RATE (script-format.md): a slow speaker's lines are timed longer, a fast one's never shorter than 2.5 allows."""
    rate = next((c.get("wordsPerSecond") for c in (s or {}).get("cast", []) if c.get("id") == speaker), None)
    return min(rate, SPOKEN_RATE) if isinstance(rate, (int, float)) and SPOKEN_RATES[0] <= rate <= SPOKEN_RATES[1] else SPOKEN_RATE


def line_end(l, s=None):
    """A line's end in film seconds: its endSeconds, else its words at its speaker's rate (spoken) or NARRATION_RATE (told)."""
    if isinstance(l.get("endSeconds"), (int, float)):
        return l["endSeconds"]
    rate = NARRATION_RATE if l.get("kind") in ("narration", "sung") else speaking_rate(s, l.get("speaker"))
    return l.get("startSeconds", 0) + words(l.get("text", "")) / rate


def clip_warnings(prompt, s, kid, read=lambda name: None):
    """What `checks.py clip` prints after its verdict without refusing: the checks whose words miss too often to refuse on."""
    k = {c.get("id"): c for c in s.get("clips", [])}.get(kid)
    if k is None or k.get("make") == "part":
        return []
    beats = timed_beats(prompt)
    return ([] if SAME_VIEW_REFUSED else same_view_pairs(beats, s, k, prompt, read)) + \
        ([] if POSTURE_REFUSED else missing_postures(beats, s, k))


def same_view_pairs(beats, s, k, prompt, read=lambda name: None):
    """Two beats in a row on the same subject, from the same view and at the same size: the model makes one shot of them (clips.md,
    Cutting the film into clips: 4 of 9 such pairs lost their cut, none of 32 that changed the side or the size)."""
    out = []
    for (a, b, x), (c, d, y) in zip(beats, beats[1:]):
        one, two = subjects(x, s, k), subjects(y, s, k)
        f1, f2 = direction(x, s, k, prompt, read)[0], direction(y, s, k, prompt, read)[0]
        if one and two and (one <= two or two <= one) and framing(x) and framing(x) == framing(y) and f1 and f1 == f2:
            out.append(f'the beats {a:g}-{b:g} s and {c:g}-{d:g} s are both {framing(x)} on {named(one, s)} from the same view: '
                       "the model makes one shot of two such beats (4 of 9 lost their cut, none of 32 that changed the side or the size): "
                       "change the side or the size, or write them as one beat (clips.md, Cutting the film into clips)")
    return out


def missing_postures(beats, s, k):
    """Every cast member a beat names (not only as an owner, "Ernie's shoe") has a posture word in a sentence that names them (clips.md,
    The clip's prompt: a character with no posture written sat down, stood up or knelt between two shots)."""
    out = []
    of = {f.get("id"): f.get("of") for f in s.get("forms", [])}
    tags = {n: of.get(im, im) for n, im in enumerate(shown_images(s, k), 1)}
    patterns = {}
    for c in s.get("cast", []):
        first = plain(c.get("name", "")).split()[:1]
        if not first:
            continue
        own = [str(n) for n, im in tags.items() if im == c.get("id")]
        # named in the shot, never as an owner ("Ernie's shoe") or as where someone looks or turns ("her eyes on Ernie", "toward Gary")
        patterns[c.get("id")] = (rf"(?<!toward )(?<!towards )(?<!\bto )(?<!\bat )(?<!\bfrom )(?<!eyes on )(?<!\bpast )"
                                 rf"(?:\b{re.escape(first[0])}\b" + (rf"|@Image(?:{'|'.join(own)})\b" if own else "") + r")(?!['’])")

    def shown(part):
        """K6: the words of a sentence part that can name a character in the shot: a depiction's description (from "photo",
        "portrait", "picture", "drawing", "painting" or "poster" to the part's end) names who it depicts, not who is there."""
        return re.split(DEPICTION, part, maxsplit=1, flags=re.I)[0] if DEPICTION_NOT_SHOWN else part

    def only_named(part):
        """C4: the one cast member a clause names, else None (two named: the clause after it could be either's)."""
        at = [cid for cid, p in patterns.items() if re.search(p, shown(part), re.I)]
        return at[0] if len(at) == 1 else None

    for a, b, text in beats:
        text = re.sub(r'"[^"]*"|“[^”]*”', '""', text)  # a name inside a spoken line is not the character in the shot
        parts = re.split(r"(?<=[.;:!?])\s+", text)
        for c in s.get("cast", []):
            pattern = patterns.get(c.get("id"))
            if not pattern:
                continue
            named = [i for i, p in enumerate(parts) if re.search(pattern, shown(p), re.I)]
            # its posture: in a sentence that names them, or in the sentence after it that goes on with a pronoun ("on Rosa: she steps
            # back"), or "both standing"
            near = [parts[i] for i in named] + [parts[i + 1] for i in named if i + 1 < len(parts)
                                                and re.match(r"(?:in silence, )?(?:he|she|it|they|his|her|its|their)\b", parts[i + 1], re.I)]
            # C4: or in the clause after it that opens on a posture ("on Marco: in silence, standing astride the bicycle, he …"),
            # when they are the only one that clause names
            near += [parts[i + 1] for i in named if POSTURE_CLAUSE and i + 1 < len(parts) and only_named(parts[i]) == c.get("id")
                     and re.match(r"(?:in silence,\s*)?" + POSTURE, parts[i + 1], re.I)]
            both = any(re.search(r"\b(?:both|all)\b", p, re.I) and re.search(POSTURE, p, re.I) for p in parts)
            if named and not both and not any(re.search(POSTURE, p, re.I) for p in near):
                out.append(f'the beat {a:g}-{b:g} s names {c.get("name")} without a posture (stands, sits, kneels, lies, walks, leans…): '
                           "every shot says each character's posture (clips.md, The clip's prompt; a character seated at the end of one "
                           "clip stood from the first frame of the next)")
    return out


# ---------- main ----------

def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    step, flags, warnings = argv[1], [a for a in argv[2:] if a.startswith("--")], []
    args = [a for i, a in enumerate(argv[2:], 2) if not a.startswith("--") and argv[i - 1] not in ("--faces", "--style")]
    style = argv[argv.index("--style") + 1] if "--style" in argv else None
    def load(path):
        with open(path) as f:
            return json.load(f)
    def text(path):
        with open(path) as f:
            return f.read()
    if step == "script":
        faces = int(argv[argv.index("--faces") + 1]) if "--faces" in argv else 0
        reasons = check_script(load(args[0]), faces)
    elif step == "plan":
        reasons = check_plan(load(args[0]), load(args[1]))
    elif step == "effects":
        reasons = check_effects(load(args[0]), load(args[1]))
    elif step == "sheet":
        reasons = check_sheet(text(args[0]).strip(), "--photo" in flags, "--stylized" in flags or "--2d" in flags, "--2d" in flags, bool(style))
    elif step == "location":
        reasons = check_location(text(args[0]).strip(), bool(style))
    elif step == "master":
        reasons = check_master(text(args[0]).strip())
    elif step == "prop":
        reasons = check_prop(text(args[0]).strip(), "--2d" in flags)
    elif step == "plate":
        reasons = check_plate(text(args[0]).strip(), args[0])
    elif step == "clip":
        plan = os.path.join(os.path.dirname(os.path.abspath(args[1])), "plan.json")  # the viewer plan beside script.json
        beside = lambda name: os.path.join(os.path.dirname(os.path.abspath(args[0])), name)  # the other clips' prompts
        reasons = check_clip(text(args[0]).strip(), load(args[1]), args[2], load(plan) if os.path.isfile(plan) else None,
                             lambda name: text(beside(name)) if os.path.isfile(beside(name)) else None)
        warnings = clip_warnings(text(args[0]).strip(), load(args[1]), args[2],
                                 lambda name: text(beside(name)) if os.path.isfile(beside(name)) else None)
    else:
        print(f"unknown step {step}\n{__doc__}")
        return 2
    edit = text(args[0]).lstrip().startswith("Edit the attached reference image")  # a frame of the film keeps its own look
    if style and step in ("master", "sheet", "prop", "plate", "location") and not edit:
        reasons = reasons + check_style(text(args[0]), style)
        if step != "master" and "Copy the style of the attached reference image completely" not in text(args[0]):
            reasons.append('an image made from the master says "Copy the style of the attached reference image completely, <copy words>, '
                           'and draw <it> in it:" before the style block (style-master.md, The style block in every image)')
    # a narrated film's clip prompt is written to its lines' seconds: print them in the clip's own seconds
    told = told_lines(load(args[1]), args[2]) if step == "clip" and load(args[1]).get("format") in NARRATED else []
    if step == "clip" and warnings:  # printed, never refused: read each and fix the prompt where it is right
        told = [f"Warnings ({len(warnings)}, not refused):"] + [f"- {w}" for w in warnings] + told
    if reasons:
        print(f"REFUSED ({len(reasons)}):")
        for reason in reasons:
            print(f"- {reason}")
        for line in told:
            print(line)
        return 1
    print("PASS")
    for line in told:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
