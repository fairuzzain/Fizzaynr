// Contact sheet untuk gerbang persetujuan: SATU frame per scene, tidak rapat.
//   node sheet.js <out.jpg> <t1,t2,...> [kolom] [url]
// Maksimal 6 kolom, thumbnail 300px. Lembar 8 kolom berisi 40 frame tidak terbaca.
const { openStage } = require('./_chrome');
const fs = require('fs'), os = require('os'), path = require('path');
const { execFileSync } = require('child_process');

const out = process.argv[2];
const ts = process.argv[3].split(',').map(Number).filter(n => !Number.isNaN(n));
const cols = Math.min(6, +(process.argv[4] || 5));
const url = process.argv[5] || ('file://' + path.resolve('index.html'));
const work = fs.mkdtempSync(path.join(os.tmpdir(), 'sheet'));
const W = 300;

(async () => {
  const { b, p, errs } = await openStage(url);
  let i = 0;
  for (const t of ts) {
    await p.evaluate(t => seek(t), t);
    await p.screenshot({ path: `${work}/${String(i++).padStart(3, '0')}.jpg`, type: 'jpeg', quality: 86 });
  }
  if (errs.length) console.log('PAGE ERRORS', errs.slice(0, 5));
  await b.close();
  const rows = Math.ceil(ts.length / cols);
  execFileSync(process.env.FFMPEG_BIN || 'ffmpeg',
    ['-nostdin', '-v', 'error', '-y', '-framerate', '1', '-i', `${work}/%03d.jpg`,
     '-vf', `scale=${W}:-2,tile=${cols}x${rows}:padding=6:margin=6:color=#101114`,
     '-frames:v', '1', '-q:v', '3', out]);
  console.log(`${out}  ${ts.length} frame, ${cols} kolom, thumbnail ${W}px`);
})();
