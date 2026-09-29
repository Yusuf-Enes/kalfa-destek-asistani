# Antre

Küçük işletmeler için kurgusal bir müşteri destek asistanı hizmetinin landing page'i ve talep formu. Ziyaretçinin talebi sunucuda kalıcı bir kayda dönüşür. Bu bir değerlendirme çalışmasıdır, yalnızca kurgusal test verisi kullanılmalıdır.

Sayfa hizmeti anlatır. Gerçek bir yapay zekâ ya da otomasyon çalışmaz, çalışan kısım talep formu ve kayıttır.

**Canlı URL:** _(yayına alındıktan sonra buraya eklenecek)_
**Teslim commit kimliği:** _(teslimde `git rev-parse HEAD` çıktısı buraya eklenecek)_

## Ne yapar

- Mobil ve masaüstünde çalışan tek sayfa: sorun, nasıl çalışır, hizmetler, talep formu. Marka kimliği (logo, renk paleti, yazı tipi, hareket kuralları) [BRAND.md](BRAND.md) dosyasındadır.
- Tek açılış sahnesi (kemer yükselir, başlık gelir, örnek konuşma yazılır), çizilen adım çizgisi ve kendini çizen başarı işareti. "Hareketi azalt" seçiliyse hareket kapanır.
- Form: ad, e-posta, hizmet seçimi, açıklama.
- Aynı doğrulama kuralları hem tarayıcıda hem sunucuda çalışır (`public/validation.js` tek dosyadır, ikisi de onu kullanır). İstemci doğrulaması yalnızca kolaylıktır, güvenlik sunucudadır.
- Gönderiliyor, başarı, alan hatası, sunucu hatası, zaman aşımı ve ağ kesintisi durumları ayrı ayrı ele alınır.
- Başarı mesajı ve talep numarası yalnızca sunucu kaydı gerçekten yazdığında (`201` ve kayıt numarası) gösterilir.

## Teknoloji

Node.js, Express 5, PostgreSQL, sade HTML/CSS/JS (framework yok). Hazır bir şablon kullanılmadı, tüm kod bu depoda yazıldı. Tek üçüncü taraf varlık, sunucudan yayınlanan Jost yazı tipidir (SIL OFL 1.1, lisansı `public/fonts/OFL.txt`).

Veri tabanı iki modda çalışır ve SQL aynıdır:
- `DATABASE_URL` tanımlıysa PostgreSQL (canlı ortam).
- Tanımlı değilse gömülü PGlite (`.data/pglite` klasörüne yazar, yerel geliştirme için). Kayıtlar sunucu yeniden başlayınca da durur.

## Çalıştırma

Gereksinim: Node.js 20 veya üstü.

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
npm test                       # 29 sunucu testi (node:test)
python3 tests/e2e.py           # 40 tarayıcı kontrolü, sunucu çalışırken
```

Tarayıcı testi için bir kerelik kurulum: `python3 -m pip install playwright && python3 -m playwright install chromium`. Test sonunda `shots/` klasörüne ekran görüntüleri yazar.

Sunucu testleri: geçerli ve geçersiz girdiler (sınır değerler dahil), kaydın gerçekten yazılması, SQL enjeksiyon denemesi, bozuk ve aşırı büyük gövde, veri tabanı hatasında başarı dönmemesi, hız sınırı, yönetici ucunun korunması, güvenlik başlıkları.
Tarayıcı testi: dört ekran genişliğinde yatay taşma ve konsol hatası, hatalı ve başarılı gönderim, sunucu 500 dönünce başarı mesajının çıkmaması, ağ kesintisi, çift tıklama, klavye ile kullanım, "hareketi azalt" modunda durağan sayfa, kemerin açılışı, Antre'nin "yazıyor" durumu, adım çizgisinin çizilmesi, başarı işaretinin çizilmesi.

## Güvenlik önlemleri

- Sunucuda zorunlu alan doğrulaması, izin verilen hizmet listesi, uzunluk sınırları, kontrol karakteri reddi.
- Parametreli SQL sorgusu.
- Helmet ile güvenlik başlıkları ve sıkı Content-Security-Policy (satır içi betik ve stil yok).
- `POST /api/requests` için IP başına dakikada 10 istek sınırı, gövde boyutu 10 KB sınırı.
- Kayıt listesi yönetici anahtarı olmadan kapalı. Anahtar sabit sürede karşılaştırılır.
- Hata durumunda istemciye iç hata mesajı verilmez, form içeriği loglanmaz.

## Canlıya alma (Render + Neon, ücretsiz planlar)

Planların güncel kotalarını kendiniz de kontrol edin.

1. Neon'da bir proje açın ve bağlantı adresini (`postgresql://...`) kopyalayın.
2. Kodu GitHub'a gönderin.
3. Render'da "New Web Service" ile depoyu bağlayın. Build komutu `npm install`, start komutu `npm start`.
4. Ortam değişkeni olarak `DATABASE_URL` (Neon adresi) ve isteğe bağlı `ADMIN_TOKEN` girin.
5. Yayına alındıktan sonra formdan bir test kaydı gönderin ve `GET /api/requests` ile görün.

Ücretsiz Render planında hizmet bir süre kullanılmazsa uyur. İlk açılış birkaç saniye yavaş olabilir.

## Bilinen eksikler

- Canlı Postgres (Neon) bağlantısı bu ortamda denenmedi. Yerelde aynı SQL, PGlite ile test edildi. `pg` sürücüsü yolu canlıya alındıktan sonra doğrulanmalıdır.
- Rate limit bellekte tutulur. Tek sunuculuk bir kurulum için yeterlidir, birden fazla sunucuda paylaşılmaz.
- Aynı kişi aynı talebi tekrar gönderirse ikinci bir kayıt oluşur (tekilleştirme yok).
- Talep sonrası e-posta gönderilmez. Kayıt yalnızca veri tabanına yazılır.
- Ekran okuyucu ile elle test yapılmadı. Erişilebilirlik için etiketler, `aria-invalid`, hata bağlantıları, klavye akışı ve renk kontrastı hesaplandı (metinler WCAG AA üstünde).
- Tasarım tek temalıdır. Sistem koyu tema tercihine göre değişmez.
- Safari ve Firefox'ta denenmedi, yalnızca Chromium.
