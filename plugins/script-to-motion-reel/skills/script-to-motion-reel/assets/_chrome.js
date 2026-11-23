// Cari Chromium + Playwright yang sudah ada, dan buka halaman video sampai siap.
// Dipakai bersama oleh render.js, qa.js, sheet.js, snap.js.
const fs = require('fs'), path = require('path');

function findChrome() {
  if (process.env.CHROME_BIN && fs.existsSync(process.env.CHROME_BIN)) return process.env.CHROME_BIN;
  try {
    const p = pw().chromium.executablePath();
    if (p && fs.existsSync(p)) return p;
  } catch (e) { /* lanjut cari manual */ }
  for (const c of ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'])
    if (fs.existsSync(c)) return c;
  const roots = [path.join(process.env.HOME || '', '.cache/ms-playwright'),
                 path.join(process.env.HOME || '', 'Library/Caches/ms-playwright')];
  const names = ['chrome-headless-shell', 'headless_shell', 'chrome', 'Google Chrome for Testing'];
  for (const root of roots) {
    if (!fs.existsSync(root)) continue;
    const stack = [root];
    while (stack.length) {
      const d = stack.pop();
      let ents = [];
      try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch (e) { continue; }
      for (const e of ents) {
        const f = path.join(d, e.name);
        if (e.isDirectory()) stack.push(f);
        else if (names.includes(e.name)) return f;
      }
    }
  }
  return null;
}

function launchOpts(extra = {}) {
  const exe = findChrome();
  const base = { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-dev-shm-usage', '--allow-file-access-from-files'] };
  if (extra.args) base.args = base.args.concat(extra.args);
  return Object.assign(exe ? { executablePath: exe } : {}, extra, { args: base.args });
}

// Cari modul playwright di beberapa lokasi umum.
let _pw = null;
function pw() {
  if (_pw) return _pw;
  const tries = [
    () => require('playwright'),
    () => require('playwright-core'),
    () => require(path.join(process.cwd(), 'node_modules/playwright')),
    () => require(path.join(process.cwd(), 'node_modules/playwright-core')),
    () => require(path.join(process.cwd(), '.tools/node_modules/playwright-core')),
    () => require(path.join(process.env.HOME || '', '.cache/script-to-motion-reel/node_modules/playwright-core')),
    () => require('/opt/npm-tools/node_modules/playwright'),
    () => require('/opt/npm-tools/node_modules/playwright-core'),
  ];
  if (process.env.PW_MODULE) tries.unshift(() => require(process.env.PW_MODULE));
  for (const t of tries) { try { _pw = t(); return _pw; } catch (e) { /* coba berikutnya */ } }
  console.error('Playwright tidak ketemu. Jalankan preflight.sh lagi, lalu `source <build>/env.sh`.');
  process.exit(2);
}

// Buka index.html, tunggu READY. Gagal cepat kalau template error.
async function openStage(url, { scale = 1 } = {}) {
  const { chromium } = pw();
  const b = await chromium.launch(launchOpts());
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: scale });
  const errs = [];
  p.on('pageerror', e => errs.push('JS: ' + e.message));
  p.on('requestfailed', r => errs.push('REQ: ' + r.url().slice(-90)));
  p.on('console', m => { if (m.type() === 'error' || /\[motion\]|ikon hilang/.test(m.text())) errs.push('LOG: ' + m.text().slice(0, 200)); });
  await p.goto(url, { waitUntil: 'load' });
  await p.waitForFunction('window.READY || window.TEMPLATE_ERROR', null, { timeout: 180000 });
  const te = await p.evaluate(() => window.TEMPLATE_ERROR || null);
  if (te) { console.error('HALAMAN ERROR (cek scenes.js):\n' + te); await b.close(); process.exit(3); }
  return { b, p, errs };
}

module.exports = { findChrome, launchOpts, pw, openStage };
