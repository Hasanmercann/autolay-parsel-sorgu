"""
imar_hesap.py — ImarHesap modülü

TAKS, KAKS (emsal) ve emsal harici alan hesaplarını yapar.

Bu modül ÇİZİM yapmaz, yalnızca hesap yapar.
Sonuçlar MimariVeriler'den okunur ve rapor olarak döndürülür.

Bağımlılıklar:
    - MimariVeriler   : Girdi verisi
    - GeometryUtils   : Arsa alanı hesabı
    - logger_olustur  : Loglama
"""

from autolay.mimari.veriler import MimariVeriler
from autolay.utils.geometri import GeometryUtils
from autolay.utils.logger import logger_olustur


class ImarHesap:
    """
    Mimari ruhsat projesi için TAKS/KAKS (emsal) hesaplarını yapar.

    Kullanım sırası:
        1. MimariVeriler nesnesi oluştur (taks, kaks, kat_sayisi dolu olmalı)
        2. ImarHesap(veri) ile nesne oluştur
        3. hesapla() ile tüm hesapları yap
        4. rapor() ile okunabilir özeti al
        5. uyarilar() ile sınır aşımı kontrollerini gör

    Formüller (Planlı Alanlar İmar Yönetmeliği):
        - Arsa Alanı = Shoelace ile köşelerden
        - Maks Taban Alanı = Arsa × TAKS
        - Emsal İçi İnşaat = Arsa × KAKS
        - Emsal Harici Limit = Emsal İçi × 0.30 (Madde 22)
        - Toplam Maks İnşaat = Emsal İçi + Emsal Harici
        - Ortalama Kat Alanı = Emsal İçi / Kat Sayısı
    """

    def __init__(self, veri: MimariVeriler):
        """
        ImarHesap nesnesini başlatır.

        Parametreler:
            veri (MimariVeriler): Proje verileri. taks ve kaks DOLU olmalı.

        Hata:
            ValueError: veri.taks veya veri.kaks None ise.
        """
        self.log = logger_olustur(__name__)
        self.veri = veri
        self.geo = GeometryUtils()

        # TAKS ve KAKS zorunlu
        if veri.taks is None:
            raise ValueError("ImarHesap için veri.taks tanımlı olmalı.")
        if veri.kaks is None:
            raise ValueError("ImarHesap için veri.kaks tanımlı olmalı.")

        # Hesaplanan değerler — hesapla() çağrıldıktan sonra dolar
        self._arsa_alani = None
        self._maks_taban_alani = None
        self._maks_insaat_emsal_ici = None
        self._maks_emsal_harici = None
        self._maks_toplam_insaat = None
        self._ortalama_kat_alani = None
        self._hesaplandi = False

    def hesapla(self):
        """
        Tüm imar hesaplarını yapar ve iç değişkenlerde saklar.

        Formüller:
            arsa_alani          = Shoelace(koseler)
            maks_taban_alani    = arsa_alani × taks
            maks_insaat_ici     = arsa_alani × kaks
            maks_emsal_harici   = maks_insaat_ici × emsal_harici_orani
            maks_toplam_insaat  = maks_insaat_ici + maks_emsal_harici
            ortalama_kat_alani  = maks_insaat_ici / kat_sayisi
        """
        # Adım 1: Arsa alanı
        self._arsa_alani = self.geo.poligon_alani(self.veri.arsa_koseleri)

        # Adım 2: Maks taban alanı (TAKS kuralı)
        self._maks_taban_alani = self._arsa_alani * self.veri.taks

        # Adım 3: Maks inşaat alanı (emsal içi, KAKS kuralı)
        self._maks_insaat_emsal_ici = self._arsa_alani * self.veri.kaks

        # Adım 4: Maks emsal harici (emsal içinin %30'u)
        self._maks_emsal_harici = (
            self._maks_insaat_emsal_ici * self.veri.emsal_harici_orani
        )

        # Adım 5: Toplam maks inşaat
        self._maks_toplam_insaat = (
            self._maks_insaat_emsal_ici + self._maks_emsal_harici
        )

        # Adım 6: Ortalama kat alanı
        self._ortalama_kat_alani = (
            self._maks_insaat_emsal_ici / self.veri.kat_sayisi
        )

        self._hesaplandi = True

        self.log.info(
            f"İmar hesabı tamamlandı: "
            f"arsa={self._arsa_alani:.2f}m², "
            f"maks_taban={self._maks_taban_alani:.2f}m², "
            f"emsal_ici={self._maks_insaat_emsal_ici:.2f}m², "
            f"emsal_harici={self._maks_emsal_harici:.2f}m²"
        )

    # --- Okuma metodları (hesapla çağrılmış olmalı) ---

    def _hesaplanmis_mi(self):
        """Hesapla çağrılmadıysa hata fırlatır."""
        if not self._hesaplandi:
            raise RuntimeError("Önce hesapla() çağrılmalı.")

    def arsa_alani(self) -> float:
        """Arsa toplam alanı (m²)."""
        self._hesaplanmis_mi()
        return self._arsa_alani

    def maks_taban_alani(self) -> float:
        """Binanın zemin katta kaplayabileceği maksimum alan (m²)."""
        self._hesaplanmis_mi()
        return self._maks_taban_alani

    def maks_insaat_emsal_ici(self) -> float:
        """Emsal içi maksimum toplam inşaat alanı (m²)."""
        self._hesaplanmis_mi()
        return self._maks_insaat_emsal_ici

    def maks_emsal_harici(self) -> float:
        """Emsal harici maksimum alan (balkon, çıkma, bodrum depoları vb.)."""
        self._hesaplanmis_mi()
        return self._maks_emsal_harici

    def maks_toplam_insaat(self) -> float:
        """Emsal içi + emsal harici toplam maksimum inşaat (m²)."""
        self._hesaplanmis_mi()
        return self._maks_toplam_insaat

    def ortalama_kat_alani(self) -> float:
        """Emsal içi alanın kat sayısına bölünmüş hali (m²)."""
        self._hesaplanmis_mi()
        return self._ortalama_kat_alani

    def rapor(self) -> str:
        """
        Mimar için okunabilir rapor metni döner.

        Dönüş:
            str: Çok satırlı formatlanmış özet.
        """
        self._hesaplanmis_mi()

        satirlar = [
            "=== İmar Hesabı Raporu ===",
            f"Arsa alanı              : {self._arsa_alani:.2f} m²",
            f"TAKS                    : {self.veri.taks} ({self.veri.taks*100:.0f}%)",
            f"KAKS (Emsal)            : {self.veri.kaks}",
            f"Kat sayısı              : {self.veri.kat_sayisi}",
            "",
            f"Maks. taban alanı       : {self._maks_taban_alani:.2f} m²",
            f"Maks. emsal içi inşaat  : {self._maks_insaat_emsal_ici:.2f} m²",
            f"Maks. emsal harici      : {self._maks_emsal_harici:.2f} m² "
            f"(emsal içinin %{self.veri.emsal_harici_orani*100:.0f}'ı)",
            f"Maks. toplam inşaat     : {self._maks_toplam_insaat:.2f} m²",
            f"Ortalama kat alanı      : {self._ortalama_kat_alani:.2f} m²",
        ]
        return "\n".join(satirlar)

    def uyarilar(self) -> list:
        """
        Potansiyel sorunları liste halinde döner.

        Kontroller:
            - Ortalama kat alanı maks tabanı aşıyorsa (yapılamaz)
            - TAKS çok yüksek (>0.6) veya çok düşük (<0.1)
            - KAKS çok düşük (<0.3) veya çok yüksek (>4.0)

        Dönüş:
            list[str]: Uyarı mesajları. Sorun yoksa boş liste.
        """
        self._hesaplanmis_mi()
        uyarilar = []

        # Ortalama kat maks tabanı aşıyor mu?
        if self._ortalama_kat_alani > self._maks_taban_alani:
            uyarilar.append(
                f"⚠ Ortalama kat alanı ({self._ortalama_kat_alani:.2f} m²) "
                f"maks taban alanını ({self._maks_taban_alani:.2f} m²) aşıyor. "
                f"Mevcut TAKS/KAKS/kat kombinasyonu uygulanamaz."
            )

        # TAKS ekstrem değerler
        if self.veri.taks > 0.6:
            uyarilar.append(
                f"⚠ TAKS çok yüksek ({self.veri.taks}). "
                f"Açık alan gereksinimleri kontrol edilmeli."
            )
        if self.veri.taks < 0.1:
            uyarilar.append(
                f"⚠ TAKS çok düşük ({self.veri.taks}). "
                f"Ekonomik uygulama zor olabilir."
            )

        # KAKS ekstrem değerler
        if self.veri.kaks > 4.0:
            uyarilar.append(
                f"⚠ KAKS çok yüksek ({self.veri.kaks}). "
                f"Plan notlarını ve kat yüksekliğini kontrol edin."
            )
        if self.veri.kaks < 0.3:
            uyarilar.append(
                f"⚠ KAKS çok düşük ({self.veri.kaks})."
            )

        return uyarilar
