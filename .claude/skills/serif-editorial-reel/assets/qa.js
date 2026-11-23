// node qa.js [url]
// Pemeriksa otomatis: safe zone, overflow, sinkron kata, frame kosong, error halaman.
// Lolos semua != bagus. Tetap lihat snapshot sendiri.
const { openStage } = require('./_chrome');
const path = require('path');
const url = process.argv[2] || ('file://' + path.resolve('index.html'));

// Safe zone reels
// sama dengan SKILL.md: x 125-955, y 150-1720
const SZ = { left: 125, right: 955, top: 150, bottom: 1720, railX: 960, railY: 1100 };

(async () => {
  const { b, p, errs } = await openStage(url);
  await p.waitForTimeout(600);
  const total = await p.evaluate(() => window.TOTAL);

  // --- 1. safe zone + overflow, disampel tiap 0.25 dtk ---
  const hits = {};
  const empty = [];
  for (let t = 0.1; t < total; t += 0.25) {
    await p.evaluate(t => seek(t), t);
    const r = await p.evaluate(SZ => {
      const out = { bad: [], ink: 0 };
      const eff = el => { let o = 1;
        for (let e = el; e && e !== document.body; e = e.parentElement) {
          const cs = getComputedStyle(e);
          if (cs.visibility === 'hidden' || cs.display === 'none') return 0;
          o *= +cs.opacity; }
        return o; };
      const ov = document.getElementById('ov');
      // isi visual (gambar, panel berlatar, HP) dihitung sebagai isi, tapi tidak dicek safe zone
      for (const e of ov.querySelectorAll('img,.phone,div')) {
        if (eff(e) < 0.08) continue;
        const cs = getComputedStyle(e), q = e.getBoundingClientRect();
        if (e.tagName === 'IMG' || e.classList.contains('phone') ||
            ((cs.backgroundImage !== 'none' || cs.backgroundColor !== 'rgba(0, 0, 0, 0)') && q.width * q.height > 20000)) { out.ink++; break; }
      }
      const els = [...ov.querySelectorAll('*')].filter(e =>
        e.classList.contains('card') || e.classList.contains('cap') ||
        [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
      for (const e of els) {
        if (e.closest('.cap') && !e.classList.contains('cap')) continue;
        if (eff(e) < 0.08) continue;
        const q = e.getBoundingClientRect();
        if (q.width < 2) continue;
        out.ink++;
        if (e.dataset.qaSkip !== undefined || e.closest('[data-qa-skip]')) continue;
        const label = (e.textContent || '').trim().slice(0, 28) || e.className;
        if (q.left < SZ.left || q.right > SZ.right || q.top < SZ.top || q.bottom > SZ.bottom)
          out.bad.push([label, 'safezone', Math.round(q.left), Math.round(q.top), Math.round(q.right), Math.round(q.bottom)]);
        else if (q.bottom > SZ.railY && q.right > SZ.railX)
          out.bad.push([label, 'rail-kanan', Math.round(q.right), Math.round(q.bottom)]);
        if (e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow !== 'visible')
          out.bad.push([label, 'teks-terpotong', e.scrollWidth, e.clientWidth]);
      }
      return out;
    }, SZ);
    for (const x of r.bad) { const k = x[0] + '|' + x[1]; (hits[k] = hits[k] || []).push(+t.toFixed(2)); }
    if (r.ink === 0) empty.push(+t.toFixed(2));
  }

  // --- 2. sinkron kata ---
  const late = await p.evaluate(async () => {
    const out = [];
    for (const [c] of (window.CAPS || [])) {
      for (const s of c.querySelectorAll('.cw')) {
        if (s._t === undefined) continue;
        await seek(s._t + 0.3);
        if (getComputedStyle(c).visibility !== 'visible') continue;
        const o = +getComputedStyle(s).opacity;
        if (o < 0.95) out.push([s._t, s.textContent, +o.toFixed(2)]);
      }
    }
    return out;
  });

  const keys = Object.keys(hits);
  console.log('=== QA ===');
  console.log('durasi        :', total, 'dtk');
  console.log('error halaman :', errs.length ? errs.slice(0, 6) : 'tidak ada');
  console.log('frame kosong  :', empty.length ? empty : 'tidak ada');
  console.log('kata telat    :', late.length ? late : 'tidak ada');
  if (!keys.length) console.log('safe zone     : bersih');
  else {
    console.log('safe zone     :', keys.length, 'temuan');
    for (const k of keys) {
      const a = hits[k];
      console.log('  -', k, '| n=' + a.length, '| t=' + a.slice(0, 6).join(',') + (a.length > 6 ? ',...' : ''));
    }
    console.log('  (kartu yang hanya keluar beberapa frame saat animasi masuk/keluar masih wajar)');
  }
  await b.close();
  process.exit(errs.length || empty.length || late.length ? 1 : 0);
})();
