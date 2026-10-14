// Deterministic frame renderer. window.seek(frame) draws exactly one frame.
// Modes (?mode=): preview (default, with transport UI), render (full frame), captions (live-shot captions only, transparent bg).
import { SCENES, buildCursor, updateCursor } from './scenes.js';
import { cameraAt } from './util.js';

const params = new URLSearchParams(location.search);
const MODE = params.get('mode') || 'preview';
document.body.dataset.mode = MODE;
if (MODE === 'captions') document.documentElement.style.background = document.body.style.background = 'transparent';

const state = { tl: null, brand: null, shots: [], frame: 0 };

function fillBrand(v, brand) {
  if (typeof v === 'string') return v.replace(/\{\{(\w+)\}\}/g, (_, k) => brand[k] ?? `{{${k}}}`);
  if (Array.isArray(v)) return v.map((x) => fillBrand(x, brand));
  if (v && typeof v === 'object') return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, fillBrand(x, brand)]));
  return v;
}

export async function load(tlOverride) {
  const [tl, brand] = await Promise.all([
    tlOverride ? Promise.resolve(tlOverride) : fetch('/timeline/timeline.json', { cache: 'no-store' }).then((r) => r.json()),
    fetch('/timeline/brand.json', { cache: 'no-store' }).then((r) => r.json()),
  ]);
  state.tl = tl;
  state.brand = brand;
  const root = document.documentElement.style;
  for (const [k, v] of Object.entries(brand.colors)) root.setProperty(`--${k}`, v);

  const stage = document.getElementById('stage');
  stage.innerHTML = '';
  state.shots = tl.shots.map((raw) => {
    const shot = fillBrand(raw, brand);
    const wrap = document.createElement('div');
    wrap.className = `shot shot-${shot.kind}`;
    wrap.dataset.id = shot.id;
    const cam = document.createElement('div');
    cam.className = 'cam';
    wrap.appendChild(cam);
    stage.appendChild(wrap);
    const scene = SCENES[shot.scene];
    if (!scene) throw new Error(`unknown scene ${shot.scene} in ${shot.id}`);
    const ctx = { brand, shot, mode: MODE, root: cam, wrap };
    scene.build(ctx);
    if (shot.cursor) ctx.cursor = buildCursor(cam, shot.cursor);
    return { shot, wrap, cam, scene, ctx };
  });
  window.__timeline = tl;
  seek(state.frame);
}

export function shotAt(f) {
  return state.shots.find((s) => f >= s.shot.start && f < s.shot.end);
}

export function seek(f) {
  f = Math.max(0, Math.min(state.tl.durationFrames - 1, Math.round(f)));
  state.frame = f;
  for (const s of state.shots) {
    const on = f >= s.shot.start && f < s.shot.end;
    s.wrap.style.display = on ? '' : 'none';
    if (!on) continue;
    const lf = f - s.shot.start;
    const len = s.shot.end - s.shot.start;
    const c = cameraAt(s.shot.camera, lf, len);
    s.cam.style.transform =
      `translate(960px,540px) perspective(1600px) rotateX(${c.tilt}deg) rotate(${c.r}deg) scale(${c.s}) translate(${-c.x}px,${-c.y}px)`;
    s.cam.style.filter = c.blur > 0.05 && MODE !== 'captions' ? `blur(${c.blur.toFixed(2)}px)` : 'none';
    s.cam.style.opacity = c.o;
    s.ctx.cam = c;
    s.scene.update(s.ctx, lf, len);
    if (s.ctx.cursor) updateCursor(s.ctx.cursor, s.shot.cursor, lf);
  }
  document.dispatchEvent(new CustomEvent('frame', { detail: f }));
  return f;
}

window.seek = seek;
window.reloadTimeline = (tl) => load(tl);
window.__state = state;
window.__ready = load().then(() => true);
