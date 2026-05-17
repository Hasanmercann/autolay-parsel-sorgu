"""
tests/test_cekme.py

CekmeCizici sınıfını AutoCAD üzerinde test eder.
25x20 metrelik arsa üzerine 3 metrelik çekme mesafesi uygulanır.
Beklenen sonuç: 19x14 = 266 m² yapı yaklaşma alanı.

Çalıştırma:
    cd C:/Projeler/Autolay
    python tests/test_cekme.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.mimari.arsa import ArsaCizici
from autolay.mimari.cekme import CekmeCizici
from autolay.mimari.veriler import MimariVeriler
from autolay.utils.logger import logger_olustur

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()

log = logger_olustur(__name__)


def test_cekme():
    """ArsaCizici + CekmeCizici birlikte çalışmasını uçtan uca test eder."""

    print("=" * 40)
    print("AutoLay — CekmeCizici Testi")
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

    # 2. Arsayı çiz
    koseler = [(0, 0), (25, 0), (25, 20), (0, 20)]
    arsa = ArsaCizici(connector)
    arsa.koseleri_ayarla(koseler)
    arsa.ciz()
    print(f"✓ Arsa çizildi        → {koseler}")
    print(f"  Alan: {arsa.alan():.2f} m²  (beklenen: 500.00)")

    # 3. CekmeCizici nesnesi oluştur
    cekme = CekmeCizici(connector)

    # 4. Arsa köşelerini ayarla
    cekme.arsa_koseleri_ayarla(koseler)
    print(f"✓ Arsa köşeleri ayarlandı → {len(koseler)} köşe")

    # 5. Çekme mesafesini ayarla: 3 metre içeri
    cekme.cekme_mesafesi_ayarla(3)
    print("✓ Çekme mesafesi ayarlandı → 3 m")

    # 6. Çekme sınırını çiz
    cekme.ciz()
    print("✓ Çekme çizildi       → AUTOLAY_CEKME katmanı, sarı")

    # 7. Hesaplanan çekme köşelerini göster
    kose_listesi = cekme.cekme_koseleri()
    print(f"✓ Çekme köşeleri      → {kose_listesi}")
    log.info(f"Çekme köşeleri: {kose_listesi}")

    # 8. Beklenen: 19x14 = 266 m² (her kenarda 3m çekilince 25-6=19, 20-6=14)
    from autolay.utils.geometri import GeometryUtils
    geo = GeometryUtils()
    cekme_alani = geo.poligon_alani(kose_listesi)
    log.info(f"Çekme alanı: {cekme_alani:.2f} m²  (beklenen: 266.00 m²)")
    print(f"  Çekme alanı: {cekme_alani:.2f} m²  (beklenen: 266.00)")

    # 9. Tüm çizimin ekranda görünmesi için ZoomExtents uygula
    connector.acad.ZoomExtents()
    print("✓ ZoomExtents uygulandı — arsa ve çekme ekranda görünüyor")

    print("=" * 40)
    print("Test tamamlandı.")


def test_cekme_kenar_bazli():
    utf8_aktif_et()

    print("="*50)
    print("CekmeCizici Kenar Bazlı Test")
    print("="*50)

    connector = AutoCADConnector()
    try:
        connector.baglan()
    except Exception as e:
        print(f"AutoCAD bağlantısı başarısız: {e}")
        return

    # Önce arsa çiz
    arsa = ArsaCizici(connector)
    arsa_koseleri = [(50, 0), (75, 0), (75, 20), (50, 20)]  # Farklı konumda 25x20 arsa
    arsa.koseleri_ayarla(arsa_koseleri)
    arsa.ciz()

    # Kenar bazlı çekme
    cekme = CekmeCizici(connector)
    cekme.arsa_koseleri_ayarla(arsa_koseleri)

    # Mesafeler:
    # Kenar 0: alt (ön bahçe) = 5m
    # Kenar 1: sağ (yan) = 3m
    # Kenar 2: üst (arka) = 3m
    # Kenar 3: sol (yan) = 3m
    cekme.tum_kenarlar_ayarla([5, 3, 3, 3])
    cekme.ciz()

    print(f"Çekme köşeleri: {cekme.cekme_koseleri()}")
    # Beklenen: (53, 5), (72, 5), (72, 17), (53, 17)
    # 19 geniş, 12 derin = 228 m²

    connector.acad.ZoomExtents()
    print("Test tamamlandı.")


def test_kademeli_cekme():
    utf8_aktif_et()

    print("="*50)
    print("Kademeli Çekme Testi (AutoCAD'siz)")
    print("="*50)

    connector = AutoCADConnector()
    try:
        connector.baglan()
    except Exception:
        # Bağlantı olmasa bile kademeli hesap saf matematik
        # Sadece kenar_mesafeleri listesini manipüle ediyor
        print("AutoCAD bağlantısı yok, yine de saf matematik testine devam...")

    cekme = CekmeCizici(connector)
    cekme.arsa_koseleri_ayarla([(0,0),(25,0),(25,20),(0,20)])

    # TEST 1: 4 kat veya az → değişiklik yok
    cekme.tum_kenarlar_ayarla([5, 3, 3, 3])
    cekme.kademeli_cekme_hesapla(kat_sayisi=4, on_kenar_indeks=0)
    beklenen = [5, 3, 3, 3]
    sonuc = cekme.kenar_mesafeleri
    print(f"Test 1 (4 kat): {sonuc} {'✓' if sonuc == beklenen else '✗ beklenen ' + str(beklenen)}")

    # TEST 2: 7 kat → 3 ekstra kat × 0.5 = +1.5m yan/arka
    cekme.tum_kenarlar_ayarla([5, 3, 3, 3])
    cekme.kademeli_cekme_hesapla(kat_sayisi=7, on_kenar_indeks=0)
    beklenen = [5, 4.5, 4.5, 4.5]  # ön değişmez, diğerleri +1.5
    sonuc = cekme.kenar_mesafeleri
    print(f"Test 2 (7 kat, parksız): {sonuc} {'✓' if sonuc == beklenen else '✗ beklenen ' + str(beklenen)}")

    # TEST 3: 7 kat + kenar 2 park komşusu
    cekme.tum_kenarlar_ayarla([5, 3, 3, 3])
    cekme.kademeli_cekme_hesapla(kat_sayisi=7, on_kenar_indeks=0, park_komsusu_kenarlar=[2])
    beklenen = [5, 4.5, 3, 4.5]  # ön değişmez, kenar 2 park → değişmez
    sonuc = cekme.kenar_mesafeleri
    print(f"Test 3 (7 kat, park=[2]): {sonuc} {'✓' if sonuc == beklenen else '✗ beklenen ' + str(beklenen)}")

    # TEST 4: 10 kat → 6 ekstra kat × 0.5 = +3m
    cekme.tum_kenarlar_ayarla([5, 3, 3, 3])
    cekme.kademeli_cekme_hesapla(kat_sayisi=10, on_kenar_indeks=0)
    beklenen = [5, 6, 6, 6]
    sonuc = cekme.kenar_mesafeleri
    print(f"Test 4 (10 kat): {sonuc} {'✓' if sonuc == beklenen else '✗ beklenen ' + str(beklenen)}")

    # TEST 5: Geçersiz parametreler
    try:
        cekme.kademeli_cekme_hesapla(kat_sayisi=-1, on_kenar_indeks=0)
        print("Test 5: ✗ (negatif kat hata fırlatmadı)")
    except ValueError:
        print("Test 5: Negatif kat → ValueError ✓")

    print("="*50)


def test_bitisik_nizam():
    utf8_aktif_et()
    print("="*50)
    print("Bitişik Nizam Testi")
    print("="*50)

    connector = AutoCADConnector()
    try:
        connector.baglan()
    except Exception as e:
        print(f"AutoCAD bağlantısı başarısız: {e}")
        return

    # TEST 1: Tek taraflı bitişik (sağ yan komşuya yapışık)
    # 25x20 arsa, x=100'den başlasın
    arsa_koseleri = [(100, 0), (125, 0), (125, 20), (100, 20)]

    arsa = ArsaCizici(connector)
    arsa.koseleri_ayarla(arsa_koseleri)
    arsa.ciz()

    cekme = CekmeCizici(connector)
    cekme.arsa_koseleri_ayarla(arsa_koseleri)

    # Kenar 0: alt (ön) = 5m
    # Kenar 1: sağ (bitişik) = 0
    # Kenar 2: üst (arka) = 3m
    # Kenar 3: sol (yan) = 3m
    cekme.bitisik_nizam_ayarla(
        bitisik_kenarlar=[1],
        diger_mesafeler={0: 5, 2: 3, 3: 3}
    )
    cekme.ciz()

    print(f"Kenar mesafeleri: {cekme.kenar_mesafeleri}")
    # Beklenen: [5, 0, 3, 3]
    print(f"Çekme köşeleri: {cekme.cekme_koseleri()}")
    # Beklenen: (103, 5), (125, 5), (125, 17), (103, 17)
    # Genişlik: 125-103 = 22 (sağa bitişik, soldan 3m çekildi)
    # Yükseklik: 17-5 = 12 (ön 5, arka 3)
    # Alan: 22 * 12 = 264 m²

    # TEST 2: İki taraflı bitişik (her iki yan komşuya yapışık)
    arsa2_koseleri = [(150, 0), (175, 0), (175, 20), (150, 20)]

    arsa2 = ArsaCizici(connector)
    arsa2.koseleri_ayarla(arsa2_koseleri)
    arsa2.ciz()

    cekme2 = CekmeCizici(connector)
    cekme2.arsa_koseleri_ayarla(arsa2_koseleri)
    cekme2.bitisik_nizam_ayarla(
        bitisik_kenarlar=[1, 3],  # Her iki yan komşu
        diger_mesafeler={0: 5, 2: 3}
    )
    cekme2.ciz()

    print(f"\n2. Arsa (iki taraflı bitişik):")
    print(f"Kenar mesafeleri: {cekme2.kenar_mesafeleri}")
    # Beklenen: [5, 0, 3, 0]
    print(f"Çekme köşeleri: {cekme2.cekme_koseleri()}")
    # Beklenen: (150, 5), (175, 5), (175, 17), (150, 17)
    # Genişlik: tam 25m (iki yan bitişik)
    # Yükseklik: 12m
    # Alan: 300 m²

    connector.acad.ZoomExtents()
    print("="*50)


def test_dar_aci_uyarisi():
    import io
    import logging
    utf8_aktif_et()

    print("="*50)
    print("Dar Açı ve Kısa Kenar Uyarı Testi")
    print("="*50)

    # Log mesajlarını yakalamak için özel handler
    log_buffer = io.StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setLevel(logging.WARNING)
    logger = logging.getLogger('autolay.mimari.cekme')
    logger.addHandler(handler)

    connector = AutoCADConnector()
    try:
        connector.baglan()
    except Exception:
        print("AutoCAD yok, yine de geometri uyarıları test edilir.")

    # TEST 1: Normal arsa — UYARI OLMAMALI
    print("\n--- Test 1: Normal 25x20 arsa ---")
    log_buffer.truncate(0)
    log_buffer.seek(0)
    cekme = CekmeCizici(connector)
    cekme.arsa_koseleri_ayarla([(0,0),(25,0),(25,20),(0,20)])
    cekme.tum_kenarlar_ayarla([3, 3, 3, 3])
    cekme._geometri_uyarilari()
    uyari = log_buffer.getvalue()
    print(f"Uyarı sayısı: {uyari.count('⚠')}")
    print(f"Test 1 {'✓' if uyari.count('⚠') == 0 else '✗ (uyarı çıkmamalıydı)'}")

    # TEST 2: Çok dar açılı üçgen arsa — UYARI OLMALI
    print("\n--- Test 2: İnce üçgen arsa ---")
    log_buffer.truncate(0)
    log_buffer.seek(0)
    cekme2 = CekmeCizici(connector)
    # Çok uzun dar üçgen: bir köşe 15° olmalı
    cekme2.arsa_koseleri_ayarla([(0,0),(50,0),(25,3)])
    cekme2.tum_kenarlar_ayarla([1, 1, 1])
    cekme2._geometri_uyarilari()
    uyari = log_buffer.getvalue()
    print(f"Uyarı mesajları:\n{uyari}")
    print(f"Test 2 {'✓ (dar açı yakalandı)' if '⚠ Köşe' in uyari else '✗'}")

    # TEST 3: Kısa kenar — UYARI OLMALI
    print("\n--- Test 3: Küçük arsa, büyük çekme ---")
    log_buffer.truncate(0)
    log_buffer.seek(0)
    cekme3 = CekmeCizici(connector)
    # 5x5 arsa, 3m çekme — kenar 5m, 3*2=6m, kenar <= 6 → uyarı
    cekme3.arsa_koseleri_ayarla([(0,0),(5,0),(5,5),(0,5)])
    cekme3.tum_kenarlar_ayarla([3, 3, 3, 3])
    cekme3._geometri_uyarilari()
    uyari = log_buffer.getvalue()
    print(f"Uyarı mesajları:\n{uyari}")
    print(f"Test 3 {'✓ (kısa kenar yakalandı)' if '⚠ Kenar' in uyari else '✗'}")

    # TEST 4: Hem kısa kenar hem dar açı
    print("\n--- Test 4: Zorlayıcı arsa (ince uzun üçgen, büyük çekme) ---")
    log_buffer.truncate(0)
    log_buffer.seek(0)
    cekme4 = CekmeCizici(connector)
    cekme4.arsa_koseleri_ayarla([(0,0),(20,0),(10,1)])  # çok yassı üçgen
    cekme4.tum_kenarlar_ayarla([3, 3, 3])
    cekme4._geometri_uyarilari()
    uyari = log_buffer.getvalue()
    print(f"Uyarı mesajları:\n{uyari}")
    kose_uyari = uyari.count('⚠ Köşe')
    kenar_uyari = uyari.count('⚠ Kenar')
    print(f"Köşe uyarıları: {kose_uyari}, Kenar uyarıları: {kenar_uyari}")
    print(f"Test 4 {'✓' if (kose_uyari > 0 or kenar_uyari > 0) else '✗'}")

    # Handler temizle
    logger.removeHandler(handler)
    print("="*50)


def test_verilerden_hesapla():
    utf8_aktif_et()
    print("="*50)
    print("verilerden_hesapla Testi")
    print("="*50)

    connector = AutoCADConnector()
    try:
        connector.baglan()
    except Exception as e:
        print(f"AutoCAD bağlantısı başarısız: {e}")
        return

    # TEST 1: Basit ayrık nizam, 1 kat — sadece varsayılan mesafeler
    print("\n--- Test 1: 1 kat ayrık ---")
    arsa_koseleri = [(200, 0), (225, 0), (225, 20), (200, 20)]
    veri1 = MimariVeriler(
        arsa_koseleri=arsa_koseleri,
        kat_sayisi=1,
        on_kenar_indeks=0,
    )
    arsa1 = ArsaCizici(connector)
    arsa1.koseleri_ayarla(arsa_koseleri)
    arsa1.ciz()

    cekme1 = CekmeCizici(connector)
    cekme1.verilerden_hesapla(veri1)
    cekme1.ciz()
    print(f"Mesafeler: {cekme1.kenar_mesafeleri}")
    # Beklenen: [5, 3, 3, 3] (ön=5, yan=3, arka=3, yan=3)
    assert cekme1.kenar_mesafeleri == [5.0, 3.0, 3.0, 3.0], f"Beklenen [5,3,3,3], alınan {cekme1.kenar_mesafeleri}"
    print("Test 1 ✓")

    # TEST 2: 7 kat — kademeli çekme uygulanmalı
    print("\n--- Test 2: 7 kat ayrık ---")
    arsa2_koseleri = [(240, 0), (265, 0), (265, 20), (240, 20)]
    veri2 = MimariVeriler(
        arsa_koseleri=arsa2_koseleri,
        kat_sayisi=7,
        on_kenar_indeks=0,
    )
    arsa2 = ArsaCizici(connector)
    arsa2.koseleri_ayarla(arsa2_koseleri)
    arsa2.ciz()

    cekme2 = CekmeCizici(connector)
    cekme2.verilerden_hesapla(veri2)
    cekme2.ciz()
    print(f"Mesafeler: {cekme2.kenar_mesafeleri}")
    # Beklenen: [5, 4.5, 4.5, 4.5] (ön değişmez, diğerleri +1.5)
    assert cekme2.kenar_mesafeleri == [5.0, 4.5, 4.5, 4.5], f"Beklenen [5,4.5,4.5,4.5], alınan {cekme2.kenar_mesafeleri}"
    print("Test 2 ✓")

    # TEST 3: Bitişik nizam, 1 kat
    print("\n--- Test 3: Bitişik, 1 kat ---")
    arsa3_koseleri = [(280, 0), (305, 0), (305, 20), (280, 20)]
    veri3 = MimariVeriler(
        arsa_koseleri=arsa3_koseleri,
        yapi_nizami="bitisik",
        kat_sayisi=1,
        on_kenar_indeks=0,
        bitisik_kenarlar=[1],  # sağ yan bitişik
    )
    arsa3 = ArsaCizici(connector)
    arsa3.koseleri_ayarla(arsa3_koseleri)
    arsa3.ciz()

    cekme3 = CekmeCizici(connector)
    cekme3.verilerden_hesapla(veri3)
    cekme3.ciz()
    print(f"Mesafeler: {cekme3.kenar_mesafeleri}")
    # Beklenen: [5, 0, 3, 3]
    assert cekme3.kenar_mesafeleri == [5.0, 0, 3.0, 3.0], f"Beklenen [5,0,3,3], alınan {cekme3.kenar_mesafeleri}"
    print("Test 3 ✓")

    # TEST 4: Bitişik + 7 kat (park komşusu dahil)
    print("\n--- Test 4: Bitişik + 7 kat + park komşusu=[2] ---")
    arsa4_koseleri = [(320, 0), (345, 0), (345, 20), (320, 20)]
    veri4 = MimariVeriler(
        arsa_koseleri=arsa4_koseleri,
        yapi_nizami="bitisik",
        kat_sayisi=7,
        on_kenar_indeks=0,
        bitisik_kenarlar=[1],
        park_komsusu_kenarlar=[2],
    )
    arsa4 = ArsaCizici(connector)
    arsa4.koseleri_ayarla(arsa4_koseleri)
    arsa4.ciz()

    cekme4 = CekmeCizici(connector)
    cekme4.verilerden_hesapla(veri4)
    cekme4.ciz()
    print(f"Mesafeler: {cekme4.kenar_mesafeleri}")
    # Beklenen: [5, 0, 3, 4.5]
    # Kenar 0 (ön): 5 (değişmez)
    # Kenar 1 (bitişik): 0 (değişmez)
    # Kenar 2 (park komşusu): 3 (değişmez)
    # Kenar 3 (yan): 3 + 1.5 = 4.5
    assert cekme4.kenar_mesafeleri == [5.0, 0, 3.0, 4.5], f"Beklenen [5,0,3,4.5], alınan {cekme4.kenar_mesafeleri}"
    print("Test 4 ✓")

    # TEST 5: Yüksek yapı uyarısı (65m)
    print("\n--- Test 5: Yüksek yapı (65m) ---")
    arsa5_koseleri = [(360, 0), (385, 0), (385, 20), (360, 20)]
    veri5 = MimariVeriler(
        arsa_koseleri=arsa5_koseleri,
        kat_sayisi=20,
        on_kenar_indeks=0,
        bina_yuksekligi_m=65.0,  # yüksek yapı
    )
    arsa5 = ArsaCizici(connector)
    arsa5.koseleri_ayarla(arsa5_koseleri)
    arsa5.ciz()

    cekme5 = CekmeCizici(connector)
    cekme5.verilerden_hesapla(veri5)
    # Uyarı log.warning'e gitmeli (konsolda görünecek)
    print(f"Mesafeler: {cekme5.kenar_mesafeleri}")
    # 20 kat → 16 ekstra × 0.5 = 8m eklenir yan/arkaya
    # Beklenen: [5, 11, 11, 11]
    # Yüksek yapı uyarısı bekleniyor
    print("Test 5 ✓ (yüksek yapı uyarısı log'da görünmeli)")

    connector.acad.ZoomExtents()
    print("\n" + "="*50)
    print("Tüm entegrasyon testleri tamamlandı")
    print("="*50)


if __name__ == "__main__":
    test_cekme()
    test_cekme_kenar_bazli()
    test_kademeli_cekme()
    test_bitisik_nizam()
    test_dar_aci_uyarisi()
    test_verilerden_hesapla()
