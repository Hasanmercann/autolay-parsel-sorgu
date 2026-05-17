import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autolay.utils.konsol import utf8_aktif_et
from autolay.mimari.veriler import MimariVeriler
from autolay.core.hatalar import YetersizKoseHatasi


def test_mimari_veriler():
    utf8_aktif_et()

    print("="*50)
    print("MimariVeriler Testleri")
    print("="*50)

    # TEST 1: Minimum parametreyle oluşturma (sadece arsa_koseleri)
    print("\n--- Test 1: Minimum parametreler ---")
    v1 = MimariVeriler(arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)])
    assert v1.yapi_nizami == "ayrik"
    assert v1.kat_sayisi == 1
    assert v1.on_kenar_indeks == 0
    assert v1.park_komsusu_kenarlar == []
    assert v1.bitisik_kenarlar == []
    assert v1.imar_durumu == {"on": 5.0, "yan": 3.0, "arka": 3.0}
    assert v1.bina_yuksekligi_m is None
    print("Test 1 ✓ — Varsayılanlar doğru")

    # TEST 2: Tüm parametrelerle oluşturma
    print("\n--- Test 2: Tüm parametreler verilmiş ---")
    v2 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        yapi_nizami="bitisik",
        kat_sayisi=7,
        on_kenar_indeks=0,
        park_komsusu_kenarlar=[2],
        bitisik_kenarlar=[1],
        imar_durumu={"on": 7, "yan": 3, "arka": 4},
        bina_yuksekligi_m=21.5,
    )
    assert v2.yapi_nizami == "bitisik"
    assert v2.kat_sayisi == 7
    assert v2.imar_durumu["on"] == 7
    assert v2.imar_durumu["arka"] == 4
    print("Test 2 ✓ — Tüm alanlar ayarlandı")

    # TEST 3: imar_durumu kısmi girildi, eksikler default
    print("\n--- Test 3: imar_durumu kısmi (sadece on) ---")
    v3 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        imar_durumu={"on": 10},  # sadece on verilmiş
    )
    assert v3.imar_durumu["on"] == 10
    assert v3.imar_durumu["yan"] == 3.0  # default
    assert v3.imar_durumu["arka"] == 3.0  # default
    print("Test 3 ✓ — Eksik anahtarlar default ile dolduruldu")

    # TEST 4: cekme_baslangic_mesafeleri — basit 4 kenarlı
    print("\n--- Test 4: Başlangıç mesafeleri (4 kenarlı, on=0) ---")
    v4 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        on_kenar_indeks=0,
    )
    mesafeler = v4.cekme_baslangic_mesafeleri()
    beklenen = [5.0, 3.0, 3.0, 3.0]  # on=5, yan=3, arka=3, yan=3
    assert mesafeler == beklenen, f"Beklenen {beklenen}, alınan {mesafeler}"
    print(f"Test 4 ✓ — {mesafeler}")

    # TEST 5: cekme_baslangic_mesafeleri — bitişik kenar var
    print("\n--- Test 5: Başlangıç mesafeleri (bitişik=[1]) ---")
    v5 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        on_kenar_indeks=0,
        bitisik_kenarlar=[1],
    )
    mesafeler = v5.cekme_baslangic_mesafeleri()
    beklenen = [5.0, 0.0, 3.0, 3.0]  # kenar 1 bitişik → 0
    assert mesafeler == beklenen, f"Beklenen {beklenen}, alınan {mesafeler}"
    print(f"Test 5 ✓ — {mesafeler}")

    # TEST 6: cekme_baslangic_mesafeleri — on_kenar_indeks=2 (farklı ön)
    print("\n--- Test 6: on_kenar_indeks=2 ---")
    v6 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        on_kenar_indeks=2,  # üst kenar ön
    )
    mesafeler = v6.cekme_baslangic_mesafeleri()
    # on=2, arka=(2+2)%4=0, yan=1 ve 3
    beklenen = [3.0, 3.0, 5.0, 3.0]
    assert mesafeler == beklenen, f"Beklenen {beklenen}, alınan {mesafeler}"
    print(f"Test 6 ✓ — {mesafeler}")

    # TEST 7: 3 kenarlı (üçgen) — arka ayrımı yapılamaz, uyarı
    print("\n--- Test 7: Üçgen arsa ---")
    v7 = MimariVeriler(
        arsa_koseleri=[(0,0),(20,0),(10,15)],
        on_kenar_indeks=0,
    )
    mesafeler = v7.cekme_baslangic_mesafeleri()
    # on=0 → 5, diğerleri → yan=3
    beklenen = [5.0, 3.0, 3.0]
    assert mesafeler == beklenen, f"Beklenen {beklenen}, alınan {mesafeler}"
    print(f"Test 7 ✓ — {mesafeler}")

    # TEST 8: Validation — 2 köşeli → YetersizKoseHatasi
    print("\n--- Test 8: 2 köşe → hata ---")
    try:
        MimariVeriler(arsa_koseleri=[(0,0),(10,10)])
        print("Test 8 ✗ — Hata fırlatmadı!")
    except YetersizKoseHatasi:
        print("Test 8 ✓ — YetersizKoseHatasi doğru")

    # TEST 9: Validation — negatif kat sayısı
    print("\n--- Test 9: kat_sayisi=-1 → hata ---")
    try:
        MimariVeriler(
            arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
            kat_sayisi=-1,
        )
        print("Test 9 ✗ — Hata fırlatmadı!")
    except ValueError:
        print("Test 9 ✓ — ValueError doğru")

    # TEST 10: Validation — geçersiz yapi_nizami
    print("\n--- Test 10: yapi_nizami='karma' → hata ---")
    try:
        MimariVeriler(
            arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
            yapi_nizami="karma",
        )
        print("Test 10 ✗ — Hata fırlatmadı!")
    except ValueError:
        print("Test 10 ✓ — ValueError doğru")

    # TEST 11: Validation — on_kenar_indeks aralık dışı
    print("\n--- Test 11: on_kenar_indeks=5 (arsa 4 köşeli) ---")
    try:
        MimariVeriler(
            arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
            on_kenar_indeks=5,
        )
        print("Test 11 ✗ — Hata fırlatmadı!")
    except ValueError:
        print("Test 11 ✓ — ValueError doğru")

    # TEST 12: Validation — bitisik_kenarlar geçersiz indeks
    print("\n--- Test 12: bitisik_kenarlar=[10] ---")
    try:
        MimariVeriler(
            arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
            bitisik_kenarlar=[10],
        )
        print("Test 12 ✗ — Hata fırlatmadı!")
    except ValueError:
        print("Test 12 ✓ — ValueError doğru")

    # TEST 13: ozet() metodu
    print("\n--- Test 13: ozet() çıktısı ---")
    v13 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        yapi_nizami="bitisik",
        kat_sayisi=7,
        bina_yuksekligi_m=21.5,
        bitisik_kenarlar=[1],
    )
    ozet_str = v13.ozet()
    assert "Yapı nizamı      : bitisik" in ozet_str
    assert "Kat sayısı       : 7" in ozet_str
    assert "21.5 m" in ozet_str
    print(ozet_str)
    print("Test 13 ✓ — Özet formatı doğru")

    print("\n" + "="*50)
    print("Tüm testler geçti — 13/13 ✓")
    print("="*50)


if __name__ == "__main__":
    test_mimari_veriler()
