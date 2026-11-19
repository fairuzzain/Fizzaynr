"""Shared toolkit for every video style (import with sys.path.insert(0, <skill>/scripts)).

Fonts
  get_font(name) -> local .ttf path (downloads from github google/fonts on first use)
  names: bangers, comicneue, marker (Permanent Marker), typewriter (Special Elite),
         anton, bebas, caveat, poppins (local), oswald, mono (JetBrains Mono)
Animation
  ease(x), ease_out(x), ease_back(x, c=1.8), lerp(a, b, k)
Post FX (PIL RGB 1080x1920 in/out)
  Post(): .grain(img, t, amt=0.07) .vignette(img) .glitch(img, t) .flash(img, amount)
  shake_offset(t, t0, dur, amp) -> (dx, dy)
Audio (numpy mono 44.1k)
  Mix(dur): .add(sig, t, gain) .pop() .word_pop() .slam() .whoosh() .shutter() .paper() .knock()
            .boom() .heartbeat(t0, t1) .static(d) .typing(t0, t1) .notif() .riser(d)
            .music(style, gain, mute=[(t0,t1)], duck=0.35, seed=None, **override) -> info dict
               styles: cheerful comedy lofi tense epic emotional funky retro8bit traditional
               seeded generator: random key/bpm/progression/pattern/instrument/drums per video;
               seed=None -> new track (seed printed), seed=<int or title str> -> reproducible
               override: bpm=, key='D', mode='min', arp='marimba', lead=None, drums='lofi' ...
  make_music(style, dur, seed) -> (np track, info)   # standalone, for custom audio scripts
            .drone(t0, t1, gain) .vo(path) .write('audio.wav')
Render
  render_chunk(compose, a, b, out)    # frames a..b -> part file (keep each call < ~280 s CPU)
  concat_and_mux(parts, audio, out)
  frame_time(compose, t)              # seconds per frame, to plan chunks
Sandbox limits: 1 CPU core, 300 s per tool call -> ALWAYS render in chunks, never one long call.
"""
import os, math, random, subprocess, time, wave
import numpy as np
from PIL import Image, ImageEnhance

W, H, FPS, SR = 1080, 1920, 24, 44100
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------- fonts ----------------
FONTS = {
    'bangers': 'ofl/bangers/Bangers-Regular.ttf',
    'comicneue': 'ofl/comicneue/ComicNeue-Bold.ttf',
    'marker': 'apache/permanentmarker/PermanentMarker-Regular.ttf',
    'typewriter': 'apache/specialelite/SpecialElite-Regular.ttf',
    'anton': 'ofl/anton/Anton-Regular.ttf',
    'bebas': 'ofl/bebasneue/BebasNeue-Regular.ttf',
    'caveat': 'ofl/caveat/Caveat[wght].ttf',
    'oswald': 'ofl/oswald/Oswald[wght].ttf',
    'mono': 'ofl/jetbrainsmono/JetBrainsMono[wght].ttf',
}
LOCAL = {'poppins': '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
         'poppins-regular': '/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf'}

def get_font(name, dest='fonts'):
    if name in LOCAL: return LOCAL[name]
    os.makedirs(dest, exist_ok=True)
    p = os.path.join(dest, os.path.basename(FONTS[name]).replace('[', '_').replace(']', '_'))
    if not os.path.exists(p) or os.path.getsize(p) < 10000:
        url = 'https://github.com/google/fonts/raw/main/' + FONTS[name].replace('[', '%5B').replace(']', '%5D')
        subprocess.run(['curl', '-sL', '-o', p, url], check=True)
        with open(p, 'rb') as f:
            if f.read(15).lower().startswith(b'<!doctype') : raise RuntimeError(f'font download failed: {url}')
    return p

# ---------------- easing ----------------
def clamp01(x): return min(max(x, 0.0), 1.0)
def ease(x): x = clamp01(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp01(x); return 1 - (1 - x) ** 3
def ease_back(x, c=1.8): x = clamp01(x); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k

# ---------------- post fx ----------------
class Post:
    def __init__(self, seed=5):
        rng = np.random.default_rng(seed)
        self.grains = [Image.fromarray(rng.normal(128, 26, (H // 2, W // 2)).clip(0, 255).astype(np.uint8))
                       .resize((W, H), Image.BILINEAR).convert('RGB') for _ in range(6)]
        yy, xx = np.mgrid[0:H, 0:W]
        v = np.clip(1.15 - 0.85 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2), 0.15, 1)
        self.vig = Image.fromarray((255 * v).astype(np.uint8))
        self.black = Image.new('RGB', (W, H), (0, 0, 0))
    def grain(self, img, t, amt=0.07): return Image.blend(img, self.grains[int(t * FPS) % 6], amt)
    def vignette(self, img): return Image.composite(img, self.black, self.vig)
    def flash(self, img, amount, col=(255, 255, 250)):
        return Image.blend(img, Image.new('RGB', (W, H), col), clamp01(amount)) if amount > 0 else img
    def glitch(self, img, t):
        r = random.Random(int(t * FPS)); a = np.array(img); sh = r.randint(8, 26)
        a[..., 0] = np.roll(a[..., 0], sh, 1); a[..., 2] = np.roll(a[..., 2], -sh, 1)
        for _ in range(r.randint(3, 7)):
            y = r.randint(0, H - 80); h = r.randint(10, 90)
            a[y:y + h] = np.roll(a[y:y + h], r.randint(-120, 120), 1)
        return Image.fromarray(a)
    def brightness(self, img, k): return ImageEnhance.Brightness(img).enhance(k)

def shake_offset(t, t0, dur, amp):
    if not (t0 <= t < t0 + dur): return 0, 0
    a = amp * (1 - (t - t0) / dur); r = random.Random(int(t * 48))
    return int(r.uniform(-a, a)), int(r.uniform(-a, a))

# ---------------- audio ----------------
def _note(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- music engine (seeded: every video gets its own track) ----------------
import zlib

_SCALES = {'maj': [0, 2, 4, 5, 7, 9, 11], 'min': [0, 2, 3, 5, 7, 8, 10], 'dor': [0, 2, 3, 5, 7, 9, 10],
           'pent': [0, 2, 4, 7, 9], 'pelog': [0, 1, 3, 7, 8]}
_PROGS = {  # scale-degree progressions, one chord per bar
    'maj': [[0, 4, 5, 3], [0, 5, 3, 4], [3, 4, 0, 5], [0, 3, 4, 3], [5, 3, 0, 4], [0, 2, 3, 4],
            [0, 5, 1, 4], [3, 0, 4, 5], [0, 3, 5, 4], [1, 4, 0, 0]],
    'min': [[0, 5, 2, 6], [0, 3, 4, 0], [0, 6, 5, 6], [0, 5, 6, 0], [0, 3, 6, 2], [5, 6, 0, 0],
            [0, 4, 5, 3], [0, 2, 5, 4]],
    'dor': [[0, 3, 0, 3], [0, 6, 3, 0], [0, 1, 3, 4], [0, 3, 6, 4]],
    'pent': [[0, 0, 3, 0], [0, 3, 2, 0], [0, 2, 0, 3], [0, 4, 3, 0]],
    'pelog': [[0, 0, 3, 0], [0, 3, 0, 4], [0, 2, 3, 0]],
}
_PATS = [[0, 2, 1, 2, 0, 2, 1, 2], [0, 1, 2, 3, 2, 1, 0, 1], [0, None, 2, None, 1, None, 3, None],
         [0, 2, 3, 2, 1, 2, 3, 2], [3, 2, 1, 0, 1, 2, 3, 2], [0, 0, 2, None, 1, 1, 3, None],
         [None, 2, None, 1, None, 2, None, 3], [0, 2, 4, 2, 3, 1, 2, None], [0, 3, 1, 4, 2, 3, 1, 2]]
_KEYS = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

MUSIC_STYLES = {
    'cheerful':    dict(bpm=(104, 126), modes=['maj'], arp=['pluck', 'marimba', 'bell', 'epiano'],
                        lead=['flute', 'square', 'marimba', None], bass=['bass', 'pluck'], drums=['pop', 'four', None], pad=0.4),
    'comedy':      dict(bpm=(116, 138), modes=['maj'], arp=['pluck', 'marimba', 'square'], lead=['square', 'flute', None],
                        bass=['bounce'], drums=['pop', None], pad=0.0, ring=0.22),
    'lofi':        dict(bpm=(70, 88), modes=['maj', 'dor'], sev=True, arp=['epiano', 'pluck'], lead=['flute', 'epiano', None],
                        bass=['sub'], drums=['lofi'], pad=0.7, swing=0.12, crackle=True),
    'tense':       dict(bpm=(62, 78), modes=['min'], arp=['pluck', 'bell'], lead=[None], bass=['sub'], drums=['half', None],
                        pad=0.8, drone=True, sparse=0.4),
    'epic':        dict(bpm=(84, 100), modes=['min'], arp=['pluck', 'saw'], lead=['saw', None], bass=['octave'],
                        drums=['epic'], pad=1.0, step=0.25),
    'emotional':   dict(bpm=(64, 80), modes=['maj', 'min'], arp=['epiano', 'bell', 'pluck'], lead=['flute', None],
                        bass=['sub'], drums=[None], pad=0.9, ring=1.1),
    'funky':       dict(bpm=(98, 112), modes=['dor', 'min'], sev=True, arp=['epiano', 'square'], lead=['saw', 'square'],
                        bass=['funk'], drums=['funk'], pad=0.2, swing=0.06, ring=0.3),
    'retro8bit':   dict(bpm=(126, 150), modes=['maj', 'min'], arp=['square'], lead=['square'], bass=['chipbass'],
                        drums=['chip'], pad=0.0, step=0.25, ring=0.15),
    'traditional': dict(bpm=(72, 96), modes=['pent', 'pelog'], arp=['koto', 'bell', 'marimba'], lead=['flute', 'koto'],
                        bass=['gong'], drums=['gendang'], pad=0.0),
}


class _Synth:
    def __init__(self, rng): self.rng = rng; self.cache = {}
    def _x(self, d): return np.arange(max(1, int(d * SR))) / SR
    def _lp(self, x, k): return np.convolve(x, np.ones(k) / k, 'same')
    def _tail(self, x, d, r=0.03): return np.clip((d - x) / r, 0, 1)
    def note(self, inst, m, d):
        key = (inst, m, round(d, 2))
        if key not in self.cache: self.cache[key] = getattr(self, 'i_' + inst)(_note(m), d)
        return self.cache[key]
    # --- instruments ---
    def i_pluck(self, f, d, dec=0.996):
        p = max(2, int(SR / f)); buf = self.rng.uniform(-1, 1, p); n = int(d * SR); y = np.zeros(n)
        for i in range(n): y[i] = buf[i % p]; buf[i % p] = dec * 0.5 * (buf[i % p] + buf[(i + 1) % p])
        return y * self._tail(np.arange(n) / SR, d)
    def i_koto(self, f, d): return self.i_pluck(f, d, 0.993) * 1.1
    def i_marimba(self, f, d):
        x = self._x(d); w = 2 * np.pi * f * x
        return (np.sin(w) * np.exp(-x * 7) + 0.35 * np.sin(4 * w) * np.exp(-x * 30) + 0.1 * np.sin(10 * w) * np.exp(-x * 80)) * self._tail(x, d)
    def i_bell(self, f, d):
        x = self._x(d); w = 2 * np.pi * f * x
        return 0.8 * np.sin(w + 2.5 * np.exp(-x * 3) * np.sin(3.5 * w)) * np.exp(-x * 3.5) * self._tail(x, d)
    def i_epiano(self, f, d):
        x = self._x(d); w = 2 * np.pi * f * x
        s = np.sin(w) + 0.3 * np.sin(2 * w) * np.exp(-x * 4) + 0.2 * np.sin(7 * w) * np.exp(-x * 30)
        return s * np.exp(-x * 2.2) * (1 + 0.15 * np.sin(2 * np.pi * 5 * x)) * 0.8 * self._tail(x, d)
    def i_square(self, f, d):
        x = self._x(d); return np.sign(np.sin(2 * np.pi * f * x)) * 0.35 * np.exp(-x * 4) * self._tail(x, d)
    def i_flute(self, f, d):
        x = self._x(d); vib = 0.004 * np.sin(2 * np.pi * 5.5 * x) * np.clip(x / 0.3, 0, 1)
        ph = 2 * np.pi * f * np.cumsum(1 + vib) / SR
        s = np.sin(ph) + 0.15 * np.sin(2 * ph) + self._lp(self.rng.normal(0, 0.04, len(x)), 6)
        return s * np.clip(x / 0.06, 0, 1) * self._tail(x, d, 0.12)
    def i_saw(self, f, d):
        x = self._x(d); s = sum(2 * ((f * k * x) % 1) - 1 for k in (1, 1.006))
        return self._lp(s, 6) * 0.35 * np.clip(x / 0.02, 0, 1) * np.exp(-x * 1.5) * self._tail(x, d, 0.08)
    def i_bass(self, f, d):
        x = self._x(d); return np.tanh(1.6 * np.sin(2 * np.pi * f * x)) * np.exp(-x * 3) * self._tail(x, d)
    def i_sub(self, f, d):
        x = self._x(d); return np.sin(2 * np.pi * f * x) * np.clip(x / 0.02, 0, 1) * np.exp(-x * 0.8) * self._tail(x, d, 0.1)
    def i_pad(self, f, d):
        x = self._x(d); s = sum(2 * ((f * k * x + k) % 1) - 1 for k in (1, 1.004, 0.997))
        return self._lp(s, 40) * 0.5 * np.clip(x / 0.4, 0, 1) * self._tail(x, d, 0.6)
    def i_gong(self, f, d):
        x = self._x(d); w = 2 * np.pi * f * x
        return (np.sin(w) + 0.5 * np.sin(2.01 * w) + 0.25 * np.sin(2.76 * w)) * np.exp(-x * 0.9) * (1 + 0.3 * np.sin(2 * np.pi * 3 * x)) * 0.6
    # --- drums ---
    def kick(self):
        x = self._x(0.35); return np.sin(2 * np.pi * np.cumsum(np.linspace(130, 42, len(x))) / SR) * np.exp(-x * 9)
    def snare(self):
        x = self._x(0.22); n = self.rng.normal(0, 1, len(x))
        return (n - self._lp(n, 6)) * np.exp(-x * 22) * 0.6 + np.sin(2 * np.pi * 185 * x) * np.exp(-x * 30) * 0.5
    def hat(self, open_=False):
        d = 0.25 if open_ else 0.05; x = self._x(d); n = self.rng.normal(0, 1, len(x))
        return (n - self._lp(n, 3)) * np.exp(-x * (12 if open_ else 90)) * 0.35
    def tom(self, f=90):
        x = self._x(0.4); return np.sin(2 * np.pi * np.cumsum(np.linspace(f * 1.6, f, len(x))) / SR) * np.exp(-x * 6)
    def gendang(self, high):
        x = self._x(0.2); f = 240 if high else 110
        return np.sin(2 * np.pi * f * x) * np.exp(-x * 25) + self._lp(self.rng.normal(0, 1, len(x)), 4) * np.exp(-x * 70) * 0.4


_DRUMS = {  # 16 steps per bar: (step, part, gain)
    'pop':  [(0, 'k', 1), (8, 'k', 1), (10, 'k', .6), (4, 's', 1), (12, 's', 1)] + [(i, 'h', 1) for i in range(0, 16, 2)],
    'four': [(i, 'k', 1) for i in (0, 4, 8, 12)] + [(i, 'h', 1.2) for i in (2, 6, 10, 14)] + [(4, 's', .5), (12, 's', .5)],
    'lofi': [(0, 'k', 1), (7, 'k', .7), (10, 'k', .8), (4, 's', .7), (12, 's', .7)] + [(i, 'h', .7) for i in range(0, 16, 2)],
    'half': [(0, 'k', .8), (8, 's', .5), (14, 'h', .5)],
    'epic': [(0, 'k', 1), (0, 't', 1), (6, 't', .8), (8, 's', 1), (10, 't', .8), (12, 't', .9), (14, 't', .7)],
    'funk': [(0, 'k', 1), (3, 'k', .7), (10, 'k', .9), (4, 's', 1), (12, 's', 1), (7, 's', .25), (15, 's', .25)] + [(i, 'h', .8) for i in range(16)],
    'chip': [(0, 'k', 1), (8, 'k', 1), (4, 's', .7), (12, 's', .7)] + [(i, 'h', 1) for i in (2, 6, 10, 14)],
    'gendang': [(0, 'gl', 1), (6, 'gl', .8), (8, 'gl', 1), (3, 'gh', .7), (10, 'gh', .8), (12, 'gh', .6), (14, 'gh', .7)],
}


def make_music(style='cheerful', dur=45.0, seed=None, **over):
    """Generate a background track. Same seed = same track; new seed = new track.
    over: bpm, key (0-11 or 'D'), mode, arp, lead, bass, drums, prog, pattern -> override the random pick."""
    if seed is None: seed = random.SystemRandom().randrange(1 << 30)
    if isinstance(seed, str): seed = zlib.crc32(seed.encode())
    rng = np.random.default_rng(seed); P = dict(MUSIC_STYLES[style]); syn = _Synth(rng)
    pick = lambda name, opts: over[name] if name in over else opts[rng.integers(len(opts))]
    mode = pick('mode', P['modes']); scale = _SCALES[mode]; L = len(scale)
    key = over.get('key', int(rng.integers(12))); key = _KEYS.index(key) if isinstance(key, str) else key
    T = 55 + key  # tonic around G3..F#4
    bpm = over.get('bpm', int(rng.integers(P['bpm'][0], P['bpm'][1] + 1)))
    prog = pick('prog', _PROGS[mode]); arp_i = pick('arp', P['arp']); lead_i = pick('lead', P['lead'])
    bass_m = pick('bass', P['bass']); drums = pick('drums', P['drums'])
    pa = pick('pattern', _PATS); pb = _PATS[rng.integers(len(_PATS))]
    step = P.get('step', 0.5); ring = P.get('ring', 0.7); swing = P.get('swing', 0.0); sev = P.get('sev', False)
    b = 60 / bpm; bar = 4 * b; N = int(dur * SR); out = np.zeros(N)

    def add(sig, t, g):
        i = int(t * SR); j = min(N, i + len(sig))
        if j > i >= 0: out[i:j] += sig[:j - i] * g
    def pitch(i, base): return base + scale[i % L] + 12 * (i // L)
    def tones(deg):
        idx = [deg, deg + 2, deg + 4, deg + 6] if sev else [deg, deg + 2, deg + 4, deg + L]
        return [pitch(i, T) for i in idx] + [pitch(deg + 2, T) + 12]
    def sw(t16, tb):  # swing the off-8ths
        return tb + (swing * b if swing and t16 % 4 == 2 else 0)

    # lead motif: 2 bars of 8ths as scale-step contour
    def motif():
        m, cur = [], int(rng.integers(0, L))
        for s in range(16):
            if s % 4 and rng.random() < (0.45 if bpm < 90 else 0.3): m.append(None); continue
            cur = int(np.clip(cur + rng.choice([-2, -1, -1, 0, 1, 1, 2]), -2, L + 3)); m.append(cur)
        return m
    mot = motif(); mot2 = mot[:8] + motif()[8:]
    nbars = int(np.ceil(dur / bar))
    for bi in range(nbars):
        t0 = bi * bar
        if t0 > dur - 0.3: break
        deg = prog[bi % len(prog)]; ch = tones(deg); section = (bi // 4) % 3
        intro, last = bi < 2, t0 + bar > dur - 0.5
        # pad
        if P['pad'] and (rng.random() < P['pad'] or section != 2):
            for m in ch[:3]: add(syn.note('pad', m - 12, bar + 0.4), t0, 0.08)
        # arp
        pat = pb if section == 2 else pa; nsteps = int(round(4 / step))
        for s in range(nsteps):
            v = pat[s % 8]
            if v is None or (P.get('sparse') and rng.random() < P['sparse']): continue
            t16 = int(s * step * 4); add(syn.note(arp_i, ch[v], ring), sw(t16, t0 + s * step * b), 0.17)
        # bass
        r = pitch(deg, T - 24)
        if bass_m in ('bass', 'pluck', 'sub'):
            for k in (0, 2): add(syn.note(bass_m, r, 2 * b), t0 + k * b, 0.32)
        elif bass_m == 'bounce':
            for k in range(4): add(syn.note('bass', r if k % 2 == 0 else r + 7, 0.3 * b), t0 + k * b, 0.3)
        elif bass_m == 'octave':
            for k in range(8): add(syn.note('bass', r + (12 if k % 2 else 0), 0.45 * b), t0 + k * b / 2, 0.28)
        elif bass_m == 'funk':
            for s16, iv in [(0, 0), (3, 0), (6, 12), (8, 0), (10, 7), (14, 10)]:
                add(syn.note('bass', r + iv, 0.2 * b), sw(s16, t0 + s16 * b / 4), 0.3)
        elif bass_m == 'chipbass':
            for k in range(8): add(syn.note('square', r + 12, 0.45 * b), t0 + k * b / 2, 0.22)
        elif bass_m == 'gong':
            if bi % 2 == 0: add(syn.note('gong', r, 2 * bar), t0, 0.35)
            add(syn.note('sub', r + 12, b), t0 + 2 * b, 0.15)
        # drums
        if drums and not intro and not last:
            for s16, part, g in _DRUMS[drums]:
                if drums == 'epic' and part == 't' and bi % 4 != 3 and s16 > 8: continue
                tt = sw(s16, t0 + s16 * b / 4)
                if part == 'k': add(syn.kick(), tt, 0.38 * g)
                elif part == 's': add(syn.snare(), tt, 0.2 * g)
                elif part == 'h': add(syn.hat(drums == 'four' and s16 % 4 == 2), tt, 0.08 * g)
                elif part == 't': add(syn.tom(85 + 15 * (s16 % 3)), tt, 0.3 * g)
                elif part == 'gl': add(syn.gendang(False), tt, 0.3 * g)
                elif part == 'gh': add(syn.gendang(True), tt, 0.22 * g)
        # lead (rests during section 2 for contrast)
        if lead_i and not intro and section != 2 and not last:
            src = mot2 if (bi // 2) % 4 == 3 else mot; half = (bi % 2) * 8
            for s in range(8):
                v = src[half + s]
                if v is None: continue
                m = pitch(v, T + 12)
                if s % 2 == 0:  # snap strong beats to chord tones
                    m = min([c + 12 * o for c in ch[:3] for o in (0, 1, 2)], key=lambda c: abs(c - m))
                nxt = next((k for k in range(s + 1, 8) if src[half + k] is not None), 8)
                add(syn.note(lead_i, m, min(1.2, (nxt - s) * b / 2 + 0.1)), sw(s * 2, t0 + s * b / 2), 0.15)
    if P.get('drone'):
        x = np.arange(N) / SR; f = _note(T - 24)
        out += (np.sin(2 * np.pi * f * x) + 0.6 * np.sin(2 * np.pi * f * 1.012 * x)) * 0.05 * np.minimum(1, x / 2)
    if P.get('crackle'):
        out += (rng.random(N) < 0.0004) * rng.uniform(-0.15, 0.15, N) + np.convolve(rng.normal(0, 0.01, N), np.ones(30) / 30, 'same')
    rms = np.sqrt((out ** 2).mean()) + 1e-9; out *= min(0.09 / rms, 0.6 / max(1e-6, np.abs(out).max()))  # even loudness across styles
    info = dict(style=style, seed=seed, key=_KEYS[key] + ('m' if mode == 'min' else ' ' + mode if mode != 'maj' else ''),
                bpm=bpm, arp=arp_i, lead=lead_i, bass=bass_m, drums=drums)
    print('[music]', ' '.join(f'{k}={v}' for k, v in info.items()))
    return out, info


class Mix:
    def __init__(self, dur, seed=1):
        self.dur = dur; self.N = int(dur * SR); self.out = np.zeros(self.N); self.rng = np.random.default_rng(seed)
        self.t = np.arange(self.N) / SR
    def add(self, sig, t, g=1.0):
        i = int(t * SR); j = min(self.N, i + len(sig))
        if j > i >= 0: self.out[i:j] += sig[:j - i] * g
    def _n(self, d): return self.rng.normal(0, 1, int(d * SR))
    def _x(self, d): return np.arange(int(d * SR)) / SR
    def _lp(self, x, k): return np.convolve(x, np.ones(k) / k, 'same')
    def _sweep(self, f0, f1, d): x = self._x(d); return np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, len(x))) / SR), x
    # --- sfx ---
    def pop(self, t, g=0.4): s, x = self._sweep(500, 1100, 0.09); self.add(s * np.exp(-x * 40), t, g)
    def word_pop(self, t, g=0.18): s, x = self._sweep(900, 1500, 0.05); self.add(s * np.exp(-x * 40), t, g)
    def slam(self, t, g=0.5):
        s, x = self._sweep(160, 40, 0.5); self.add(s * np.exp(-x * 9) + self._n(0.5) * 0.5 * np.exp(-x * 30), t, g)
    def whoosh(self, t, g=0.35):
        n = self._lp(self._n(0.4), 30); self.add(n * np.sin(np.linspace(0, np.pi, len(n))) ** 2 * 3, t - 0.08, g)
    def shutter(self, t, g=0.35):
        x = self._x(0.12); c = self._n(0.12) * np.exp(-x * 120); k = int(0.05 * SR)
        c[k:] += 0.8 * self._n(0.12)[k:] * np.exp(-(x[k:] - 0.05) * 90); self.add(c, t, g)
    def paper(self, t, g=0.2): x = self._x(0.2); self.add(self._lp(self._n(0.2), 4) * np.exp(-x * 18), t, g)
    def knock(self, t, g=0.6):
        x = self._x(0.3); self.add(np.sin(2 * np.pi * 95 * x) * np.exp(-x * 22) + self._lp(self._n(0.3), 8) * np.exp(-x * 60) * 0.6, t, g)
    def boom(self, t, g=0.5, d=2.5):
        s, x = self._sweep(70, 28, d)
        self.add(s * np.exp(-x * 1.6) + np.sin(2 * np.pi * (1800 + 300 * np.sin(x * 40)) * x) * np.exp(-x * 3) * 0.12
                 + self._lp(self._n(d), 3) * np.exp(-x * 6) * 0.3, t, g)
    def heartbeat(self, t0, t1, bpm=70, g=0.5):
        t = t0
        while t < t1:
            for dt, gg in [(0, 1), (0.18, 0.7)]:
                x = self._x(0.15); self.add(np.sin(2 * np.pi * 50 * x) * np.exp(-x * 30), t + dt, g * gg)
            t += 60 / bpm; bpm += 4
    def static(self, t, d, g=0.12): self.add(self._n(d) * (self.rng.random(int(d * SR)) > 0.3), t, g)
    def typing(self, t0, t1, g=0.15, rate=11):
        t = t0
        while t < t1:
            x = self._x(0.03); self.add(self._n(0.03) * np.exp(-x * 200), t, g * self.rng.uniform(0.6, 1)); t += self.rng.uniform(0.6, 1.4) / rate
    def notif(self, t, g=0.3):
        for k, f in enumerate((880, 1320)):
            x = self._x(0.18); self.add(np.sin(2 * np.pi * f * x) * np.exp(-x * 18), t + k * 0.09, g)
    def ding(self, t, g=0.3): x = self._x(0.8); self.add(np.sin(2 * np.pi * 1568 * x) * np.exp(-x * 5), t, g)
    def riser(self, t, d=1.5, g=0.25):
        s, x = self._sweep(200, 1400, d); self.add((s * 0.3 + self._lp(self._n(d), 6)) * (x / d) ** 2, t, g)
    def scribble(self, t0, t1, g=0.12):
        d = t1 - t0; n = self._lp(self._n(d), 3) * (0.5 + 0.5 * np.abs(np.sin(self._x(d) * 18))); self.add(n, t0, g)
    # --- beds ---
    def _pluck(self, f, d, dec=0.996):
        p = int(SR / f); buf = self.rng.uniform(-1, 1, p); n = int(d * SR); y = np.zeros(n)
        for i in range(n): y[i] = buf[i % p]; buf[i % p] = dec * 0.5 * (buf[i % p] + buf[(i + 1) % p])
        return y
    def music(self, style='cheerful', gain=0.3, mute=(), duck=1.0, start=0.0, end=None, seed=None, **over):
        """Seeded background track (see make_music / MUSIC_STYLES). seed=None -> new random track each run
        (printed as [music] seed=..., reuse it to re-render the same video with the same song)."""
        end = end or self.dur
        trk, info = make_music(style, end - start, seed, **over)
        mus = np.zeros(self.N); i = int(start * SR); s = trk[:self.N - i]; mus[i:i + len(s)] = s
        env = np.ones(self.N)
        f = (self.t >= start) & (self.t < start + 0.3); env[f] = np.linspace(0, 1, f.sum())
        for a, z in mute:
            m = (self.t >= a) & (self.t < z); env[m] = 0
            f = (self.t >= a - 0.2) & (self.t < a); env[f] = np.linspace(1, 0, f.sum())
            f = (self.t >= z) & (self.t < z + 0.5); env[f] = np.linspace(0, 1, f.sum())
        f = (self.t >= end - 1.2) & (self.t < end); env[f] *= np.linspace(1, 0, f.sum()); env[self.t >= end] = 0
        self.out += mus * env * gain * duck
        self.music_info = info
        return info
    def drone(self, t0, t1, gain=0.1, base=48):
        d = t1 - t0; x = self._x(d)
        s = np.sin(2 * np.pi * base * x) + 0.6 * np.sin(2 * np.pi * base * 1.015 * x) + 0.3 * np.sin(2 * np.pi * base * 1.5 * x + np.sin(x * 0.7) * 2)
        s += self._lp(self._n(d), 60) * 3 * (0.6 + 0.4 * np.sin(x * 0.5))
        env = np.minimum(1, x / 1.5) * np.minimum(1, (d - x) / 0.6)
        self.add(s * env, t0, gain)
    def vo(self, path, t=0.0, g=0.9):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '_vo.wav'], check=True)
        with wave.open('_vo.wav') as f: v = np.frombuffer(f.readframes(f.getnframes()), np.int16) / 32768
        self.add(v / np.abs(v).max() * g, t, 1.0)
    def write(self, path='audio.wav'):
        o = self.out / max(1, np.abs(self.out).max() / 0.95)
        with wave.open(path, 'w') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((o * 32767).astype(np.int16).tobytes())
        return path

# ---------------- render ----------------
def frame_time(compose, t=1.0, n=6):
    s = time.time()
    for i in range(n): compose(t + i / FPS)
    return (time.time() - s) / n

def render_chunk(compose, a, b, out=None, preset='veryfast'):
    out = out or f'part_{a:05d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', preset, '-crf', '20',
                          '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(compose(i / FPS).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return out

def concat_and_mux(parts, audio, out):
    with open('_list.txt', 'w') as f:
        for p in sorted(parts): f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', '_list.txt', '-c', 'copy', '_video.mp4'], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '_video.mp4', '-i', audio, '-c:v', 'copy', '-c:a', 'aac',
                    '-b:a', '192k', '-shortest', out], check=True)
    return out

def contact_sheet(compose, times, out='grid.jpg', per_row=4):
    rows = math.ceil(len(times) / per_row)
    S = Image.new('RGB', (270 * min(per_row, len(times)), 480 * rows), 'white')
    for i, t in enumerate(times): S.paste(compose(t).convert('RGB').resize((270, 480)), ((i % per_row) * 270, (i // per_row) * 480))
    S.save(out); return out
