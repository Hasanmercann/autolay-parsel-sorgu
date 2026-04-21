"""
tkgm_okuyucu.py — TKGMOkuyucu modülü

TKGM CBS API'sini kullanarak il/ilçe/mahalle/ada/parsel bilgisinden
arsa koordinatlarını çeker.

Çalışma mantığı:
    1. tkgm_idler.json'dan mahalle ID'sini bulur.
    2. cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api/parsel/{mahalle_id}/{ada}/{parsel}
       adresinden GeoJSON koordinatları çeker.
    3. WGS84 koordinatlarını AutoCAD için rölatif metreye dönüştürür.

Bağımlılıklar:
    pip install requests

Yeni il eklemek için:
    python tests/tkgm_id_olustur_hizli.py <IL_ADI>

Kullanım:
    okuyucu = TKGMOkuyucu()
    sonuc = okuyucu.parsel_sorgula(
        il="KONYA", ilce="ILGIN", mahalle="TEKELER", ada="175", parsel="1"
    )
    print(sonuc.koseler)   # [(x1,y1), (x2,y2), ...]
    print(sonuc.alan_m2)   # float
"""

import os
import json
import math

from autolay.utils.logger import logger_olustur

# Önbellek dosyası: autolay/okuyucu/tkgm_idler.json
_ONBELLEK_YOLU = os.path.join(os.path.dirname(__file__), "tkgm_idler.json")
_CBS_API = "https://cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api/parsel"


class ParselSonucu:
    """
    TKGM'den çekilen parsel verisini taşıyan veri sınıfı.

    Alanlar:
        koseler (list)          : [(x1,y1), (x2,y2), ...] rölatif metre koordinatları
        alan_m2 (float|None)    : Parsel alanı m²
        il, ilce, mahalle       : Sorgu bilgileri
        ada, parsel             : Ada/parsel numaraları
        mahalle_id (str)        : TKGM iç mahalle kodu
    """

    def __init__(self, koseler: list, il: str, ilce: str, mahalle: str,
                 ada: str, parsel: str, mahalle_id: str,
                 alan_m2: float = None):
        self.koseler = koseler
        self.il = il
        self.ilce = ilce
        self.mahalle = mahalle
        self.ada = ada
        self.parsel = parsel
        self.mahalle_id = mahalle_id
        self.alan_m2 = alan_m2

    def __repr__(self):
        return (
            f"ParselSonucu(il={self.il!r}, ilce={self.ilce!r}, "
            f"mahalle={self.mahalle!r}, ada={self.ada!r}, parsel={self.parsel!r}, "
            f"kose_sayisi={len(self.koseler)}, alan_m2={self.alan_m2:.1f})"
        )


class TKGMOkuyucu:
    """
    TKGM CBS API'sini kullanarak il/ilçe/mahalle/ada/parsel bilgisinden
    arsa koordinatlarını çeker.

    Yeni il eklemek için:
        python tests/tkgm_id_olustur_hizli.py <IL_ADI>

    Kullanım:
        okuyucu = TKGMOkuyucu()
        sonuc = okuyucu.parsel_sorgula("KONYA", "ILGIN", "TEKELER", "175", "1")
        koseler = sonuc.koseler  # [(x1,y1), ...] rölatif metre
    """

    _CBS_API = _CBS_API

    def __init__(self, onbellek_yolu: str = None):
        """
        TKGMOkuyucu nesnesini başlatır.

        Parametreler:
            onbellek_yolu (str|None): tkgm_idler.json dosya yolu.
                                      None ise varsayılan konum kullanılır.
        """
        self._onbellek_yolu = onbellek_yolu or _ONBELLEK_YOLU
        self._idler = None
        self.log = logger_olustur(__name__)

    def _idleri_yukle(self) -> dict:
        """tkgm_idler.json dosyasını yükler (lazy, bir kere yükler)."""
        if self._idler is not None:
            return self._idler

        if not os.path.exists(self._onbellek_yolu):
            raise FileNotFoundError(
                f"ID önbellek dosyası bulunamadı: {self._onbellek_yolu}\n"
                f"Yeni il eklemek için:\n"
                f"  python tests/tkgm_id_olustur_hizli.py <IL_ADI>"
            )

        with open(self._onbellek_yolu, encoding="utf-8") as f:
            self._idler = json.load(f)
        self.log.debug(f"ID önbelleği yüklendi: {len(self._idler)} il")
        return self._idler

    def mahalle_id_bul(self, il: str, ilce: str, mahalle: str) -> str:
        """
        il/ilçe/mahalle adından TKGM iç mahalle ID'sini döndürür.

        Hata:
            KeyError: İl, ilçe veya mahalle önbellekte yoksa
        """
        idler = self._idleri_yukle()

        il_k = il.strip().upper()
        ilce_k = ilce.strip().upper()
        mahalle_k = mahalle.strip().upper()

        if il_k not in idler:
            mevcut = ", ".join(sorted(idler.keys()))
            raise KeyError(
                f"'{il_k}' ili önbellekte yok.\n"
                f"Mevcut iller: {mevcut}\n"
                f"Eklemek için: python tests/tkgm_id_olustur_hizli.py {il_k}"
            )

        il_veri = idler[il_k]
        ilceler = il_veri.get("ilceler", {})

        if ilce_k not in ilceler:
            mevcut = ", ".join(sorted(ilceler.keys()))
            raise KeyError(f"'{ilce_k}' ilçesi '{il_k}' ilinde bulunamadı. Mevcut: {mevcut}")

        mahalleler = ilceler[ilce_k].get("mahalleler", {})

        if mahalle_k not in mahalleler:
            mevcut = ", ".join(sorted(mahalleler.keys()))
            raise KeyError(
                f"'{mahalle_k}' mahallesi '{il_k}/{ilce_k}' içinde bulunamadı.\n"
                f"Mevcut mahalleler: {mevcut}"
            )

        return str(mahalleler[mahalle_k])

    def parsel_sorgula(self, il: str, ilce: str, mahalle: str,
                       ada: str, parsel: str) -> "ParselSonucu":
        """
        TKGM CBS API üzerinden parsel koordinatlarını çeker.

        Parametreler:
            il (str)       : İl adı — örnek: "KONYA"
            ilce (str)     : İlçe adı — örnek: "ILGIN"
            mahalle (str)  : Mahalle adı — örnek: "TEKELER"
            ada (str)      : Ada numarası — örnek: "175"
            parsel (str)   : Parsel numarası — örnek: "1"

        Dönüş:
            ParselSonucu — rölatif metre koordinatları ve parsel bilgileri

        Hata:
            KeyError     : İl/ilçe/mahalle önbellekte yoksa
            RuntimeError : Parsel bulunamazsa veya API erişim hatası
            ImportError  : requests kurulu değilse
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests kurulu değil. Kurmak için: pip install requests")

        self.log.info(
            f"TKGM sorgusu: {il}/{ilce}/{mahalle} ada={ada} parsel={parsel}"
        )

        # 1. Önbellekten mahalle ID'sini al
        mahalle_id = self.mahalle_id_bul(il, ilce, mahalle)
        self.log.debug(f"Mahalle ID: {mahalle_id}")

        # 2. CBS API'den GeoJSON çek
        url = f"{self._CBS_API}/{mahalle_id}/{ada}/{parsel}"
        self.log.debug(f"CBS API URL: {url}")

        yanit = requests.get(url, timeout=15)
        if yanit.status_code == 404:
            raise RuntimeError(
                f"Parsel bulunamadı: {il}/{ilce}/{mahalle} ada={ada} parsel={parsel}\n"
                f"(HTTP 404 — mahalle_id={mahalle_id})"
            )
        yanit.raise_for_status()

        data = yanit.json()

        # 3. GeoJSON'dan koordinatları çıkar
        koordinatlar = self._geojson_isle(data)
        if not koordinatlar:
            raise RuntimeError(
                f"GeoJSON'dan koordinat çıkarılamadı. "
                f"API yanıt formatı değişmiş olabilir.\nURL: {url}"
            )

        # 4. WGS84 → rölatif metre
        # GeoJSON kapalı polygon: ilk == son nokta — AutoCAD Closed=True ile
        # zaten kapatacağı için son tekrar eden noktayı at
        if len(koordinatlar) > 1 and koordinatlar[0] == koordinatlar[-1]:
            koordinatlar = koordinatlar[:-1]

        koseler_metre = self._wgs84_metre_donustur(koordinatlar)
        alan = self._alan_hesapla(koseler_metre)

        self.log.info(
            f"Parsel çekildi: {len(koseler_metre)} köşe, alan≈{alan:.1f} m²"
        )

        return ParselSonucu(
            koseler=koseler_metre,
            il=il.upper(), ilce=ilce.upper(), mahalle=mahalle.upper(),
            ada=str(ada), parsel=str(parsel),
            mahalle_id=mahalle_id,
            alan_m2=alan,
        )

    # -------------------------------------------------------------------
    # Yardımcı metodlar
    # -------------------------------------------------------------------

    def _geojson_isle(self, data: dict) -> list:
        """
        GeoJSON Feature/FeatureCollection yapısından koordinat listesi çıkarır.

        CBS API formatı:
            {"type": "Feature", "geometry": {"type": "Polygon",
             "coordinates": [[[lon, lat], ...]]}, ...}

        Dönüş:
            list — [(lon1, lat1), (lon2, lat2), ...] veya []
        """
        if not isinstance(data, dict):
            return []

        # Doğrudan geometry
        geom = data.get("geometry")
        if isinstance(geom, dict):
            tip = geom.get("type", "")
            coords = geom.get("coordinates")
            if "Polygon" in tip and coords:
                return [(c[0], c[1]) for c in coords[0]]
            if "MultiPolygon" in tip and coords:
                # En büyük halkayı al
                en_buyuk = max(coords, key=lambda p: len(p[0]))
                return [(c[0], c[1]) for c in en_buyuk[0]]

        # FeatureCollection
        features = data.get("features")
        if isinstance(features, list):
            for feat in features:
                sonuc = self._geojson_isle(feat)
                if sonuc:
                    return sonuc

        return []

    def _wgs84_metre_donustur(self, koordinatlar: list) -> list:
        """
        WGS84 (boylam, enlem derece) koordinatlarını rölatif metre cinsinden
        yerel koordinatlara dönüştürür.

        Yöntem: Merkez noktaya göre farkları alır, derece → metre için
        Haversine yaklaşımı kullanır.

        Parametreler:
            koordinatlar (list): [(lon1,lat1), (lon2,lat2), ...]

        Dönüş:
            list: [(x1,y1), (x2,y2), ...] — metre cinsinden rölatif koordinatlar
        """
        if not koordinatlar:
            return []

        # Merkez noktayı hesapla
        orta_lon = sum(c[0] for c in koordinatlar) / len(koordinatlar)
        orta_lat = sum(c[1] for c in koordinatlar) / len(koordinatlar)

        # Dereceyi metreye çevirme katsayıları (Türkiye için)
        # 1 enlem derecesi ≈ 111320 metre (sabittir)
        # 1 boylam derecesi ≈ 111320 * cos(φ) metre (enlem bağımlı)
        lat_rad = math.radians(orta_lat)
        metre_per_lon = 111320.0 * math.cos(lat_rad)
        metre_per_lat = 111320.0

        sonuc = []
        for lon, lat in koordinatlar:
            x = (lon - orta_lon) * metre_per_lon
            y = (lat - orta_lat) * metre_per_lat
            sonuc.append((round(x, 3), round(y, 3)))

        return sonuc

    def _alan_hesapla(self, koseler: list) -> float:
        """Shoelace formülü ile poligon alanı hesaplar (m²)."""
        n = len(koseler)
        if n < 3:
            return 0.0
        toplam = 0.0
        for i in range(n):
            j = (i + 1) % n
            toplam += koseler[i][0] * koseler[j][1]
            toplam -= koseler[j][0] * koseler[i][1]
        return abs(toplam) / 2.0
