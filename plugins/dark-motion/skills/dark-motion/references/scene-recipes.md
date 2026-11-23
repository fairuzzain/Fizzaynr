# Scene Recipes

Pustaka resep, disusun menurut **pola ucapan**: apa yang sedang dikatakan pembicara → apa yang muncul di layar. Pilih dan gabungkan sesuai isi video; jangan dipakai semua. Satu scene khusus kira-kira tiap 5-10 detik. Sisanya cukup caption otomatis dan zoom.

## Aturan umum menulis scene

- Semua scene ditulis di `build/scenes.js`, dibungkus `{ ... }` supaya variabelnya tidak bentrok.
- Waktu dalam detik **hasil**. Ambil detik kata dari `words_list.txt` lalu bungkus `T()`: `const t0 = T(12.40)`.
- Mulai dari `grp(t0, t1)` (wadah yang hanya terlihat di rentang itu), lalu `exit(g, t1)` untuk keluar halus.
- Kalau scene menampilkan sendiri kata-kata yang diucapkan, masukkan rentangnya ke `capplan.json` → `skip` supaya caption tidak dobel. Kalau scene hanya grafis pendukung, biarkan caption tetap jalan dan taruh grafik di area yang tidak dipakai caption (cek `captions_preview.txt` untuk posisi caption di rentang itu).
- Elemen yang tidak boleh terlihat sebelum waktunya: pakai `fadeIn()` atau `tl.fromTo()`. Di mesin animasi skill ini nilai "from" sudah berlaku sebelum tween mulai, jadi tidak ada kebocoran di awal.
- Isi yang belum pasti (nama, angka, teks prompt) **diminta ke user**. Kalau terpaksa mengarang contoh, laporkan di contact sheet.

### Helper yang tersedia (dari template)

| Helper | Fungsi |
|---|---|
| `grp(t0,t1)` | Wadah layar penuh yang terlihat dari t0 sampai t1 |
| `A(p,x,y,html,kelas,css)` / `P(...)` | Elemen absolut, berpusat di (x,y) / pojok kiri-atas di (x,y) |
| `fadeIn(el,t,dur,from)`, `exit(g,t)` | Masuk halus (opacity+blur+gerak), keluar halus |
| `bgBlur`, `bgPhoto`, `bgVideo` | Latar scene (lihat style-system.md) |
| `scrimT`, `scrimB`, `scrimM` | Gradien gelap memudar di belakang teks |
| `icon(nama,ukuran,warna)` | Ikon garis bawaan (cari nama: `assemble.py --icons <kata>`; varian `-fill` juga ada) |
| `chip(p,x,y,teks,warna,ikon)` | Label kecil bertepi warna |
| `label(t0,t1,judul,sub,{x,y})` | Lower third mono dengan efek acak huruf |
| `phone(p)`, `brackets(p,x,y,w,h,warna)` | Mockup HP, sudut bingkai |
| `vid(p,dir,n,t0,t1)` | Image sequence di dalam elemen (klip dari `frames.py --clip`) |
| `shake(t,amp,dur)` | Getaran kamera (maksimal dua kali per video) |
| `sfx(t,jenis,gain)` | SFX: `sub air tick glitch key conf rise sweep` |
| `perFrame.push(t=>{...})` | Logika per frame (penghitung, mengetik, dll.) |
| `tl.to / fromTo / set` | Animasi, gaya GSAP: `tl.to(el,{x:100,duration:.4,ease:'power3.out'}, detik)` |
| `gfxBg(t0,t1)` | Latar full motion graphic (grid + cahaya bergerak). Satu per rentang tanpa wajah (P1) |
| `phoneTrio(p,t1,clips)` | Tiga HP berisi klip (P2) |
| `videoWall(t0,t1,dirs,n)` | Dinding video bergulir di latar (P3) |
| `imgCard(p,x,y,w,h,src,pos)` | Kartu gambar berpusat |
| `popIn(el,t)`, `burstAt(p,x,y,t)` | Hasil yang "lahir" (skala .62 + terang), kilatan tabrakan |
| `plusSign(p,x,y,t)`, `mergeTo(p,[[el,x0,y0],..],x,y,t)` | Tanda plus, penggabungan kartu (N1). mergeTo mengembalikan detik tabrakan |
| `chipC(p,x,y,teks,warna,ikon,t)` | Chip berpusat horizontal, dengan animasi masuk |
| `logoBuild(p,cx,cy,skala,{emblem,lines,tag,times})` | Logo dibangun ulang (O1) |
| `bigArrow(p,x,y,w,{t,dir})` | Panah CTA tebal dua warna yang memantul (M3) |

**Huruf di scene buatan sendiri:** nama keluarga font di halaman adalah `I` (Inter), `PF` (Playfair), `JB` (JetBrains Mono). Menulis `font:'700 25px Inter'` membuat huruf jatuh ke serif bawaan browser. Pakai kelas (`n`, `s`, `k1`...), `fontFamily:'var(--bf),sans-serif'` untuk teks biasa, atau `font:'700 26px JB'` untuk mono.

---

## A. Pembuka (hook, 5 detik pertama)

### A1. Kalimat pembuka sebagai judul
Pemicu: kalimat pertama. Biasanya cukup lewat `capplan.json` → `hook_end` (caption otomatis membesar jadi judul). Untuk penekanan ekstra, tambahkan satu getaran saat kata kuncinya jatuh: `shake(T(1.8), 10, .2)`.

### A2. Efek pembuka yang dibakar ke frame
Pemicu: video dibuka dengan wide shot atau footage yang terlihat datar. Baris-baris menyala dari hitam sambil zoom keluar, grain dan garis scan halus hanya di detik-detik awal. Dibakar langsung ke frame supaya menyatu:

```bash
$PY $SK/assets/bake.py grade build/vf/main build/vf/main --range 0:120 --soft --scan --grain 9 --open 0.42 --zoom 0.55:1.18
```

Juga berguna sebagai penyamar: footage yang terlihat flat atau buatan AI jadi terbaca sebagai gaya yang disengaja.

### A3. Glitch di kata masalah
Pemicu: kata yang menyebut masalah di detik-detik awal ("gagal", "rugi", "salah"). Burst 0,1-0,26 detik dibakar ke frame plus `sfx(t,'glitch')`. Maksimal 3 burst di 5 detik pertama, setelah itu berhenti sama sekali.

```bash
$PY $SK/assets/bake.py glitch build/vf/main build/vf/main --at <nomorFrame> --width 9 --ca 24
```

---

## B. Saat menyebut angka

### B1. Penghitung naik
Pemicu: persentase, jumlah, rupiah, pengikut, hasil. Angka besar menghitung naik dan berhenti tepat saat angkanya diucapkan.

```js
{ const t0=T(8.10), tEnd=T(9.20), t1=T(11.0), target=37, suf='%';
  const g=grp(t0,t1); bgBlur(t0,t1);
  const num=A(g,540,880,'0'+suf,'X',{color:'var(--c1)'});
  const sub=A(g,540,1060,'pelanggan kembali','n',{fontSize:'48px'});
  fadeIn(num,t0,.3); fadeIn(sub,tEnd-.1,.3);
  perFrame.push(t=>{const p=Math.min(1,Math.max(0,(t-t0)/(tEnd-t0)));
    num.textContent=Math.round(target*(1-Math.pow(1-p,3)))+suf;});
  sfx(tEnd,'tick'); exit(g,t1); }
```

Untuk rupiah atau angka besar, format dengan `toLocaleString('id-ID')`.

### B2. Roda angka bergulir
Pemicu: tahun, tanggal, tenggat. Layar hitam penuh (pengecualian aturan latar yang disengaja), deretan angka bergulir vertikal lalu melambat dan berhenti. Nilai sebelum dan sesudahnya terlihat samar.

```js
{ const t0=T(4.0), tL=T(5.2), t1=T(6.4), vals=['2019','2020','2021','2022','2023','2024','2025'], N=vals.length-1, PITCH=216;
  const g=grp(t0,t1); mk(g,'','L',{background:'#000'});
  const wrap=mk(g,'','L',{WebkitMaskImage:'linear-gradient(180deg,transparent 0%,rgba(0,0,0,.28) 15%,#000 34%,#000 66%,rgba(0,0,0,.28) 85%,transparent 100%)'});
  const els=vals.map(v=>P(wrap,0,0,v,'X',{width:'1080px',textAlign:'center',fontSize:'200px',lineHeight:'216px',textShadow:'none',
     background:'linear-gradient(180deg,#ffffff 20%,#9aa0a8 62%,#f2f2f4 85%)',WebkitBackgroundClip:'text',backgroundClip:'text',color:'transparent'}));
  const cur=t=>{const p=Math.min(1,Math.max(0,(t-t0)/(tL-t0)));return N*(1-Math.pow(1-p,2.5));};
  perFrame.push(t=>{const c=cur(t),v=Math.abs(cur(t+1/60)-cur(t-1/60))*30;
    els.forEach((b,i)=>{b.style.transform=`translateY(${852+(i-c)*PITCH}px)`;b.style.filter=`blur(${Math.min(14,v*1.4).toFixed(1)}px)`;});});
  sfx(tL,'sub'); exit(g,t1); }
```

### B3. Bar progres terisi
Pemicu: "naik dari X ke Y", target, kapasitas, skor. Bar tipis bertepi, isinya memanjang ke nilai yang disebut, angka di ujungnya. Dua bar bertumpuk untuk "dulu vs sekarang".

### B4. Bar sisa yang terkuras
Pemicu: "waktunya makin sedikit", "tinggal sebentar", kuota habis. Deretan bar (mis. 12 untuk bulan) menyala semua, lalu padam satu per satu dari kanan dengan jeda 0,08-0,09 detik, menyisakan satu yang berdenyut pelan.

---

## C. Saat menyebut daftar atau langkah

### C1. Daftar bertahap dengan centang
Pemicu: "ada tiga hal", "pertama... kedua...", langkah-langkah. Tiap baris muncul tepat saat butirnya diucapkan; centang tergambar saat butir selesai.

```js
{ const items=[['Riset audiens',T(20.1)],['Tulis hook',T(22.4)],['Uji 3 versi',T(24.9)]], t1=T(27.0);
  const g=grp(items[0][1]-.3,t1); bgBlur(items[0][1]-.3,t1);
  items.forEach(([txt,t],i)=>{const y=760+i*150;
    const row=P(g,190,y,`<span style="display:inline-flex;align-items:center;gap:26px">${icon('check-circle',58,C1)}<span class="n" style="font-size:54px">${txt}</span></span>`);
    tl.fromTo(row,{opacity:0,x:-40,filter:'blur(10px)'},{opacity:1,x:0,filter:'blur(0px)',duration:.35,ease:'power3.out'},t-.04);
    sfx(t,'tick',.8);});
  exit(g,t1); }
```

Untuk daftar yang diucapkan cepat, caption di rentang itu dimatikan lewat `skip`.

### C2. Nomor besar per langkah
Pemicu: "langkah kedua", "nomor tiga". Angka raksasa tipis (`X`, warna `C2`, opacity 0,9) di sisi kosong frame, judul langkah kecil mono di bawahnya. Bertahan sepanjang langkah itu dibahas, berganti saat langkah berikutnya disebut.

---

## D. Saat membandingkan

### D1. Dua kolom berdampingan
Pemicu: salah vs benar, dulu vs sekarang, A vs B. Dua kartu sejajar, label chip di atas, satu kata besar di bawah tiap kartu. Kartu yang "kalah" diredupkan (`opacity:.45`) saat pemenangnya disebut.

```js
{ const t0=T(31.0), tWin=T(33.2), t1=T(35.5);
  const g=grp(t0,t1); bgBlur(t0,t1);
  const L=P(g,140,700,'','frameC',{width:'380px',height:'520px'}), R=P(g,560,700,'','frameC',{width:'380px',height:'520px',boxShadow:'0 0 0 3px var(--c1),0 30px 80px rgba(0,0,0,.7)'});
  // isi kartu: gambar dari user, rekonstruksi UI, atau ikon besar
  L.innerHTML=`<div style="display:grid;place-items:center;height:100%">${icon('x-circle',120,'#fff')}</div>`;
  R.innerHTML=`<div style="display:grid;place-items:center;height:100%">${icon('check-circle',120,C1)}</div>`;
  chip(g,175,620,'DULU','#ffffff'); chip(g,595,620,'SEKARANG',C1);
  fadeIn(L,t0,.4,{x:-60}); fadeIn(R,t0+.25,.4,{x:60});
  tl.to(L,{opacity:.45,duration:.3},tWin); shake(tWin,6,.2); sfx(tWin,'tick');
  exit(g,t1); }
```

Butuh 1,5-2,5 detik untuk dibaca. Kalau tidak ada ucapan di situ, tambahkan jeda di `project.json` → `pauses`.

### D2. Sebelum-sesudah dengan garis geser
Pemicu: hasil edit, transformasi, perbaikan. Dua gambar menumpuk; yang "sesudah" dibuka dengan `clipPath: inset(0 X% 0 0)` dari 100% ke 0% mengikuti garis vertikal tipis `C1` yang bergeser.

### D3. Dua hal digabung jadi satu
Pemicu: "digabung", "ditempel", "dipasangkan". Dua kartu berdampingan dengan tanda `+` di tengah, meluncur dan bertabrakan tepat di kata kuncinya, lalu hasil gabungan muncul dari skala 0,62 dengan `brightness 2.6 → 1` plus getaran kecil. Helper: `imgCard` + `plusSign` + `mergeTo` + `popIn`. Untuk alur bertahap lihat N1.

---

## E. Saat menyebut alat, aplikasi, atau produk

### E1. Logo + nama dengan sorotan berpindah
Pemicu: "pakai tool apa", "aplikasinya", daftar platform. Baris logo + nama; sorotan berpindah antar baris dengan jeda menurun, lalu berhenti di satu, sisanya meredup ke `opacity:.38`. Logo resmi pihak ketiga diambil sesuai `asset-sourcing.md`, **tidak digambar ulang**; kalau tidak ada, tulis nama produknya dalam huruf mono. (Logo milik user sendiri: resep O1.)

### E2. Kolom ketik
Pemicu: "promptnya", "cari di Google", "ketik ini". Kotak radius 22px bertepi `C1` tipis, teks diketik per huruf, kursor blok berkedip hanya setelah selesai.

```js
{ const t0=T(40.2), dur=1.6, t1=T(43.5), TXT='buatkan caption untuk produk kopi';   // isi dari user; kalau mengarang, laporkan
  const g=grp(t0-.2,t1); bgBlur(t0-.2,t1);
  const box=A(g,540,900,'<span class="ty"></span><span class="cu">▍</span>','',{width:'820px',minHeight:'120px',padding:'34px 40px',
     borderRadius:'22px',border:'2px solid color-mix(in srgb,var(--c1) 60%,transparent)',background:'rgba(10,12,14,.82)',
     font:'500 40px JB',color:'#fff',whiteSpace:'normal',lineHeight:'1.35'});
  const ty=box.querySelector('.ty'), cu=box.querySelector('.cu'); fadeIn(box,t0-.2,.3);
  perFrame.push(t=>{const u=(t-t0)/dur,n=Math.max(0,Math.min(TXT.length,Math.floor(u*TXT.length)));
    if(ty._n!==n){ty.textContent=TXT.slice(0,n);ty._n=n;} cu.style.opacity=(u>1&&Math.floor(t*2.5)%2)?0:1;});
  for(let i=0;i<TXT.length;i+=3)sfx(t0+dur*i/TXT.length,'key',.6);
  exit(g,t1); }
```

### E3. Rekonstruksi UI dari screenshot user
Pemicu: user mengirim tangkapan layar yang kecil, ramai, atau tidak rapi. **Jangan ditempel apa adanya.** Bangun ulang sebagai panel bersih: kartu, daftar, kolom, angka. Teks dan angkanya diambil dari screenshot asli, tata letaknya netral (bukan tiruan persis UI perusahaan lain).

### E4. Mockup HP berisi klip atau screenshot
Pemicu: "di HP", "aplikasinya begini", contoh hasil video. `phone(g)` lalu isi layarnya dengan `vid(hp.screen,'klip',n,t0,t1)` atau gambar. Masuk dari bawah dengan sedikit rotasi 3D, `hp.finish()` menambah kilap. **Beberapa contoh video sekaligus: `phoneTrio()` (P2), bukan potongan B-roll full layar.**

---

## F. Saat bercerita atau menyebut kronologi

### F1. Garis waktu
Pemicu: "tahun 2019...", "setelah itu", "tiga bulan kemudian". Garis horizontal tipis tergambar dari kiri, titik-titik muncul satu per satu dengan label tahun/bulan mono di atasnya dan satu kata kecil di bawahnya. Titik yang sedang dibahas diberi warna `C1` dan sedikit membesar.

### F2. Label tempat atau waktu
Pemicu: menyebut kota, tanggal, momen. Label mono kecil di pojok atas (`label(t0,t1,'JAKARTA','MARET 2023')`). Sebentar saja, 2-3 detik.

---

## G. Saat menekankan satu kata atau keputusan

### G1. Kata hantaman
Pemicu: satu kata paling penting di sebuah bagian. Lewat `capplan.json` → `"<nomor>": "X"`. Otomatis besar, `sfx sub`, dan zoom sedikit lebih dekat. Maksimal dua per video.

### G2. Stempel tinta
Pemicu: kata penentu ("DITOLAK", "LOLOS", "WAJIB"). Kotak bergaris tebal diputar -13°, masuk dari skala 2,7 dalam 0,1 detik dengan `power4.in`, plus getaran layar. Tekstur tinta pecah dengan filter SVG `feTurbulence` + `feDisplacementMap`, `mix-blend-mode:multiply` supaya terasa menempel di gambar.

### G3. Garis bawah tergambar
Pemicu: penekanan halus yang tidak perlu kata hantaman. Garis SVG di bawah sebuah kata scene, digambar dengan `strokeDashoffset` dari panjang penuh ke 0 dalam 0,4 detik.

```js
const svg=A(g,540,1000,svgNS(520,30,`<path d="M10 20 Q260 4 510 18" stroke="${C1}" stroke-width="7" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`));
tl.to(svg.querySelector('path'),{attr:{'stroke-dashoffset':0},duration:.4,ease:'power2.out'},T(52.3));
```

---

## H. Saat mengutip atau menyampaikan inti

### H1. Kartu kutipan
Pemicu: kalimat inti, kutipan orang lain, punchline. Latar blur, label mono kecil di atas (`KUTIPAN` atau nama sumbernya, kalau user menyebutnya), kalimat muncul per frasa mengikuti ucapan, satu frasa kunci berwarna `C1`, garis tipis tergambar di bawahnya. Rentangnya masuk `skip`.

### H2. Kartu definisi
Pemicu: menjelaskan istilah ("jadi yang dimaksud dengan X itu..."). Kartu bergaya kamus: istilah besar (kelas `s`), keterangan kelas kata mono kecil, lalu definisi satu kalimat pendek dalam teks biasa.

---

## I. Saat menunjukkan gambar atau hasil

### I1. Zoom ke detail lalu mundur
Pemicu: "lihat detailnya", "teksturnya". Satu kartu dengan `background-image` resolusi besar; yang dianimasikan `backgroundSize` dan `backgroundPosition`, bukan `transform`, supaya tetap tajam. Mulai rapat di detail, mundur saat kalimat menyebut keseluruhan. Gambar kecil di-upscale dulu dengan `lanczos` + `unsharp`.

### I2. Garis pindai
Pemicu: "cek", "periksa", "analisis". Garis `C1` setebal 4px dengan bayangan lebar, turun melintasi kartu dalam 0,7-1,2 detik, grid halus opacity 0,1 di dalam kartu. Untuk pindai berulang: `const q=((u/1.05)%2+2)%2, y=(q<1?q:2-q)*H;`.

### I3. Carousel kartu 3D
Pemicu: "banyak contoh", "berbagai macam", portofolio. 6-8 kartu berdiri melingkar, berputar masuk dan melambat berhenti. Kartu di belakang diredupkan lewat `opacity`, bukan blur. Batasi radius dan skala supaya tidak menabrak safe zone saat berputar.

```js
perFrame.push(t=>{const k=Math.min(1,Math.max(0,(t-t0)/.34)), rot=-540*Math.pow(1-Math.min(1,(t-t0)/2.2),3);
  cards.forEach((c,i)=>{const th=(rot+i*45)*Math.PI/180,sn=Math.sin(th),cs=Math.cos(th),R=330;
    const x=R*k*sn, z=(R*cs-60)*k, y=-z*.13;
    c.style.transform=`perspective(1500px) translate3d(${x}px,${y}px,${z}px) rotateY(${sn*44}deg) scale(${.15+.85*k})`;
    c.style.zIndex=Math.round(z+1000); c.style.opacity=k*(.42+.58*(cs+1)/2);});});
```

### I4. Grid hasil atau lembar bergambar dibangun ulang
Pemicu: user mengirim satu gambar berisi banyak panel (lembar karakter, kolase, grid hasil). Potong per panel (cari kolom/baris yang hampir polos sebagai garis pemisah), lalu susun ulang: satu panel utama besar, panel lain kecil mengapit, label mono kecil di tiap panel.

### I5. Sensor piksel + silang
Pemicu: "jangan ditiru", "contoh yang salah". Versi pikselasi gambar yang sama (dibuat dengan ffmpeg: `scale=iw/28:ih/28:flags=area,scale=W:H:flags=neighbor`) dibuka lewat `clipPath: circle()` yang membesar, lalu dua garis silang putih tergambar.

---

## J. Lebih dari satu orang

### J1. Label nama
Pemicu: orang pertama kali bicara, atau setiap ganti pembicara di menit-menit awal. `label(t0, t0+3, 'NAMA', 'peran')`. Nama dan peran hanya dari user. Taruh di sisi yang tidak dipakai caption (default di atas).

---

## K. Suara

### K1. Bentuk gelombang dari suara asli
Pemicu: "dengarkan", "suaranya", podcast audio. Jangan pakai gelombang acak. Hitung amplitudo per frame dari audio video kerja, simpan ke `build/extra/env.js` sebagai `const ENV=[...]`, lalu gambar bar yang mengikuti `ENV[Math.floor(srcT(t)*30)]`.

```bash
$PY - <<'EOF'
import json, subprocess, numpy as np
raw=subprocess.run(["ffmpeg","-v","error","-i","build/src/main.mp4","-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout
x=np.frombuffer(raw,np.float32); hop=1600
e=[float(np.sqrt((x[i:i+hop]**2).mean())) for i in range(0,len(x)-hop,hop)]; m=max(e) or 1
import os; os.makedirs("build/extra",exist_ok=True)
open("build/extra/env.js","w").write("const ENV="+json.dumps([round(v/m,3) for v in e])+";")
EOF
```

---

## L. Transisi

### L1. Zoom-through antar dunia
Pemicu: pindah dari footage ke scene grafis atau sebaliknya. Yang ditinggalkan membesar ke 1,4-1,55 dengan blur naik selama 0,3 detik, lalu potong keras; yang berikutnya masuk dari skala 1,16 dan blur 16 → 0 dalam 0,34 detik. **Jangan fade silang** antara wajah dan latar grafis.

### L2. Transisi glitch antar shot
Pemicu: potongan antar adegan yang perlu terasa tegas. 15-19 frame di sekitar titik potong dibakar lewat `bake.py glitch`. Intensitas berbentuk segitiga, puncaknya tepat di frame potongan. Hemat; maksimal 2-3 per video.

---

## M. Penutup (sesuai jawaban user untuk pertanyaan penutup)

Semua penutup memakai ekor: isi `project.json` → `tail` dengan 3-6 detik. Video latar tetap jalan lewat `bgBlur(..., {over:.86})`. Isinya muncul bertahap, tidak sekaligus. Jangan memasukkan informasi baru di penutup.

### M1. Ajak komentar kata tertentu
Label kecil "TULIS DI KOMENTAR", kata CTA raksasa (`X`) diketik huruf per huruf (0,06-0,08 detik per huruf, `sfx key`), kolom komentar netral yang terisi kata itu, tombol kirim berubah `C1`, lalu kartu notifikasi pesan masuk bertepi `C2` (`sfx conf`). Kata CTA berdenyut halus (`scale` 1 ± 0,02) supaya frame terakhir tidak mati. **Kata CTA persis seperti yang user tulis.**

### M2. Ajak follow
Handle user (persis seperti yang diberikan) di kartu profil netral: lingkaran foto (potong dari footage), nama, tombol "Follow" yang berubah jadi "Following" dengan centang. Bukan tiruan persis UI aplikasi mana pun.

### M3. "Link di bio" / "klik link di bawah"
Logo user versi kecil (O1) di atas, label mono kecil (mis. "GABUNG KELASNYA"), kalimat ajakan besar dua baris (`k1` + `s`, 128px) persis seperti kata CTA dari user, lalu **`bigArrow()`**: panah datar solid dua warna yang memantul, ke bawah untuk "di bawah", ke atas (`dir:'up'`) untuk "di bio". Panah garis tipis terlalu lemah untuk ajakan. Kata ajakan berdenyut halus (scale 1 ± 0,02) supaya frame terakhir tidak mati.
```js
{ const t0=T(29.75), g=grp(t0,TOTAL); gfxBg(t0,TOTAL+1);
  logoBuild(g,540,470,.62,{emblem:'aset/emblem.png',lines:[['ULTIMATE',104],['HYPER REALISTIC',70]],tag:'...',times:[t0,t0+.1,t0+.18,t0+.26]});
  const a=A(g,540,880,'KLIK LINK','k1',{fontSize:'128px'}), b=A(g,540,1020,'DI BAWAH','s',{fontSize:'128px'});
  popIn(a,t0+.6); popIn(b,t0+.92); bigArrow(g,540,1300,190,{t:t0+1.3}); sfx(t0+1.3,'conf',1); }
```

### M4. Tanpa ajakan
Penutup ringkas: kalimat atau kata inti terakhir dibesarkan di latar blur, garis tipis tergambar, lalu memudar ke hitam di 0,5 detik terakhir.

---

## N. Saat menjelaskan alur / proses berurutan ("mulai dari A, B, sampai C")

### N1. Rantai penggabungan "A + B = C", lalu "C + D = E"
Pemicu: kalimat yang menyebut bahan atau langkah berurutan yang menghasilkan sesuatu: "mulai dari character sheet, foto reference, sampai prompt", "bahan, resep, lalu jadi produk". **Jangan hanya didaftar.** Tunjukkan bahan-bahannya menyatu menjadi hasil, tahap demi tahap. Hasil tiap tahap memakai aset asli user (foto hasil, screenshot hasil); kalau hasil akhirnya video, putar potongan video user sendiri di kartu itu (misalnya PART 1 dari footage-nya, diekstrak dengan `frames.py --clips-only --clip-h 960`).

Tata letak baku (layar penuh, di atas `gfxBg` atau `bgBlur`): dua kartu di x 315 dan 765, y 860, 360x203 (landscape) atau 300x483 (teks/prompt); tanda `+` di tengah; label 34px di bawah tiap kartu (warna aksen untuk kata kedua). Hasil di tengah (540, 860), potret 340x604 (foto) atau 400x711 (video), chip hasil di bawahnya.

Waktu: kartu muncul tepat di kata yang menyebutnya. **Penggabungan terjadi di dalam jeda** yang disisipkan (`gaps.py` → `pauses`, 1,5-2 dtk per tahap) supaya penonton sempat mencerna; tanpa jeda, penggabungan bertabrakan dengan kalimat berikutnya. Tahap kedua: hasil tahap pertama bergeser ke posisi kiri (scale .8), bahan berikutnya masuk di kanan, lalu digabung lagi.

```js
/* pauses di project.json: [[14.86,1.6],[15.85,1.8]]  (posisi dari gaps.py) */
{ const t0=T(12.30), t1=T(16.45), P1=14.86, P2=T(15.84)+.01;      // awal jeda 1 & 2 (detik hasil)
  const g=grp(t0,t1);
  chipC(g,540,250,'MULAI DARI',C2,'stack',t0+.02);                  // elemen pembuka: tidak ada layar kosong
  const a=imgCard(g,315,860,360,203,'aset/charsheet.jpg','50% 45%');
  const b=imgCard(g,765,860,360,203,'aset/fotoref.jpg','50% 28%');
  popIn(a,T(13.18)); popIn(b,T(13.86)); const p1=plusSign(g,540,860,T(13.95));
  const k1=mergeTo(g,[[a,315,860],[b,765,860]],540,860,P1+.1,{plus:p1});
  const ad=imgCard(g,540,860,340,604,'aset/adegan.jpg','50% 40%'); popIn(ad,k1);
  const adL=chipC(g,540,1210,'FOTO ADEGAN',C1,'check-circle',k1+.15); sfx(k1+.15,'tick',.9);
  // tahap 2: hasil bergeser ke kiri, prompt masuk di kanan
  tl.to(ad,{x:-225,scale:.8,duration:.4,ease:'power3.inOut'},T(14.94)-.15);
  tl.to(adL,{opacity:0,duration:.2},T(14.94)-.15);
  const pr=A(g,765,860,'PROMPT...','',{width:'300px',height:'483px' /* kotak ketik, lihat E2 */});
  popIn(pr,T(15.37)); const p2=plusSign(g,540,860,T(15.42));
  const k2=mergeTo(g,[[ad,315,860],[pr,765,860]],540,860,P2+.1,{plus:p2});
  const vm=A(g,540,850,'','frameC',{width:'400px',height:'711px'}); vid(vm,'p1',240,k2,t1); popIn(vm,k2);
  chipC(g,540,1290,'VIDEO MENTAH',C1,'video-camera',k2+.15);
  tl.to(g,{scale:1.3,opacity:0,filter:'blur(14px)',duration:.26,ease:'power2.in'},t1-.26);   // zoom-through keluar
}
```

Catatan `mergeTo`: posisi awal yang diberikan harus posisi kartu SAAT penggabungan dimulai (kartu yang sudah digeser `x:-225` dari 540 → beri 315). Elemen yang sudah di-tween `x`/`scale` tetap aman karena mergeTo memakai tween juga.

---

## O. Logo dan identitas user

### O1. Logo dibangun ulang (simbol + teks diketik ulang)
Pemicu: nama brand/kelas/produk user diucapkan dan user memberi file logo. **Jangan pernah** menempel logo utuh di dalam lingkaran, kotak, atau masker bulat: latar hitam/putih file logo jadi piringan yang terlihat murahan.

1. Potong **simbolnya saja** dari file logo dan pekatkan latarnya jadi hitam murni:
   ```bash
   ffmpeg -i aset/logo.png -vf "crop=W:H:X:Y,curves=all='0/0 0.12/0 0.3/0.22 1/1'" build/aset/emblem.png
   ```
   Lihat hasilnya dengan grid (`drawgrid`) untuk menemukan W/H/X/Y. Simbol di latar putih: pakai `negate` dulu atau `mix-blend-mode:multiply` di latar terang.
2. `logoBuild()` menggabungkan simbol dengan `mix-blend-mode:screen` (hitam hilang), memutarnya pelan, dan mengetik ulang teks logo dengan gradien warna logo (`grad`, default emas `GOLD`). Tiap baris muncul tepat saat katanya diucapkan.
   ```js
   logoBuild(g,540,900,1.15,{emblem:'aset/emblem.png',lines:[['ULTIMATE',104],['HYPER REALISTIC',70]],
     tag:'AI PHOTO &amp; VIDEO WORKFLOW',times:[t0,T(16.95),T(17.10),T(17.88)]});
   ```
   Versi kecil di penutup: skala .62 di y 470.
3. Warna gradien diambil dari logo aslinya (ambil 3-4 warna dari terang ke gelap). Teks logo diketik persis seperti di logo.

---

## P. Bagian full motion graphic

### P1. Rentang tanpa wajah
Pemicu: jawaban pertanyaan nomor 9 ("part 2 dan 3 full motion graphic"). Satu `gfxBg(t0,t1)` menutup seluruh rentang, dipanggil sebelum scene-scene di dalamnya. `t0` tepat setelah kata terakhir part sebelumnya, `t1` tepat sebelum kata pertama part sesudahnya. Di dalam rentang:
- tiap kalimat punya visual (HP berisi klip, rantai penggabungan, logo, angka + dinding video, kartu);
- caption boleh tetap jalan di bawah kalau scene tidak membawa teksnya sendiri, dan latar gelap gfxBg sudah cukup kontras;
- transisi antar scene: zoom-through (L1), bukan fade ke wajah.
Wajah kembali di part berikutnya bersama caption dan zoom berirama. Penutup di ekor (`tail`) boleh memakai `gfxBg` sendiri.

### P2. Tiga HP berisi contoh video
Pemicu: "video AI", "contoh hasil", "konten seperti ini". `phoneTrio()`: HP tengah besar (skala 1,32) muncul di kata pertama, dua HP samping (skala .95, miring ±20°, sedikit digelapkan) di kata berikutnya. Klip diambil dari potongan bersih (clipscan). Caption tetap jalan di bawah (y 1400); HP ada di y 435-1165.
```js
phoneTrio(g,t1,[{dir:'ugc',n:135,t:T(8.95),off:.2},{dir:'viral',n:135,t:T(9.25),off:2},{dir:'com',n:135,t:T(8.42),off:2}]);
```

### P3. Angka + dinding video
Pemicu: jumlah koleksi ("113 study case", "500 template"). `videoWall(t0,t1,['w1','w2',...],135)` di latar (ubin 300x534 dari `frames.py --clips-only --clip-h 534`), lalu penghitung B1 dan panel daftar di atasnya. Overlay .74 menjaga teks tetap terbaca.
