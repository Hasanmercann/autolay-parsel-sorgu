"""
tests/test_layers.py

LayerManager sınıfının katman oluşturma, aktif yapma, listeleme
ve silme işlevlerini GeometryDrawer ile birlikte test eder.

Çalıştırmadan önce AutoCAD 2026'nın açık ve bir .dwg dosyasının
yüklü olduğundan emin olun.

Çalıştırma:
    cd C:/Projeler/Autolay
    python tests/test_layers.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.drawing.shapes import GeometryDrawer
from autolay.drawing.layers import LayerManager

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()


def test_layers():
    """LayerManager ve GeometryDrawer sınıflarını birlikte test eder."""

    print("=" * 40)
    print("AutoLay — Katman Yönetimi Testi")
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

    # 2. Yardımcı nesneleri oluştur
    cizici = GeometryDrawer(connector)
    katman_yoneticisi = LayerManager(connector)

    # --- a, b, c, d: TEST_ARSA katmanı ---
    katman_yoneticisi.katman_olustur("TEST_ARSA", renk="kirmizi")
    katman_yoneticisi.aktif_katman_yap("TEST_ARSA")
    cizici.dikdortgen_ciz((0, 0), en=100, boy=60)
    print("✓ TEST_ARSA katmanı oluşturuldu ve dikdörtgen çizildi")

    # --- e, f, g, h: TEST_CEKME katmanı ---
    katman_yoneticisi.katman_olustur("TEST_CEKME", renk="sari")
    katman_yoneticisi.aktif_katman_yap("TEST_CEKME")
    cizici.dikdortgen_ciz((10, 10), en=80, boy=40)
    print("✓ TEST_CEKME katmanı oluşturuldu ve dikdörtgen çizildi")

    # --- i, j, k, l: TEST_BINA katmanı ---
    katman_yoneticisi.katman_olustur("TEST_BINA", renk="yesil")
    katman_yoneticisi.aktif_katman_yap("TEST_BINA")
    cizici.daire_ciz((50, 30), 15)
    print("✓ TEST_BINA katmanı oluşturuldu ve daire çizildi")

    # 6. Mevcut tüm katmanları listele
    print("\nMevcut katmanlar:")
    for katman_adi in katman_yoneticisi.tum_katmanlar():
        print(f"  - {katman_adi}")

    # 7. TEST_BINA katmanını silmeyi dene
    # AutoCAD üzerinde nesne bulunan katmanı silmeye izin vermeyebilir
    print("\nTEST_BINA katmanı siliniyor...")
    try:
        katman_yoneticisi.katman_sil("TEST_BINA")
        print("✓ TEST_BINA silindi")
    except Exception as hata:
        print(f"✗ TEST_BINA silinemedi (içinde nesne olabilir): {hata}")

    # 8. Tüm çizimin ekranda görünmesi için ZoomExtents uygula
    connector.acad.ZoomExtents()
    print("\n✓ ZoomExtents uygulandı — tüm çizim ekranda görünüyor")

    print("=" * 40)
    print("Test tamamlandı.")


if __name__ == "__main__":
    test_layers()
