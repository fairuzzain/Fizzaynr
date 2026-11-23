/* demo-scenes.js — contoh pemakaian SEMUA komponen, dengan campuran scene GELAP dan TERANG.
   Untuk uji: python3 assets/gen_placeholders.py build 45 ; cp examples/demo-scenes.js build/scenes.js ; python3 assets/build.py build
   Di proyek asli: ganti semua teks, gambar, folder klip, dan waktu dengan konten user. Jangan sisakan teks contoh. */

// Jendela wajah (talking head). Di luar jendela = latar motion graphic.
bgMotion([[0,3],[9,12]]);

// Caption di atas wajah: satu blok rapat (baris kecil + kata besar).
cap(2.9,YC,[[['Bingung',0.3],['cari',0.6],['ide',0.85]],[['konten?',1.2,'s']]]);
cap(11.9,YC,[[['Padahal',9.3],['caranya',9.7]],[['SIMPEL',10.3,'R']]]);

// 3-6 gelap: hook search
sceneSearchHook(3,6,{query:'konten viral',typeAt:3.2,results:['Beli iklan mahal','Posting tiap jam','Ikut tren asal-asalan'],resultsAt:4.1,strikeAt:[4.7,4.95,5.2],qAt:5.4});

// 6-9 TERANG: profil
sceneProfile(6,9,{light:true,avatar:'img/avatar.png',name:'Nama Kreator',handle:'namakreator',bio:'Bikin konten tiap hari',grid:['img/shot1.png','img/shot2.png','img/shot3.png',{dir:'c1'},{dir:'c2'},'img/shot4.png'],highlightAt:7.2,pill:'Akun ini naik dalam 30 hari'});

// 12-15 gelap: kolase
sceneCollage(12,15,{items:[{dir:'c1'},{dir:'c2'},{dir:'c3'},{dir:'c4'},{dir:'c5'},{dir:'c6'},'img/shot1.png','img/shot2.png','img/shot3.png'],marks:['check','check','x','check','x','check','check','x','check'],markAt:13.4});

// 15-18 TERANG: carousel + langkah
sceneCarousel(15,18,{light:true,wipe:'circle',items:[{dir:'c1'},{dir:'c2'},{dir:'c3'},{dir:'c4'},{dir:'c5'}],pick:2,pickAt:16.2,steps:['Pilih ide','Tulis naskah','Rekam'],stepsAt:[16.7,17.0,17.3]});

// 18-21 gelap: anotasi
sceneAnnotate(18,21,{src:{dir:'c3'},scanAt:18.4,labels:[['Hook 3 detik',19.0,'l',.2],['Teks besar',19.4,'r',.45],['CTA jelas',19.8,'l',.75]]});

// 21-24 TERANG: checklist
sceneChecklist(21,24,{light:true,src:{dir:'c4'},title:'Wajib ada',items:[['Hook kuat',21.6],['Satu ide',22.0],['Caption rapi',22.4],['Ajakan jelas',22.8]]});

// 24-27 gelap: filmstrip
sceneFilmstrip(24,27,{clip:{dir:'c5',n:90},playFrom:24.6,playTo:26.6,seconds:3});

// 27-30 gelap: browser
sceneBrowser(27,30,{url:'contoh-alat.ai',src:{dir:'c6'},title:'Satu alat saja',titleAt:28.2});

// 30-33 gelap: dinding screenshot lalu HP fokus
sceneWall(30,33,{imgs:['img/shot1.png','img/shot2.png','img/shot3.png','img/shot4.png','img/shot5.png','img/shot6.png'],focus:{src:{dir:'c1'},at:31.6,pill:'Yang ini paling laris'}});

// 33-36 TERANG: satu HP
scenePhoneFocus(33,36,{light:true,src:{dir:'c2'},label:'Hasil akhirnya',pill:'Dibuat dalam 10 menit',pillAt:34.4});

// 36-39 gelap: coba lalu gagal
sceneTryFail(36,39,{prompt:'Buatkan video viral tentang kopi',typeAt:36.3,genAt:37.3,failAt:38.2,badge:'GAGAL'});

// 39-42 TERANG: CTA komentar
sceneCommentCTA(39,42,{light:true,label:'Mau templatenya?',word:'MAU',typeAt:39.6,sendAt:40.4,link:'Klik link di bio',linkAt:40.9});

// 42-45 gelap: penutup
sceneClosing(42,TOTAL,{label:'TERIMA KASIH',word:'MAU?',line:'Ketik di kolom komentar',green:'Gratis untuk 100 orang',small:'*selama kuota masih ada'});
