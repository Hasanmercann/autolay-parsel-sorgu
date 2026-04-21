"""
veriler.py — MimariVeriler modülü

Bir mimari ruhsat projesi için gereken tüm proje verilerini
tek bir yerde toplayan merkezi veri sınıfı.

Bu sınıf SADECE veri tutar ve basit doğrulama yapar.
Hesap mantığı (kademeli çekme vb.) CekmeCizici'de kalır.

Bağımlılıklar:
    - YetersizKoseHatasi : Köşe sayısı 3'ün altındaysa fırlatılır.
    - logger_olustur     : Modül düzeyinde loglama için.
"""

from autolay.core.hatalar import YetersizKoseHatasi
from autolay.utils.logger import logger_olustur
from autolay.config.sabitler import MIN_POLIGON_KOSE_SAYISI

# Geçerli yapı nizamı değerleri
_GECERLI_NIZAMLAR = {"ayrik", "bitisik", "blok"}

# Planlı Alanlar İmar Yönetmeliği Madde 23 — plan notu yoksa uygulanır
_VARSAYILAN_IMAR_DURUMU = {"on": 5.0, "yan": 3.0, "arka": 3.0}

_VARSAYILAN_EMSAL_HARICI_ORANI = 0.30  # Planlı Alanlar İmar Yönetmeliği Madde 22


class MimariVeriler:
    """
    Mimari ruhsat projesi için merkezi veri taşıyıcı sınıf.

    ArsaCizici, CekmeCizici ve ileride eklenecek modüller
    (TAKS/KAKS, VaziyetCizici vb.) bu sınıfı veri kaynağı olarak kullanır.

    Kullanım sırası:
        1. MimariVeriler(...) ile nesne oluştur.
        2. Diğer modüllere veri.arsa_koseleri, veri.kat_sayisi vb. ilet.
        3. veri.cekme_baslangic_mesafeleri() ile ilk mesafe listesini al.
        4. veri.ozet() ile proje bilgilerini logla.
    """

    def __init__(
        self,
        arsa_koseleri: list,
        yapi_nizami: str = "ayrik",
        kat_sayisi: int = 1,
        on_kenar_indeks: int = 0,
        park_komsusu_kenarlar: list = None,
        bitisik_kenarlar: list = None,
        imar_durumu: dict = None,
        bina_yuksekligi_m: float = None,
        taks: float = None,
        kaks: float = None,
        emsal_harici_orani: float = None,
    ):
        """
        MimariVeriler nesnesini başlatır ve doğrular.

        Parametreler:
            arsa_koseleri (list)          : (x, y) veya (x, y, z) tuple listesi.
                                            En az MIN_POLIGON_KOSE_SAYISI köşe
                                            gereklidir.
            yapi_nizami (str)             : "ayrik", "bitisik" veya "blok".
                                            Varsayılan: "ayrik".
            kat_sayisi (int)              : Binanın toplam kat sayısı (≥ 1).
                                            Varsayılan: 1.
            on_kenar_indeks (int)         : Ön bahçeye karşılık gelen kenarın
                                            sıfır tabanlı indeksi. Varsayılan: 0.
            park_komsusu_kenarlar (list)  : Park alanına komşu kenar indeksleri.
                                            Bu kenarlara kademeli çekme eklenmez.
                                            Varsayılan: [] (boş liste).
            bitisik_kenarlar (list)       : Komşu parsele yapışık kenar indeksleri.
                                            Bu kenarlarda çekme mesafesi 0 olur.
                                            Varsayılan: [] (boş liste).
            imar_durumu (dict)            : Plan notuna göre özel mesafeler.
                                            {"on": float, "yan": float, "arka": float}
                                            Varsayılan: {"on": 5.0, "yan": 3.0,
                                            "arka": 3.0} (mevzuat minimumu).
            bina_yuksekligi_m (float|None): Binanın toplam yüksekliği (metre).
                                            60.50m kontrolü için kullanılır.
                                            Henüz bilinmiyorsa None bırakılır.
            taks (float|None)             : Taban Alanı Katsayısı (0-1 arası).
                                            İmar hesabı için gerekli. None ise
                                            ImarHesap kullanılamaz.
            kaks (float|None)             : Kat Alanı Katsayısı / Emsal.
                                            İmar hesabı için gerekli.
            emsal_harici_orani (float)    : Emsal harici alanların toplam emsal
                                            içi alana oranı üst limiti.
                                            Varsayılan: 0.30 (Madde 22).

        Hata:
            YetersizKoseHatasi : arsa_koseleri 3'ten az köşe içeriyorsa.
            ValueError         : Diğer doğrulama hatalarında.
        """
        self.log = logger_olustur(__name__)

        # Zorunlu alan
        self.arsa_koseleri = arsa_koseleri

        # None gelirse güvenli varsayılanlara dön
        self.yapi_nizami = yapi_nizami
        self.kat_sayisi = kat_sayisi
        self.on_kenar_indeks = on_kenar_indeks
        self.park_komsusu_kenarlar = park_komsusu_kenarlar if park_komsusu_kenarlar is not None else []
        self.bitisik_kenarlar = bitisik_kenarlar if bitisik_kenarlar is not None else []
        self.bina_yuksekligi_m = bina_yuksekligi_m
        self.taks = taks
        self.kaks = kaks
        self.emsal_harici_orani = emsal_harici_orani if emsal_harici_orani is not None else _VARSAYILAN_EMSAL_HARICI_ORANI

        # imar_durumu: eksik anahtarları varsayılanla tamamla
        if imar_durumu is None:
            self.imar_durumu = dict(_VARSAYILAN_IMAR_DURUMU)
        else:
            self.imar_durumu = dict(_VARSAYILAN_IMAR_DURUMU)
            self.imar_durumu.update(imar_durumu)

        # Tüm alanlar atandıktan sonra doğrula
        self._dogrula()

    def _dogrula(self):
        """
        Tüm alanlarda tutarlılık ve geçerlilik kontrolü yapar.

        __init__ sonunda çağrılır; hata bulunursa nesne oluşturulmadan
        uygun istisna fırlatılır.

        Kontroller sırası:
            1. arsa_koseleri uzunluğu (≥ MIN_POLIGON_KOSE_SAYISI)
            2. kat_sayisi pozitifliği
            3. on_kenar_indeks aralık kontrolü
            4. bitisik_kenarlar geçerlilik kontrolü
            5. park_komsusu_kenarlar geçerlilik kontrolü
            6. yapi_nizami geçerli değer kontrolü
            7. bina_yuksekligi_m negatif kontrolü
            8. imar_durumu anahtar ve pozitif değer kontrolü
        """
        n = len(self.arsa_koseleri)

        # 1. Köşe sayısı kontrolü
        if n < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(kose_sayisi=n)

        # 2. Kat sayısı kontrolü
        if self.kat_sayisi <= 0:
            raise ValueError(
                f"kat_sayisi pozitif olmalı, verildi: {self.kat_sayisi}."
            )

        # 3. on_kenar_indeks aralık kontrolü
        if self.on_kenar_indeks < 0 or self.on_kenar_indeks >= n:
            raise ValueError(
                f"on_kenar_indeks {self.on_kenar_indeks} geçersiz. "
                f"Geçerli aralık: 0–{n - 1}."
            )

        # 4. bitisik_kenarlar indeks geçerlilik kontrolü
        for i in self.bitisik_kenarlar:
            if i < 0 or i >= n:
                raise ValueError(
                    f"bitisik_kenarlar içindeki {i} indeksi geçersiz. "
                    f"Geçerli aralık: 0–{n - 1}."
                )

        # 5. park_komsusu_kenarlar indeks geçerlilik kontrolü
        for i in self.park_komsusu_kenarlar:
            if i < 0 or i >= n:
                raise ValueError(
                    f"park_komsusu_kenarlar içindeki {i} indeksi geçersiz. "
                    f"Geçerli aralık: 0–{n - 1}."
                )

        # 6. yapi_nizami geçerli değer kontrolü
        if self.yapi_nizami not in _GECERLI_NIZAMLAR:
            raise ValueError(
                f"yapi_nizami '{self.yapi_nizami}' geçersiz. "
                f"Geçerli değerler: {sorted(_GECERLI_NIZAMLAR)}."
            )

        # 7. bina_yuksekligi_m negatif kontrolü
        if self.bina_yuksekligi_m is not None and self.bina_yuksekligi_m < 0:
            raise ValueError(
                f"bina_yuksekligi_m negatif olamaz, verildi: {self.bina_yuksekligi_m}."
            )

        # 8. imar_durumu anahtar ve pozitif değer kontrolü
        for anahtar in ("on", "yan", "arka"):
            if anahtar not in self.imar_durumu:
                raise ValueError(
                    f"imar_durumu '{anahtar}' anahtarını içermelidir."
                )
            if self.imar_durumu[anahtar] <= 0:
                raise ValueError(
                    f"imar_durumu['{anahtar}'] pozitif olmalı, "
                    f"verildi: {self.imar_durumu[anahtar]}."
                )

        # 9. taks kontrolü (None değilse)
        if self.taks is not None:
            if self.taks <= 0 or self.taks > 1:
                raise ValueError(
                    f"taks 0 ile 1 arasında olmalı, verildi: {self.taks}."
                )

        # 10. kaks kontrolü (None değilse)
        if self.kaks is not None:
            if self.kaks <= 0:
                raise ValueError(
                    f"kaks pozitif olmalı, verildi: {self.kaks}."
                )

        # 11. emsal_harici_orani kontrolü
        if self.emsal_harici_orani < 0 or self.emsal_harici_orani > 1:
            raise ValueError(
                f"emsal_harici_orani 0 ile 1 arasında olmalı, "
                f"verildi: {self.emsal_harici_orani}."
            )

        self.log.info(
            f"MimariVeriler oluşturuldu: {n} köşe, "
            f"nizam={self.yapi_nizami}, kat={self.kat_sayisi}."
        )

    def cekme_baslangic_mesafeleri(self) -> list:
        """
        İmar durumu ve kenar rollerine göre başlangıç çekme mesafesi listesi üretir.

        Kural:
            - on_kenar_indeks          → imar_durumu["on"]
            - arka kenar (4 kenarlıda) → imar_durumu["arka"]
            - bitisik_kenarlar         → 0.0 (komşuya yapışık, çekme yok)
            - diğer tüm kenarlar       → imar_durumu["yan"]

        4 kenarlı arsada arka kenar otomatik:
            arka_indeks = (on_kenar_indeks + 2) % 4

        4'ten farklı köşe sayısında arka ayrımı yapılamaz;
        tüm ön olmayan kenarlar "yan" kabul edilir ve log.warning verilir.

        Not: Kademeli çekme (+0.5m/kat) bu metotta UYGULANMAZ.
        Kademeli artış için CekmeCizici.kademeli_cekme_hesapla() kullanılır.

        Dönüş:
            list[float]: len(arsa_koseleri) uzunluğunda çekme mesafesi listesi.
        """
        n = len(self.arsa_koseleri)
        mesafeler = [0.0] * n

        # Arka kenar sadece 4 kenarlı arsada net belirlenir
        if n == 4:
            arka_indeks = (self.on_kenar_indeks + 2) % 4
        else:
            arka_indeks = None
            self.log.warning(
                f"{n} kenarlı arsada arka kenar otomatik belirlenemedi. "
                "Tüm yan/arka kenarlar aynı mesafede (yan) hesaplanacak."
            )

        for i in range(n):
            if i in self.bitisik_kenarlar:
                # Komşuya yapışık kenar — çekme yok
                mesafeler[i] = 0.0
            elif i == self.on_kenar_indeks:
                # Ön bahçe kenarı
                mesafeler[i] = self.imar_durumu["on"]
            elif i == arka_indeks:
                # Arka bahçe kenarı (sadece 4 kenarlıda)
                mesafeler[i] = self.imar_durumu["arka"]
            else:
                # Yan bahçe kenarı
                mesafeler[i] = self.imar_durumu["yan"]

        self.log.info(f"Başlangıç çekme mesafeleri: {mesafeler}")
        return mesafeler

    def ozet(self) -> str:
        """
        Proje verilerini okunabilir formatta döndürür.

        log.info veya print ile kullanım için tasarlanmıştır.
        Nesneyi değiştirmez, sadece okur.

        Dönüş:
            str: Çok satırlı proje özeti.
        """
        yukseklik = (
            f"{self.bina_yuksekligi_m} m"
            if self.bina_yuksekligi_m is not None
            else "(belirtilmedi)"
        )
        satirlar = [
            "=== Proje Özeti ===",
            f"Arsa köşe sayısı : {len(self.arsa_koseleri)}",
            f"Yapı nizamı      : {self.yapi_nizami}",
            f"Kat sayısı       : {self.kat_sayisi}",
            f"Ön kenar         : {self.on_kenar_indeks}",
            f"Bina yüksekliği  : {yukseklik}",
            f"Park komşusu     : {self.park_komsusu_kenarlar}",
            f"Bitişik kenarlar : {self.bitisik_kenarlar}",
            (
                f"İmar durumu      : "
                f"ön={self.imar_durumu['on']}m, "
                f"yan={self.imar_durumu['yan']}m, "
                f"arka={self.imar_durumu['arka']}m"
            ),
        ]
        satirlar.append(
            f"TAKS             : {self.taks if self.taks is not None else '(belirtilmedi)'}"
        )
        satirlar.append(
            f"KAKS             : {self.kaks if self.kaks is not None else '(belirtilmedi)'}"
        )
        satirlar.append(
            f"Emsal harici %   : {self.emsal_harici_orani * 100:.0f}%"
        )
        return "\n".join(satirlar)
