import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autolay.utils.konsol import utf8_aktif_et
from autolay.mimari.veriler import MimariVeriler
from autolay.mimari.imar_hesap import ImarHesap


def test_imar_hesap():
    utf8_aktif_et()

    print("="*50)
    print("ImarHesap Testleri")
    print("="*50)

    # TEST 1: Klasik örnek — 1000 m² arsa, TAKS 0.40, KAKS 2.00
    print("\n--- Test 1: 1000 m² arsa, TAKS=0.40, KAKS=2.00 ---")
    # 40x25 dikdörtgen = 1000 m²
    veri1 = MimariVeriler(
        arsa_koseleri=[(0,0),(40,0),(40,25),(0,25)],
        kat_sayisi=5,
        taks=0.40,
        kaks=2.00,
    )
    imar1 = ImarHesap(veri1)
    imar1.hesapla()

    print(f"Arsa alanı: {imar1.arsa_alani():.2f} m² (beklenen: 1000.00)")
    print(f"Maks taban: {imar1.maks_taban_alani():.2f} m² (beklenen: 400.00)")
    print(f"Emsal içi: {imar1.maks_insaat_emsal_ici():.2f} m² (beklenen: 2000.00)")
    print(f"Emsal harici: {imar1.maks_emsal_harici():.2f} m² (beklenen: 600.00)")
    print(f"Toplam inşaat: {imar1.maks_toplam_insaat():.2f} m² (beklenen: 2600.00)")
    print(f"Ortalama kat: {imar1.ortalama_kat_alani():.2f} m² (beklenen: 400.00)")

    assert abs(imar1.arsa_alani() - 1000.0) < 0.01
    assert abs(imar1.maks_taban_alani() - 400.0) < 0.01
    assert abs(imar1.maks_insaat_emsal_ici() - 2000.0) < 0.01
    assert abs(imar1.maks_emsal_harici() - 600.0) < 0.01
    assert abs(imar1.maks_toplam_insaat() - 2600.0) < 0.01
    assert abs(imar1.ortalama_kat_alani() - 400.0) < 0.01
    print("Test 1 ✓")

    # TEST 2: Küçük arsa, TAKS 0.30, KAKS 1.50
    print("\n--- Test 2: 500 m² arsa, TAKS=0.30, KAKS=1.50 ---")
    # 25x20 = 500 m²
    veri2 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        kat_sayisi=3,
        taks=0.30,
        kaks=1.50,
    )
    imar2 = ImarHesap(veri2)
    imar2.hesapla()

    # Beklenen: arsa=500, taban=150, emsal_ici=750, emsal_harici=225, toplam=975, ort_kat=250
    assert abs(imar2.arsa_alani() - 500.0) < 0.01
    assert abs(imar2.maks_taban_alani() - 150.0) < 0.01
    assert abs(imar2.maks_insaat_emsal_ici() - 750.0) < 0.01
    assert abs(imar2.maks_emsal_harici() - 225.0) < 0.01
    assert abs(imar2.ortalama_kat_alani() - 250.0) < 0.01
    print(f"Test 2 ✓ — arsa=500, taban=150, emsal_ici=750, emsal_harici=225")

    # TEST 3: TAKS None → hata
    print("\n--- Test 3: TAKS belirsiz → hata ---")
    veri3 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        kaks=1.5,  # taks verilmedi
    )
    try:
        ImarHesap(veri3)
        print("Test 3 ✗ — Hata fırlatmadı!")
    except ValueError as e:
        print(f"Test 3 ✓ — {e}")

    # TEST 4: KAKS None → hata
    print("\n--- Test 4: KAKS belirsiz → hata ---")
    veri4 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        taks=0.4,
    )
    try:
        ImarHesap(veri4)
        print("Test 4 ✗")
    except ValueError as e:
        print(f"Test 4 ✓")

    # TEST 5: hesapla() çağrılmadan değer okuma → hata
    print("\n--- Test 5: hesapla() çağrılmadan okuma ---")
    veri5 = MimariVeriler(
        arsa_koseleri=[(0,0),(25,0),(25,20),(0,20)],
        taks=0.4, kaks=1.5,
    )
    imar5 = ImarHesap(veri5)
    try:
        imar5.arsa_alani()
        print("Test 5 ✗")
    except RuntimeError:
        print("Test 5 ✓ — RuntimeError doğru")

    # TEST 6: Rapor çıktısı
    print("\n--- Test 6: Rapor ---")
    rapor = imar1.rapor()
    print(rapor)
    assert "=== İmar Hesabı Raporu ===" in rapor
    assert "1000.00 m²" in rapor
    print("Test 6 ✓")

    # TEST 7: Uyarılar — ortalama kat maks tabanı aşıyor
    print("\n--- Test 7: Uyarılar (ort kat > maks taban) ---")
    # TAKS 0.20 (küçük), KAKS 2.00 (büyük), 2 kat → emsal içi=2000, maks taban=200
    # Ortalama kat = 2000/2 = 1000 > 200 → UYARI olmalı
    veri7 = MimariVeriler(
        arsa_koseleri=[(0,0),(40,0),(40,25),(0,25)],  # 1000 m²
        kat_sayisi=2,
        taks=0.20,
        kaks=2.00,
    )
    imar7 = ImarHesap(veri7)
    imar7.hesapla()
    uyarilar = imar7.uyarilar()
    print(f"Uyarı sayısı: {len(uyarilar)}")
    for u in uyarilar:
        print(f"  {u}")
    assert any("aşıyor" in u.lower() for u in uyarilar)
    print("Test 7 ✓ — Uyarı yakalandı")

    # TEST 8: Emsal harici oranı override
    print("\n--- Test 8: Emsal harici %20 (normal %30) ---")
    veri8 = MimariVeriler(
        arsa_koseleri=[(0,0),(40,0),(40,25),(0,25)],
        kat_sayisi=5,
        taks=0.40,
        kaks=2.00,
        emsal_harici_orani=0.20,  # default 0.30 yerine 0.20
    )
    imar8 = ImarHesap(veri8)
    imar8.hesapla()
    # Emsal içi 2000, harici = 2000 × 0.20 = 400 (default %30 olsaydı 600)
    assert abs(imar8.maks_emsal_harici() - 400.0) < 0.01
    print(f"Test 8 ✓ — Emsal harici: {imar8.maks_emsal_harici():.2f} (beklenen 400)")

    print("\n" + "="*50)
    print("Tüm testler geçti — 8/8 ✓")
    print("="*50)


if __name__ == "__main__":
    test_imar_hesap()
