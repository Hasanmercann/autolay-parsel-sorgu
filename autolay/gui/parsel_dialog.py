"""
autolay/gui/parsel_dialog.py

Parsel bilgisi giriş penceresi.

Il/ilçe/mahalle dropdown'ları tkgm_idler.json'dan dinamik olarak dolar.
Ada ve parsel numaraları klavyeyle girilir.

Kullanım:
    from autolay.gui.parsel_dialog import parsel_bilgisi_al

    sonuc = parsel_bilgisi_al()
    if sonuc:
        il, ilce, mahalle, ada, parsel = sonuc
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

_ONBELLEK_YOLU = os.path.join(
    os.path.dirname(__file__), "..", "tkgm", "idler.json"
)


def _idleri_yukle() -> dict:
    if not os.path.exists(_ONBELLEK_YOLU):
        return {}
    with open(_ONBELLEK_YOLU, encoding="utf-8") as f:
        return json.load(f)


class ParselDialog:
    """
    Parsel bilgisi giriş penceresi.

    Kullanım:
        dialog = ParselDialog()
        sonuc = dialog.goster()
        # sonuc: (il, ilce, mahalle, ada, parsel) veya None (iptal)
    """

    def __init__(self):
        self._idler = _idleri_yukle()
        self._sonuc = None

        self._root = tk.Tk()
        self._root.title("AutoLay — Parsel Sorgula")
        self._root.resizable(False, False)
        self._root.configure(bg="#f0f0f0")

        # Ekran ortasına taşı
        self._root.update_idletasks()
        genislik, yukseklik = 400, 340
        x = (self._root.winfo_screenwidth() - genislik) // 2
        y = (self._root.winfo_screenheight() - yukseklik) // 2
        self._root.geometry(f"{genislik}x{yukseklik}+{x}+{y}")

        self._arayuz_olustur()

    def _arayuz_olustur(self):
        ana = tk.Frame(self._root, bg="#f0f0f0", padx=20, pady=15)
        ana.pack(fill=tk.BOTH, expand=True)

        # Başlık
        baslik = tk.Label(
            ana,
            text="Parsel Bilgilerini Girin",
            font=("Segoe UI", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
        )
        baslik.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

        etiket_font = ("Segoe UI", 9)
        widget_font = ("Segoe UI", 9)

        # Il
        tk.Label(ana, text="İl:", font=etiket_font, bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=4
        )
        self._il_var = tk.StringVar()
        self._il_cb = ttk.Combobox(
            ana, textvariable=self._il_var, font=widget_font,
            width=28, state="readonly"
        )
        self._il_cb.grid(row=1, column=1, sticky="ew", pady=4)
        self._il_cb.bind("<<ComboboxSelected>>", self._il_degisti)

        # İlçe
        tk.Label(ana, text="İlçe:", font=etiket_font, bg="#f0f0f0").grid(
            row=2, column=0, sticky="w", pady=4
        )
        self._ilce_var = tk.StringVar()
        self._ilce_cb = ttk.Combobox(
            ana, textvariable=self._ilce_var, font=widget_font,
            width=28, state="readonly"
        )
        self._ilce_cb.grid(row=2, column=1, sticky="ew", pady=4)
        self._ilce_cb.bind("<<ComboboxSelected>>", self._ilce_degisti)

        # Mahalle
        tk.Label(ana, text="Mahalle:", font=etiket_font, bg="#f0f0f0").grid(
            row=3, column=0, sticky="w", pady=4
        )
        self._mahalle_var = tk.StringVar()
        self._mahalle_cb = ttk.Combobox(
            ana, textvariable=self._mahalle_var, font=widget_font,
            width=28, state="readonly"
        )
        self._mahalle_cb.grid(row=3, column=1, sticky="ew", pady=4)

        # Ayraç
        ttk.Separator(ana, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=10
        )

        # Ada
        tk.Label(ana, text="Ada No:", font=etiket_font, bg="#f0f0f0").grid(
            row=5, column=0, sticky="w", pady=4
        )
        self._ada_var = tk.StringVar()
        ada_entry = ttk.Entry(ana, textvariable=self._ada_var, font=widget_font, width=30)
        ada_entry.grid(row=5, column=1, sticky="ew", pady=4)

        # Parsel
        tk.Label(ana, text="Parsel No:", font=etiket_font, bg="#f0f0f0").grid(
            row=6, column=0, sticky="w", pady=4
        )
        self._parsel_var = tk.StringVar()
        parsel_entry = ttk.Entry(
            ana, textvariable=self._parsel_var, font=widget_font, width=30
        )
        parsel_entry.grid(row=6, column=1, sticky="ew", pady=4)

        # Enter tuşu sorgula butonuna bassın
        self._root.bind("<Return>", lambda e: self._sorgula())

        # Butonlar
        btn_cerceve = tk.Frame(ana, bg="#f0f0f0")
        btn_cerceve.grid(row=7, column=0, columnspan=2, pady=(15, 0), sticky="e")

        ttk.Button(btn_cerceve, text="İptal", width=10, command=self._iptal).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        sorgula_btn = ttk.Button(
            btn_cerceve, text="Sorgula →", width=12, command=self._sorgula
        )
        sorgula_btn.pack(side=tk.RIGHT)

        ana.columnconfigure(1, weight=1)

        # İl listesini doldur
        iller = sorted(self._idler.keys())
        self._il_cb["values"] = iller
        if iller:
            self._il_cb.current(0)
            self._il_degisti()

    def _il_degisti(self, event=None):
        il = self._il_var.get()
        ilceler = sorted(
            self._idler.get(il, {}).get("ilceler", {}).keys()
        )
        self._ilce_cb["values"] = ilceler
        self._ilce_var.set("")
        self._mahalle_cb["values"] = []
        self._mahalle_var.set("")
        if ilceler:
            self._ilce_cb.current(0)
            self._ilce_degisti()

    def _ilce_degisti(self, event=None):
        il = self._il_var.get()
        ilce = self._ilce_var.get()
        mahalleler = sorted(
            self._idler.get(il, {})
            .get("ilceler", {})
            .get(ilce, {})
            .get("mahalleler", {})
            .keys()
        )
        self._mahalle_cb["values"] = mahalleler
        self._mahalle_var.set("")
        if mahalleler:
            self._mahalle_cb.current(0)

    def _sorgula(self):
        il = self._il_var.get().strip()
        ilce = self._ilce_var.get().strip()
        mahalle = self._mahalle_var.get().strip()
        ada = self._ada_var.get().strip()
        parsel = self._parsel_var.get().strip()

        if not il:
            messagebox.showwarning("Eksik Bilgi", "Lütfen bir il seçin.", parent=self._root)
            return
        if not ilce:
            messagebox.showwarning("Eksik Bilgi", "Lütfen bir ilçe seçin.", parent=self._root)
            return
        if not mahalle:
            messagebox.showwarning("Eksik Bilgi", "Lütfen bir mahalle seçin.", parent=self._root)
            return
        if not ada:
            messagebox.showwarning("Eksik Bilgi", "Ada numarasını girin.", parent=self._root)
            return
        if not parsel:
            messagebox.showwarning("Eksik Bilgi", "Parsel numarasını girin.", parent=self._root)
            return
        if not ada.isdigit():
            messagebox.showwarning("Geçersiz Değer", "Ada numarası rakam olmalıdır.", parent=self._root)
            return
        if not parsel.isdigit():
            messagebox.showwarning("Geçersiz Değer", "Parsel numarası rakam olmalıdır.", parent=self._root)
            return

        self._sonuc = (il, ilce, mahalle, ada, parsel)
        self._root.destroy()

    def _iptal(self):
        self._sonuc = None
        self._root.destroy()

    def goster(self):
        """
        Pencereyi açar ve kullanıcı girişini döndürür.

        Dönüş:
            tuple (il, ilce, mahalle, ada, parsel) — Sorgula butonuna basıldıysa
            None — İptal edildiyse veya pencere kapatıldıysa
        """
        self._root.mainloop()
        return self._sonuc


def parsel_bilgisi_al() -> tuple | None:
    """
    Parsel bilgisi giriş penceresini açar.

    Dönüş:
        (il, ilce, mahalle, ada, parsel) tuple veya None (iptal)

    Hata:
        RuntimeError: tkgm_idler.json bulunamazsa
    """
    idler = _idleri_yukle()
    if not idler:
        raise RuntimeError(
            "tkgm_idler.json bulunamadı veya boş.\n"
            "En az bir il için şunu çalıştırın:\n"
            "  python tests/tkgm_id_olustur_hizli.py KONYA"
        )

    dialog = ParselDialog()
    return dialog.goster()


if __name__ == "__main__":
    # Standalone test
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    sonuc = parsel_bilgisi_al()
    if sonuc:
        print(f"Seçilen: il={sonuc[0]}, ilçe={sonuc[1]}, mahalle={sonuc[2]}, ada={sonuc[3]}, parsel={sonuc[4]}")
    else:
        print("İptal edildi.")
