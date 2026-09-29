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
    if (bg) bg.style.removeProperty('--p');
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
  function initReveals() {
    function all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
    observeOnce(all('.reveal-title'), { threshold: 0.4 }, markInView);
    observeOnce(all('.rv'), { threshold: 0.2 }, markInView);
    observeOnce(all('.split-grid, .services'), { threshold: 0.15 }, markInView);
    var steps = document.getElementById('steps');
    if (steps) observeOnce([steps], { threshold: 0.4 }, markInView);
  }

  // Üstte kaydırma çizgisi, başlığa gölge ve zemindeki lekelerin kaydırmaya bağlı hareketi (--p).
  function initScroll() {
    var header = document.querySelector('.site-header');
    var bar = document.querySelector('.progress');
    var bg = document.querySelector('.page-bg');
    var ticking = false;
    function update() {
      ticking = false;
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      if (header) header.classList.toggle('is-scrolled', window.scrollY > 8);
      if (reduced) return;
      if (bar) bar.style.setProperty('--p', p.toFixed(4));
      if (bg) bg.style.setProperty('--p', p.toFixed(4));
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } });
    update();
  }

  // Konuşma: müşteri satırı belirir, Kalfa önce "yazıyor" noktalarını gösterir, sonra cevabı açılır.
  // Son satır iş fişidir: düşer, ardından mühür basılır. Konuşma hızlıdır, toplam yaklaşık 4 saniye.
  function initChat() {
    var log = document.querySelector('.chat-log');
    if (!log) return;
    if (reduced) { document.body.setAttribute('data-chat-done', '1'); return; }

    var msgs = Array.prototype.slice.call(log.children);
    // [önce bekle (ms), yazıyor süresi (ms), satır]
    var script = [
      [500, 0, msgs[0]],
      [350, 650, msgs[1]],
      [500, 0, msgs[2]],
      [350, 800, msgs[3]],
      [300, 0, msgs[4]],
    ];

    function play() {
      var chain = Promise.resolve();
      script.forEach(function (step) {
        chain = chain.then(function () { return sleep(step[0]); }).then(function () {
          var el = step[2];
          if (step[1] > 0) {
            el.classList.add('typing', 'show');
            return sleep(step[1]).then(function () { el.classList.remove('typing'); });
          }
          el.classList.add('show');
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
    observeOnce([log], { threshold: 0.35 }, start);
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
