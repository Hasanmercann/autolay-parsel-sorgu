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
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pythoncom

from autolay.tkgm.okuyucu import TKGMOkuyucu
from autolay.cizim.shapes import GeometryDrawer
from autolay.cizim.layers import LayerManager


def _kaynak_yolu(goreceli: str) -> str:
    """PyInstaller EXE içinde ve normal çalışmada doğru yolu döndürür."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, goreceli)
    return os.path.join(os.path.dirname(__file__), "..", goreceli)


_ONBELLEK_YOLU = _kaynak_yolu(os.path.join("tkgm", "idler.json"))


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

        genislik, yukseklik = 720, 460
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

        # --- Yatay içerik çerçevesi ---
        icerik = tk.Frame(self._root, bg="#f5f5f5")
        icerik.pack(fill=tk.BOTH, expand=True)

        # Sol: Form alanları
        sol = tk.Frame(icerik, bg="#f5f5f5", padx=20, pady=15)
        sol.pack(side=tk.LEFT, fill=tk.BOTH)
        sol.columnconfigure(1, weight=1)

        ef = ("Segoe UI", 9)

        def satir(etiket, satir_no):
            tk.Label(sol, text=etiket, font=ef, bg="#f5f5f5").grid(
                row=satir_no, column=0, sticky="w", pady=4
            )

        satir("İl:", 0)
        self._il_var = tk.StringVar()
        self._il_cb = ttk.Combobox(sol, textvariable=self._il_var, font=ef, width=30, state="readonly")
        self._il_cb.grid(row=0, column=1, sticky="ew", pady=4)
        self._il_cb.bind("<<ComboboxSelected>>", self._il_degisti)

        satir("İlçe:", 1)
        self._ilce_var = tk.StringVar()
        self._ilce_cb = ttk.Combobox(sol, textvariable=self._ilce_var, font=ef, width=30, state="readonly")
        self._ilce_cb.grid(row=1, column=1, sticky="ew", pady=4)
        self._ilce_cb.bind("<<ComboboxSelected>>", self._ilce_degisti)

        satir("Mahalle:", 2)
        self._mahalle_var = tk.StringVar()
        self._mahalle_cb = ttk.Combobox(sol, textvariable=self._mahalle_var, font=ef, width=30, state="readonly")
        self._mahalle_cb.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Separator(sol, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)

        satir("Ada No:", 4)
        self._ada_var = tk.StringVar()
        ttk.Entry(sol, textvariable=self._ada_var, font=ef, width=32).grid(row=4, column=1, sticky="ew", pady=4)

        satir("Parsel No:", 5)
        self._parsel_var = tk.StringVar()
        ttk.Entry(sol, textvariable=self._parsel_var, font=ef, width=32).grid(row=5, column=1, sticky="ew", pady=4)

        self._sonuc_var = tk.StringVar(value="")
        self._sonuc_label = tk.Label(
            sol, textvariable=self._sonuc_var,
            font=("Segoe UI", 9, "italic"),
            bg="#f5f5f5", fg="#555555",
            wraplength=340, justify="left",
        )
        self._sonuc_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

        btn_f = tk.Frame(sol, bg="#f5f5f5")
        btn_f.grid(row=7, column=0, columnspan=2, pady=(12, 0), sticky="e")

        ttk.Button(btn_f, text="Kapat", width=10, command=self._kapat).pack(side=tk.RIGHT, padx=(8, 0))
        self._kaydet_btn = ttk.Button(btn_f, text="DWG Kaydet", width=13, command=self._kaydet)
        self._kaydet_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._ciz_btn = ttk.Button(btn_f, text="Çiz  →", width=12, command=self._ciz)
        self._ciz_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._ara_btn = ttk.Button(btn_f, text="Ara", width=8, command=self._ara)
        self._ara_btn.pack(side=tk.RIGHT)

        # Sağ: Harita önizleme paneli
        ayrac = tk.Frame(icerik, bg="#cccccc", width=1)
        ayrac.pack(side=tk.LEFT, fill=tk.Y)

        sag = tk.Frame(icerik, bg="#e8e8e8", padx=12, pady=12)
        sag.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            sag, text="Harita Önizleme",
            font=("Segoe UI", 8, "bold"),
            bg="#e8e8e8", fg="#555555",
        ).pack(anchor="center")

        self._canvas = tk.Canvas(
            sag, width=240, height=240,
            bg="white", relief="sunken", bd=1,
            cursor="crosshair",
        )
        self._canvas.pack(pady=(6, 4))
        self._canvas.create_text(
            120, 120, text="Parsel seçip\n'Ara', 'Çiz' veya\n'DWG Kaydet' tıklayın",
            font=("Segoe UI", 8), fill="#aaaaaa", justify="center",
        )

        self._onizle_bilgi = tk.StringVar(value="")
        tk.Label(
            sag, textvariable=self._onizle_bilgi,
            font=("Segoe UI", 8), bg="#e8e8e8", fg="#444444",
            justify="center",
        ).pack()

        self._root.bind("<Return>", lambda e: self._ciz())

        iller = sorted(self._idler.keys())
        self._il_cb["values"] = iller
        if iller:
            self._il_cb.current(0)
            self._il_degisti()

    # --- Harita önizleme ---

    def _onizle(self, koseler, alan_m2):
        """Koordinat listesini canvas üzerinde ölçekleyerek çizer."""
        c = self._canvas
        c.delete("all")
        if len(koseler) < 2:
            return

        pad = 20
        cw, ch = 240, 240

        xs = [p[0] for p in koseler]
        ys = [p[1] for p in koseler]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        dx = max_x - min_x or 1.0
        dy = max_y - min_y or 1.0
        olcek = min((cw - 2 * pad) / dx, (ch - 2 * pad) / dy)

        ox = pad + (cw - 2 * pad - dx * olcek) / 2
        oy = pad + (ch - 2 * pad - dy * olcek) / 2

        def donustur(p):
            # Y eksenini tersle (UTM yukarı artar, canvas aşağı artar)
            return ox + (p[0] - min_x) * olcek, oy + (max_y - p[1]) * olcek

        noktalar = [donustur(p) for p in koseler]
        c.create_polygon(noktalar, outline="#1a6fad", fill="#d9eaf7", width=2)

        for px, py in noktalar:
            c.create_oval(px - 2, py - 2, px + 2, py + 2, fill="#1a6fad", outline="")

        # Alan etiketi
        cx_m = (cw / 2)
        cy_m = (ch / 2)
        c.create_text(cx_m, cy_m, text=f"{alan_m2:.0f} m²", font=("Segoe UI", 9, "bold"), fill="#1a6fad")

        self._onizle_bilgi.set(f"{len(koseler)} köşe  |  {alan_m2:.1f} m²")

    # --- Ortak yardımcılar ---

    def _butonlar_durum(self, state):
        """Ara / Çiz / DWG Kaydet butonlarını toplu enable/disable yapar."""
        self._ara_btn.config(state=state)
        self._ciz_btn.config(state=state)
        self._kaydet_btn.config(state=state)

    def _giris_dogrula(self):
        """Alanları doğrular; sorunsa uyarı gösterir ve False döner."""
        il = self._il_var.get().strip()
        ilce = self._ilce_var.get().strip()
        mahalle = self._mahalle_var.get().strip()
        ada = self._ada_var.get().strip()
        parsel = self._parsel_var.get().strip()
        if not all([il, ilce, mahalle, ada, parsel]):
            messagebox.showwarning("Eksik Bilgi", "Tüm alanları doldurun.", parent=self._root)
            return None
        if not ada.isdigit() or not parsel.isdigit():
            messagebox.showwarning("Geçersiz", "Ada ve parsel rakam olmalıdır.", parent=self._root)
            return None
        return il, ilce, mahalle, ada, parsel

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

    # --- Ara butonu (sadece harita önizleme) ---

    def _ara(self):
        alan = self._giris_dogrula()
        if alan is None:
            return
        il, ilce, mahalle, ada, parsel = alan
        self._butonlar_durum("disabled")
        self._sonuc_label.config(fg="#e67e22")
        self._sonuc_var.set("TKGM'den koordinatlar çekiliyor...")
        self._root.update_idletasks()
        threading.Thread(
            target=self._ara_thread,
            args=(il, ilce, mahalle, ada, parsel),
            daemon=True,
        ).start()

    def _ara_thread(self, il, ilce, mahalle, ada, parsel):
        try:
            sonuc = TKGMOkuyucu().parsel_sorgula(il, ilce, mahalle, ada, parsel)
            self._root.after(0, lambda: self._ara_tamam(sonuc))
        except Exception as e:
            self._root.after(0, lambda err=str(e): self._ara_hata(err))

    def _ara_tamam(self, sonuc):
        self._sonuc_var.set(
            f"✓  Bulundu!   {len(sonuc.koseler)} köşe  |  Alan ≈ {sonuc.alan_m2:.1f} m²"
        )
        self._sonuc_label.config(fg="#2980b9")
        self._butonlar_durum("normal")
        self._onizle(sonuc.koseler, sonuc.alan_m2)

    def _ara_hata(self, hata):
        self._sonuc_var.set(f"✗  Hata: {hata}")
        self._sonuc_label.config(fg="#c0392b")
        self._butonlar_durum("normal")

    # --- Çiz butonu (açık DWG'ye çizer) ---

    def _ciz(self):
        alan = self._giris_dogrula()
        if alan is None:
            return
        il, ilce, mahalle, ada, parsel = alan
        self._butonlar_durum("disabled")
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
        self._butonlar_durum("normal")
        self._onizle(sonuc.koseler, sonuc.alan_m2)

    def _ciz_hata(self, hata):
        self._sonuc_var.set(f"✗  Hata: {hata}")
        self._sonuc_label.config(fg="#c0392b")
        self._butonlar_durum("normal")

    def _kaydet(self):
        alan = self._giris_dogrula()
        if alan is None:
            return
        il, ilce, mahalle, ada, parsel = alan
        self._butonlar_durum("disabled")
        self._sonuc_label.config(fg="#e67e22")
        self._sonuc_var.set("TKGM'den koordinatlar çekiliyor...")
        self._root.update_idletasks()
        threading.Thread(
            target=self._kaydet_thread,
            args=(il, ilce, mahalle, ada, parsel),
            daemon=True,
        ).start()

    def _kaydet_thread(self, il, ilce, mahalle, ada, parsel):
        pythoncom.CoInitialize()
        doc = None
        try:
            sonuc = TKGMOkuyucu().parsel_sorgula(il, ilce, mahalle, ada, parsel)

            import win32com.client, os
            acad = win32com.client.Dispatch("AutoCAD.Application")
            doc = acad.Documents.Add()

            from autolay.core.baglanti import AutoCADConnector
            connector = AutoCADConnector()
            connector.acad = acad
            connector._bagli = True

            katman = "TKGM-ARSA"
            from autolay.cizim.layers import LayerManager
            from autolay.cizim.shapes import GeometryDrawer
            LayerManager(connector).katman_olustur(katman, renk="yesil")
            LayerManager(connector).aktif_katman_yap(katman)
            GeometryDrawer(connector).lwpoligon_ciz(sonuc.koseler)

            # Masaüstüne kaydet: ada-parsel_mahalle_il_ilce.dwg
            masaustu = os.path.join(os.path.expanduser("~"), "Desktop")
            dosya_adi = f"{ada}-{parsel}_{mahalle}_{il}_{ilce}.dwg"
            tam_yol = os.path.join(masaustu, dosya_adi)
            doc.SaveAs(tam_yol)
            doc.Close(False)
            doc = None

            self._root.after(0, lambda p=tam_yol, s=sonuc: self._kaydet_tamam(p, s))
        except Exception as e:
            if doc:
                try: doc.Close(False)
                except: pass
            self._root.after(0, lambda err=str(e): self._kaydet_hata(err))
        finally:
            pythoncom.CoUninitialize()

    def _kaydet_tamam(self, tam_yol, sonuc):
        self._sonuc_var.set(
            f"✓  Kaydedildi!   {len(sonuc.koseler)} köşe  |  Alan ≈ {sonuc.alan_m2:.1f} m²\n"
            f"   → {tam_yol}"
        )
        self._sonuc_label.config(fg="#27ae60")
        self._butonlar_durum("normal")
        self._onizle(sonuc.koseler, sonuc.alan_m2)

    def _kaydet_hata(self, hata):
        self._sonuc_var.set(f"✗  Hata: {hata}")
        self._sonuc_label.config(fg="#c0392b")
        self._butonlar_durum("normal")

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


