/* motion.js — mesin animasi deterministik untuk Dark Motion. Bebas lisensi pihak ketiga.
 *
 * Gaya pemanggilannya sengaja dibuat sama dengan GSAP (subset), jadi resep lama tetap jalan:
 *   const tl = gsap.timeline({paused:true});
 *   tl.set(el,{opacity:0},0);  tl.to(el,{x:100,duration:.4,ease:'power3.out'},2.1);
 *   tl.fromTo(el,{opacity:0,scale:1.3},{opacity:1,scale:1,duration:.3},4);
 *   gsap.set(el,{xPercent:-50,yPercent:-50});
 *   tl.seek(12.4);   // render frame di detik 12.4, hasilnya selalu sama
 *
 * Yang didukung: to / from / fromTo / set / call / addLabel, posisi angka atau "+=", "-=", "<", ">",
 * duration, delay, ease, stagger, repeat, yoyo, repeatDelay, keyframes, onUpdate, attr:{}, autoAlpha,
 * transform (x y z xPercent yPercent scale scaleX scaleY rotation rotationX rotationY skewX skewY
 * transformPerspective), properti CSS apa pun (angka + satuan, warna, filter, clip-path, bayangan),
 * variabel CSS (--nama), dan objek JS biasa.
 *
 * Perbedaan penting dari GSAP:
 *  - Sebelum tween fromTo/from dimulai, elemen SUDAH memakai nilai "from"-nya. Tidak ada efek bocor di awal.
 *  - onUpdate dipanggil di setiap seek (progress 0..1 dijepit). onStart/onComplete diabaikan.
 *  - tl.call(fn) dipanggil di setiap seek yang waktunya >= posisi call, jadi isinya harus aman diulang.
 *  - Jangan menulis style.transform manual pada elemen yang juga di-tween transform-nya.
 */
(function (root) {
  'use strict';
  const TF = { x: 0, y: 0, z: 0, xPercent: 0, yPercent: 0, rotation: 0, rotationX: 0, rotationY: 0,
    skewX: 0, skewY: 0, scale: 1, scaleX: 1, scaleY: 1, transformPerspective: 0 };
  const ALIAS = { rotate: 'rotation', rotateZ: 'rotation', rotationZ: 'rotation', rotateX: 'rotationX',
    rotateY: 'rotationY', perspective: 'transformPerspective' };
  const UNITLESS = new Set(['opacity', 'zIndex', 'fontWeight', 'lineHeight', 'flexGrow', 'flexShrink',
    'order', 'zoom', 'fillOpacity', 'strokeOpacity', 'stopOpacity', 'scale']);
  const SPECIAL = new Set(['duration', 'ease', 'delay', 'stagger', 'repeat', 'yoyo', 'repeatDelay', 'onUpdate',
    'onStart', 'onComplete', 'keyframes', 'immediateRender', 'overwrite', 'id', 'data', 'callbackScope',
    'clearProps', 'lazy', 'paused', 'onUpdateParams', 'onCompleteParams', 'onStartParams', 'startAt', 'runBackwards']);
  const warned = new Set();
  const warn = (k, ...a) => { if (!warned.has(k)) { warned.add(k); console.warn('[motion]', ...a); } };

  /* ---------------- ease ---------------- */
  const pw = p => ({ in: t => Math.pow(t, p), out: t => 1 - Math.pow(1 - t, p),
    inOut: t => t < .5 ? Math.pow(2 * t, p) / 2 : 1 - Math.pow(2 * (1 - t), p) / 2 });
  const E = {
    power0: pw(1), power1: pw(2), power2: pw(3), power3: pw(4), power4: pw(5),
    quad: pw(2), cubic: pw(3), quart: pw(4), quint: pw(5), strong: pw(5),
    sine: { in: t => 1 - Math.cos(t * Math.PI / 2), out: t => Math.sin(t * Math.PI / 2), inOut: t => -(Math.cos(Math.PI * t) - 1) / 2 },
    expo: { in: t => t === 0 ? 0 : Math.pow(2, 10 * t - 10), out: t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
      inOut: t => t === 0 ? 0 : t === 1 ? 1 : t < .5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2 },
    circ: { in: t => 1 - Math.sqrt(1 - t * t), out: t => Math.sqrt(1 - (t - 1) * (t - 1)),
      inOut: t => t < .5 ? (1 - Math.sqrt(1 - 4 * t * t)) / 2 : (Math.sqrt(1 - Math.pow(-2 * t + 2, 2)) + 1) / 2 },
  };
  const back = (s = 1.70158) => ({ in: t => t * t * ((s + 1) * t - s), out: t => { t -= 1; return t * t * ((s + 1) * t + s) + 1; },
    inOut: t => { const k = s * 1.525; t *= 2; return t < 1 ? (t * t * ((k + 1) * t - k)) / 2 : ((t -= 2) * t * ((k + 1) * t + k) + 2) / 2; } });
  const elastic = (a = 1, p = .3) => { a = Math.max(1, a || 1); p = p || .3; const s = p / (2 * Math.PI) * Math.asin(1 / a);
    const out = t => t === 0 || t === 1 ? t : a * Math.pow(2, -10 * t) * Math.sin((t - s) * (2 * Math.PI) / p) + 1;
    return { out, in: t => 1 - out(1 - t), inOut: t => t < .5 ? (1 - out(1 - 2 * t)) / 2 : (out(2 * t - 1) + 1) / 2 }; };
  const bOut = t => { const n = 7.5625, d = 2.75; if (t < 1 / d) return n * t * t; if (t < 2 / d) return n * (t -= 1.5 / d) * t + .75;
    if (t < 2.5 / d) return n * (t -= 2.25 / d) * t + .9375; return n * (t -= 2.625 / d) * t + .984375; };
  const bounce = { out: bOut, in: t => 1 - bOut(1 - t), inOut: t => t < .5 ? (1 - bOut(1 - 2 * t)) / 2 : (1 + bOut(2 * t - 1)) / 2 };
  function parseEase(e) {
    if (typeof e === 'function') return e;
    if (e == null) return E.power1.out;
    const m = String(e).trim().match(/^([a-zA-Z0-9]+)(?:\.(in|out|inOut))?(?:\(([^)]*)\))?$/);
    if (!m) { warn('ease' + e, 'ease tidak dikenal:', e); return E.power1.out; }
    const n = m[1], dir = m[2] || 'out', a = m[3] ? m[3].split(',').map(Number) : [];
    if (n === 'none' || n === 'linear') return t => t;
    if (n === 'steps') { const k = a[0] || 1; return t => t >= 1 ? 1 : Math.floor(t * k) / k; }
    if (n === 'back') return back(a[0])[dir];
    if (n === 'elastic') return elastic(a[0], a[1])[dir];
    if (n === 'bounce') return bounce[dir];
    if (E[n] && E[n][dir]) return E[n][dir];
    warn('ease' + e, 'ease tidak dikenal:', e); return E.power1.out;
  }

  /* ---------------- nilai ---------------- */
  const NUM = /[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?/g;
  function hex(h) {
    if (h.length === 3 || h.length === 4) h = h.split('').map(c => c + c).join('');
    const n = parseInt(h.slice(0, 6), 16), a = h.length === 8 ? parseInt(h.slice(6), 16) / 255 : 1;
    return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${+a.toFixed(3)})`;
  }
  const NAMED = { transparent: 'rgba(0,0,0,0)', white: 'rgba(255,255,255,1)', black: 'rgba(0,0,0,1)' };
  function normStr(s) {
    s = String(s);
    s = s.replace(/#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b/g, (m, h) => hex(h));
    s = s.replace(/\brgb\(\s*([-\d.]+)[,\s]+([-\d.]+)[,\s]+([-\d.]+)\s*\)/g, 'rgba($1,$2,$3,1)');
    s = s.replace(/\b(transparent|white|black)\b/g, m => NAMED[m]);
    return s;
  }
  function parse(s) { s = normStr(s); const nums = []; const parts = s.split(NUM); (s.match(NUM) || []).forEach(n => nums.push(+n)); return { nums, parts }; }
  function same(A, B) { if (A.nums.length !== B.nums.length || A.parts.length !== B.parts.length) return false;
    for (let i = 0; i < A.parts.length; i++) if (A.parts[i].replace(/\s+/g, '') !== B.parts[i].replace(/\s+/g, '')) return false; return true; }
  function neutral(prop, target) {
    // nilai awal netral untuk 'none': filter, bayangan
    const t = normStr(target);
    if (prop === 'filter' || prop === 'backdropFilter')
      return t.replace(/([a-z-]+)\(([^)]*)\)/g, (m, f, v) => {
        if (['brightness', 'contrast', 'saturate', 'opacity'].includes(f)) return `${f}(${v.replace(NUM, '1')})`;
        return `${f}(${v.replace(NUM, '0')})`; });
    if (/shadow/i.test(prop)) return t.replace(NUM, '0');
    return null;
  }
  // samakan daftar fungsi filter di kedua sisi, fungsi yang hilang diisi nilai netral
  function mergeFilters(a, b) {
    const fn = s => (normStr(s).match(/[a-z-]+\([^)]*\)/g) || []).map(x => [x.slice(0, x.indexOf('(')), x]);
    const A = fn(a), B = fn(b);
    if (!A.length || !B.length) return [a, b];
    const names = []; [...A, ...B].forEach(([n]) => { if (!names.includes(n)) names.push(n); });
    const pick = (L, other, n) => { const f = L.find(x => x[0] === n); if (f) return f[1]; return neutral('filter', other.find(x => x[0] === n)[1]); };
    return [names.map(n => pick(A, B, n)).join(' '), names.map(n => pick(B, A, n)).join(' ')];
  }
  const fmt = v => Math.abs(v) < 1e-6 ? '0' : String(+v.toFixed(4));
  function lerp(a, b, p, prop) {
    if (typeof a === 'number' && typeof b === 'number') return a + (b - a) * p;
    if (typeof b === 'number' && typeof a === 'string' && !isNaN(parseFloat(a))) return parseFloat(a) + (b - parseFloat(a)) * p;
    if (a === b) return b;
    let sa = a == null ? '' : String(a), sb = b == null ? '' : String(b);
    if ((sa === 'none' || sa === '' || sa === 'normal') && sb !== 'none') { const n = neutral(prop, sb); if (n) sa = n; }
    if (sb === 'none' && sa !== 'none') { const n = neutral(prop, sa); if (n) { if (p >= 1) return 'none'; sb = n; } }
    if ((prop === 'filter' || prop === 'backdropFilter') && sa !== sb) { const m = mergeFilters(sa, sb); sa = m[0]; sb = m[1]; }
    const A = parse(sa), B = parse(sb);
    if (A.nums.length && same(A, B)) {
      let out = '';
      for (let i = 0; i < B.parts.length; i++) {
        out += B.parts[i];
        if (i < B.nums.length) out += fmt(A.nums[i] + (B.nums[i] - A.nums[i]) * p);
      }
      return out;
    }
    return p > 0 ? b : a;   // tidak bisa diinterpolasi: lompat saat tween mulai
  }

  /* ---------------- target ---------------- */
  function toArray(t) {
    if (t == null) return [];
    if (typeof t === 'string') return Array.from(document.querySelectorAll(t));
    if (Array.isArray(t)) return t.flatMap(toArray);
    if (typeof NodeList !== 'undefined' && (t instanceof NodeList || t instanceof HTMLCollection)) return Array.from(t);
    return [t];
  }
  const isEl = o => typeof Element !== 'undefined' && o instanceof Element;
  const kebab = s => s.replace(/[A-Z]/g, m => '-' + m.toLowerCase());
  function tfState(el) { if (!el.__tf) el.__tf = Object.assign({}, TF); return el.__tf; }
  function composeTF(s) {
    let o = '';
    if (s.transformPerspective) o += `perspective(${fmt(s.transformPerspective)}px) `;
    if (s.xPercent || s.yPercent) o += `translate(${fmt(s.xPercent)}%,${fmt(s.yPercent)}%) `;
    o += `translate3d(${fmt(s.x)}px,${fmt(s.y)}px,${fmt(s.z)}px)`;
    if (s.rotation) o += ` rotate(${fmt(s.rotation)}deg)`;
    if (s.rotationY) o += ` rotateY(${fmt(s.rotationY)}deg)`;
    if (s.rotationX) o += ` rotateX(${fmt(s.rotationX)}deg)`;
    if (s.skewX || s.skewY) o += ` skew(${fmt(s.skewX)}deg,${fmt(s.skewY)}deg)`;
    const sx = s.scale * s.scaleX, sy = s.scale * s.scaleY;
    if (sx !== 1 || sy !== 1) o += ` scale(${fmt(sx)},${fmt(sy)})`;
    return o;
  }
  function tfNum(prop, v) {
    if (typeof v === 'number') return v;
    const s = String(v).trim();
    return parseFloat(s);
  }
  // ubah satu pasangan (prop, nilai) jadi [kunci-track, nilai yang sudah dinormalkan]
  function normProp(target, prop, v) {
    prop = ALIAS[prop] || prop;
    if (!isEl(target)) return [['obj', prop], v];
    if (prop in TF) {
      if ((prop === 'x' || prop === 'y') && typeof v === 'string' && /%$/.test(v.trim()) && !/^[-+]=/.test(v)) return [['tf', prop + 'Percent'], parseFloat(v)];
      if (typeof v === 'string' && !/^[-+]=/.test(v.trim())) v = parseFloat(v) || 0;
      return [['tf', prop], v];
    }
    if (prop === 'autoAlpha') return [['auto', 'opacity'], v];
    if (prop.startsWith('--')) return [['var', prop], v];
    if (typeof v === 'number' && !UNITLESS.has(prop)) v = v + 'px';
    return [['css', prop], v];
  }
  function readBase(target, kind, prop) {
    if (kind === 'obj') return target[prop];
    if (kind === 'tf') return tfState(target)[prop];
    if (kind === 'attr') { const a = target.getAttribute(prop); return a == null ? 0 : (isNaN(+a) ? a : +a); }
    const cs = getComputedStyle(target);
    if (kind === 'auto') return +cs.opacity;
    if (kind === 'var') return cs.getPropertyValue(prop).trim() || target.style.getPropertyValue(prop).trim();
    const v = target.style[prop] || cs[prop];
    if (UNITLESS.has(prop)) return v === '' || v == null ? (prop === 'opacity' ? 1 : 0) : (isNaN(+v) ? v : +v);
    return v;
  }
  function write(target, kind, prop, v) {
    if (kind === 'obj') { target[prop] = v; return; }
    if (kind === 'tf') { tfState(target)[prop] = typeof v === 'number' ? v : parseFloat(v) || 0; return; }
    if (kind === 'attr') { target.setAttribute(prop, typeof v === 'number' ? fmt(v) : v); return; }
    if (kind === 'auto') { const o = typeof v === 'number' ? v : parseFloat(v);
      target.style.opacity = fmt(o); target.style.visibility = o <= 0.0001 ? 'hidden' : 'inherit'; return; }
    if (kind === 'var') { target.style.setProperty(prop, typeof v === 'number' ? fmt(v) : v); return; }
    target.style[prop] = typeof v === 'number' ? fmt(v) : v;
  }

  /* ---------------- timeline ---------------- */
  const TIMELINES = [];
  class Timeline {
    constructor(opts = {}) {
      this.defaults = Object.assign({ duration: .5, ease: 'power1.out' }, opts.defaults || {});
      this.tracks = new Map();      // target -> Map(key -> track)
      this.list = [];               // semua track, urutan dibuat
      this.cbs = [];                // tween dengan onUpdate
      this.calls = [];
      this.labels = {};
      this._end = 0; this._lastStart = 0; this._lastEnd = 0; this._t = 0;
      TIMELINES.push(this);
    }
    _pos(p) {
      if (p === undefined || p === null) return this._end;
      if (typeof p === 'number') return p;
      const s = String(p).trim();
      if (s.startsWith('+=')) return this._end + parseFloat(s.slice(2));
      if (s.startsWith('-=')) return this._end - parseFloat(s.slice(2));
      if (s[0] === '<') return this._lastStart + (parseFloat(s.slice(1)) || 0);
      if (s[0] === '>') return this._lastEnd + (parseFloat(s.slice(1)) || 0);
      const lm = s.match(/^([A-Za-z_][\w-]*)\s*([-+]=\s*[\d.]+)?$/);
      if (lm && this.labels[lm[1]] !== undefined) {
        let b = this.labels[lm[1]]; if (lm[2]) b += (lm[2][0] === '-' ? -1 : 1) * parseFloat(lm[2].slice(2)); return b; }
      const n = parseFloat(s); return isNaN(n) ? this._end : n;
    }
    _track(target, kind, prop) {
      let m = this.tracks.get(target); if (!m) { m = new Map(); this.tracks.set(target, m); }
      const key = kind + ':' + prop; let tr = m.get(key);
      if (!tr) { tr = { target, kind, prop, segs: [], base: undefined, sorted: true, last: undefined }; m.set(key, tr); this.list.push(tr); }
      return tr;
    }
    _add(type, targets, fromV, toV, position) {
      const vars = toV || {};
      const arr = toArray(targets);
      if (!arr.length) { warn('notarget' + type, 'target kosong pada', type); return this; }
      let start = this._pos(position) + (vars.delay || 0);
      const dur = type === 'set' ? 0 : (vars.duration !== undefined ? vars.duration : this.defaults.duration);
      const ease = parseEase(vars.ease !== undefined ? vars.ease : this.defaults.ease);
      const rep = vars.repeat || 0, yoyo = !!vars.yoyo, rd = vars.repeatDelay || 0;
      const total = rep < 0 ? 1e9 : dur * (rep + 1) + rd * rep;
      let stagger = vars.stagger, each = 0, sFrom = 'start';
      if (typeof stagger === 'number') each = stagger;
      else if (stagger && typeof stagger === 'object') { each = stagger.each !== undefined ? stagger.each : (stagger.amount || 0) / Math.max(1, arr.length - 1); sFrom = stagger.from || 'start'; }
      const order = i => sFrom === 'end' ? arr.length - 1 - i : sFrom === 'center' ? Math.abs(i - (arr.length - 1) / 2) : typeof sFrom === 'number' ? Math.abs(i - sFrom) : i;
      if (vars.onStart || vars.onComplete) warn('cb', 'onStart/onComplete tidak dipakai di mode render. Pakai onUpdate atau perFrame.');
      const imm = vars.immediateRender !== false;
      if (vars.keyframes) {
        const kfs = Array.isArray(vars.keyframes) ? vars.keyframes : [];
        const per = dur / Math.max(1, kfs.length);
        arr.forEach((tg, i) => {
          let t0 = start + order(i) * each;
          kfs.forEach(kf => {
            const d = kf.duration !== undefined ? kf.duration : per;
            const kv = Object.assign({}, kf, { duration: d, ease: kf.ease !== undefined ? kf.ease : (vars.ease !== undefined ? vars.ease : 'none') });
            delete kv.delay;
            this._add('to', tg, null, kv, t0 + (kf.delay || 0));
            t0 += d + (kf.delay || 0);
          });
        });
        this._lastStart = start; this._lastEnd = start + dur + each * (arr.length - 1);
        this._end = Math.max(this._end, this._lastEnd); return this;
      }
      const props = {};
      for (const k in vars) { if (SPECIAL.has(k)) continue; if (k === 'attr' || k === 'css') continue; props[k] = vars[k]; }
      if (vars.css) Object.assign(props, vars.css);
      const attrs = vars.attr || {};
      const fprops = fromV ? Object.assign({}, fromV, fromV.css || {}) : null;
      const fattrs = fromV && fromV.attr ? fromV.attr : {};
      arr.forEach((tg, i) => {
        const s0 = start + order(i) * each;
        const val = v => typeof v === 'function' ? v(i, tg, arr) : v;
        const push = (kind, prop, to, from, hasFrom) => {
          const tr = this._track(tg, kind, prop);
          let rel = 0, toVal = to;
          if (typeof to === 'string' && /^[-+]=/.test(to)) { rel = (to[0] === '-' ? -1 : 1) * parseFloat(to.slice(2)); toVal = undefined; }
          tr.segs.push({ start: s0, dur, ease, rep, yoyo, rd, total, to: toVal, rel, from, hasFrom, imm, isFrom: type === 'from' });
          tr.sorted = false;
        };
        if (type === 'from') {
          for (const k in props) { const [[kind, p], v] = normProp(tg, k, val(props[k])); push(kind, p, undefined, v, true); }
          for (const k in attrs) push('attr', k, undefined, val(attrs[k]), true);
        } else {
          for (const k in props) {
            const [[kind, p], v] = normProp(tg, k, val(props[k]));
            let f, hf = false;
            if (fprops) { for (const fk in fprops) { if (SPECIAL.has(fk) || fk === 'attr' || fk === 'css') continue;
              const [[fkind, fp], fv] = normProp(tg, fk, val(fprops[fk])); if (fkind === kind && fp === p) { f = fv; hf = true; } } }
            push(kind, p, v, f, hf);
          }
          for (const k in attrs) push('attr', k, val(attrs[k]), fattrs[k] !== undefined ? val(fattrs[k]) : undefined, fattrs[k] !== undefined);
          if (fprops) {   // properti yang hanya ada di "from"
            for (const fk in fprops) { if (SPECIAL.has(fk) || fk === 'attr' || fk === 'css') continue;
              const [[fkind, fp]] = normProp(tg, fk, 0);
              const has = Object.keys(props).some(k => { const [[kk, pp]] = normProp(tg, k, 0); return kk === fkind && pp === fp; });
              if (!has) warn('fromonly' + fk, `properti "${fk}" hanya ada di bagian from; tambahkan juga di bagian to.`); }
          }
        }
        if (vars.onUpdate) this.cbs.push({ start: s0, dur, ease, rep, yoyo, rd, total, fn: vars.onUpdate, params: vars.onUpdateParams || [], target: tg, targets: arr });
      });
      this._lastStart = start; this._lastEnd = start + total + each * (arr.length - 1);
      this._end = Math.max(this._end, rep < 0 ? start + dur : this._lastEnd);
      return this;
    }
    to(t, v, p) { return this._add('to', t, null, v, p); }
    from(t, v, p) { return this._add('from', t, null, v, p); }
    fromTo(t, f, v, p) { return this._add('fromTo', t, f, v, p); }
    set(t, v, p) { return this._add('set', t, null, Object.assign({}, v, { duration: 0 }), p); }
    call(fn, args, p) { const t = this._pos(p); this.calls.push({ t, fn, args: args || [] }); this._end = Math.max(this._end, t); return this; }
    addLabel(n, p) { this.labels[n] = this._pos(p); return this; }
    add(x, p) {
      if (typeof x === 'function') return this.call(x, [], p);
      if (typeof x === 'string') return this.addLabel(x, p);
      warn('addtl', 'tl.add(timeline) tidak didukung; tulis langsung di timeline utama.'); return this;
    }
    duration() { return this._end; }
    time() { return this._t; }
    progress(p) { if (p === undefined) return this._end ? this._t / this._end : 0; return this.seek(p * this._end); }
    play() { return this; } pause() { return this; } kill() { return this; }

    /* --- inti: nilai track pada waktu t --- */
    _prog(s, t) {
      if (s.dur <= 0) return 1;
      let local = t - s.start; if (local <= 0) return s.ease(0) * 0;
      const cyc = s.dur + s.rd, reps = s.rep < 0 ? 1e9 : s.rep;
      let i = Math.floor(local / cyc), lt;
      if (i > reps) { i = reps; lt = s.dur; } else { lt = Math.min(s.dur, local - i * cyc); }
      let p = Math.min(1, Math.max(0, lt / s.dur));
      if (s.yoyo && i % 2 === 1) p = 1 - p;
      return s.ease(p);
    }
    _base(tr) { if (tr.base === undefined) tr.base = readBase(tr.target, tr.kind, tr.prop); return tr.base; }
    _sort(tr) { if (!tr.sorted) { tr.segs.forEach((s, i) => s._i = i); tr.segs.sort((a, b) => a.start - b.start || a._i - b._i); tr.segs.forEach(s => { s._from = undefined; s._to = undefined; }); tr.sorted = true; } }
    _pre(tr) { const s0 = tr.segs[0]; return s0 && s0.hasFrom && s0.imm ? this._fromOf(tr, 0) : this._base(tr); }
    _valueBefore(tr, k, t) {
      let j = -1; for (let i = 0; i < k; i++) { if (tr.segs[i].start <= t + 1e-9) j = i; else break; }
      if (j < 0) return k === 0 ? this._base(tr) : this._pre(tr);
      const s = tr.segs[j]; return lerp(this._fromOf(tr, j), this._toOf(tr, j), this._prog(s, t), tr.prop);
    }
    _fromOf(tr, k) {
      const s = tr.segs[k];
      if (s._from === undefined) s._from = s.hasFrom ? s.from : this._valueBefore(tr, k, s.start);
      return s._from;
    }
    _toOf(tr, k) {
      const s = tr.segs[k];
      if (s._to === undefined) {
        if (s.isFrom) s._to = this._valueBefore(tr, k, s.start) ?? this._base(tr);
        else if (s.to === undefined && s.rel) { const f = this._fromOf(tr, k); s._to = (typeof f === 'number' ? f : parseFloat(f) || 0) + s.rel;
          if (typeof f === 'string' && /[a-z%]+$/i.test(f)) s._to = s._to + f.match(/[a-z%]+$/i)[0]; }
        else s._to = s.to;
      }
      return s._to;
    }
    _value(tr, t) {
      this._sort(tr);
      let j = -1; const S = tr.segs;
      for (let i = 0; i < S.length; i++) { if (S[i].start <= t + 1e-9) j = i; else break; }
      if (j < 0) return this._pre(tr);
      return lerp(this._fromOf(tr, j), this._toOf(tr, j), this._prog(S[j], t), tr.prop);
    }
    seek(t) {
      this._t = t;
      const touched = new Set();
      for (const tr of this.list) {
        const v = this._value(tr, t);
        if (tr.kind === 'tf') { tfState(tr.target); touched.add(tr.target); if (!tr.target.__tfv) tr.target.__tfv = {}; tr.target.__tfv[tr.prop] = v; continue; }
        if (v === tr.last) continue;
        tr.last = v; write(tr.target, tr.kind, tr.prop, v);
      }
      for (const el of touched) {
        const s = Object.assign({}, el.__tfb || TF, el.__tfv);
        const str = composeTF(s);
        if (el.__tfs !== str) { el.style.transform = str; el.__tfs = str; }
      }
      for (const c of this.cbs) {
        const p = t < c.start ? 0 : this._prog(c, t);
        const self = { progress: () => p, targets: () => c.targets, ratio: p, time: () => Math.max(0, t - c.start) };
        try { c.fn.apply(self, c.params); } catch (e) { console.error('[motion] onUpdate error', e); }
      }
      for (const c of this.calls) if (t >= c.t) { try { c.fn.apply(null, c.args); } catch (e) { console.error('[motion] call error', e); } }
      return this;
    }
  }

  /* ---------------- gsap.set di luar timeline ---------------- */
  function set(targets, vars) {
    for (const tg of toArray(targets)) {
      let tfTouched = false;
      for (const k in vars) {
        if (SPECIAL.has(k)) continue;
        if (k === 'attr') { for (const a in vars.attr) tg.setAttribute(a, vars.attr[a]); continue; }
        const [[kind, p], v] = normProp(tg, k, typeof vars[k] === 'function' ? vars[k](0, tg) : vars[k]);
        if (kind === 'tf') { if (!tg.__tfb) tg.__tfb = Object.assign({}, TF); tg.__tfb[p] = tfNum(p, v); tfState(tg)[p] = tg.__tfb[p]; tfTouched = true; }
        else write(tg, kind, p, v);
      }
      if (tfTouched && isEl(tg)) {
        const s = Object.assign({}, tg.__tfb, tg.__tfv || {});
        const str = composeTF(s); tg.style.transform = str; tg.__tfs = str;
      }
    }
  }

  /* ---------------- utils ---------------- */
  let seed = 7;
  const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
  const utils = {
    clamp: (a, b, v) => v === undefined ? (x => Math.min(b, Math.max(a, x))) : Math.min(b, Math.max(a, v)),
    mapRange: (a, b, c, d, v) => { const f = x => c + (x - a) * (d - c) / (b - a); return v === undefined ? f : f(v); },
    interpolate: (a, b, p) => { const f = x => lerp(a, b, x, ''); return p === undefined ? f : f(p); },
    random: (a, b, snap) => { if (Array.isArray(a)) return a[Math.floor(rnd() * a.length)]; let v = a + rnd() * (b - a); if (snap) v = Math.round(v / snap) * snap; return v; },
    seed: s => { seed = s >>> 0 || 7; },
    wrap: (a, b, v) => { const r = b - a; const f = x => a + ((((x - a) % r) + r) % r); return v === undefined ? f : f(v); },
    snap: (s, v) => { const f = x => Math.round(x / s) * s; return v === undefined ? f : f(v); },
    toArray,
    parseEase,
  };

  const notInTl = name => function () { warn('global' + name, `gsap.${name}() di luar timeline diabaikan. Pakai tl.${name}(..., detik).`); };
  const api = {
    timeline: o => new Timeline(o), set, utils, parseEase,
    to: notInTl('to'), from: notInTl('from'), fromTo: notInTl('fromTo'),
    registerPlugin() {}, config() {}, defaults() {}, ticker: { add() {}, remove() {}, lagSmoothing() {} },
    getProperty: (el, p) => { p = ALIAS[p] || p; return p in TF ? tfState(el)[p] : getComputedStyle(el)[p]; },
    version: 'motion-1',
  };
  root.motion = api;
  root.gsap = api;
})(typeof window !== 'undefined' ? window : globalThis);
