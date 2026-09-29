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
    const pool = new Pool({ connectionString, max: 5, connectionTimeoutMillis: 10000 });
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
