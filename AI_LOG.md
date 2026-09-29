# AI_LOG

Bu dosya, çalışmanın nasıl üretildiğini ve nasıl doğrulandığını anlatır. Yalnızca gerçekten yapılanlar yazılmıştır.

## Araçlar

- **Claude Code** (Anthropic, model: Claude Sonnet 5.5). Kod, testler, README ve bu günlük onunla üretildi. Kararları veren, yönlendiren ve sonucu inceleyen kişi proje sahibidir.
- **Skill'ler:** Anthropic'in resmi skill deposundan `frontend-design` ve `webapp-testing` kuruldu. Kurmadan önce içerikleri ve yardımcı script okundu. Makinede önceden kurulu olan `apple-design` ve `emil-design-eng` de mevcuttu.
- **Playwright (Chromium):** Tarayıcı testleri için.

## Görev dağılımı

- **Proje sahibi:** Hizmet fikrini seçti (Müşteri Destek Asistanı), teknoloji yığınını (Node.js + Express + Postgres + sade HTML/CSS/JS) ve canlı yayın yolunu (GitHub + Render + Neon) onayladı. İlk önerilen fikirleri beğenmeyip yapay zekâ ve otomasyon odaklı yeni seçenekler istedi.
- **Yapay zekâ:** Kodu yazdı, testleri yazıp çalıştırdı, ekran görüntülerini inceledi, hataları buldu ve düzeltti.

Çalışma "ekip toplantısı" yöntemiyle yürütüldü: yapay zekâ, karar aşamalarında farklı rollerin (güvenlik, veri tabanı, frontend, QA, DevOps) bakış açısıyla değerlendirme yaptı ve nedenini yazdı. Bunlar gerçek kişiler değil, tek bir modelin üstlendiği rollerdir.

## Önemli yönlendirmeler ve kararlar

| Konu | Öneri / karar | Sonuç |
|---|---|---|
| Veri tabanı | SQLite önerildi. Ardından ücretsiz barındırma diskinin geçici olabileceği ve "kalıcı kayıt" şartını riske attığı için Postgres'e geçildi. | Canlıda Postgres, yerelde aynı SQL ile gömülü PGlite. |
| Yerel veri tabanı | Makinede Postgres ve Docker yoktu. | PGlite ile aynı SQL yerelde çalıştırıldı. |
| Doğrulama | Kurallar tek dosyada (`public/validation.js`) yazıldı, tarayıcı ve sunucu aynı dosyayı kullanır. | İstemci ve sunucu birbirinden sapmaz. |
| Kayıt listeleme | Herkese açık liste yerine `ADMIN_TOKEN` ile korunan uç. Anahtar yoksa uç hiç açılmaz. | Değerlendirici kayıtları görebilir, başkası göremez. |
| Yapay zekâ çağrısı | Hizmet "yapay zekâ destekli" olsa da sayfada gerçek model çağrısı yok. | Görev bunu istemiyor. Maliyet, güvenlik ve hata yüzeyi eklemez. |
| Tasarım | `frontend-design` yönergesi izlendi: önce plan, sonra "şablon gibi mi" kontrolü. Krem/terracotta, büyük harfli üst etiketler, aynı kartların tekrarı ve başlıkta tek kelime vurgusu bilerek kullanılmadı. | Hero'da ürünün kendisi olan örnek konuşma var. |

## Doğrulama: neyi nasıl sınadık

- **Sunucu testleri (29, `npm test`):** Geçerli ve geçersiz girdiler, sınır değerler, kaydın gerçekten yazılması, SQL enjeksiyon denemesi, bozuk ve büyük gövde, veri tabanı hatasında başarı dönmemesi, hız sınırı, yönetici ucu, güvenlik başlıkları, formdaki hizmet listesinin sunucu listesiyle aynı olması.
- **Tarayıcı testleri (28, `tests/e2e.py`):** Dört ekran genişliğinde yatay taşma ve konsol hatası, hatalı ve başarılı gönderim, sunucu 500 dönünce ve yanıt kayıt numarası içermeyince başarı gösterilmemesi, ağ kesintisi, çift tıklamada tek istek, klavye akışı.
- **Kalıcılık:** Kayıt oluşturuldu, sunucu kapatılıp açıldı, kayıt yerinde duruyordu.
- **Testlerin gerçekten iş yaptığı:** Kod bilerek iki şekilde bozuldu. Mesaj alt sınırı 10'dan 1'e indirilince ilgili test kızdı. Başarı yanıtı kayıttan önce döndürülünce üç test kızdı. Kod geri alındı ve testler yeniden geçti.
- **Renk kontrastı:** Palet için WCAG oranları hesaplandı. Metin renkleri 4,5'in üzerinde (en düşük 5,61), form çerçevesi 3'ün üzerinde (3,43).
- **Bağımlılıklar:** `npm audit` sonucu 0 açık.
- **Ekran görüntüleri:** Masaüstü ve mobil görüntüler gözle incelendi.

## Süreçte bulunan gerçek hatalar

1. **Yerel veri tabanı klasörü oluşmuyordu.** Sunucu ilk çalıştırmada `.data/pglite` klasörü yok diye başlamadı. Testler bellekte çalıştığı için bunu yakalamamıştı, elle çalıştırınca ortaya çıktı. `mkdirSync` ile düzeltildi.
2. **Masaüstünde iki bölümün üst boşluğu yoktu.** Ekran görüntüsünde "Nasıl çalışır" ve "Talep oluşturun" başlıkları üstteki çizgiye yapışıktı. Sebep: masaüstü kuralındaki `.wrap { padding: 0 2rem }`, `.section` sınıfının üst boşluğunu sıfırlıyordu. Otomatik testler bunu yakalamadı. Yalnızca yatay boşluk ayarlanarak (`padding-inline`) düzeltildi, sonra görüntü yeniden incelendi.
3. Bir düzeltme denemesi sırasında macOS `sed` komutu hata verdi ve değişiklik uygulanmadı. Eski görüntüye bakıp düzeldi sanılmıştı. Sonuç görüntüsü yeniden üretilerek kontrol edildi ve düzeltme Edit aracıyla yapıldı.

## Sınanmayanlar

- Canlı Neon Postgres bağlantısı (`pg` sürücüsü yolu) bu ortamda denenmedi.
- Ekran okuyucu ile elle test yapılmadı.
- Safari ve Firefox'ta denenmedi, yalnızca Chromium.

## Süre

_(Proje sahibi: toplam harcanan süreyi buraya dürüstçe yaz.)_
