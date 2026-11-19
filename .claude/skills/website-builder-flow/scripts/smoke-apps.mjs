#!/usr/bin/env node
// Smoke test for the thin apps-engine: a full tic-tac-toe game through the
// PUMP-mode kernel app, then a join/state check on a DIRECT-mode app.
//
//   node scripts/smoke-apps.mjs [engine-base-url] [pump-app-id] [direct-app-id]

const BASE = (process.argv[2] || "").replace(/\/$/, "");
if (!BASE) { console.error("usage: smoke-apps.mjs <engine-base-url> [pump-app-id] [direct-app-id]"); process.exit(1); }
const PUMP = process.argv[3] || "tic-tac-toe";
const DIRECT = process.argv[4] || "blockade-v2";
const wsBase = BASE.replace(/^http/, "ws");

function mk(name, url) {
  const ws = new WebSocket(url);
  const q = [], w = [];
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    (w.shift() ?? ((x) => q.push(x)))(m);
  });
  return {
    name, ws,
    open: new Promise((res, rej) => {
      ws.addEventListener("open", res);
      ws.addEventListener("error", () => rej(new Error(`${name}: connect failed`)));
    }),
    send: (o) => ws.send(JSON.stringify(o)),
    next: (ms = 15000) => q.length
      ? Promise.resolve(q.shift())
      : new Promise((res, rej) => {
          const t = setTimeout(() => rej(new Error(`${name}: timeout`)), ms);
          w.push((m) => { clearTimeout(t); res(m); });
        }),
  };
}

async function until(p, f, label) {
  for (let i = 0; i < 50; i++) {
    const m = await p.next();
    if (m.type === "error" || m.t === "error") throw new Error(`${p.name}: ${m.error}`);
    if (f(m)) return m;
  }
  throw new Error(`${p.name}: never saw ${label}`);
}

// --- pump mode: full tic-tac-toe game --------------------------------------
{
  const room = "smoke-" + Math.random().toString(36).slice(2, 10);
  const url = `${wsBase}/a/${PUMP}/ws/${room}`;
  const a = mk("a", url), b = mk("b", url);
  await Promise.all([a.open, b.open]);
  a.send({ type: "join", playerId: "a" });
  await until(a, (s) => s.type === "state" && s.seats.includes("a"), "a seated");
  b.send({ type: "join", playerId: "b" });
  await until(a, (s) => s.type === "state" && s.status === "playing", "playing");
  let fin;
  for (const [p, c] of [[a, 0], [b, 3], [a, 1], [b, 4], [a, 2]]) {
    p.send({ type: "action", action: { cell: c } });
    fin = await until(p, (s) => s.type === "state" && s.view && s.view.board[c] !== null, `cell ${c}`);
  }
  if (fin.status !== "over") throw new Error("expected over, got " + fin.status);
  if (fin.result.winner !== "a") throw new Error("wrong winner: " + JSON.stringify(fin.result));
  console.log(`PUMP  PASS — full game on /a/${PUMP}/ws/${room}, winner ${fin.result.winner} (line ${fin.result.line.join(",")})`);
  a.ws.close(); b.ws.close();
}

// --- direct mode: join + teams + state sync --------------------------------
{
  const url = `${wsBase}/a/${DIRECT}/ws`;
  const a = mk("da", url);
  await a.open;
  a.send({ t: "join", name: "smoke-a" });
  const w = await until(a, (m) => m.t === "welcome", "welcome");
  a.send({ t: "state", pos: { x: 1, y: 1.05, z: 1 }, ry: 0, rx: 0, anim: 0 });
  await until(a, (m) => m.t === "states", "20Hz states");
  console.log(`DIRECT PASS — joined /a/${DIRECT}/ws as id ${w.id} (team ${w.team}), 20 Hz sync flowing`);
  a.ws.close();
}

console.log("PASS — thin engine hosts both modes");
process.exit(0);
