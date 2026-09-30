// Hareket katmanı. <head> içinde çalışır ki başlangıç durumları ilk boyamadan önce hazır olsun.
// Kullanıcı "hareketi azalt" dediyse hiçbir şey animasyonlanmaz. Bir şey ters giderse sınıf kaldırılır ve sayfa hareketsiz, tam görünür kalır.
(function () {
  var root = document.documentElement;
  var reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  if (!reduced) root.classList.add('js-motion');

  function fallback() {
    root.classList.remove('js-motion');
    if (document.body) document.body.setAttribute('data-chat-done', '1');
    var bg = document.querySelector('.page-bg');
    if (bg) { bg.style.removeProperty('--p'); ['--c1', '--c2', '--c3', '--c4'].forEach(function (n) { bg.style.removeProperty(n); }); }
  }

  function sleep(ms) {
    return new Promise(function (resolve) { setTimeout(resolve, ms); });
  }

  function observeOnce(elements, options, onVisible) {
    if (!('IntersectionObserver' in window)) {
      elements.forEach(onVisible);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          io.unobserve(entry.target);
          onVisible(entry.target);
        }
      });
    }, options);
    elements.forEach(function (el) { io.observe(el); });
  }

  function markInView(el) { el.classList.add('in-view'); }

  // Bölümler görünür olunca bir kez oynar: başlıklar, metin blokları, iki sütun, hizmet satırları, adımlar.
  // Tetikleyici bir oran değil, öğenin üst kenarının ekranın alt %10'unun üstüne çıkmasıdır. Oran kullanılsaydı,
  // ekrandan uzun bir öğe (küçük telefon ya da büyütülmüş metin) hiçbir zaman "yeterince görünür" olmaz ve sonsuza kadar gizli kalırdı.
  var REVEAL_AT = { threshold: 0, rootMargin: '0px 0px -10% 0px' };
  function initReveals() {
    function all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
    observeOnce(all('.reveal-title'), REVEAL_AT, markInView);
    observeOnce(all('.rv'), REVEAL_AT, markInView);
    observeOnce(all('.split-grid, .services'), REVEAL_AT, markInView);
    var steps = document.getElementById('steps');
    if (steps) observeOnce([steps], REVEAL_AT, markInView);
  }

  // Her konunun leke tonları: [leke1, leke2, leke3, leke4] = [r, g, b, alfa]. Sıra sayfadaki bölüm sırasıdır:
  // hero (nane), statement (sönük gri-yeşil), kim neye bakar (canlı zümrüt-yeşil), nasıl çalışır (yumuşak nane-yeşil), hizmetler (taze yeşil), form. Hepsi yalnızca yeşil ailesindedir (sarı ve mavi yok) ve
  // ilk paletteki renklerden daha koyu değildir, bu yüzden metin kontrastı bozulmaz.
  var BLOB_PALETTES = [
    [[143, 222, 183, 0.6], [168, 230, 204, 0.65], [189, 236, 209, 0.7], [106, 212, 164, 0.5]],
    [[179, 214, 191, 0.6], [195, 223, 207, 0.65], [210, 231, 215, 0.7], [157, 202, 174, 0.5]],
    [[77, 230, 179, 0.6], [125, 236, 208, 0.65], [162, 242, 210, 0.7], [32, 223, 169, 0.5]],
    [[161, 217, 203, 0.6], [184, 226, 216, 0.65], [200, 233, 222, 0.7], [135, 206, 188, 0.5]],
    [[111, 228, 160, 0.6], [149, 235, 192, 0.65], [174, 240, 197, 0.7], [60, 218, 133, 0.5]],
    [[143, 222, 183, 0.6], [168, 230, 204, 0.65], [189, 236, 209, 0.7], [106, 212, 164, 0.5]]
  ];
  // Koyu tema: aynı yeşil tonlar, ama arka planla karışınca en parlak nokta bile metin kontrastını bozmayacak kadar koyu.
  var BLOB_PALETTES_DARK = [
    [[22, 74, 50, 0.6], [21, 71, 52, 0.65], [20, 68, 42, 0.7], [25, 85, 60, 0.5]],
    [[39, 73, 50, 0.6], [37, 69, 50, 0.65], [36, 66, 44, 0.7], [44, 82, 59, 0.5]],
    [[11, 75, 54, 0.6], [10, 71, 56, 0.65], [10, 68, 45, 0.7], [12, 86, 65, 0.5]],
    [[30, 72, 62, 0.6], [28, 70, 59, 0.65], [27, 67, 54, 0.7], [34, 83, 70, 0.5]],
    [[15, 77, 41, 0.6], [14, 72, 43, 0.65], [13, 70, 33, 0.7], [16, 86, 49, 0.5]],
    [[22, 74, 50, 0.6], [21, 71, 52, 0.65], [20, 68, 42, 0.7], [25, 85, 60, 0.5]]
  ];
  function smooth(t) { return t * t * (3 - 2 * t); }
  function mixPalettes(a, b, t) {
    return a.map(function (blob, i) {
      return blob.map(function (v, k) { return v + (b[i][k] - v) * t; });
    });
  }
  function paletteStr(blob) {
    return 'rgba(' + Math.round(blob[0]) + ',' + Math.round(blob[1]) + ',' + Math.round(blob[2]) + ',' + blob[3].toFixed(3) + ')';
  }

  // Üstte kaydırma çizgisi, başlığa gölge, zemindeki lekelerin kaydırmaya bağlı hareketi (--p) ve
  // konu değişince leke tonlarının sürekli ve yumuşak kayması. Ekranın ortasındaki konu esas alınır.
  function initScroll() {
    var header = document.querySelector('.site-header');
    var bar = document.querySelector('.progress');
    var bg = document.querySelector('.page-bg');
    var topics = Array.prototype.slice.call(document.querySelectorAll('main > section'));
    var ticking = false;
    function updateTones() {
      if (!bg || !topics.length) return;
      var PAL = document.documentElement.getAttribute('data-theme') === 'dark' ? BLOB_PALETTES_DARK : BLOB_PALETTES;
      var mid = window.innerHeight * 0.5;
      var centers = topics.map(function (el) { var r = el.getBoundingClientRect(); return r.top + r.height / 2; });
      var k = 0;
      while (k < centers.length - 1 && centers[k + 1] <= mid) k++;
      var pal;
      if (mid <= centers[0]) pal = PAL[0];
      else if (k >= centers.length - 1) pal = PAL[Math.min(centers.length - 1, PAL.length - 1)];
      else pal = mixPalettes(PAL[k], PAL[k + 1], smooth((mid - centers[k]) / (centers[k + 1] - centers[k])));
      for (var i = 0; i < 4; i++) bg.style.setProperty('--c' + (i + 1), paletteStr(pal[i]));
    }
    function update() {
      ticking = false;
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      if (header) header.classList.toggle('is-scrolled', window.scrollY > 8);
      if (reduced) return;
      if (bar) bar.style.setProperty('--p', p.toFixed(4));
      if (bg) bg.style.setProperty('--p', p.toFixed(4));
      updateTones();
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } });
    document.addEventListener('kalfa:theme', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } });
    update();
  }

  // Konuşma: satırlar sırayla belirir.
  // Son satır iş fişidir: düşer, ardından mühür basılır. Mesajlar peşpeşe gelir, toplam yaklaşık 3,5 saniye.
  function initChat() {
    var log = document.querySelector('.chat-log');
    if (!log) return;
    if (reduced) { document.body.setAttribute('data-chat-done', '1'); return; }

    var msgs = Array.prototype.slice.call(log.children);
    // [önce bekle (ms), satır]. Mesajlar peşpeşe gelir, arada bekleme göstergesi yoktur.
    var script = [
      [450, msgs[0]],
      [520, msgs[1]],
      [520, msgs[2]],
      [520, msgs[3]],
      [520, msgs[4]],
    ];

    function play() {
      var chain = Promise.resolve();
      script.forEach(function (step) {
        chain = chain.then(function () { return sleep(step[0]); }).then(function () {
          step[1].classList.add('show');
        });
      });
      return chain.then(function () { return sleep(350); }).then(function () {
        msgs[msgs.length - 1].classList.add('stamped');
        return sleep(250);
      }).then(function () {
        document.body.setAttribute('data-chat-done', '1');
      });
    }

    var started = false;
    function start() {
      if (started) return;
      started = true;
      play().catch(fallback);
    }
    // Üst kenar ekrana girince başlar (kart ekrandan uzun olsa bile). Oran eşiği kullanılsaydı uzun kartta hiç başlamazdı.
    observeOnce([log], REVEAL_AT, start);
  }

  document.addEventListener('DOMContentLoaded', function () {
    try {
      initReveals();
      initScroll();
      initChat();
    } catch (e) {
      fallback();
    }
  });
})();
