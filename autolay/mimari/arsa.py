"""
arsa.py — ArsaCizici modülü

AutoCAD üzerinde arsa sınırlarını çizmek, alanını hesaplamak ve
merkez noktasını bulmak için kullanılır.

Bağımlılıklar:
    - AutoCADConnector: AutoCAD COM bağlantısını yönetir
    - GeometryDrawer: Geometrik şekilleri çizer
    - LayerManager: Katman oluşturma ve yönetimi
    - GeometryUtils: Alan, merkez ve mesafe hesaplamaları
"""

from autolay.core.baglanti import AutoCADConnector
from autolay.drawing.shapes import GeometryDrawer
from autolay.drawing.layers import LayerManager
from autolay.utils.geometri import GeometryUtils
from autolay.utils.logger import logger_olustur
from autolay.core.hatalar import YetersizKoseHatasi
from autolay.config.sabitler import MIN_POLIGON_KOSE_SAYISI


class ArsaCizici:
    """
    Arsa sınırlarını AutoCAD'de çizen ve arsa bilgilerini hesaplayan sınıf.

    Kullanım sırası:
        1. ArsaCizici(connector) ile nesne oluştur
        2. koseleri_ayarla(koseler) ile köşe listesini ver
        3. ciz() ile AutoCAD'e çiz
    """

    def __init__(self, connector: AutoCADConnector):
        """
        ArsaCizici nesnesini başlatır.

        Parametreler:
            connector (AutoCADConnector): Aktif AutoCAD COM bağlantısı.
        """
        self.connector = connector
        self.layer_mgr = LayerManager(connector)
        self.drawer = GeometryDrawer(connector)
        self.geo = GeometryUtils()
        self.log = logger_olustur(__name__)
        self.koseler = None
        self.KATMAN_ADI = "AUTOLAY_ARSA"
        self.KATMAN_RENGI = "kirmizi"

    def koseleri_ayarla(self, koseler: list):
        """
        Arsa köşe koordinatlarını ayarlar.

        Parametreler:
            koseler (list): (x, y) veya (x, y, z) tuple'larından oluşan liste.
                            En az MIN_POLIGON_KOSE_SAYISI kadar köşe olmalıdır.

        Hata:
            YetersizKoseHatasi: Köşe sayısı minimumun altındaysa fırlatılır.
        """
        if len(koseler) < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(kose_sayisi=len(koseler))
        self.koseler = koseler
        self.log.info(f"{len(koseler)} köşe noktası alındı.")

    def ciz(self):
        """
        Arsa poligonunu AutoCAD'de çizer.

        AUTOLAY_ARSA katmanını oluşturur (yoksa), aktif yapar ve
        belirlenen köşe noktalarından poligon çizer.

        Hata:
            ValueError: koseleri_ayarla daha önce çağrılmamışsa fırlatılır.
        """
        if self.koseler is None:
            raise ValueError("Önce koseleri_ayarla çağır.")

        self.layer_mgr.katman_olustur(self.KATMAN_ADI, renk=self.KATMAN_RENGI)
        self.layer_mgr.aktif_katman_yap(self.KATMAN_ADI)
        self.drawer.poligon_ciz(self.koseler)

        alan = self.alan()
        self.log.info(
            f"Arsa çizildi. Köşe sayısı: {len(self.koseler)}, Alan: {alan:.2f} m²"
        )

    def alan(self) -> float:
        """
        Arsa alanını Shoelace (Gauss) formülüyle hesaplar.

        Dönüş:
            float: Arsa alanı (m² cinsinden, koordinatlar metredeyse).

        Hata:
            ValueError: koseleri_ayarla daha önce çağrılmamışsa fırlatılır.
        """
        if self.koseler is None:
            raise ValueError("Önce koseleri_ayarla çağır.")
        return self.geo.poligon_alani(self.koseler)

    def merkez_noktasi(self) -> tuple:
        """
        Arsa poligonunun geometrik merkezini (centroid) hesaplar.

        Dönüş:
            tuple: (x, y) koordinat çifti olarak merkez noktası.

        Hata:
            ValueError: koseleri_ayarla daha önce çağrılmamışsa fırlatılır.
        """
        if self.koseler is None:
            raise ValueError("Önce koseleri_ayarla çağır.")
        return self.geo.poligon_merkezi(self.koseler)
