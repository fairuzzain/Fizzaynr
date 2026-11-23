/* =====================================================================
   components.js — 14 komponen generik Serif Editorial Reel (bgMotion + 13 scene).
   Disisipkan build.py ke template. Semua teks, gambar, folder frame, dan waktu = parameter.
   Waktu = detik FINAL (sudah lewat T()).

   Sumber gambar/video (parameter src) boleh:
     'img/foto.jpg'          gambar diam
     {dir:'c1', n:120}       image sequence vf/c1/0001.jpg.. (n = jumlah frame, diputar loop)
     null                    kotak gradien gelap (hanya untuk uji)
   Opsi umum tiap scene:  light:true  -> scene TERANG (lightBg + tinta gelap, tanpa glow)
                          wipe:'up'|'circle'  cara masuk latar terang
   ===================================================================== */

/* ---------- helper komponen ---------- */
function media(parent,src,t0,t1){
 if(!src){mk(parent,'','',{position:'absolute',inset:'0',background:'linear-gradient(160deg,#34343e 0%,#16161b 60%,#0b0b0e 100%)'});return null;}
 if(typeof src==='string'){const im=document.createElement('img');im.src=src;
  im.style.cssText='position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block';parent.appendChild(im);return im;}
 return vid(parent,src.dir,src.n||((typeof CLIPS!=='undefined'&&CLIPS[src.dir])||30),t0,t1);}
// HP di (x,y) dengan skala sc. -> {W (lapisan 3D), w (pembungkus), ph (phone()), sheen}
function phoneAt(g,x,y,sc,src,t0,t1){const W=mk(g,'','p3');const w=P(W,x,y,'','',{});gsap.set(w,{scale:sc});
 const ph=phone(w);media(ph.screen,src,t0,t1);const sheen=ph.finish();return {W,w,ph,sheen};}
// teks dengan warna/glow mengikuti mode gelap/terang
function TX(g,x,y,txt,font,css={}){return A(g,x,y,txt,'',Object.assign({font,color:'var(--ink)',textShadow:'var(--glow)'},css));}
function blurIn(el,t,d=.32,from={}){tl.fromTo(el,Object.assign({opacity:0,scale:1.08,filter:'blur(12px)'},from),{opacity:1,scale:1,filter:'blur(0px)',x:0,y:0,duration:d,ease:'power3.out'},t);}
function popIn(el,t,d=.4){tl.fromTo(el,{opacity:0,scale:0},{opacity:1,scale:1,duration:d,ease:'back.out(2)'},t);}
function outG(g,t1){tl.to(g,{opacity:0,filter:'blur(10px)',duration:.24,ease:'power2.in'},t1-.24);}
// buka scene: grup + latar terang opsional. -> {g, ts (waktu konten mulai)}
function scn(t0,t1,o={}){const g=grp(t0,t1);if(o.light){lightBg(t0-.05,t1+.02,{wipe:o.wipe,tone:o.tone});g.classList.add('lt');}
 outG(g,t1);return {g,ts:t0+(o.light?.22:0)};}
/* stack(items, yTengah, gap): susun elemen (dibuat dengan A/TX) jadi SATU blok rapat yang ditengahkan di yTengah.
   gap angka (px) atau array per sela. Default 0,22 x tinggi elemen yang lebih kecil, maks 36 px.
   Pakai ini untuk teks yang berkaitan, supaya tidak "berjauhan". */
function stack(items,y,gap){const hs=items.map(e=>e.offsetHeight);
 const gp=i=>Array.isArray(gap)?gap[i]:(gap!=null?gap:Math.min(36,Math.round(Math.min(hs[i],hs[i+1])*.22)));
 let tot=hs.reduce((a,b)=>a+b,0);for(let i=0;i<items.length-1;i++)tot+=gp(i);
 let cy=y-tot/2;items.forEach((e,i)=>{e.style.top=(cy+hs[i]/2)+'px';cy+=hs[i]+(i<items.length-1?gp(i):0);});
 return {top:y-tot/2,bottom:y+tot/2};}
function badgeIcon(name,ok){return `<div style="width:54px;height:54px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:${ok?'linear-gradient(180deg,#5dffa0,#14b85a)':'linear-gradient(180deg,#ff6a6a,#d20f1a)'};box-shadow:0 0 18px ${ok?'rgba(40,240,120,.7)':'rgba(255,30,30,.7)'},0 6px 14px rgba(0,0,0,.5)">${icon(name,30,'#fff')}</div>`;}
function typeInto(el,text,t0,step=.068,caretTo=null,snd=true){
 perFrame.push(t=>{const n=t<t0?0:Math.min(text.length,Math.floor((t-t0)/step)+1);
  const on=caretTo===null||t<caretTo;const cr=(on&&t>=t0-.3&&Math.floor(t*3)%2===0)?'▍':'';el.textContent=text.slice(0,n)+cr;});
 if(snd)[...text].forEach((c,i)=>{if(c.trim())sfx(t0+i*step,'type',.5);});return t0+text.length*step;}

/* ===================================================================
   1. bgMotion(face, {src, dim, zoom})
   face = [[a,b],...] jendela WAJAH (detik final). Di luar jendela: latar MG dari footage
   yang diblur kuat + overlay hitam. Masuk ke wajah: zoom-through (dunia MG membesar + blur,
   wajah masuk dari skala .55). Dipanggil SEKALI, sebelum scene lain.
   =================================================================== */
function bgMotion(face,o={}){
 const L=mk(under,'','L');const im=document.createElement('img');
 im.style.cssText='position:absolute;left:-80px;top:-80px;width:1240px;height:2080px;object-fit:cover;filter:blur(40px) saturate(.75) brightness(.6)';L.appendChild(im);
 const src=o.src||{dir:MAIN,n:MAIN_FRAMES};VIDS.push({im,dir:src.dir,n:src.n,t0:-1,t1:TOTAL+1,cur:-1});
 mk(L,'','',{position:'absolute',inset:'0',background:`rgba(0,0,0,${o.dim!=null?o.dim:.84})`});
 mk(L,'','',{position:'absolute',inset:'0',backgroundImage:'linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px)',backgroundSize:'90px 90px',WebkitMaskImage:'radial-gradient(ellipse at 50% 45%,#000 30%,transparent 75%)'});
 const vidL=document.getElementById('vidL'),grade=document.getElementById('grade');
 perFrame.push(t=>{let inF=false,k=0;for(const [a,b] of face)if(t>=a&&t<b){inF=true;k=t-a;}
  let s=1,bl=0;if(o.zoom!==false)for(const [a] of face){const d=a-t;if(a>0&&d>0&&d<.3){const p=1-d/.3;s=1+.4*p*p;bl=16*p;}}
  L.style.visibility=inF?'hidden':'visible';L.style.transform=`scale(${s})`;L.style.filter=bl?`blur(${bl.toFixed(1)}px)`:'none';
  vidL.style.visibility=grade.style.visibility=inF?'visible':'hidden';
  const a0=face.find(([a,b])=>t>=a&&t<b);
  if(inF&&o.zoom!==false&&a0&&a0[0]>0&&k<.35){const e=1-Math.pow(1-k/.35,3);vidL.style.transform=`scale(${(.55+.45*e).toFixed(4)})`;}
  else vidL.style.transform='';});
 face.forEach(([a])=>{if(a>0)sfx(a-.12,'whoosh',.8);});
 return L;}

/* ===================================================================
   2. sceneSearchHook(t0,t1,{query, typeAt, results:[..], resultsAt, strikeAt:[..], qAt, y, light})
   Kolom search mengetik pertanyaan, hasil muncul lalu dicoret satu per satu, tanda tanya besar.
   =================================================================== */
function sceneSearchHook(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const R=o.results||[];
 const bar=A(g,540,0,`<div style="display:flex;align-items:center;gap:22px;width:100%">${icon('magnifying-glass',44,'var(--ink)')}<span class="q" style="font:500 40px I;color:var(--ink)"></span></div>`,'',
  {width:'820px',height:'112px',borderRadius:'56px',background:'var(--panel)',border:'1.5px solid var(--line)',padding:'0 36px',display:'flex',alignItems:'center',boxShadow:'0 20px 50px rgba(0,0,0,.35)'});
 const rows=R.map(r=>A(g,540,0,`<span class="rt" style="position:relative;font:500 34px I;color:var(--sub)">${r}<span class="st" style="position:absolute;left:-6px;right:-6px;top:52%;height:4px;background:var(--red);box-shadow:var(--glowR);transform-origin:0 50%;transform:scaleX(0)"></span></span>`,'',
  {width:'820px',height:'86px',borderRadius:'20px',background:'var(--panel2)',border:'1px solid var(--line)',padding:'0 34px',display:'flex',alignItems:'center'}));
 const q=TX(g,540,0,'?','italic 900 230px PF',{color:'var(--red)',textShadow:'var(--glowR)',lineHeight:'1'});
 stack([bar,...rows,q],o.y||900,[28,...rows.map(()=>14)].slice(0,rows.length).concat([24]));
 blurIn(bar,ts,.35);sfx(ts,'pop');
 const tq=o.typeAt||ts+.3;typeInto(bar.querySelector('.q'),o.query||'',tq);
 rows.forEach((r,i)=>{const t=(o.resultsAt||tq+(o.query||'').length*.068+.2)+i*.14;blurIn(r,t,.3,{y:20});sfx(t,'bubble',.6);});
 (o.strikeAt||[]).forEach((t,i)=>{if(!rows[i])return;tl.to(rows[i].querySelector('.st'),{scaleX:1,duration:.28,ease:'power3.out'},t);
  tl.to(rows[i],{opacity:.5,duration:.2},t+.25);sfx(t,'swish');});
 const tqm=o.qAt||t1-1;tl.fromTo(q,{opacity:0,scale:1.6,filter:'blur(20px) brightness(2.4)'},{opacity:1,scale:1,filter:'blur(0px) brightness(1)',duration:.36,ease:'power3.out'},tqm);sfx(tqm,'thud');
 return {g,bar,rows,q};}

/* ===================================================================
   3. sceneProfile(t0,t1,{avatar, name, handle, bio, stats:[[angka,label],..], grid:[src..], highlightAt, pill, scrollAt, light})
   UI profil akun di HP besar, username disorot, grid postingan bergulir.
   =================================================================== */
function sceneProfile(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);
 const P0=phoneAt(g,540,880,1.62,null,t0,t1);const sc=P0.ph.screen;
 const ui=mk(sc,'','',{position:'absolute',inset:'0',background:'#0c0c0f',padding:'44px 14px 0',color:'#fff',font:'500 9px I'});
 const head=mk(ui,'','',{display:'flex',alignItems:'center',gap:'12px'});
 const av=mk(head,'','',{width:'58px',height:'58px',borderRadius:'50%',overflow:'hidden',flex:'0 0 58px',border:'2px solid #e1306c',position:'relative'});media(av,o.avatar||null,t0,t1);
 const st=mk(head,'','',{display:'flex',gap:'12px',flex:'1',justifyContent:'space-around'});
 (o.stats||[['120','post'],['10rb','pengikut'],['80','mengikuti']]).forEach(([n,l])=>mk(st,`<div style="font:800 13px I;text-align:center">${n}</div><div style="font:400 8px I;color:#aaa;text-align:center">${l}</div>`));
 const nm=mk(ui,o.name||'Nama Akun','',{font:'700 11px I',marginTop:'10px'});
 const hd=mk(ui,'@'+(o.handle||'username'),'',{display:'inline-block',font:'600 11px I',color:'#fff',marginTop:'3px',padding:'2px 6px',borderRadius:'5px',position:'relative'});
 mk(ui,o.bio||'','',{font:'400 9px I',color:'#bbb',marginTop:'5px',lineHeight:'1.35',whiteSpace:'normal'});
 const btn=mk(ui,'Ikuti','',{marginTop:'9px',height:'24px',borderRadius:'6px',background:'#0095f6',font:'700 10px I',display:'flex',alignItems:'center',justifyContent:'center'});
 const gw=mk(ui,'','',{marginTop:'10px',position:'relative',height:'300px',overflow:'hidden'});
 const gr=mk(gw,'','',{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:'2px'});
 const items=o.grid&&o.grid.length?o.grid:[null,null,null,null,null,null,null,null,null];
 for(let i=0;i<Math.max(12,items.length);i++){const c=mk(gr,'','',{position:'relative',aspectRatio:'3/4',overflow:'hidden',background:'#1b1b20'});media(c,items[i%items.length],t0,t1);}
 tl.fromTo(P0.w,{y:260,rotationX:-40,opacity:0},{y:0,rotationX:0,opacity:1,duration:.6,ease:'power3.out'},ts);sfx(ts,'whoosh');
 const tsA=o.scrollAt||ts+1.2;perFrame.push(t=>{const k=Math.max(0,Math.min(1,(t-tsA)/1.6));gr.style.transform=`translateY(${(-120*(k*k*(3-2*k))).toFixed(1)}px)`;});
 const th=o.highlightAt||ts+.8;tl.to(hd,{backgroundColor:'#ff2f2f',boxShadow:'0 0 14px rgba(255,40,40,.8)',duration:.18},th);
 tl.to(btn,{backgroundColor:'#26262c',duration:.2},th+.5);
 perFrame.push(t=>{btn.textContent=t>=th+.5?'Mengikuti':'Ikuti';});sfx(th,'click');sfx(th+.5,'pop',.6);
 if(o.pill){const pl=TX(g,540,880+452+50,o.pill,'600 34px I',{padding:'14px 30px',borderRadius:'40px',background:'var(--panel)',border:'1px solid var(--line)'});blurIn(pl,th+.1);}
 return {g,phone:P0};}

/* ===================================================================
   4. sceneCollage(t0,t1,{items:[src..maks 12], marks:['check'|'x'|null..], markAt, light})
   Hingga 12 HP 3D memenuhi layar, tanda di tiap HP.
   =================================================================== */
function sceneCollage(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const it=(o.items||[]).slice(0,12);const n=it.length||9;
 const cols=n>9?4:3,rows=Math.ceil(n/cols),sc=cols===4?.56:.68,dx=cols===4?205:265,dy=cols===4?345:390;
 const box=mk(g,'','L');const ps=[];
 for(let i=0;i<n;i++){const c=i%cols,r=Math.floor(i/cols);const x=540+(c-(cols-1)/2)*dx,y=960+(r-(rows-1)/2)*dy;
  const p=phoneAt(box,x,y,sc,it[i]||null,t0,t1);ps.push(p);const t=ts+.06*i;
  tl.fromTo(p.w,{y:220,rotationX:-55,opacity:0},{y:0,rotationX:0,opacity:1,duration:.5,ease:'power3.out'},t);}
 sfx(ts,'whoosh');perFrame.push(t=>{box.style.transform=`translateY(${Math.sin(t*.8)*8}px) rotate(${Math.sin(t*.5)*.6}deg)`;});
 const mk_=o.marks||[];ps.forEach((p,i)=>{if(!mk_[i])return;const ok=mk_[i]!=='x';const b=mk(p.w,badgeIcon(ok?'check':'x',ok),'',{position:'absolute',left:'95px',top:'-285px'});
  const t=(Array.isArray(o.markAt)?o.markAt[i]:(o.markAt||ts+1))+(Array.isArray(o.markAt)?0:.08*i);popIn(b,t,.35);sfx(t,ok?'pop':'error',.6);});
 return {g,phones:ps};}

/* ===================================================================
   5. sceneCarousel(t0,t1,{items:[src..3-7], pick, pickAt, steps:[label..maks 4], stepsAt:[t..], light})
   HP berderet bergeser, satu dipilih dan maju ke tengah, lalu deretan langkah.
   =================================================================== */
function sceneCarousel(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const it=o.items||[null,null,null,null,null];const pick=o.pick||0;const tp=o.pickAt||ts+1.2;
 const row=mk(g,'','L');row.dataset.qaSkip='';const ps=it.map((s,i)=>phoneAt(row,540+(i-pick)*300,700,.82,s,t0,t1));
 ps.forEach((p,i)=>tl.fromTo(p.w,{opacity:0,y:120},{opacity:1,y:0,duration:.45,ease:'power3.out'},ts+.05*i));sfx(ts,'whoosh');
 perFrame.push(t=>{const k=Math.max(0,Math.min(1,(tp-t)/1.4));row.style.transform=`translateX(${(k*k*420).toFixed(1)}px)`;});
 ps.forEach((p,i)=>{if(i===pick)tl.to(p.w,{scale:1.12,duration:.4,ease:'power3.out'},tp);else tl.to(p.w,{opacity:.28,filter:'blur(3px)',duration:.35},tp);});
 const ring=mk(ps[pick].w,'','',{position:'absolute',left:'-150px',top:'-290px',width:'300px',height:'580px',borderRadius:'52px',border:'4px solid var(--green)',boxShadow:'var(--glowG)'});
 tl.set(ring,{opacity:0},0);tl.fromTo(ring,{opacity:0,scale:1.15},{opacity:1,scale:1,duration:.3,immediateRender:false},tp+.1);sfx(tp,'ding',.7);
 const S=(o.steps||[]).slice(0,4);const ch=S.map((s,i)=>TX(g,540,0,`<span class="mono" style="font:700 24px JB;color:var(--green);text-shadow:var(--glowG);margin-right:16px">${String(i+1).padStart(2,'0')}</span>${s}`,'600 34px I',
  {padding:'14px 28px',borderRadius:'16px',background:'var(--panel)',border:'1px solid var(--line)'}));
 if(ch.length)stack(ch,700+300+40+(ch.length*70+(ch.length-1)*14)/2,14);
 ch.forEach((c,i)=>{const t=(o.stepsAt&&o.stepsAt[i])||tp+.5+i*.35;blurIn(c,t,.3,{x:-40});sfx(t,'pop',.5);});
 return {g,phones:ps,steps:ch};}

/* ===================================================================
   6. sceneAnnotate(t0,t1,{src, labels:[[teks,t,'l'|'r',yFrac]..maks 4], scanAt, light})
   HP membesar, grid + garis scan, label menarik garis dari titik di layar ke luar HP.
   =================================================================== */
function sceneAnnotate(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const sc=1.42,Y=950;
 const P0=phoneAt(g,540,Y,sc,o.src||null,t0,t1);tl.fromTo(P0.w,{scale:.9,opacity:0},{scale:sc,opacity:1,duration:.5,ease:'power3.out'},ts);sfx(ts,'whoosh');
 const gridL=mk(P0.ph.screen,'','',{position:'absolute',inset:'0',backgroundImage:'linear-gradient(rgba(255,255,255,.16) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.16) 1px,transparent 1px)',backgroundSize:'21px 21px',opacity:0});
 const scan=mk(P0.ph.screen,'','',{position:'absolute',left:'0',right:'0',top:'0',height:'3px',background:'#fff',boxShadow:'0 0 14px #fff,0 0 30px rgba(255,255,255,.6)',opacity:0});
 const tsn=o.scanAt||ts+.5;tl.to(gridL,{opacity:1,duration:.3},tsn);tl.fromTo(scan,{opacity:1,y:0},{y:520,duration:1.0,ease:'power1.inOut',immediateRender:false},tsn);tl.to(scan,{opacity:0,duration:.15},tsn+1);sfx(tsn,'tick',.6);
 const half=135*sc,top=Y-270*sc;(o.labels||[]).slice(0,4).forEach(([txt,t,side,yf],i)=>{const L=side==='l';const y=top+(yf!=null?yf:.25+.17*i)*540*sc;
  const dotX=540+(L?-1:1)*half*.45,edge=540+(L?-1:1)*(half+18);
  const dot=A(g,dotX,y,'','',{width:'14px',height:'14px',borderRadius:'50%',background:'var(--green)',boxShadow:'var(--glowG)'});
  const ln=P(g,Math.min(dotX,edge),y-1,'','',{width:Math.abs(edge-dotX)+'px',height:'2px',background:'var(--green)',boxShadow:'var(--glowG)',transformOrigin:L?'100% 50%':'0 50%'});
  const lab=P(g,L?125:edge+10,y-24,txt,'',{width:(L?edge-10-125:955-edge-10)+'px',whiteSpace:'normal',textAlign:L?'right':'left',font:'600 26px I',lineHeight:'1.15',color:'var(--ink)',textShadow:'var(--glow)'});
  popIn(dot,t,.25);tl.fromTo(ln,{scaleX:0},{scaleX:1,duration:.3,ease:'power3.out'},t+.08);blurIn(lab,t+.2,.3);sfx(t,'pop',.5);});
 return {g,phone:P0};}

/* ===================================================================
   7. sceneChecklist(t0,t1,{src, title, items:[[teks,t]..maks 6], light})
   HP di kiri + kartu checklist bertahap di kanan, garis penghubung tergambar, centang hijau.
   =================================================================== */
function sceneChecklist(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const it=(o.items||[]).slice(0,6);
 const P0=phoneAt(g,300,960,.98,o.src||null,t0,t1);tl.fromTo(P0.w,{x:-200,opacity:0},{x:0,opacity:1,duration:.5,ease:'power3.out'},ts);sfx(ts,'whoosh');
 const H=86,G=16,tot=it.length*H+(it.length-1)*G,y0=960-tot/2;
 const rail=P(g,478,y0+H/2,'','',{width:'3px',height:Math.max(0,tot-H)+'px',background:'var(--line)',transformOrigin:'50% 0'});
 const railOn=P(g,478,y0+H/2,'','',{width:'3px',height:Math.max(0,tot-H)+'px',background:'var(--green)',boxShadow:'var(--glowG)',transformOrigin:'50% 0'});
 tl.fromTo(rail,{scaleY:0},{scaleY:1,duration:.5,ease:'power2.out'},ts+.2);tl.set(railOn,{scaleY:0},0);
 if(o.title){const tt=TX(g,715,y0-56,o.title,'italic 800 50px PF');blurIn(tt,ts+.15);}
 it.forEach(([txt,t],i)=>{const y=y0+i*(H+G);
  const c=P(g,500,y,`<div class="ck" style="width:40px;height:40px;border-radius:50%;border:2.5px solid var(--line);flex:0 0 40px;display:flex;align-items:center;justify-content:center">${icon('check',24,'#fff')}</div><span style="font:600 30px I;color:var(--ink);white-space:normal;line-height:1.15">${txt}</span>`,'',
   {width:'455px',height:H+'px',borderRadius:'18px',background:'var(--panel)',border:'1px solid var(--line)',display:'flex',alignItems:'center',gap:'18px',padding:'0 22px',transformOrigin:'50% 0'});
  const k=c.querySelector('.ck');tl.set(k.firstChild,{opacity:0},0);
  tl.fromTo(c,{opacity:0,rotationX:-80,transformPerspective:800,filter:'blur(8px)'},{opacity:1,rotationX:0,filter:'blur(0px)',duration:.38,ease:'power3.out'},t);sfx(t,'swish',.6);
  tl.to(k,{backgroundColor:GREEN,borderColor:GREEN,boxShadow:'0 0 16px rgba(40,240,120,.7)',duration:.18},t+.3);tl.to(k.firstChild,{opacity:1,duration:.12},t+.3);sfx(t+.3,'pop',.6);
  if(i>0)tl.to(railOn,{scaleY:i/(it.length-1),duration:.3,ease:'power2.out'},t+.3);});
 return {g,phone:P0};}

/* ===================================================================
   8. sceneFilmstrip(t0,t1,{frames:[src..5] atau clip:{dir,n}, playFrom, playTo, labels:['AWAL','AKHIR'], light})
   Deretan frame + playhead merah berjalan dari awal sampai akhir, timecode mono.
   =================================================================== */
function sceneFilmstrip(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);
 let fr=o.frames;if(!fr&&o.clip){const n=Math.min(o.clip.n||1e9,(typeof CLIPS!=='undefined'&&CLIPS[o.clip.dir])||o.clip.n||30);fr=[0,.25,.5,.75,.98].map(k=>`vf/${o.clip.dir}/${String(Math.max(1,Math.round(k*n))).padStart(4,'0')}.jpg`);}
 fr=(fr||[null,null,null,null,null]).slice(0,5);const W=150,Hh=266,gap=12,tw=fr.length*W+(fr.length-1)*gap,x0=540-tw/2,Y=900;
 const strip=P(g,x0-18,Y-Hh/2-30,'','',{width:(tw+36)+'px',height:(Hh+60)+'px',borderRadius:'14px',background:'var(--panel)',border:'1px solid var(--line)'});
 blurIn(strip,ts,.3);
 fr.forEach((s,i)=>{const c=P(g,x0+i*(W+gap),Y-Hh/2,'','',{width:W+'px',height:Hh+'px',borderRadius:'8px',overflow:'hidden'});media(c,s,t0,t1);blurIn(c,ts+.08*i,.3,{y:30});});
 sfx(ts,'whoosh');
 const ph=P(g,x0,Y-Hh/2-44,`<div style="width:0;height:0;border-left:12px solid transparent;border-right:12px solid transparent;border-top:16px solid var(--red);margin-left:-12px"></div><div style="width:3px;height:${Hh+56}px;background:var(--red);box-shadow:var(--glowR);margin-left:-1.5px"></div>`,'',{});
 const tcode=TX(g,540,Y+Hh/2+62,'00:00:00','500 28px JB');const a=o.playFrom||ts+.5,b=o.playTo||t1-.5;tl.set(ph,{opacity:0},0);tl.set(ph,{opacity:1},a);
 perFrame.push(t=>{const k=Math.max(0,Math.min(1,(t-a)/(b-a)));ph.style.transform=`translateX(${(k*tw).toFixed(1)}px)`;const s=k*(o.seconds||8);
  tcode.textContent=`00:${String(Math.floor(s)).padStart(2,'0')}:${String(Math.floor((s%1)*30)).padStart(2,'0')}`;});
 blurIn(tcode,a);const lb=o.labels||['AWAL','AKHIR'];
 const l1=P(g,x0,Y-Hh/2-90,lb[0],'',{font:'700 22px JB',letterSpacing:'.12em',color:'var(--sub)'}),l2=P(g,x0+tw-W,Y-Hh/2-90,lb[1],'',{font:'700 22px JB',letterSpacing:'.12em',color:'var(--sub)',width:W+'px',textAlign:'right'});
 blurIn(l1,ts+.3);blurIn(l2,b-.2);sfx(b,'ding',.6);return {g};}

/* ===================================================================
   9. sceneBrowser(t0,t1,{url, src, title, titleAt, light})
   Jendela browser (titik, address bar) berisi video/gambar, masuk miring 3D.
   =================================================================== */
function sceneBrowser(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const W=830,H=600,Y=o.y||880;
 const wrap=mk(g,'','p3');const win=P(wrap,540-W/2,Y-H/2,'','',{width:W+'px',height:H+'px',borderRadius:'18px',overflow:'hidden',background:'#121216',boxShadow:'0 40px 90px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.12)',transformOrigin:'50% 100%'});
 const bar=mk(win,`<div style="display:flex;gap:9px">${['#ff5f57','#febc2e','#28c840'].map(c=>`<span style="width:14px;height:14px;border-radius:50%;background:${c};display:block"></span>`).join('')}</div><div class="url" style="flex:1;height:36px;border-radius:18px;background:#2a2a31;display:flex;align-items:center;gap:10px;padding:0 16px;font:500 20px I;color:#ddd">${icon('lock-simple',16,'#9a9aa3')}<span class="u"></span></div>`,'',
  {height:'62px',background:'#1d1d22',display:'flex',alignItems:'center',gap:'22px',padding:'0 20px'});
 const body=mk(win,'','',{position:'absolute',left:'0',right:'0',top:'62px',bottom:'0',overflow:'hidden'});media(body,o.src||null,t0,t1);
 tl.fromTo(win,{rotationX:32,y:150,opacity:0,filter:'blur(10px)'},{rotationX:0,y:0,opacity:1,filter:'blur(0px)',duration:.6,ease:'power3.out'},ts);sfx(ts,'whoosh');
 scr(bar.querySelector('.u'),o.url||'example.com',ts+.35,.5);
 if(o.title){const tt=TX(g,540,Y+H/2+70,o.title,'italic 800 64px PF');blurIn(tt,o.titleAt||ts+.6);}
 return {g,win,body};}

/* ===================================================================
   10. sceneWall(t0,t1,{imgs:[src..], focus:{src, at, pill}, light})
   Dinding screenshot besar miring yang bergulir, lalu (opsional) satu HP maju ke depan.
   =================================================================== */
function sceneWall(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const im=o.imgs&&o.imgs.length?o.imgs:[null,null,null,null,null,null];
 const wall=mk(g,'','L');wall.dataset.qaSkip='';const inner=mk(wall,'','',{position:'absolute',left:'-260px',top:'-300px',width:'1600px',height:'2520px',transform:'rotate(-9deg)',display:'flex',gap:'26px',justifyContent:'center'});
 const cols=[];for(let c=0;c<4;c++){const col=mk(inner,'','',{display:'flex',flexDirection:'column',gap:'26px',width:'340px'});cols.push(col);
  for(let k=0;k<6;k++){const s=im[(c*3+k)%im.length];const card=mk(col,'','',{position:'relative',width:'340px',height:'604px',borderRadius:'22px',overflow:'hidden',flex:'0 0 604px',boxShadow:'0 20px 50px rgba(0,0,0,.5)'});media(card,s,t0,t1);}}
 perFrame.push(t=>{cols.forEach((c,i)=>{c.style.transform=`translateY(${(((i%2?1:-1)*(t-t0)*60)%630-(i%2?630:0)).toFixed(1)}px)`;});});
 tl.fromTo(wall,{opacity:0,scale:1.15},{opacity:1,scale:1,duration:.6,ease:'power3.out'},ts);sfx(ts,'whoosh');
 mk(g,'','L',{background:'radial-gradient(ellipse 70% 55% at 50% 50%,rgba(0,0,0,0) 40%,rgba(0,0,0,.75) 100%)',pointerEvents:'none'});
 if(o.focus){const fa=o.focus.at||ts+1.2;tl.to(wall,{opacity:.22,filter:'blur(6px)',duration:.4},fa);
  const P0=phoneAt(g,540,900,1.5,o.focus.src||null,t0,t1);tl.fromTo(P0.w,{scale:.6,opacity:0,y:200},{scale:1.5,opacity:1,y:0,duration:.5,ease:'power3.out'},fa);sfx(fa,'pop');
  if(o.focus.pill){const pl=TX(g,540,900+405+50,o.focus.pill,'600 34px I',{padding:'14px 30px',borderRadius:'40px',background:'var(--panel)',border:'1px solid var(--line)'});blurIn(pl,fa+.35);}}
 return {g};}

/* ===================================================================
   11. scenePhoneFocus(t0,t1,{src, pill, pillAt, label, light})
   Satu HP besar sedikit miring 3D, sheen menyapu, pill di bawahnya (dekat, satu blok).
   =================================================================== */
function scenePhoneFocus(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const sc=1.55,Y=o.y||880;
 const P0=phoneAt(g,540,Y,sc,o.src||null,t0,t1);
 tl.fromTo(P0.w,{y:300,rotationX:-50,opacity:0},{y:0,rotationX:0,opacity:1,duration:.6,ease:'power3.out'},ts);sfx(ts,'whoosh');
 perFrame.push(t=>{P0.ph.flip.style.transform=`rotateY(${(-10+Math.sin((t-t0)*.7)*5).toFixed(2)}deg) rotateX(${(4+Math.cos((t-t0)*.5)*2).toFixed(2)}deg)`;});
 const tp=o.pillAt||ts+.8;tl.fromTo(P0.sheen,{x:'-160%'},{x:'360%',duration:.9,ease:'power2.inOut',immediateRender:false},tp);
 if(o.pill){const pl=TX(g,540,Y+270*sc+46,o.pill,'600 36px I',{padding:'16px 34px',borderRadius:'44px',background:'var(--panel)',border:'1px solid var(--line)'});blurIn(pl,tp);sfx(tp,'pop',.7);}
 if(o.label){const lb=TX(g,540,Y-270*sc-50,o.label,'italic 800 58px PF');blurIn(lb,ts+.2);}
 return {g,phone:P0};}

/* ===================================================================
   12. sceneTryFail(t0,t1,{prompt, typeAt, genAt, failAt, badge, src, light})
   Prompt mengetik, tombol Generate + progress, hasil glitch, lencana error merah.
   =================================================================== */
function sceneTryFail(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);
 const box=A(g,540,0,`<div class="pt" style="font:500 32px I;color:var(--ink);white-space:normal;line-height:1.3;min-height:84px"></div><div style="display:flex;justify-content:flex-end;margin-top:14px"><div class="gb" style="position:relative;overflow:hidden;height:56px;border-radius:28px;padding:0 30px;background:#fff;color:#111;font:700 26px I;display:flex;align-items:center;gap:10px">${icon('sparkle',24,'#111')}<span class="gl">Generate</span><div class="pb" style="position:absolute;left:0;bottom:0;height:5px;width:100%;background:${RED};transform-origin:0 50%;transform:scaleX(0)"></div></div></div>`,'',
  {width:'820px',padding:'26px 30px',borderRadius:'26px',background:'var(--panel)',border:'1.5px solid var(--line)',whiteSpace:'normal'});
 const res=A(g,540,0,'','',{width:'520px',height:'520px',borderRadius:'24px',overflow:'hidden',border:'1px solid var(--line)'});
 const rm=mk(res,'','',{position:'absolute',inset:'0'});media(rm,o.src||null,t0,t1);
 const sl=[0,1,2,3,4,5].map(i=>{const d=mk(res,'','',{position:'absolute',left:'0',right:'0',top:(i*87)+'px',height:'60px',background:'rgba(255,40,40,.35)',mixBlendMode:'screen',opacity:0});return d;});
 const bdg=A(g,540,0,`${icon('warning',34,'#fff')}<span>${o.badge||'GAGAL'}</span>`,'',{display:'flex',alignItems:'center',gap:'12px',padding:'14px 30px',borderRadius:'40px',background:'linear-gradient(180deg,#ff5a5a,#c80d16)',font:'800 34px I',color:'#fff',letterSpacing:'.04em',boxShadow:'0 0 24px rgba(255,30,30,.6),0 10px 24px rgba(0,0,0,.4)'});
 stack([box,res,bdg],o.y||930,[30,-30]);
 blurIn(box,ts,.35);sfx(ts,'pop');const te=typeInto(box.querySelector('.pt'),o.prompt||'',o.typeAt||ts+.3,.045);
 const tg=o.genAt||te+.3,tf=o.failAt||tg+1.2;sfx(tg,'click');tl.to(box.querySelector('.gb'),{scale:.92,duration:.07,yoyo:true,repeat:1},tg);
 perFrame.push(t=>{box.querySelector('.gl').textContent=t<tg?'Generate':t<tf?'Generating...':'Gagal';});
 tl.fromTo(box.querySelector('.pb'),{scaleX:0},{scaleX:.85,duration:tf-tg,ease:'power1.out',immediateRender:false},tg);
 tl.fromTo(res,{opacity:0,scale:.9},{opacity:1,scale:1,duration:.4,ease:'power3.out'},tg+.2);
 perFrame.push(t=>{const on=t>=tf&&t<tf+.7;const fr=Math.round(t*30);rm.style.transform=on?`translateX(${((fr*37)%23)-11}px)`:'';rm.style.filter=on?`hue-rotate(${(fr*53)%360}deg) contrast(1.6)`:(t>=tf?'grayscale(.8) brightness(.6)':'');
  sl.forEach((d,i)=>{d.style.opacity=on&&((fr+i*3)%4<2)?1:0;d.style.transform=`translateX(${on?(((fr*13+i*29)%60)-30):0}px)`;});});
 popIn(bdg,tf+.1,.4);shake(tf,12,.3);sfx(tf,'error');return {g};}

/* ===================================================================
   13. sceneCommentCTA(t0,t1,{word, label, typeAt, sendAt, link, linkAt, y, light})
   Kolom komentar mengetik kata CTA, tombol kirim ditekan, lalu tombol "klik link".
   =================================================================== */
function sceneCommentCTA(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);const word=o.word||'MAU';
 const lab=o.label?TX(g,540,0,o.label,'italic 800 64px PF'):null;
 const box=A(g,540,0,`<div style="width:64px;height:64px;border-radius:50%;flex:0 0 64px;background:linear-gradient(135deg,#ff7a7a,#7a5cff)"></div><span class="cw2" style="flex:1;font:600 40px I;color:#111"></span><div class="send" style="width:84px;height:84px;border-radius:50%;flex:0 0 84px;background:linear-gradient(180deg,#ff5a5a,#c80d16);display:flex;align-items:center;justify-content:center;box-shadow:0 0 20px rgba(255,30,30,.55)">${icon('paper-plane-tilt',40,'#fff')}</div>`,'',
  {width:'820px',height:'112px',borderRadius:'56px',background:'#fff',display:'flex',alignItems:'center',gap:'22px',padding:'0 14px 0 24px',boxShadow:'0 24px 60px rgba(0,0,0,.45)'});
 const lk=A(g,540,0,`${icon('link-simple',38,'#fff')}<span>${o.link||'Klik link di bio'}</span>`,'',{display:'flex',alignItems:'center',gap:'14px',padding:'22px 44px',borderRadius:'60px',background:'linear-gradient(180deg,#ff4545,#b80a14)',font:'800 40px I',color:'#fff',boxShadow:'0 0 34px rgba(255,30,30,.6),0 14px 30px rgba(0,0,0,.45)'});
 stack(lab?[lab,box,lk]:[box,lk],o.y||960,lab?[30,44]:[44]);
 if(lab)blurIn(lab,ts);blurIn(box,ts+.15,.35);sfx(ts+.15,'pop');
 const te=typeInto(box.querySelector('.cw2'),word,o.typeAt||ts+.5,.068,(o.sendAt||ts+1.6)+.05);
 const tsd=o.sendAt||Math.max(te+.3,ts+1.6);const sd=box.querySelector('.send');
 tl.to(sd,{scale:.84,duration:.08,yoyo:true,repeat:1},tsd);sfx(tsd,'click');
 const ring=A(g,540+820/2-14-42,parseFloat(box.style.top),'','',{width:'84px',height:'84px',borderRadius:'50%',border:'4px solid #fff'});tl.set(ring,{opacity:0},0);
 tl.fromTo(ring,{opacity:.9,scale:.5},{opacity:0,scale:2.4,duration:.5,ease:'power2.out',immediateRender:false},tsd);
 tl.to(box.querySelector('.cw2'),{y:-60,opacity:0,duration:.3,ease:'power2.in'},tsd+.05);sfx(tsd+.1,'ding',.7);
 const tl_=o.linkAt||tsd+.5;tl.fromTo(lk,{opacity:0,scale:1.4,filter:'blur(14px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:.35,ease:'power3.out'},tl_);sfx(tl_,'thud',.7);
 perFrame.push(t=>{if(t>tl_+.4)lk.style.translate=`0 ${(Math.sin((t-tl_)*4)*5).toFixed(1)}px`;});
 return {g,box,link:lk};}

/* ===================================================================
   14. sceneClosing(t0,t1,{src, label, word, line, green, small, light})
   Penutup: video latar blur + overlay gelap (atau latar terang), kata CTA raksasa, satu blok rapat di tengah.
   =================================================================== */
function sceneClosing(t0,t1,o={}){const {g,ts}=scn(t0,t1,o);
 if(!o.light){const bg=mk(g,'','L');const im=document.createElement('img');im.style.cssText='position:absolute;left:-60px;top:-60px;width:1200px;height:2040px;object-fit:cover;filter:blur(22px)';bg.appendChild(im);
  const s=o.src||{dir:MAIN,n:MAIN_FRAMES};VIDS.push({im,dir:s.dir,n:s.n,t0,t1,cur:-1});mk(bg,'','L',{background:'rgba(0,0,0,.8)'});
  perFrame.push(t=>{im.style.transform=`scale(${(1+(t-t0)*.02).toFixed(4)})`;});tl.fromTo(bg,{opacity:0},{opacity:1,duration:.4},t0);}
 const items=[];const add=(e,d)=>{items.push([e,d]);return e;};
 if(o.label)add(TX(g,540,0,o.label,'500 26px JB',{letterSpacing:'.18em',color:'var(--sub)'}),.0);
 const W_=add(TX(g,540,0,o.word||'MAU?','italic 900 170px PF',{color:'var(--red)',textShadow:'var(--glowR)',lineHeight:'1'}),.15);
 if(o.line)add(TX(g,540,0,o.line,'600 44px I'),.45);
 const dv=add(A(g,540,0,`<span style="width:120px;height:2px;background:var(--line);display:block"></span>${icon('arrow-down',30,'var(--ink)')}<span style="width:120px;height:2px;background:var(--line);display:block"></span>`,'',{display:'flex',alignItems:'center',gap:'18px'}),.65);
 if(o.green)add(TX(g,540,0,o.green,'italic 800 60px PF',{color:'var(--green)',textShadow:'var(--glowG)'}),.8);
 if(o.small)add(TX(g,540,0,o.small,'400 24px I',{color:'var(--sub)'}),.95);
 stack(items.map(x=>x[0]),o.y||955);items.forEach(([e,d])=>{if(e===W_){tl.fromTo(e,{opacity:0,scale:1.5,filter:'blur(22px) brightness(2.6)'},{opacity:1,scale:1,filter:'blur(0px) brightness(1)',duration:.36,ease:'power3.out'},ts+d);sfx(ts+d,'thud');}else blurIn(e,ts+d,.3);
  floaters.push([e,3,d*7]);});
 return {g};}
