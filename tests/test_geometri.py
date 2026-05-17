"""
tests/test_geometri.py

GeometryUtils sınıfının matematiksel metodlarını saf Python ile test eder.
AutoCAD bağlantısı gerekmez.

Çalıştırma:
    cd C:/Projeler/Autolay
    venv/Scripts/python tests/test_geometri.py
"""

import sys
import os

# autolay paketinin bulunduğu ana klasörü Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
from autolay.utils.geometri import GeometryUtils

# Türkçe karakterlerin konsolda doğru görünmesi için UTF-8'i etkinleştir
utf8_aktif_et()


def test_geometri():
    """GeometryUtils sınıfının tüm metodlarını sayısal doğrulukla test eder."""

    gu = GeometryUtils()

    print("=" * 50)
    print("GeometryUtils Matematik Testi")
    print("=" * 50)

    # TEST 1: mesafe
    sonuc = gu.mesafe((0, 0), (3, 4))
    beklenen = 5.0
    print(f"Test 1 - mesafe((0,0),(3,4)) = {sonuc}  beklenen={beklenen}  {'✓' if abs(sonuc - beklenen) < 0.001 else '✗'}")

    # TEST 2: poligon_alani (10x10 kare)
    sonuc = gu.poligon_alani([(0, 0), (10, 0), (10, 10), (0, 10)])
    beklenen = 100.0
    print(f"Test 2 - 10x10 kare alanı = {sonuc}  beklenen={beklenen}  {'✓' if abs(sonuc - beklenen) < 0.001 else '✗'}")

    # TEST 3: poligon_alani (üçgen)
    sonuc = gu.poligon_alani([(0, 0), (10, 0), (0, 10)])
    beklenen = 50.0
    print(f"Test 3 - dik üçgen alanı = {sonuc}  beklenen={beklenen}  {'✓' if abs(sonuc - beklenen) < 0.001 else '✗'}")

    # TEST 4: poligon_merkezi
    sonuc = gu.poligon_merkezi([(0, 0), (10, 0), (10, 10), (0, 10)])
    beklenen = (5.0, 5.0)
    print(f"Test 4 - 10x10 kare merkezi = {sonuc}  beklenen={beklenen}  {'✓' if abs(sonuc[0] - beklenen[0]) < 0.001 and abs(sonuc[1] - beklenen[1]) < 0.001 else '✗'}")

    # TEST 5: nokta_poligon_icinde_mi (içerde)
    sonuc = gu.nokta_poligon_icinde_mi((5, 5), [(0, 0), (10, 0), (10, 10), (0, 10)])
    print(f"Test 5 - (5,5) karenin içinde = {sonuc}  beklenen=True  {'✓' if sonuc == True else '✗'}")

    # TEST 6: nokta_poligon_icinde_mi (dışarda)
    sonuc = gu.nokta_poligon_icinde_mi((15, 15), [(0, 0), (10, 0), (10, 10), (0, 10)])
    print(f"Test 6 - (15,15) karenin dışında = {sonuc}  beklenen=False  {'✓' if sonuc == False else '✗'}")

    # TEST 7: poligon_offset (CCW, 10x10 → 6x6 içeri 2)
    sonuc = gu.poligon_offset([(0, 0), (10, 0), (10, 10), (0, 10)], 2)
    print(f"Test 7 - CCW 10x10 içeri 2 = {sonuc}")
    print(f"         beklenen ≈ [(2,2),(8,2),(8,8),(2,8)]")
    beklenen_7 = [(2, 2), (8, 2), (8, 8), (2, 8)]
    tum_dogru = all(
        abs(sonuc[i][0] - beklenen_7[i][0]) < 0.01 and
        abs(sonuc[i][1] - beklenen_7[i][1]) < 0.01
        for i in range(4)
    )
    print(f"         Sonuç: {'✓' if tum_dogru else '✗'}")

    # TEST 8: poligon_offset (CW, 10x10 ters sıra → yine 6x6 içeri)
    sonuc = gu.poligon_offset([(0, 0), (0, 10), (10, 10), (10, 0)], 2)
    print(f"Test 8 - CW 10x10 içeri 2 = {sonuc}")
    print(f"         (köşe sırası farklı ama sonuç içeri gitmeli)")
    alan_kontrol = gu.poligon_alani(sonuc)
    print(f"         Sonuç alanı: {alan_kontrol:.1f}  beklenen≈36.0  {'✓' if abs(alan_kontrol - 36.0) < 0.1 else '✗'}")

    # TEST 9: poligon_offset (dışarı - negatif mesafe)
    sonuc = gu.poligon_offset([(0, 0), (10, 0), (10, 10), (0, 10)], -2)
    alan_kontrol = gu.poligon_alani(sonuc)
    print(f"Test 9 - 10x10 dışarı 2 (negatif mesafe)")
    print(f"         Alan = {alan_kontrol:.1f}  beklenen≈196.0 (14x14)  {'✓' if abs(alan_kontrol - 196.0) < 0.1 else '✗'}")

    # TEST 10: YetersizKoseHatasi fırlatıyor mu?
    try:
        gu.poligon_alani([(0, 0), (1, 1)])
        print("Test 10 - 2 köşeli poligon alanı ✗ (hata fırlatmadı)")
    except Exception:
        print("Test 10 - 2 köşe → YetersizKoseHatasi fırlatıldı ✓")

    print("=" * 50)
    print("Test tamamlandı.")


def test_kenar_bazli_offset():
    gu = GeometryUtils()

    print("="*50)
    print("Kenar Bazlı Offset Testleri")
    print("="*50)

    # TEST 1: 10x10 kare, tüm kenarlar eşit 2m
    # Beklenen: 6x6 kare, köşeler (2,2), (8,2), (8,8), (2,8)
    sonuc = gu.poligon_offset_kenar_bazli(
        [(0,0),(10,0),(10,10),(0,10)],
        [2, 2, 2, 2]
    )
    beklenen = [(2,2),(8,2),(8,8),(2,8)]
    tum_dogru = all(
        abs(sonuc[i][0]-beklenen[i][0])<0.01 and abs(sonuc[i][1]-beklenen[i][1])<0.01
        for i in range(4)
    )
    print(f"Test 1 - Eşit 2m: {'✓' if tum_dogru else '✗'}")
    print(f"  Sonuç: {sonuc}")

    # TEST 2: 12x10 dikdörtgen, mesafeler [3,2,3,2]
    # Beklenen: 8x4 dikdörtgen merkezi, köşeler (2,3), (10,3), (10,7), (2,7)
    sonuc = gu.poligon_offset_kenar_bazli(
        [(0,0),(12,0),(12,10),(0,10)],
        [3, 2, 3, 2]
    )
    beklenen = [(2,3),(10,3),(10,7),(2,7)]
    tum_dogru = all(
        abs(sonuc[i][0]-beklenen[i][0])<0.01 and abs(sonuc[i][1]-beklenen[i][1])<0.01
        for i in range(4)
    )
    print(f"Test 2 - Farklı mesafeler [3,2,3,2]: {'✓' if tum_dogru else '✗'}")
    print(f"  Sonuç: {sonuc}")

    # TEST 3: 25x20 arsa, ön bahçe 5m, yan/arka 3m
    # Arsa: alt(ön)=5m, sağ(yan)=3, üst(arka)=3, sol(yan)=3
    # Beklenen: 19 geniş, 12 derin (sol-sağ: 25-3-3=19, alt-üst: 20-5-3=12)
    # Köşeler: (3,5), (22,5), (22,17), (3,17)
    sonuc = gu.poligon_offset_kenar_bazli(
        [(0,0),(25,0),(25,20),(0,20)],
        [5, 3, 3, 3]
    )
    beklenen = [(3,5),(22,5),(22,17),(3,17)]
    tum_dogru = all(
        abs(sonuc[i][0]-beklenen[i][0])<0.01 and abs(sonuc[i][1]-beklenen[i][1])<0.01
        for i in range(4)
    )
    print(f"Test 3 - Gerçek arsa (ön:5, yan:3, arka:3): {'✓' if tum_dogru else '✗'}")
    print(f"  Sonuç: {sonuc}")
    alan = gu.poligon_alani(sonuc)
    print(f"  Alan: {alan:.2f} m² (beklenen: 228)")

    # TEST 4: CW poligon (ters sıra) aynı sonuç vermeli
    # Kare ters sıra ile: [(0,0),(0,10),(10,10),(10,0)]
    sonuc = gu.poligon_offset_kenar_bazli(
        [(0,0),(0,10),(10,10),(10,0)],
        [2, 2, 2, 2]
    )
    alan = gu.poligon_alani(sonuc)
    print(f"Test 4 - CW poligon 2m içeri: Alan={alan:.2f} (beklenen: 36) {'✓' if abs(alan-36)<0.1 else '✗'}")

    # TEST 5: Uzunluk eşitsizliği
    try:
        gu.poligon_offset_kenar_bazli([(0,0),(10,0),(10,10),(0,10)], [2, 2, 2])
        print("Test 5 - 3 mesafe vermek: ✗ (hata fırlatmadı)")
    except ValueError:
        print("Test 5 - 3 mesafe → ValueError ✓")

    # TEST 6: Üçgen arsa, her kenara farklı mesafe
    sonuc = gu.poligon_offset_kenar_bazli(
        [(0,0),(20,0),(10,15)],
        [2, 2, 2]
    )
    alan_orj = gu.poligon_alani([(0,0),(20,0),(10,15)])
    alan_yeni = gu.poligon_alani(sonuc)
    print(f"Test 6 - Üçgen 2m içeri: Orijinal alan={alan_orj:.2f}, Yeni alan={alan_yeni:.2f} {'✓' if alan_yeni < alan_orj else '✗'}")
    print(f"  Sonuç köşeleri: {sonuc}")

    print("="*50)
    print("Kenar bazlı offset testleri tamamlandı.")


if __name__ == "__main__":
    test_geometri()
    test_kenar_bazli_offset()
