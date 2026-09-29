// Hareket katmanı. <head> içinde çalışır ki başlangıç durumları ilk boyamadan önce hazır olsun.
// Kullanıcı "hareketi azalt" dediyse hiçbir şey animasyonlanmaz. Bir şey ters giderse sınıf kaldırılır ve sayfa hareketsiz, tam görünür kalır.
(function () {
  var root = document.documentElement;
  var reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  if (!reduced) root.classList.add('js-motion');

  function fallback() {
    root.classList.remove('js-motion');
    if (document.body) document.body.setAttribute('data-chat-done', '1');
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

  function initTicker() {
    var ticker = document.getElementById('ticker');
    var toggle = document.getElementById('ticker-toggle');
    if (!ticker || !toggle || reduced) return;
    toggle.hidden = false;
    toggle.addEventListener('click', function () {
      var paused = ticker.classList.toggle('is-paused');
      toggle.setAttribute('aria-pressed', paused ? 'true' : 'false');
      toggle.textContent = paused ? 'Akışı başlat' : 'Akışı durdur';
    });
  }

  function initReveals() {
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
    observeOnce(items, { threshold: 0.15 }, function (el) { el.classList.add('is-visible'); });
    var steps = document.getElementById('steps');
    if (steps) observeOnce([steps], { threshold: 0.4 }, function (el) { el.classList.add('in-view'); });
  }

  function initProgress() {
    var bar = document.querySelector('.progress');
    if (!bar || reduced) return;
    var ticking = false;
    function update() {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      bar.style.setProperty('--p', p.toFixed(4));
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  // Konuşma: müşteri mesajı belirir, asistan önce "yazıyor" noktalarını gösterir, sonra cevabı açılır.
  function initChat() {
    var log = document.querySelector('.chat-log');
    if (!log) return;
    if (reduced) { document.body.setAttribute('data-chat-done', '1'); return; }

    var msgs = Array.prototype.slice.call(log.children);
    // [önce bekle (ms), yazıyor süresi (ms), mesaj]
    var script = [
      [500, 0, msgs[0]],
      [900, 1200, msgs[1]],
      [1300, 0, msgs[2]],
      [900, 1500, msgs[3]],
      [700, 0, msgs[4]],
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
      return chain.then(function () { document.body.setAttribute('data-chat-done', '1'); });
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
      initTicker();
      initReveals();
      initProgress();
      initChat();
    } catch (e) {
      fallback();
    }
  });
})();
