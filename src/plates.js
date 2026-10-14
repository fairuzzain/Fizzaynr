// Procedural stand-in "footage" for thumbnails, viewer and preview cards:
// a cyclist on a coastal road. Swap for real renders by dropping images into
// assets/ and pointing scenes at them; everything here is deterministic in t.
import { rand } from './util.js';

const PALETTES = {
  warm: { sky0: '#F6C79A', sky1: '#F9E6CF', sea: '#6FA3B5', hill0: '#B7896A', hill1: '#8E6A55', road: '#4A4440', line: '#F4E7C8', grade: 'none' },
  cool: { sky0: '#9FC3DA', sky1: '#E1ECF2', sea: '#3E7D99', hill0: '#6F8C8A', hill1: '#516B6E', road: '#3B4045', line: '#E7EEF2', grade: 'none' },
  dusk: { sky0: '#C77B7A', sky1: '#F1B98E', sea: '#4C6F8E', hill0: '#6E5263', hill1: '#4E3B4C', road: '#2F2B30', line: '#F2D3B1', grade: 'none' },
  day:  { sky0: '#8EC1E6', sky1: '#DCEFF8', sea: '#2F8DB0', hill0: '#7FA07A', hill1: '#5D7E5E', road: '#45474A', line: '#F7F1DE', grade: 'none' },
};
export const PLATE_VARIANTS = Object.keys(PALETTES);

export function paintPlate(canvas, t, opts = {}) {
  const g = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const p = PALETTES[opts.palette || 'warm'];
  const view = opts.view || 'side'; // side | aerial | close
  g.save();
  // sky
  const sky = g.createLinearGradient(0, 0, 0, H * 0.6);
  sky.addColorStop(0, p.sky0); sky.addColorStop(1, p.sky1);
  g.fillStyle = sky; g.fillRect(0, 0, W, H);

  if (view === 'aerial') {
    g.fillStyle = p.hill1; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 40; i++) {
      g.fillStyle = i % 2 ? p.hill0 : p.hill1;
      g.globalAlpha = 0.5;
      g.beginPath();
      g.arc(rand(i) * W, ((rand(i + 9) * H + t * H * 0.04) % (H * 1.2)) - H * 0.1, W * (0.03 + rand(i + 3) * 0.06), 0, Math.PI * 2);
      g.fill();
    }
    g.globalAlpha = 1;
    // winding road seen from above
    g.strokeStyle = p.road; g.lineWidth = W * 0.07; g.lineCap = 'round';
    g.beginPath();
    for (let y = -20; y <= H + 20; y += 8) {
      const x = W * 0.5 + Math.sin((y + t * H * 0.04) / H * 4) * W * 0.18;
      y === -20 ? g.moveTo(x, y) : g.lineTo(x, y);
    }
    g.stroke();
    g.strokeStyle = p.line; g.lineWidth = Math.max(1, W * 0.004); g.setLineDash([W * 0.02, W * 0.02]);
    g.stroke(); g.setLineDash([]);
    const ry = H * 0.62, rx = W * 0.5 + Math.sin((ry + t * H * 0.04) / H * 4) * W * 0.18;
    g.fillStyle = '#1B1B1E'; g.beginPath(); g.ellipse(rx, ry, W * 0.008, W * 0.02, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#FF6A2B'; g.beginPath(); g.arc(rx, ry - W * 0.006, W * 0.006, 0, Math.PI * 2); g.fill();
    g.restore();
    return;
  }

  const horizon = H * (view === 'close' ? 0.5 : 0.56);
  // sun
  g.fillStyle = 'rgba(255,255,240,0.55)';
  g.beginPath(); g.arc(W * 0.78, H * 0.22, H * 0.09, 0, Math.PI * 2); g.fill();
  // sea
  g.fillStyle = p.sea; g.fillRect(0, horizon - H * 0.06, W, H * 0.12);
  // hills (parallax)
  const hills = (col, base, amp, speed, seed) => {
    g.fillStyle = col; g.beginPath(); g.moveTo(0, H);
    for (let x = 0; x <= W; x += W / 24) {
      const u = x / W + t * speed;
      g.lineTo(x, base - amp * (0.5 + 0.5 * Math.sin(u * 7 + seed) * Math.cos(u * 3.1 + seed * 2)));
    }
    g.lineTo(W, H); g.fill();
  };
  hills(p.hill0, horizon - H * 0.02, H * 0.2, 0.01, 1);
  hills(p.hill1, horizon + H * 0.06, H * 0.12, 0.03, 4);
  // road
  g.fillStyle = p.road; g.fillRect(0, horizon + H * 0.12, W, H);
  g.fillStyle = p.line;
  const dash = W * 0.08;
  for (let x = -dash * 2; x < W + dash; x += dash * 2) {
    const ox = ((x - (t * W * 0.35) % (dash * 2)) + dash * 4) % (W + dash * 4) - dash * 2;
    g.fillRect(ox, horizon + H * 0.3, dash, H * 0.012);
  }
  // cyclist (simple silhouette)
  const cx = W * (view === 'close' ? 0.5 : 0.42) + Math.sin(t * 0.8) * W * 0.01;
  const cy = horizon + H * (view === 'close' ? 0.22 : 0.26);
  const sc = (view === 'close' ? 2.2 : 1) * H * 0.0024;
  const wr = 26 * sc, ang = t * 9;
  g.strokeStyle = '#151517'; g.lineWidth = 3.2 * sc; g.lineCap = 'round';
  for (const wx of [cx - 34 * sc, cx + 34 * sc]) {
    g.beginPath(); g.arc(wx, cy, wr, 0, Math.PI * 2); g.stroke();
    g.beginPath(); g.moveTo(wx, cy); g.lineTo(wx + Math.cos(ang) * wr, cy + Math.sin(ang) * wr); g.stroke();
  }
  g.beginPath(); g.moveTo(cx - 34 * sc, cy); g.lineTo(cx - 6 * sc, cy - 30 * sc); g.lineTo(cx + 24 * sc, cy - 30 * sc); g.lineTo(cx + 34 * sc, cy); g.lineTo(cx, cy); g.closePath(); g.stroke();
  g.fillStyle = '#151517';
  g.beginPath(); g.moveTo(cx - 8 * sc, cy - 36 * sc); g.lineTo(cx + 16 * sc, cy - 62 * sc); g.lineTo(cx + 26 * sc, cy - 56 * sc); g.lineTo(cx + 2 * sc, cy - 30 * sc); g.fill();
  g.fillStyle = '#FF6A2B';
  g.beginPath(); g.arc(cx + 26 * sc, cy - 70 * sc, 9 * sc, 0, Math.PI * 2); g.fill();

  // boom mic intrusion (for the clean-up beat)
  if (opts.mic) {
    g.fillStyle = '#2A2A2E';
    g.fillRect(W * 0.18, 0, W * 0.5, H * 0.025);
    g.fillStyle = '#3A3A40';
    g.beginPath(); g.ellipse(W * 0.66, H * 0.07, W * 0.06, H * 0.05, -0.2, 0, Math.PI * 2); g.fill();
    g.strokeStyle = 'rgba(255,255,255,0.15)'; g.lineWidth = 1;
    for (let i = 0; i < 8; i++) { g.beginPath(); g.moveTo(W * (0.61 + i * 0.012), H * 0.03); g.lineTo(W * (0.6 + i * 0.012), H * 0.11); g.stroke(); }
  }
  g.restore();
}
