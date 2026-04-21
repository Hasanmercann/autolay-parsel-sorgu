"""
autolay/gui/parsel_dialog.py

Parsel çizici penceresi.

AutoCAD connector'ı alır; il/ilçe/mahalle seçimi, TKGM sorgusu ve
AutoCAD'e çizimi tek pencerede yönetir. Birden fazla parsel arka arkaya
çizilebilir; pencereyi kapatmak için "Kapat" butonu kullanılır.

Kullanım:
    from autolay.gui.parsel_dialog import parsel_bilgisi_al
    parsel_bilgisi_al(connector)
"""

import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pythoncom

from autolay.tkgm.okuyucu import TKGMOkuyucu
from autolay.cizim.shapes import GeometryDrawer
from autolay.cizim.layers import LayerManager

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
    Parsel çizici penceresi.

    connector: AutoCADConnector — açık ve bağlı connector nesnesi
    """

    def __init__(self, connector):
        self._connector = connector
        self._idler = _idleri_yukle()

        self._root = tk.Tk()
        self._root.title("AutoLay — Parsel Çizici")
        self._root.resizable(False, False)
        self._root.configure(bg="#f5f5f5")

        genislik, yukseklik = 440, 420
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth() - genislik) // 2
        y = (self._root.winfo_screenheight() - yukseklik) // 2
        self._root.geometry(f"{genislik}x{yukseklik}+{x}+{y}")

        self._arayuz_olustur()

    def _arayuz_olustur(self):
        # --- Üst başlık şeridi ---
        ust = tk.Frame(self._root, bg="#2c3e50", pady=8)
        ust.pack(fill=tk.X)

        tk.Label(
            ust,
            text="AutoLay  —  TKGM Parsel Çizici",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50", fg="white",
        ).pack(side=tk.LEFT, padx=15)

        # AutoCAD bağlantı durumu
        try:
            dosya = self._connector.dosya_adi()
            acad_text = f"AutoCAD: {dosya}  ✓"
            acad_renk = "#2ecc71"
        except Exception:
            acad_text = "AutoCAD: bağlı değil"
            acad_renk = "#e74c3c"

        tk.Label(
            ust, text=acad_text,
            font=("Segoe UI", 8),
            bg="#2c3e50", fg=acad_renk,
        ).pack(side=tk.RIGHT, padx=15)

        # --- Form alanları ---
        ana = tk.Frame(self._root, bg="#f5f5f5", padx=20, pady=15)
        ana.pack(fill=tk.BOTH, expand=True)

        ef = ("Segoe UI", 9)

        def satir(etiket, satir_no):
            tk.Label(ana, text=etiket, font=ef, bg="#f5f5f5").grid(
                row=satir_no, column=0, sticky="w", pady=4
            )

        # İl
        satir("İl:", 0)
        self._il_var = tk.StringVar()
        self._il_cb = ttk.Combobox(ana, textvariable=self._il_var, font=ef, width=32, state="readonly")
        self._il_cb.grid(row=0, column=1, sticky="ew", pady=4)
        self._il_cb.bind("<<ComboboxSelected>>", self._il_degisti)

        # İlçe
        satir("İlçe:", 1)
        self._ilce_var = tk.StringVar()
        self._ilce_cb = ttk.Combobox(ana, textvariable=self._ilce_var, font=ef, width=32, state="readonly")
        self._ilce_cb.grid(row=1, column=1, sticky="ew", pady=4)
        self._ilce_cb.bind("<<ComboboxSelected>>", self._ilce_degisti)

        # Mahalle
        satir("Mahalle:", 2)
        self._mahalle_var = tk.StringVar()
        self._mahalle_cb = ttk.Combobox(ana, textvariable=self._mahalle_var, font=ef, width=32, state="readonly")
        self._mahalle_cb.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Separator(ana, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)

        # Ada
        satir("Ada No:", 4)
        self._ada_var = tk.StringVar()
        ttk.Entry(ana, textvariable=self._ada_var, font=ef, width=34).grid(row=4, column=1, sticky="ew", pady=4)

        # Parsel
        satir("Parsel No:", 5)
        self._parsel_var = tk.StringVar()
        ttk.Entry(ana, textvariable=self._parsel_var, font=ef, width=34).grid(row=5, column=1, sticky="ew", pady=4)

        # Sonuç / durum etiketi
        self._sonuc_var = tk.StringVar(value="")
        self._sonuc_label = tk.Label(
            ana, textvariable=self._sonuc_var,
            font=("Segoe UI", 9, "italic"),
            bg="#f5f5f5", fg="#555555",
            wraplength=360, justify="left",
        )
        self._sonuc_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Butonlar
        btn_f = tk.Frame(ana, bg="#f5f5f5")
        btn_f.grid(row=7, column=0, columnspan=2, pady=(12, 0), sticky="e")

        ttk.Button(btn_f, text="Kapat", width=10, command=self._kapat).pack(side=tk.RIGHT, padx=(8, 0))
        self._ciz_btn = ttk.Button(btn_f, text="Çiz  →", width=12, command=self._ciz)
        self._ciz_btn.pack(side=tk.RIGHT)

        ana.columnconfigure(1, weight=1)
        self._root.bind("<Return>", lambda e: self._ciz())

        # Dropdown'ları doldur
        iller = sorted(self._idler.keys())
        self._il_cb["values"] = iller
        if iller:
            self._il_cb.current(0)
            self._il_degisti()

    # --- Dropdown değişim olayları ---

    def _il_degisti(self, event=None):
        il = self._il_var.get()
        ilceler = sorted(self._idler.get(il, {}).get("ilceler", {}).keys())
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
            self._idler.get(il, {}).get("ilceler", {}).get(ilce, {}).get("mahalleler", {}).keys()
        )
        self._mahalle_cb["values"] = mahalleler
        self._mahalle_var.set("")
        if mahalleler:
            self._mahalle_cb.current(0)

    # --- Çiz butonu ---

    def _ciz(self):
        il = self._il_var.get().strip()
        ilce = self._ilce_var.get().strip()
        mahalle = self._mahalle_var.get().strip()
        ada = self._ada_var.get().strip()
        parsel = self._parsel_var.get().strip()

        if not all([il, ilce, mahalle, ada, parsel]):
            messagebox.showwarning("Eksik Bilgi", "Tüm alanları doldurun.", parent=self._root)
            return
        if not ada.isdigit():
            messagebox.showwarning("Geçersiz", "Ada numarası rakam olmalıdır.", parent=self._root)
            return
        if not parsel.isdigit():
            messagebox.showwarning("Geçersiz", "Parsel numarası rakam olmalıdır.", parent=self._root)
            return

        self._ciz_btn.config(state="disabled")
        self._sonuc_label.config(fg="#e67e22")
        self._sonuc_var.set("TKGM'den koordinatlar çekiliyor...")
        self._root.update_idletasks()

        threading.Thread(
            target=self._ciz_thread,
            args=(il, ilce, mahalle, ada, parsel),
            daemon=True,
        ).start()

    def _ciz_thread(self, il, ilce, mahalle, ada, parsel):
        pythoncom.CoInitialize()
        try:
            from autolay.core.baglanti import AutoCADConnector
            connector = AutoCADConnector()
            connector.baglan()

            sonuc = TKGMOkuyucu().parsel_sorgula(il, ilce, mahalle, ada, parsel)

            katman = "TKGM-ARSA"
            LayerManager(connector).katman_olustur(katman, renk="yesil")
            LayerManager(connector).aktif_katman_yap(katman)
            GeometryDrawer(connector).lwpoligon_ciz(sonuc.koseler)
            connector.aktif_cizim().Application.ZoomExtents()

            self._root.after(0, lambda: self._ciz_tamam(sonuc))
        except Exception as e:
            self._root.after(0, lambda err=str(e): self._ciz_hata(err))
        finally:
            pythoncom.CoUninitialize()

    def _ciz_tamam(self, sonuc):
        self._sonuc_var.set(
            f"✓  Çizildi!   {len(sonuc.koseler)} köşe  |  Alan ≈ {sonuc.alan_m2:.1f} m²  |  Katman: TKGM-ARSA"
        )
        self._sonuc_label.config(fg="#27ae60")
        self._ciz_btn.config(state="normal")

    def _ciz_hata(self, hata):
        self._sonuc_var.set(f"✗  Hata: {hata}")
        self._sonuc_label.config(fg="#c0392b")
        self._ciz_btn.config(state="normal")

    def _kapat(self):
        self._root.destroy()

    def goster(self):
        self._root.mainloop()


def parsel_bilgisi_al(connector) -> None:
    """
    Parsel çizici penceresini açar.

    connector: Bağlı AutoCADConnector nesnesi.
    TKGM sorgusu ve AutoCAD çizimi pencere içinden yapılır.
    """
    idler = _idleri_yukle()
    if not idler:
        raise RuntimeError(
            "idler.json bulunamadı veya boş.\n"
            "Önce şunu çalıştırın:\n"
            "  python autolay/tkgm/id_olustur.py KONYA"
        )
    ParselDialog(connector).goster()


