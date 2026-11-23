// node qa.js [url]
// Pemeriksa otomatis: safe zone, teks terpotong, kata telat, frame kosong, error halaman.
// Lolos semua != bagus. Tetap lihat contact sheet dan frame dari MP4 hasil render sendiri.
// Elemen yang memang sengaja melewati tepi (dekorasi, tile video wall) beri data-qa-skip.
const { openStage } = require('./_chrome');
const path = require('path');
const url = process.argv[2] || ('file://' + path.resolve('index.html'));

// Zona aman teks Script to Motion Reel: x 60-1020, y 140-1700 (di bawah 1700 tertutup UI platform).
const SZ = { left: 60, right: 1020, top: 140, bottom: 1700 };

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
      const cam = document.getElementById('cam');
      const all = [...cam.querySelectorAll('*')];
      for (const e of all) {
        if (eff(e) < 0.08) continue;
        const q = e.getBoundingClientRect();
        if (q.width < 2 || q.height < 2) continue;
        const isText = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        const isVisual = e.tagName === 'IMG' || e.tagName === 'svg' || e.classList.contains('card') || e.classList.contains('chip') || e.classList.contains('badge');
        if (isText || isVisual) out.ink++;
        if (!isText) continue;
        if (e.dataset.qaSkip !== undefined || e.closest('[data-qa-skip]')) continue;
        const label = (e.textContent || '').trim().slice(0, 28);
        if (q.left < SZ.left || q.right > SZ.right || q.top < SZ.top || q.bottom > SZ.bottom)
          out.bad.push([label, 'luar-safezone', Math.round(q.left), Math.round(q.top), Math.round(q.right), Math.round(q.bottom)]);
        for (let a = e; a && a !== cam; a = a.parentElement) {
          const cs = getComputedStyle(a);
          if (cs.overflow !== 'visible' && (a.scrollWidth > a.clientWidth + 2 || a.scrollHeight > a.clientHeight + 2) && !a.classList.contains('scene')) {
            const pr = a.getBoundingClientRect();
            if (q.right > pr.right + 2 || q.left < pr.left - 2 || q.bottom > pr.bottom + 2 || q.top < pr.top - 2) {
              out.bad.push([label, 'teks-terpotong', Math.round(q.width), Math.round(pr.width)]); break; }
          }
        }
      }
      return out;
    }, SZ);
    for (const x of r.bad) { const k = x[0] + '|' + x[1]; (hits[k] = hits[k] || []).push(+t.toFixed(2)); }
    if (r.ink === 0) empty.push(+t.toFixed(2));
  }

  // kata telat: setiap kata dari line() harus sudah tampil 0,45 dtk setelah waktunya
  const late = await p.evaluate(async () => {
    const out = [];
    const eff = el => { let o = 1;
      for (let e = el; e && e !== document.body; e = e.parentElement) {
        const cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || cs.display === 'none') return -1;
        o *= +cs.opacity; }
      return o; };
    for (const s of document.querySelectorAll('#cam .w')) {
      if (s._t === undefined) continue;
      await seek(s._t + 0.45);
      const o = eff(s);
      if (o >= 0 && o < 0.9 && +getComputedStyle(s).opacity < 0.9) out.push([+(+s._t).toFixed(2), s.textContent, +o.toFixed(2)]);
    }
    return out;
  });

  const keys = Object.keys(hits);
  console.log('=== QA ===');
  console.log('durasi        :', total, 'dtk');
  console.log('error halaman :', errs.length ? errs.slice(0, 6) : 'tidak ada');
  console.log('frame kosong  :', empty.length ? empty.slice(0, 30) : 'tidak ada');
  console.log('kata telat    :', late.length ? late : 'tidak ada');
  if (!keys.length) console.log('safe zone & potong: bersih');
  else {
    console.log('temuan        :', keys.length);
    for (const k of keys) {
      const a = hits[k];
      console.log('  -', k, '| n=' + a.length, '| t=' + a.slice(0, 6).join(',') + (a.length > 6 ? ',...' : ''));
    }
    console.log('  (muncul 1-2 kali saat animasi masuk/keluar masih wajar; yang muncul terus harus diperbaiki)');
  }
  await b.close();
  process.exit(errs.length || late.length || empty.length ? 1 : 0);
})();
