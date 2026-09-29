# Destekçi marka rehberi

## Fikir

Destekçi, küçük işletmelerin müşteri sorularını yanıtlayan bir asistandır. Marka bir **konuşmayı** anlatır: kısa, net ve güven veren. Kurgusal bir hizmettir.

## Logo

**Simge:** "D" harfi biçiminde bir konuşma balonu. Balonun içindeki sarı nokta "cevap verildi" anlamına gelir. Simge, sola dayalı düz bir kenar ve sağda yuvarlak bir gövdeden oluşur, kuyruğu sol altta durur.

**Yazı:** "Destekçi" adı Bricolage Grotesque 800 ile yazılır, harf aralığı sıkıdır (-0.03em).

| Kullanım | Balon | Nokta |
|---|---|---|
| Açık zemin | Kobalt `#2540F0` | Güneş sarısı `#FFC93C` |
| Koyu zemin | Beyaz `#FFFFFF` | Kobalt `#2540F0` |

Neden ters çevrildi: kobalt, koyu lacivert üstünde yalnızca 2,58:1 kontrast verir. Bu yüzden koyu zeminde balon beyaz olur, nokta kobalt kalır (beyaz üstünde 6,84:1).

**Dosyalar:** `public/logo.svg` (simge), `public/favicon.svg` (sekme simgesi). Sayfadaki logo satır içi SVG'dir, böylece renkleri CSS ile değişir ve üzerine gelince nokta zıplar.

**Kurallar:** Simgenin çevresinde en az balon genişliğinin yarısı kadar boşluk bırakın. Simgeyi eğmeyin, gölge eklemeyin, renklerini bu tablo dışında değiştirmeyin. En küçük kullanım genişliği 16 px.

## Renk paleti

| Ad | Değer | Rol |
|---|---|---|
| Gece lacivert | `#0D1830` | Koyu zemin, ana metin |
| Kart lacivert | `#15224A` | Koyu zemindeki kartlar |
| Kobalt | `#2540F0` | Ana marka rengi, düğmeler, asistan balonları |
| Kobalt koyu | `#1B31C4` | Düğme üzerine gelme durumu |
| Güneş sarısı | `#FFC93C` | Vurgu: koyu zeminde düğme, ilerleme çubuğu, "devredildi" işareti |
| Sis | `#EEF1FB` | Açık zemin |
| Soluk metin | `#4A5578` | İkincil metin (açık zeminde) |
| Koyu zeminde soluk | `#B9C3E6` | İkincil metin (koyu zeminde) |
| Hata | `#B3261E` | Yalnızca hata mesajları |

### Kontrast (WCAG, hesaplanmış değerler)

| Çift | Oran | Kullanım |
|---|---|---|
| Beyaz / kobalt | 6,84 | Düğme, asistan balonu, şerit |
| Beyaz / kobalt koyu | 9,20 | Düğme üzerine gelme |
| Lacivert / sarı | 11,48 | Sarı düğme |
| Beyaz / lacivert | 17,64 | Koyu zemindeki metin |
| Koyu zemin soluk / lacivert | 10,09 | Koyu zemindeki ikincil metin |
| Lacivert / sis | 15,63 | Açık zemindeki metin |
| Soluk metin / sis | 6,50 | Açık zemindeki ikincil metin |
| Soluk metin / beyaz | 7,34 | Beyaz üzerinde ikincil metin |
| Hata / beyaz | 6,54 | Hata mesajı |
| Form çerçevesi `#7583A8` / beyaz | 3,77 | Alan çerçevesi (grafik için en az 3) |
| Kobalt / lacivert | **2,58** | **Metin için kullanılmaz.** Yalnızca dolgu olarak, üstüne beyaz yazıyla. |

## Yazı tipi

- **Başlıklar ve logo yazısı:** Bricolage Grotesque, ağırlık 700–800. Sunucudan yayınlanır (`public/fonts/`), Google'a istek atılmaz. Lisans: SIL Open Font License 1.1 (`public/fonts/OFL.txt`). Türkçe karakterler (ğ, ş, ı, İ) için `latin` ve `latin-ext` alt kümeleri yüklüdür.
- **Gövde metni:** Sistem yazı tipi. Hızlı yüklenir ve okunaklıdır.

## Ses

Sade, somut ve saygılı konuşur. Eylemi adıyla söyler ("Talebi gönder"). Hata mesajı ne olduğunu ve ne yapılacağını söyler, özür dilemez. Övünmez, rakam uydurmaz.

## Hareket

Hareket bir şey anlatıyorsa vardır:

| Hareket | Ne anlatır |
|---|---|
| Başlık kelime kelime yükselir | Sayfanın tek açılış anı |
| Asistan önce "yazıyor" noktalarını gösterir | Konuşmanın canlı olduğu |
| Adımların çizgisi çizilir, daireler sırayla dolar | Sıralı bir süreç |
| Soru şeridi akar | Müşterilerin gerçek soruları |
| Başarı işareti kendini çizer | Kaydın gerçekten yapıldığı |
| Düğme basınca tepki verir | Dokunmanın algılandığı |

Kurallar: Yalnızca `transform` ve `opacity` animasyonlanır. `prefers-reduced-motion: reduce` seçiliyse hiçbir şey hareket etmez ve her içerik hemen görünür. Akan şeritte "Akışı durdur" düğmesi vardır. Hareket kodu hata verirse sayfa hareketsiz ve tam görünür kalır.
