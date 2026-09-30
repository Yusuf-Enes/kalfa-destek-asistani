# Kalfa

Küçük işletmeler için kurgusal bir müşteri destek asistanı hizmetinin landing page'i ve talep formu. Ziyaretçinin talebi sunucuda kalıcı bir kayda dönüşür. Bu bir değerlendirme çalışmasıdır, yalnızca kurgusal test verisi kullanılmalıdır.

Sayfa hizmeti anlatır. Gerçek bir yapay zekâ ya da otomasyon çalışmaz, çalışan kısım talep formu ve kayıttır.

**Canlı URL:** _(yayına alındıktan sonra buraya eklenecek)_
**Teslim commit kimliği:** _(teslimde `git rev-parse HEAD` çıktısı buraya eklenecek)_

## Ne yapar

- Mobil ve masaüstünde çalışan tek sayfa: sorun, nasıl çalışır, hizmetler, talep formu. Marka kimliği (logo, renk paleti, yazı tipi, hareket kuralları) [BRAND.md](BRAND.md) dosyasındadır.
- Tek açılış sahnesi: başlık gelir, örnek konuşma oynar, ardından iş fişi düşer ve üstüne "Ustaya devredildi" mührü basılır. Kaydırırken bölüm başlıkları yükselir, "Kim neye bakar" işleri kalfadan ustaya doğru sırayla gelir, adım çizgisi çizilir. Formda açıklama ilerleme çizgisi, gönderirken şeritli düğme ve fiş gibi basılan başarı kutusu var. Sayfanın arkasında yumuşak lekeler kaydırdıkça süzülür ve hangi konuda olduğuna göre yeşil ailesinin başka bir tonuna kayar (nane, sönük gri-yeşil, canlı zümrüt-yeşil, yumuşak nane-yeşil, taze yeşil). Sarı ve mavi yoktur. "Hareketi azalt" seçiliyse hareket kapanır, zemin sabit kalır ve her şey hemen görünür.
- Form: ad, e-posta, hizmet seçimi, açıklama.
- **Üç dil:** Türkçe (varsayılan), İngilizce, Almanca. Başlıktaki tek bir dil düğmesinden açılan menüyle (klavyeyle ok tuşları, Escape ve odak yönetimi çalışır) ya da `?lang=en` adres parametresiyle seçilir, seçim tarayıcıda saklanır. Tüm sayfa, form hataları, gönderme durumu ve başarı mesajı seçili dilde görünür. Varsayılan bilerek her zaman Türkçedir, tarayıcının dilinden tahmin edilmez.
- **Koyu tema:** Başlıktaki düğmeyle açılıp kapanır. İlk açılışta işletim sisteminin tercihini izler, düğmeyle yapılan seçim saklanır ve işletim sistemi tercihinden önce gelir. Sayfa çizilmeden önce uygulanır, yani koyu temada beyaz bir parlama olmaz.
- Örnek konuşmadaki mesajlar peşpeşe gelir, "yazıyor" beklemesi yoktur.
- Aynı doğrulama kuralları hem tarayıcıda hem sunucuda çalışır (`public/validation.js` tek dosyadır, ikisi de onu kullanır). İstemci doğrulaması yalnızca kolaylıktır, güvenlik sunucudadır.
- Gönderiliyor, başarı, alan hatası, sunucu hatası, zaman aşımı ve ağ kesintisi durumları ayrı ayrı ele alınır.
- Başarı mesajı ve talep numarası yalnızca sunucu kaydı gerçekten yazdığında (`201` ve kayıt numarası) gösterilir.
- **Tekrar göndermek güvenlidir:** her form doldurma bir gönderim anahtarı taşır. Cevap kaybolur ya da zaman aşımı olursa kayıt yazılmış olabilir, arayüz bunu dürüstçe söyler ("kaydedilmiş olabilir"). Aynı içerikle tekrar gönderince sunucu ikinci bir kayıt açmaz, ilk kaydı döndürür. Alan değişirse anahtar yenilenir, düzeltilmiş içerik kaybolmaz.
- Veri tabanı, uygulamayı atlayan bozuk bir kaydı da reddeder (`CHECK` kuralları). API yanıtları önbelleğe alınmaz. Bilinmeyen adresler düzgün bir 404 sayfası gösterir.

## Teknoloji

Node.js, Express 5, PostgreSQL, sade HTML/CSS/JS (framework yok). Hazır bir şablon kullanılmadı, tüm kod bu depoda yazıldı. Tek üçüncü taraf varlık, sunucudan yayınlanan Archivo yazı tipidir (SIL OFL 1.1, lisansı `public/fonts/OFL.txt`).

Veri tabanı iki modda çalışır ve SQL aynıdır:
- `DATABASE_URL` tanımlıysa PostgreSQL (canlı ortam).
- Tanımlı değilse gömülü PGlite (`.data/pglite` klasörüne yazar, yerel geliştirme için). Kayıtlar sunucu yeniden başlayınca da durur.

## Çalıştırma

Gereksinim: Node.js 20 veya üstü (Node 20, 22 ve 26'da 49 sunucu testinin tamamı geçti).

```bash
npm install
npm start                      # http://localhost:3000
```

Ortam değişkenleri (hepsi isteğe bağlı):

| Değişken | Anlamı |
|---|---|
| `PORT` | Dinlenecek port. Varsayılan 3000. |
| `DATABASE_URL` | PostgreSQL bağlantı adresi. Yoksa yerel PGlite kullanılır. |
| `ADMIN_TOKEN` | Tanımlıysa kayıtları `GET /api/requests` ucundan görmeyi sağlar. Tanımlı değilse bu uç hiç açılmaz. |

Kayıtları görmek için:

```bash
ADMIN_TOKEN=gizli-bir-deger npm start
curl -H "x-admin-token: gizli-bir-deger" http://localhost:3000/api/requests
```

## Test

```bash
npm test                       # 49 sunucu testi (node:test): API, güvenlik, çeviri bütünlüğü, kalıcılık, Postgres yolu, veri tabanı kuralları
npm run test:e2e               # 145 tarayıcı kontrolü (Chromium). Sunucuyu boş bir geçici veri klasörüyle kendisi başlatır ve kapatır
npm run test:all               # ikisi arka arkaya
```

Tarayıcı testleri için bir kerelik kurulum: `python3 -m pip install playwright && python3 -m playwright install chromium`. Test sonunda `shots/` klasörüne ekran görüntüleri yazar. GitHub Actions ile de çalışır (`.github/workflows/ci.yml`).

**Sunucu testleri:** geçerli ve geçersiz girdiler (sınır değerler dahil), kaydın gerçekten yazılması, SQL enjeksiyon denemesi, bozuk ve aşırı büyük gövde, veri tabanı hatasında başarı dönmemesi, hız sınırı, yönetici ucunun korunması, güvenlik başlıkları, tekrar gönderimin güvenli olması (gönderim anahtarı), veri tabanı düzeyindeki geçerlilik kuralları, API yanıtlarının önbelleğe alınmaması, 404 sayfası, çeviri bütünlüğü (eksik, boş ya da çevrilmemiş metin yakalanır), sunucunun kapatılıp açılınca kaydın yerinde durması, canlıda kullanılan Postgres yolunun gerçek Postgres protokolüyle sınanması, bağlantı kopunca sunucunun çökmemesi, canlıda `DATABASE_URL` yoksa açılmayı reddetmesi. Testler Node 20, 22 ve 26'da geçti.

**Tarayıcı testleri:** görünüm ve yatay taşma (320 ile 1920 px, üç dil), hatalı ve başarılı gönderim, sunucu hatası ve ağ kesintisinde başarı gösterilmemesi, cevap kaybolduğunda tekrar göndermenin ikinci kayıt açmaması, çift tıklama, klavye kullanımı, "hareketi azalt" modunda durağan sayfa, animasyonlar, dil değiştirme ve kalıcılığı, çevrilmiş hata mesajları, açılır dil menüsünün klavye ve odak davranışı, koyu tema ve iki temada da tüm metinlerin kontrastı, zemindeki lekelerin en koyu ve en parlak noktasında metin kontrastı, **axe-core ile erişilebilirlik denetimi (WCAG 2.2 AA ve en iyi uygulamalar, 13 farklı durum)**, erişilebilir isim, başlık sırası, dokunma hedefi boyutu, %200 metin büyütmede taşma ve içerik kaybı.

## Değerlendirme ölçütlerine göre kanıtlar

| Ölçüt | Nerede, neyle kanıtlı |
|---|---|
| Çalışan ürün ve gereksinimler | Landing page, form, sunucuda kalıcı kayıt: `public/`, `src/`. Canlı URL yukarıda. `npm run test:e2e` gerçek tarayıcıda uçtan uca doğrular |
| Kod, veri akışı, temel güvenlik | Tek kural dosyası hem tarayıcıda hem sunucuda (`public/validation.js`), parametreli sorgu, veri tabanı `CHECK` kuralları, tekrar gönderim güvenli (gönderim anahtarı), CSP + Helmet, hız sınırı, korumalı yönetici ucu, canlıda veri tabanı adresi zorunlu. Ayrıntı: "Güvenlik önlemleri" |
| AI ile üretim ve doğrulama | [AI_LOG.md](AI_LOG.md): araçlar, görev dağılımı, proje sahibinin gerçek talimatları, bulunan hatalar (kanıtlarıyla), sınanmayanlar |
| Kullanılabilirlik ve erişilebilirlik | axe-core: 13 durumda ihlal yok. Lighthouse (mobil): Erişilebilirlik 100. Klavye, odak, atlama bağlantısı, `prefers-reduced-motion`, iki tema ve üç dil, %200 büyütme, kontrast ölçümleri |
| Test, hata yönetimi ve teslim | 49 sunucu + 145 tarayıcı testi, CI, `render.yaml`, hata durumları (400, 429, 500, ağ, zaman aşımı), düzgün 404, bağlantı kopmasına dayanıklılık, README |

## Canlıya alma (GitHub + Render + Neon, ücretsiz planlar)

Planların güncel kotalarını ve koşullarını kendiniz de kontrol edin, bunlar sık değişir.

1. **Neon** ([neon.com](https://neon.com)): bir proje açın ve bağlantı adresini (`postgresql://...`) kopyalayın. Ücretsiz planda kayıtlar süresiz durur (Render'ın kendi ücretsiz Postgres'i 30 gün sonra silindiği için kullanılmaz).
2. **GitHub**: bu depoyu bir GitHub deposuna gönderin (`git remote add origin ...`, `git push -u origin main`).
3. **Render** ([render.com](https://render.com)): "New +" → "Blueprint" ile depoyu bağlayın. `render.yaml` uygulamayı kendisi kurar (Node web servisi, ücretsiz plan, `/healthz` sağlık kontrolü, `ADMIN_TOKEN` otomatik üretilir).
4. Render'ın istediği `DATABASE_URL` alanına Neon adresini yapıştırın.
5. Yayına alındıktan sonra formdan bir test kaydı gönderin, ardından Render panelinden `ADMIN_TOKEN` değerini alıp kaydı görün: `curl -H "x-admin-token: DEĞER" https://SERVİS.onrender.com/api/requests`.

**Canlıda `DATABASE_URL` yoksa uygulama bilerek açılmaz** (`NODE_ENV=production` iken). Aksi halde kayıtlar sessizce Render'ın geçici diskine yazılır ve servis yeniden başlayınca silinirdi.

**Ücretsiz Render planının sınırı:** 15 dakika istek almazsa servis uyur ve uyanması yaklaşık bir dakika sürer ([Render belgesi](https://render.com/docs/free)). Linki birine göstermeden önce bir kez açıp uyandırın.

**Sorun giderme:** Bağlantı hatası alırsanız Neon adresindeki `&channel_binding=require` parçasını silip yeniden deneyin.

## Bilinen eksikler

- **Gerçek Neon hesabına bağlanılmadı.** Canlıda kullanılan `pg` sürücüsü yolu, gömülü veri tabanı Postgres ağ protokolüyle sunularak gerçekten çalıştırıldı ve sınandı (tablo kurulumu, kayıt, bağlantı kopması ve geri gelmesi). Ancak Neon'a özgü kısımlar (SSL, `channel_binding`, boştayken uykuya geçme) canlıya alınınca ilk gerçek kayıtla doğrulanmalıdır.
- Rate limit bellekte tutulur. Tek sunuculuk bir kurulum için yeterlidir, birden fazla sunucuda paylaşılmaz.
- Aynı kişi aynı talebi tekrar gönderirse ikinci bir kayıt oluşur (tekilleştirme yok).
- Talep sonrası e-posta gönderilmez. Kayıt yalnızca veri tabanına yazılır.
- Ekran okuyucu ile elle test yapılmadı. Erişilebilirlik için etiketler, `aria-invalid`, hata bağlantıları, klavye akışı ve renk kontrastı hesaplandı (metinler WCAG AA üstünde).
- Çevirilerin dil bilgisi ve üslubu bir anadili konuşan tarafından okunmadı. Türkçe metin ana kaynaktır, İngilizce ve Almanca çeviriler yapay zekâ tarafından yazıldı ve otomatik olarak yalnızca bütünlük (eksik, boş ya da çevrilmemiş metin) yönünden sınandı.
- Sunucunun döndürdüğü hata mesajları Türkçedir. Tarayıcı bunları seçili dile kendisi çevirir.
- Safari ve Firefox'ta denenmedi, yalnızca Chromium.
