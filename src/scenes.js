// Scene library. Each scene: build(ctx) creates DOM inside ctx.root (1920x1080 scene space),
// update(ctx, lf, len) sets every animated property for local frame lf. No hidden state between frames.
import { clamp, lerp, prog, typed, wordsTyped, el, pathAt, rand } from './util.js';
import { paintPlate, PLATE_VARIANTS } from './plates.js';

const SVG = (inner, size = 24, extra = '') =>
  `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" ${extra}>${inner}</svg>`;
const ICON = {
  plus: '<path d="M12 5v14M5 12h14"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  clock: '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
  puzzle: '<path d="M9 4h6v3a2 2 0 1 0 4 0h1v6h-3a2 2 0 1 0 0 4h3v3H4v-6h3a2 2 0 1 0 0-4H4V4z"/>',
  compass: '<circle cx="12" cy="12" r="8"/><path d="M15 9l-2 5-4 1 2-5z"/>',
  search: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
  chevron: '<path d="M7 10l5 5 5-5"/>',
  right: '<path d="M10 7l5 5-5 5"/>',
  up: '<path d="M12 19V6M6 12l6-6 6 6"/>',
  play: '<path d="M8 5l11 7-11 7z" fill="currentColor"/>',
  drive: '<rect x="3" y="7" width="18" height="10" rx="2"/><path d="M7 13h.01M11 13h6"/>',
  home: '<path d="M4 11l8-7 8 7v8a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
  meter: '<path d="M4 16a8 8 0 1 1 16 0"/><path d="M12 16l4-5"/>',
  help: '<circle cx="12" cy="12" r="8"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5M12 16.5h.01"/>',
  share: '<path d="M7 17L17 7M9 7h8v8"/>',
  lock: '<rect x="6" y="11" width="12" height="9" rx="2"/><path d="M9 11V8a3 3 0 0 1 6 0v3"/>',
  eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
};
const icon = (name, size, extra) => SVG(ICON[name], size, extra);

// Original marks: Reel Studio = three offset rounded bars; Atlas = ring with an orbiting dot.
const studioMark = (size = 40) =>
  `<svg width="${size}" height="${size}" viewBox="0 0 40 40"><rect width="40" height="40" rx="10" fill="var(--accent)"/>` +
  `<rect x="8" y="10" width="18" height="5" rx="2.5" fill="#fff"/><rect x="12" y="17.5" width="20" height="5" rx="2.5" fill="#fff"/><rect x="8" y="25" width="15" height="5" rx="2.5" fill="#fff"/></svg>`;
const atlasMark = (size = 28, color = 'currentColor') =>
  `<svg width="${size}" height="${size}" viewBox="0 0 28 28" fill="none"><circle cx="14" cy="14" r="9" stroke="${color}" stroke-width="2.2"/><circle cx="21.5" cy="7" r="3.2" fill="${color}"/></svg>`;

function desktop(root) {
  const d = el('div', 'desktop', root);
  d.innerHTML = `<svg class="waves" viewBox="0 0 1920 1080" preserveAspectRatio="none">
    <path d="M-200 900 C 300 600, 700 1100, 1200 700 S 2000 300, 2200 500 L 2200 1300 L -200 1300 Z" fill="var(--desktopWave)"/>
    <path d="M-200 300 C 200 100, 600 500, 1000 260 S 1700 -100, 2200 120 L 2200 -200 L -200 -200 Z" fill="var(--desktopWave2)" opacity=".7"/>
    <path d="M400 1300 C 700 900, 1100 1000, 1400 820 S 1900 700, 2200 820 L 2200 1300 Z" fill="var(--desktopWave2)" opacity=".45"/></svg>`;
  return d;
}

function plateCanvas(parent, cls, w, h, opts) {
  const c = el('canvas', cls, parent);
  c.width = w; c.height = h;
  c._opts = opts || {};
  return c;
}
const paint = (c, t, extra) => paintPlate(c, t, { ...c._opts, ...(extra || {}) });

/* ------------------------------------------------------------------ cursor */
const SYS_ARROW = `<svg width="34" height="44" viewBox="0 0 34 44"><path d="M3 3 L3 34 L11 27 L17 41 L23 38 L17 25 L28 25 Z" fill="#fff" stroke="#111" stroke-width="2.4" stroke-linejoin="round"/></svg>`;
const AGENT_ARROW = `<svg width="52" height="52" viewBox="0 0 52 52"><path d="M6 6 L44 20 L27 26 L21 44 Z" fill="var(--accent)" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>`;

export function buildCursor(root, spec) {
  const c = el('div', 'cursor', root);
  const sys = el('div', 'cur-sys', c); sys.innerHTML = SYS_ARROW;
  const ag = el('div', 'cur-agent', c); ag.innerHTML = AGENT_ARROW;
  const ring = el('div', 'cur-ring', c);
  return { c, sys, ag, ring };
}

export function updateCursor(cur, spec, lf) {
  const p = pathAt(spec.path, lf);
  cur.c.style.transform = `translate(${p.x}px,${p.y}px)`;
  let agent = spec.style === 'agent' ? 1 : 0;
  if (spec.style === 'morph') agent = prog(lf, spec.morphAt, spec.morphAt + 6, 'out');
  if (spec.style === 'unmorph') agent = 1 - prog(lf, spec.morphAt, spec.morphAt + 6, 'out');
  const pulse = Math.sin(clamp((agent - 0) * Math.PI)) * 0.35;
  cur.sys.style.opacity = 1 - agent;
  cur.sys.style.transform = `scale(${1 - agent * 0.5})`;
  cur.ag.style.opacity = agent;
  cur.ag.style.transform = `scale(${0.6 + agent * 0.4 + pulse})`;
  const click = (spec.clicks || []).map((k) => lf - k).find((d) => d >= 0 && d < 10);
  if (click !== undefined) {
    const t = click / 10;
    cur.ring.style.opacity = 1 - t;
    cur.ring.style.transform = `translate(-50%,-50%) scale(${0.3 + t * 1.4})`;
    cur.c.style.transform += ` scale(${click < 3 ? 0.88 : 1})`;
  } else cur.ring.style.opacity = 0;
}

/* -------------------------------------------------------------- captions */
function buildCaptions(ctx) {
  const box = el('div', 'captions', ctx.wrap);
  ctx.capText = el('span', 'cap-text', box);
  ctx.capDot = el('span', 'cap-dot', box);
  if (ctx.shot.props.super) ctx.superEl = el('div', 'super', ctx.wrap, ctx.shot.props.super);
}
function updateCaptions(ctx, lf) {
  const caps = ctx.shot.props.captions || [];
  let txt = '', live = false;
  for (const c of caps) {
    if (lf >= c.from) { txt = wordsTyped(c.text, lf, c.from, c.to); live = lf < c.to + 6; }
  }
  const last = caps[caps.length - 1];
  const vis = caps.length && lf >= caps[0].from - 4;
  ctx.capText.textContent = txt;
  ctx.capDot.style.opacity = vis && live ? 1 : 0;
  ctx.capDot.style.transform = `scale(${1 + 0.18 * Math.sin(lf * 0.9)})`;
  ctx.capText.parentElement.style.opacity = vis ? 1 : 0;
  if (ctx.superEl) ctx.superEl.style.opacity = prog(lf, 2, 10);
  void last;
}

/* ----------------------------------------------------------------- scenes */
export const SCENES = {};

SCENES.title = {
  build(ctx) {
    const r = ctx.root;
    r.classList.add('title-bg');
    ctx.blobs = [0, 1, 2, 3].map((i) => el('div', `blob blob${i}`, r));
    ctx.bits = Array.from({ length: 14 }, (_, i) => {
      const b = el('div', 'bit', r);
      b.style.left = `${200 + rand(i) * 1500}px`; b.style.top = `${150 + rand(i + 20) * 780}px`;
      b.style.background = ['var(--accent)', '#7AD3FF', '#C9A7FF', '#111'][i % 4];
      return b;
    });
    const lock = el('div', 'lockup', r);
    ctx.bar = el('div', 'lock-bar', lock);
    ctx.l1 = el('div', 'lock-l1', lock);
    ctx.l1.innerHTML = `<span class="mk">${studioMark(54)}</span><span class="t"></span>`;
    ctx.l2 = el('div', 'lock-l2', lock);
    ctx.arrow = el('div', 'lock-arrow', r);
    ctx.burst = el('div', 'burst', r);
    ctx.flash = el('div', 'flash', r);
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    ctx.blobs.forEach((b, i) => {
      b.style.transform = `translate(${Math.sin(lf / 30 + i * 2) * 60}px,${Math.cos(lf / 26 + i) * 40}px)`;
    });
    ctx.bits.forEach((b, i) => {
      const on = (Math.floor(lf / 3) + i) % 5 !== 0 && lf > 4;
      b.style.opacity = on ? 0.9 : 0;
    });
    const w = prog(lf, P.barIn, P.barIn + 8, 'out');
    ctx.bar.style.transform = `scaleX(${w})`;
    const colors = ['var(--accent)', '#C9F06B', '#111214'];
    ctx.bar.style.background = colors[lf < 14 ? 0 : lf < 18 ? 1 : 2];
    ctx.l1.querySelector('.t').textContent = typed(P.line1, lf, ...P.type1);
    ctx.l1.style.opacity = lf >= P.type1[0] ? 1 : 0;
    const t2 = typed(P.line2, lf, ...P.type2);
    ctx.l2.innerHTML = t2 ? `» ${t2.replace(/Atlas|$/, (m) => (m ? `<span class="a">${atlasMark(26, '#fff')}</span>${m}` : ''))}${lf > P.type2[1] ? ' «' : ''}` : '';
    ctx.arrow.style.opacity = lf > 10 ? 1 : 0;
    ctx.arrow.style.transform = `translateY(${(lf % 24) * 1.5}px)`;
    const b = prog(lf, P.burst[0], P.burst[1], 'in');
    ctx.burst.style.opacity = b > 0 ? 1 : 0;
    ctx.burst.style.transform = `translate(-50%,-50%) scale(${0.05 + b * 3.5}) rotate(${b * 90}deg)`;
    ctx.flash.style.opacity = prog(lf, P.burst[1] - 4, P.burst[1]);
  },
};

SCENES.chatApp = {
  build(ctx) {
    const r = ctx.root;
    r.classList.add('light-app');
    const side = el('div', 'sb', r);
    side.innerHTML = `<div class="sb-head">${atlasMark(26)}<b>${ctx.brand.assistant}</b>${icon('chevron', 18)}<span class="sp"></span>${icon('search', 20)}</div>`;
    const items = [['plus', 'New thread'], ['folder', 'Projects'], ['clock', 'Automations'], ['puzzle', 'Extensions'], ['compass', 'Discover']];
    ctx.items = items.map(([ic, label], i) => {
      const it = el('div', 'sb-item', side);
      it.innerHTML = `${icon(ic, 22)}<span>${label}</span>`;
      it.style.top = `${120 + i * 56}px`;
      return it;
    });
    const recents = el('div', 'sb-recents', side);
    recents.innerHTML = `<div class="sb-label">Recent</div>` + ['Launch storyboard', 'Shot list v2', 'Caption pass', 'Music cue notes'].map((t) => `<div class="sb-rec">${t}</div>`).join('');
    const main = el('div', 'main', r);
    ctx.home = el('div', 'home', main);
    ctx.home.innerHTML = `<div class="greet">What are we making today?</div><div class="home-box">Ask ${ctx.brand.assistant} anything…</div>`;
    ctx.page = el('div', 'ext-page', main);
    ctx.page.innerHTML = `<h1>Extensions</h1><p>Bring your tools into ${ctx.brand.assistant}</p>
      <div class="ext-search">${icon('search', 22)}<span class="q"></span><span class="caret"></span></div>
      <div class="ext-row">${studioMark(64)}<div><b>${ctx.brand.extension}</b><span>Edit, generate and finish video</span></div><div class="ext-add">Add</div></div>
      <div class="ext-grid">${['Docs', 'Sheets', 'Mail', 'Calendar', 'Design', 'Music'].map((n, i) => `<div class="ext-card"><i style="background:hsl(${i * 55 + 20} 60% 85%)"></i>${n}</div>`).join('')}</div>`;
    ctx.q = ctx.page.querySelector('.q');
    ctx.row = ctx.page.querySelector('.ext-row');
    ctx.add = ctx.page.querySelector('.ext-add');
    ctx.grid = ctx.page.querySelector('.ext-grid');
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    ctx.items.forEach((it, i) => it.classList.toggle('on', i === 3 && lf >= P.clickExtensions));
    ctx.items[3].classList.toggle('hover', lf >= P.clickExtensions - 6 && lf < P.clickExtensions);
    const pg = prog(lf, P.pageIn, P.pageIn + 8, 'out');
    ctx.home.style.opacity = 1 - pg;
    ctx.page.style.opacity = pg;
    ctx.page.style.transform = `translateY(${(1 - pg) * 30}px)`;
    ctx.q.textContent = typed(P.searchText, lf, ...P.typeSearch) || (lf < P.typeSearch[0] ? 'Search extensions' : '');
    ctx.q.classList.toggle('ph', lf < P.typeSearch[0]);
    const rr = prog(lf, P.resultIn, P.resultIn + 6, 'out');
    ctx.row.style.opacity = rr;
    ctx.row.style.transform = `translateY(${(1 - rr) * 16}px)`;
    ctx.grid.style.opacity = 1 - rr * 0.85;
    ctx.add.classList.toggle('press', lf >= P.addClick && lf < P.addClick + 4);
    ctx.add.textContent = lf >= P.addClick + 4 ? 'Added ✓' : 'Add';
    ctx.add.classList.toggle('done', lf >= P.addClick + 4);
  },
};

SCENES.iconReveal = {
  build(ctx) {
    desktop(ctx.root);
    const p = el('div', 'icon-panel', ctx.root);
    p.innerHTML = `<div class="ip-row dim">${icon('puzzle', 44)}<span>Doc tools</span></div>
      <div class="ip-row">${studioMark(120)}<span>${ctx.brand.extension}</span></div>
      <div class="ip-row dim">${icon('compass', 44)}<span>Discover</span></div>`;
  },
  update() {},
};

function studioWindow(ctx, parent) {
  const w = el('div', 'dwin', parent);
  w.innerHTML = `<div class="dwin-rail">${studioMark(34)}${['home', 'folder', 'clock', 'gear'].map((n) => icon(n, 24)).join('')}</div>`;
  return w;
}

SCENES.extensionHome = {
  build(ctx) {
    desktop(ctx.root);
    const w = studioWindow(ctx, ctx.root);
    w.classList.add('exthome');
    const body = el('div', 'eh-body', w);
    ctx.scroll = el('div', 'eh-scroll', body);
    ctx.scroll.innerHTML = `<div class="eh-hero"><div class="eh-pill">${studioMark(22)} ${ctx.brand.extension}</div>
      <h2>${ctx.brand.extensionTagline}</h2><div class="eh-ask">Try “cut my footage into a 30s spot”</div></div>
      <div class="eh-label">Recent renders</div><div class="eh-grid a"></div>
      <div class="eh-label">Templates</div><div class="eh-grid b"></div>`;
    ctx.canv = [];
    const ga = ctx.scroll.querySelector('.a'), gb = ctx.scroll.querySelector('.b');
    for (let i = 0; i < 4; i++) ctx.canv.push(plateCanvas(el('div', 'eh-tile', ga), '', 320, 200, { palette: PLATE_VARIANTS[i % 4], view: i === 2 ? 'aerial' : 'side' }));
    for (let i = 0; i < 4; i++) ctx.canv.push(plateCanvas(el('div', 'eh-tile', gb), '', 320, 200, { palette: PLATE_VARIANTS[(i + 2) % 4], view: i === 1 ? 'close' : 'side' }));
  },
  update(ctx, lf) {
    const [a, b, y0, y1] = ctx.shot.props.scroll;
    ctx.scroll.style.transform = `translateY(${-lerp(y0, y1, prog(lf, a, b, 'inOut'))}px)`;
    ctx.canv.forEach((c, i) => paint(c, (ctx.shot.start + lf) / 24 + i));
  },
};

SCENES.live = {
  build(ctx) {
    const P = ctx.shot.props;
    if (ctx.mode !== 'captions') {
      const r = ctx.root;
      r.classList.add('slate');
      r.innerHTML = `<div class="sl-grid"></div>
        <div class="sl-figure"><i class="head"></i><i class="body"></i><i class="desk"></i></div>
        <div class="sl-thirds"></div>`;
      const info = el('div', 'sl-info', ctx.wrap);
      const len = ctx.shot.end - ctx.shot.start;
      info.innerHTML = `<div class="sl-tag">LIVE-ACTION PLATE · ${ctx.shot.id}</div>
        <div class="sl-framing">${P.framing}</div><div class="sl-action">${P.action}</div>
        <div class="sl-drop">drop plates/${ctx.shot.id}.mp4 · ${len}f · ${(len / 24).toFixed(2)}s @24fps</div>`;
      ctx.bar = el('div', 'sl-bar', ctx.wrap);
    }
    buildCaptions(ctx);
  },
  update(ctx, lf, len) {
    if (ctx.bar) ctx.bar.style.transform = `scaleX(${lf / (len - 1)})`;
    updateCaptions(ctx, lf);
  },
};

SCENES.composer = {
  build(ctx) {
    desktop(ctx.root);
    const w = el('div', 'composer-win', ctx.root);
    ctx.tiles = [];
    const strip = el('div', 'cw-strip', w);
    for (let i = 0; i < 5; i++) ctx.tiles.push(plateCanvas(el('div', 'cw-tile', strip), '', 300, 180, { palette: PLATE_VARIANTS[i % 4], view: i % 2 ? 'close' : 'side' }));
    const chips = el('div', 'cw-chips', w);
    chips.innerHTML = ['Video', 'Edit', 'Color', 'Brand kit', 'Captions', 'Export'].map((c, i) => `<span class="chip ${i === 1 ? 'hl' : ''}">${c}</span>`).join('');
    const box = el('div', 'cw-box', w);
    box.innerHTML = `<span class="plus">${icon('plus', 26)}</span><span class="txt"></span><span class="caret"></span><span class="sp"></span><span class="model">${ctx.brand.model} ${icon('chevron', 18)}</span><span class="send">${icon('up', 26)}</span>`;
    ctx.txt = box.querySelector('.txt');
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    ctx.txt.textContent = typed(P.text, lf, ...P.type);
    ctx.tiles.forEach((c, i) => paint(c, (ctx.shot.start + lf) / 24 + i * 3));
  },
};

SCENES.sendMacro = {
  build(ctx) {
    desktop(ctx.root);
    const w = el('div', 'composer-win macro', ctx.root);
    const box = el('div', 'cw-box', w);
    box.innerHTML = `<span class="plus">${icon('plus', 26)}</span><span class="txt">${ctx.brand.prompt}</span><span class="sp"></span><span class="model">${ctx.brand.model} ${icon('chevron', 18)}</span><span class="send">${icon('up', 26)}</span>`;
    ctx.send = box.querySelector('.send');
    ctx.txt = box.querySelector('.txt');
  },
  update(ctx, lf) {
    const c = ctx.shot.props.click;
    const on = lf >= c;
    ctx.send.classList.toggle('on', on);
    ctx.send.style.transform = `scale(${lf >= c && lf < c + 3 ? 0.86 : on ? 1 + 0.08 * Math.exp(-(lf - c) / 4) : 1})`;
    ctx.txt.style.opacity = on ? 1 - prog(lf, c, c + 6) : 1;
  },
};

SCENES.agentTakeover = {
  build(ctx) {
    const r = ctx.root;
    r.classList.add('dark-bg');
    const bg = el('div', 'at-bg', r);
    bg.innerHTML = `<div class="cw-chips">${['Video', 'Edit', 'Color', 'Brand kit', 'Captions'].map((c) => `<span class="chip">${c}</span>`).join('')}</div>`;
    ctx.cards = [];
    const row = el('div', 'at-row', bg);
    for (let i = 0; i < 3; i++) ctx.cards.push(plateCanvas(el('div', 'at-card', row), '', 560, 340, { palette: PLATE_VARIANTS[(i + 1) % 4] }));
    ctx.pill = el('div', 'pill', r);
    ctx.pill.innerHTML = `<span class="spin"></span><span class="pt"></span>`;
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    ctx.cards.forEach((c, i) => paint(c, (ctx.shot.start + lf) / 24 + i * 5));
    const p = pathAt(ctx.shot.cursor.path, lf);
    const k = prog(lf, P.pillIn, P.pillIn + 8, 'back');
    ctx.pill.style.left = `${p.x + 46}px`;
    ctx.pill.style.top = `${p.y + 24}px`;
    ctx.pill.style.opacity = clamp(k * 2);
    ctx.pill.style.transform = `scale(${0.4 + 0.6 * k})`;
    ctx.pill.querySelector('.pt').textContent = typed(P.pill, lf, P.pillIn + 2, P.pillIn + 14);
    ctx.pill.style.setProperty('--sh', `${((lf * 4) % 200) - 50}%`);
    ctx.pill.querySelector('.spin').style.transform = `rotate(${lf * 24}deg)`;
  },
};

function browserWindow(ctx, parent, folderName) {
  const w = el('div', 'fb', parent);
  w.innerHTML = `<div class="fb-side"><div class="fb-dots"><i></i><i></i><i></i></div>
      <div class="fb-sec">Places</div>
      <div class="fb-it">${icon('home', 20)}Home</div><div class="fb-it">${icon('folder', 20)}Desktop</div><div class="fb-it">${icon('folder', 20)}Projects</div>
      <div class="fb-sec">Drives</div>
      <div class="fb-it on">${icon('drive', 20)}${ctx.brand.drive}</div><div class="fb-it">${icon('drive', 20)}Archive</div>
      <div class="fb-sec">Shared</div><div class="fb-it">${icon('folder', 20)}Studio</div></div>
    <div class="fb-main"><div class="fb-bar"><span class="nav">‹ ›</span><b>${ctx.brand.drive} <em>›</em> ${folderName}</b><span class="sp"></span>${icon('search', 20)}</div><div class="fb-grid"></div></div>`;
  return w;
}

SCENES.fileBrowser = {
  build(ctx) {
    desktop(ctx.root);
    const w = browserWindow(ctx, ctx.root, ctx.brand.projectFolder);
    const grid = w.querySelector('.fb-grid');
    ctx.tiles = [];
    for (let i = 0; i < 25; i++) {
      const t = el('div', 'fb-tile', grid);
      const th = el('div', 'fb-th', t);
      th.innerHTML = icon('play', 26);
      th.style.background = `linear-gradient(135deg, hsl(${20 + rand(i) * 40} 22% ${30 + rand(i + 4) * 12}%), hsl(${190 + rand(i + 2) * 30} 18% ${22 + rand(i + 7) * 10}%))`;
      el('div', 'fb-name', t, `BK_${String.fromCharCode(65 + (i % 3))}${String(i + 1).padStart(2, '0')}_0412.mov`);
      ctx.tiles.push(t);
    }
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    ctx.tiles.forEach((t, i) => t.classList.toggle('sel', lf >= P.selectFrom + i * P.selectStep));
  },
};

function editor(ctx, opts = {}) {
  const r = ctx.root;
  desktop(r);
  const w = el('div', 'ed', r);
  w.innerHTML = `<div class="ed-menu">${studioMark(22)}<span>File</span><span>Edit</span><span>Clip</span><span>Timeline</span><span>View</span><span class="sp"></span><span class="ed-proj">bike_spot_v3</span></div>
    <div class="ed-top"><div class="ed-bin"><div class="ed-h">Media <em>${ctx.brand.projectFolder}</em></div><div class="ed-thumbs"></div></div>
      <div class="ed-viewer"><div class="ed-h">Program</div><div class="ed-screen"></div><div class="ed-tc">01:00:18:12</div><div class="ed-meters"><i></i><i></i></div></div></div>
    <div class="ed-tl"><div class="ed-tlbar"><b class="tcbig">01:00:18:12</b><span class="sp"></span>${icon('play', 18)}</div>
      <div class="ed-ruler"><span style="left:6%">01 INTRO</span><span style="left:40%">02 RIDE</span><span style="left:74%">03 END</span></div>
      <div class="ed-tracks"></div><div class="ed-playhead"></div></div>`;
  ctx.thumbs = [];
  const th = w.querySelector('.ed-thumbs');
  for (let i = 0; i < 9; i++) {
    const cell = el('div', 'ed-thumb', th);
    ctx.thumbs.push({ cell, c: plateCanvas(cell, '', 240, 136, { palette: PLATE_VARIANTS[i % 4], view: i % 3 === 1 ? 'close' : 'side' }) });
    el('span', '', cell, `BK_A${String(i + 1).padStart(2, '0')}`);
  }
  ctx.screen = plateCanvas(w.querySelector('.ed-screen'), '', 960, 540, { palette: 'warm' });
  ctx.meters = [...w.querySelectorAll('.ed-meters i')];
  const tracks = w.querySelector('.ed-tracks');
  const names = [['T1', 'Titles'], ['V2', 'B-roll'], ['V1', 'Picture'], ['A1', 'Dialogue'], ['A2', 'Music']];
  ctx.clips = [];
  names.forEach(([k, n], ti) => {
    const row = el('div', 'ed-row', tracks);
    row.innerHTML = `<div class="ed-hd"><b>${k}</b><span>${n}</span>${icon('lock', 16)}${icon('eye', 16)}</div><div class="ed-lane"></div>`;
    const lane = row.querySelector('.ed-lane');
    let x = 2 + rand(ti) * 4;
    while (x < 92 && ti > 0) {
      const wd = 6 + rand(x + ti * 13) * 12;
      const c = el('div', `ed-clip t${ti}`, lane);
      c.style.left = `${x}%`; c.style.width = `${wd}%`;
      ctx.clips.push({ c, x });
      x += wd + (ti === 1 ? 6 + rand(x) * 8 : 0.4);
    }
  });
  ctx.clips.sort((a, b) => a.x - b.x);
  ctx.playhead = w.querySelector('.ed-playhead');
  ctx.tcs = [...w.querySelectorAll('.ed-tc, .tcbig')];
  return w;
}

function updateEditor(ctx, lf, o) {
  const abs = ctx.shot.start + lf;
  ctx.thumbs.forEach((t, i) => {
    const vis = o.thumbIn === undefined ? 1 : prog(lf, o.thumbIn + i * o.thumbStep, o.thumbIn + i * o.thumbStep + 4, 'out');
    t.cell.style.opacity = vis;
    t.cell.style.transform = `scale(${0.85 + 0.15 * vis})`;
    if (vis > 0) paint(t.c, abs / 24 + i);
  });
  paint(ctx.screen, abs / 24);
  ctx.clips.forEach((c, i) => {
    const vis = o.clipIn === undefined ? (o.clipsHidden ? 0 : 1) : prog(lf, o.clipIn + Math.floor(i / 3) * o.clipStep, o.clipIn + Math.floor(i / 3) * o.clipStep + 5, 'out');
    c.c.style.opacity = vis;
    c.c.style.transform = `translateX(${(1 - vis) * 120}px)`;
  });
  ctx.meters.forEach((m, i) => (m.style.transform = `scaleY(${0.3 + 0.6 * Math.abs(Math.sin(abs * 0.7 + i))})`));
  ctx.playhead.style.left = `${8 + ((abs * 0.05) % 80)}%`;
  const fr = 12 + abs, s = 18 + Math.floor(fr / 24);
  ctx.tcs.forEach((t) => (t.textContent = `01:00:${String(s % 60).padStart(2, '0')}:${String(fr % 24).padStart(2, '0')}`));
}

SCENES.editorBin = { build: (ctx) => editor(ctx), update: (ctx, lf) => updateEditor(ctx, lf, { ...ctx.shot.props, clipsHidden: true }) };
SCENES.editorTracks = { build: (ctx) => editor(ctx), update: (ctx, lf) => updateEditor(ctx, lf, { clipsHidden: true }) };
SCENES.editorFull = { build: (ctx) => editor(ctx), update: (ctx, lf) => updateEditor(ctx, lf, ctx.shot.props) };

SCENES.status = {
  build(ctx) {
    const r = ctx.root;
    r.classList.add('dark-bg', 'status');
    ctx.big = el('div', 'st-big', r);
    ctx.msg = el('div', 'st-msg', r);
    ctx.m1 = el('div', 'st-line', ctx.msg);
    ctx.m2 = el('div', 'st-line two', ctx.msg);
    ctx.glow = el('div', 'st-glow', r);
    ctx.pill = el('div', 'st-pill', r);
    ctx.pill.innerHTML = `<span class="spin"></span><span>${ctx.shot.props.pill || ''}</span>`;
    ctx.card = el('div', 'st-card', r);
    const P = ctx.shot.props;
    if (P.card === 'grade') {
      ctx.ca = plateCanvas(el('div', 'st-half', ctx.card), '', 640, 360, { palette: 'warm' });
      ctx.cb = plateCanvas(el('div', 'st-half', ctx.card), '', 640, 360, { palette: 'cool' });
      ctx.cbFix = plateCanvas(ctx.cb.parentElement, 'fix', 640, 360, { palette: 'warm' });
      el('span', 'st-tag', ctx.ca.parentElement, 'SHOT 4');
      el('span', 'st-tag', ctx.cb.parentElement, 'SHOT 5');
    } else {
      ctx.ca = plateCanvas(ctx.card, 'mic', 1920, 1080, { palette: 'day', mic: true });
      ctx.cb = plateCanvas(ctx.card, 'clean', 1920, 1080, { palette: 'day' });
      ctx.scan = el('div', 'st-scan', ctx.card);
    }
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    const abs = ctx.shot.start + lf;
    const settle = prog(lf, P.settle[0], P.settle[1], 'inOut');
    // big typography types in, then flies into the message line
    const bigTxt = typed(P.line1Big, lf, ...P.type1);
    ctx.big.innerHTML = `<span class="mk">${atlasMark(110)}</span>${bigTxt}`;
    ctx.big.style.opacity = 1 - settle;
    ctx.big.style.transform = `translate(-50%,-50%) scale(${1 + lf * 0.004 - settle * 0.6}) translateY(${-settle * 200}px)`;
    ctx.big.style.filter = `blur(${settle * 10}px)`;
    const msgOn = prog(lf, P.settle[0] + 4, P.settle[1], 'out');
    ctx.msg.style.opacity = msgOn;
    const rest = lf < P.line1Rest[0] ? P.line1Big : typed(P.line1, lf, P.line1Rest[0] - (P.line1Big.length / P.line1.length) * (P.line1Rest[1] - P.line1Rest[0]), P.line1Rest[1]);
    ctx.m1.innerHTML = `<span class="mk">${atlasMark(26)}</span>${rest.length < P.line1Big.length ? P.line1Big : rest}`;
    const l2 = typed(P.line2, lf, ...P.type2);
    ctx.m2.innerHTML = l2 ? `<span class="mk">${studioMark(26)}</span><span class="hl" style="--p:${prog(lf, P.type2[0], P.type2[1] + 10) * 100}%">${l2}</span>` : '';
    const cardStart = P.cardIn;
    const lift = prog(lf, cardStart - 6, cardStart + 8, 'inOut');
    ctx.msg.style.transform = `translate(-50%,-50%) translateY(${-lift * 200}px)`;
    if (P.pillIn) {
      const pin = prog(lf, P.pillIn[0], P.pillIn[0] + 6, 'back');
      const pout = prog(lf, P.pillIn[1] - 4, P.pillIn[1]);
      ctx.pill.style.opacity = pin * (1 - pout);
      ctx.pill.style.transform = `translate(-50%,-50%) scale(${0.6 + 0.4 * pin})`;
      ctx.glow.style.opacity = pin * (1 - pout) * (0.6 + 0.4 * Math.sin(lf / 4));
      ctx.pill.querySelector('.spin').style.transform = `rotate(${lf * 24}deg)`;
      ctx.msg.style.filter = `blur(${pin * (1 - pout) * 6}px)`;
      ctx.msg.style.opacity = msgOn * (1 - 0.6 * pin * (1 - pout));
    } else ctx.pill.style.opacity = 0;
    const cin = prog(lf, cardStart, cardStart + 10, 'out');
    ctx.card.style.opacity = cin;
    if (P.card === 'grade') {
      ctx.card.style.transform = `translate(-50%,-50%) translateY(${120 + (1 - cin) * 60}px)`;
      paint(ctx.ca, abs / 24); paint(ctx.cb, abs / 24 + 7); paint(ctx.cbFix, abs / 24 + 7);
      const fx = prog(lf, cardStart + 8, cardStart + 26, 'inOut');
      ctx.cbFix.style.clipPath = `inset(0 ${100 - fx * 100}% 0 0)`;
    } else {
      const full = prog(lf, P.cardFull[0], P.cardFull[1], 'inOut');
      const sc = lerp(0.36, 1, full);
      const ty = lerp(170, 0, full);
      ctx.card.style.transform = `translate(-50%,-50%) translateY(${ty * (1 - (1 - cin) * 0)}px) scale(${sc})`;
      ctx.card.style.borderRadius = `${lerp(28, 0, full) / sc}px`;
      ctx.msg.style.opacity = Math.min(parseFloat(ctx.msg.style.opacity), 1 - full);
      paint(ctx.ca, abs / 24); paint(ctx.cb, abs / 24);
      const s = prog(lf, P.scan[0], P.scan[1], 'inOut');
      ctx.cb.style.clipPath = `inset(0 ${100 - s * 100}% 0 0)`;
      ctx.scan.style.left = `${s * 100}%`;
      ctx.scan.style.opacity = s > 0 && s < 1 ? 1 : 0;
    }
  },
};

SCENES.folderDrop = {
  build(ctx) {
    const r = ctx.root;
    r.classList.add('dark-bg');
    const g = el('div', 'fd-grid', r);
    ctx.folders = ['01_selects', '02_audio', '03_gfx', '04_grade', '05_exports', '06_archive'].map((n) => {
      const f = el('div', 'fd-f', g);
      f.innerHTML = `<div class="fd-ic"></div><span>${n}</span>`;
      return f;
    });
    ctx.chip = el('div', 'fd-chip', r, ctx.shot.props.file);
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    const p = pathAt(ctx.shot.cursor.path, lf);
    const dropped = lf >= P.drop;
    ctx.chip.style.left = `${p.x - 30}px`;
    ctx.chip.style.top = `${p.y - 10}px`;
    ctx.chip.style.opacity = dropped ? 1 - prog(lf, P.drop, P.drop + 4) : 1;
    ctx.chip.style.transform = `scale(${dropped ? 1 - prog(lf, P.drop, P.drop + 4) * 0.6 : 1})`;
    const tgt = ctx.folders[3];
    const b = dropped ? Math.exp(-(lf - P.drop) / 3) * Math.sin((lf - P.drop) * 1.4) : 0;
    tgt.style.transform = `scale(${1 + 0.12 * b + (lf > P.drop - 6 && !dropped ? 0.06 : 0)})`;
    tgt.classList.toggle('hot', lf > P.drop - 8);
  },
};

SCENES.exportPanel = {
  build(ctx) {
    desktop(ctx.root);
    const p = el('div', 'xp', ctx.root);
    p.innerHTML = `<div class="xp-h"><b>Deliver</b><span class="sp"></span><span class="xp-btn">Render ${icon('share', 18)}</span></div>
      <div class="xp-rows"><div><span>Format</span><b>H.264 · MP4</b></div><div><span>Resolution</span><b>1920 × 1080</b></div><div><span>Frame rate</span><b>24</b></div><div><span>Audio</span><b>Stereo mix</b></div></div>
      <div class="xp-meter"><i></i><i></i></div>`;
    ctx.p = p;
    ctx.btn = p.querySelector('.xp-btn');
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    ctx.btn.classList.toggle('press', lf >= P.click && lf < P.click + 4);
    ctx.btn.classList.toggle('on', lf >= P.click);
    const s = prog(lf, P.slideOut[0], P.slideOut[1], 'in');
    ctx.p.style.transform = `translateX(${-s * 1300}px)`;
  },
};

SCENES.desktopFile = {
  build(ctx) {
    desktop(ctx.root);
    const f = el('div', 'df', ctx.root);
    ctx.thumb = plateCanvas(el('div', 'df-th', f), '', 360, 220, { palette: 'warm', view: 'close' });
    el('div', 'df-name', f, ctx.brand.finalFile.replace('_final', '_\nfinal'));
    ctx.f = f;
    ctx.toast = el('div', 'df-toast', ctx.root, ctx.shot.props.toast);
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    const k = prog(lf, P.iconIn[0], P.iconIn[1], 'out');
    ctx.f.style.opacity = k;
    ctx.f.style.filter = `blur(${(1 - k) * 18}px)`;
    ctx.f.style.transform = `scale(${0.7 + 0.3 * k})`;
    paint(ctx.thumb, (ctx.shot.start + lf) / 24);
    const p = pathAt(ctx.shot.cursor.path, lf);
    const ti = prog(lf, P.toastIn, P.toastIn + 6, 'back') * (1 - prog(lf, P.toastOut, P.toastOut + 5));
    ctx.toast.style.left = `${p.x + 50}px`;
    ctx.toast.style.top = `${p.y + 30}px`;
    ctx.toast.style.opacity = clamp(ti);
    ctx.toast.style.transform = `scale(${0.5 + 0.5 * ti})`;
  },
};

SCENES.usage = {
  build(ctx) {
    const r = ctx.root;
    r.classList.add('dark-bg');
    const bg = el('div', 'us-bg', r);
    ctx.tiles = [0, 1, 2].map((i) => plateCanvas(el('div', 'us-tile', bg), '', 480, 300, { palette: PLATE_VARIANTS[i + 1] }));
    const m = el('div', 'us-menu', r);
    m.innerHTML = `<div class="us-who"><i>${ctx.brand.userInitial}</i><div><b>${ctx.brand.user}</b><span>${ctx.brand.plan}</span></div></div>
      <div class="us-it">${icon('meter', 22)}Usage</div>
      <div class="us-it sub"><span>Monthly credits</span><b class="num"></b></div>
      <div class="us-bar"><i></i></div>
      <div class="us-it">${icon('gear', 22)}Settings</div><div class="us-it">${icon('help', 22)}Help</div>`;
    ctx.num = m.querySelector('.num');
    ctx.fill = m.querySelector('.us-bar i');
  },
  update(ctx, lf) {
    const P = ctx.shot.props;
    const v = Math.round(lerp(P.from, P.to, prog(lf, P.count[0], P.count[1], 'out')));
    ctx.num.textContent = `${v.toLocaleString('en-US')} left`;
    ctx.fill.style.transform = `scaleX(${v / P.from})`;
    ctx.tiles.forEach((c, i) => paint(c, (ctx.shot.start + lf) / 24 + i));
  },
};
