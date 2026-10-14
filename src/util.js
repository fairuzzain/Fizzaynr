export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, t) => a + (b - a) * t;

export const EASE = {
  linear: (t) => t,
  in: (t) => t * t * t,
  out: (t) => 1 - Math.pow(1 - t, 3),
  inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  // fast start, long settle: whip-pans and snap zooms
  snap: (t) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  back: (t) => 1 + 2.2 * Math.pow(t - 1, 3) + 1.2 * Math.pow(t - 1, 2),
};

// progress of lf between a and b, eased
export const prog = (lf, a, b, ease = 'linear') => EASE[ease](clamp((lf - a) / Math.max(1e-6, b - a)));

const CAM_DEFAULT = { x: 960, y: 540, s: 1, r: 0, tilt: 0, blur: 0, o: 1 };
const CAM_KEYS = Object.keys(CAM_DEFAULT);

function rawCamera(keys, lf) {
  const out = {};
  for (const k of CAM_KEYS) {
    const ks = (keys || []).filter((key) => key[k] !== undefined);
    if (!ks.length) { out[k] = CAM_DEFAULT[k]; continue; }
    // a property first keyed later in the shot starts from its default at the shot's first key
    if (keys[0].f < ks[0].f) ks.unshift({ f: keys[0].f, [k]: CAM_DEFAULT[k] });
    if (lf <= ks[0].f) { out[k] = ks[0][k]; continue; }
    const last = ks[ks.length - 1];
    if (lf >= last.f) { out[k] = last[k]; continue; }
    let i = 0;
    while (ks[i + 1].f < lf) i++;
    const a = ks[i], b = ks[i + 1];
    const t = EASE[b.ease || 'inOut']((lf - a.f) / (b.f - a.f));
    out[k] = k === 's' ? a.s * Math.pow(b.s / a.s, t) : lerp(a[k], b[k], t);
  }
  return out;
}

// Camera with automatic motion blur derived from on-screen velocity.
export function cameraAt(keys, lf) {
  const c = rawCamera(keys, lf);
  const n = rawCamera(keys, lf + 1);
  const p = rawCamera(keys, lf - 1);
  const speed = (q) => Math.hypot((q.x - c.x) * c.s, (q.y - c.y) * c.s) + Math.abs(Math.log(q.s / c.s)) * 900 + Math.abs(q.r - c.r) * 20;
  const v = Math.max(speed(n), speed(p));
  c.blur += clamp((v - 25) / 18, 0, 14);
  return c;
}

// reveal characters of text across [a,b]; returns visible string
export function typed(text, lf, a, b) {
  const n = Math.round(text.length * clamp((lf - a) / Math.max(1, b - a)));
  return text.slice(0, n);
}

// word-by-word reveal (dictation captions)
export function wordsTyped(text, lf, a, b) {
  const words = text.split(' ');
  const n = Math.ceil(words.length * clamp((lf - a) / Math.max(1, b - a)) - 1e-9);
  return words.slice(0, n).join(' ');
}

export function el(tag, cls, parent, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  if (parent) parent.appendChild(e);
  return e;
}

export function pathAt(path, lf) {
  if (lf <= path[0].f) return path[0];
  const last = path[path.length - 1];
  if (lf >= last.f) return last;
  let i = 0;
  while (path[i + 1].f < lf) i++;
  const a = path[i], b = path[i + 1];
  const t = EASE[b.ease || 'inOut']((lf - a.f) / (b.f - a.f));
  return { x: lerp(a.x, b.x, t), y: lerp(a.y, b.y, t) };
}

// deterministic pseudo-random
export function rand(seed) {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}
