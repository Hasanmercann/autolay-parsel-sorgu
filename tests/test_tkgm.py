"""
tests/test_tkgm.py

TKGM'den parsel koordinatı çekme testi.
AutoCAD'e bağlantı gerekmez — sadece internet bağlantısı yeterli.

Çalıştırma:
    cd autolay-main
    python tests/test_tkgm.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autolay.utils.konsol import utf8_aktif_et
utf8_aktif_et()

from autolay.okuyucu.tkgm_okuyucu import TKGMOkuyucu


def test_tkgm():
    print("=" * 55)
    print("TKGM CBS API Parsel Sorgulama Testi")
    print("=" * 55)

    okuyucu = TKGMOkuyucu()

    # Test parseli: Konya / Ilgın / Tekeler  ada=175  parsel=1
    print("Sorgu: KONYA / ILGIN / TEKELER / ada=175 / parsel=1")
    print()

    try:
        sonuc = okuyucu.parsel_sorgula(
            il="KONYA",
            ilce="ILGIN",
            mahalle="TEKELER",
            ada="175",
            parsel="1",
        )
        print(f"Sonuç       : {sonuc}")
        print(f"Köşe sayısı : {len(sonuc.koseler)}")
        print(f"Alan        : {sonuc.alan_m2:.1f} m²")
        print(f"Mahalle ID  : {sonuc.mahalle_id}")
        print(f"İlk 3 köşe  :")
        for k in sonuc.koseler[:3]:
            print(f"  {k}")

        assert len(sonuc.koseler) >= 3, "En az 3 köşe bekleniyor"
        assert sonuc.alan_m2 > 0, "Alan sıfırdan büyük olmalı"
        assert sonuc.mahalle_id == "142948", f"Mahalle ID yanlış: {sonuc.mahalle_id}"

        print()
        print("TEST GEÇTI ✓")

    except KeyError as e:
        print(f"Önbellek hatası: {e}")
        print("Konya için önbellekte eksik veri var mı kontrol edin.")
    except RuntimeError as e:
        print(f"Parsel bulunamadı veya API hatası: {e}")
    except ImportError as e:
        print(f"Kurulum eksik: {e}")
    except Exception as e:
        import traceback
        print(f"Beklenmedik hata: {type(e).__name__}: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    test_tkgm()
