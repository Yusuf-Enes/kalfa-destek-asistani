// Kalıcı kayıt ve üretim (Postgres) yolu testleri.
// Gerçek bir Postgres yerine, gömülü veri tabanını Postgres ağ protokolüyle sunan bir geliştirme aracı kullanılır.
// Böylece canlıda kullanılan `pg` sürücüsü yolu (DATABASE_URL) gerçekten çalıştırılır.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const net = require('node:net');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { PGlite } = require('@electric-sql/pglite');
const { PGLiteSocketServer } = require('@electric-sql/pglite-socket');
const { createDb } = require('../src/db');

const root = path.join(__dirname, '..');
const valid = {
  name: 'Ayşe Demir',
  email: 'ayse@ornek-sirket.com',
  service: 'sss-botu',
  message: 'Günde yaklaşık 40 aynı soruya cevap veriyoruz, bunu azaltmak istiyoruz.',
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Geliştirme aracının kuyruktaki son mesajı kapanmış veri tabanında işlememesi için kapanış sıralanır
async function shutdown(sock, db) {
  await sock.stop().catch(() => {});
  await sleep(500);
  await db.close().catch(() => {});
}

function freePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.listen(0, '127.0.0.1', () => { const { port } = srv.address(); srv.close(() => resolve(port)); });
    srv.on('error', reject);
  });
}

// server.js'i gerçek bir süreç olarak başlatır ve dinlemeye başlayana kadar bekler
function startServer(env) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['server.js'], { cwd: root, env: { ...process.env, ...env } });
    let out = '';
    const timer = setTimeout(() => { child.kill(); reject(new Error('sunucu başlamadı: ' + out)); }, 20000);
    child.stdout.on('data', (d) => { out += d; if (out.includes('adresinde')) { clearTimeout(timer); resolve({ child, output: () => out }); } });
    child.stderr.on('data', (d) => { out += d; });
    child.on('exit', (code) => { clearTimeout(timer); reject(new Error(`sunucu çıktı (${code}): ${out}`)); });
  });
}

const stop = (child) => new Promise((resolve) => { child.removeAllListeners('exit'); child.on('exit', resolve); child.kill('SIGTERM'); });

const post = (port, body) => fetch(`http://127.0.0.1:${port}/api/requests`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
const list = async (port) => (await (await fetch(`http://127.0.0.1:${port}/api/requests`, { headers: { 'x-admin-token': 'anahtar' } })).json()).requests;

test('kayıt, sunucu kapatılıp yeniden açılınca da yerinde durur (kalıcılık)', async () => {
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kalfa-kalicilik-'));
  try {
    let port = await freePort();
    let s = await startServer({ PORT: String(port), DATA_DIR: dataDir, ADMIN_TOKEN: 'anahtar', DATABASE_URL: '' });
    const res = await post(port, valid);
    assert.equal(res.status, 201);
    const { id } = await res.json();
    assert.equal((await list(port)).length, 1);
    await stop(s.child);

    // Sunucu tamamen kapandı. Yeni bir süreç aynı klasörden başlar.
    port = await freePort();
    s = await startServer({ PORT: String(port), DATA_DIR: dataDir, ADMIN_TOKEN: 'anahtar', DATABASE_URL: '' });
    const rows = await list(port);
    assert.equal(rows.length, 1, 'yeniden başlatınca kayıt kaybolmamalı');
    assert.equal(rows[0].id, id);
    assert.equal(rows[0].email, valid.email);
    assert.equal(rows[0].message, valid.message);
    await stop(s.child);
  } finally {
    fs.rmSync(dataDir, { recursive: true, force: true });
  }
});

test('Postgres yolu (DATABASE_URL): tablo kurulur, kayıt yazılır, sunucu Postgres sürücüsünü kullanır', async () => {
  const db = new PGlite();
  const pgPort = await freePort();
  const sock = new PGLiteSocketServer({ db, port: pgPort, host: '127.0.0.1' });
  await sock.start();
  let s;
  try {
    const port = await freePort();
    s = await startServer({ PORT: String(port), ADMIN_TOKEN: 'anahtar', DATABASE_URL: `postgresql://postgres:postgres@127.0.0.1:${pgPort}/postgres` });
    assert.match(s.output(), /veri tabanı: postgres/);
    const res = await post(port, valid);
    assert.equal(res.status, 201);
    const { id } = await res.json();
    assert.match(id, /^\d+$/, 'kayıt numarası (bigint) metin olarak dönmeli');
    const rows = await list(port);
    assert.equal(rows.length, 1);
    assert.equal(rows[0].name, valid.name);
    // Veri gerçekten Postgres tarafında duruyor
    const direct = await db.query('SELECT count(*)::int AS n FROM support_requests');
    assert.equal(direct.rows[0].n, 1);
    // Geçersiz istek Postgres'e hiç ulaşmaz
    assert.equal((await post(port, { ...valid, email: 'x' })).status, 400);
    assert.equal((await db.query('SELECT count(*)::int AS n FROM support_requests')).rows[0].n, 1);
  } finally {
    if (s) await stop(s.child);
    await shutdown(sock, db);
  }
});

test('veri tabanı bağlantıları kopunca sunucu çökmez, veri tabanı dönünce kayıt yazılır', async () => {
  const db = new PGlite();
  const pgPort = await freePort();
  let sock = new PGLiteSocketServer({ db, port: pgPort, host: '127.0.0.1' });
  await sock.start();
  let s;
  const origError = console.error;
  try {
    const port = await freePort();
    s = await startServer({ PORT: String(port), ADMIN_TOKEN: 'anahtar', DATABASE_URL: `postgresql://postgres:postgres@127.0.0.1:${pgPort}/postgres` });
    assert.equal((await post(port, valid)).status, 201);   // havuzda boşta bir bağlantı kalır

    // Neon'un boştaki bağlantıyı kapatmasına benzer: tüm bağlantılar bir anda kopar
    await sock.stop();
    await sleep(800);
    let alive = true;
    s.child.once('exit', () => { alive = false; });
    await sleep(200);
    assert.ok(alive, 'bağlantı kopunca sunucu süreci çökmemeli');

    // Veri tabanı çalışırken kopan bağlantı sırasında gelen istek dürüstçe hata verir, başarı göstermez
    const during = await post(port, valid);
    assert.notEqual(during.status, 201, 'veri tabanı yokken başarı dönmemeli');

    // Veri tabanı geri gelir, sunucu kendiliğinden yeniden bağlanır
    sock = new PGLiteSocketServer({ db, port: pgPort, host: '127.0.0.1' });
    await sock.start();
    await sleep(400);
    const after = await post(port, valid);
    assert.equal(after.status, 201, 'veri tabanı dönünce yeni kayıt yazılabilmeli');
    assert.equal((await list(port)).length, 2);
  } finally {
    console.error = origError;
    if (s) await stop(s.child);
    await shutdown(sock, db);
  }
});

test('createDb: dışarıdan verilen Postgres bağlantısında boşta bağlantı hatası süreci çökertmez', async () => {
  const db = new PGlite();
  const pgPort = await freePort();
  let sock = new PGLiteSocketServer({ db, port: pgPort, host: '127.0.0.1' });
  await sock.start();
  const uncaught = [];
  const onUncaught = (e) => uncaught.push(e.message);
  process.on('uncaughtException', onUncaught);
  const origError = console.error;
  const logged = [];
  console.error = (...a) => logged.push(a.join(' '));
  let store;
  try {
    store = await createDb({ connectionString: `postgresql://postgres:postgres@127.0.0.1:${pgPort}/postgres` });
    assert.equal(store.kind, 'postgres');
    await store.query('SELECT 1');
    await sock.stop();          // boştaki bağlantı kopar
    await sleep(800);
    assert.deepEqual(uncaught, [], 'yakalanmamış hata oluşmamalı (havuzun error olayı dinleniyor olmalı)');
    assert.ok(logged.some((l) => l.includes('Boştaki veri tabanı bağlantısı koptu')), 'kopma günlüğe yazılmalı');
  } finally {
    console.error = origError;
    process.off('uncaughtException', onUncaught);
    if (store) await store.close().catch(() => {});
    await sleep(300);
    await shutdown(sock, db);
  }
});

test('canlı ortamda DATABASE_URL yoksa sunucu açılmayı reddeder (kayıtlar sessizce kaybolmasın)', async () => {
  const run = (env) => new Promise((resolve) => {
    const child = spawn(process.execPath, ['server.js'], { cwd: root, env: { ...process.env, PORT: '0', ...env } });
    let err = '', out = '';
    child.stderr.on('data', (d) => { err += d; });
    child.stdout.on('data', (d) => { out += d; });
    const timer = setTimeout(() => { child.kill('SIGKILL'); resolve({ code: 'zaman aşımı', err, out, started: out.includes('adresinde') }); }, 6000);
    child.on('exit', (code) => { clearTimeout(timer); resolve({ code, err, out, started: out.includes('adresinde') }); });
    if (env.__stopAfter) setTimeout(() => child.kill('SIGTERM'), env.__stopAfter);
  });
  const refused = await run({ NODE_ENV: 'production', DATABASE_URL: '' });
  assert.equal(refused.code, 1, 'canlıda adres yoksa süreç hata koduyla çıkmalı');
  assert.equal(refused.started, false, 'sunucu hiç dinlemeye başlamamalı');
  assert.match(refused.err, /DATABASE_URL tanımlı değil/);
  // Bilinçli olarak yerel veri tabanına izin verilirse açılır
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kalfa-izin-'));
  try {
    const allowed = await run({ NODE_ENV: 'production', DATABASE_URL: '', ALLOW_LOCAL_DB: '1', DATA_DIR: dataDir, __stopAfter: 3000 });
    assert.equal(allowed.started, true, 'ALLOW_LOCAL_DB=1 ile açılmalı');
  } finally {
    fs.rmSync(dataDir, { recursive: true, force: true });
  }
  // NODE_ENV tanımlı değilse (yerel geliştirme) etkilenmez: bellekte/klasörde açılır
  const dev = await run({ NODE_ENV: '', DATABASE_URL: '', DATA_DIR: fs.mkdtempSync(path.join(os.tmpdir(), 'kalfa-yerel-')), __stopAfter: 3000 });
  assert.equal(dev.started, true, 'yerel geliştirmede açılmalı');
});
