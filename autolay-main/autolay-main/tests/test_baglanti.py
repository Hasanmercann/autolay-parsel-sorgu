"""
tests/test_baglanti.py

AutoCADConnector sınıfının temel işlevlerini test eder.
Çalıştırmadan önce AutoCAD 2026'nın açık ve bir .dwg dosyasının
yüklü olduğundan emin olun.

Çalıştırma:
    cd C:/Projeler/Autolay
    python tests/test_baglanti.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()


def test_baglanti():
    """AutoCAD bağlantısını ve temel bilgileri test eder."""

    print("=" * 40)
    print("AutoLay — Bağlantı Testi")
    print("=" * 40)

    connector = AutoCADConnector()

    # 1. Bağlantı kur
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

    # 2. Bağlantı durumunu kontrol et
    print(f"Bağlı mı     : {connector.bagli_mi()}")

    # 3. AutoCAD sürümünü al
    try:
        print(f"AutoCAD Sürüm: {connector.surum()}")
    except ConnectionError as hata:
        print(f"Sürüm alınamadı: {hata}")

    # 4. Aktif dosya adını al
    try:
        print(f"Açık Dosya   : {connector.dosya_adi()}")
    except RuntimeError as hata:
        print(f"Dosya adı alınamadı: {hata}")

    print("=" * 40)
    print("Test tamamlandı.")


if __name__ == "__main__":
    test_baglanti()
