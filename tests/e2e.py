"""Tarayıcı (Chromium) uçtan uca testi. Çalıştırma: python3 tests/e2e.py [http://localhost:3111]
Sunucu önceden çalışıyor olmalı. Ekran görüntüleri shots/ klasörüne yazılır."""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3111"
SHOTS = os.path.join(os.path.dirname(__file__), "..", "shots")
os.makedirs(SHOTS, exist_ok=True)
failures = []


def check(label, condition):
    print(("GEÇTİ  " if condition else "KALDI  ") + label)
    if not condition:
        failures.append(label)


def settle(page):
    """Sayfayı baştan sona kaydırıp animasyonların bitmesini bekler, sonra en üste döner."""
    height = page.evaluate("document.documentElement.scrollHeight")
    for y in range(0, height, 350):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(120)
    page.locator(".chat").scroll_into_view_if_needed()
    page.wait_for_selector("body[data-chat-done='1']", timeout=15000)
    page.wait_for_timeout(1500)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(600)


def fill_valid(page):
    page.fill("#name", "Ayşe Demir")
    page.fill("#email", "ayse@ornek-sirket.com")
    page.select_option("#service", "sss-botu")
    page.fill("#message", "Günde yaklaşık 40 aynı soruya cevap veriyoruz, bunu azaltmak istiyoruz.")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # ---- Görünüm: masaüstü ve mobil, yatay taşma, konsol hataları
    for label, size in [("masaustu", (1280, 900)), ("tablet", (768, 1000)), ("mobil-360", (360, 740)), ("mobil-390", (390, 844))]:
        ctx = browser.new_context(viewport={"width": size[0], "height": size[1]})
        page = ctx.new_page()
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        settle(page)
        overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        check(f"{label}: yatay taşma yok", not overflow)
        check(f"{label}: konsol hatası yok", not errors)
        page.screenshot(path=f"{SHOTS}/{label}.png", full_page=True)
        ctx.close()

    # ---- Hatalı gönderim: boş form
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    page = ctx.new_page()
    posts = []
    page.on("request", lambda r: posts.append(r) if r.method == "POST" else None)
    page.goto(BASE)
    page.click("#submit-btn")
    check("boş form: 4 alan hatası görünür", page.locator(".error:visible").count() == 4)
    check("boş form: ilk hatalı alana odaklanır", page.evaluate("document.activeElement.id") == "name")
    check("boş form: sunucuya istek gitmez", len(posts) == 0)
    check("boş form: başarı mesajı yok", page.locator("#success").is_hidden())
    check("boş form: alanlarda aria-invalid var", page.locator("[aria-invalid='true']").count() == 4)
    page.screenshot(path=f"{SHOTS}/hata-mobil.png", full_page=True)

    # Hatalı e-posta
    page.fill("#name", "Ayşe Demir")
    page.fill("#email", "gecersiz")
    page.select_option("#service", "sss-botu")
    page.fill("#message", "Yeterince uzun bir mesaj yazıyorum burada.")
    page.click("#submit-btn")
    check("hatalı e-posta: yalnızca e-posta hatası", page.locator(".error:visible").count() == 1 and page.locator("#email-error").is_visible())
    page.fill("#email", "ayse@ornek.com")
    check("düzeltince hata kalkar", page.locator("#email-error").is_hidden())

    # ---- Başarılı gönderim
    page.click("#submit-btn")
    page.wait_for_selector("#success:not([hidden])")
    check("başarı: 201 ile kayıt numarası gösterilir", page.inner_text("#success-id").startswith("#"))
    check("başarı: form gizlenir", page.locator("#request-form").is_hidden())
    check("başarı: odak başarı kutusunda", page.evaluate("document.activeElement.id") == "success")
    page.screenshot(path=f"{SHOTS}/basari-mobil.png", full_page=True)
    page.click("#new-request")
    check("yeni talep: form temiz ve odak adda", page.input_value("#name") == "" and page.evaluate("document.activeElement.id") == "name")
    ctx.close()

    # ---- Sunucu 500 dönerse başarı gösterilmemeli
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    page = ctx.new_page()
    page.route("**/api/requests", lambda r: r.fulfill(status=500, content_type="application/json", body='{"error":"Talebiniz kaydedilemedi. Lütfen biraz sonra tekrar deneyin."}'))
    page.goto(BASE)
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#form-alert:not([hidden])")
    check("500: hata mesajı görünür", "kaydedilemedi" in page.inner_text("#form-alert"))
    check("500: başarı mesajı YOK", page.locator("#success").is_hidden())
    check("500: girilen bilgiler korunur", page.input_value("#name") == "Ayşe Demir")
    check("500: düğme tekrar kullanılabilir", page.locator("#submit-btn").is_enabled())
    page.screenshot(path=f"{SHOTS}/sunucu-hatasi-mobil.png", full_page=True)
    ctx.close()

    # ---- 200 ama id yok: başarı sayılmamalı
    ctx = browser.new_context()
    page = ctx.new_page()
    page.route("**/api/requests", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page.goto(BASE)
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#form-alert:not([hidden])")
    check("200 ama kayıt numarası yok: başarı gösterilmez", page.locator("#success").is_hidden())
    ctx.close()

    # ---- Ağ kesintisi
    ctx = browser.new_context()
    page = ctx.new_page()
    page.route("**/api/requests", lambda r: r.abort())
    page.goto(BASE)
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#form-alert:not([hidden])")
    check("ağ kesintisi: 'kaydedilmedi' mesajı, başarı yok", "kaydedilmedi" in page.inner_text("#form-alert") and page.locator("#success").is_hidden())
    ctx.close()

    # ---- Çift tıklama: tek istek
    ctx = browser.new_context()
    page = ctx.new_page()
    count = {"n": 0}

    def slow(route):
        count["n"] += 1
        page.wait_for_timeout(800)
        route.continue_()

    page.route("**/api/requests", slow)
    page.goto(BASE)
    fill_valid(page)
    page.click("#submit-btn")
    page.click("#submit-btn", force=True, no_wait_after=True)
    page.wait_for_selector("#success:not([hidden])")
    check("çift tıklama: sunucuya tek istek gider", count["n"] == 1)
    ctx.close()

    # ---- Klavye ile kullanım ve odak görünürlüğü
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(BASE)
    page.keyboard.press("Tab")
    check("klavye: ilk Tab atlama bağlantısına gider", page.evaluate("document.activeElement.className") == "skip")
    page.keyboard.press("Enter")
    page.wait_for_timeout(300)
    check("klavye: atlama bağlantısı forma götürür", page.evaluate("location.hash") == "#talep")
    ctx.close()

    # ---- Hareket: "hareketi azalt" açıkken her şey durağan ve hemen görünür
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    check("hareketi azalt: js-motion sınıfı yok", not page.evaluate("document.documentElement.classList.contains('js-motion')"))
    check("hareketi azalt: tüm konuşma satırları hemen görünür", page.evaluate("[...document.querySelectorAll('.msg')].every(m => getComputedStyle(m).opacity === '1')"))
    check("hareketi azalt: başlık kelimeleri yerinde", page.evaluate("[...document.querySelectorAll('.hero h1 .w > span')].every(s => getComputedStyle(s).transform === 'none')"))
    check("hareketi azalt: mühür baştan görünür", page.evaluate("getComputedStyle(document.querySelector('.stamp')).opacity") == "1")
    check("hareketi azalt: başlıklar, metin blokları ve iki sütun baştan görünür", page.evaluate("[...document.querySelectorAll('.reveal-title > span')].every(e => getComputedStyle(e).transform === 'none') && [...document.querySelectorAll('.rv, .split-col li, .services > div')].every(e => getComputedStyle(e).opacity === '1')"))
    check("hareketi azalt: leke tonu değişkenleri ayarlanmaz (zemin sabit)", page.evaluate("getComputedStyle(document.querySelector('.page-bg')).getPropertyValue('--c1').trim() === ''"))
    check("hareketi azalt: kaydırma çizgisi yok", page.evaluate("getComputedStyle(document.querySelector('.progress')).display") == "none")
    check("hareketi azalt: lekeler kapalı, zemin sabit sis rengi", page.evaluate("[...document.querySelectorAll('.blob')].every(b => getComputedStyle(b).display === 'none')") and page.evaluate("getComputedStyle(document.querySelector('.page-bg')).backgroundColor") == "rgb(230, 236, 232)" and page.evaluate("getComputedStyle(document.querySelector('.page-bg')).getPropertyValue('--p') === ''"))
    check("hareketi azalt: adım çizgileri tam görünür", page.evaluate("[...document.querySelectorAll('.steps li:not(:last-child)')].every(li => getComputedStyle(li, '::after').transform === 'none')"))
    ctx.close()

    # ---- Hareket açıkken: yazıyor durumu, fiş düşer, mühür basılır, adım çizgisi
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_selector(".msg.typing", timeout=10000)
    check("hareket: Kalfa 'yazıyor' durumu görünür", True)
    check("hareket: yazarken etiket görünür, metin gizli", page.evaluate("(() => { const m = document.querySelector('.msg.typing'); if (!m) return false; return getComputedStyle(m.querySelector('.who')).opacity !== '0' && getComputedStyle(m.querySelector('.txt')).color === 'rgba(0, 0, 0, 0)'; })()"))
    check("hareket: fiş ve mühür başta görünmez", page.evaluate("getComputedStyle(document.querySelector('.stamp')).opacity") == "0")
    page.screenshot(path=f"{SHOTS}/yaziyor.png", clip={"x": 560, "y": 0, "width": 720, "height": 900})
    page.wait_for_selector(".msg-note.show", timeout=20000)
    check("hareket: iş fişi düşer", True)
    page.wait_for_selector(".msg-note.stamped", timeout=5000)
    page.wait_for_timeout(600)
    check("hareket: mühür basılınca görünür", page.evaluate("getComputedStyle(document.querySelector('.stamp')).opacity") == "1")
    page.screenshot(path=f"{SHOTS}/muhur.png", clip={"x": 560, "y": 0, "width": 720, "height": 1000})
    page.wait_for_selector("body[data-chat-done='1']", timeout=20000)
    page.wait_for_timeout(700)
    check("hareket: konuşma bitince tüm satırlar görünür", page.evaluate("[...document.querySelectorAll('.msg')].every(m => getComputedStyle(m).opacity === '1' && !m.classList.contains('typing'))"))
    page.locator("#steps").scroll_into_view_if_needed()
    page.wait_for_timeout(2500)
    check("hareket: adım çizgisi çizilir", page.evaluate("document.getElementById('steps').classList.contains('in-view') && getComputedStyle(document.querySelector('.steps li'), '::after').transform !== 'matrix(1, 0, 0, 0, 0, 0)'"))
    ctx.close()

    # ---- Hareket açıkken: bölümler kaydırınca gelir, yeniden oynat, kaydırma çizgisi
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    check("kaydırma: başlangıçta iki sütun gizli", page.evaluate("[...document.querySelectorAll('.split-col li')].every(e => getComputedStyle(e).opacity === '0')"))
    check("kaydırma: kalfa'ya giden iş soldan (-28px), ustaya giden iş sağdan (+28px) başlar", page.evaluate("getComputedStyle(document.querySelector('.split-kalfa li')).transform === 'matrix(1, 0, 0, 1, -28, 0)' && getComputedStyle(document.querySelector('.split-usta li')).transform === 'matrix(1, 0, 0, 1, 28, 0)'"))
    check("kaydırma: başlangıçta üst çubukta gölge yok", not page.evaluate("document.querySelector('.site-header').classList.contains('is-scrolled')"))
    page.locator(".split-grid").scroll_into_view_if_needed()
    page.wait_for_timeout(2200)
    check("kaydırma: Kalfa'ya ve ustaya giden işler görünür", page.evaluate("document.querySelector('.split-grid').classList.contains('in-view') && [...document.querySelectorAll('.split-col li')].every(e => getComputedStyle(e).opacity === '1')"))
    check("kaydırma: kaydırınca üst çubukta gölge", page.evaluate("document.querySelector('.site-header').classList.contains('is-scrolled')"))
    page.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})")
    page.wait_for_timeout(500)
    check("kaydırma: sayfa sonunda ilerleme çizgisi dolu", float(page.evaluate("getComputedStyle(document.querySelector('.progress')).getPropertyValue('--p')")) > 0.95)
    check("kaydırma: sayfa sonunda ekran dışında kalan başlık henüz yükselmemiştir", page.evaluate("document.getElementById('form-title').getBoundingClientRect().bottom < 0 ? !document.getElementById('form-title').classList.contains('in-view') : true"))
    page.locator("#form-title").scroll_into_view_if_needed()
    page.wait_for_timeout(1300)
    check("kaydırma: form başlığı görünür alana gelince yükselir", page.evaluate("document.getElementById('form-title').classList.contains('in-view') && getComputedStyle(document.querySelector('#form-title > span')).transform === 'none'"))

    # Form açıklama ilerleme çizgisi
    page.fill("#message", "12345")
    check("ölçer: 5 karakterde yarısı dolu, henüz hedefte değil", page.evaluate("getComputedStyle(document.getElementById('message-meter')).getPropertyValue('--fill').trim()") == "0.500" and not page.evaluate("document.getElementById('message-meter').classList.contains('ok')"))
    page.fill("#message", "123456789012")
    check("ölçer: 10 karakteri geçince dolu ve yeşil", page.evaluate("getComputedStyle(document.getElementById('message-meter')).getPropertyValue('--fill').trim()") == "1.000" and page.evaluate("document.getElementById('message-meter').classList.contains('ok')"))
    page.fill("#message", "")
    check("ölçer: metin silinince boşalır", page.evaluate("getComputedStyle(document.getElementById('message-meter')).getPropertyValue('--fill').trim()") == "0.000")

    ctx.close()

    # ---- Süzülen renkli lekeler: kaydırmaya bağlı, sürekli, okunurluğu bozmayan
    import io
    from PIL import Image

    def luminance(c):
        c = [x / 255 for x in c]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(300)
    check("lekeler: dört leke görünür", page.evaluate("[...document.querySelectorAll('.blob')].length === 4 && [...document.querySelectorAll('.blob')].every(b => getComputedStyle(b).display === 'block')"))
    rect = lambda: page.evaluate("(() => { const r = document.querySelector('.b1').getBoundingClientRect(); return [r.left, r.top]; })()")
    pval = lambda: float(page.evaluate("getComputedStyle(document.querySelector('.page-bg')).getPropertyValue('--p')"))
    r_top, p_top = rect(), pval()
    page.evaluate("window.scrollTo({top: document.documentElement.scrollHeight * 0.5, behavior: 'instant'})")
    page.wait_for_timeout(250)
    r_mid, p_mid = rect(), pval()
    page.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})")
    page.wait_for_timeout(250)
    r_bot, p_bot = rect(), pval()
    check(f"lekeler: kaydırma oranı 0 → ~0,5 → 1 ({p_top:.2f}, {p_mid:.2f}, {p_bot:.2f})", p_top < 0.02 and 0.35 < p_mid < 0.65 and p_bot > 0.98)
    check("lekeler: sayfanın başı, ortası ve sonunda lekenin konumu farklı", len({tuple(round(v) for v in r) for r in (r_top, r_mid, r_bot)}) == 3)

    # Süreklilik: 40 px'lik adımlarda leke bir anda sıçramaz
    page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
    page.wait_for_timeout(200)
    height = page.evaluate("document.documentElement.scrollHeight - window.innerHeight")
    prev = rect(); jump = 0
    for y in range(40, height, 40):
        page.evaluate(f"window.scrollTo({{top: {y}, behavior: 'instant'}})")
        page.wait_for_timeout(30)
        cur = rect()
        jump = max(jump, abs(cur[0] - prev[0]), abs(cur[1] - prev[1]))
        prev = cur
    check(f"lekeler: 40 px'lik kaydırma adımlarında sıçrama yok (en büyük yer değişimi {jump:.0f} px)", jump <= 24)
    ctx.close()

    # Okunurluk: içeriği gizleyip yalnızca zemini ölçer. En koyu pikselde soluk metin (#46574F) en az 4,5 olmalı.
    muted_lum = luminance((0x46, 0x57, 0x4F))
    worst = 99.0
    for vw, vh in ((1280, 900), (390, 844)):
        ctx = browser.new_context(viewport={"width": vw, "height": vh})
        page = ctx.new_page()
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        page.evaluate("document.querySelectorAll('body > *:not(.page-bg)').forEach(e => e.style.setProperty('visibility', 'hidden', 'important'))")
        maxy = page.evaluate("document.documentElement.scrollHeight - innerHeight")
        for k in range(0, 21):
            page.evaluate(f"window.scrollTo({{top: {maxy * k / 20}, behavior: 'instant'}})")
            page.wait_for_timeout(90)
            im = Image.open(io.BytesIO(page.screenshot())).convert("RGB").resize((160, 90))
            lmin = min(luminance(c) for c in im.getdata())
            worst = min(worst, (max(lmin, muted_lum) + 0.05) / (min(lmin, muted_lum) + 0.05))
        ctx.close()
    check(f"lekeler: en koyu zemin noktasında soluk metin kontrastı {worst:.2f} (en az 4,5)", worst >= 4.5)

    # ---- Konuya göre leke tonu
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    c1 = lambda: page.evaluate("getComputedStyle(document.querySelector('.page-bg')).getPropertyValue('--c1').trim()")
    parse = lambda t: [float(x) for x in __import__('re').search(r"rgba\(([\d.]+),([\d.]+),([\d.]+)", t.replace(' ', '')).groups()]
    tones = {}
    for name, sel in (("hero", "#hero-title"), ("sorun", "#problem-title"), ("kim", "#split-title"), ("nasil", "#steps-title"), ("hizmet", "#services-title")):
        page.evaluate("document.querySelector('%s').scrollIntoView({behavior: 'instant', block: 'center'})" % sel)
        page.wait_for_timeout(200)
        tones[name] = c1()
    check(f"ton: beş konunun leke tonu birbirinden farklı ({len(set(tones.values()))} farklı değer)", len(set(tones.values())) == 5)

    # Süreklilik: 40 px'lik adımlarda ton bir anda sıçramaz
    page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
    page.wait_for_timeout(200)
    height = page.evaluate("document.documentElement.scrollHeight - window.innerHeight")
    prev = parse(c1()); worst = 0
    for y in range(40, height, 40):
        page.evaluate("window.scrollTo({top: %d, behavior: 'instant'})" % y)
        page.wait_for_timeout(30)
        cur = parse(c1())
        worst = max(worst, max(abs(a - b) for a, b in zip(prev[:3], cur[:3])))
        prev = cur
    check(f"ton: 40 px'lik kaydırma adımlarında ton sıçraması yok (en büyük kanal farkı {worst:.1f})", worst <= 12)

    # Beyaz alanlar sırıtmasın: tam genişlik bölümlerin hiçbiri düz beyaz zeminli olmamalı
    bgs = page.evaluate("[...document.querySelectorAll('main > section')].map(s => [s.className, getComputedStyle(s).backgroundColor])")
    white = [b for b in bgs if b[1] == 'rgb(255, 255, 255)']
    check(f"beyaz alan: hiçbir bölümün düz beyaz zemini yok ({'sorun yok' if not white else white})", not white)
    check("beyaz alan: 'Bir iş nasıl yürür' bölümü şeffaf, lekelerle bütünleşik", page.evaluate("getComputedStyle(document.querySelector('.how')).backgroundColor") == "rgba(0, 0, 0, 0)")
    ctx.close()

    # Kaldırılan denemeler geri gelmemiş olmalı
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    check("kaldırılanlar: yeniden oynat, yan gösterge, fiş ayracı ve perde yok", page.evaluate("document.querySelectorAll('.replay, .topics, .divider, .curtain').length") == 0)
    ctx.close()

    # Konuşma hızlı: sayfa açıldıktan sonra 6,5 saniye içinde biter
    import time
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    t0 = time.time()
    page.goto(BASE)
    page.wait_for_selector("body[data-chat-done='1']", timeout=15000)
    took = time.time() - t0
    check(f"konuşma hızı: {took:.1f} sn içinde bitti (en fazla 6,5)", took <= 6.5)
    ctx.close()

    # Açılışta yatay taşma yok: mühür başta 2 kat büyütülmüş ve görünmez bekler, taşma yaratmamalı
    worst_overflow = 0
    for vw, vh in ((320, 640), (360, 740), (390, 844)):
        ctx = browser.new_context(viewport={"width": vw, "height": vh})
        page = ctx.new_page()
        page.goto(BASE)
        for wait in (0, 300, 700, 1200, 1800, 2500, 3500):
            page.wait_for_timeout(wait if wait == 0 else 300)
            worst_overflow = max(worst_overflow, page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"))
        ctx.close()
    check(f"açılışta yatay taşma yok: 320/360/390 px, açılışın 7 farklı anında (en büyük taşma {worst_overflow} px)", worst_overflow == 0)

    # ---- Gönderirken düğmede şerit hareketi
    ctx = browser.new_context()
    page = ctx.new_page()
    def slow_ok(route):
        page.wait_for_timeout(900)
        route.continue_()
    page.route("**/api/requests", slow_ok)
    page.goto(BASE)
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_timeout(250)
    check("gönderirken: düğmede şerit hareketi ve devre dışı", page.evaluate("document.getElementById('submit-btn').classList.contains('is-sending')") and page.locator("#submit-btn").is_disabled())
    page.wait_for_selector("#success:not([hidden])")
    check("gönderince: şerit sınıfı kalkar", not page.evaluate("document.getElementById('submit-btn').classList.contains('is-sending')"))
    page.wait_for_timeout(1300)
    check("başarı kutusu fiş gibi basılır (sonunda tam görünür)", (lambda c: c == "none" or (c.startswith("inset(") and "100%" not in c))(page.evaluate("getComputedStyle(document.getElementById('success')).clipPath")))
    ctx.close()

    # ---- Başarı işareti gerçekten çiziliyor mu
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#success:not([hidden])")
    page.wait_for_timeout(1400)
    check("başarı işareti çizimi tamamlanır", page.evaluate("getComputedStyle(document.querySelector('.check-mark')).strokeDashoffset") in ("0px", "0"))
    page.screenshot(path=f"{SHOTS}/basari-masaustu.png")
    ctx.close()

    browser.close()

print()
print("SONUÇ:", "hepsi geçti" if not failures else f"{len(failures)} test kaldı")
sys.exit(1 if failures else 0)
