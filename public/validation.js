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

  // Sunucu her zaman Türkçe döner. Tarayıcı, seçili dile göre kendi mesajını kullanır.
  var MESSAGES = {
    tr: {
      name: 'Adınızı 2 ile 80 karakter arasında yazın.',
      email: 'Geçerli bir e-posta adresi yazın. Örnek: ad@sirket.com',
      service: 'Listeden bir hizmet seçin.',
      message: 'Talebinizi 10 ile 1000 karakter arasında anlatın.',
    },
    en: {
      name: 'Enter your name, between 2 and 80 characters.',
      email: 'Enter a valid email address. Example: name@company.com',
      service: 'Choose a service from the list.',
      message: 'Describe your request in 10 to 1000 characters.',
    },
    de: {
      name: 'Geben Sie Ihren Namen mit 2 bis 80 Zeichen ein.',
      email: 'Geben Sie eine gültige E-Mail-Adresse ein. Beispiel: name@firma.de',
      service: 'Wählen Sie eine Leistung aus der Liste.',
      message: 'Beschreiben Sie Ihre Anfrage in 10 bis 1000 Zeichen.',
    },
  };

  function validate(input, lang) {
    var msg = MESSAGES[lang] || MESSAGES.tr;
    var src = input && typeof input === 'object' && !Array.isArray(input) ? input : {};
    var errors = {};
    var values = {};

    var name = typeof src.name === 'string' ? src.name.trim() : '';
    if (name.length < LIMITS.name.min || name.length > LIMITS.name.max || CONTROL_IN_LINE.test(name)) {
      errors.name = msg.name;
    }
    values.name = name;

    var email = typeof src.email === 'string' ? src.email.trim() : '';
    if (!email || email.length > LIMITS.email.max || !EMAIL_RE.test(email) || CONTROL_IN_LINE.test(email)) {
      errors.email = msg.email;
    }
    values.email = email;

    var service = typeof src.service === 'string' ? src.service : '';
    if (!Object.prototype.hasOwnProperty.call(SERVICES, service)) {
      errors.service = msg.service;
    }
    values.service = service;

    var message = typeof src.message === 'string' ? src.message.trim() : '';
    if (message.length < LIMITS.message.min || message.length > LIMITS.message.max || CONTROL_IN_TEXT.test(message)) {
      errors.message = msg.message;
    }
    values.message = message;

    return { values: values, errors: errors };
  }

  return { SERVICES: SERVICES, LIMITS: LIMITS, MESSAGES: MESSAGES, validate: validate };
});
