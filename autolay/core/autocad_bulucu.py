"""
autolay/core/autocad_bulucu.py

Windows Registry'de AutoCAD kurulumunu arar ve gerekirse başlatır.
EXE yolu bilgisayardan bilgisayara farklı olduğundan sabit yol kullanılmaz.
"""

import os
import time
import winreg
import subprocess

import win32com.client

from autolay.utils.logger import logger_olustur

log = logger_olustur(__name__)

# Registry'de AutoCAD'in bulunduğu olası konumlar
_REGISTRY_YOLLARI = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Autodesk\AutoCAD"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Autodesk\AutoCAD"),
]


def autocad_yolu_bul() -> str | None:
    """
    Windows Registry'de acad.exe yolunu arar.
    Birden fazla sürüm varsa en yenisini döndürür.

    Dönüş:
        str  — acad.exe tam yolu (varsa)
        None — bulunamazsa
    """
    for hive, reg_yol in _REGISTRY_YOLLARI:
        try:
            ana_key = winreg.OpenKey(hive, reg_yol)
        except OSError:
            continue

        # Sürümleri topla: R24.0, R25.0 vb.
        surumler = []
        i = 0
        while True:
            try:
                surumler.append(winreg.EnumKey(ana_key, i))
                i += 1
            except OSError:
                break

        # En büyük sürüm numarasını önce dene
        for surum in sorted(surumler, reverse=True):
            try:
                surum_key = winreg.OpenKey(ana_key, surum)
            except OSError:
                continue

            j = 0
            while True:
                try:
                    alt_isim = winreg.EnumKey(surum_key, j)
                except OSError:
                    break
                j += 1
                try:
                    alt_key = winreg.OpenKey(surum_key, alt_isim)
                    konum, _ = winreg.QueryValueEx(alt_key, "AcadLocation")
                    acad_exe = os.path.join(konum, "acad.exe")
                    if os.path.exists(acad_exe):
                        log.info(f"AutoCAD bulundu: {acad_exe}")
                        return acad_exe
                except (OSError, FileNotFoundError):
                    pass

    return None


def autocad_ac_ve_bekle(max_bekleme: int = 60) -> bool:
    """
    AutoCAD'i bulur, başlatır ve COM bağlantısı kurulana kadar bekler.

    Parametreler:
        max_bekleme — saniye cinsinden maksimum bekleme (varsayılan 60)

    Dönüş:
        True  — AutoCAD açıldı ve COM erişilebilir
        False — Yol bulunamadı veya süre aşıldı
    """
    yol = autocad_yolu_bul()
    if not yol:
        log.error("Registry'de AutoCAD kurulumu bulunamadı.")
        return False

    log.info(f"AutoCAD başlatılıyor: {yol}")
    subprocess.Popen([yol])

    gecen = 0
    while gecen < max_bekleme:
        time.sleep(2)
        gecen += 2
        try:
            acad = win32com.client.GetActiveObject("AutoCAD.Application")
            # Henuz DWG yoksa hemen varsayilan sablon ile ac
            if acad.Documents.Count == 0:
                acad.Documents.Add("")
                time.sleep(1)
            log.info(f"AutoCAD {gecen}s sonra hazır.")
            return True
        except Exception:
            pass

    log.error(f"AutoCAD {max_bekleme}s içinde COM'a hazır olmadı.")
    return False
