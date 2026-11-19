#!/usr/bin/env node
// render.mjs - capture frames of a reel-effects page (W/motion/index.html) in headless Chromium.
//
//   node render.mjs W OUT_DIR FRAMES
//     FRAMES: "A:B" (half-open range) or "1,5,9" (list). Writes OUT_DIR/%05d.jpg.
//
// effects.py shards a render across several of these processes and encodes the result. The page follows
// the hfPage contract: window.hfPage = { width, height, fps, frames, ready, render(t, f) }.
import { createServer } from "node:http";
import { createReadStream, mkdirSync, statSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require(
  require.resolve("playwright", {
    paths: [process.env.NODE_PATH ?? "", "/usr/local/lib/node_modules"],
  }),
);

const [W, OUT, SPEC] = process.argv.slice(2);
if (!W || !OUT || !SPEC) {
  console.error("usage: node render.mjs W OUT_DIR A:B|f1,f2,...");
  process.exit(2);
}
const ROOT = path.resolve(W);
const TYPES = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".json": "application/json",
  ".ttf": "font/ttf",
  ".jpg": "image/jpeg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".mp4": "video/mp4",
};

// Static server for the workspace only; the page makes no other requests.
const server = createServer((req, res) => {
  const file = path.resolve(ROOT, "." + decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!file.startsWith(ROOT + path.sep)) return res.writeHead(403).end();
  try {
    if (!statSync(file).isFile()) throw new Error();
  } catch {
    return res.writeHead(404).end();
  }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] ?? "application/octet-stream" });
  createReadStream(file).pipe(res);
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({ args: ["--disable-gpu", "--font-render-hinting=none"] });
try {
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("requestfailed", (r) => errors.push(`request failed: ${r.url()}`));
  await page.goto(`${base}/motion/index.html`);
  await page.waitForFunction(
    () => window.hfPage && typeof window.hfPage.render === "function",
    null,
    { timeout: 30000 },
  );
  const info = await page.evaluate(async () => {
    await window.hfPage.ready;
    await document.fonts.ready;
    const { width, height, fps, frames } = window.hfPage;
    return { width, height, fps, frames };
  });
  if (errors.length) throw new Error(errors.join("; "));
  await page.setViewportSize({ width: info.width, height: info.height });

  const frames = SPEC.includes(":")
    ? (([a, b]) => Array.from({ length: Math.max(0, b - a) }, (_, i) => a + i))(
        SPEC.split(":").map(Number),
      )
    : SPEC.split(",").map(Number);
  mkdirSync(OUT, { recursive: true });
  for (const f of frames) {
    if (!(f >= 0 && f < info.frames))
      throw new Error(`frame ${f} is outside 0..${info.frames - 1}`);
    await page.evaluate(async (f) => {
      await window.hfPage.render(f / window.hfPage.fps, f);
      window.EffectKit?.camera?.(f); // punch-in + shake on the page's hits, over the whole frame
    }, f);
    if (errors.length) throw new Error(`frame ${f}: ${errors.join("; ")}`);
    await page.screenshot({
      path: path.join(OUT, `${String(f).padStart(5, "0")}.jpg`),
      type: "jpeg",
      quality: 96,
    });
  }
  console.log(JSON.stringify({ rendered: frames.length, ...info }));
} finally {
  await browser.close();
  server.close();
}
