const path = require('node:path');
const { createDb } = require('./src/db');
const { createApp } = require('./src/app');

async function main() {
  const db = await createDb({
    connectionString: process.env.DATABASE_URL,
    dataDir: path.join(__dirname, '.data', 'pglite'),
  });
  const app = createApp({ db, adminToken: process.env.ADMIN_TOKEN });
  const port = Number(process.env.PORT) || 3000;

  const server = app.listen(port, () => {
    console.log(`Sunucu http://localhost:${port} adresinde (veri tabanı: ${db.kind})`);
  });

  const shutdown = () => {
    server.close(async () => {
      await db.close().catch(() => {});
      process.exit(0);
    });
  };
  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

main().catch((err) => {
  console.error('Başlatılamadı:', err.message);
  process.exit(1);
});
