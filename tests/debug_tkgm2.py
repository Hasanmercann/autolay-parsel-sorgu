"""TKGM debug v2 - mahalle seçimiyle tam sorgu."""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.sync_api import sync_playwright

all_responses = []

def debug_tkgm2():
    def on_response(response):
        ct = response.headers.get("content-type", "")
        url = response.url
        if response.status == 200 and "tkgm" in url and len(url) > 50:
            try:
                body = response.json()
                all_responses.append({"url": url, "body": body})
            except Exception:
                pass

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("response", on_response)

        page.goto("https://parselsorgu.tkgm.gov.tr", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)
        page.click("#terms-ok")
        page.wait_for_timeout(1500)
        try:
            page.click("#close-popup", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        # Ankara seç
        for o in page.query_selector_all("#province-select option"):
            if "ANKARA" in o.inner_text().upper():
                page.select_option("#province-select", value=o.get_attribute("value"))
                break
        page.wait_for_timeout(2000)

        # Çankaya seç
        try:
            page.wait_for_function(
                "document.querySelector('#district-select').options.length > 1",
                timeout=8000
            )
        except Exception:
            pass
        for o in page.query_selector_all("#district-select option"):
            if "ÇANKAYA" in o.inner_text().upper() or "CANKAYA" in o.inner_text().upper():
                page.select_option("#district-select", value=o.get_attribute("value"))
                break
        page.wait_for_timeout(2000)

        # Mahalle listesini al
        try:
            page.wait_for_function(
                "document.querySelector('#neighborhood-select').options.length > 1",
                timeout=8000
            )
        except Exception:
            pass
        mahalle_options = page.query_selector_all("#neighborhood-select option")
        print(f"Mahalle sayisi: {len(mahalle_options)}")
        for o in mahalle_options[:8]:
            print(f"  val={o.get_attribute('value')!r} text={o.inner_text().strip()!r}")

        # Bilkent/Üniversiteler mahallesi dene
        secilen_mahalle = None
        for o in mahalle_options:
            t = o.inner_text().strip().upper()
            if any(k in t for k in ["BAYINDIR", "AYRANCI", "KIZILAY", "BAHÇELIEVLER", "KOCATEPE"]):
                val = o.get_attribute("value")
                page.select_option("#neighborhood-select", value=val)
                secilen_mahalle = t
                print(f"\nMahalle secildi: {t}")
                break

        if not secilen_mahalle and len(mahalle_options) > 1:
            # İlk gerçek mahalleyi seç (index 1, 0 = "Seçiniz")
            val = mahalle_options[1].get_attribute("value")
            page.select_option("#neighborhood-select", value=val)
            secilen_mahalle = mahalle_options[1].inner_text().strip()
            print(f"\nİlk mahalle secildi: {secilen_mahalle}")

        page.wait_for_timeout(1500)

        # Ada/parsel sorgula - birkaç kombinasyon dene
        for ada, parsel in [("1", "1"), ("2", "1"), ("100", "10"), ("50", "1")]:
            print(f"\n--- Ada={ada} Parsel={parsel} deneniyor ---")
            all_responses.clear()
            page.fill("#block-input", ada)
            page.fill("#parcel-input", parsel)
            page.click("#administrative-query-btn")
            page.wait_for_timeout(3500)

            # Sonuç sayacını oku
            try:
                sayac = page.text_content(".result-count, #result-count, .count", timeout=2000)
                print(f"  Sayaç: {sayac}")
            except Exception:
                pass

            print(f"  Yakalanan API yaniti: {len(all_responses)}")
            for r in all_responses[:3]:
                print(f"  URL: {r['url'][:90]}")
                body_str = json.dumps(r["body"], ensure_ascii=False)
                print(f"  Body: {body_str[:400]}")

            # Sayfada parsel listesi var mı kontrol
            try:
                liste = page.query_selector_all(".parcel-item, .result-item, li.parcel")
                print(f"  Parsel listesi elementi: {len(liste)}")
            except Exception:
                pass

            page.screenshot(path=f"tkgm_debug_ada{ada}_p{parsel}.png")

        browser.close()
        print("\nBitti.")

if __name__ == "__main__":
    debug_tkgm2()
