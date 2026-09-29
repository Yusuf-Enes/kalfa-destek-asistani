(function () {
  var form = document.getElementById('request-form');
  var submitBtn = document.getElementById('submit-btn');
  var alertBox = document.getElementById('form-alert');
  var success = document.getElementById('success');
  var successId = document.getElementById('success-id');
  var counter = document.getElementById('message-count');
  var meter = document.getElementById('message-meter');
  var newRequestBtn = document.getElementById('new-request');
  var FIELDS = ['name', 'email', 'service', 'message'];
  var TIMEOUT_MS = 15000;
  var sending = false;

  // Seçili dil ve çeviri (i18n.js yüklenmediyse Türkçe varsayılan)
  function lang() { return window.I18N ? window.I18N.lang : 'tr'; }
  function t(key) { return window.I18N ? window.I18N.t(key) : key; }
  var alertKey = null; // görünen genel uyarının çeviri anahtarı, dil değişince yeniden yazılır

  function field(name) { return document.getElementById(name); }
  function errorBox(name) { return document.getElementById(name + '-error'); }

  function showError(name, text) {
    var input = field(name);
    var box = errorBox(name);
    input.setAttribute('aria-invalid', 'true');
    box.textContent = text;
    box.hidden = false;
  }

  function clearError(name) {
    field(name).removeAttribute('aria-invalid');
    errorBox(name).hidden = true;
    errorBox(name).textContent = '';
  }

  function clearAll() {
    FIELDS.forEach(clearError);
    hideAlert();
  }

  function showAlert(key) {
    alertKey = key;
    alertBox.textContent = t(key);
    alertBox.hidden = false;
  }

  function hideAlert() {
    alertKey = null;
    alertBox.hidden = true;
    alertBox.textContent = '';
  }

  function currentValues() {
    var v = {};
    FIELDS.forEach(function (n) { v[n] = field(n).value; });
    return v;
  }

  function applyErrors(errors) {
    var first = null;
    FIELDS.forEach(function (n) {
      if (errors[n]) {
        showError(n, errors[n]);
        if (!first) first = n;
      }
    });
    if (first) field(first).focus();
    return first !== null;
  }

  function setSending(on) {
    sending = on;
    submitBtn.disabled = on;
    submitBtn.textContent = on ? t('js.sending') : t('f.submit');
    submitBtn.classList.toggle('is-sending', on);
    form.setAttribute('aria-busy', on ? 'true' : 'false');
  }

  function updateCounter() {
    var n = field('message').value.length;
    counter.textContent = String(n);
    // İlerleme çizgisi, en az uzunluk hedefine doğru dolar ve hedefe ulaşınca yeşile döner.
    var goal = Validation.LIMITS.message.min;
    meter.style.setProperty('--fill', Math.min(n / goal, 1).toFixed(3));
    meter.classList.toggle('ok', n >= goal);
  }

  // Alan bırakıldığında ya da hatalı alan düzeltilirken o alanı yeniden denetle.
  FIELDS.forEach(function (n) {
    var input = field(n);
    function check() {
      var res = Validation.validate(currentValues(), lang());
      if (res.errors[n]) showError(n, res.errors[n]);
      else clearError(n);
    }
    input.addEventListener('blur', function () {
      if (input.value !== '' || input.hasAttribute('aria-invalid')) check();
    });
    input.addEventListener('input', function () {
      if (input.hasAttribute('aria-invalid')) check();
      if (n === 'message') updateCounter();
    });
    if (n === 'service') input.addEventListener('change', check);
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (sending) return;
    clearAll();

    var result = Validation.validate(currentValues(), lang());
    if (applyErrors(result.errors)) return;

    setSending(true);
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, TIMEOUT_MS);

    fetch('/api/requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result.values),
      signal: controller.signal,
    })
      .then(function (res) {
        return res.json().catch(function () { return null; }).then(function (body) {
          return { status: res.status, body: body };
        });
      })
      .then(function (r) {
        // Başarı yalnızca sunucu kaydı oluşturduğunu (201 + id) söylediğinde gösterilir.
        if (r.status === 201 && r.body && r.body.id) {
          successId.textContent = '#' + r.body.id;
          form.hidden = true;
          success.hidden = false;
          success.focus();
          return;
        }
        if (r.status === 400 && r.body && r.body.errors) {
          // Sunucu alan adlarını Türkçe mesajla döner. Tarayıcı, seçili dilde kendi mesajını gösterir.
          var texts = Validation.MESSAGES[lang()] || Validation.MESSAGES.tr;
          var shown = {};
          Object.keys(r.body.errors).forEach(function (n) { shown[n] = texts[n] || r.body.errors[n]; });
          applyErrors(shown);
          showAlert('js.fixFields');
          return;
        }
        showAlert(r.status === 429 ? 'js.rate' : 'js.saveFailed');
      })
      .catch(function (err) {
        showAlert(err && err.name === 'AbortError' ? 'js.timeout' : 'js.network');
      })
      .then(function () {
        clearTimeout(timer);
        setSending(false);
      });
  });

  newRequestBtn.addEventListener('click', function () {
    form.reset();
    clearAll();
    updateCounter();
    success.hidden = true;
    form.hidden = false;
    field('name').focus();
  });

  // Dil değişince görünen hata mesajlarını ve genel uyarıyı yeni dilde yeniden yaz.
  document.addEventListener('kalfa:lang', function () {
    var errs = Validation.validate(currentValues(), lang()).errors;
    FIELDS.forEach(function (n) {
      if (field(n).hasAttribute('aria-invalid') && errs[n]) errorBox(n).textContent = errs[n];
    });
    if (alertKey) alertBox.textContent = t(alertKey);
    if (sending) submitBtn.textContent = t('js.sending');
  });

  updateCounter();
})();
