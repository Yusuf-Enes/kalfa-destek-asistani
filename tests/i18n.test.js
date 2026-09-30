const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const I18N = require('../public/i18n.js');
const Validation = require('../public/validation.js');

const html = fs.readFileSync(path.join(__dirname, '..', 'public', 'index.html'), 'utf8')
  + '\n' + fs.readFileSync(path.join(__dirname, '..', 'public', '404.html'), 'utf8'); // çeviri anahtarları iki sayfada da taranır
const appJs = fs.readFileSync(path.join(__dirname, '..', 'public', 'app.js'), 'utf8');

const textKeys = [...html.matchAll(/data-i18n="([^"]+)"/g)].map((m) => m[1]);
const wordKeys = [...html.matchAll(/data-i18n-words="([^"]+)"/g)].map((m) => m[1]);
const attrKeys = [...html.matchAll(/data-i18n-attr="([^"]+)"/g)].flatMap((m) => m[1].split(';').map((p) => p.split(':')[1].trim()));
const usedInHtml = new Set([...textKeys, ...wordKeys, ...attrKeys]);
// app.js içindeki çeviri anahtarları: çağrı biçimine (koşullu ifade dahil) değil, dizgelerin kendisine bakılır
const jsKeys = [...appJs.matchAll(/'((?:js|f)\.[A-Za-z0-9.]+)'/g)].map((m) => m[1]);

test('diller tr, en, de ve HTML dil düğmeleri bunlarla birebir aynı', () => {
  assert.deepEqual([...I18N.LANGS], ['tr', 'en', 'de']);
  const buttons = [...html.matchAll(/data-lang="([a-z]+)"/g)].map((m) => m[1]);
  assert.deepEqual(buttons, ['tr', 'en', 'de']);
  assert.match(html, /<html lang="tr">/);
});

test('HTML\'de kullanılan her çeviri anahtarı İngilizce ve Almancada var', () => {
  assert.ok(usedInHtml.size > 50, 'HTML anahtarları bulunamadı');
  for (const lang of ['en', 'de']) {
    const missing = [...usedInHtml].filter((k) => !(k in I18N.DICT[lang]));
    assert.deepEqual(missing, [], `${lang} çevirisi eksik: ${missing.join(', ')}`);
  }
});

test('İngilizce ve Almanca sözlüklerin anahtarları aynı, hiçbir değer boş değil', () => {
  assert.deepEqual(Object.keys(I18N.DICT.en).sort(), Object.keys(I18N.DICT.de).sort());
  for (const lang of ['en', 'de']) {
    for (const [k, v] of Object.entries(I18N.DICT[lang])) {
      assert.ok(typeof v === 'string' && v.trim().length > 0, `${lang}.${k} boş`);
    }
  }
});

test('kullanılmayan (ölü) çeviri anahtarı yok', () => {
  const allowed = (k) => k.startsWith('js.') || k.startsWith('meta.');
  const dead = Object.keys(I18N.DICT.en).filter((k) => !usedInHtml.has(k) && !allowed(k));
  assert.deepEqual(dead, [], `HTML'de kullanılmayan anahtarlar: ${dead.join(', ')}`);
});

test('çeviriler Türkçe metinle aynı değil (unutulmuş çeviri yakalanır)', () => {
  const original = {};
  for (const m of html.matchAll(/<(\w+)[^>]*data-i18n(?:-words)?="([^"]+)"[^>]*>([\s\S]*?)<\/\1>/g)) {
    const text = m[3].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
    if (text) original[m[2]] = original[m[2]] || text;
  }
  const same = [];
  for (const lang of ['en', 'de']) {
    for (const [k, tr] of Object.entries(original)) {
      if (I18N.DICT[lang][k] === tr) same.push(`${lang}.${k}`);
    }
  }
  assert.deepEqual(same, [], `Türkçeyle aynı kalan çeviriler: ${same.join(', ')}`);
});

test('app.js\'te kullanılan çeviri anahtarları üç dilde de çözülebilir', () => {
  assert.ok(jsKeys.length >= 5, 'app.js anahtarları bulunamadı');
  for (const k of new Set(jsKeys)) {
    for (const lang of ['tr', 'en', 'de']) {
      const found = k in I18N.DICT[lang] || (lang === 'tr' && (k in I18N.DICT.tr || usedInHtml.has(k)));
      assert.ok(found, `${lang} için '${k}' çözülemiyor`);
    }
  }
});

test('doğrulama mesajları üç dilde var ve dile göre seçilir', () => {
  const fields = ['name', 'email', 'service', 'message'];
  for (const lang of ['tr', 'en', 'de']) {
    assert.deepEqual(Object.keys(Validation.MESSAGES[lang]).sort(), [...fields].sort());
    const errs = Validation.validate({}, lang).errors;
    for (const f of fields) assert.equal(errs[f], Validation.MESSAGES[lang][f]);
  }
  assert.notEqual(Validation.MESSAGES.en.email, Validation.MESSAGES.tr.email);
  assert.notEqual(Validation.MESSAGES.de.email, Validation.MESSAGES.en.email);
  // Bilinmeyen dil ve dil verilmemesi Türkçeye düşer (sunucu davranışı)
  assert.equal(Validation.validate({}, 'xx').errors.name, Validation.MESSAGES.tr.name);
  assert.equal(Validation.validate({}).errors.name, Validation.MESSAGES.tr.name);
});

test('sunucu doğrulaması dilden bağımsız çalışır (aynı alanlar hatalı)', () => {
  const bad = { name: '', email: 'x', service: 'yok', message: 'kısa' };
  const keys = (l) => Object.keys(Validation.validate(bad, l).errors).sort().join();
  assert.equal(keys('tr'), keys('en'));
  assert.equal(keys('tr'), keys('de'));
});
