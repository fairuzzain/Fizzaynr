// ANIMATIC — a placeholder plate for any timeline entry that has no plate of its own yet.
// It shows the voiceover lines that start inside its window as karaoke on graph paper, one line at a
// time, so the whole video plays end to end (and cuts can be judged) before the real plates exist.
// Use it from timeline.ts as E('<id>', 'animatic', start, end); swap the file name for the real
// plate once it is written. Finds its lines by time, so it never throws on a changed script.
import type * as THREE from 'three';
import { Scene, type Frame, type PostOverrides } from '../engine/scene';
import { Layer2D } from '../engine/gl';
import { F } from '../engine/type';
import { type Line, type Word } from '../engine/lyrics';
import { noise1, prog, pulse } from '../engine/util';
import { gridPass, setGrid, drawKaraoke, placeRow, rowWidth, label, type KWord, type Cam } from './_vo';

const SIZE = 84, MAX_W = 1500;

export default class Animatic extends Scene {
  grid = gridPass(24, 96);
  ui = new Layer2D();
  kw: KWord[] = [];
  lines: Line[] = [];

  override init() {
    const { lyrics, start, end } = this.ctx;
    this.lines = lyrics.lines.filter((l) => l.start >= start - 0.05 && l.start < end);
    const fam = F.archivo(100, 700);
    const lh = SIZE * 1.15;
    this.lines.forEach((l, i) => {
      const rows: Word[][] = [[]];
      for (const w of l.words) {
        const cur = rows[rows.length - 1]!;
        if (cur.length && rowWidth([...cur, w].map((x) => x.w), SIZE, fam) > MAX_W) rows.push([w]);
        else cur.push(w);
      }
      rows.forEach((r, j) => {
        const width = rowWidth(r.map((x) => x.w), SIZE, fam);
        const y = (j - (rows.length - 1) / 2) * lh + SIZE * 0.35;
        this.kw.push(...placeRow(r, -width / 2, y, SIZE, fam, `l${i}`, { ant: 0.25 }).words);
      });
    });
  }

  /** Each line fades in just before it is said and out just before the next one. */
  lineAlpha(g: string, t: number) {
    const i = Number(g.slice(1));
    const l = this.lines[i]!, next = this.lines[i + 1];
    const tIn = l.start - 0.25, tOut = next ? next.start - 0.25 : this.ctx.end + 1;
    return prog(t, tIn, tIn + 0.2) * (1 - prog(t, tOut - 0.05, tOut + 0.15));
  }

  override render(f: Frame, out: THREE.WebGLRenderTarget): PostOverrides {
    const { renderer, comp } = this.ctx;
    const t = f.t;
    const c: Cam = { cx: 8 * noise1(t * 0.3, 1), cy: 6 * noise1(t * 0.27, 2), z: 1 + 0.04 * f.p, roll: 0 };
    setGrid(this.grid, c, { reveal: [0, 0, 1e5], ink: 0.6 });
    this.grid.render(renderer, out);
    const U = this.ui; U.clear();
    drawKaraoke(U.ctx, c, t, this.kw, { alpha: (g, tt) => this.lineAlpha(g, tt) });
    label(U.ctx, `ANIMATIC  ·  ${this.ctx.id.toUpperCase()}`, 64, 1024, { size: 14, col: 'rgba(156,151,143,0.85)', spacing: 4 });
    comp.draw(renderer, U.upload(), out);
    const hit = Math.max(0, ...this.lines.map((l) => pulse(t, l.start, 0.1)));
    return { bloom: 0.6, bloomThreshold: 0.84, vignette: 0.4, grain: 0.05, zoom: 1 + 0.01 * hit };
  }
}
