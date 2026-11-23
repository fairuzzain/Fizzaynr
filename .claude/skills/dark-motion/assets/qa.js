// node qa.js [url]
// Pemeriksa otomatis: safe zone, overflow, sinkron kata, frame kosong, error halaman.
// Lolos semua != bagus. Tetap lihat frame dari MP4 hasil render sendiri.
const { openStage } = require('./_chrome');
const path = require('path');
const url = process.argv[2] || ('file://' + path.resolve('index.html'));

// Safe zone: batas bawah 1560, di bawah itu ada caption dan tombol aplikasi.
const SZ = { left: 125, right: 955, top: 150, bottom: 1560 };

(async () => {
  const { b, p, errs } = await openStage(url);
  const total = await p.evaluate(() => window.TOTAL);

  const hits = {}, empty = [];
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
      const els = [...ov.querySelectorAll('*')].filter(e =>
        e.classList.contains('card') || e.classList.contains('cap') ||
        [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
      for (const e of els) {
        if (e.closest('.cap') && !e.classList.contains('cap')) continue;
        if (e.dataset.qaSkip !== undefined || e.closest('[data-qa-skip]')) continue;
        if (eff(e) < 0.08) continue;
        const q = e.getBoundingClientRect();
        if (q.width < 2) continue;
        out.ink++;
        const label = (e.textContent || '').trim().slice(0, 28) || e.className;
        if (q.left < SZ.left || q.right > SZ.right || q.top < SZ.top || q.bottom > SZ.bottom)
          out.bad.push([label, 'safezone', Math.round(q.left), Math.round(q.top), Math.round(q.right), Math.round(q.bottom)]);
        if (e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow !== 'visible')
          out.bad.push([label, 'teks-terpotong', e.scrollWidth, e.clientWidth]);
      }
      return out;
    }, SZ);
    for (const x of r.bad) { const k = x[0] + '|' + x[1]; (hits[k] = hits[k] || []).push(+t.toFixed(2)); }
    if (r.ink === 0) empty.push(+t.toFixed(2));
  }

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
    console.log('  (elemen yang hanya keluar beberapa frame saat animasi masuk/keluar masih wajar;');
    console.log('   elemen yang memang sengaja melewati tepi diberi data-qa-skip)');
  }
  await b.close();
  process.exit(errs.length || late.length ? 1 : 0);
})();
