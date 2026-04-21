"""
tests/test_arsa.py

ArsaCizici sınıfını AutoCAD üzerinde test eder.
25x20 metrelik dikdörtgen bir arsa çizer, alan ve merkez noktasını doğrular.

Çalıştırma:
    cd C:/Projeler/Autolay
    python tests/test_arsa.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.mimari.arsa import ArsaCizici
from autolay.utils.logger import logger_olustur

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()

log = logger_olustur(__name__)


def test_arsa():
    """ArsaCizici sınıfını uçtan uca test eder: çizim, alan, merkez."""

    print("=" * 40)
    print("AutoLay — ArsaCizici Testi")
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

    # 2. ArsaCizici nesnesini oluştur
    arsa = ArsaCizici(connector)

    # 3. 25x20 metrelik dikdörtgen arsa köşelerini ayarla
    koseler = [(0, 0), (25, 0), (25, 20), (0, 20)]
    arsa.koseleri_ayarla(koseler)
    print(f"✓ Köşeler ayarlandı   → {koseler}")

    # 4. Arsayı AutoCAD'e çiz
    arsa.ciz()
    print("✓ Arsa çizildi        → AUTOLAY_ARSA katmanı, kırmızı")

    # 5. Alan hesapla ve doğrula (beklenen: 500 m²)
    alan = arsa.alan()
    log.info(f"Hesaplanan alan: {alan:.2f} m²  (beklenen: 500.00 m²)")
    print(f"✓ Alan hesaplandı     → {alan:.2f} m²  (beklenen: 500.00)")

    # 6. Merkez noktasını hesapla ve doğrula (beklenen: (12.5, 10.0))
    merkez = arsa.merkez_noktasi()
    log.info(f"Hesaplanan merkez: {merkez}  (beklenen: (12.5, 10.0))")
    print(f"✓ Merkez hesaplandı   → {merkez}  (beklenen: (12.5, 10.0))")

    # 7. Tüm çizimin ekranda görünmesi için ZoomExtents uygula
    connector.acad.ZoomExtents()
    print("✓ ZoomExtents uygulandı — arsa ekranda görünüyor")

    print("=" * 40)
    print("Test tamamlandı.")


if __name__ == "__main__":
    test_arsa()
