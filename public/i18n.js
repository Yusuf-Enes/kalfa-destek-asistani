// Çok dillilik (Türkçe, İngilizce, Almanca).
// Türkçe metin HTML'in içindedir (JavaScript'siz de okunur, arama motorları da onu görür). Bu dosya İngilizce ve Almanca
// çevirileri taşır, sayfadaki data-i18n işaretli öğeleri değiştirir. Türkçeye dönüşte HTML'deki özgün metin geri yüklenir.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.I18N = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  var DICT = {
    tr: {
  "js.sending": "Gönderiliyor…",
  "js.fixFields": "Bazı alanları düzeltmeniz gerekiyor.",
  "js.saveFailed": "Talebiniz kaydedilemedi. Lütfen biraz sonra tekrar deneyin.",
  "js.rate": "Çok fazla deneme yaptınız. Bir dakika sonra tekrar deneyin.",
  "js.timeout": "Sunucu zamanında yanıt vermedi. Talebiniz kaydedilmiş olabilir. Aynı talebi tekrar göndermek güvenlidir, iki kez kaydedilmez.",
  "js.network": "Sunucuya ulaşılamadı. Bağlantınızı kontrol edin. Talebiniz kaydedilmiş olabilir, aynı talebi tekrar göndermek güvenlidir.",
  "f.submit": "Talebi gönder"
},
    en: {
  "meta.title": "Kalfa · Customer support assistant",
  "meta.desc": "Kalfa answers your business's frequently asked customer questions and hands anything that needs approval or care to you, the master, with a summary. A fictional service page.",
  "skip": "Skip to the request form",
  "brand.aria": "Kalfa home",
  "nav.aria": "Page sections",
  "nav.kim": "Who handles what",
  "nav.nasil": "How it works",
  "nav.hizmet": "Services",
  "tools.lang": "Language",
  "tools.theme": "Dark theme",
  "cta.request": "Make a request",
  "hero.h1": "Kalfa handles it, the master decides.",
  "hero.lead": "Kalfa answers the questions your customers ask most. Anything that needs approval or care is handed to you, the master, together with a summary.",
  "hero.link": "See how a job reaches the master",
  "hero.fine": "This is a fictional service. Do not enter real personal information in the form.",
  "chat.aria": "Sample customer conversation and the job slip handed to the master",
  "chat.caption": "Sample conversation",
  "chat.customer": "Customer",
  "chat.m1": "When will my order arrive? Order no: 4821",
  "chat.m2": "Your order 4821 shipped yesterday. Estimated delivery is Thursday. I sent the tracking code to your email.",
  "chat.m3": "I changed my mind about another item, I'd like to return it.",
  "chat.m4": "I've received your return request. We will get back to you as soon as possible.",
  "slip.title": "Note for the master",
  "slip.topic": "Subject",
  "slip.topic.v": "Return request",
  "slip.order": "Order",
  "slip.summary": "Kalfa's summary",
  "slip.summary.v": "Customer changed their mind, item unopened. Awaiting your approval.",
  "slip.stamp": "Handed to the master",
  "st.title": "The phone never stops while the shop is open.",
  "st.p1": "Where is my order, how do returns work, how late are you open. Answering the same question every day means leaving your work. A complicated customer question also gets lost in the queue.",
  "st.p2": "Kalfa takes care of the repeating questions. You only deal with the jobs that need your decision.",
  "sp.title": "Who handles what",
  "sp.kalfa": "Goes to Kalfa",
  "sp.k1": "Shipping and delivery status",
  "sp.k2": "Opening hours and address",
  "sp.k3": "How returns and exchanges work",
  "sp.k4": "Product and price information, from the answers you wrote",
  "sp.usta": "Goes to the master",
  "sp.u1": "Approval of returns and refunds",
  "sp.u2": "Complaints and dissatisfaction",
  "sp.u3": "Special price and discount requests",
  "sp.u4": "Any question Kalfa cannot answer",
  "sp.note": "Every job that goes to the master arrives as a job slip with a summary of the conversation. The customer is not asked the same questions again.",
  "how.title": "How a job runs",
  "how.intro": "Setup is done once. After that, Kalfa stands at the counter while the shop is open.",
  "how.s1t": "Fill in your notebook",
  "how.s1p": "You write down your frequent questions and answers once.",
  "how.s2t": "Kalfa looks after the customer",
  "how.s2p": "It understands the question and replies in the customer's own words.",
  "how.s3t": "Hard jobs go to the master",
  "how.s3p": "Approvals for returns or complaints are left to you, together with a summary of the conversation.",
  "sv.title": "Put Kalfa to work in three places",
  "sv.1t": "FAQ bot",
  "sv.1d": "On your FAQ page, it matches the customer's own sentence to the right answer.",
  "sv.2t": "Email reply drafts",
  "sv.2d": "Writes a ready draft for emails in your inbox. You read and edit it before sending.",
  "sv.3t": "Live chat assistant",
  "sv.3d": "Talks with customers in the chat box on your site and hands the job to the master, meaning you, when needed.",
  "f.title": "Make a request",
  "f.intro": "Briefly describe your business and what you need. Once your request is saved, we give you a request number.",
  "f.fine": "This is an evaluation exercise. Enter fictional test data only.",
  "f.name": "Your name",
  "f.email": "Email",
  "f.service": "Service",
  "f.opt0": "Choose a service",
  "f.message": "What would you like to do?",
  "f.hint": "/ 1000 characters. Write at least 10 characters.",
  "f.submit": "Send request",
  "ok.title": "Your request has been saved",
  "ok.number": "Your request number:",
  "ok.note": "Make a note of this number. The record was written to the server.",
  "ok.new": "Make a new request",
  "ft.note": "Kalfa is a fictional service and was prepared only for this evaluation.",
  "js.sending": "Sending…",
  "js.fixFields": "Some fields need to be corrected.",
  "js.saveFailed": "Your request could not be saved. Please try again in a moment.",
  "js.rate": "Too many attempts. Try again in a minute.",
  "js.timeout": "The server did not respond in time. Your request may have been saved. Sending the same request again is safe, it will not be saved twice.",
  "js.network": "Could not reach the server. Check your connection. Your request may have been saved, and sending the same request again is safe.",
    "nf.title": "This page could not be found.",
    "nf.text": "The address you are looking for does not exist or may have moved. You can continue from the home page.",
    "nf.home": "Back to the home page"
},
    de: {
  "meta.title": "Kalfa · Kundensupport-Assistent",
  "meta.desc": "Kalfa beantwortet die häufigsten Kundenfragen Ihres Betriebs und übergibt alles, was Ihre Freigabe oder besondere Sorgfalt braucht, samt Zusammenfassung an Sie, den Meister. Eine fiktive Dienstleistungsseite.",
  "skip": "Zum Anfrageformular springen",
  "brand.aria": "Kalfa Startseite",
  "nav.aria": "Abschnitte der Seite",
  "nav.kim": "Wer macht was",
  "nav.nasil": "So funktioniert es",
  "nav.hizmet": "Leistungen",
  "tools.lang": "Sprache",
  "tools.theme": "Dunkles Design",
  "cta.request": "Anfrage stellen",
  "hero.h1": "Kalfa kümmert sich, der Meister entscheidet.",
  "hero.lead": "Kalfa beantwortet die Fragen, die Ihre Kunden am häufigsten stellen. Was Ihre Freigabe oder besondere Sorgfalt braucht, geht mit einer Zusammenfassung an Sie, den Meister.",
  "hero.link": "Sehen Sie, wie ein Auftrag beim Meister ankommt",
  "hero.fine": "Dies ist eine fiktive Dienstleistung. Geben Sie im Formular keine echten persönlichen Daten ein.",
  "chat.aria": "Beispielgespräch mit einem Kunden und der an den Meister übergebene Auftragszettel",
  "chat.caption": "Beispielgespräch",
  "chat.customer": "Kunde",
  "chat.m1": "Wann kommt meine Bestellung an? Bestellnr.: 4821",
  "chat.m2": "Ihre Bestellung 4821 wurde gestern versandt. Voraussichtliche Lieferung am Donnerstag. Den Sendungscode habe ich Ihnen per E-Mail geschickt.",
  "chat.m3": "Ich habe mich bei einem anderen Artikel umentschieden und möchte ihn zurückgeben.",
  "chat.m4": "Ich habe Ihre Rückgabeanfrage erhalten. Wir melden uns so schnell wie möglich bei Ihnen.",
  "slip.title": "Notiz an den Meister",
  "slip.topic": "Betreff",
  "slip.topic.v": "Rückgabeanfrage",
  "slip.order": "Bestellung",
  "slip.summary": "Zusammenfassung von Kalfa",
  "slip.summary.v": "Kunde hat sich umentschieden, Artikel ungeöffnet. Ihre Freigabe steht aus.",
  "slip.stamp": "An den Meister übergeben",
  "st.title": "Solange der Laden offen ist, steht das Telefon nie still.",
  "st.p1": "Wo ist meine Bestellung, wie funktioniert die Rückgabe, wie lange haben Sie geöffnet. Jeden Tag dieselbe Frage zu beantworten heißt, die eigentliche Arbeit liegen zu lassen. Eine komplizierte Kundenfrage geht dabei auch noch in der Schlange unter.",
  "st.p2": "Kalfa kümmert sich um die wiederkehrenden Fragen. Sie befassen sich nur mit den Aufträgen, die Ihre Entscheidung brauchen.",
  "sp.title": "Wer macht was",
  "sp.kalfa": "Geht an Kalfa",
  "sp.k1": "Versand- und Lieferstatus",
  "sp.k2": "Öffnungszeiten und Adresse",
  "sp.k3": "Wie Rückgabe und Umtausch funktionieren",
  "sp.k4": "Produkt- und Preisinformationen, aus Ihren eigenen Antworten",
  "sp.usta": "Geht an den Meister",
  "sp.u1": "Freigabe von Rückgaben und Erstattungen",
  "sp.u2": "Beschwerden und Unzufriedenheit",
  "sp.u3": "Sonderpreise und Rabattwünsche",
  "sp.u4": "Jede Frage, die Kalfa nicht beantworten kann",
  "sp.note": "Jeder Auftrag, der zum Meister geht, kommt als Auftragszettel mit einer Zusammenfassung des Gesprächs an. Dem Kunden werden dieselben Fragen nicht noch einmal gestellt.",
  "how.title": "So läuft ein Auftrag",
  "how.intro": "Die Einrichtung erfolgt einmal. Danach steht Kalfa bei geöffnetem Laden an der Theke.",
  "how.s1t": "Füllen Sie Ihr Notizbuch",
  "how.s1p": "Sie schreiben Ihre häufigen Fragen und Antworten einmal auf.",
  "how.s2t": "Kalfa kümmert sich um den Kunden",
  "how.s2p": "Es versteht die Frage und antwortet in den Worten des Kunden.",
  "how.s3t": "Schwierige Aufträge gehen an den Meister",
  "how.s3p": "Freigaben für Rückgaben oder Beschwerden überlässt es Ihnen, zusammen mit einer Zusammenfassung des Gesprächs.",
  "sv.title": "Kalfa an drei Stellen einsetzen",
  "sv.1t": "FAQ-Bot",
  "sv.1d": "Auf Ihrer FAQ-Seite ordnet er den Satz des Kunden der passenden Antwort zu.",
  "sv.2t": "E-Mail-Antwortentwürfe",
  "sv.2d": "Schreibt für E-Mails in Ihrem Posteingang einen fertigen Entwurf. Sie lesen und korrigieren ihn vor dem Senden.",
  "sv.3t": "Live-Chat-Assistent",
  "sv.3d": "Spricht im Chatfenster Ihrer Website mit Kunden und übergibt den Auftrag bei Bedarf an den Meister, also an Sie.",
  "f.title": "Anfrage stellen",
  "f.intro": "Beschreiben Sie kurz Ihren Betrieb und Ihren Bedarf. Sobald Ihre Anfrage gespeichert ist, nennen wir Ihnen eine Anfragenummer.",
  "f.fine": "Dies ist eine Bewertungsaufgabe. Bitte nur fiktive Testdaten eingeben.",
  "f.name": "Ihr Name",
  "f.email": "E-Mail",
  "f.service": "Leistung",
  "f.opt0": "Leistung auswählen",
  "f.message": "Was möchten Sie tun?",
  "f.hint": "/ 1000 Zeichen. Schreiben Sie mindestens 10 Zeichen.",
  "f.submit": "Anfrage senden",
  "ok.title": "Ihre Anfrage wurde gespeichert",
  "ok.number": "Ihre Anfragenummer:",
  "ok.note": "Notieren Sie sich diese Nummer. Der Eintrag wurde auf dem Server gespeichert.",
  "ok.new": "Neue Anfrage stellen",
  "ft.note": "Kalfa ist eine fiktive Dienstleistung und wurde nur für diese Bewertung erstellt.",
  "js.sending": "Wird gesendet…",
  "js.fixFields": "Einige Felder müssen korrigiert werden.",
  "js.saveFailed": "Ihre Anfrage konnte nicht gespeichert werden. Bitte versuchen Sie es gleich noch einmal.",
  "js.rate": "Zu viele Versuche. Bitte in einer Minute erneut versuchen.",
  "js.timeout": "Der Server hat nicht rechtzeitig geantwortet. Ihre Anfrage wurde möglicherweise gespeichert. Dieselbe Anfrage erneut zu senden ist sicher, sie wird nicht doppelt gespeichert.",
  "js.network": "Der Server ist nicht erreichbar. Prüfen Sie Ihre Verbindung. Ihre Anfrage wurde möglicherweise gespeichert, das erneute Senden derselben Anfrage ist sicher.",
    "nf.title": "Diese Seite wurde nicht gefunden.",
    "nf.text": "Die gesuchte Adresse existiert nicht oder wurde verschoben. Sie können auf der Startseite weitermachen.",
    "nf.home": "Zurück zur Startseite"
}
  };
  var LANGS = ['tr', 'en', 'de'];
  var LANG_KEY = 'kalfa-lang';
  var NAMES = { tr: 'Türkçe', en: 'English', de: 'Deutsch' };
  var api = { DICT: DICT, LANGS: LANGS, lang: 'tr' };
  if (typeof document === 'undefined') return api;

  var ORIGINAL = {};            // HTML'deki Türkçe metinler: anahtar → metin
  var ATTR_ORIGINAL = [];       // [öğe, öznitelik, anahtar, Türkçe değer]
  var meta = { title: document.title, description: '' };
  var descEl = document.querySelector('meta[name="description"]');
  if (descEl) meta.description = descEl.getAttribute('content');

  function read(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function write(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* tercih kaydedilemez, sorun değil */ } }

  api.t = function (key) {
    var d = DICT[api.lang];
    if (d && d[key] !== undefined) return d[key];
    if (DICT.tr[key] !== undefined) return DICT.tr[key];
    return ORIGINAL[key] !== undefined ? ORIGINAL[key] : key;
  };

  function collect() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n]'), function (el) {
      var key = el.getAttribute('data-i18n');
      if (!(key in ORIGINAL)) ORIGINAL[key] = el.textContent;
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n-words]'), function (el) {
      var key = el.getAttribute('data-i18n-words');
      if (!(key in ORIGINAL)) ORIGINAL[key] = el.textContent.replace(/\s+/g, ' ').trim();
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n-attr]'), function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':');
        ATTR_ORIGINAL.push([el, p[0].trim(), p[1].trim(), el.getAttribute(p[0].trim())]);
      });
    });
  }

  function pick(lang, key) {
    if (lang === 'tr') return ORIGINAL[key] !== undefined ? ORIGINAL[key] : DICT.tr[key];
    var d = DICT[lang];
    return d && d[key] !== undefined ? d[key] : ORIGINAL[key];
  }

  function buildWords(el, text) {
    while (el.firstChild) el.removeChild(el.firstChild);
    text.split(' ').forEach(function (word, i) {
      if (i > 0) el.appendChild(document.createTextNode(' '));
      var outer = document.createElement('span');
      outer.className = 'w';
      var inner = document.createElement('span');
      inner.textContent = word;
      outer.appendChild(inner);
      el.appendChild(outer);
    });
  }

  function apply(lang) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n]'), function (el) {
      var v = pick(lang, el.getAttribute('data-i18n'));
      if (v !== undefined) el.textContent = v;
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n-words]'), function (el) {
      var v = pick(lang, el.getAttribute('data-i18n-words'));
      if (v !== undefined) buildWords(el, v);
    });
    ATTR_ORIGINAL.forEach(function (a) {
      var v = lang === 'tr' ? a[3] : (DICT[lang][a[2]] !== undefined ? DICT[lang][a[2]] : a[3]);
      if (v !== null && v !== undefined) a[0].setAttribute(a[1], v);
    });
    document.title = lang === 'tr' ? meta.title : DICT[lang]['meta.title'];
    if (descEl) descEl.setAttribute('content', lang === 'tr' ? meta.description : DICT[lang]['meta.desc']);
    document.documentElement.setAttribute('lang', lang);
    // Açılır dil menüsü: seçili dil işaretlenir, düğmede kodu ve tam adı görünür
    Array.prototype.forEach.call(document.querySelectorAll('.lang-menu button[data-lang]'), function (b) {
      if (b.getAttribute('data-lang') === lang) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
    });
    var toggle = document.querySelector('.lang-toggle');
    if (toggle) {
      var code = toggle.querySelector('.lang-code');
      if (code) code.textContent = lang.toUpperCase();
      // Erişilebilir isim, ekrandaki görünen metni (dil kodu) içermeli: sesle kontrol "TR" diyerek düğmeyi bulabilsin (WCAG 2.5.3)
      toggle.setAttribute('aria-label', lang.toUpperCase() + ', ' + (lang === 'tr' ? 'Dil' : DICT[lang]['tools.lang']) + ': ' + NAMES[lang]);
    }
  }

  api.setLang = function (lang, persist) {
    if (LANGS.indexOf(lang) === -1) return;
    api.lang = lang;
    apply(lang);
    if (persist) write(LANG_KEY, lang);
    document.dispatchEvent(new CustomEvent('kalfa:lang', { detail: { lang: lang } }));
  };

  function init() {
    collect();
    var fromUrl = null;
    try { fromUrl = new URLSearchParams(window.location.search).get('lang'); } catch (e) { /* eski tarayıcı */ }
    var stored = read(LANG_KEY);
    var start = LANGS.indexOf(fromUrl) !== -1 ? fromUrl : (LANGS.indexOf(stored) !== -1 ? stored : 'tr');
    if (start !== 'tr') api.setLang(start, LANGS.indexOf(fromUrl) !== -1);
    else { api.lang = 'tr'; apply('tr'); }
    initMenu();
  }

  // Açılır dil menüsü: düğmeyle açılır, seçince, Escape'e basınca ya da dışarı tıklayınca kapanır.
  // Ok tuşlarıyla gezilir. Kapanınca odak düğmeye döner.
  function initMenu() {
    var root = document.querySelector('.lang');
    var toggle = document.querySelector('.lang-toggle');
    var menu = document.getElementById('lang-menu');
    if (!root || !toggle || !menu) return;
    var items = Array.prototype.slice.call(menu.querySelectorAll('button[data-lang]'));

    function isOpen() { return !menu.hidden; }
    function open() {
      menu.hidden = false;
      toggle.setAttribute('aria-expanded', 'true');
      var current = menu.querySelector('[aria-current="true"]') || items[0];
      if (current) current.focus();
    }
    function close(returnFocus) {
      if (!isOpen()) return;
      menu.hidden = true;
      toggle.setAttribute('aria-expanded', 'false');
      if (returnFocus) toggle.focus();
    }

    toggle.addEventListener('click', function () { if (isOpen()) close(false); else open(); });
    items.forEach(function (b) {
      b.addEventListener('click', function () {
        api.setLang(b.getAttribute('data-lang'), true);
        close(true);
      });
    });
    document.addEventListener('keydown', function (e) {
      if (!isOpen()) return;
      if (e.key === 'Escape') { e.preventDefault(); close(true); return; }
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        var at = items.indexOf(document.activeElement);
        if (at === -1) return;
        e.preventDefault();
        items[(at + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length].focus();
      }
    });
    document.addEventListener('click', function (e) { if (isOpen() && !root.contains(e.target)) close(false); });
    root.addEventListener('focusout', function (e) {
      if (isOpen() && e.relatedTarget && !root.contains(e.relatedTarget)) close(false);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
  return api;
});
