// Grab stills at given absolute frames: node scripts/stills.mjs 10 120 900 → out/stills/f00010.png …
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { serve } from './server.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const frames = process.argv.slice(2).map(Number);
const dir = path.join(ROOT, 'out/stills');
fs.mkdirSync(dir, { recursive: true });
const port = 4600 + Math.floor(Math.random() * 300);
const server = await serve(port);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', (e) => console.error('page error:', e.message));
page.on('console', (m) => m.type() === 'error' && console.error('console:', m.text()));
await page.goto(`http://127.0.0.1:${port}/src/index.html?mode=render`);
await page.evaluate(() => window.__ready);
for (const f of frames) {
  await page.evaluate((fr) => window.seek(fr), f);
  await page.locator('#viewport').screenshot({ path: path.join(dir, `f${String(f).padStart(5, '0')}.png`) });
}
await browser.close();
server.close();
console.log(`wrote ${frames.length} stills to out/stills`);
