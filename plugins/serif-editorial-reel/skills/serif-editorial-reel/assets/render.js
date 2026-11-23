// node render.js <frameStart> <frameEnd> <out.mp4> [sfx.json] [url]
// Render deterministik: panggil seek(f/30) tiap frame, pipe JPEG ke ffmpeg.
// Jalankan dua separuh paralel. Kalau modul tidak ketemu:
//   NODE_PATH=/opt/npm-tools/node_modules node render.js ...
const { openStage } = require('./_chrome');
const path = require('path');
const { spawn } = require('child_process');
const FPS = 30;
const [start, end, out] = [+process.argv[2], +process.argv[3], process.argv[4]];
const sfxOut = process.argv[5];
const url = process.argv[6] || ('file://' + path.resolve('index.html'));

(async () => {
  const { b, p, errs } = await openStage(url);
  await p.waitForTimeout(800);
  if (errs.length) console.log('PAGE ERRORS', errs.slice(0, 5));
  if (sfxOut) {
    require('fs').writeFileSync(sfxOut, JSON.stringify(
      await p.evaluate(() => ({ sfx: window.SFX, total: window.TOTAL }))));
  }
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe',
    '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', out]);
  for (let f = start; f < end; f++) {
    await p.evaluate(t => seek(t), f / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(out, f);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log('done', out);
})();
