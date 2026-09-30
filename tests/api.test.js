const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { createDb } = require('../src/db');
const { createApp } = require('../src/app');

const valid = {
  name: 'Ayşe Demir',
  email: 'ayse@ornek-sirket.com',
  service: 'sss-botu',
  message: 'Günde yaklaşık 40 aynı soruya cevap veriyoruz, bunu azaltmak istiyoruz.',
};

let db, server, base;

async function post(body, { raw = false, headers = {} } = {}) {
  const res = await fetch(`${base}/api/requests`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...headers },
    body: raw ? body : JSON.stringify(body),
  });
  return { status: res.status, body: await res.json().catch(() => null) };
}

async function count() {
  const rows = await db.query('SELECT count(*)::int AS n FROM support_requests');
  return rows[0].n;
}

before(async () => {
  db = await createDb(); // bellekte PGlite
  const app = createApp({ db, adminToken: 'test-anahtari', submitLimit: 1000 });
  await new Promise((resolve) => (server = app.listen(0, resolve)));
  base = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  await new Promise((resolve) => server.close(resolve));
  await db.close();
});

test('geçerli talep 201 döner ve gerçekten kaydedilir', async () => {
  const before = await count();
  const res = await post(valid);
  assert.equal(res.status, 201);
  assert.ok(res.body.id);
  assert.equal(await count(), before + 1);
  const [row] = await db.query('SELECT * FROM support_requests WHERE id = $1', [res.body.id]);
  assert.equal(row.email, valid.email);
  assert.equal(row.service, valid.service);
});

test('metin alanları kırpılır', async () => {
  const res = await post({ ...valid, name: '  Can Yılmaz  ' });
  assert.equal(res.status, 201);
  const [row] = await db.query('SELECT name FROM support_requests WHERE id = $1', [res.body.id]);
  assert.equal(row.name, 'Can Yılmaz');
});

const invalidCases = [
  ['boş ad', { name: '' }, 'name'],
  ['tek harfli ad', { name: 'A' }, 'name'],
  ['81 karakterli ad', { name: 'a'.repeat(81) }, 'name'],
  ['ad sayı türünde', { name: 12345 }, 'name'],
  ['e-posta @ içermiyor', { email: 'ayse.ornek.com' }, 'email'],
  ['e-posta alan adı yok', { email: 'ayse@' }, 'email'],
  ['e-posta çok uzun', { email: 'a'.repeat(250) + '@x.com' }, 'email'],
  ['e-postada boşluk', { email: 'ay se@ornek.com' }, 'email'],
  ['listede olmayan hizmet', { service: 'hack' }, 'service'],
  ['hizmet yok', { service: '' }, 'service'],
  ['prototip anahtarı hizmet olarak', { service: 'constructor' }, 'service'],
  ['9 karakterli mesaj', { message: '123456789' }, 'message'],
  ['1001 karakterli mesaj', { message: 'a'.repeat(1001) }, 'message'],
  ['sadece boşluklu mesaj', { message: ' '.repeat(50) }, 'message'],
  ['NUL karakterli mesaj', { message: 'merhaba\u0000 dünya nasılsınız' }, 'message'],
];

for (const [label, patch, field] of invalidCases) {
  test(`geçersiz: ${label} → 400 ve kayıt yok`, async () => {
    const before = await count();
    const res = await post({ ...valid, ...patch });
    assert.equal(res.status, 400);
    assert.ok(res.body.errors[field], `${field} için hata bekleniyordu`);
    assert.equal(await count(), before);
  });
}

test('sınır değerler kabul edilir (2 karakterli ad, 10 ve 1000 karakterli mesaj)', async () => {
  assert.equal((await post({ ...valid, name: 'Al' })).status, 201);
  assert.equal((await post({ ...valid, message: 'a'.repeat(10) })).status, 201);
  assert.equal((await post({ ...valid, message: 'a'.repeat(1000) })).status, 201);
});

test('çok satırlı mesaj kabul edilir', async () => {
  assert.equal((await post({ ...valid, message: 'Birinci satır\nİkinci satır burada' })).status, 201);
});

test('SQL enjeksiyon denemesi düz metin olarak saklanır, tablo bozulmaz', async () => {
  const evil = "Robert'); DROP TABLE support_requests;-- ",
    res = await post({ ...valid, name: evil + 'x' });
  assert.equal(res.status, 201);
  const [row] = await db.query('SELECT name FROM support_requests WHERE id = $1', [res.body.id]);
  assert.ok(row.name.startsWith('Robert'));
  assert.ok((await count()) > 0);
});

test('gövde JSON değilse veya bozuksa 400', async () => {
  assert.equal((await post('{bozuk', { raw: true })).status, 400);
  const res = await fetch(`${base}/api/requests`, { method: 'POST', headers: { 'content-type': 'text/plain' }, body: 'x' });
  assert.equal(res.status, 400);
});

test('dizi veya null gövde 400', async () => {
  assert.equal((await post([])).status, 400);
  assert.equal((await post(null)).status, 400);
});

test('çok büyük gövde 413', async () => {
  const res = await post({ ...valid, message: 'a'.repeat(20000) });
  assert.equal(res.status, 413);
});

test('veri tabanı hata verirse 500 döner ve başarı bilgisi sızmaz', async () => {
  const broken = {
    kind: 'broken',
    query: async () => {
      throw new Error('bağlantı koptu');
    },
  };
  const app = createApp({ db: broken, submitLimit: 1000 });
  const s = await new Promise((resolve) => {
    const srv = app.listen(0, () => resolve(srv));
  });
  const origError = console.error;
  console.error = () => {};
  try {
    const res = await fetch(`http://127.0.0.1:${s.address().port}/api/requests`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(valid),
    });
    const body = await res.json();
    assert.equal(res.status, 500);
    assert.equal(body.id, undefined);
    assert.ok(body.error);
    assert.doesNotMatch(JSON.stringify(body), /bağlantı koptu/); // iç hata mesajı istemciye gitmez
  } finally {
    console.error = origError;
    await new Promise((resolve) => s.close(resolve));
  }
});

test('hız sınırı aşılınca 429', async () => {
  const app = createApp({ db, submitLimit: 2 });
  const s = await new Promise((resolve) => {
    const srv = app.listen(0, () => resolve(srv));
  });
  try {
    const url = `http://127.0.0.1:${s.address().port}/api/requests`;
    const send = () =>
      fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({}) });
    assert.equal((await send()).status, 400);
    assert.equal((await send()).status, 400);
    assert.equal((await send()).status, 429);
  } finally {
    await new Promise((resolve) => s.close(resolve));
  }
});

test('kayıt listesi anahtarsız 401, yanlış anahtarla 401, doğru anahtarla 200', async () => {
  assert.equal((await fetch(`${base}/api/requests`)).status, 401);
  assert.equal((await fetch(`${base}/api/requests`, { headers: { 'x-admin-token': 'yanlis' } })).status, 401);
  const ok = await fetch(`${base}/api/requests`, { headers: { 'x-admin-token': 'test-anahtari' } });
  assert.equal(ok.status, 200);
  assert.ok((await ok.json()).requests.length > 0);
});

test('ADMIN_TOKEN tanımlı değilse liste ucu 404', async () => {
  const app = createApp({ db });
  const s = await new Promise((resolve) => {
    const srv = app.listen(0, () => resolve(srv));
  });
  try {
    const res = await fetch(`http://127.0.0.1:${s.address().port}/api/requests`, { headers: { 'x-admin-token': '' } });
    assert.equal(res.status, 404);
  } finally {
    await new Promise((resolve) => s.close(resolve));
  }
});

test('güvenlik başlıkları ve CSP var, X-Powered-By yok', async () => {
  const res = await fetch(`${base}/healthz`);
  assert.match(res.headers.get('content-security-policy'), /script-src 'self'/);
  assert.equal(res.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(res.headers.get('x-powered-by'), null);
});

test('formdaki hizmet seçenekleri sunucunun kabul ettiği listeyle birebir aynı', async () => {
  const html = require('node:fs').readFileSync(require('node:path').join(__dirname, '..', 'public', 'index.html'), 'utf8');
  const select = html.match(/<select id="service"[\s\S]*?<\/select>/)[0];
  const values = [...select.matchAll(/<option value="([^"]+)"/g)].map((m) => m[1]).sort();
  const { SERVICES } = require('../public/validation');
  assert.deepEqual(values, Object.keys(SERVICES).sort());
});


// ---------- Gönderim anahtarı (tekrar gönderim güvenli) ----------
const KEY_A = 'a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a8';
const KEY_B = 'b1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a9';

test('aynı gönderim anahtarıyla tekrar gönderim yeni kayıt açmaz, ilk kaydı döndürür', async () => {
  const before = await count();
  const first = await post({ ...valid, clientId: KEY_A });
  assert.equal(first.status, 201);
  assert.equal(first.body.duplicate, false);
  const second = await post({ ...valid, clientId: KEY_A });
  assert.equal(second.status, 201, 'tekrar gönderim de başarı döner (kayıt gerçekten var)');
  assert.equal(second.body.id, first.body.id, 'aynı kayıt numarası dönmeli');
  assert.equal(second.body.duplicate, true);
  assert.equal(await count(), before + 1, 'iki istek tek kayıt oluşturmalı');
});

test('farklı gönderim anahtarları ayrı kayıt oluşturur', async () => {
  const before = await count();
  const a = await post({ ...valid, clientId: KEY_B });
  const b = await post({ ...valid, clientId: 'c1b2c3d4-e5f6-4789-a012-b3c4d5e6f7aa' });
  assert.notEqual(a.body.id, b.body.id);
  assert.equal(await count(), before + 2);
});

test('anahtarsız ya da geçersiz biçimli anahtarlı istekler her seferinde yeni kayıt açar (idempotency yok)', async () => {
  const before = await count();
  await post(valid);
  await post(valid);
  await post({ ...valid, clientId: 'kisa' });          // çok kısa
  await post({ ...valid, clientId: 'kisa' });
  await post({ ...valid, clientId: 12345678901234567 }); // metin değil
  await post({ ...valid, clientId: "x'; DROP TABLE support_requests;--xxxxxxxx" }); // izin verilmeyen karakterler
  assert.equal(await count(), before + 6);
});

test('geçersiz içerik gönderim anahtarı olsa bile kaydedilmez ve anahtarı tüketmez', async () => {
  const before = await count();
  const bad = await post({ ...valid, email: 'x', clientId: 'd1b2c3d4-e5f6-4789-a012-b3c4d5e6f7ab' });
  assert.equal(bad.status, 400);
  assert.equal(await count(), before);
  const ok = await post({ ...valid, clientId: 'd1b2c3d4-e5f6-4789-a012-b3c4d5e6f7ab' });
  assert.equal(ok.status, 201);
  assert.equal(ok.body.duplicate, false, 'reddedilen istek anahtarı tüketmemeli');
});

// ---------- Veri tabanı kuralları (savunma derinliği) ----------
test('veri tabanı, uygulamayı atlayan bozuk kaydı da reddeder (CHECK kuralları)', async () => {
  const ins = (n, e, sv, m) => db.query('INSERT INTO support_requests (name, email, service, message) VALUES ($1, $2, $3, $4)', [n, e, sv, m]);
  const ok = ['Al', 'a@b.co', 'sss-botu', '1234567890'];
  await ins(...ok); // sınır değerli geçerli kayıt girer
  const bads = [
    ['tek harfli ad', ['A', ok[1], ok[2], ok[3]]],
    ['81 karakterli ad', ['a'.repeat(81), ok[1], ok[2], ok[3]]],
    ['e-postada @ yok', [ok[0], 'abc', ok[2], ok[3]]],
    ['e-postada boşluk', [ok[0], 'a b@c.com', ok[2], ok[3]]],
    ['alan adı çok kısa', [ok[0], 'a@b.c', ok[2], ok[3]]],
    ['listede olmayan hizmet', [ok[0], ok[1], 'hack', ok[3]]],
    ['9 karakterli mesaj', [ok[0], ok[1], ok[2], '123456789']],
    ['1001 karakterli mesaj', [ok[0], ok[1], ok[2], 'a'.repeat(1001)]],
  ];
  for (const [label, args] of bads) {
    await assert.rejects(ins(...args), (e) => /check constraint|violates/i.test(e.message), `${label} veri tabanında reddedilmeli`);
  }
});

// ---------- Önbellek ve 404 ----------
test('API yanıtları önbelleğe alınmaz (no-store)', async () => {
  const p = await fetch(`${base}/api/requests`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(valid) });
  assert.equal(p.headers.get('cache-control'), 'no-store');
  const l = await fetch(`${base}/api/requests`, { headers: { 'x-admin-token': 'test-anahtari' } });
  assert.equal(l.headers.get('cache-control'), 'no-store');
  const n = await fetch(`${base}/api/yok`);
  assert.equal(n.headers.get('cache-control'), 'no-store');
});

test('bilinmeyen sayfa düzgün 404 sayfası döner, bilinmeyen API JSON 404 döner', async () => {
  const page = await fetch(`${base}/olmayan-sayfa`);
  assert.equal(page.status, 404);
  assert.match(page.headers.get('content-type'), /text\/html/);
  const html = await page.text();
  assert.match(html, /Bu sayfa bulunamadı/);
  assert.doesNotMatch(html, /Cannot GET/);
  const api = await fetch(`${base}/api/olmayan`);
  assert.equal(api.status, 404);
  assert.match(api.headers.get('content-type'), /application\/json/);
  assert.equal((await fetch(`${base}/`)).status, 200);
  assert.equal((await fetch(`${base}/healthz`)).status, 200);
});
