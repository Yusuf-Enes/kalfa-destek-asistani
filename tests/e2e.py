"""Tarayıcı (Chromium) uçtan uca testi. Çalıştırma: python3 tests/e2e.py [http://localhost:3111]
Sunucu önceden çalışıyor olmalı. Ekran görüntüleri shots/ klasörüne yazılır."""
import json
import os
import sys
import urllib.request
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


def admin_list():
    """Sunucudaki kayıtları yönetici anahtarıyla okur (kalıcı kaydın gerçekten yazıldığını doğrulamak için)."""
    req = urllib.request.Request(BASE + "/api/requests", headers={"x-admin-token": os.environ.get("ADMIN_TOKEN", "yerel-deneme")})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())["requests"]


def max_id():
    rows = admin_list()
    return max((int(r["id"]) for r in rows), default=0)


def new_since(base):
    """Verilen numaradan sonra oluşan kayıt sayısı. Yönetici listesi yalnızca son 50 kaydı verdiği için toplam sayı değil numara karşılaştırılır."""
    return len([r for r in admin_list() if int(r["id"]) > base])


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
    check("ağ kesintisi: 'kaydedilmiş olabilir, tekrar göndermek güvenli' mesajı, başarı yok", "kaydedilmiş olabilir" in page.inner_text("#form-alert") and "güvenlidir" in page.inner_text("#form-alert") and page.locator("#success").is_hidden())
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
    check("dil: varsayılan Türkçe (html lang, başlık, düğme etiketi ve kodu)", page.evaluate("document.documentElement.lang") == "tr" and "Müşteri destek asistanı" in page.title() and page.get_attribute(".lang-toggle", "aria-label") == "TR, Dil: Türkçe" and page.inner_text(".lang-code") == "TR")

    pick_lang(page, 'en')
    page.wait_for_timeout(200)
    check("dil: İngilizce başlık, html lang, sayfa başlığı, düğme etiketi ve seçili öğe", page.inner_text("#hero-title").replace("\n", " ") == "Kalfa handles it, the master decides." and page.evaluate("document.documentElement.lang") == "en" and page.title() == "Kalfa · Customer support assistant" and page.get_attribute(".lang-toggle", "aria-label") == "EN, Language: English" and page.inner_text(".lang-code") == "EN" and page.get_attribute(".lang-menu [data-lang='en']", "aria-current") == "true" and page.get_attribute(".lang-menu [data-lang='tr']", "aria-current") is None)
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
    check("menü: dil seçince menü kapanır, odak düğmeye döner, düğme yeni dili gösterir", page.locator(".lang-menu").is_hidden() and page.evaluate("document.activeElement.className") == "lang-toggle" and page.inner_text(".lang-code") == "DE" and page.get_attribute(".lang-toggle", "aria-label") == "DE, Sprache: Deutsch" and page.evaluate("document.documentElement.lang") == "de")
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

    # ================= ERİŞİLEBİLİRLİK DENETİMİ (axe-core) =================

    AXE = os.path.join(os.path.dirname(__file__), "..", "node_modules", "axe-core", "axe.min.js")
    TAGS = '["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa","best-practice"]'

    def axe_violations(page):
        page.add_script_tag(path=AXE)
        res = page.evaluate("axe.run(document, {runOnly: {type: 'tag', values: %s}})" % TAGS)
        return [(v["id"], v["nodes"][0]["target"][0] if v["nodes"] else "?") for v in res["violations"]]

    axe_bad = []
    axe_states = 0
    for theme in ("light", "dark"):
        for lang in ("tr", "en", "de"):
            ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme=theme, bypass_csp=True)
            page = ctx.new_page()
            page.goto(BASE + "/?lang=" + lang)
            page.wait_for_load_state("networkidle")
            page.wait_for_selector("body[data-chat-done='1']", timeout=20000)
            page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            page.wait_for_timeout(1500)
            axe_states += 1
            axe_bad += [(f"{theme}/{lang}/sayfa",) + v for v in axe_violations(page)]
            if lang == "tr":
                page.click("#submit-btn"); page.wait_for_timeout(250)
                axe_states += 1
                axe_bad += [(f"{theme}/{lang}/hata durumu",) + v for v in axe_violations(page)]
                page.click(".lang-toggle"); page.wait_for_timeout(250)
                axe_states += 1
                axe_bad += [(f"{theme}/{lang}/açık dil menüsü",) + v for v in axe_violations(page)]
            ctx.close()
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, bypass_csp=True)
    page = ctx.new_page()
    page.goto(BASE); page.wait_for_load_state("networkidle")
    # Telefonda konuşma ekranın altında başlar. Belirme animasyonu sürerken ölçülürse renkler yarı saydamdır ve
    # axe kontrastı yanlış hesaplar (4 denemenin 3'ünde sahte ihlal), bu yüzden konuşmanın bitmesi beklenir.
    page.locator(".chat").scroll_into_view_if_needed()
    page.wait_for_selector("body[data-chat-done='1']", timeout=20000); page.wait_for_timeout(900)
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"); page.wait_for_timeout(1500)
    axe_states += 1
    axe_bad += [("mobil",) + v for v in axe_violations(page)]
    ctx.close()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, bypass_csp=True)
    page = ctx.new_page()
    page.goto(BASE); page.wait_for_load_state("networkidle")
    fill_valid(page); page.click("#submit-btn"); page.wait_for_selector("#success:not([hidden])"); page.wait_for_timeout(1200)
    axe_states += 1
    axe_bad += [("başarı durumu",) + v for v in axe_violations(page)]
    ctx.close()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, bypass_csp=True)
    page = ctx.new_page()
    page.goto(BASE + "/yok-boyle-bir-sayfa"); page.wait_for_load_state("networkidle")
    axe_states += 1
    axe_bad += [("404 sayfası",) + v for v in axe_violations(page)]
    ctx.close()
    check(f"erişilebilirlik (axe, WCAG 2.2 AA + en iyi uygulamalar): {axe_states} durumda ihlal yok" + (f" | İHLALLER: {axe_bad[:6]}" if axe_bad else ""), not axe_bad)

    # WCAG 2.5.3 (Label in Name): görünen metin erişilebilir isimde geçmeli
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE); page.wait_for_load_state("networkidle")
    mism = page.evaluate("""[...document.querySelectorAll('a[aria-label], button[aria-label]')].filter(e => {
      const vis = (e.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase();
      return vis && !e.getAttribute('aria-label').toLowerCase().includes(vis); }).map(e => e.className || e.tagName)""")
    check(f"erişilebilirlik: görünen metin erişilebilir isimde geçiyor (Label in Name) {mism or ''}", not mism)

    # Başlık sırası atlamaz, sayfada tek h1 var, ana yapı işaretli
    hs = page.evaluate("[...document.querySelectorAll('h1,h2,h3')].map(h => +h.tagName[1])")
    jumps = [(a, b) for a, b in zip(hs, hs[1:]) if b - a > 1]
    check(f"erişilebilirlik: tek h1 var, başlık seviyeleri atlamıyor ({hs.count(1)} adet h1)", hs.count(1) == 1 and not jumps)
    check("erişilebilirlik: header, nav, main, footer yer işaretleri var", page.evaluate("['header', 'nav', 'main', 'footer'].every(t => document.querySelector(t))"))

    # Dokunma hedefleri en az 24x24 CSS piksel (WCAG 2.2, 2.5.8)
    small = page.evaluate("""[...document.querySelectorAll('button, a.btn, .nav a, input, select, textarea, .skip')].filter(e => {
      const r = e.getBoundingClientRect(); return r.width > 0 && (r.width < 24 || r.height < 24); }).map(e => e.className || e.id || e.tagName)""")
    check(f"erişilebilirlik: tüm düğme ve alanlar en az 24x24 px {small or ''}", not small)
    ctx.close()

    # Metin büyütülünce (WCAG 1.4.4, 1.4.10): sayfa yana taşmaz, konuşma yine de başlar, sohbet kartında metin kesilmez.
    # Çok büyük metinde ya da çok küçük ekranda kart, ekrandan uzun olur. Eskiden konuşma bu yüzden hiç başlamaz ve
    # mesajlar sonsuza kadar görünmez kalırdı.
    CLIPPED = """(() => { const chat = document.querySelector('.chat').getBoundingClientRect(); const bad = [];
      document.querySelectorAll('.chat .txt, .chat .who, .chat dt, .chat dd, .chat .stamp, .chat-caption').forEach(e => { const r = e.getBoundingClientRect();
        if (r.width > 0 && (r.left < chat.left - 2 || r.right > chat.right + 2)) bad.push(e.className || e.tagName); });
      return bad; })()"""
    worst_zoom = 0; stuck = []; clipped = []; combos = 0
    for lang in ("tr", "en", "de"):
        for zoom in ("100%", "200%"):
            for vw in (320, 390, 768, 1280):
                combos += 1
                ctx = browser.new_context(viewport={"width": vw, "height": 800})
                page = ctx.new_page()
                page.goto(BASE + "/?lang=" + lang)
                page.wait_for_load_state("networkidle")
                page.evaluate(f"document.documentElement.style.fontSize = '{zoom}'")
                page.locator(".chat").scroll_into_view_if_needed()
                try:
                    page.wait_for_selector("body[data-chat-done='1']", timeout=12000)
                except Exception:
                    stuck.append((lang, zoom, vw))
                page.wait_for_timeout(600)
                worst_zoom = max(worst_zoom, page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"))
                if page.evaluate(CLIPPED): clipped.append((lang, zoom, vw))
                ctx.close()
    check(f"büyütme: {combos} kombinasyonda (3 dil x 100/200% x 320-1280 px) yatay taşma yok (en büyük {worst_zoom} px)", worst_zoom == 0)
    check(f"büyütme: konuşma her kombinasyonda başlıyor, uzun kartta bile ({stuck or 'takılan yok'})", not stuck)
    check(f"büyütme: sohbet kartında hiçbir metin kesilmiyor ({clipped or 'kesilen yok'})", not clipped)

    # Bölüm görünme animasyonları ne kadar uzun olurlarsa olsunlar tetiklenir: küçük ekran + %200 metinde tüm bölümlere inince hepsi görünür
    ctx = browser.new_context(viewport={"width": 320, "height": 640})
    page = ctx.new_page()
    page.goto(BASE + "/?lang=de")
    page.wait_for_load_state("networkidle")
    page.evaluate("document.documentElement.style.fontSize = '200%'")
    page.wait_for_timeout(300)
    total = page.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < total:
        page.evaluate(f"window.scrollTo({{top: {y}, behavior: 'instant'}})")
        page.wait_for_timeout(120)
        y += 300
    page.wait_for_timeout(1800)
    hidden = page.evaluate("""[...document.querySelectorAll('.reveal-title, .rv, .split-col li, .services > div, .msg')].filter(e => getComputedStyle(e).opacity !== '1' && !e.closest('.reveal-title')).map(e => e.className || e.tagName)""")
    titles = page.evaluate("[...document.querySelectorAll('.reveal-title')].every(e => e.classList.contains('in-view'))")
    check(f"büyütme: 320 px + %200 metin + Almanca: sayfayı sonuna kadar gezince hiçbir içerik gizli kalmıyor ({hidden[:4] or 'gizli yok'})", not hidden and titles)
    ctx.close()

    # ================= TEKRAR GÖNDERİM (uçtan uca) =================
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    bodies = []
    mode = {"lose": True}

    def lose_response(route):
        bodies.append(route.request.post_data_json)
        if mode["lose"]:
            route.fetch()      # istek sunucuya gerçekten gider ve kaydedilir
            route.abort()      # ama cevap istemciye ulaşmaz (bağlantı koptu)
        else:
            route.continue_()

    page.route("**/api/requests", lose_response)
    page.goto(BASE)
    base = max_id()
    fill_valid(page)
    page.click("#submit-btn")
    page.wait_for_selector("#form-alert:not([hidden])")
    check("tekrar gönderim: cevap kaybolunca dürüst uyarı ('kaydedilmiş olabilir'), başarı gösterilmez", "kaydedilmiş olabilir" in page.inner_text("#form-alert") and page.locator("#success").is_hidden())
    check("tekrar gönderim: istek gönderim anahtarıyla gitti", isinstance(bodies[0].get("clientId"), str) and len(bodies[0]["clientId"]) >= 16)
    check("tekrar gönderim: cevap kaybolsa da sunucu kaydı yazmıştı", new_since(base) == 1)
    mode["lose"] = False
    page.click("#submit-btn")            # aynı içerikle tekrar
    page.wait_for_selector("#success:not([hidden])")
    check("tekrar gönderim: aynı içerikle tekrar aynı anahtarı kullanır", bodies[1]["clientId"] == bodies[0]["clientId"])
    check("tekrar gönderim: sunucu ikinci kayıt açmadı (tekrar gönderim güvenli)", new_since(base) == 1)
    first_key = bodies[0]["clientId"]
    page.click("#new-request")
    fill_valid(page); page.click("#submit-btn"); page.wait_for_selector("#success:not([hidden])")
    check("tekrar gönderim: yeni talepte yeni anahtar kullanılır ve ayrı kayıt oluşur", bodies[2]["clientId"] != first_key and new_since(base) == 2)
    ctx.close()

    # Düzeltilmiş içerik eskisinin yerine sessizce yutulmaz: alan değişince anahtar yenilenir
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    bodies2 = []
    mode2 = {"lose": True}

    def lose2(route):
        bodies2.append(route.request.post_data_json)
        if mode2["lose"]:
            route.fetch(); route.abort()
        else:
            route.continue_()

    page.route("**/api/requests", lose2)
    page.goto(BASE)
    base2 = max_id()
    fill_valid(page); page.click("#submit-btn"); page.wait_for_selector("#form-alert:not([hidden])")
    mode2["lose"] = False
    page.fill("#message", "Mesajı düzelttim: artık başka bir şey soruyorum ve bunu kaydetmenizi istiyorum.")
    page.click("#submit-btn"); page.wait_for_selector("#success:not([hidden])")
    check("tekrar gönderim: içerik düzeltilince yeni anahtar kullanılır, düzeltme kaybolmaz", bodies2[1]["clientId"] != bodies2[0]["clientId"] and new_since(base2) == 2)
    ctx.close()

    # ================= 404 SAYFASI =================
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    resp = page.goto(BASE + "/olmayan-adres")
    check("404: bilinmeyen adres 404 durum koduyla düzgün sayfa gösterir", resp.status == 404 and "bulunamadı" in page.inner_text("h1") and page.locator("a.btn[href='/']").is_visible() and "Cannot GET" not in page.content())
    page.click("a.btn[href='/']")
    page.wait_for_load_state("networkidle")
    check("404: 'Ana sayfaya dön' bağlantısı ana sayfaya götürür", page.url.rstrip("/") == BASE.rstrip("/") and page.locator("#hero-title").is_visible())
    ctx.close()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme="dark")
    page = ctx.new_page()
    page.goto(BASE + "/yok?lang=de")
    check("404: koyu tema ve Almanca çalışır", page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark" and "nicht gefunden" in page.inner_text("h1"))
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
