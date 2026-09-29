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
        page.wait_for_timeout(2600)  # açılış hareketi bitsin
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

    browser.close()

print()
print("SONUÇ:", "hepsi geçti" if not failures else f"{len(failures)} test kaldı")
sys.exit(1 if failures else 0)
