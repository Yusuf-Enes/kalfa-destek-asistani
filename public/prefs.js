// Tema tercihi. <head> içinde çalışır ki sayfa ilk boyanmadan önce doğru tema uygulansın (koyu temada beyaz parlama olmasın).
// Sıra: kullanıcının kaydettiği seçim, yoksa işletim sisteminin tercihi. Seçim yalnızca düğmeye basılınca kaydedilir.
(function () {
  var root = document.documentElement;
  var KEY = 'kalfa-theme';
  var COLORS = { light: '#E6ECE8', dark: '#0E1A16' };

  function read() { try { return window.localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v) { try { window.localStorage.setItem(KEY, v); } catch (e) { /* tercih kaydedilemez, sorun değil */ } }

  var stored = read();
  var prefersDark = !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  var theme = stored === 'dark' || stored === 'light' ? stored : (prefersDark ? 'dark' : 'light');
  root.setAttribute('data-theme', theme);

  function sync() {
    var t = root.getAttribute('data-theme');
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', COLORS[t]);
    var btn = document.querySelector('.theme-toggle');
    if (btn) btn.setAttribute('aria-pressed', t === 'dark' ? 'true' : 'false');
  }

  window.KalfaTheme = {
    get: function () { return root.getAttribute('data-theme'); },
    set: function (t, persist) {
      root.setAttribute('data-theme', t);
      if (persist) write(t);
      sync();
      document.dispatchEvent(new CustomEvent('kalfa:theme', { detail: { theme: t } }));
    }
  };

  document.addEventListener('DOMContentLoaded', function () {
    sync();
    var btn = document.querySelector('.theme-toggle');
    if (btn) btn.addEventListener('click', function () {
      window.KalfaTheme.set(window.KalfaTheme.get() === 'dark' ? 'light' : 'dark', true);
    });
  });
})();
