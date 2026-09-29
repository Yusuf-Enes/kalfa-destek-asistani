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

Her hareket hizmetin bir yanını anlatır. Abartı yoktur, çünkü değerlendirme görsel süslemeye değil kullanılabilirliğe puan verir.

**Açılış sahnesi:** Başlık tabela usulü aşağıdan yükselir, örnek konuşma oynar (Kalfa cevap yazarken önce "yazıyor" noktalarını gösterir), sonra **iş fişi yukarıdan düşer ve üstüne "Ustaya devredildi" mührü basılır**. Konuşma hızlıdır, toplam yaklaşık 4 saniye sürer. Tekrar oynatma düğmesi yoktur.

**Zemin:** Sayfanın arkasında sabit bir katman vardır. Yeşil tonlarında dört yumuşak leke (nane, adaçayı, açık teal, koyu nane) kaydırma oranına göre çapraz yönlerde kayar ve boyut değiştirir. Her leke ayrıca çok yavaş, kendi başına süzülür. Bu renkler bilerek marka yeşilinin etrafında tutulmuştur.

**Kaydırırken:**

| Hareket | Ne anlatır |
|---|---|
| Her bölüm başlığı aşağıdan yükselir | Sayfanın tek sesi: tabela usulü |
| "Kim neye bakar": Kalfa'ya giden işler soldan, ustaya giden işler sağdan, sırayla gelir | Devir yönü ve sırası |
| Adım rakamları sırayla pop yapar, çizgi çizilir | Sıralı bir süreç |
| Hizmet satırları sırayla gelir, üzerine gelince kayar | Satırın seçilebildiği |
| Üstte ince kaydırma çizgisi, kaydırınca başlığa gölge | Sayfadaki konum |
| Zemindeki lekeler kaydırdıkça kayar | Sayfada ilerlendiği, sayfanın canlı olduğu |

**Formda:**

| Hareket | Ne anlatır |
|---|---|
| Açıklama kutusunun altındaki çizgi dolar, 10 karaktere ulaşınca yeşile döner | En az uzunluğa ulaşıldığı |
| Gönderirken düğmede şeritler akar | İşlemin sürdüğü |
| Başarı kutusu makineden çıkan fiş gibi basılır, onay işareti çizilir | Kaydın gerçekten yapıldığı |

**Küçük eylem geri bildirimleri:** Düğme basınca 1 px iner. Bağlantı altı çizgisi kalınlaşır. Fişin üzerine gelince fiş hafifçe kalkar. Logonun üzerine gelince önlük sallanır.

**Kurallar:** Yalnızca `transform`, `opacity` ve `clip-path` animasyonlanır (istisna: gönderirken düğmedeki şerit). `prefers-reduced-motion: reduce` seçiliyse hiçbir şey hareket etmez: fiş ve mühür baştan yerindedir, tüm bölümler hemen görünür, kaydırma çizgisi ve zemindeki lekeler kapalıdır, zemin sabit sis rengidir. Lekelerin en koyu noktasında bile soluk metnin kontrastı en az 4,5 olmak zorundadır ve bu, ekran görüntüsünden ölçülerek test edilir (ölçülen en düşük değer 4,77). Gizli başlangıç durumları yalnızca hareket açıkken geçerlidir. Hareket kodu hata verirse ya da JavaScript çalışmazsa sayfa hareketsiz ve tam görünür kalır.
