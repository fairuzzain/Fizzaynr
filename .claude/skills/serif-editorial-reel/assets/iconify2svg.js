#!/usr/bin/env node
/* Ubah set @iconify-json/<set> jadi berkas SVG siap pakai.
 *
 *   node iconify2svg.js <set> <folderTujuan> [nama...]
 *   node iconify2svg.js lucide build/icon sparkles wand-2 clapperboard
 *
 * Tanpa daftar nama, SELURUH set dikonversi. Jangan lakukan untuk set besar
 * seperti mdi (7.638 ikon). Install dulu: npm i @iconify-json/<set>
 */
const fs = require('fs'), path = require('path');
const [set, out, ...names] = process.argv.slice(2);
if (!set || !out) { console.error('pakai: node iconify2svg.js <set> <folderTujuan> [nama...]'); process.exit(1); }

let d;
for (const base of [process.cwd(), path.join(process.cwd(), '..'), '/home/claude/work/build']) {
  const p = path.join(base, 'node_modules', '@iconify-json', set, 'icons.json');
  if (fs.existsSync(p)) { d = JSON.parse(fs.readFileSync(p, 'utf8')); break; }
}
if (!d) { console.error(`@iconify-json/${set} tidak ketemu. Jalankan: npm i @iconify-json/${set}`); process.exit(1); }

fs.mkdirSync(out, { recursive: true });
const list = names.length ? names : Object.keys(d.icons);
if (!names.length && list.length > 400)
  console.error(`PERINGATAN: ${list.length} ikon akan ditulis. Sebutkan nama untuk membatasi.`);

let n = 0, miss = [];
for (const k of list) {
  const ic = d.icons[k];
  if (!ic) { miss.push(k); continue; }
  const w = ic.width || d.width || 24, h = ic.height || d.height || 24;
  fs.writeFileSync(path.join(out, k + '.svg'),
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}">${ic.body}</svg>`);
  n++;
}
console.log(`${n} svg -> ${out}`);
if (miss.length) {
  console.log('tidak ada di set:', miss.join(', '));
  const all = Object.keys(d.icons);
  for (const m of miss) {
    const near = all.filter(k => k.includes(m.split('-')[0])).slice(0, 8);
    if (near.length) console.log(`  mirip "${m}":`, near.join(', '));
  }
}
