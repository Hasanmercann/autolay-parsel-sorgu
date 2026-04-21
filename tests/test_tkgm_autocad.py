"""
tests/test_tkgm_autocad.py

TKGM'den parsel çek → AutoCAD'e LWPolyline olarak çiz.

Çalıştırmadan önce:
    - AutoCAD 2026 açık olmalı
    - Bir .dwg dosyası yüklü olmalı

Çalıştırma:
    cd autolay-main
    python tests/test_tkgm_autocad.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.utils.logger import logger_olustur
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.drawing.shapes import GeometryDrawer
from autolay.drawing.layers import LayerManager
from autolay.okuyucu.tkgm_okuyucu import TKGMOkuyucu

utf8_aktif_et()
log = logger_olustur(__name__)


# ── Test parametreleri ──────────────────────────────────────────────
IL      = "KONYA"
ILCE    = "ILGIN"
MAHALLE = "TEKELER"
ADA     = "175"
PARSEL  = "1"
KATMAN  = "TKGM-ARSA"
# ───────────────────────────────────────────────────────────────────


def test_tkgm_autocad():
    print("=" * 55)
    print("TKGM → AutoCAD LWPolyline Testi")
    print("=" * 55)
    print(f"Parsel : {IL}/{ILCE}/{MAHALLE}  Ada:{ADA}  Parsel:{PARSEL}")
    print(f"Katman : {KATMAN}")
    print()

    # 1. TKGM'den koordinatları çek
    print("[1/4] TKGM'den koordinatlar çekiliyor...")
    okuyucu = TKGMOkuyucu()
    try:
        sonuc = okuyucu.parsel_sorgula(IL, ILCE, MAHALLE, ADA, PARSEL)
    except KeyError as e:
        print(f"HATA: Önbellekte bulunamadı — {e}")
        return
    except RuntimeError as e:
        print(f"HATA: {e}")
        return

    print(f"  Köşe sayısı : {len(sonuc.koseler)}")
    print(f"  Alan        : {sonuc.alan_m2:.1f} m²")
    print(f"  İlk köşe    : {sonuc.koseler[0]}")
    print(f"  Son köşe    : {sonuc.koseler[-1]}")
    print()

    # 2. AutoCAD'e bağlan
    print("[2/4] AutoCAD'e bağlanılıyor...")
    connector = AutoCADConnector()
    try:
        basarili = connector.baglan()
    except AktifCizimYokHatasi as e:
        print(f"HATA: {e}")
        print("Çözüm: AutoCAD'de bir .dwg dosyası açın.")
        return

    if not basarili:
        print("HATA: AutoCAD'e bağlanılamadı. AutoCAD 2026 açık mı?")
        return
    print("  Bağlantı kuruldu.")
    print()

    # 3. Katmanı hazırla
    print(f"[3/4] '{KATMAN}' katmanı hazırlanıyor...")
    katman_yoneticisi = LayerManager(connector)
    katman_yoneticisi.katman_olustur(KATMAN, renk="yesil")
    katman_yoneticisi.aktif_katman_yap(KATMAN)
    print(f"  Katman aktif: {KATMAN}")
    print()

    # 4. LWPolyline olarak çiz
    print("[4/4] Parsel AutoCAD'e çiziliyor...")
    cizici = GeometryDrawer(connector)
    try:
        polyline = cizici.lwpoligon_ciz(sonuc.koseler)
        # Zoom yap — çizilen nesne görüntüde ortaya gelsin
        connector.aktif_cizim().Application.ZoomExtents()
        print(f"  LWPolyline oluşturuldu.")
        print(f"  Kapalı: {polyline.Closed}")
    except Exception as e:
        print(f"HATA: Çizim başarısız — {type(e).__name__}: {e}")
        return
    print()

    print("TEST GEÇTI ✓")
    print("AutoCAD'de TKGM-ARSA katmanına geçerek parseli görebilirsiniz.")


if __name__ == "__main__":
    test_tkgm_autocad()
