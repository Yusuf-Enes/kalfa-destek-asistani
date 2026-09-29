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

**Açılış sahnesi:** Başlık tabela usulü aşağıdan yükselir, örnek konuşmanın mesajları peşpeşe gelir ("yazıyor" beklemesi yoktur), sonra **iş fişi yukarıdan düşer ve üstüne "Ustaya devredildi" mührü basılır**. Konuşma hızlıdır, toplam yaklaşık 3,5 saniye sürer. Tekrar oynatma düğmesi yoktur.

**Zemin:** Sayfanın arkasında sabit bir katman vardır. Dört yumuşak leke kaydırma oranına göre çapraz yönlerde kayar ve boyut değiştirir, her leke ayrıca çok yavaş kendi başına süzülür. **Lekelerin rengi hangi konuda olunduğuna göre sürekli ve yumuşak biçimde değişir**, böylece "başka bir konuya geçildi" hissi verir. Beş konunun tonu, yalnızca yeşil ailesinden ve doygunlukla ayrıştırılmış: hero nane `#8FDEB7`, "Dükkân açıkken telefon susmaz" sönük gri-yeşil `#B3D6BF`, "Kim neye bakar" canlı zümrüt-yeşil `#4DE6B3`, "Bir iş nasıl yürür" yumuşak nane-yeşil `#A1D9CB`, "Kalfa'yı üç yerde çalıştırabilirsiniz" taze yeşil `#6FE4A0` (her konudaki ilk lekenin rengi). Sarı ve sarımsı yeşil, camgöbeği ve mavi bilerek kullanılmaz: ton aralığı 136° ile 165° arasındadır. Renk değerleri `public/motion.js` içindeki `BLOB_PALETTES` dizisindedir. Tüm bölümlerin zemini şeffaftır, düz beyaz bant yoktur, böylece lekeler her yerde görünür.

**Kaydırırken:**

| Hareket | Ne anlatır |
|---|---|
| Her bölüm başlığı aşağıdan yükselir | Sayfanın tek sesi: tabela usulü |
| "Kim neye bakar": Kalfa'ya giden işler soldan, ustaya giden işler sağdan, sırayla gelir | Devir yönü ve sırası |
| Adım rakamları sırayla pop yapar, çizgi çizilir | Sıralı bir süreç |
| Hizmet satırları sırayla gelir, üzerine gelince kayar | Satırın seçilebildiği |
| Üstte ince kaydırma çizgisi, kaydırınca başlığa gölge | Sayfadaki konum |
| Zemindeki lekeler kaydırdıkça kayar, konuya göre ton değiştirir | Sayfada ilerlendiği ve konunun değiştiği |

**Formda:**

| Hareket | Ne anlatır |
|---|---|
| Açıklama kutusunun altındaki çizgi dolar, 10 karaktere ulaşınca yeşile döner | En az uzunluğa ulaşıldığı |
| Gönderirken düğmede şeritler akar | İşlemin sürdüğü |
| Başarı kutusu makineden çıkan fiş gibi basılır, onay işareti çizilir | Kaydın gerçekten yapıldığı |

**Küçük eylem geri bildirimleri:** Düğme basınca 1 px iner. Bağlantı altı çizgisi kalınlaşır. Fişin üzerine gelince fiş hafifçe kalkar. Logonun üzerine gelince önlük sallanır.

**Kurallar:** Yalnızca `transform`, `opacity` ve `clip-path` animasyonlanır (istisna: gönderirken düğmedeki şerit). `prefers-reduced-motion: reduce` seçiliyse hiçbir şey hareket etmez: fiş ve mühür baştan yerindedir, tüm bölümler hemen görünür, kaydırma çizgisi ve zemindeki lekeler kapalıdır, zemin sabit sis rengidir. Lekelerin en koyu noktasında bile soluk metnin kontrastı en az 4,5 olmak zorundadır ve bu, ekran görüntüsünden ölçülerek test edilir (ölçülen en düşük değer 4,73). Gizli başlangıç durumları yalnızca hareket açıkken geçerlidir. Hareket kodu hata verirse ya da JavaScript çalışmazsa sayfa hareketsiz ve tam görünür kalır.

## Koyu tema

Aynı değişken adları koyu değerler alır (`:root[data-theme="dark"]`). Tezgâh yeşili koyu zeminde **açık nane** olur (başlık, düğme, bağlantı, Kalfa balonu), yüzeyler koyu yeşile döner. Sayfa çizilmeden önce uygulanır, işletim sistemi tercihini izler, düğmeyle yapılan seçim saklanır.

| Ad | Açık tema | Koyu tema |
|---|---|---|
| Zemin | `#E6ECE8` | `#0E1A16` |
| Yüzey (kart, fiş, form kâğıdı) | `#FFFFFF` | `#14231D` |
| Metin | `#17372E` | `#E4EEE8` |
| Soluk metin | `#46574F` | `#A8BCB2` |
| Marka rengi | `#1F4B3E` | `#8FDEB7` (açık nane) |
| Marka rengi üzerindeki yazı | `#EEF3F0` | `#0B1611` |
| Koyu bant (form bölümü, "Ustaya gider") | `#1F4B3E` | `#163A30` |
| Alt bilgi | `#163A30` | `#08130F` |
| Mühür | `#C4382B` | `#FF8F80` |

Koyu temada zemindeki lekeler de koyu yeşile döner. Renkleri, arka planla karışınca en parlak noktada bile soluk metnin kontrastı en az 4,5 kalacak biçimde hesaplanmıştır (ölçülen en düşük değer 5,31). Her iki temada tüm metin çiftlerinin en az 4,5:1 olduğu tarayıcı testiyle sınanır (ölçülen en düşük: açıkta 5,32, koyuda 6,47).

## Diller

Türkçe (varsayılan), İngilizce ve Almanca. Türkçe metin HTML'in içindedir, çeviriler `public/i18n.js` içindeki sözlüktedir. Marka adı ve "Kalfa" her dilde aynı kalır. Usta ve kalfa benzetmesi dile göre uyarlanır: Türkçede usta, İngilizcede "the master", Almanca'da "der Meister" (Almanca'da usta-çırak geleneği doğal olarak "Geselle" ve "Meister" ikilisidir, ama burada marka adı Kalfa olduğu için yalnızca "Meister" kullanılır). Hata mesajları ve gönderme durumu da seçili dilde görünür.
