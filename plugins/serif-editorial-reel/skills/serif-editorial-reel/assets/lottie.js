/* Pembungkus lottie-web supaya deterministik di pipeline render per frame.
 *
 * Dipakai hanya untuk gerakan abstrak (garis, partikel halus, pulse) atau file
 * Lottie milik user sendiri. Lottie kartun melanggar aturan gaya skill ini.
 * Untuk hampir semua kebutuhan, GSAP lebih tepat karena lebih mudah dikunci ke waktu kata.
 *
 * Pasang: npm i lottie-web
 *         cp node_modules/lottie-web/build/player/lottie.min.js build/
 *         <script src="lottie.min.js"></script>  sebelum script utama
 *
 * Pakai di dalam halaman:
 *   const L = await lottieLayer(parent, 'anim/garis.json', {width:420, height:420, fps:30});
 *   L.play(12.4, 1.0);            // mulai detik 12.4, kecepatan 1x
 *   L.tint('#36f281');            // warnai ulang semua fill dan stroke
 *
 * Verifikasi: goToAndStop(frame, true) menghasilkan piksel identik untuk frame
 * yang sama, jadi aman untuk render dua separuh paralel.
 */
async function lottieLayer(parent, src, opt = {}) {
  const { width = 400, height = 400, fps = 30, loop = false } = opt;
  const host = document.createElement('div');
  host.style.cssText = `position:absolute;width:${width}px;height:${height}px;pointer-events:none`;
  parent.appendChild(host);

  const data = await (await fetch(src)).json();
  const anim = lottie.loadAnimation({
    container: host, renderer: 'svg', loop: false, autoplay: false, animationData: data
  });
  await new Promise(r => anim.addEventListener('DOMLoaded', r));

  const total = anim.totalFrames;
  const srcFps = (data.fr || 30);
  let t0 = null, rate = 1;

  const api = {
    el: host,
    totalFrames: total,
    durasi: total / srcFps,
    play(startSec, speed = 1) { t0 = startSec; rate = speed; return api; },
    tint(color) {
      host.querySelectorAll('path,rect,circle,ellipse,polygon,g').forEach(n => {
        if (n.getAttribute('fill') && n.getAttribute('fill') !== 'none') n.setAttribute('fill', color);
        if (n.getAttribute('stroke') && n.getAttribute('stroke') !== 'none') n.setAttribute('stroke', color);
      });
      return api;
    },
    at(x, y) { host.style.left = (x - width / 2) + 'px'; host.style.top = (y - height / 2) + 'px'; return api; },
    // dipanggil dari perFrame di template
    tick(t) {
      if (t0 === null) { host.style.opacity = 0; return; }
      const f = (t - t0) * srcFps * rate;
      if (f < 0) { host.style.opacity = 0; return; }
      host.style.opacity = 1;
      let ff = loop ? ((f % total) + total) % total : Math.min(f, total - 1);
      anim.goToAndStop(ff, true);
    }
  };
  host.style.opacity = 0;
  return api;
}

/* Di template:
 *   const L = await lottieLayer(ov, 'anim/pulse.json', {width:520,height:520});
 *   L.at(540, 1100).tint('#36f281').play(T(31.4));
 *   perFrame.push(t => L.tick(t));
 */
