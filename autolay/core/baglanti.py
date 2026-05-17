"""
autolay/core/baglanti.py

AutoCAD uygulamasına COM (Component Object Model) arayüzü üzerinden
bağlantı kurmayı ve bu bağlantıyı yönetmeyi sağlayan modül.

Kullanım:
    connector = AutoCADConnector()
    connector.baglan()
    model = connector.model_uzayi()
"""

import win32com.client  # AutoCAD COM bağlantısı için
import pythoncom        # COM veri tipleri için (koordinat formatında kullanılacak)

from autolay.core.hatalar import AutoCADKapaliHatasi, AktifCizimYokHatasi
from autolay.utils.logger import logger_olustur

log = logger_olustur(__name__)


class AutoCADConnector:
    """
    AutoCAD uygulamasına bağlantıyı temsil eden sınıf.

    Bu sınıf, pywin32 kütüphanesi aracılığıyla çalışan AutoCAD 2026
    uygulamasına bağlanır ve aktif çizim/model uzayına erişim sağlar.
    """

    def __init__(self):
        """
        AutoCADConnector nesnesini başlatır.

        Bağlantı kurulmaz; yalnızca dahili değişkenler hazırlanır.
        Bağlantı kurmak için baglan() metodunu çağır.
        """
        self.acad = None    # AutoCAD uygulama nesnesi (bağlantı sonrası dolar)
        self._bagli = False  # Bağlantı durumu: başlangıçta bağlı değil

    def baglan(self):
        """
        AutoCAD uygulamasına COM arayüzü üzerinden bağlantı kurar.
        Bağlantı başarılıysa aktif çizim belgesi olup olmadığını da doğrular.

        AutoCAD'in önceden açık ve bir .dwg dosyası yüklü olması gerekir.
        Bağlantı başarılı olursa self.acad ve self._bagli güncellenir.

        Parametreler:
            Yok

        Dönüş değeri:
            bool — True: bağlantı ve aktif çizim doğrulandı
                   False: AutoCAD'e ulaşılamadı (kapalı veya lisans sorunu)

        Hatalar:
            AktifCizimYokHatasi — AutoCAD açık fakat aktif .dwg belgesi yoksa
        """
        try:
            # AutoCAD'in COM kimliğiyle bağlantı kur
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
        except Exception as hata:
            # Dispatch başarısızsa — AutoCAD kapalı veya erişilemiyor
            log.error(f"AutoCAD'e bağlanılamadı. AutoCAD açık mı? Hata detayı: {hata}")
            self._bagli = False
            return False

        # Dispatch başarılı; aktif çizim belgesini doğrula
        try:
            cizim = self.acad.ActiveDocument
            dosya_adi = cizim.Name if cizim else "bilinmiyor"
            self._bagli = True
            log.info(f"AutoCAD bağlantısı kuruldu, aktif çizim: {dosya_adi}")
            return True
        except Exception as hata:
            # AutoCAD açık ama hiç .dwg yüklü değil
            log.error(
                f"AutoCAD açık fakat aktif çizim belgesi alınamadı. "
                f"Bir .dwg dosyası açık mı? Hata: {hata}"
            )
            raise AktifCizimYokHatasi(
                "AutoCAD açık fakat çizim belgesi yok.\n"
                "Çözüm: AutoCAD'de Ctrl+N ile yeni bir çizim açın, "
                "sonra tekrar deneyin."
            )

    def bagli_mi(self):
        """
        Bağlantının aktif olup olmadığını döndürür.

        Parametreler:
            Yok

        Dönüş değeri:
            bool — True: bağlantı kurulu, False: bağlantı yok
        """
        return self._bagli

    def aktif_cizim(self):
        """
        AutoCAD'deki aktif (açık) çizim belgesini döndürür.

        AutoCAD'in bir .dwg dosyası açmış olması gerekir.
        Yalnızca başlangıç ekranı açıksa (dosya yok) hata verir.

        Parametreler:
            Yok

        Dönüş değeri:
            win32com object — AutoCAD ActiveDocument nesnesi

        Hatalar:
            ConnectionError — baglan() çağrılmadan önce kullanılırsa
            RuntimeError   — AutoCAD açık ama aktif çizim belgesi yoksa
        """
        if not self._bagli:
            raise AutoCADKapaliHatasi(
                "AutoCAD'e bağlı değilsiniz. Önce baglan() metodunu çağırın."
            )

        try:
            cizim = self.acad.ActiveDocument  # Açık olan çizim belgesini al
        except Exception as hata:
            raise AktifCizimYokHatasi(
                f"Aktif çizim belgesi alınamadı. AutoCAD'de bir .dwg dosyası açık mı?\n"
                f"Hata detayı: {hata}"
            )

        if cizim is None:
            raise AktifCizimYokHatasi(
                "AutoCAD açık fakat aktif çizim belgesi bulunamadı. "
                "Lütfen bir .dwg dosyası açın."
            )

        return cizim

    def model_uzayi(self):
        """
        Aktif çizimin Model Uzayı nesnesini döndürür.

        Tüm çizim elemanları (çizgi, daire, metin vb.) bu nesne
        üzerinden oluşturulur.

        Parametreler:
            Yok

        Dönüş değeri:
            win32com object — AutoCAD ModelSpace nesnesi

        Hatalar:
            ConnectionError — bağlantı kurulmamışsa (aktif_cizim() üzerinden)
            RuntimeError   — aktif çizim yoksa (aktif_cizim() üzerinden)
        """
        return self.aktif_cizim().ModelSpace  # Model uzayını çizim belgesinden al

    def surum(self):
        """
        Bağlı AutoCAD uygulamasının sürüm numarasını döndürür.

        Örnek dönüş değeri: "26.0s" (AutoCAD 2026 için)

        Parametreler:
            Yok

        Dönüş değeri:
            str — AutoCAD sürüm numarası

        Hatalar:
            ConnectionError — bağlantı kurulmamışsa
        """
        if not self._bagli:
            raise AutoCADKapaliHatasi(
                "AutoCAD'e bağlı değilsiniz. Önce baglan() metodunu çağırın."
            )

        return str(self.acad.Version)  # Sürüm bilgisini string olarak döndür

    def dosya_adi(self):
        """
        Aktif çizim belgesinin dosya adını döndürür.

        Örnek dönüş değeri: "Drawing1.dwg"

        Parametreler:
            Yok

        Dönüş değeri:
            str — Açık olan .dwg dosyasının adı

        Hatalar:
            ConnectionError — bağlantı kurulmamışsa (aktif_cizim() üzerinden)
            RuntimeError   — aktif çizim yoksa (aktif_cizim() üzerinden)
        """
        return str(self.aktif_cizim().Name)  # Belge adını string olarak döndür
