"""
tkgm_id_olustur_tumtur.py
Türkiye'nin 81 ilinin tüm ilçe ve mahallelerini TKGM'den çekip
tkgm_idler.json dosyasına kaydeder.

Kullanım:
    python tests/tkgm_id_olustur_tumtur.py           # Tüm iller
    python tests/tkgm_id_olustur_tumtur.py --eksik   # Sadece önbellekte olmayanlar
    python tests/tkgm_id_olustur_tumtur.py ANKARA ISTANBUL  # Belirli iller

Süre: İl başına ortalama 2-4 dakika → tüm Türkiye ~3-5 saat
Yarım kalırsa --eksik seçeneğiyle kaldığı yerden devam eder.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.sync_api import sync_playwright

CIKTI = os.path.join(
    os.path.dirname(__file__), "..", "autolay", "okuyucu", "tkgm_idler.json"
)
TKGM_URL = "https://parselsorgu.tkgm.gov.tr"


def veri_yukle() -> dict:
    if os.path.exists(CIKTI):
        with open(CIKTI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def veri_kaydet(veri: dict):
    os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def sayfa_hazirla(page):
    """TKGM sayfasını açar, şartları kabul eder."""
    page.goto(TKGM_URL, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=20000)
    page.click("#terms-ok")
    page.wait_for_timeout(1500)
    try:
        page.click("#close-popup", timeout=3000)
    except Exception:
        pass
    page.wait_for_timeout(1500)


def il_listesi_al(page) -> list[dict]:
    """Sayfadaki il dropdown'ından tüm illeri döndürür."""
    opts = page.query_selector_all("#province-select option")
    iller = []
    for o in opts:
        val = o.get_attribute("value")
        ad = o.inner_text().strip()
        if val and val not in ("", "-1", "-2", "-3", "-4"):
            iller.append({"ad": ad.upper(), "val": val})
    return iller


def il_cek(page, il_ad: str, il_val: str) -> dict:
    """Tek il için tüm ilçe→mahalle verisini çeker."""
    ilceler = {}

    page.select_option("#province-select", value=il_val)
    page.wait_for_timeout(1200)
    try:
        page.wait_for_function(
            "document.querySelector('#district-select').options.length > 1",
            timeout=8000,
        )
    except Exception:
        pass

    ilce_opts = page.query_selector_all("#district-select option")

    for ilce_o in ilce_opts:
        ilce_val = ilce_o.get_attribute("value")
        ilce_ad = ilce_o.inner_text().strip().upper()
        if not ilce_val or ilce_val in ("", "-1", "-2", "-3", "-4"):
            continue

        mahalleler = {}
        page.select_option("#district-select", value=ilce_val)
        page.wait_for_timeout(800)
        try:
            page.wait_for_function(
                "document.querySelector('#neighborhood-select').options.length > 1",
                timeout=5000,
            )
        except Exception:
            pass

        mah_opts = page.query_selector_all("#neighborhood-select option")
        for mo in mah_opts:
            mval = mo.get_attribute("value")
            mad = mo.inner_text().strip().upper()
            if mval and mval not in ("", "-1", "-2", "-3", "-4"):
                mahalleler[mad] = mval

        ilceler[ilce_ad] = {"id": ilce_val, "mahalleler": mahalleler}
        print(f"    {ilce_ad}: {len(mahalleler)} mahalle")

    return ilceler


def tumunu_cek(hedef_iller: list[str] = None, sadece_eksik: bool = False):
    veri = veri_yukle()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        print("TKGM sayfası açılıyor...")
        sayfa_hazirla(page)

        tum_iller = il_listesi_al(page)
        print(f"Toplam {len(tum_iller)} il bulundu.\n")

        # Hangi iller çekilecek?
        if hedef_iller:
            hedef_iller_upper = [i.strip().upper() for i in hedef_iller]
            iller = [il for il in tum_iller if il["ad"] in hedef_iller_upper]
        elif sadece_eksik:
            iller = [il for il in tum_iller if il["ad"] not in veri]
            print(f"Önbellekte {len(veri)} il var, {len(iller)} il eksik.\n")
        else:
            iller = tum_iller

        toplam = len(iller)
        for sira, il in enumerate(iller, 1):
            il_ad = il["ad"]
            il_val = il["val"]
            print(f"[{sira}/{toplam}] {il_ad} işleniyor...")
            baslangic = time.time()

            try:
                ilceler = il_cek(page, il_ad, il_val)
                veri[il_ad] = {"id": il_val, "ilceler": ilceler}

                # Her il sonrası kaydet — yarım kalırsa veri kaybolmasın
                veri_kaydet(veri)

                sure = time.time() - baslangic
                ilce_sayisi = len(ilceler)
                mah_toplam = sum(
                    len(v["mahalleler"]) for v in ilceler.values()
                )
                print(
                    f"  ✓ {ilce_sayisi} ilçe, {mah_toplam} mahalle "
                    f"({sure:.0f} sn)\n"
                )

            except Exception as e:
                print(f"  ✗ HATA: {e}\n")
                veri_kaydet(veri)  # Hata öncesi kaydedilenleri koru

        browser.close()

    print(f"\nTamamlandı. Toplam {len(veri)} il kaydedildi.")
    print(f"Dosya: {os.path.abspath(CIKTI)}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--eksik" in args:
        args.remove("--eksik")
        tumunu_cek(sadece_eksik=True)
    elif args:
        tumunu_cek(hedef_iller=args)
    else:
        onay = input(
            "Tüm 81 il çekilecek (~3-5 saat sürebilir).\n"
            "Devam etmek istiyor musunuz? [e/H]: "
        ).strip().lower()
        if onay == "e":
            tumunu_cek()
        else:
            print("İptal. Belirli iller için: python tkgm_id_olustur_tumtur.py ANKARA ISTANBUL")
