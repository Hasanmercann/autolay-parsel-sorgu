"""TKGM debug - Konya/Ilgin/Tekeler ada=175 parsel=1"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.sync_api import sync_playwright

all_responses = []

def debug():
    def on_response(response):
        ct = response.headers.get("content-type", "")
        url = response.url
        if response.status == 200:
            try:
                body = response.json()
                # Koordinat içerebilecek her JSON yanıtı yakala
                body_str = json.dumps(body)
                if any(k in body_str for k in ["coordinate", "geometry", "parcel", "feature", "Geometry", "Feature"]):
                    all_responses.append({"url": url, "body": body})
            except Exception:
                pass

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("response", on_response)

        print("Sayfa açılıyor...")
        page.goto("https://parselsorgu.tkgm.gov.tr", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)
        page.click("#terms-ok")
        page.wait_for_timeout(1500)
        try:
            page.click("#close-popup", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        # Konya seç
        for o in page.query_selector_all("#province-select option"):
            if "KONYA" in o.inner_text().upper():
                page.select_option("#province-select", value=o.get_attribute("value"))
                print(f"İl seçildi: {o.inner_text().strip()}")
                break
        page.wait_for_timeout(2000)

        # Ilgın seç
        try:
            page.wait_for_function(
                "document.querySelector('#district-select').options.length > 1",
                timeout=8000
            )
        except Exception:
            pass

        ilce_options = page.query_selector_all("#district-select option")
        print(f"İlçe sayısı: {len(ilce_options)}")
        for o in ilce_options:
            t = o.inner_text().strip().upper()
            if "ILGIN" in t or "ILĞIN" in t or "ILGIN" in t.replace("Ğ","G").replace("I","I"):
                page.select_option("#district-select", value=o.get_attribute("value"))
                print(f"İlçe seçildi: {o.inner_text().strip()}")
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
        print(f"Mahalle sayısı: {len(mahalle_options)}")
        for o in mahalle_options:
            print(f"  val={o.get_attribute('value')!r} text={o.inner_text().strip()!r}")

        # Tekeler mahallesi seç
        for o in mahalle_options:
            if "TEKELER" in o.inner_text().upper():
                page.select_option("#neighborhood-select", value=o.get_attribute("value"))
                print(f"\nMahalle seçildi: {o.inner_text().strip()}")
                break
        page.wait_for_timeout(1500)

        # Ada=175, Parsel=1
        print("\nAda=175, Parsel=1 sorgulanıyor...")
        all_responses.clear()
        page.fill("#block-input", "175")
        page.fill("#parcel-input", "1")
        page.click("#administrative-query-btn")
        page.wait_for_timeout(5000)

        print(f"Yakalanan API yanıtı: {len(all_responses)}")
        for i, r in enumerate(all_responses):
            print(f"\n=== Yanıt {i+1} ===")
            print(f"URL: {r['url']}")
            body_str = json.dumps(r["body"], ensure_ascii=False)
            print(f"Body ({len(body_str)} byte):")
            print(body_str[:1000])

        page.screenshot(path="tkgm_konya.png")
        print("\nEkran görüntüsü: tkgm_konya.png")
        browser.close()

if __name__ == "__main__":
    debug()
