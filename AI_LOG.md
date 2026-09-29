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
| Ad | Ad için iki liste sunuldu: önce açıklayıcı adlar (Yanıt, Yankı, Masa vb.), sonra proje sahibinin "farklı yaratıcı" isteği üzerine hikâyeli adlar (Kalfa, Ahtapot, Telsiz vb.). Proje sahibi **Kalfa**'yı seçti. | Marka adı Kalfa. |
| Tasarım, 1. sürüm | Turkuaz ve gri-yeşil, konuşma kartlı sade bir sayfa. | Sonra kaldırıldı. |
| Tasarım, 2. sürüm | Proje sahibi logo, palet ve animasyon istedi. Koyu lacivert, kobalt ve sarı palet, konuşma balonlu logo, akan soru şeridi ve ışık lekeleriyle yapıldı (ad: Destekçi). | Sonra kaldırıldı: yapay zekâ ve SaaS sayfalarında çok sık görülen bir kalıptı. |
| Tasarım, 3. sürüm | Proje sahibi "daha premium, klasik yapay zekâ tasarımından uzak, ad ve logo değişsin" dedi. Ad Antre (giriş holü), logo iç içe iki kemer, palet bordo ve kireç, yazı tipi Jost oldu. | Sonra kaldırıldı: proje sahibi "yaptığımız işle alakası olmayan bir tasarım" olduğunu söyledi. Bu doğruydu, kemer ve giriş holü fikri hizmetin işini göstermiyordu. |
| Tasarım, 4. sürüm (teslim) | Kalfa adıyla, hizmetin gerçek mantığı üzerinden yeniden tasarlandı: kalfa günlük işe bakar, zor işi iş fişiyle ustaya (işletme sahibine) devreder. Yapay zekâ önce `frontend-design` yönergesine göre bir plan yazdı ve planı "her sayfaya uyan şablon mu" sorusuyla gözden geçirdi. Logo kalfa önlüğü, palet tezgâh yeşili, sis ve fiş beyazı (mühür kırmızısı yalnızca fişte), yazı tipi Archivo (dar ve kalın başlıklar). Hero'da konuşma, ardından düşen iş fişi ve basılan mühür var. "Kim neye bakar" bölümü devir kuralını iki sütunla gösteriyor. | Ayrıntılar [BRAND.md](BRAND.md) içinde. |
| Logo | Proje sahibi logoyu "daha mantıklı ve estetik" istedi. Mevcut logo (çentikli dikdörtgen) küçük boyutta gerçekten plastik poşete ve pile benziyordu. Yapay zekâ önce dört adayı, sonra üç rafine adayı büyük, orta, 24 piksel ve koyu/açık zeminde yan yana çizip gözle karşılaştırdı. Elenenler: çan biçimli etek (kettlebell gibi), ince uzun bel bağları (kolları açık figür gibi), cepten çıkan not (küçükte karışık). | Seçilen: boyun askılı, kısa kalın bel bağlı önlük. Header, alt bilgi ve 16/32/64 piksel favicon'da kontrol edildi. |
| Animasyon | Proje sahibi sayfanın daha dinamik olmasını istedi. Önceki turda premium görünsün diye hareket bilerek kısılmıştı, bu sefer artırıldı ama her hareket hizmetin bir yanına bağlandı (devir yönü, sıra, en az uzunluk, kaydın yazılması). Otomatik döngü eklenmedi, onun yerine "Yeniden oynat" düğmesi kondu. Hareket azaltma, JavaScript hatası ve JavaScript'siz durumlarda içerik tam görünür kalır. | Ayrıntılar [BRAND.md](BRAND.md) içinde. |
| Font | Google Fonts'a bağlanmak yerine font dosyaları indirilip sunucudan yayınlandı. | CSP gevşemedi, dış istek yok, lisans (SIL OFL) depoda. |
| Hareket | Değerlendirme görsel süslemeye puan vermiyor, kullanılabilirlik ve erişilebilirliğe veriyor. Bu yüzden hareket az tutuldu, `prefers-reduced-motion` desteği ve hareket hata verirse durağan geri dönüş eklendi. | Tarayıcı testleri bunu sınıyor. |

## Doğrulama: neyi nasıl sınadık

- **Sunucu testleri (29, `npm test`):** Geçerli ve geçersiz girdiler, sınır değerler, kaydın gerçekten yazılması, SQL enjeksiyon denemesi, bozuk ve büyük gövde, veri tabanı hatasında başarı dönmemesi, hız sınırı, yönetici ucu, güvenlik başlıkları, formdaki hizmet listesinin sunucu listesiyle aynı olması.
- **Tarayıcı testleri (61 kontrol, `tests/e2e.py`):** Dört ekran genişliğinde yatay taşma ve konsol hatası, hatalı ve başarılı gönderim, sunucu 500 dönünce ve yanıt kayıt numarası içermeyince başarı gösterilmemesi, ağ kesintisi, çift tıklamada tek istek, klavye akışı. Son tasarımda ayrıca "hareketi azalt" modunda durağanlık (fiş ve mühür baştan yerinde), Kalfa'nın "yazıyor" durumu, fişin düşmesi ve mührün basılması, adım çizgisinin çizilmesi, başarı işaretinin çizilmesi, kalfa ve usta sütunlarının zıt yönlerden başlayıp yerine oturması, kaydırma çizgisi, üst çubuk gölgesi, açıklama ilerleme çizgisi, gönderirken şerit, başarı kutusunun basılması ve konuşmanın yeniden oynatılması sınanıyor.
- **Kalıcılık:** Kayıt oluşturuldu, sunucu kapatılıp açıldı, kayıt yerinde duruyordu.
- **Testlerin gerçekten iş yaptığı:** Kod bilerek iki şekilde bozuldu. Mesaj alt sınırı 10'dan 1'e indirilince ilgili test kızdı. Başarı yanıtı kayıttan önce döndürülünce üç test kızdı. Kod geri alındı ve testler yeniden geçti.
- **Renk kontrastı:** Her palet için WCAG oranları hesaplandı. Teslim edilen palette tüm metin çiftleri 4,5'in üzerinde (en düşük 5,32), form çerçevesi 3'ün üzerinde (3,53). Mühür kırmızısının açık zeminde 4,44 verdiği görüldü ve bu yüzden yalnızca beyaz fişin üzerinde kullanıldı. Değerlerin tam tablosu [BRAND.md](BRAND.md) içinde.
- **Bağımlılıklar:** `npm audit` sonucu 0 açık.
- **Ekran görüntüleri:** Masaüstü ve mobil görüntüler gözle incelendi.

## Süreçte bulunan gerçek hatalar

Hatalar hangi tasarım sürümünde bulunduysa oraya göre yazıldı. 2. sürümün kendisi sonra kaldırıldı, ama hatalardan çıkan dersler 3. sürümde uygulandı.

1. **Yerel veri tabanı klasörü oluşmuyordu.** Sunucu ilk çalıştırmada `.data/pglite` klasörü yok diye başlamadı. Testler bellekte çalıştığı için bunu yakalamamıştı, elle çalıştırınca ortaya çıktı. `mkdirSync` ile düzeltildi.
2. **1. sürümde masaüstünde iki bölümün üst boşluğu yoktu.** Ekran görüntüsünde başlıklar üstteki çizgiye yapışıktı. Sebep: masaüstü kuralındaki `padding: 0 2rem`, bölümün üst boşluğunu sıfırlıyordu. Otomatik testler bunu yakalamadı. `padding-inline` ile düzeltildi.
3. **2. sürümde "Nasıl çalışır" çizgisi başlıkların üstünden geçiyordu.** Ekran görüntüsünde başlıklar üstü çizili görünüyordu.
4. **2. sürümde akan şeritte "Akışı başlat" düğmesi çalışmıyordu.** Tarayıcı testi, ikinci tıklamadan sonra şeridin hâlâ durduğunu gösterdi. Sebep: düğme odakta kaldığı için `:focus-within` kuralı şeridi durdurmayı sürdürüyordu.
5. **3. sürümde başlıkta yetim kelime.** "Destek, küçük ekiplerin mesaisini yer." başlığı üç satıra bölünüp sonda "yer." tek başına kalıyordu. Ekran görüntüsünde fark edildi, `text-wrap: balance` ile düzeltildi.
6. **3. sürümde dış kemer çizgisinin tepesi üst çubuğa değip kesiliyordu.** Ekran görüntüsünde fark edildi, hero'ya üst boşluk verilerek düzeltildi. Kemer açılış animasyonunun kırpma alanı da dış çizgiyi kesmesin diye negatif kenar payıyla genişletildi.
7. **Tasarımın işle ilgisizliği (3. sürüm).** En önemli hata teknik değil, yönlendirmeydi: sayfa güzeldi ama müşteri desteğini anlatmıyordu. Proje sahibi bunu fark etti. Yapay zekâ kemeri "hizmetin devir mantığını anlatan bir eşik" diye önermişti, ama bu bağ sayfada okunmuyordu. Ders: bir görsel fikrin hizmetin işini gösterip göstermediği, estetik kadar kontrol edilmeli.
8. **4. sürümde (teslim) stil dosyası ilk yazımda reddedildi.** Araç, dosyanın arada Python ile değiştiğini söyleyip yazmayı reddetti. Yeni stiller uygulanmadan test koşulsaydı eski dosyayla sonuç yanıltıcı olurdu. Dosya yeniden okunup yazıldı ve ancak sonra testler çalıştırıldı.
9. **4. sürümde Türkçe yazım hatası.** "Kalfaya gider" ve "Kalfayı" yazımlarında marka adından sonra kesme işareti eksikti (Kalfa'ya, Kalfa'yı). Ekran görüntüsünde fark edildi, düzeltildi ve kural BRAND.md'ye yazıldı.
10. **Testin kendi hataları (kod değil).** Yeni hareket testlerinde üç kez test yanlış çıktı: geçiş animasyonu bitmeden ölçüm, yumuşak kaydırma bitmeden ölçüm ve tarayıcının `clip-path` değerini beklediğimden farklı biçimde (`inset(0% 0px 0px)`) döndürmesi. Her seferinde kodu değiştirmeden önce gerçek değer ölçülerek bunun testin hatası olduğu doğrulandı.
11. **Animasyon turunda kodda hata bulunmadı, testte üç yanlışlık bulundu.** (a) "Kalfa soldan, usta sağdan gelir" testi yalnızca son durumu ölçüyordu, yönleri değil. Yeniden yazılıp başlangıç durumları (-28px ve +28px) ölçüldü. (b) Yeniden oynat testinde kaba bir `or` ifadesi vardı, düzeltildi. (c) Sayfanın en altına atlayınca form başlığı yükselmedi. Önce kod hatası sanıldı, sonra başlığın ekranın 91 piksel üstünde kaldığı ve henüz görünmediği için yükselmediği ölçülerek doğrulandı. Başlığa kaydırınca yükseliyor, bu doğru davranıştı. Test buna göre düzeltildi.
12. Bir düzeltme denemesi sırasında macOS `sed` komutu hata verdi ve değişiklik uygulanmadı. Eski görüntüye bakıp düzeldi sanılmıştı. Görüntü yeniden üretilerek kontrol edildi ve düzeltme Edit aracıyla yapıldı.

## Sınanmayanlar

- Canlı Neon Postgres bağlantısı (`pg` sürücüsü yolu) bu ortamda denenmedi.
- Ekran okuyucu ile elle test yapılmadı.
- Safari ve Firefox'ta denenmedi, yalnızca Chromium.
- Animasyonların akıcılığı (kare hızı) düşük güçlü telefonlarda ölçülmedi. Ekran görüntüleri hareketin ortasından alınan karelerdir, gerçek akıcılığı yerine geçmez.

## Süre

_(Proje sahibi: toplam harcanan süreyi buraya dürüstçe yaz.)_
