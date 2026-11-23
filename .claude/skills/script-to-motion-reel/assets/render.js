// Render satu potongan frame ke MP4. Biasanya dipanggil oleh render_all.py, bukan langsung.
//   node render.js <frameMulai> <frameSelesai> <out.mp4> [url]
//   node render.js --info <out.json> [url]        tulis TOTAL dan daftar SFX dari halaman
const { spawn } = require('child_process');
const { openStage } = require('./_chrome');
const path = require('path'), fs = require('fs');
const FPS = 30;
const a = process.argv.slice(2);

(async () => {
  if (a[0] === '--info') {
    const url = a[2] || ('file://' + path.resolve('index.html'));
    const { b, p, errs } = await openStage(url);
    const info = await p.evaluate(() => ({ total: window.TOTAL, sfx: window.SFX }));
    info.errors = errs;
    fs.writeFileSync(a[1], JSON.stringify(info));
    console.log('info', a[1], 'TOTAL', info.total, 'SFX', info.sfx.length, errs.length ? ('ERRORS ' + errs.slice(0, 3).join(' | ')) : '');
    await b.close(); return;
  }
  const [start, end, out] = [+a[0], +a[1], a[2]];
  const url = a[3] || ('file://' + path.resolve('index.html'));
  const { b, p, errs } = await openStage(url);
  if (errs.length) console.log('PAGE ERRORS', errs.slice(0, 5));
  const tmp = out + '.part.mp4';
  const ff = spawn(process.env.FFMPEG_BIN || 'ffmpeg',
    ['-nostdin', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
     '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', tmp]);
  for (let f = start; f < end; f++) {
    await p.evaluate(t => seek(t), f / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  const code = await new Promise(r => ff.on('close', r));
  await b.close();
  if (code !== 0) { console.error('ffmpeg gagal untuk', out); process.exit(1); }
  fs.renameSync(tmp, out);   // file hanya muncul kalau potongan selesai utuh
  console.log('done', out);
})();
