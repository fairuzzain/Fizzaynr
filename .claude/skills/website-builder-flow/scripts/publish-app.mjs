#!/usr/bin/env node
// Publish an app to the thin apps-engine.
//
//   node scripts/publish-app.mjs <app-id> --dir <path>   # app dir: app.json + src/ + public/
//   node scripts/publish-app.mjs <app-id> --delete
//
// Env: ENGINE_URL (default personal POC apps-engine), PUBLISH_TOKEN.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const [, , appId, mode, arg] = process.argv;
const BASE = (process.env.ENGINE_URL || "").replace(/\/$/, "");
const TOKEN = process.env.PUBLISH_TOKEN || "";

if (!BASE || !TOKEN) {
  console.error("ENGINE_URL and PUBLISH_TOKEN env vars are required");
  process.exit(1);
}

if (!appId || !mode) {
  console.error("usage: publish-app.mjs <app-id> --dir <path> | --delete  (env: ENGINE_URL, PUBLISH_TOKEN, USER_ID)");
  process.exit(1);
}

const TEXT_EXT = new Set([".html", ".js", ".css", ".json", ".svg", ".txt"]);

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = path.join(dir, name);
    if (statSync(p).isDirectory()) yield* walk(p);
    else yield p;
  }
}

function collectAssets(pubDir) {
  const assets = {};
  if (!existsSync(pubDir)) return assets;
  for (const f of walk(pubDir)) {
    const rel = path.relative(pubDir, f).split(path.sep).join("/");
    assets[rel] = TEXT_EXT.has(path.extname(f).toLowerCase())
      ? { content: readFileSync(f, "utf8") }
      : { content: readFileSync(f).toString("base64"), b64: true };
  }
  return assets;
}

async function send(method, body) {
  const headers = { "content-type": "application/json", "x-publish-token": TOKEN };
  if (process.env.USER_ID) headers["x-user-id"] = process.env.USER_ID;
  const res = await fetch(`${BASE}/publish/${appId}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const out = await res.json().catch(() => ({}));
  if (!res.ok || !out.ok) {
    console.error(`${method} failed (${res.status}):`, JSON.stringify(out));
    process.exit(1);
  }
  return out;
}

if (mode === "--delete") {
  const out = await send("DELETE");
  console.log(`deleted ${out.app} (${out.deleted} keys)`);
  process.exit(0);
}

let body;
if (mode === "--dir") {
  const appDir = path.isAbsolute(arg) ? arg : path.join(root, arg);
  const manifest = JSON.parse(readFileSync(path.join(appDir, "app.json"), "utf8"));
  const modules = {};
  for (const f of walk(path.join(appDir, "src"))) {
    modules[path.relative(path.join(appDir, "src"), f)] = readFileSync(f, "utf8");
  }
  body = {
    main: manifest.main || "server.js",
    class_name: manifest.class_name || "App",
    socket_mode: manifest.socket_mode || "pump",
    modules,
    assets: collectAssets(path.join(appDir, "public")),
  };
} else {
  console.error(`unknown mode: ${mode}`);
  process.exit(1);
}

console.log(`publishing ${appId}: ${Object.keys(body.modules).length} module(s), ${Object.keys(body.assets).length} asset(s), ${body.socket_mode}`);
const out = await send("POST", body);
console.log(`published ${out.app} v${out.version} (${out.socket_mode})`);
console.log(`play: ${out.url}`);
