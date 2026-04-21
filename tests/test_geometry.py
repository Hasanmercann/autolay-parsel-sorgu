"""
tests/test_geometry.py

GeometryDrawer sınıfının tüm çizim metodlarını AutoCAD üzerinde test eder.
Çalıştırmadan önce AutoCAD 2026'nın açık ve bir .dwg dosyasının
yüklü olduğundan emin olun.

Çalıştırma:
    cd C:/Projeler/Autolay
    python tests/test_geometry.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.drawing.shapes import GeometryDrawer

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()


def test_geometry():
    """GeometryDrawer sınıfının tüm çizim metodlarını sırayla test eder."""

    print("=" * 40)
    print("AutoLay — Geometri Çizim Testi")
    print("=" * 40)

    # 1. AutoCAD bağlantısını kur
    connector = AutoCADConnector()
    try:
        basarili = connector.baglan()
    except AktifCizimYokHatasi as hata:
        print(f"HATA: {hata}")
        print("Çözüm: AutoCAD'de bir .dwg dosyası açın ve tekrar deneyin.")
        return

    if not basarili:
        print("HATA: AutoCAD'e bağlanılamadı. Test durduruluyor.")
        print("Çözüm: AutoCAD 2026'yı açın ve tekrar deneyin.")
        return

    # 2. GeometryDrawer nesnesini oluştur
    cizici = GeometryDrawer(connector)

    # 3. Çizgi: (0,0)'dan (200,0)'a yatay çizgi
    cizici.cizgi_ciz((0, 0), (200, 0))
    print("✓ Çizgi çizildi       → (0,0) → (200,0)")

    # 4. Kare: sol alt köşesi (0,30), kenar uzunluğu 60
    cizici.kare_ciz((0, 30), 60)
    print("✓ Kare çizildi        → sol_alt=(0,30), kenar=60")

    # 5. Dikdörtgen: sol alt köşesi (100,30), en=80, boy=40
    cizici.dikdortgen_ciz((100, 30), en=80, boy=40)
    print("✓ Dikdörtgen çizildi  → sol_alt=(100,30), en=80, boy=40")

    # 6. Daire: merkezi (250,60), yarıçap=30
    cizici.daire_ciz((250, 60), 30)
    print("✓ Daire çizildi       → merkez=(250,60), yarıçap=30")

    # 7. Üçgen poligon: 3 köşeli kapalı şekil
    cizici.poligon_ciz([(350, 30), (420, 30), (385, 90)])
    print("✓ Üçgen çizildi       → [(350,30), (420,30), (385,90)]")

    # 8. Tüm çizimin ekranda görünmesi için ZoomExtents uygula
    connector.acad.ZoomExtents()
    print("✓ ZoomExtents uygulandı — tüm çizim ekranda görünüyor")

    print("=" * 40)
    print("Test tamamlandı.")


if __name__ == "__main__":
    test_geometry()
