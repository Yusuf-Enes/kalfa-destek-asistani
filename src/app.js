const crypto = require('node:crypto');
const path = require('node:path');
const express = require('express');
const helmet = require('helmet');
const { rateLimit } = require('express-rate-limit');
const { validate } = require('../public/validation');

const SAVE_FAILED = 'Talebiniz kaydedilemedi. Lütfen biraz sonra tekrar deneyin.';

function digest(value) {
  return crypto.createHash('sha256').update(String(value)).digest();
}

function createApp({ db, adminToken, submitLimit = 10 }) {
  const app = express();
  app.set('trust proxy', 1); // Render gibi bir ters vekil arkasında gerçek istemci IP'si için
  app.disable('x-powered-by');

  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'"],
          styleSrc: ["'self'"],
          imgSrc: ["'self'", 'data:'],
          connectSrc: ["'self'"],
          objectSrc: ["'none'"],
          baseUri: ["'self'"],
          formAction: ["'self'"],
          frameAncestors: ["'none'"],
          upgradeInsecureRequests: null,
        },
      },
    })
  );

  app.get('/healthz', (req, res) => res.json({ ok: true }));

  const submitLimiter = rateLimit({
    windowMs: 60 * 1000,
    limit: submitLimit,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: 'Çok fazla deneme yaptınız. Bir dakika sonra tekrar deneyin.' },
  });

  app.post('/api/requests', submitLimiter, express.json({ limit: '10kb' }), async (req, res) => {
    const { values, errors } = validate(req.body);
    if (Object.keys(errors).length > 0) {
      return res.status(400).json({ errors });
    }

    // Yanıt, INSERT tamamlanmadan asla başarı döndürmez. Hata olursa Express 5 hata yakalayıcısına düşer.
    const rows = await db.query(
      'INSERT INTO support_requests (name, email, service, message) VALUES ($1, $2, $3, $4) RETURNING id, created_at',
      [values.name, values.email, values.service, values.message]
    );
    res.status(201).json({ id: String(rows[0].id), createdAt: new Date(rows[0].created_at).toISOString() });
  });

  // Kayıtları görmek için yönetici anahtarı gerekir. ADMIN_TOKEN tanımlı değilse uç hiç açılmaz.
  app.get('/api/requests', (req, res, next) => {
    if (!adminToken) return res.status(404).json({ error: 'Bulunamadı.' });
    const given = req.get('x-admin-token') || '';
    if (!crypto.timingSafeEqual(digest(given), digest(adminToken))) {
      return res.status(401).json({ error: 'Yetkisiz.' });
    }
    db.query(
      'SELECT id, name, email, service, message, created_at FROM support_requests ORDER BY id DESC LIMIT 50'
    )
      .then((rows) => res.json({ requests: rows.map((r) => ({ ...r, id: String(r.id) })) }))
      .catch(next);
  });

  app.use('/api', (req, res) => res.status(404).json({ error: 'Bulunamadı.' }));
  app.use(express.static(path.join(__dirname, '..', 'public')));

  // eslint-disable-next-line no-unused-vars
  app.use((err, req, res, next) => {
    if (err.type === 'entity.parse.failed') return res.status(400).json({ error: 'İstek okunamadı.' });
    if (err.type === 'entity.too.large') return res.status(413).json({ error: 'İstek çok büyük.' });
    console.error('İstek hatası:', err.message); // gövde içeriğini bilerek loglamıyoruz
    res.status(500).json({ error: SAVE_FAILED });
  });

  return app;
}

module.exports = { createApp };
