# Scene Recipes

Pustaka resep. Pilih dan gabungkan sesuai naskah. Tiap resep: pemicu kata -> visual.

Semua contoh memakai helper dari `assets/template.html` (`grp`, `P`, `A`, `mk`, `fig`, `icon`, `scr`, `sfx`, `tl`, `perFrame`).

---

## Komponen siap pakai (assets/components.js)

Semua waktu = detik final. `src` = `'img/x.jpg'` | `{dir:'c1'}` (image sequence, n otomatis dari build.py) | `null`.
Opsi umum: `light:true` (scene terang, tinta gelap tanpa glow), `wipe:'up'|'circle'`. Contoh lengkap: `examples/demo-scenes.js`.

| Komponen | Parameter |
|---|---|
| `bgMotion(face, {src, dim, zoom})` | `face` = [[a,b],...] jendela wajah; di luarnya latar MG footage blur + overlay `dim` (.84); `zoom:false` mematikan zoom-through |
| `sceneSearchHook(t0,t1,{...})` | `query`, `typeAt`, `results` [teks], `resultsAt`, `strikeAt` [t per hasil], `qAt`, `y` |
| `sceneProfile(t0,t1,{...})` | `avatar`, `name`, `handle`, `bio`, `stats` [[angka,label]], `grid` [src], `highlightAt`, `scrollAt`, `pill` |
| `sceneCollage(t0,t1,{...})` | `items` [src, maks 12], `marks` ['check'/'x'/null], `markAt` (t atau [t]) |
| `sceneCarousel(t0,t1,{...})` | `items` [src 3-7], `pick`, `pickAt`, `steps` [label maks 4], `stepsAt` [t] |
| `sceneAnnotate(t0,t1,{...})` | `src`, `scanAt`, `labels` [[teks,t,'l'/'r',yFrac 0-1]] maks 4 |
| `sceneChecklist(t0,t1,{...})` | `src`, `title`, `items` [[teks,t]] maks 6 |
| `sceneFilmstrip(t0,t1,{...})` | `frames` [src 5] atau `clip:{dir}`, `playFrom`, `playTo`, `seconds`, `labels` ['AWAL','AKHIR'] |
| `sceneBrowser(t0,t1,{...})` | `url`, `src`, `title`, `titleAt`, `y` |
| `sceneWall(t0,t1,{...})` | `imgs` [src], `focus:{src, at, pill}` |
| `scenePhoneFocus(t0,t1,{...})` | `src`, `label`, `pill`, `pillAt`, `y` |
| `sceneTryFail(t0,t1,{...})` | `prompt`, `typeAt`, `genAt`, `failAt`, `badge`, `src`, `y` |
| `sceneCommentCTA(t0,t1,{...})` | `word`, `label`, `typeAt`, `sendAt`, `link`, `linkAt`, `y` |
| `sceneClosing(t0,t1,{...})` | `src`, `label`, `word`, `line`, `green`, `small`, `y` (semua dalam satu blok rapat) |
| `lightBg(tIn,tOut,{tone,wipe})` | latar terang untuk scene buatan sendiri; isi grup diberi class `lt` |
| `stack([el..], yTengah, gap)` | susun teks yang berkaitan jadi satu blok rapat |

---

## 1. Hook grafik garis tipis di wide shot (0 - 5 dtk)

Pemicu: kalimat pembuka saat kamera masih jauh dan ada ruang kosong di atas kepala.

Bangun grafik batang garis tipis di ruang kosong itu. Bukan grafik berwarna penuh, melainkan outline putih tipis dengan satu batang terisi warna.

Urutan yang terbukti menahan penonton:
1. Judul mono letterspacing lebar muncul dengan efek scramble.
2. Sumbu Y dan X tumbuh (`scaleY`/`scaleX` dari 0, `power3.out`).
3. Batang yang **jadi antagonis** naik duluan sendirian, terisi merah, diberi label serif italic merah di atasnya.
4. Batang lain menyusul belakangan dengan outline abu, lalu diberi tanda X merah bulat kecil satu per satu.
5. Garis ambang hijau menyapu horizontal saat kalimat pertanyaan diucapkan.

Kuncinya: grafik **menjawab pertanyaan hook secara visual** sebelum narasumber menjawabnya.

```js
const b=P(g,x,BOT-h,'','',{width:BW+'px',height:h+'px',
  border:'2px solid rgba(190,190,200,.45)',borderBottom:'none',
  background:'linear-gradient(180deg,rgba(160,160,172,.30),rgba(120,120,130,.12))',
  transformOrigin:'50% 100%'});
tl.fromTo(b,{scaleY:0,opacity:0},{scaleY:1,opacity:1,duration:.55,ease:'power4.out'},t);
```

Tanda X: lingkaran 38px gradien merah, `scale:0, rotation:-90` -> `back.out(2.4)`, lalu induknya diredupkan ke `opacity:.5`.

---

## 2. Lower third mono dengan scramble

Pemicu: beberapa detik setelah potongan ke close-up.

Bar vertikal aksen 4x88px (`scaleY` 0 -> 1), judul mono 27px dan subjudul mono 19px yang muncul lewat efek scramble karakter, lalu hilang lagi dengan scramble terbalik.

```js
scr(el,'TOOLS MURAH vs MAHAL', t0+.08, .55, t1, .35);
```

`scr(el,text,t0,durIn,tOut,durOut)` ada di template. Beri 5 SFX `type` beruntun saat muncul.

Isi: topik pembicaraan atau nama narasumber. **Jangan karang nama.** Kalau user tidak memberi nama, pakai topik.

---

## 3. Kata hantaman yang bertahan

Pemicu: satu kata paling tegas di seluruh naskah ("HARAM", "SALAH", "STOP").

Kapital, kelas `.R`, flash radial merah 0.85 opacity selama 0.4 dtk, `shake(t,12,.3)`, SFX `thud`.

**Jangan hilangkan kata itu saat kalimat berikutnya muncul.** Taruh kata hantaman sebagai baris pertama dari blok caption yang sama dengan kalimat lanjutannya, supaya bertahan 2-3 detik di layar. Ini perbedaan antara terbaca dan terlewat.

---

## 4. Kartu scene berlabel

Pemicu: menyebut beberapa jenis adegan atau kategori.

Kotak outline 240x135 radius 10px di sisi kiri, berisi label mono kecil di atas dan nama adegan mono tebal di bawah. Masuk dari kiri dengan stagger 0.12 dtk.

Saat kata kunci positif diucapkan: garis scan putih turun melintasi kotak (0.4 dtk), lalu badge hijau `✓ <LABEL>` pop dengan `back.out(2.2)` dan border kotak berubah hijau.

---

## 5. Bar perbandingan biaya

Pemicu: menyebut angka pengali atau perbandingan.

Dua baris: label mono hijau dengan bar pendek, label mono merah dengan bar panjang bergradien. Bar merah tumbuh dua tahap (`scaleX` 0 -> 0.5 saat angka pertama, 0.5 -> 1 saat angka kedua), angka pengali muncul dengan scramble dan SFX `tick`.

---

## 6. Log mono berjalan

Pemicu: menyebut proses coba-coba, iterasi, atau percobaan.

Baris mono 24px yang diketik karakter per karakter lewat `perFrame`, dengan caret `▍` berkedip. Baris gagal abu, baris berhasil hijau.

```js
perFrame.push(t=>{ if(t<t0){el.textContent='';return;}
  const n=Math.min(txt.length,Math.floor((t-t0)/dur*txt.length));
  el.textContent=txt.slice(0,n)+((t-t0<dur+.25&&Math.floor(t*6)%2===0)?'▍':''); });
```

---

## 7. Viewfinder "AI GENERATED"

Pemicu: mengakui bahwa video ini sendiri dibuat AI.

Empat sudut bracket putih 64x3px di dalam safe zone (x 120-960, y 262-1518), masuk dari luar secara diagonal. Titik merah berkedip + label mono scramble di kiri atas, timecode berjalan di kanan atas, dan satu garis scan menyapu dari atas ke bawah sekali (1.15 dtk, `power1.inOut`).

Timecode dihitung dari `t` supaya deterministik:

```js
perFrame.push(t=>{const ss=Math.floor(t),ff=Math.floor((t-ss)*30);
  tc.textContent=`00:00:${String(ss).padStart(2,'0')}:${String(ff).padStart(2,'0')}`;});
```

---

## 8. Rekonstruksi UI aplikasi

Pemicu: menyebut nama alat atau aplikasi tertentu.

**Jangan tempel screenshot mentah.** Bangun ulang UI-nya dengan HTML: chrome browser (tiga titik, tab, address bar), sidebar dengan ikon garis, grid media berisi klip user sendiri, dan kolom prompt di bawah.

Animasinya singkat dan terarah, pas dengan panjang kalimat:
1. Jendela masuk dengan `rotationX:32 -> 0`, `y:150 -> 0`, blur 10 -> 0 (0.6 dtk).
2. Sidebar stagger dari kiri, thumbnail stagger `back.out(1.6)`.
3. Kursor SVG bergerak ke satu klip (klip ikut membesar dan diberi ring putih), lalu pindah ke chip model.
4. Saat nama model diucapkan: chip menyala hijau + callout mono hijau pop di atasnya.
5. Saat nama platform diucapkan: host di address bar di-highlight hijau + callout kedua.

Satu thumbnail boleh berisi image sequence yang benar-benar bergerak. Itu yang membuatnya terasa hidup, bukan gambar tempel.

---

## 9. Judul mask-reveal

Pemicu: menyebut nama produk, kelas, atau penawaran.

Baris pertama: tiap kata dibungkus `overflow:hidden`, naik `yPercent 115 -> 0`, stagger mengikuti waktu kata. Baris kedua (nama inti): kelas besar berwarna, masuk dengan `scale 1.4 -> 1` + `brightness 2.4 -> 1`. Lalu garis bawah bergradien `scaleX 0 -> 1`.

Ukuran baris pengantar sekitar 0.66x dari nama inti supaya hierarkinya tegas. Dua baris diberi offset x berlawanan.

---

## 10. Grid mockup HP 3D

Pemicu: "sebagus video-video ini", "contohnya", "hasilnya".

Tiga HP sejajar di ruang bawah frame, diberi `z` dan `rotationY` berbeda (`[-80,+28]`, `[+50,0]`, `[-80,-28]`) supaya terasa tiga dimensi. Masuk dari bawah satu per satu dengan `rotationX:-55 -> 0`.

Saat kata penekanan: `sheen` menyapu tiap kartu lalu `scale 1.05` yoyo.

Untuk scene tambahan: ketiga HP bergerak ke posisi grid 3x2, tiga HP baru naik dari bawah, lalu badge kecil muncul di tiap layar. Induk grid bergoyang pelan lewat `perFrame`.

---

## 11. Banner scene tambahan

Pemicu: scene tanpa VO yang perlu penjelasan.

Pill mono dengan titik berkedip di atas, satu baris Inter 38px, satu baris Playfair italic 70px, lalu nama platform Playfair 108px berwarna dengan garis bawah bergradien. Semua masuk berurutan dalam 1 detik, lalu diam dan sedikit mengambang.

---

## 12. CTA kolom komentar

Pemicu: "ketik X di kolom komen".

Kotak komentar radius penuh 820x112 di `y=1428`: avatar lingkaran, placeholder, tombol kirim bulat gradien. Kata CTA diketik huruf per huruf (0.068 dtk per huruf, SFX `type`), caret mengikuti lebar teks. Lalu tombol kirim ditekan (`scale .84` yoyo), cincin putih menyebar, teks terbang ke atas.

Ganti kotak dengan toast notifikasi: ikon hijau, judul Inter 800, subjudul kecil. Beri SFX `ding` dan ring hijau saat penekanan.

Koordinat tombol **di-hardcode** setelah diukur, bukan `getBoundingClientRect()` saat elemen masih bergerak.

---

## 13. Scene penutup blur

Pemicu: setelah kalimat terakhir, sebagai tambahan 3-5 detik.

Video latar tetap jalan tapi di-blur 22px dan di-zoom pelan, ditimpa lapisan hitam 80%. Di tengah frame: label kecil, kata CTA raksasa `.R`, baris penjelas, pemisah garis + ikon, lalu baris hijau dan baris kecil syarat.

Semua teks di tengah vertikal (`y` sekitar 955), bukan di bawah. Beri `floaters` amplitudo 3-4px supaya tidak mati.
