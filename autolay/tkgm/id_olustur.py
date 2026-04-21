"""
tkgm_id_olustur_hizli.py
Sadece kullanilacak il icin mahalle id'lerini ceker.
Kullanim: python tests/tkgm_id_olustur_hizli.py KONYA
"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


from playwright.sync_api import sync_playwright

CIKTI = os.path.join(os.path.dirname(__file__), "idler.json")


def il_cek(hedef_il: str):
    # Mevcut veriyi yukle
    if os.path.exists(CIKTI):
        with open(CIKTI, "r", encoding="utf-8") as f:
            veri = json.load(f)
    else:
        veri = {}

    hedef_il = hedef_il.upper()

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

        # Il bul
        opts = page.query_selector_all("#province-select option")
        il_val = None
        for o in opts:
            if hedef_il in o.inner_text().strip().upper():
                il_val = o.get_attribute("value")
                break

        if not il_val:
            print(f"HATA: '{hedef_il}' ili bulunamadi.")
            browser.close()
            return

        veri[hedef_il] = {"id": il_val, "ilceler": {}}
        page.select_option("#province-select", value=il_val)
        page.wait_for_timeout(1500)

        try:
            page.wait_for_function(
                "document.querySelector('#district-select').options.length > 1",
                timeout=8000
            )
        except Exception:
            pass

        ilce_opts = page.query_selector_all("#district-select option")
        print(f"{hedef_il}: {len(ilce_opts)} ilce")

        for ilce_o in ilce_opts:
            ilce_val = ilce_o.get_attribute("value")
            ilce_ad = ilce_o.inner_text().strip()
            if not ilce_val or ilce_val in ("-3", "-4"):
                continue

            veri[hedef_il]["ilceler"][ilce_ad.upper()] = {"id": ilce_val, "mahalleler": {}}

            page.select_option("#district-select", value=ilce_val)
            page.wait_for_timeout(1000)
            try:
                page.wait_for_function(
                    "document.querySelector('#neighborhood-select').options.length > 1",
                    timeout=5000
                )
            except Exception:
                pass

            mah_opts = page.query_selector_all("#neighborhood-select option")
            for mo in mah_opts:
                mval = mo.get_attribute("value")
                mad = mo.inner_text().strip()
                if mval and mval not in ("-3", "-4"):
                    veri[hedef_il]["ilceler"][ilce_ad.upper()]["mahalleler"][mad.upper()] = mval

            print(f"  {ilce_ad}: {len(veri[hedef_il]['ilceler'][ilce_ad.upper()]['mahalleler'])} mahalle")

        browser.close()

    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

    print(f"\nKaydedildi: {CIKTI}")


if __name__ == "__main__":
    il_adi = sys.argv[1] if len(sys.argv) > 1 else "KONYA"
    il_cek(il_adi)
