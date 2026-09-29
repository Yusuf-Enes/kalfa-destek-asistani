// Form kuralları tek yerde: tarayıcı bu dosyayı <script> ile, sunucu require ile kullanır.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Validation = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  var SERVICES = {
    'sss-botu': 'SSS botu',
    'e-posta-taslak': 'E-posta cevap taslakları',
    'canli-sohbet': 'Canlı sohbet asistanı',
  };

  var LIMITS = {
    name: { min: 2, max: 80 },
    email: { max: 254 },
    message: { min: 10, max: 1000 },
  };

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  // NUL karakteri Postgres'te hataya yol açar; satır sonu ve sekme dışındaki kontrol karakterlerini reddediyoruz.
  var CONTROL_IN_LINE = /[\u0000-\u001F\u007F]/;
  var CONTROL_IN_TEXT = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/;

  var MESSAGES = {
    name: 'Adınızı 2 ile 80 karakter arasında yazın.',
    email: 'Geçerli bir e-posta adresi yazın. Örnek: ad@sirket.com',
    service: 'Listeden bir hizmet seçin.',
    message: 'Talebinizi 10 ile 1000 karakter arasında anlatın.',
  };

  function validate(input) {
    var src = input && typeof input === 'object' && !Array.isArray(input) ? input : {};
    var errors = {};
    var values = {};

    var name = typeof src.name === 'string' ? src.name.trim() : '';
    if (name.length < LIMITS.name.min || name.length > LIMITS.name.max || CONTROL_IN_LINE.test(name)) {
      errors.name = MESSAGES.name;
    }
    values.name = name;

    var email = typeof src.email === 'string' ? src.email.trim() : '';
    if (!email || email.length > LIMITS.email.max || !EMAIL_RE.test(email) || CONTROL_IN_LINE.test(email)) {
      errors.email = MESSAGES.email;
    }
    values.email = email;

    var service = typeof src.service === 'string' ? src.service : '';
    if (!Object.prototype.hasOwnProperty.call(SERVICES, service)) {
      errors.service = MESSAGES.service;
    }
    values.service = service;

    var message = typeof src.message === 'string' ? src.message.trim() : '';
    if (message.length < LIMITS.message.min || message.length > LIMITS.message.max || CONTROL_IN_TEXT.test(message)) {
      errors.message = MESSAGES.message;
    }
    values.message = message;

    return { values: values, errors: errors };
  }

  return { SERVICES: SERVICES, LIMITS: LIMITS, validate: validate };
});
