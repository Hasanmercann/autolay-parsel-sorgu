"""AutoLay komut satiri giris noktasi."""

from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.drawing.shapes import GeometryDrawer
from autolay.drawing.layers import LayerManager
from autolay.okuyucu.tkgm_okuyucu import TKGMOkuyucu
from autolay.gui.parsel_dialog import parsel_bilgisi_al
from autolay.utils.konsol import utf8_aktif_et


def main() -> int:
    """Uygulamayı başlatır: parsel sorgula ve AutoCAD'e çiz."""
    utf8_aktif_et()

    print("=" * 45)
    print("AutoLay — TKGM Parsel Çizici")
    print("=" * 45)

    # 1. AutoCAD bağlantısını kur
    connector = AutoCADConnector()
    try:
        baglandi = connector.baglan()
    except AktifCizimYokHatasi as hata:
        print(f"HATA: {hata}")
        return 1

    if not baglandi:
        print("HATA: AutoCAD'e bağlanılamadı. AutoCAD 2026 açık mı?")
        return 1

    print(f"AutoCAD bağlandı  : {connector.dosya_adi()}")
    print()

    # 2. Parsel bilgisi giriş penceresi
    try:
        secim = parsel_bilgisi_al()
    except RuntimeError as e:
        print(f"HATA: {e}")
        return 1

    if secim is None:
        print("İşlem iptal edildi.")
        return 0

    il, ilce, mahalle, ada, parsel = secim
    print(f"Parsel seçildi    : {il}/{ilce}/{mahalle}  Ada:{ada}  Parsel:{parsel}")

    # 3. TKGM'den koordinatları çek
    print("TKGM'den koordinatlar çekiliyor...")
    okuyucu = TKGMOkuyucu()
    try:
        sonuc = okuyucu.parsel_sorgula(il, ilce, mahalle, ada, parsel)
    except KeyError as e:
        print(f"HATA: Önbellekte bulunamadı — {e}")
        return 1
    except RuntimeError as e:
        print(f"HATA: {e}")
        return 1

    print(f"Koordinatlar alındı: {len(sonuc.koseler)} köşe, alan≈{sonuc.alan_m2:.1f} m²")

    # 4. AutoCAD'de katmanı hazırla ve çiz
    katman = "TKGM-ARSA"
    katman_yoneticisi = LayerManager(connector)
    katman_yoneticisi.katman_olustur(katman, renk="yesil")
    katman_yoneticisi.aktif_katman_yap(katman)

    cizici = GeometryDrawer(connector)
    cizici.lwpoligon_ciz(sonuc.koseler)
    connector.aktif_cizim().Application.ZoomExtents()

    print(f"AutoCAD'e çizildi  : katman '{katman}'")
    print()
    print("Tamamlandı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
