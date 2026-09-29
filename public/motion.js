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

  // Adımların çizgisi, bölüm görünür olunca bir kez çizilir.
  function initSteps() {
    var steps = document.getElementById('steps');
    if (steps) observeOnce([steps], { threshold: 0.4 }, function (el) { el.classList.add('in-view'); });
  }

  // Konuşma: müşteri satırı belirir, Kalfa önce "yazıyor" noktalarını gösterir, sonra cevabı açılır.
  function initChat() {
    var log = document.querySelector('.chat-log');
    if (!log) return;
    if (reduced) { document.body.setAttribute('data-chat-done', '1'); return; }

    var msgs = Array.prototype.slice.call(log.children);
    // [önce bekle (ms), yazıyor süresi (ms), satır]. İlk bekleme, başlığın gelmesine zaman tanır.
    var script = [
      [900, 0, msgs[0]],
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
      // Son satır iş fişidir: düşer, ardından mühür basılır.
      return chain.then(function () { return sleep(550); }).then(function () {
        msgs[msgs.length - 1].classList.add('stamped');
        return sleep(400);
      }).then(function () { document.body.setAttribute('data-chat-done', '1'); });
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
      initSteps();
      initChat();
    } catch (e) {
      fallback();
    }
  });
})();
