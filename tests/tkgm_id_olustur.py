"""
il_ilce_listesi.py - TKGM il/ilce/mahalle ID onbellegini olusturur.
Tek seferlik calistirilir, cikti: autolay/okuyucu/tkgm_idler.json
"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.sync_api import sync_playwright

CIKTI = os.path.join(os.path.dirname(__file__), "..", "autolay", "okuyucu", "tkgm_idler.json")

def il_listesi_cek():
    veri = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://parselsorgu.tkgm.gov.tr", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)
        page.click("#terms-ok")
        page.wait_for_timeout(1500)
        try:
            page.click("#close-popup", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        # Il listesi
        opts = page.query_selector_all("#province-select option")
        for o in opts:
            val = o.get_attribute("value")
            ad = o.inner_text().strip()
            if val and val not in ("-3", "-4"):
                veri[ad.upper()] = {"id": val, "ilceler": {}}

        print(f"Il sayisi: {len(veri)}")

        # Her il icin ilce listesi
        for il_adi, il_bilgi in veri.items():
            page.select_option("#province-select", value=il_bilgi["id"])
            page.wait_for_timeout(1200)
            try:
                page.wait_for_function(
                    "document.querySelector('#district-select').options.length > 1",
                    timeout=5000
                )
            except Exception:
                pass

            ilce_opts = page.query_selector_all("#district-select option")
            for o in ilce_opts:
                val = o.get_attribute("value")
                ad = o.inner_text().strip()
                if val and val not in ("-3", "-4"):
                    veri[il_adi]["ilceler"][ad.upper()] = {"id": val, "mahalleler": {}}

            print(f"  {il_adi}: {len(veri[il_adi]['ilceler'])} ilce")

            # Her ilce icin mahalle listesi
            for ilce_adi, ilce_bilgi in veri[il_adi]["ilceler"].items():
                page.select_option("#district-select", value=ilce_bilgi["id"])
                page.wait_for_timeout(1000)
                try:
                    page.wait_for_function(
                        "document.querySelector('#neighborhood-select').options.length > 1",
                        timeout=5000
                    )
                except Exception:
                    pass

                mah_opts = page.query_selector_all("#neighborhood-select option")
                for o in mah_opts:
                    val = o.get_attribute("value")
                    ad = o.inner_text().strip()
                    if val and val not in ("-3", "-4"):
                        veri[il_adi]["ilceler"][ilce_adi]["mahalleler"][ad.upper()] = val

        browser.close()

    # Kaydet
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

    print(f"\nKaydedildi: {CIKTI}")
    return veri

if __name__ == "__main__":
    il_listesi_cek()
