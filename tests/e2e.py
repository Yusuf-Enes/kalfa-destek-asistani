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
    check("hareketi azalt: yeniden oynat düğmesi ve kaydırma çizgisi yok", page.locator(".replay").is_hidden() and page.evaluate("getComputedStyle(document.querySelector('.progress')).display") == "none")
    check("hareketi azalt: adım çizgileri tam görünür", page.evaluate("[...document.querySelectorAll('.steps li:not(:last-child)')].every(li => getComputedStyle(li, '::after').transform === 'none')"))
    ctx.close()

    # ---- Hareket açıkken: yazıyor durumu, fiş düşer, mühür basılır, adım çizgisi
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_selector(".msg.typing", timeout=10000)
    check("hareket: Kalfa 'yazıyor' durumu görünür", True)
    page.wait_for_timeout(300)
    check("hareket: yazarken etiket görünür, metin gizli", page.evaluate("(() => { const m = document.querySelector('.msg.typing'); return getComputedStyle(m.querySelector('.who')).opacity !== '0' && getComputedStyle(m.querySelector('.txt')).color === 'rgba(0, 0, 0, 0)'; })()"))
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

    # Konuşmayı yeniden oynat
    page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
    page.wait_for_selector("body[data-chat-done='1']", timeout=25000)
    check("yeniden oynat: konuşma bitince düğme görünür ve açık", page.locator(".replay").is_visible() and page.locator(".replay").is_enabled())
    page.click(".replay")
    check("yeniden oynat: tıklayınca düğme kapanır ve konuşma başa döner", page.locator(".replay").is_disabled() and page.evaluate("document.body.getAttribute('data-chat-done')") is None and page.evaluate("document.querySelector('.msg-note').classList.contains('stamped')") is False)
    page.wait_for_selector("body[data-chat-done='1']", timeout=25000)
    page.wait_for_timeout(700)
    check("yeniden oynat: konuşma yeniden oynar, fiş düşer, mühür basılır", page.evaluate("document.querySelector('.msg-note').classList.contains('stamped') && getComputedStyle(document.querySelector('.stamp')).opacity === '1'"))
    check("yeniden oynat: bitince düğme yeniden açılır", page.locator(".replay").is_enabled())
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
