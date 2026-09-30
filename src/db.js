// İki sürücü, tek arayüz: DATABASE_URL varsa Postgres (canlı), yoksa gömülü PGlite (yerel geliştirme ve test).
const { SERVICES, LIMITS } = require('../public/validation');

// Geçerlilik sınırları veri tabanında da kural olarak durur (savunma derinliği): uygulama bir gün hatalı bir
// değer üretse bile ya da biri veri tabanına doğrudan yazsa bile bozuk kayıt girmez. Sınırlar validation.js ile aynı kaynaktan gelir.
const SERVICE_LIST = Object.keys(SERVICES).map((k) => `'${k}'`).join(', ');
const SCHEMA = `
  CREATE TABLE IF NOT EXISTS support_requests (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT        NOT NULL CHECK (char_length(name) BETWEEN ${LIMITS.name.min} AND ${LIMITS.name.max}),
    email      TEXT        NOT NULL CHECK (char_length(email) <= ${LIMITS.email.max} AND email ~ '^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$'),
    service    TEXT        NOT NULL CHECK (service IN (${SERVICE_LIST})),
    message    TEXT        NOT NULL CHECK (char_length(message) BETWEEN ${LIMITS.message.min} AND ${LIMITS.message.max}),
    client_id  TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
  );
  -- Eski kurulumlar için: sütun yoksa eklenir
  ALTER TABLE support_requests ADD COLUMN IF NOT EXISTS client_id TEXT;
  -- Aynı gönderim anahtarıyla ikinci kez gelen istek yeni kayıt oluşturmaz (tekrar göndermek güvenlidir)
  CREATE UNIQUE INDEX IF NOT EXISTS support_requests_client_id_key ON support_requests (client_id) WHERE client_id IS NOT NULL;
`;

async function createDb({ connectionString, dataDir } = {}) {
  if (connectionString) {
    const { Pool } = require('pg');
    // Boştaki bağlantıları 20 saniyede kendimiz kapatırız (Neon'un boştaki bağlantıyı kesmesinden çok önce).
    const pool = new Pool({ connectionString, max: 5, connectionTimeoutMillis: 10000, idleTimeoutMillis: 20000 });
    // Boştaki bir bağlantı koparsa havuz 'error' olayı yayar. Dinleyici yoksa Node süreci çöker,
    // yani tek bir kopan bağlantı yüzünden tüm site düşerdi. Bağlantı havuzdan atılır, sonraki istek yenisini açar.
    pool.on('error', (err) => console.error('Boştaki veri tabanı bağlantısı koptu, yenisi açılacak:', err.message));
    await pool.query(SCHEMA);
    return {
      kind: 'postgres',
      query: async (text, params) => (await pool.query(text, params)).rows,
      close: () => pool.end(),
    };
  }

  const { PGlite } = require('@electric-sql/pglite');
  if (dataDir) require('node:fs').mkdirSync(dataDir, { recursive: true });
  const pg = new PGlite(dataDir); // dataDir yoksa bellekte çalışır
  await pg.exec(SCHEMA);
  return {
    kind: 'pglite',
    query: async (text, params) => (await pg.query(text, params)).rows,
    close: () => pg.close(),
  };
}

module.exports = { createDb };
