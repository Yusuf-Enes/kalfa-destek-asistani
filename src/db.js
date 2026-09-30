// İki sürücü, tek arayüz: DATABASE_URL varsa Postgres (canlı), yoksa gömülü PGlite (yerel geliştirme ve test).
const SCHEMA = `
  CREATE TABLE IF NOT EXISTS support_requests (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT        NOT NULL,
    email      TEXT        NOT NULL,
    service    TEXT        NOT NULL,
    message    TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
  )
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
