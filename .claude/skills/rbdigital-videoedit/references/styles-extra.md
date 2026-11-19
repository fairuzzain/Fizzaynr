# Style 22-85: resipi

Baca bila build mana-mana style 22-85. Semua guna struktur komposisi asas SKILL.md (#ground, #cam > #stage > #vid / #behind / #cut, overlay, caption) dan peraturan lint. Tag **[cutout]** = perlu `cutout.webm` (tech.md §4); **[bg-swap]** = `#vid` opacity 0, `#cut` atas latar baru (resipi #2); **[aset]** = perlu fail user atau bina sendiri dalam HTML/SVG.

## Peraturan umum
- **Deterministik**: tiada `Math.random`/`Date`. Kedudukan zarah, jitter, orbit: array tetap atau formula (`sin(i*2.4)`), kira masa build.
- **3D CSS**: `perspective:1600px` pada pembalut (bukan pada elemen yang GSAP animate), `transform-style:preserve-3d`, GSAP animate `rotationX/rotationY/z`. Elemen "belakang badan" letak dalam `#behind` (bawah `#cut`), elemen "depan" letak selepas `#cut`. Satu elemen yang lalu depan & belakang = dua salinan, tukar `opacity` ikut sudut (`cos(a) > 0` → depan).
- **Gerak setiap frame** (orbit, jitter, boil): satu proxy tween `{a:0}→{a:N}` dengan `onUpdate` yang set posisi dari nilai `a`, ATAU `tl.set` per frame / per 2-3 frame (stop-motion). Jangan `repeat:-1`.
- **Stop-motion / 12fps**: `ease:'steps(n)'` atau `tl.set` setiap 0.083s.
- **SVG lukis diri**: `stroke-dasharray = stroke-dashoffset = panjang path` (kira masa build, contoh 1200), tween offset → 0.
- **Morph tanpa plugin berbayar**: `clip-path: polygon()` dengan BILANGAN titik sama, atau `border-radius` 8 nilai, atau tukar beberapa path SVG siap dengan `tl.set` (boil).
- **Pra-render ffmpeg/python** untuk rupa yang mahal di browser (piksel, ASCII, duotone, halftone): jana klip berasingan `fx_X.mp4` (bt709, `-an`), main sebagai `<video muted id=fxX>` atas `#vid` dengan opacity/mask, sync `data-start`.
- **Logo / brand / UI app sebenar**: hanya fail user. Tiada → versi generik rekaan, label jelas.
- Satu style "besar" setiap seksyen; muka tetap nampak ≥ 60% masa (talking head = trust). Style yang menyembunyikan muka (#27, #48, #78) → muka dalam bulatan PIP 260px atau cutout di sudut.

## 3D / Ruang / Kamera

22. **Orbit** [cutout]: cincin 6-10 item (icon, perkataan, logo user) radius 420px, pusat ~ dada (540, 900). Proxy `a` 0→2π sepanjang seksyen: `x=R·cos(a+i·step)`, `y=80·sin(a+i·step)` (elips), `scale=0.75+0.25·sin(...)`, `z` ikut sin. Item dengan sin<0 dalam `#behind`, lain depan `#cut` (dua salinan, tukar opacity). Blur ringan item belakang. Masuk: cincin mengembang dari 0 + whoosh. Keyword sedang disebut maju ke depan & membesar.

23. **Couch Wall** [cutout][bg-swap]: latar = dinding gelap dengan grid 3x4 frame/TV (bucu 12px, border nipis, glow skrin). Setiap frame isi still dari footage (ffmpeg `-ss T -frames:v 1`), screenshot user atau kad keyword. Frame menyala satu-satu ikut point; frame aktif glow + scale 1.08. Kamera dolly perlahan (`#ground` scale 1→1.08). Kau di depan, bayang lembut bawah badan.

24. **UI World** [cutout][bg-swap]: latar app gergasi dalam perspektif (lantai `rotationX:60`): butang, toggle, kad, slider bersaiz bangunan, palette app. Elemen bertindak ikut ayat (toggle ON pada "boleh", slider naik pada "lebih"). Kau berdiri atas "lantai" UI, bayang di lantai. Kad besar bangun dari lantai (`rotationX:90→0`).

25. **Frame Break** [cutout]: `#stage` jadi frame/skrin (scale 0.8, border 14px). Pada punch word: retakan SVG (garis zigzag dilukis 0.15s) → 8-12 serpihan poligon (`clip-path` salinan frame) terbang keluar dengan rotation tetap → `#cut` (tanpa clip) membesar keluar frame + shake + boom. Selepas itu frame hilang, kau kekal full.

26. **Isometric World** [bg-swap][cutout pilihan]: kontena `rotationX:55, rotationZ:-45`, grid lantai. Blok kubus (3 muka div, warna gelap/terang/sederhana) naik dari lantai (`z` 0→tinggi) satu setiap point, icon atas blok. Kau berdiri di depan/tepi, atau muka dalam bulatan PIP. Kamera pusing perlahan (`rotationZ` -45→-35).

27. **Infinite Canvas**: `#canvas` 4000x6000 latar grid titik, berisi kad nota, screenshot, gambar, anak panah antara kad. Setiap point = kamera (transform `#canvas` x/y/scale) terbang ke kad seterusnya (0.6s power3.inOut), kad aktif highlight. Muka: cutout di bawah kanan (scale 0.55) atau bulatan PIP. Akhir: zoom keluar tunjuk keseluruhan peta.

28. **Parallax Layers** [cutout]: 4 lapis: latar (still footage blur atau gambar user) bergerak x -40, bentuk/teks tengah x -90, `#cut` x -20, latar depan (daun/partikel/teks besar kabur) x -180, serentak scale ringan. Tukar arah setiap seksyen. Bagus untuk hook & transition.

29. **Macro World** [cutout][bg-swap][aset]: latar = objek gergasi (foto keyboard/phone/meja dari user atau image prompt). `#cut` scale 0.3-0.4, berdiri atas objek, bayang kontak. Tilt-shift: blur atas & bawah (dua jalur dengan `backdrop-filter:blur` + mask gradient). Objek bertindak (kekunci ditekan bila sebut "tekan").

30. **Tunnel Type** [cutout pilihan]: 10-14 cincin teks/bingkai (`translateZ` -400·i) dalam satu kontena `preserve-3d`; tween kontena `z` 0→4000 (kamera terbang masuk), cincin lepas kamera fade. Teks = keyword berulang. Kau cutout di depan atau muncul di hujung terowong (scale 0.2→1).

31. **Vertigo** [cutout][aset plate]: perlu plate latar tanpa subjek (frame bersih user, foto lokasi, atau latar rekaan). `#vid` opacity 0; plate scale 1→1.35 (atau 1.35→1) sementara `#cut` kekal saiz. Tambah blur/vignette naik + bunyi drone rendah. 1-2s sahaja, pada momen "shock".

32. **Pull-Back Reveal**: mula `#cam` scale 1.15 (muka rapat). Tarik keluar (1.0s power2.inOut) ke scale 0.32-0.4: rupanya video dalam phone di tangan / billboard di bandar / skrin TV / muka depan majalah (mockup HTML atau gambar user di `#ground`). Untuk hook atau ending; phone mockup boleh terus jadi #35.

33. **Digital Zoom**: pilih titik (mata, skrin, objek). Kotak fokus putih nipis + label "ENHANCE ×4" monospace muncul, `#cam` zoom 1→2.2 berlangkah (`steps(3)`) ke titik tu. Pra-render: klip sama di-pixelate (`scale=iw/16:-1,scale=1080:1920:flags=neighbor`) crossfade masuk pada langkah terakhir + grid piksel overlay. Footage ≤1080p: jangan lebih 2.2 tanpa pixelate (pecah).

34. **Zoom-Through Cut**: transition antara seksyen/take. Pilih kawasan gelap (baju, mulut, anak mata, lubang objek): `transform-origin` ke titik tu, `#cam` scale 1→6 + blur 0→12px dalam 0.25s power3.in; shot seterusnya masuk scale 0.4→1 + blur 12→0 power3.out. Whoosh. Max 2 kali/video.

## Layout / Kad / Transition

35. **Phone Mockup**: `#cam` scale 0.56 dalam bingkai phone (CSS: bucu 70px, bezel hitam 18px, notch). UI app generik keliling (nama akaun rekaan / handle CLAUDE.md, hati & komen terbang naik, kiraan like naik). Phone tilt 3D sikit (`rotationY` ±8) dan float. Latar gradient brand. Kad/tooltip muncul di luar phone ikut point.

36. **Bento Grid**: grid 2-3 lajur, gap 18px, bucu 28px. Tile besar = video muka (`#cam` dalam tile via clip-path/scale). Tile lain: keyword besar, nombor counter, icon, screenshot, mini carta. Setiap beat grid susun semula: kira kedudukan setiap tile per layout, tween `left/top/width/height` 0.5s power3.inOut. Max 3 layout.

37. **Card Stack**: setiap point = kad (bucu 32px, bayang) bertindan dengan offset y -18 & scale 0.96 setiap lapis. Point seterusnya: kad atas swipe (`x:-900, rotation:-14` 0.35s), kad bawah naik ke depan. Video muka di separuh atas atau sebagai kad pertama. Kiraan "2/5" di sudut.

38. **Accordion Panels**: 4-5 jalur menegak (flex row), setiap satu gambar/still/footage crop (`object-position` beza). Panel aktif `flex-grow` 1→5 (tween `width` px), lain mengecil & gelap, label menegak di setiap panel. Panel pertama = muka.

39. **Cover Story** [cutout]: freeze frame terbaik (ffmpeg `<img>`) atau footage; masthead serif 240px BELAKANG kepala, cover lines kiri/kanan (Inter Tight + serif italic), issue "No.01 · 2026", barcode SVG, harga. Masuk: elemen tersusun satu-satu 0.08s. Untuk hook (2-3s) atau CTA. Beza #21: ini satu cover penuh, bukan gaya sepanjang video.

40. **Headline Wall** [cutout]: dinding 12-20 kad headline/tweet/komen REKAAN (label "contoh" kalau nampak real), sedikit senget, scroll menegak perlahan di `#behind`. Headline yang disebut keluar ke depan `#cut` (z+, scale 1.3, highlight kuning). Untuk topik "ramai cakap…", berita, myth.

41. **Before / After Wipe**: dua lapis (sebelum: footage raw / gambar lama; selepas: graded / hasil). Garis putih 6px + pemegang bulat bergerak x 0→1080 (`clip-path: inset(0 X 0 0)` pada lapis atas, X tween sama). Label BEFORE/AFTER pill. Boleh balik separuh (yoyo) untuk tekankan.

42. **Match Cut**: rancang dua shot dengan bentuk/gerak sama di posisi sama (muka bulat → jam/pinggan/logo bulat; tangan swipe kanan → kad swipe kanan). Overlay bentuk (bulatan SVG nipis) ikut objek 0.2s sebelum cut, kekal posisi selepas cut, kemudian hilang. Cut tepat, tiada fade. Ambil frame dari footage untuk cari posisi.

43. **Mask Reveal**: shot baru muncul melalui mask: (a) huruf gergasi (`mask-image` SVG text 900px yang membesar 1→20 sampai penuh), (b) bulatan (`clip-path: circle(0%→150% at x y)`), (c) brush (mask PNG/SVG stroke dilukis). 0.5-0.7s. Mask teks = keyword ayat tu.

## Info / Proses

44. **Checklist**: kad (krim/gelap) sebelah atau bawah muka; item masuk satu-satu (y 20→0), kotak kosong → tick dilukis (dashoffset 0.25s) + pop SFX; item "salah" dapat strike merah (scaleX 0→1). Item aktif tebal, lain malap. Kiraan "3/5 ✓".

45. **Chart Grow**: kad separa lutsinar sebelah muka. Bar: `scaleY 0→1` transform-origin bawah, berselang 0.12s; garis: path dashoffset; nombor atas setiap bar counter (`tl.set` textContent 20 langkah). Bar penting warna aksen + label. Paksi & grid nipis. Nombor dari ayat, jangan reka data.

46. **Timeline Scroll**: separuh bawah (y 1250-1500 elak caption → caption naik ke 1100) garis mendatar panjang; tanda tahun/langkah; seluruh trek bergerak x ikut masa ayat; titik "kini" di tengah berdenyut; label aktif membesar. Muka atas.

47. **Map Journey** [aset]: peta ringkas (SVG bentuk abstrak/rekaan, atau gambar peta user), Ken Burns. Laluan putus-putus dilukis (dashoffset) antara pin; pin jatuh (y -60→0 back.out) + label nama tempat; kamera ikut pin aktif. Muka dalam bulatan PIP atas kanan atau seksyen berasingan.

48. **Blueprint Build**: latar biru #1d4e89 + grid putih 8% opacity. Objek (UI, produk, rajah) dilukis garis putih stroke-by-stroke, label dimensi + anak panah, font monospace. Kemudian lapis "sebenar" (gambar/UI siap) masuk melalui wipe kiri → kanan. Muka PIP.

49. **Wireframe Reveal**: kotak kelabu (#d9d9d9) + garis X untuk gambar, garisan teks kelabu; kemudian setiap blok bertukar jadi versi siap (warna, teks, gambar) satu-satu (crossfade 0.2s + scale 0.98→1). Sesuai topik design/website/app; atas muka atau split.

50. **Exploded View** [cutout pilihan]: objek (phone / frame video) dalam 3D (`rotationX:55, rotationZ:-30`), pecah jadi 4-5 lapisan (`z` 0, 80, 160...) dengan label garis penunjuk. Topik edit video: lapisan FOOTAGE / CAPTION / EFFECT / MUSIC / B-ROLL. Masuk satu-satu ikut ayat, kemudian cantum semula (z → 0) jadi hasil akhir.

51. **Product Assembly** [aset]: bahagian (PNG user, atau bentuk SVG) mula bertabur di luar frame dengan rotation tetap, terbang masuk & "snap" (back.out 1.6) satu-satu + click SFX, akhir flash + nama produk/logo. Untuk reveal hasil / CTA.

52. **Domino Chain**: 4-6 jubin (kad dengan teks sebab-akibat) berdiri dalam barisan senget. Jubin jatuh berantai (`rotation 0→70`, transform-origin bawah kanan, berselang 0.15s) + tick SFX; jubin terakhir = hasil (warna aksen, glow). Bawah muka.

## UI / Digital

53. **Notification Storm**: notifikasi gaya iOS generik (app rekaan, bucu 26px, blur kaca) jatuh bertindan cepat dari atas (0.08s jarak), phone/`#cam` bergegar, badge 1→99+. Pada "tapi…": swipe clear semua ke kanan + sunyi. Untuk topik overload/distraction.

54. **Search Bar Story**: bar carian generik (tiada logo Google) tengah skrin; teks soalan menaip + cursor, 3-4 cadangan autocomplete muncul, satu dipilih, hasil (kad) slide naik. Muka bawah atau mengecil ke PIP semasa typing.

55. **Cursor Journey**: cursor SVG hitam/putih bergerak sepanjang laluan keyframe (x/y dengan ease power2.inOut), hover = elemen highlight, klik = cursor scale 0.85 + ripple bulatan + click SFX. Atas UI rekaan/screenshot user. Boleh atas muka (klik keyword dalam caption).

56. **Terminal / Code**: tetingkap gelap (3 titik merah/kuning/hijau), font JetBrains Mono; prompt `$` + arahan menaip (`tl.set` textContent per aksara, 0.035s), output berwarna muncul baris demi baris, cursor blok berkelip. Syntax highlight warna tetap. Split atas/bawah atau kad sebelah muka.

57. **HUD Interface** [cutout pilihan]: bracket sudut cyan #5fe1ff mengunci muka (dari besar → ketat), cincin SVG putus-putus berpusing (`rotation` proxy), bacaan data monospace (nilai berubah ikut array tetap), garis scan menegak lalu. Grade sejuk. Kunci sasaran baru pada setiap keyword.

58. **Data Stream**: lajur aksara/nombor (array rentetan tetap) mengalir menegak di `#behind` (setiap lajur beza laju, `y` linear), hijau/aksen brand. Garis bercahaya (path) dari tepi ke badan dengan paket titik bergerak (dashoffset). Keyword muncul "decode" (aksara rawak tetap → perkataan sebenar).

59. **Glass Type**: panel kaca `backdrop-filter: blur(24px) saturate(1.4)`, latar rgba(255,255,255,.14), border 1.5px rgba(255,255,255,.4), bayang lembut; teks tajam putih besar di dalam. Panel slide/float atas footage, highlight bergerak di border (gradient). Elak atas muka. Sahkan backdrop-filter dalam snapshot render.

60. **Logo Playground** [aset logo user, WAJIB]: logo SVG/PNG user: masuk melantun (y, squash scaleY 0.8), pecah jadi huruf/bentuk (kalau SVG), berputar 3D (`rotationY`), berulang jadi pattern latar, akhir lock-up tengah + tagline. Tiada logo → jangan buat, tawar style lain.

## Typography / Material

61. **Chrome Type**: teks besar (Anton/Archivo Black) `background: linear-gradient(180deg,#fff 0%,#9aa3ad 45%,#3b4148 50%,#d7dde3 75%,#fff 100%); background-clip:text; color:transparent`, extrude dengan 6-8 `text-shadow` berlapis, kilauan = pseudo-lapis gradient putih menyerong bergerak x -100%→100% (salinan teks dengan mask). Sesuai belakang badan (#1) untuk perkataan "premium".

62. **Claymorphism**: bentuk bucu besar (40px+), warna pastel, `box-shadow` dalam & luar (cerah atas kiri, gelap bawah kanan). Icon & kad lembut; gerak squash-stretch (scaleX 1.1/scaleY 0.9 → 1, elastic.out). Latar pastel [bg-swap] atau kad atas footage.

63. **Liquid Morph**: blob SVG dengan 3-4 path siap (bilangan titik sama), tukar dengan `attr:{d}` tween; gooey: kumpulan bulatan + `filter: url(#goo)` (feGaussianBlur 12 + feColorMatrix alpha 20 -9). Untuk transition (blob membesar tutup skrin → shot baru) dan bekas keyword.

64. **Shape Morph**: `clip-path: polygon()` 8 titik untuk bulat (anggaran), segi empat, segi tiga, bintang; tween antara bentuk ikut point (1, 2, 3). Bentuk jadi bingkai video muka atau penanda keyword. Warna bertukar setiap bentuk.

65. **Line Art Flow**: satu path SVG panjang (garis berterusan) melingkar keliling badan dan membentuk icon/perkataan di hujung (dashoffset ikut ayat). Dua salinan (depan/belakang `#cut`) untuk ilusi melingkar [cutout]. Stroke putih 6px + glow halus.

66. **Ribbon Flow** [cutout]: reben = path SVG tebal (40-60px) dengan gradient, melingkar badan; bahagian depan & belakang dua path dipisah. `textPath` dengan keyword mengalir sepanjang reben (`startOffset` tween). Masuk: dashoffset; gerak: offset berterusan.

67. **Particle Form**: kira titik sasaran masa build (python: render perkataan/logo ke bitmap kecil, ambil 300-600 piksel aktif → JSON). Titik mula bertabur (posisi formula), tween ke sasaran (stagger tetap) membentuk perkataan, tahan 0.6s, kemudian bersepai. Div bulat 6px atau satu canvas yang dilukis dalam `onUpdate` (deterministik).

68. **Dot Matrix**: grid titik (contoh 64x12) LED oren/merah, titik padam malap. Huruf dari font 5x7 (jadual tetap dalam kod) dinyalakan; teks berjalan (anjakan lajur setiap 0.05s `tl.set`). Papan di atas atau bawah muka, atau belakang badan.

## Retro / Cetak

69. **Risograph**: pra-render footage duotone (ffmpeg: `format=gray,curves`, kemudian dua lapis warna pink #ff48b0 & biru #0078bf dengan `blend=all_mode=multiply`, satu lapis offset 4px), grain + tekstur kertas (overlay PNG noise). Teks & bentuk 2 warna sahaja, overprint (`mix-blend-mode:multiply`), salah daftar 3-5px.

70. **Halftone Comic**: overlay titik halftone (`radial-gradient` pattern 8px, `mix-blend-mode:multiply`) atas footage posterize (CSS `contrast(1.4) saturate(1.5)` atau ffmpeg `posterize`). Panel komik (border hitam 10px, footage dalam 2-3 panel), bubble pertuturan dengan ekor, burst "POW!"/"WOW!" Bangers bintang SVG + shake. Garis laju (speed lines) radial pada punch.

71. **Pixel Motion**: pra-render footage pixelate (`scale=135:-1,scale=1080:1920:flags=neighbor`) + palette terhad (`paletteuse` 16 warna). UI 8-bit: font VT323/Press Start, bar HP, syiling/hati sprite SVG kotak, bunyi chiptune (sine/square numpy). Gerak berlangkah `steps()`.

72. **ASCII Motion**: pra-render dengan python: setiap frame → grid aksara (`@%#*+=-:. ` ikut kecerahan, 90 lajur), lukis guna PIL font monospace hijau/putih atas hitam → `ascii.mp4`. Dalam komposisi: transition real → ASCII (mask wipe) untuk seksyen tech, kembali real untuk CTA.

73. **Stamp & Print**: latar kertas (krim + tekstur noise), elemen "dicop": scale 1.4→1 power4.in + rotation tetap, tekstur dakwat (mask grunge SVG feTurbulence), shake 0.1s + bunyi thud. Warna dakwat merah/biru tua. Caption macam cop dakwat.

74. **Marker Highlight**: highlighter (kuning/hijau 45% opacity, `mix-blend-mode:multiply`, bucu tak sekata) di belakang keyword caption/screenshot, `scaleX 0→1` transform-origin kiri 0.25s. Bulatan & anak panah lukis tangan (path SVG dashoffset, stroke 8px marker). Font Permanent Marker untuk nota.

## Kraf / Buatan tangan

75. **Paper Cut** [cutout]: `#cut` dengan border kertas putih (`drop-shadow` putih 8 arah + bayang). Lapisan kertas (path SVG tepi tak rata, warna pastel, `drop-shadow` 0 6px 10px) di depan/belakang bergerak parallax. Tajuk huruf kertas. Untuk video penuh gaya ni, cadang skill rbdigital-parallax.

76. **Doodle Boil** [cutout pilihan]: doodle SVG (bintang, anak panah, bulatan, bunga api, mahkota) keliling badan; setiap doodle ada 3 versi path sedikit berbeza, `tl.set` tukar setiap 0.083s (line boil). Masuk: dilukis (dashoffset). Warna putih/kuning, stroke 7px hujung bulat.

77. **Sticky Notes**: nota kuning/pink/biru (bayang bawah, sedikit senget, Permanent Marker) ditampal (scale 1.2→1 + rotation, tap SFX) atas dinding/skrin/sebelah muka; nota lama dikopek (rotationX + y). Max 4 nota serentak.

78. **Whiteboard Draw** [bg-swap pilihan]: latar papan putih (#f7f7f5 + kesan pemadam samar), rajah/teks dilukis marker hitam/biru/merah (dashoffset; teks guna font tulisan tangan dengan reveal clip-path kiri → kanan), tangan/marker SVG ikut hujung garis. Kau cutout di tepi kanan (scale 0.7) atau PIP.

79. **Collage Motion**: gambar dipotong (clip-path tepi koyak), tekstur kertas, washi tape, bentuk warna, huruf potong majalah (setiap huruf font/warna beza). Semua gerak berlangkah 12fps (`steps`) dengan jitter tetap ±2px. Footage muka dalam bingkai koyak.

80. **Flipbook**: muka surat (kad krim, sudut ikat di atas) flip `rotationX 0→-180` transform-origin atas, 0.25s setiap muka; setiap muka satu lakaran/keyword/point. Atau footage dimain pada 8fps (`fps=8` pra-render) dengan tekstur kertas & tepi muka surat berlapis.

81. **Stop-Motion Objects** [aset]: objek sebenar (PNG cutout user atau image prompt) bergerak berlangkah (`tl.set` setiap 0.083s) dengan jitter & rotation kecil tetap, bayang kontak. Objek masuk satu-satu membentuk susunan/perkataan. Bunyi tap kecil setiap langkah besar.

82. **Fabric / Felt**: bentuk dengan tekstur felt (SVG `feTurbulence` baseFrequency 0.9 + `feDisplacementMap` halus + warna lembut), border jahitan putus-putus (`stroke-dasharray 10 8` putih), bayang lembut. Caption atas label kain. Gerak lembut (sine) macam digantung.

## Cahaya

83. **Shadow Play** [cutout]: salinan `#cut` dengan `filter: brightness(0) blur(6px)` opacity 0.55 di dinding belakang (offset x+60, scale 1.15, skew). Pada punch: bayang bertukar (crossfade ke siluet lain: raksasa, mahkota, sayap — SVG hitam blur) atau membesar sendiri. Cahaya hangat dari satu arah (gradient radial).

84. **Light Scan**: bar cahaya menyerong (gradient putih → lutsinar, `mix-blend-mode:screen`) sapu x -100%→100% 0.6s; teks/objek yang dilalui menjadi nampak (mask gradient sama bergerak). Lens glint (bintang 4 bucu SVG) pada hujung sapuan. Untuk reveal tajuk, logo, produk.

85. **X-Ray Reveal**: lapis "dalaman" (blueprint, before, rangka, kod, harga sebenar) di atas footage, hanya nampak dalam bulatan kanta 300px (`clip-path: circle(150px at X Y)`, X/Y tween ikut laluan). Bingkai kanta + garis silang. Versi sinar-X: salinan `#cut` `invert(1) hue-rotate(180deg) brightness(1.4)` biru dalam kanta.
