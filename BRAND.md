# Antre marka rehberi

## Fikir

**Antre**, bir binanın giriş holü demektir. Hizmet de tam olarak bunu yapar: müşteriyi kapıda karşılar, sık sorulan sorulara yanıt verir, özen ya da onay gerektiren konuları içeri, ekibe taşır. Kurgusal bir hizmettir.

Marka bir **eşiği** anlatır. Bu yüzden tek görsel dil kemerdir (kapı açıklığı). Sayfadaki tek yuvarlak biçim kemerdir, geri kalan her şey köşelidir (köşe yarıçapı 2 px).

## Logo

**Simge:** İç içe iki kemer ve bir zemin çizgisi. Dıştaki ince çizgiyle çizilmiş bir kapı açıklığı, içteki dolu kemer o kapıda duran kişidir.

| Kullanım | Renk |
|---|---|
| Açık zemin | Bordo `#6A1B31` |
| Bordo zemin (kemer içinde) | Gül `#D9C2C7` |
| Koyu bordo zemin (alt bilgi) | Kâğıt `#F7F7F4` |

**Yazı:** "Antre", Jost 500, harf aralığı +0.01em.

**Dosyalar:** `public/logo.svg` (simge), `public/favicon.svg` (sekme simgesi). Sayfadaki logolar satır içi SVG'dir, böylece rengi bağlama göre CSS ile değişir. Üzerine gelince iç kemer hafifçe yükselir (kapı aralanır).

**Kurallar:** Simgenin çevresinde en az simge genişliği kadar boşluk bırakın. Eğmeyin, gölge eklemeyin, dolgusunu değiştirmeyin. En küçük kullanım genişliği 16 px.

## Renk paleti

| Ad | Değer | Rol |
|---|---|---|
| Kireç | `#E9EAE6` | Ana zemin |
| Kireç koyu | `#DEDFDA` | Form bölümü zemini |
| Kâğıt | `#F7F7F4` | Yüzeyler (form paneli, "Nasıl çalışır" bölümü) |
| Şarap mürekkebi | `#26121A` | Metin |
| Bordo | `#6A1B31` | Marka rengi: kemer, düğme, bağlantı |
| Koyu bordo | `#4A1122` | Alt bilgi, düğme üzerine gelme |
| Gül | `#D9C2C7` | Bordo zeminde ikincil metin |
| Soluk metin | `#5E5459` | İkincil metin |
| Hata | `#A8261D` | Yalnızca hata mesajları |

Renk seçimi bilinçlidir: koyu lacivert ve sarı, krem ve toprak rengi, siyah ve canlı yeşil gibi yapay zekâ ve SaaS sayfalarında sık görülen ikililer kullanılmadı. Bordo ve kireç, otel ve özel kulüp dünyasından gelir.

### Kontrast (WCAG, hesaplanmış değerler)

| Çift | Oran |
|---|---|
| Metin / kireç | 14,68 |
| Metin / kâğıt | 16,53 |
| Metin / kireç koyu | 13,24 |
| Soluk metin / kireç | 6,02 |
| Soluk metin / kâğıt | 6,77 |
| Soluk metin / kireç koyu | 5,43 |
| Bordo / kireç (bağlantı, başlık numaraları) | 9,58 |
| Kâğıt / bordo (düğme, Antre satırları) | 10,79 |
| Gül / bordo (etiketler) | 6,89 |
| Gül-yumuşak `#ECDDE0` / bordo (müşteri satırları) | 8,81 |
| Gül / koyu bordo (alt bilgi) | 8,96 |
| Hata / kâğıt | 6,61 |
| Hata / hata zemini | 6,18 |
| Form çerçevesi `#8A8083` / kâğıt (grafik için en az 3) | 3,56 |

## Yazı tipi

**Jost**, tek aile. Geometrik ve sakin, kemer biçimiyle uyumlu. Başlıklar büyük ve ince (300), gövde normal (400), vurgular 500. Sunucudan yayınlanır (`public/fonts/`), Google'a istek atılmaz. Lisans: SIL Open Font License 1.1 (`public/fonts/OFL.txt`). Türkçe karakterler (ğ, ş, ı, İ) için `latin` ve `latin-ext` alt kümeleri yüklüdür.

Kaçınılan kalıplar: başlıkta tek kelimeyi vurgulamak, büyük harfli üst etiketler, aynı kartların tekrarı, gradyan yıkamalar.

## Düzen

Sola dayalı, asimetrik, bol boşluklu. Bölümler iki sütundur: solda başlık, sağda içerik. Yapı, kart yerine ince çizgilerle kurulur. Numara yalnızca gerçekten sıralı olan "Nasıl çalışır" adımlarında vardır.

Tek çarpıcı öğe hero'daki bordo kemerdir. İçinde örnek konuşma, balonlarla değil düzgün dizilmiş bir yazışma metni olarak akar. Kemerin etrafındaki ince dış çizgi, logonun iç içe kemerlerini sayfaya taşır.

## Ses

Sade, somut ve saygılı konuşur. Eylemi adıyla söyler ("Talebi gönder"). Hata mesajı ne olduğunu ve ne yapılacağını söyler, özür dilemez. Övünmez, rakam uydurmaz.

## Hareket

Sayfa açılırken tek bir sahne oynar: kemer aşağıdan yükselir, başlık kelime kelime gelir, ardından konuşma başlar ve Antre cevap yazarken önce "yazıyor" noktalarını gösterir. Bunun dışında yalnızca bir eyleme cevap veren küçük hareketler vardır:

| Hareket | Ne anlatır |
|---|---|
| "Nasıl çalışır" çizgisi kaydırınca çizilir | Sıralı bir süreç |
| Hizmet satırı üzerine gelince kayar, başlığı bordoya döner | Satırın seçilebildiği |
| Bağlantı altı çizgisi kalınlaşır | Tıklanabilirlik |
| Düğme basınca 1 px iner | Dokunmanın algılandığı |
| Başarı işareti: önce kemer çizilir, sonra onay | Kaydın gerçekten yapıldığı |

Kurallar: Yalnızca `transform`, `opacity` ve `clip-path` animasyonlanır. `prefers-reduced-motion: reduce` seçiliyse hiçbir şey hareket etmez ve her içerik hemen görünür. Hareket kodu hata verirse sayfa hareketsiz ve tam görünür kalır.
