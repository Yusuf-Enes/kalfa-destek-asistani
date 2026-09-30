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


def pick_lang(page, code):
    """Dil menüsünü açar (kapalıysa) ve verilen dili seçer."""
    if page.get_attribute(".lang-toggle", "aria-expanded") != "true":
        page.click(".lang-toggle")
    page.click(f".lang-menu [data-lang='{code}']")


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

    # ---- Hareket açıkken: mesajlar peşpeşe gelir ("yazıyor" durumu yok), fiş düşer, mühür basılır
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.add_init_script("""
      window.__log = []; window.__typing = 0;
      document.addEventListener('DOMContentLoaded', () => {
        const t0 = performance.now();
        new MutationObserver(ms => ms.forEach(m => {
          const el = m.target;
          if (!el.classList) return;
          if (el.classList.contains('typing')) window.__typing++;
          if (el.classList.contains('msg') && el.classList.contains('show') && !el.__seen) { el.__seen = true; window.__log.push(Math.round(performance.now() - t0)); }
        })).observe(document.querySelector('.chat-log'), { attributes: true, subtree: true, attributeFilter: ['class'] });
      });
    """)
    page.goto(BASE)
    page.wait_for_selector(".msg-note.show", timeout=15000)
    check("hareket: fiş ve mühür başta görünmez", page.evaluate("getComputedStyle(document.querySelector('.stamp')).opacity") == "0")
    page.wait_for_selector(".msg-note.stamped", timeout=5000)
    page.wait_for_timeout(600)
    check("hareket: mühür basılınca görünür", page.evaluate("getComputedStyle(document.querySelector('.stamp')).opacity") == "1")
    page.screenshot(path=f"{SHOTS}/muhur.png", clip={"x": 560, "y": 0, "width": 720, "height": 1000})
    page.wait_for_selector("body[data-chat-done='1']", timeout=20000)
    page.wait_for_timeout(500)
    log = page.evaluate("window.__log")
    gaps = [b - a for a, b in zip(log, log[1:])]
    check(f"mesajlar: 5 satır sırayla belirdi ({len(log)} satır)", len(log) == 5)
    check("mesajlar: hiçbir satırda 'yazıyor' durumu oluşmadı", page.evaluate("window.__typing") == 0)
    check(f"mesajlar: peşpeşe geliyor, aralar en fazla 900 ms (aralar {gaps})", bool(gaps) and max(gaps) <= 900)
    check("mesajlar: HTML'de 'yazıyor' bileşeni kalmadı", page.evaluate("document.querySelectorAll('.typing').length") == 0)
    check("hareket: konuşma bitince tüm satırlar görünür", page.evaluate("[...document.querySelectorAll('.msg')].every(m => getComputedStyle(m).opacity === '1')"))
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

    # ================= ÇOK DİLLİLİK =================
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    snapshot = lambda: page.evaluate("Object.fromEntries([...document.querySelectorAll('[data-i18n]')].map((e, i) => [i, e.textContent]))")
    tr_before = snapshot()
    check("dil: varsayılan Türkçe (html lang, başlık, düğme etiketi ve kodu)", page.evaluate("document.documentElement.lang") == "tr" and "Müşteri destek asistanı" in page.title() and page.get_attribute(".lang-toggle", "aria-label") == "Dil: Türkçe" and page.inner_text(".lang-code") == "TR")

    pick_lang(page, 'en')
    page.wait_for_timeout(200)
    check("dil: İngilizce başlık, html lang, sayfa başlığı, düğme etiketi ve seçili öğe", page.inner_text("#hero-title").replace("\n", " ") == "Kalfa handles it, the master decides." and page.evaluate("document.documentElement.lang") == "en" and page.title() == "Kalfa · Customer support assistant" and page.get_attribute(".lang-toggle", "aria-label") == "Language: English" and page.inner_text(".lang-code") == "EN" and page.get_attribute(".lang-menu [data-lang='en']", "aria-current") == "true" and page.get_attribute(".lang-menu [data-lang='tr']", "aria-current") is None)
    check("dil: İngilizce menü, konuşma ve form", page.inner_text(".nav a") == "Who handles what" and "When will my order arrive" in page.inner_text(".chat-log") and page.inner_text("label[for='name']") == "Your name" and page.inner_text("#submit-btn") == "Send request")
    check("dil: seçim tarayıcıda saklanır", page.evaluate("localStorage.getItem('kalfa-lang')") == "en")
    page.reload(); page.wait_for_load_state("networkidle")
    check("dil: sayfa yenilenince seçilen dil korunur", page.evaluate("document.documentElement.lang") == "en" and page.inner_text("#submit-btn") == "Send request")

    pick_lang(page, 'de')
    page.wait_for_timeout(200)
    check("dil: Almanca başlık, seçenekler ve düğme", page.inner_text("#hero-title").replace("\n", " ") == "Kalfa kümmert sich, der Meister entscheidet." and page.inner_text("#service option:first-child") == "Leistung auswählen" and page.inner_text("#submit-btn") == "Anfrage senden" and page.evaluate("document.documentElement.lang") == "de")
    check("dil: başlık kelimeleri animasyon için yeniden bölünür", page.evaluate("document.querySelectorAll('#hero-title .w').length") == 6)

    pick_lang(page, 'tr')
    page.wait_for_timeout(200)
    check("dil: Türkçeye dönünce tüm metinler ilk hâlinin birebir aynısı", snapshot() == tr_before and page.evaluate("document.querySelectorAll('#hero-title .w').length") == 5)
    page.evaluate("localStorage.clear()")
    ctx.close()

    # ---- Dil seçici açılır menü olarak çalışır
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    check("menü: kapalıyken başlıkta yan yana dil düğmesi yok, tek düğme var", page.locator(".lang-menu").is_hidden() and page.locator(".lang [data-lang]:visible").count() == 0 and page.locator(".lang-toggle").is_visible() and page.get_attribute(".lang-toggle", "aria-expanded") == "false")
    page.click(".lang-toggle")
    check("menü: düğmeye basınca açılır", page.locator(".lang-menu").is_visible() and page.get_attribute(".lang-toggle", "aria-expanded") == "true")
    names = page.evaluate("[...document.querySelectorAll('.lang-menu button')].map(b => b.firstChild.textContent.trim())")
    check(f"menü: dil adları kendi dilinde ({names})", names == ["Türkçe", "English", "Deutsch"])
    check("menü: açılınca odak seçili dilin öğesinde", page.evaluate("document.activeElement.getAttribute('data-lang')") == "tr")
    page.keyboard.press("ArrowDown")
    check("menü: aşağı ok bir sonraki dile geçer", page.evaluate("document.activeElement.getAttribute('data-lang')") == "en")
    page.keyboard.press("ArrowDown"); page.keyboard.press("ArrowDown")
    check("menü: ok tuşları başa sarar", page.evaluate("document.activeElement.getAttribute('data-lang')") == "tr")
    page.keyboard.press("ArrowUp")
    check("menü: yukarı ok sona sarar", page.evaluate("document.activeElement.getAttribute('data-lang')") == "de")
    page.keyboard.press("Escape")
    check("menü: Escape menüyü kapatır ve odağı düğmeye döndürür", page.locator(".lang-menu").is_hidden() and page.evaluate("document.activeElement.className") == "lang-toggle" and page.get_attribute(".lang-toggle", "aria-expanded") == "false")
    page.click(".lang-toggle")
    page.mouse.click(300, 500)
    check("menü: dışarı tıklayınca kapanır", page.locator(".lang-menu").is_hidden())
    page.click(".lang-toggle")
    page.click(".lang-menu [data-lang='de']")
    check("menü: dil seçince menü kapanır, odak düğmeye döner, düğme yeni dili gösterir", page.locator(".lang-menu").is_hidden() and page.evaluate("document.activeElement.className") == "lang-toggle" and page.inner_text(".lang-code") == "DE" and page.get_attribute(".lang-toggle", "aria-label") == "Sprache: Deutsch" and page.evaluate("document.documentElement.lang") == "de")
    page.click(".lang-toggle")
    check("menü: seçili dil işaretli (aria-current) ve menü etiketi çevrilmiş", page.get_attribute(".lang-menu [data-lang='de']", "aria-current") == "true" and page.get_attribute(".lang-menu", "aria-label") == "Sprache")
    page.click(".lang-toggle")
    check("menü: düğmeye tekrar basınca kapanır", page.locator(".lang-menu").is_hidden())
    page.click(".lang-toggle")
    for _ in range(4):
        page.keyboard.press("Tab")
    page.wait_for_timeout(100)
    check("menü: odak menüden dışarı çıkınca menü kapanır", page.locator(".lang-menu").is_hidden())
    ctx.close()

    # Telefonda menü ekranın dışına taşmaz, en dar ekranda da açılır
    bad_fit = 0
    for vw, vh in ((320, 640), (360, 740), (390, 844)):
        ctx = browser.new_context(viewport={"width": vw, "height": vh})
        page = ctx.new_page()
        page.goto(BASE)
        page.click(".lang-toggle")
        box = page.evaluate("(() => { const r = document.getElementById('lang-menu').getBoundingClientRect(); return [r.left, r.right, document.documentElement.scrollWidth - document.documentElement.clientWidth]; })()")
        if box[0] < 0 or box[1] > vw or box[2] > 0: bad_fit += 1
        ctx.close()
    check("menü: 320/360/390 px'te menü ekran içinde, yatay taşma yok", bad_fit == 0)

    # Koyu temada menü koyu yüzeyde
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme="dark")
    page = ctx.new_page()
    page.goto(BASE)
    page.click(".lang-toggle")
    check("menü: koyu temada menü koyu yüzeyde", page.evaluate("getComputedStyle(document.getElementById('lang-menu')).backgroundColor") == "rgb(20, 35, 29)")
    ctx.close()

    # Adres parametresi seçimi geçersiz kılar, geçersiz değer yok sayılır
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(BASE + "/?lang=de")
    check("dil: ?lang=de adres parametresi Almancayı açar", page.evaluate("document.documentElement.lang") == "de" and page.inner_text("#submit-btn") == "Anfrage senden")
    ctx.close()
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(BASE + "/?lang=fr")
    check("dil: geçersiz ?lang=fr Türkçede kalır", page.evaluate("document.documentElement.lang") == "tr")
    ctx.close()

    # Doğrulama mesajları seçili dilde
    for lang, expected_name, expected_email in (("en", "Enter your name, between 2 and 80 characters.", "Enter a valid email address. Example: name@company.com"), ("de", "Geben Sie Ihren Namen mit 2 bis 80 Zeichen ein.", "Geben Sie eine gültige E-Mail-Adresse ein. Beispiel: name@firma.de")):
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto(BASE + "/?lang=" + lang)
        page.click("#submit-btn")
        check(f"{lang}: alan hataları seçili dilde", page.inner_text("#name-error") == expected_name and page.inner_text("#email-error") == expected_email)
        pick_lang(page, 'tr')
        page.wait_for_timeout(150)
        check(f"{lang}: dil değişince görünen hata metni yeni dilde yeniden yazılır", "Adınızı 2 ile 80" in page.inner_text("#name-error"))
        ctx.close()

    # Sunucu 400 dönerse mesaj seçili dilde, 500 ve ağ hataları seçili dilde
    ctx = browser.new_context()
    page = ctx.new_page()
    page.route("**/api/requests", lambda r: r.fulfill(status=400, content_type="application/json", body='{"errors":{"email":"Geçerli bir e-posta adresi yazın. Örnek: ad@sirket.com"}}'))
    page.goto(BASE + "/?lang=en")
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#form-alert:not([hidden])")
    check("en: sunucu 400 dönünce hata İngilizce gösterilir", page.inner_text("#email-error") == "Enter a valid email address. Example: name@company.com" and page.inner_text("#form-alert") == "Some fields need to be corrected.")
    ctx.close()
    ctx = browser.new_context()
    page = ctx.new_page()
    page.route("**/api/requests", lambda r: r.fulfill(status=500, content_type="application/json", body='{"error":"x"}'))
    page.goto(BASE + "/?lang=de")
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#form-alert:not([hidden])")
    check("de: sunucu 500 dönünce uyarı Almanca, başarı yok", "konnte nicht gespeichert" in page.inner_text("#form-alert") and page.locator("#success").is_hidden())
    pick_lang(page, 'en')
    page.wait_for_timeout(150)
    check("de→en: görünen genel uyarı dil değişince yeniden yazılır", "could not be saved" in page.inner_text("#form-alert"))
    ctx.close()
    ctx = browser.new_context()
    page = ctx.new_page()
    page.route("**/api/requests", lambda r: r.fulfill(status=429, content_type="application/json", body='{"error":"x"}'))
    page.goto(BASE + "/?lang=en")
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#form-alert:not([hidden])")
    check("en: 429 dönünce 'çok fazla deneme' uyarısı İngilizce", "Too many attempts" in page.inner_text("#form-alert"))
    ctx.close()

    # Gönderme ve başarı akışı seçili dilde
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(BASE + "/?lang=de")
    fill_valid(page)
    def slow_de(route):
        page.wait_for_timeout(700)
        route.continue_()
    page.route("**/api/requests", slow_de)
    page.click("#submit-btn")
    page.wait_for_timeout(200)
    check("de: gönderirken düğme 'Wird gesendet…'", page.inner_text("#submit-btn") == "Wird gesendet…")
    page.wait_for_selector("#success:not([hidden])")
    check("de: başarı mesajı Almanca ve kayıt numarası var", page.inner_text("#success h3") == "Ihre Anfrage wurde gespeichert" and page.inner_text("#success-id").startswith("#") and "Ihre Anfragenummer" in page.inner_text("#success"))
    ctx.close()

    # Üç dilde de en dar ekranlarda yatay taşma yok
    worst = 0
    for lang in ("tr", "en", "de"):
        for vw, vh in ((320, 640), (360, 740), (390, 844)):
            ctx = browser.new_context(viewport={"width": vw, "height": vh})
            page = ctx.new_page()
            page.goto(BASE + "/?lang=" + lang)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            worst = max(worst, page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"))
            ctx.close()
    check(f"dil: TR/EN/DE için 320/360/390 px'te yatay taşma yok (en büyük {worst} px)", worst == 0)

    # ================= KOYU TEMA =================
    def lum(c):
        c = [x / 255 for x in c]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

    def ratio(a, b):
        la, lb = lum(a), lum(b)
        return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

    eff = """(sel) => {
      const el = document.querySelector(sel); if (!el) return null;
      const parse = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); const p = m[1].split(',').map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
      const layers = []; let n = el;
      while (n && n.nodeType === 1 && n !== document.documentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c[3] > 0) layers.push(c); if (c[3] >= 1) break; n = n.parentElement; }
      let base = parse(getComputedStyle(document.querySelector('.page-bg')).backgroundColor).slice(0, 3);
      if (layers.length && layers[layers.length - 1][3] >= 1) base = layers.pop().slice(0, 3);
      for (const l of layers.reverse()) base = base.map((v, i) => l[3] * l[i] + (1 - l[3]) * v);
      return { fg: parse(getComputedStyle(el).color).slice(0, 3), bg: base };
    }"""
    TEXT = [".hero h1", ".lead", ".hero-copy .fine", ".nav a", ".lang-toggle", ".lang-menu button:not([aria-current='true'])", ".lang-menu [aria-current='true']", ".lang-menu .code",
            ".msg-customer .txt", ".msg-bot .txt", ".msg-customer .who", ".chat-caption", ".slip .who", ".slip-lines dt", ".slip-lines dd", ".stamp",
            ".statement h2", ".statement-body p", ".split h2", ".split-kalfa h3", ".split-kalfa li", ".split-usta h3", ".split-usta li", ".split-note",
            ".how h2", ".how-intro p", ".steps h3", ".steps p", ".services dt", ".services dd", ".form-intro h2", ".form-intro p", ".form-intro .fine",
            "label[for='name']", "#name", ".hint", "#submit-btn", ".site-footer p", ".site-footer .wordmark", ".btn-small"]
    theme_worst = {}
    for theme in ("light", "dark"):
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme=theme)
        page = ctx.new_page()
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        page.click("#submit-btn")   # hata mesajlarını görünür yap
        page.wait_for_timeout(200)
        check(f"tema: {theme} temada html data-theme='{theme}' ve düğme durumu doğru", page.evaluate("document.documentElement.getAttribute('data-theme')") == theme and page.get_attribute(".theme-toggle", "aria-pressed") == ("true" if theme == "dark" else "false"))
        bad = []
        low = (99, "")
        for sel in TEXT + [".error"]:
            r = page.evaluate(eff, sel)
            if not r:
                bad.append(f"{sel}: bulunamadı"); continue
            cr = ratio(r["fg"], r["bg"])
            if cr < low[0]: low = (cr, sel)
            if cr < 4.5: bad.append(f"{sel} {cr:.2f}")
        theme_worst[theme] = low
        check(f"tema: {theme} temada tüm metinler en az 4,5:1 (en düşük {low[0]:.2f}, {low[1]})", not bad)
        if bad: print("      okunmayanlar:", bad)
        field_r = page.evaluate("""(() => { const cs = getComputedStyle(document.querySelector('#name')); const p = c => c.match(/[\\d.]+/g).map(Number).slice(0, 3); return { border: p(cs.borderTopColor), bg: p(cs.backgroundColor) }; })()""")
        check(f"tema: {theme} temada form alanı çerçevesi en az 3:1 ({ratio(field_r['border'], field_r['bg']):.2f})", ratio(field_r["border"], field_r["bg"]) >= 3)
        ctx.close()

    # Tema düğmesi: değiştirir, saklar, yenilemede korur (işletim sistemi tercihine baskın)
    ctx = browser.new_context(color_scheme="dark")
    page = ctx.new_page()
    page.goto(BASE)
    check("tema: işletim sistemi koyuysa sayfa koyu açılır", page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark")
    dark_bg = page.evaluate("getComputedStyle(document.querySelector('.page-bg')).backgroundColor")
    page.click(".theme-toggle")
    page.wait_for_timeout(200)
    light_bg = page.evaluate("getComputedStyle(document.querySelector('.page-bg')).backgroundColor")
    check("tema: düğme temayı açığa çevirir, zemin rengi değişir ve tercih kaydedilir", page.evaluate("document.documentElement.getAttribute('data-theme')") == "light" and dark_bg == "rgb(14, 26, 22)" and light_bg == "rgb(230, 236, 232)" and page.evaluate("localStorage.getItem('kalfa-theme')") == "light" and page.get_attribute(".theme-toggle", "aria-pressed") == "false")
    check("tema: tarayıcı tema rengi (theme-color) temayla değişir", page.evaluate("document.querySelector('meta[name=theme-color]').getAttribute('content')") == "#E6ECE8")
    page.reload(); page.wait_for_load_state("networkidle")
    check("tema: yenilenince seçim (açık) işletim sistemi tercihine (koyu) baskın çıkar", page.evaluate("document.documentElement.getAttribute('data-theme')") == "light")
    page.click(".theme-toggle")
    check("tema: tekrar basınca koyu, meta rengi de koyu", page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark" and page.evaluate("document.querySelector('meta[name=theme-color]').getAttribute('content')") == "#0E1A16")
    ctx.close()

    # Koyu temada dil ve tema birlikte, hareketi azalt açıkken de çalışır
    ctx = browser.new_context(color_scheme="dark", reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(BASE + "/?lang=en")
    page.wait_for_load_state("networkidle")
    check("tema: koyu + İngilizce + hareketi azalt birlikte çalışır (zemin koyu, leke yok)", page.evaluate("getComputedStyle(document.querySelector('.page-bg')).backgroundColor") == "rgb(14, 26, 22)" and page.evaluate("[...document.querySelectorAll('.blob')].every(b => getComputedStyle(b).display === 'none')") and page.inner_text("#submit-btn") == "Send request")
    ctx.close()

    # Koyu temada lekelerin en parlak noktasında soluk metin (--muted) yine okunur olmalı
    worst_dark = 99.0
    for vw, vh in ((1280, 900), (390, 844)):
        ctx = browser.new_context(viewport={"width": vw, "height": vh}, color_scheme="dark")
        page = ctx.new_page()
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        muted = [int(x) for x in page.evaluate("getComputedStyle(document.querySelector('.hint')).color").replace('rgb(', '').replace(')', '').split(',')]
        page.evaluate("document.querySelectorAll('body > *:not(.page-bg)').forEach(e => e.style.setProperty('visibility', 'hidden', 'important'))")
        maxy = page.evaluate("document.documentElement.scrollHeight - innerHeight")
        for k in range(0, 21):
            page.evaluate(f"window.scrollTo({{top: {maxy * k / 20}, behavior: 'instant'}})")
            page.wait_for_timeout(90)
            im = Image.open(io.BytesIO(page.screenshot())).convert("RGB").resize((160, 90))
            lmax = max(luminance(c) for c in im.getdata())
            worst_dark = min(worst_dark, (luminance(muted) + 0.05) / (lmax + 0.05))
        ctx.close()
    check(f"tema: koyu temada lekelerin en parlak noktasında soluk metin kontrastı {worst_dark:.2f} (en az 4,5)", worst_dark >= 4.5)

    # ---- Başlık sayfa açılınca yeterince yukarıda, iade mesajı yeni metinle
    worst_top = 0
    for vw, vh in ((1280, 800), (1440, 900), (1920, 1080), (390, 844)):
        for lang in ("tr", "en", "de"):
            ctx = browser.new_context(viewport={"width": vw, "height": vh})
            page = ctx.new_page()
            page.goto(BASE + "/?lang=" + lang)
            page.wait_for_load_state("networkidle")
            top = page.evaluate("document.querySelector('h1').getBoundingClientRect().top")
            gap = top - page.evaluate("document.querySelector('.site-header').getBoundingClientRect().bottom")
            worst_top = max(worst_top, gap)
            ctx.close()
    check(f"başlık: 4 ekran boyutu ve 3 dilde üst çubuğun en fazla 80 px altında başlar (en büyük boşluk {worst_top:.0f} px)", worst_top <= 80)

    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    reply = page.inner_text(".chat-log .msg-bot:nth-of-type(4) .txt")
    check("mesaj: iade cevabı istenen Türkçe metin", reply == "İade talebinizi aldım. En kısa zamanda size geri dönüş sağlanacak.")
    check("mesaj: eski 'ustaya soruyorum' metni kalmadı", "ustaya soruyorum" not in page.inner_text(".chat-log"))
    pick_lang(page, "en")
    check("mesaj: İngilizce iade cevabı", "return request" in page.inner_text(".chat-log .msg-bot:nth-of-type(4) .txt") and "get back to you as soon as possible" in page.inner_text(".chat-log .msg-bot:nth-of-type(4) .txt"))
    pick_lang(page, "de")
    check("mesaj: Almanca iade cevabı", "Rückgabeanfrage erhalten" in page.inner_text(".chat-log .msg-bot:nth-of-type(4) .txt") and "so schnell wie möglich" in page.inner_text(".chat-log .msg-bot:nth-of-type(4) .txt"))
    ctx.close()

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
