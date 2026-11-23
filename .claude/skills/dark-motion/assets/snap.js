// Ambil beberapa frame besar untuk diperiksa sendiri saat membangun scene (bukan untuk user).
//   node snap.js <folderHasil> <t1> <t2> ... [--url <url>] [--scale 0.5]
const { openStage } = require('./_chrome');
const fs = require('fs'), path = require('path');
const args = process.argv.slice(2);
const pick = f => { const i = args.indexOf(f); if (i < 0) return null; const v = args[i + 1]; args.splice(i, 2); return v; };
const url = pick('--url') || ('file://' + path.resolve('index.html'));
const scale = +(pick('--scale') || 0.5);
const dir = args.shift();
const ts = args.map(Number).filter(n => !Number.isNaN(n));
(async () => {
  fs.mkdirSync(dir, { recursive: true });
  const { b, p, errs } = await openStage(url, { scale });
  for (const t of ts) {
    await p.evaluate(t => seek(t), t);
    const f = path.join(dir, `t_${t}.jpg`);
    await p.screenshot({ path: f, type: 'jpeg', quality: 82 });
    console.log(f);
  }
  if (errs.length) console.log('PAGE ERRORS', errs.slice(0, 5));
  await b.close();
})();
