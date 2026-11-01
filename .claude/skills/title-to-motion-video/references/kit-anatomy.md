# Motion-as-Code kit — anatomy, toolkit, pitfalls

Read this before writing plate code. Paths are relative to the project root.

## Contents
1. Layout
2. How timing works (script → lyrics.json → plates)
3. Writing a plate (skeleton)
4. Toolkit cheat sheet (`scenes/_vo.ts`, `_motifs.ts`, engine helpers)
5. Post-processing overrides
6. Commands
7. Pitfalls (learned the hard way)

## 1. Layout

| Path | What |
|---|---|
| `audio/voiceover.mp3` | the voice (drives the audio clock in preview + mux in render) |
| `audio/sfx/*.mp3` | 28 sound effects, `name_N.mp3` alternate takes |
| `data/lyrics.json` | word timings, written by `analysis/align_vo.py` |
| `data/audio.json` | duration, loudness envelopes, word onsets, nominal 120 BPM grid (`analysis/audio_vo.py`) |
| `analysis/models/` | wav2vec2 ONNX model for alignment (offline) |
| `app/src/engine/` | the pdoom-video engine — **do not edit** |
| `app/src/scenes/_vo.ts`, `_motifs.ts` | shared toolkit for plates |
| `app/src/scenes/<id>.ts` | one plate each (default export: a `Scene` subclass) |
| `app/src/scenes/animatic.ts` | generic placeholder plate (karaoke of the lines in its window); any timeline entry can use it |
| `CLAUDE.md` | project rules written by `new_project.py` (voice step allowed, renders only on request) |
| `app/src/timeline.ts` | which plate plays when |
| `app/scripts/render.ts` | stills / sheet / video renderer (headless Chrome + ffmpeg) |
| `out/` | renders; `out/wip/` for stills |

The canvas is fixed at **1920×1080** (`engine/gl.ts` W, H), 60 fps. Total length = `data/audio.json`
→ `duration` (voice length + 0.3 s tail).

## 2. How timing works

1. `SCRIPT` in `analysis/align_vo.py` is a list of display lines. Words split on spaces. `SPOKEN`
   maps a display token to the words actually said (`"MP4": ["EM","PEE","FOUR"]`, `"—": []`).
   Multi-part words get `syl` spans so each spoken part can light up separately (`parts(w)`).
2. `align_vo.py` → `data/lyrics.json`: `{ lines: [{ text, start, end, words: [{ w, start, end, syl? }] }] }`.
3. Plates find their words **by content**, at `init()`:
   - `lineOf(ly, 'substring of the line')` — case/quote-insensitive substring; throws
     `lyric not found` if missing. `nth` picks a later occurrence.
   - `wordOf(line, 'word', nth)` — matches the normalised word (`a-z0-9()` only, so `"Effects?"` ==
     `'Effects'`); throws `word not found`.
   - Store times like `this.tX = w.word.start` and animate with `prog(t, a, b)`, `pulse(t, t0)`.
4. `timeline.ts` → `cut('anchor')` puts each plate boundary in the pause before the line containing
   the anchor (0.04–0.18 s before its first word). Last plate ends at `au.duration`.
5. Because everything keys off words, a re-read with the same script re-times the whole video for
   free; a changed script means updating every lookup that changed.

## 3. Writing a plate (skeleton)

```ts
import type * as THREE from 'three';
import { Scene, type Frame, type PostOverrides } from '../engine/scene';
import { Layer2D } from '../engine/gl';
import { LineBatch } from '../engine/lines';
import { rgba } from '../engine/palette';
import { F, font } from '../engine/type';
import { type Line, type Word } from '../engine/lyrics';
import { ease, prog, pulse } from '../engine/util';
import { Cam2D, Plot, gridPass, setGrid, drawKaraoke, placeRow, setWorld, label, drawPen, w2s, lineOf, wordOf, pt, type KWord } from './_vo';

export default class Example extends Scene {
  cam = new Cam2D();
  grid = gridPass(24, 96);
  plot = new Plot();
  glow = new LineBatch(20000);   // plotter strokes (additive glow)
  fx = new LineBatch(20000);     // the spark / pen
  ui = new Layer2D();            // Canvas2D layer composited on top
  kw: KWord[] = [];
  w: Record<string, Word> = {};
  L!: Line;

  override init() {                       // precompute EVERYTHING here from word times
    const ly = this.ctx.lyrics;
    this.L = lineOf(ly, 'Then that code');
    for (const k of ['then', 'code', 'video'] as const) this.w[k] = wordOf(this.L, k);
    const w = this.w;
    this.kw.push(...placeRow([w.then!, w.code!], -400, -200, 72, F.archivo(100, 700), 'row1').words);
    this.plot.add([pt(-400, 0), pt(400, 0)], w.code!.start, w.code!.end, 'plot', { pen: true, width: 2 });
    this.cam.key(this.ctx.start, 0, 0, 1.2, 0);
    this.cam.key(w.video!.start, 120, 40, 0.9, 0.01, ease.inOutCubic);
  }

  override render(f: Frame, out: THREE.WebGLRenderTarget): PostOverrides {
    const { renderer, comp } = this.ctx;
    const t = f.t, c = this.cam.at(t);
    setGrid(this.grid, c, { reveal: [0, 0, 1e5], ink: 0.7 });
    this.grid.render(renderer, out);                       // 1. background (must fully overwrite out)
    const L = this.glow; L.clear(); this.plot.draw(t, c, L); L.render(renderer, out);   // 2. strokes
    const U = this.ui; U.clear();
    drawKaraoke(U.ctx, c, t, this.kw);                     // 3. 2D type / UI
    this.plot.drawNotes(t, c, U.ctx);
    comp.draw(renderer, U.upload(), out);
    const X = this.fx; X.clear();                          // 4. the spark rides the pen
    drawPen(X, t, (tt) => { const q = this.plot.penAt(tt); return q ? w2s(c, q.x, q.y) : null; });
    X.render(renderer, out);
    return { bloom: 0.7, bloomThreshold: 0.84, vignette: 0.42, grain: 0.05, zoom: 1 + 0.02 * pulse(t, this.w.video!.start, 0.1) };
  }
}
```

Rules that keep it deterministic: no `Math.random()` or `Date` (use `hash`, `noise1`, `mulberry32`),
no state carried between `render()` calls (or set `stateful = true` and implement `reset()`), and
`render` must overwrite `out` completely. Times come from `f.t` (song seconds); `f.lt`/`f.p` are
local time / 0..1 progress through the plate.

## 4. Toolkit cheat sheet

**Camera** — `Cam2D.key(t, cx, cy, zoom, roll = 0, ease?)`; `cam.at(t)` → `{cx, cy, z, roll}`.
World units are px, y down, (0,0) = frame centre at zoom 1. `w2s(c, x, y)` world→screen,
`setWorld(ctx, c, x, y, scale?, rot?)` puts the 2D context in world space at (x, y) — reset with
`ctx.setTransform(1,0,0,1,0,0)` afterwards.

**Plot (the plotter)** — strokes on a timetable, drawn statelessly:
- `add(points, t0, t1, kind, { pen, ez, width, dash, alpha, group, col })` — kind:
  `'axis' | 'cons' | 'prim' | 'dim' | 'hatch' | 'plot' | 'ghost' | 'ink' | 'signal'`. `pen: true`
  means the spark draws it (and `penAt(t)` follows it).
- `wp(point, t, dur)` — pen waypoint (travel without drawing).
- `note(text, x, y, t0, { size, col, a, spacing, group })` — mono annotation.
- `dimension(a, b, label, t0, group, size, side)` — engineering dimension line.
- `writeWords(text, words, strokeFont, size, x, y, group)` — single-stroke plotter lettering
  written word by word as said.
- `paper = true` for bone-paper plates (ink strokes). `alpha = (group, t) => …` per-group fades.
- Geometry helpers: `pt`, `arc`, `rectPts`, `bezier`, `resample`, `lengths`, `at`.

**Karaoke type** — `placeRow(words, x, baselineY, size, fam, group, { texts, ant, hot, done })`
lays a row; `drawKaraoke(ctx, cam, t, kws, { alpha, paper, pop, outline })` draws: unsaid = ash
hairline, being said = signal wipe, said = cools to bone (ink on paper). `fitRow(texts, width, fam)`
sizes a row to a width.

**Backgrounds** — `gridPass(minor, major)` + `setGrid(g, cam, { reveal, ink, paper, fade })` for
graph paper; paper plates use an `FSPass` shader (see `pipeline.ts` / `verdict.ts` `PAPER`).

**Spark** — `drawPen(lineBatch, t, headAt, { scale, rate })` (spark following a path),
`sparkHead(lb, x, y, t, scale, intensity)`, `sparkParticles(lb, t, headAt, { rate, speed, life })`.

**Labels/UI** — `label(ctx, text, x, y, { size, col, spacing, weight, align })` (tracked caps),
`arrowHead`, `triangle`, `returnArrow`, `mixCss(a, b, k, alpha)` for colour blends.

**Engine helpers** — `prog(x, a, b, easeFn?)` clamped progress; `pulse(t, t0, halfLife)` decaying
hit; `ease.*` (outExpo, inOutCubic, outBack…); `clamp`, `lerp`, `hash(...)`, `noise1(x, seed)`.
Palette keys for `rgba(key, a)`: `ink, ink2, graphite, ash, bone, signal, ember, blood, acid`
(acid = one rare accent). Fonts: `F.archivo(width 62–125, weight 300–900)`, `F.mono(weight)`
(IBM Plex Mono), `F.serif(weight, italic)` (Cormorant); `font(fam, px)`; `layout`, `measure`.

## 5. Post-processing overrides (return from `render`)

`bloom, bloomThreshold, vignette, grain, halation, ca` (chromatic aberration), `paper` (1 on bone
paper — flips HUD to ink), `zoom` (punch-ins: `1 + 0.03 * pulse(...)`), `shake: [x, y]`, `flash`
(additive white), `fade`, `invert`, `frame` (0..1 crop-mark frame — 1 only on the bookends).
Dark plates typically: `bloom 0.7, bloomThreshold 0.84, vignette 0.42, grain 0.05`.
Paper plates: `bloom 0.15, bloomThreshold 1.4, vignette 0.28, grain 0.04, paper: 1`.

## 6. Commands (from `app/`)

```bash
bun scripts/render.ts stills --t 12.5,40.2 --only <id> --out ../out/wip       # PNG stills
bun scripts/render.ts sheet --cuts --out ../out/wip/cuts.png                  # one frame per cut
bun scripts/render.ts sheet --from 20 --to 35 --n 12 --out ../out/wip/s.png   # contact sheet
bun scripts/render.ts video --samples auto --min-samples 4 --max-samples 12 --shutter 0.5 --crf 17 --out ../out/<slug>.mp4
```
Stills/sheets render in seconds. `--only` loads just those plates — times outside them render
blank/flat colour, which is expected, not a bug. Preview URL `?t=35` starts at 35 s; keys: space
play/pause, ←/→ ±1 s, `[`/`]` prev/next plate, `l` loop plate. Clicking the canvas also toggles play.

## 7. Pitfalls (learned the hard way)

- **`-shortest` chops the tail.** Muxing audio shorter than the video with plain `-shortest`
  drops the final frames (the implode + loop frame). Always pad audio: `-af apad … -shortest`.
  `new_project.py` patches `render.ts`; apply the same to manual ffmpeg muxes.
- **`sfx_mix.py` hard-codes `DUR`** in the template; `new_project.py` makes it read `audio.json`.
  Its cue sheet uses the *template's* words — rewrite cues per new plate before running it.
- **Windows console encoding.** The analysis scripts print `→`, curly quotes and `…`; run them
  with `PYTHONIOENCODING=utf-8` or they crash after doing the work.
- **No `uv` on this machine.** Use the shared venv python printed by `new_project.py` instead of
  `python -m uv run …`.
- **Port 5173 is shared.** `render.ts` defaults to whatever answers on `localhost:5173` (often the
  template's or another project's dev server) and silently renders *that* project. Each project gets
  its own port from `new_project.py`; always pass `--url http://localhost:<PREVIEW_PORT>` (with the
  preview running), or an unused port to make render.ts start a private server for this project.
- **`preview_start` reads the session's `.claude/launch.json`**, not the project's — merge the
  printed `LAUNCH_ENTRY` into the working directory's launch.json.
- **Stale data until Stage 4.** A fresh project still has the template's `lyrics.json`/`audio.json`
  (92.64 s) and plates; they only become this video's after alignment and the timeline rewrite.
- **Lazy plate loading during renders.** A full render loads each plate when it reaches it; editing
  plate files mid-render leaks half-finished code into the MP4. Don't edit while rendering.
- **Hard-coded template numbers in plates** (e.g. `frames.ts` shows `5558` frames and `01:32.64`)
  — derive such readouts from `this.ctx.audio.duration` instead when reusing a plate.
- **The closing hold.** The last plate holds its slam `HOLD` seconds past the last word, into the
  0.3 s silent tail added by `audio_vo.py` (`TAIL`). Keep `HOLD ≤ TAIL` or the implode runs out of
  room before the bookend frame at `end − 0.08`.
