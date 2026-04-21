import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.okuyucu.arsa_okuyucu import ArsaOkuyucu
from autolay.mimari.arsa import ArsaCizici
from autolay.mimari.cekme import CekmeCizici
from autolay.mimari.veriler import MimariVeriler
from autolay.mimari.imar_hesap import ImarHesap


def test_arsa_okuyucu():
    utf8_aktif_et()
    print("="*50)
    print("ArsaOkuyucu İnteraktif Test")
    print("="*50)
    print()
    print("HAZIRLIK:")
    print("1. AutoCAD'de boş bir çizim aç")
    print("2. AutoCAD'de bir POLYLINE çiz:")
    print("   - Komut: PLINE (veya Türkçe: POLIGON)")
    print("   - 4 köşeli kapalı bir dikdörtgen yeterli")
    print("   - Örnek: (0,0) → (25,0) → (25,20) → (0,20) → C")
    print("3. Polyline çizdikten sonra Enter'a bas")
    print()
    input("Polyline'ı çizdiğinde Enter'a bas: ")

    connector = AutoCADConnector()
    try:
        connector.baglan()
    except Exception as e:
        print(f"AutoCAD bağlantısı başarısız: {e}")
        return

    # AŞAMA 1: Polyline oku
    okuyucu = ArsaOkuyucu(connector)

    try:
        koseler = okuyucu.polyline_sec("AutoLay — Arsayı seçin:")
    except RuntimeError as e:
        print(f"Hata: {e}")
        return

    print(f"\n✓ Polyline okundu: {len(koseler)} köşe")
    print(f"Köşeler:")
    for i, (x, y) in enumerate(koseler):
        print(f"  Kenar {i}: ({x:.2f}, {y:.2f})")

    # AŞAMA 2: MimariVeriler oluştur
    print("\n" + "="*50)
    print("AŞAMA 2: Otomatik Proje Oluşturma")
    print("="*50)

    veri = MimariVeriler(
        arsa_koseleri=koseler,
        yapi_nizami="ayrik",
        kat_sayisi=5,
        on_kenar_indeks=0,
        taks=0.40,
        kaks=2.00,
    )
    print(f"\n{veri.ozet()}")

    # AŞAMA 3: Arsa ve çekme çiz
    print("\n" + "="*50)
    print("AŞAMA 3: Çizim")
    print("="*50)

    # NOT: Mevcut polyline kullanıcının çizdiği olduğu için
    # ArsaCizici tekrar çizmez, sadece katman ve işaret için
    # mevcut arsanın koordinatlarını kullanır. Ama çekme yeni çizilir.

    cekme = CekmeCizici(connector)
    cekme.verilerden_hesapla(veri)
    cekme.ciz()
    print(f"\n✓ Çekme çizildi. Mesafeler: {cekme.kenar_mesafeleri}")

    # AŞAMA 4: İmar hesabı
    print("\n" + "="*50)
    print("AŞAMA 4: İmar Hesabı")
    print("="*50)

    imar = ImarHesap(veri)
    imar.hesapla()
    print(f"\n{imar.rapor()}")

    uyarilar = imar.uyarilar()
    if uyarilar:
        print("\nUyarılar:")
        for u in uyarilar:
            print(f"  {u}")

    # ZoomExtents
    connector.acad.ZoomExtents()

    print("\n" + "="*50)
    print("Test tamamlandı!")
    print("="*50)


if __name__ == "__main__":
    test_arsa_okuyucu()
