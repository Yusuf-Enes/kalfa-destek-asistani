(function () {
  var form = document.getElementById('request-form');
  var submitBtn = document.getElementById('submit-btn');
  var alertBox = document.getElementById('form-alert');
  var success = document.getElementById('success');
  var successId = document.getElementById('success-id');
  var counter = document.getElementById('message-count');
  var newRequestBtn = document.getElementById('new-request');
  var FIELDS = ['name', 'email', 'service', 'message'];
  var SEND_LABEL = 'Talebi gönder';
  var TIMEOUT_MS = 15000;
  var sending = false;

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

  function showAlert(text) {
    alertBox.textContent = text;
    alertBox.hidden = false;
  }

  function hideAlert() {
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
    submitBtn.textContent = on ? 'Gönderiliyor…' : SEND_LABEL;
    form.setAttribute('aria-busy', on ? 'true' : 'false');
  }

  function updateCounter() {
    counter.textContent = String(field('message').value.length);
  }

  // Alan bırakıldığında ya da hatalı alan düzeltilirken o alanı yeniden denetle.
  FIELDS.forEach(function (n) {
    var input = field(n);
    function check() {
      var res = Validation.validate(currentValues());
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

    var result = Validation.validate(currentValues());
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
          applyErrors(r.body.errors);
          showAlert('Bazı alanları düzeltmeniz gerekiyor.');
          return;
        }
        var message = r.body && r.body.error ? r.body.error : 'Talebiniz kaydedilemedi. Lütfen biraz sonra tekrar deneyin.';
        showAlert(message);
      })
      .catch(function (err) {
        showAlert(err && err.name === 'AbortError'
          ? 'Sunucu zamanında yanıt vermedi. Talebiniz kaydedilmedi, tekrar deneyin.'
          : 'Sunucuya ulaşılamadı. Bağlantınızı kontrol edip tekrar deneyin. Talebiniz kaydedilmedi.');
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

  updateCounter();
})();
