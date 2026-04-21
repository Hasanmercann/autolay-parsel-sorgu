"""TKGM debug - tam API yanıtını ve sayfa içeriğini yakalama."""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.sync_api import sync_playwright

all_responses = []

def debug_tkgm():
    def on_response(response):
        ct = response.headers.get("content-type", "")
        url = response.url
        # Tüm başarılı yanıtları logla
        if response.status == 200 and ("json" in ct or "query" in url.lower()):
            try:
                body = response.json()
                all_responses.append({"url": url, "body": body})
            except Exception:
                try:
                    text = response.text()
                    if len(text) < 2000 and text.strip().startswith("{"):
                        all_responses.append({"url": url, "body": text})
                except Exception:
                    pass

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("response", on_response)

        print("1. Sayfa açılıyor...")
        page.goto("https://parselsorgu.tkgm.gov.tr", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)

        print("2. Şartlar kabul ediliyor...")
        page.click("#terms-ok")
        page.wait_for_timeout(1500)
        try:
            page.click("#close-popup", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        print("3. İl seçiliyor: ANKARA")
        options = page.query_selector_all("#province-select option")
        print(f"   Toplam il: {len(options)}")
        for o in options[:5]:
            print(f"   val={o.get_attribute('value')!r} text={o.inner_text().strip()!r}")

        # ANKARA'yı seç
        for o in options:
            if "ANKARA" in o.inner_text().strip().upper():
                val = o.get_attribute("value")
                page.select_option("#province-select", value=val)
                print(f"   Seçildi: val={val}")
                break
        page.wait_for_timeout(2000)

        print("4. İlçe seçiliyor: ÇANKAYA")
        try:
            page.wait_for_function(
                "document.querySelector('#district-select').options.length > 1",
                timeout=8000
            )
        except Exception as e:
            print(f"   İlçe yükleme beklenemedi: {e}")

        ilce_options = page.query_selector_all("#district-select option")
        print(f"   Toplam ilçe: {len(ilce_options)}")
        for o in ilce_options[:5]:
            print(f"   val={o.get_attribute('value')!r} text={o.inner_text().strip()!r}")

        for o in ilce_options:
            if "ÇANKAYA" in o.inner_text().strip().upper() or "CANKAYA" in o.inner_text().strip().upper():
                val = o.get_attribute("value")
                page.select_option("#district-select", value=val)
                print(f"   Seçildi: val={val}")
                break
        page.wait_for_timeout(1500)

        print("5. Ada=100, Parsel=1 giriliyor ve sorgulanıyor...")
        all_responses.clear()
        page.fill("#block-input", "100")
        page.fill("#parcel-input", "1")
        page.click("#administrative-query-btn")
        page.wait_for_timeout(4000)

        print(f"\n6. Yakalanan API yanıtları: {len(all_responses)}")
        for i, r in enumerate(all_responses):
            print(f"\n--- Yanıt {i+1} ---")
            print(f"URL: {r['url']}")
            body_str = json.dumps(r['body'], ensure_ascii=False)
            print(f"Body ({len(body_str)} byte): {body_str[:500]}")

        # Sayfa içeriğinden parsel sonucunu ara
        print("\n7. Sayfa içeriğinde parsel verisi aranıyor...")
        content = page.content()
        if "koordinat" in content.lower() or "coordinate" in content.lower() or "geometry" in content.lower():
            print("   Sayfada geometri/koordinat verisi VAR")
        else:
            print("   Sayfada geometri/koordinat verisi YOK")

        # Ekran görüntüsü al
        page.screenshot(path="tkgm_debug.png")
        print("\n8. Ekran görüntüsü kaydedildi: tkgm_debug.png")

        browser.close()

if __name__ == "__main__":
    debug_tkgm()
