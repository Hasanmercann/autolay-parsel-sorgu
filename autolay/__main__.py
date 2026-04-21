"""AutoLay komut satiri giris noktasi."""

import tkinter as tk
from tkinter import messagebox

from autolay.core.baglanti import AutoCADConnector
from autolay.core.hatalar import AktifCizimYokHatasi
from autolay.core.autocad_bulucu import autocad_ac_ve_bekle
from autolay.gui.parsel_dialog import parsel_bilgisi_al
from autolay.utils.konsol import utf8_aktif_et


def _hata_goster(mesaj: str):
    """Tkinter messagebox ile hata penceresi açar."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("AutoLay — Hata", mesaj)
    root.destroy()


def main() -> int:
    utf8_aktif_et()

    print("=" * 45)
    print("AutoLay — TKGM Parsel Çizici")
    print("=" * 45)

    connector = AutoCADConnector()

    # AutoCAD bağlantısı kurulana kadar döngüde bekle
    while True:
        try:
            baglandi = connector.baglan()
        except AktifCizimYokHatasi:
            # AutoCAD açık ama DWG yok — otomatik yeni çizim aç
            print("AutoCAD açık fakat çizim yok, yeni çizim açılıyor...")
            try:
                import win32com.client
                acad = win32com.client.GetActiveObject("AutoCAD.Application")
                acad.Documents.Add("")  # bos string = varsayilan sablon, dialog acma
                import time; time.sleep(2)
            except Exception as e:
                _hata_goster(f"AutoCAD'de yeni çizim açılamadı.\nHata: {e}")
                return 1
            continue  # tekrar bağlanmayı dene

        if baglandi:
            break

        # AutoCAD hiç açık değil — otomatik aç
        print("AutoCAD bulunamadı, otomatik açılıyor...")
        acildi = autocad_ac_ve_bekle()
        if not acildi:
            _hata_goster(
                "AutoCAD bulunamadı veya açılamadı.\n\n"
                "Lütfen AutoCAD'i manuel olarak açıp tekrar deneyin."
            )
            return 1

    print(f"AutoCAD bağlandı  : {connector.dosya_adi()}")
    print()

    try:
        parsel_bilgisi_al(connector)
    except RuntimeError as e:
        _hata_goster(str(e))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

