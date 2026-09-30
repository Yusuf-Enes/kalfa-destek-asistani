const path = require('node:path');
const { createDb } = require('./src/db');
const { createApp } = require('./src/app');

async function main() {
  // Canlı ortamda veri tabanı adresi yoksa açılmayı reddet. Aksi halde uygulama sessizce geçici diske yazar
  // ve servis yeniden başlayınca tüm kayıtlar silinirdi. Yerel denemede NODE_ENV tanımlı olmadığı için etkilenmez.
  if (process.env.NODE_ENV === 'production' && !process.env.DATABASE_URL && process.env.ALLOW_LOCAL_DB !== '1') {
    console.error('DATABASE_URL tanımlı değil. Canlı ortamda kayıtların kalıcı olması için bir Postgres adresi gerekir.');
    console.error('Neon bağlantı adresini DATABASE_URL olarak ekleyin. (Yalnızca deneme için ALLOW_LOCAL_DB=1 verilebilir.)');
    process.exit(1);
  }
  const db = await createDb({
    connectionString: process.env.DATABASE_URL,
    dataDir: process.env.DATA_DIR || path.join(__dirname, '.data', 'pglite'),
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
