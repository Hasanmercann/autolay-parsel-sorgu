"""
tkgm_autocad.py — TKGM'den AutoCAD'e parsel çizici

TKGM CBS API'sinden parsel koordinatlarını çeker ve açık olan
AutoCAD belgesine poligon olarak çizer.

Kullanım:
    from autolay.tkgm.cizici import tkgm_parsel_ciz

    tkgm_parsel_ciz(
        il="KONYA", ilce="ILGIN", mahalle="TEKELER",
        ada="175", parsel="1"
    )

Komut satırından:
    python -m autolay.tkgm.cizici KONYA ILGIN TEKELER 175 1
"""

import sys
import os

from autolay.core.baglanti import AutoCADConnector
from autolay.cizim.shapes import GeometryDrawer
from autolay.cizim.layers import LayerManager
from autolay.tkgm.okuyucu import TKGMOkuyucu
from autolay.utils.konsol import utf8_aktif_et
from autolay.utils.logger import logger_olustur

log = logger_olustur(__name__)


def tkgm_parsel_ciz(il: str, ilce: str, mahalle: str,
                    ada: str, parsel: str,
                    katman: str = "ARSA") -> None:
    """
    TKGM CBS API'sinden parsel koordinatlarını çeker ve AutoCAD'e çizer.

    Parametreler:
        il (str)       : İl adı  — örnek: "KONYA"
        ilce (str)     : İlçe adı — örnek: "ILGIN"
        mahalle (str)  : Mahalle adı — örnek: "TEKELER"
        ada (str)      : Ada numarası — örnek: "175"
        parsel (str)   : Parsel numarası — örnek: "1"
        katman (str)   : AutoCAD katman adı. Varsayılan: "ARSA"

    Hata:
        KeyError     : İl/ilçe/mahalle önbellekte yoksa
        RuntimeError : Parsel bulunamazsa, AutoCAD açık değilse
    """
    # 1. TKGM'den koordinatları çek
    log.info(f"TKGM sorgusu: {il}/{ilce}/{mahalle} ada={ada} parsel={parsel}")
    okuyucu = TKGMOkuyucu()
    sonuc = okuyucu.parsel_sorgula(il, ilce, mahalle, ada, parsel)

    log.info(
        f"Parsel çekildi: {len(sonuc.koseler)} köşe, "
        f"alan≈{sonuc.alan_m2:.1f} m²"
    )

    # 2. AutoCAD'e bağlan
    connector = AutoCADConnector()
    connector.baglan()

    # 3. Katmanı oluştur/aktif et
    katman_yoneticisi = LayerManager(connector)
    katman_yoneticisi.katman_olustur(katman)
    katman_yoneticisi.aktif_katman_yap(katman)

    # 4. Parseli tek kapalı polyline olarak çiz
    cizici = GeometryDrawer(connector)
    polyline = cizici.lwpoligon_ciz(sonuc.koseler)

    log.info(
        f"AutoCAD'e çizildi: kapalı polyline ({len(sonuc.koseler)} köşe), "
        f"katman='{katman}'"
    )
    print(
        f"\nParsel AutoCAD'e çizildi!\n"
        f"  {il}/{ilce}/{mahalle}  Ada:{ada}  Parsel:{parsel}\n"
        f"  Köşe: {len(sonuc.koseler)}  Alan: {sonuc.alan_m2:.1f} m²\n"
        f"  Katman: {katman}"
    )


# -------------------------------------------------------------------
if __name__ == "__main__":
    utf8_aktif_et()

    args = sys.argv[1:]
    if len(args) != 5:
        print(
            "Kullanım: python -m autolay.tkgm.cizici "
            "<IL> <ILCE> <MAHALLE> <ADA> <PARSEL>\n"
            "Örnek   : python -m autolay.tkgm.cizici "
            "KONYA ILGIN TEKELER 175 1"
        )
        sys.exit(1)

    il_, ilce_, mahalle_, ada_, parsel_ = args
    tkgm_parsel_ciz(il_, ilce_, mahalle_, ada_, parsel_)
