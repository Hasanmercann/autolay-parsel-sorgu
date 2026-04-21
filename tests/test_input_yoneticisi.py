"""
tests/test_input_yoneticisi.py

InputManager sınıfının interaktif testini yapar.
Kullanıcıdan terminal üzerinden yarıçap, merkez koordinatı ve onay alarak
AutoCAD'de bir daire çizer.

UYARI: Bu test interaktiftir; çalıştırırken terminal girişi gerektirir.
Çalıştırmadan önce AutoCAD 2026'nın açık ve bir .dwg dosyasının
yüklü olduğundan emin olun.

Çalıştırma:
    cd C:/Projeler/Autolay
    venv/Scripts/python tests/test_input_yoneticisi.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.drawing.shapes import GeometryDrawer
from autolay.utils.input_yoneticisi import InputManager
from autolay.utils.logger import logger_olustur

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()

log = logger_olustur(__name__)

print("========================================")
print("AutoLay — InputManager İnteraktif Test")
print("========================================")

# 1. Bağlantı kur
connector = AutoCADConnector()
try:
    if not connector.baglan():
        print("AutoCAD bağlantısı kurulamadı. Test durduruluyor.")
        sys.exit(1)
except AktifCizimYokHatasi as hata:
    print(f"HATA: {hata}")
    print("Çözüm: AutoCAD'de bir .dwg dosyası açın ve tekrar deneyin.")
    sys.exit(1)

# 2. Çizici ve girdi yöneticisi oluştur
cizici = GeometryDrawer(connector)
im = InputManager()

# 3. Kullanıcıdan yarıçap al
yaricap = im.sayi_al("Daire yarıçapı", min=1, max=500, ondalikli=True)

# 4. Kullanıcıdan merkez koordinatı al
merkez = im.koordinat_al("Daire merkezi")

# 5. Onay sor
onay = im.evet_hayir("Bu daireyi çizelim mi?", varsayilan=True)

# 6. Onaya göre işlem yap
if onay:
    daire = cizici.daire_ciz(merkez, yaricap)
    connector.aktif_cizim().Application.ZoomExtents()
    log.info(
        f"Daire çizildi → merkez={merkez}, yarıçap={yaricap}"
    )
else:
    log.info("Kullanıcı iptal etti. Daire çizilmedi.")

print("========================================")
print("Test tamamlandı.")
