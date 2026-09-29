# Kalfa marka rehberi

## Fikir

Esnaf dükkânında **kalfa** günlük işlere bakar, zor bir işte **ustaya** danışır. Hizmet de tam olarak böyle çalışır: Kalfa (asistan) müşterilerin sık sorduğu sorulara yanıt verir, onay ya da özen gerektiren işleri **iş fişine** yazıp ustaya, yani işletme sahibine bırakır. Kurgusal bir hizmettir.

Marka kendi işini anlatır. Sayfadaki her görsel karar (dar ve kalın tabela yazısı, tezgâh yeşili, tırtıklı fiş, kırmızı mühür) hizmetin devir mantığından çıkar.

## Logo

**Simge:** Kalfa önlüğü. Boyun askısı, gövde, iki kısa bel bağı, etek ve cep. Bel bağları siluete önlük olduğunu söyletir, cep de işin (fişin) taşındığı yerdir. Simge yalnızca düz dolgu ve tek bir çizgiden oluşur, bu yüzden 16 piksele kadar okunur.

| Kullanım | Önlük (gövde, bağlar, askı) | Cep çizgisi |
|---|---|---|
| Açık zemin | Tezgâh yeşili `#1F4B3E` | Sis `#E6ECE8` |
| Koyu zemin (alt bilgi) | Açık `#EEF3F0` | Koyu tezgâh `#163A30` |

Cep çizgisi her zaman zeminin rengindedir, böylece cep önlükten "oyulmuş" görünür.

**Yazı:** "Kalfa", Archivo 800, dar genişlik (%78).

**Dosyalar:** `public/logo.svg` (simge), `public/favicon.svg` (sekme simgesi). Sayfadaki logolar satır içi SVG'dir, böylece renk bağlama göre CSS ile değişir. Üzerine gelince önlük hafifçe sallanır.

**Denenen ve elenenler:** Boyun çentikli dikdörtgen (küçükte plastik poşete benziyor), çan biçimli geniş etek (kettlebell ve el çantasına benziyor), uzun ince bel bağları (kollarını açmış bir figüre benziyor) ve cepten çıkan not (küçükte karışıyor). Seçilen biçim bunların hepsinden büyük ve küçük boyutta karşılaştırılarak seçildi.

**Kurallar:** Simgenin çevresinde en az simge genişliğinin yarısı kadar boşluk bırakın. Eğmeyin, gölge eklemeyin, renklerini bu tablo dışında değiştirmeyin. En küçük kullanım genişliği 16 px.

## Renk paleti

| Ad | Değer | Rol |
|---|---|---|
| Sis | `#E6ECE8` | Ana zemin |
| Sis koyu | `#D9E2DD` | İnce ayırıcılar |
| Fiş beyazı | `#FFFFFF` | Konuşma kartı, fiş, form, "Nasıl çalışır" bölümü |
| Tezgâh yeşili | `#1F4B3E` | Marka rengi: başlık, düğme, Kalfa balonu, form bölümü |
| Koyu tezgâh | `#163A30` | Alt bilgi, düğme üzerine gelme |
| Metin | `#17372E` | Metin (koyu tezgâh yeşili) |
| Soluk metin | `#46574F` | İkincil metin |
| Mühür kırmızısı | `#C4382B` | Yalnızca beyaz fişin üzerindeki "Ustaya devredildi" mührü |
| Hata | `#B3261E` | Yalnızca hata mesajları |

Renkler konudan gelir: tezgâh yeşili atölye makinelerinin boyasıdır, fiş beyazı kâğıt fiştir, kırmızı da mühür mürekkebidir. Lacivert ve sarı, krem ve toprak rengi, bordo ve kireç gibi genel kalıplar kullanılmadı.

### Kontrast (WCAG, hesaplanmış değerler)

| Çift | Oran |
|---|---|
| Metin / sis | 10,80 |
| Metin / beyaz | 12,94 |
| Soluk metin / sis | 6,41 |
| Soluk metin / beyaz | 7,67 |
| Soluk metin / sis koyu | 5,80 |
| Beyaz / tezgâh yeşili (düğme, Kalfa balonu) | 9,84 |
| Açık `#EEF3F0` / tezgâh yeşili (form bölümü, "Ustaya gider") | 8,77 |
| Açık soluk `#B9CCC2` / tezgâh yeşili | 5,85 |
| Açık soluk / koyu tezgâh (alt bilgi) | 7,42 |
| Tezgâh yeşili / sis (bağlantı, başlık) | 8,21 |
| Mühür kırmızısı / beyaz | 5,32 |
| Hata / beyaz | 6,54 |
| Form çerçevesi `#7C8C84` / beyaz (grafik için en az 3) | 3,53 |
| Mühür kırmızısı / sis | **4,44** (yetersiz, bu yüzden kırmızı yalnızca beyaz fişte kullanılır) |

## Yazı tipi

**Archivo**, tek aile, iki genişlik. Başlıklar dar ve kalın (genişlik %76, ağırlık 800), tabela yazısı gibi. Gövde normal genişlikte (400), vurgular 500 ve 600. Sunucudan yayınlanır (`public/fonts/`), Google'a istek atılmaz. Lisans: SIL Open Font License 1.1 (`public/fonts/OFL.txt`). Türkçe karakterler (ğ, ş, ı, İ) için `latin` ve `latin-ext` alt kümeleri yüklüdür.

Kaçınılan kalıplar: başlıkta tek kelimeyi vurgulamak, büyük harfli üst etiketler, aynı kartların tekrarı, gradyan yıkamalar.

## Düzen

Sola dayalı, geniş boşluklu. Yapı, kart yığını yerine ince çizgilerle ve işe uygun iki bileşenle kurulur:

- **İş fişi:** Kenarı tırtıklı, üstü tezgâh yeşili şeritli beyaz kâğıt. Hero'da ustaya bırakılan işi, sayfa sonunda talep formunu taşır.
- **Kim neye bakar:** İki sütun. Solda beyaz "Kalfa'ya gider", sağda yeşil "Ustaya gider". Hizmetin devir kuralı tek bakışta görülür.

Numara yalnızca gerçekten sıralı olan "Bir iş nasıl yürür" adımlarında vardır.

## Dil

Hizmetin diliyle konuşur: kalfa, usta, iş fişi, defter, tezgâh. Sade, somut ve saygılı. Eylemi adıyla söyler ("Talebi gönder"). Hata mesajı ne olduğunu ve ne yapılacağını söyler, özür dilemez. Övünmez, rakam uydurmaz. "Kalfa" marka adı olduğu için ek alırken kesme işareti kullanılır (Kalfa'ya, Kalfa'nın); "usta" genel ad olduğu için kullanılmaz (ustaya).

## Hareket

Sayfa açılırken tek bir sahne oynar ve bu sahne ürünün gerçek işini anlatır: başlık gelir, örnek konuşma oynar (Kalfa cevap yazarken önce "yazıyor" noktalarını gösterir), sonra **iş fişi yukarıdan düşer ve üstüne "Ustaya devredildi" mührü basılır**. Bunun dışında yalnızca bir eyleme cevap veren küçük hareketler vardır:

| Hareket | Ne anlatır |
|---|---|
| "Bir iş nasıl yürür" çizgisi kaydırınca çizilir | Sıralı bir süreç |
| Hizmet satırı üzerine gelince kayar, başlığı yeşile döner | Satırın seçilebildiği |
| Bağlantı altı çizgisi kalınlaşır | Tıklanabilirlik |
| Düğme basınca 1 px iner | Dokunmanın algılandığı |
| Başarı işareti çizilir | Kaydın gerçekten yapıldığı |

Kurallar: Yalnızca `transform` ve `opacity` animasyonlanır. `prefers-reduced-motion: reduce` seçiliyse hiçbir şey hareket etmez, fiş ve mühür baştan yerindedir. Hareket kodu hata verirse sayfa hareketsiz ve tam görünür kalır.
