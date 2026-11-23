# Katalog scene (resep dari video referensi)

Pakai sebagai pustaka; pilih dan gabungkan sesuai script. Setiap resep: pemicu kata → visual.
Semua waktu memakai `at('kata')` (waktu final). Warna lewat `ACC`, `ACC_HI`, `INK`, `var(--accent)`.

1. **Hook + emoji ekspresif** (0-2,5 dtk): emoji 3D (mis. bingung) `scale 0->1 + rotate -25->0 back.out(2)`, bergoyang sinus; kalimat hook muncul per kata (blur-in) dengan 1-2 kata kunci di pil putih (`hlOn`).
2. **Kartu video -> background**: klip contoh tampil sebagai kartu putih berbingkai (lalu membesar jadi background full-screen, overlay hitam semi-transparan .55) sementara teks di atasnya.
3. **Judul mask-reveal** ("Kelas AI"): tiap huruf di dalam `overflow:hidden` naik `yPercent 110->0` (stagger .035), lalu bar accent `scaleX 0->1` dari kiri di belakang, teks berubah putih, kilap (`shine`) menyapu, pil "Joined" + 5 sinar kecil. Scene terang (`whiteRise`).
4. **Counter + video wall** ("ada 100+ video"): angka 360px/900 menghitung 0->100 (`count()`), thud + scale pop, label di bawah; lalu grid miring (rotate -12) berisi 8-12 tile video unik 200x356 muncul dengan stagger dari tengah, scroll vertikal pelan; angka bergeser ke atas, kata "Dibedah" slam dengan shake. Tile video wall diberi `data-qa-skip` (sengaja melewati tepi).
5. **Carousel kategori** (UGC / Cinematic / Talking Head): kartu klip bergantian, tiap kartu ditahan 3 dtk (`pauses`), badge 2x bila dipercepat; kategori "Lainnya" mengecil lalu rantai workflow 4 langkah (Ide -> Prompt -> Generate -> Edit) dengan ikon, panah tumbuh, tiap node pop berurutan; hold 2 dtk.
6. **Mockup HP**: `phone(s,540,960,520)` lalu `vid(p.screen,'nama',null,t0,t1,{position:'absolute',inset:0})`; bingkai masuk dengan rotasi 3D ringan + cincin glow; muncul saat kalimat "hasilnya berkualitas". Tanpa simbol murahan (mata, bintang).
7. **Tong sampah** ("video murahan"): chip label murahan terbang ke bin dan ter-clip di dalamnya (jangan ada label "bocor" keluar), tutup bin goyang. SFX: `error` saat label masuk bin, `thud` kecil saat tutup menutup.
8. **Gembok** ("kalau kamu gabung...bisa masuk ke private group"): kartu putih dengan satu gembok terkunci; tetap terkunci sampai kata "masuk", lalu terbuka (transform shackle) + pil "1.483+ member" dengan `count()`. Satu gembok saja.
9. **Screen record chat** (Telegram): klip direkam diputar `rate≈.77`, tanpa blur, overlay gelap ringan, judul melayang bergantian, lencana member mengambang; hold 2 dtk setelah kalimat penutup.
10. **Metafora tabrakan** ("ada kalanya mentok"): mobil emoji berlabel "BELAJAR" melaju -> menabrak tembok bata (shake besar, partikel kolision) -> roket menghancurkan tembok -> mobil lanjut. Pemicu: "mentok" = tabrakan, "cara tercepat" = roket.
11. **Profil sosial** (IG): kartu putih berisi foto profil bulat (crop wajah di tengah, tidak miring), nama, tombol Follow yang langsung berganti Following (tanpa kursor), caption pengalaman; durasi cukup panjang (4+ dtk).
12. **Bonus tools**: ikon tools orbit/burst dari tengah (bukan ikon hadiah), judul "Bonus Tools", lalu kartu mini-app (lihat 13), lalu daftar item (pil putih bergantian masuk dari kanan): item inti, item "dan masih banyak lagi" menambah item lanjutan.
13. **Kartu mini-app** (menggantikan screenshot mentah; wajib bila menampilkan banyak tool): grid 2 x 3 kartu putih 480x330, radius 30, bayangan `0 30px 60px rgba(0,0,0,.5)`. Isi kartu: header (ikon kotak accent 52px, nama 25px/800, subjudul 16px abu, label `#n` pil accent soft) -> baris tengah (input chip/thumbnail di kiri 150px, panah, output di kanan) -> tombol bawah hitam tinggi 44 dengan `.gfill` accent `scaleX 0->1` (0,85 dtk) lalu ganti hijau, label berganti "Generate" -> "Generating..." -> "✓ <hasil>" (via `perFrame`, fase berdasar t). Output pop `back.out(2)` satu per satu; kartu stagger masuk 0,18 dtk; setelah semua selesai ada sorotan bergilir (scale 1.045), lalu semua kartu terbang ke titik tengah & memudar. Thumbnail hasil dipotong dari screenshot user (`img/gc/*.jpg`), tampil kecil dengan `object-fit:cover`. Teks chip pendek (maks ~14 karakter); qa.js menangkap yang terpotong.
14. **Pertanyaan penutup** ("MAU TAHU?"): teks besar slam + shake kecil sebelum CTA.
15. **CTA minimalis**: bg gelap sederhana; kolom komentar mock berisi kata kunci diketik per huruf (`typeText`, caret berkedip), teks "di kolom komen" muncul, kursor bergerak ke tombol SEND lalu klik (`click()`), kata hilang, lalu kartu accent "SKILL SUDAH DIUPGRADE ✓" slam + cincin gelombang + thud + ding; kartu sedikit bergerak naik-turun sampai akhir. Posisi tombol klik harus **di-hardcode** (ukur setelah transform selesai lewat snapshot), bukan `C()` saat elemen masih bergerak. Boleh ditambah `bigArrow` yang menunjuk kolom komentar.
16. **A + B = C** (alur/proses yang diucapkan berurutan: "gabungkan ide dan prompt, jadi video keren"): dua kartu putih dengan tanda plus, meluncur dan bertabrakan (shake + thud), cincin accent mengembang, lalu kartu hasil lahir (zoom + ding) dengan bingkai accent. Hasil memakai aset asli user; kalau hasilnya video, putar klip user di kartu C. Tahap kedua boleh menggabungkan hasil tahap pertama dengan bahan berikutnya. Beri jeda 1,5-2 dtk setelah hasil lahir (`pauses`).
17. **Panah ajakan** (CTA "klik link di bawah", "komen di sini"): `bigArrow` solid gradasi accent dengan garis putih, pop lalu memantul terus ke arah target. Bukan ikon garis tipis.

## Contoh kode helper baru

```js
// 16. A + B = C, tabrakan tepat di kata "jadi"
{const t0=at('Gabungkan')-.05, t1=at('Ketik')-.02; const s=scene(t0,t1);
 const ta=at('ide')-.05, gap=at('jadi')-ta-.4;           // tabrakan = ta + .4 + gap
 const kA=`${icon('lightbulb',90)}<div style="font-size:52px;font-weight:800;margin-top:14px">Ide</div>`;
 const kB=`${icon('chat-text',90)}<div style="font-size:52px;font-weight:800;margin-top:14px">Prompt</div>`;
 const m=mergeTo(s,ta,kA,kB,'<div class="cv" style="position:absolute;inset:0"></div>',{y:960,gap});
 vid(m.C.querySelector('.cv'),'ugc',null,m.end-.5,t1,{position:'absolute',inset:0});
 outA(m.C,t1-.22);}

// 15 + 17. CTA komentar dengan ketikan, klik, panah
{const t0=at('Ketik')-.05; const s=scene(t0,TOTAL);
 const box=A(s,540,900,'','card',{width:'820px',height:'150px',flexDirection:'row',justifyContent:'space-between',padding:'0 26px 0 40px',borderRadius:'75px'});
 const txt=mk(box,'','',{fontSize:'60px',fontWeight:800,color:INK});
 mk(box,icon('paper-plane-tilt',54,'#fff'),'',{width:'104px',height:'104px',borderRadius:'50%',background:'linear-gradient(180deg,var(--accentHi),var(--accent))',display:'flex',alignItems:'center',justifyContent:'center'});
 inA(box,t0,'zoom'); sfx(t0,'whoosh');
 const end=typeText(txt,at('MAU'),'MAU',.12,true,at('komentar')+.6);
 bigArrow(s,540,1130,end+.1,{dir:'up',size:150});
 const tc=at('komentar')+.3; cursorPath([[tc-.5,820,1250],[tc,872,912]],tc+.6); click(tc+.05,872,912,s);
 tl.to(txt,{opacity:0,duration:.15},tc+.1);
 const ok=A(s,540,1400,'SKILL SUDAH DIUPGRADE ✓','chip',{fontWeight:800});
 inA(ok,tc+.35,'slam'); shake(tc+.5,12); sfx(tc+.5,'thud',.7); sfx(tc+.55,'ding'); float(ok,8,1);}

// 4. counter di scene terang: tiga baris yang berkaitan = SATU blok rapat lewat stack()
{const t0=at('Di'), t1=at('Gabungkan')-.02; const s=scene(t0,t1); whiteRise(s,t0-.05);
 const L=line(s,540,0,[['Di',at('Di')],['kelas',at('kelas')],['ini',at('ini')],['ada',at('ada')]],{fontSize:'68px',fontWeight:600,fontStyle:'italic',color:INK}); wordsIn(L);
 const num=A(s,540,0,'<span>0</span><span style="color:var(--accent)">+</span>','',{fontSize:'360px',fontWeight:900,letterSpacing:'-.04em',lineHeight:'.9',color:INK});
 const lab=A(s,540,0,'<span class="w" style="background:var(--accent);color:#fff;padding:6px 34px">video dibedah</span>','',{fontSize:'78px',fontWeight:800});
 stack([L,num,lab],930,[10,26]);                       // bukan y 560 / 900 / 1230 yang berjauhan
 inA(num,at('seratus')-.05,'pop'); count(num.firstChild,at('seratus'),.9,100); sfx(at('seratus')+.9,'thud',.8);
 inA(lab,at('dibedah')-.05,'slam'); shake(at('dibedah')+.15,14); sfx(at('dibedah')+.15,'thud');}
```
