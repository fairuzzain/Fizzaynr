// Render the timeline frame-by-frame with headless Chromium and pipe PNGs into ffmpeg.
//   node scripts/render.mjs                       → out/ui.mp4 (full picture, slates in live slots)
//   node scripts/render.mjs --mode captions       → out/captions.mov (alpha; captions/supers for live slots only)
//   --from N --to M                               → partial range (absolute frames)
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { serve } from './server.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : d; };
const mode = arg('mode', 'render');
const tl = JSON.parse(fs.readFileSync(path.join(ROOT, 'timeline/timeline.json'), 'utf8'));
const from = +arg('from', 0), to = +arg('to', tl.durationFrames);
fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });
const out = path.join(ROOT, 'out', arg('out', mode === 'captions' ? 'captions.mov' : 'ui.mp4'));

const workers = +arg('workers', 4);
const port = 4100 + Math.floor(Math.random() * 500);
const server = await serve(port);
const browser = await chromium.launch();
const pages = await Promise.all(Array.from({ length: workers }, async () => {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('page error:', e.message); process.exitCode = 1; });
  await page.goto(`http://127.0.0.1:${port}/src/index.html?mode=${mode}`);
  await page.evaluate(() => window.__ready);
  await page.evaluate(() => document.fonts.ready);
  return page;
}));

const vcodec = mode === 'captions'
  ? ['-c:v', 'png', '-pix_fmt', 'rgba']
  : ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p'];
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(tl.fps), '-c:v', 'png', '-i', '-', ...vcodec, '-r', String(tl.fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });

// captions pass: only live shots carry pixels, every other frame is one cached transparent PNG
const isLive = (f) => tl.shots.some((s) => s.kind === 'live' && f >= s.start && f < s.end);
let blank = null;
async function grab(page, f) {
  if (mode === 'captions' && !isLive(f)) {
    if (!blank) { await page.evaluate((fr) => window.seek(fr), f); blank = await page.locator('#viewport').screenshot({ type: 'png', omitBackground: true }); }
    return blank;
  }
  await page.evaluate((fr) => window.seek(fr), f);
  return page.locator('#viewport').screenshot({ type: 'png', omitBackground: mode === 'captions', animations: 'disabled' });
}

const t0 = Date.now();
const done = new Map();
let next = from, flushed = from;
async function flush() {
  while (done.has(flushed)) {
    const png = done.get(flushed); done.delete(flushed);
    if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once('drain', r));
    if (flushed % 48 === 0) process.stdout.write(`\r${mode} frame ${flushed}/${to} (${((flushed - from + 1) / ((Date.now() - t0) / 1000)).toFixed(1)} fps)   `);
    flushed++;
  }
}
let flushing = Promise.resolve();
await Promise.all(pages.map(async (page) => {
  while (next < to) {
    const f = next++;
    done.set(f, await grab(page, f));
    flushing = flushing.then(flush);
    while (f - flushed > workers * 8) await new Promise((r) => setTimeout(r, 5)); // keep memory bounded
  }
}));
await flushing;
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
server.close();
console.log(`\nwrote ${path.relative(ROOT, out)}`);
