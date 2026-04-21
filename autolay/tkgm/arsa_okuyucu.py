"""
arsa_okuyucu.py — ArsaOkuyucu modülü

AutoCAD'de çizili polyline'ları kullanıcıdan seçtirip
köşe koordinatlarını Python listesi olarak döndürür.

Kullanıcı AutoLay kullanırken:
1. Önce AutoCAD'de arsayı polyline olarak çizer (plankoteden)
2. AutoLay polyline_sec() çağrıldığında "Arsayı seçin" diye bekler
3. Kullanıcı fareyle polyline'a tıklar
4. AutoLay koordinatları okur, tuple listesi olarak döner

Bağımlılıklar:
    - AutoCADConnector : AutoCAD COM bağlantısı
    - logger_olustur   : Loglama
"""

from autolay.core.baglanti import AutoCADConnector
from autolay.utils.logger import logger_olustur


class ArsaOkuyucu:
    """
    AutoCAD'de çizili polyline'lardan arsa koordinatları okur.

    Kullanım:
        okuyucu = ArsaOkuyucu(connector)
        koseler = okuyucu.polyline_sec("Arsayı seçin:")
        # Mimar AutoCAD'de tıklar
        # Dönüş: [(x1,y1), (x2,y2), ...]
    """

    def __init__(self, connector: AutoCADConnector):
        """
        ArsaOkuyucu nesnesini başlatır.

        Parametreler:
            connector (AutoCADConnector): Aktif AutoCAD bağlantısı.
        """
        self.connector = connector
        self.log = logger_olustur(__name__)

    def polyline_sec(self, mesaj: str = "Bir polyline seçin:") -> list:
        """
        Kullanıcıdan AutoCAD'de bir polyline seçmesini ister.

        SelectionSet mekanizması kullanılır: AutoCAD'de geçici bir seçim kümesi
        oluşturulur, kullanıcıdan nesne seçmesi istenir ve seçilen polyline
        okunur.

        Parametreler:
            mesaj (str): AutoCAD komut satırında gösterilecek mesaj.

        Dönüş:
            list[tuple]: [(x1,y1), (x2,y2), ...] köşe listesi.

        Hata:
            RuntimeError: Hiçbir şey seçilmezse veya polyline değilse.
        """
        self.log.info(f"Polyline seçimi bekleniyor: {mesaj}")

        aktif_cizim = self.connector.aktif_cizim()

        # Geçici SelectionSet oluştur (benzersiz isim)
        import time
        ss_adi = f"AUTOLAY_SEC_{int(time.time() * 1000)}"

        try:
            # Eski aynı isimli SelectionSet varsa sil
            try:
                eski = aktif_cizim.SelectionSets.Item(ss_adi)
                eski.Delete()
            except Exception:
                pass

            # Yeni SelectionSet oluştur
            ss = aktif_cizim.SelectionSets.Add(ss_adi)

            # Kullanıcıya mesaj göster
            aktif_cizim.Utility.Prompt(f"\n{mesaj}\n")

            # Kullanıcıdan tek nesne seçmesini iste
            # SelectOnScreen: kullanıcı fareyle tıklar
            ss.SelectOnScreen()

            if ss.Count == 0:
                raise RuntimeError("Hiçbir nesne seçilmedi.")

            # Seçilen nesneler arasında polyline olanı bul
            polyline_tipleri = ("AcDbPolyline", "AcDb2dPolyline", "AcDb3dPolyline")
            entity = None
            polyline_sayisi = 0

            for i in range(ss.Count):
                nesne = ss.Item(i)
                if nesne.ObjectName in polyline_tipleri:
                    polyline_sayisi += 1
                    if entity is None:
                        entity = nesne

            if entity is None:
                # Hiç polyline yok, tüm seçilenlerin tipini logla
                tipler = [ss.Item(i).ObjectName for i in range(ss.Count)]
                raise RuntimeError(
                    f"Seçilen {ss.Count} nesne içinde polyline yok. "
                    f"Seçilen tipler: {tipler}. "
                    f"Lütfen polyline (PLINE komutu) seçin, düz çizgi değil."
                )

            if polyline_sayisi > 1:
                self.log.warning(
                    f"{polyline_sayisi} polyline seçildi, ilki kullanılacak."
                )

        except Exception as e:
            self.log.error(f"Polyline seçimi başarısız: {e}")
            raise RuntimeError(f"Seçim hatası: {e}")
        finally:
            # SelectionSet'i temizle
            try:
                ss.Delete()
            except Exception:
                pass

        # Nesne tipini kontrol et
        nesne_tipi = entity.ObjectName
        self.log.info(f"Seçilen nesne tipi: {nesne_tipi}")

        if nesne_tipi not in ("AcDbPolyline", "AcDb2dPolyline", "AcDb3dPolyline"):
            raise RuntimeError(
                f"Seçilen nesne polyline değil: {nesne_tipi}. "
                f"Lütfen bir polyline seçin."
            )

        # Koordinatları al
        flat_coords = entity.Coordinates
        koseler = []

        if nesne_tipi == "AcDb3dPolyline":
            for i in range(0, len(flat_coords), 3):
                x, y = flat_coords[i], flat_coords[i + 1]
                koseler.append((float(x), float(y)))
        else:
            for i in range(0, len(flat_coords), 2):
                x, y = flat_coords[i], flat_coords[i + 1]
                koseler.append((float(x), float(y)))

        # Kapalı polyline kontrolü
        try:
            kapali = entity.Closed
        except Exception:
            kapali = False

        if len(koseler) >= 2:
            ilk = koseler[0]
            son = koseler[-1]
            if not kapali and ilk != son:
                self.log.warning(
                    f"Seçilen polyline kapalı değil. İlk köşe {ilk}, son köşe {son}. "
                    f"Polygon olarak kabul edilecek."
                )

        if len(koseler) >= 2 and koseler[0] == koseler[-1]:
            koseler = koseler[:-1]

        self.log.info(
            f"Polyline okundu: {len(koseler)} köşe. "
            f"İlk köşe: {koseler[0]}, son köşe: {koseler[-1]}."
        )

        return koseler
