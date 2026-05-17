"""
autolay/drawing/layers.py

AutoCAD katmanlarını (layers) yöneten modül.

Mimari projelerde katmanlar, çizimin farklı bileşenlerini
(taşıyıcı sistem, duvarlar, kapılar, pencereler, ölçüler, notlar vb.)
birbirinden ayırt etmek için kullanılır. Her katmana farklı renk,
çizgi tipi ve çizgi kalınlığı atanarak çizim okunabilirliği artırılır.
Ruhsat projelerinde katman standartlarına uymak zorunludur.

Kullanım:
    connector = AutoCADConnector()
    connector.baglan()
    katman_yoneticisi = LayerManager(connector)
    katman_yoneticisi.katman_olustur("DUVARLAR", renk="kirmizi")
    katman_yoneticisi.aktif_katman_yap("DUVARLAR")
"""


from autolay.core.hatalar import (
    AutoCADKapaliHatasi,
    KatmanBulunamadiHatasi,
    KatmanSilmeHatasi,
    GecersizRenkHatasi,
)

# AutoCAD Color Index (ACI) değerlerinin Türkçe karşılıkları.
# ACI, AutoCAD'in 0-256 arası tam sayılarla renkleri kodladığı sistemdir.
RENK_ADLARI = {
    "kirmizi": 1,
    "sari":    2,
    "yesil":   3,
    "cyan":    4,
    "mavi":    5,
    "magenta": 6,
    "siyah":   7,
    "gri":     8,
    "beyaz":   7,
    "turuncu": 30,
}


class LayerManager:
    """
    AutoCAD katmanlarını oluşturan, düzenleyen ve silen sınıf.

    Bir AutoCADConnector nesnesine bağımlıdır; bağlantı bu nesne
    üzerinden sağlanır. Doğrudan AutoCAD'e bağlanmaz.
    """

    def __init__(self, connector):
        """
        LayerManager nesnesini başlatır.

        Parametreler:
            connector (AutoCADConnector): Kurulu AutoCAD bağlantısı.
                                         baglan() çağrılmış olmalıdır.
        """
        self.connector = connector  # Dışarıdan gelen bağlantı nesnesi

    def _katmanlar_koleksiyonu(self):
        """
        Aktif çizimin Layers koleksiyonunu döndürür.

        Bu iç metot, diğer metodların katman koleksiyonuna erişmek için
        tekrar tekrar aynı kodu yazmasını önler.

        Parametreler:
            Yok

        Dönüş değeri:
            win32com object — AutoCAD Layers koleksiyonu.

        Hatalar:
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        if not self.connector.bagli_mi():
            raise AutoCADKapaliHatasi(
                "AutoCAD bağlantısı yok. Önce connector.baglan() çağırın."
            )

        # Aktif çizim üzerinden katmanlar koleksiyonunu al
        return self.connector.aktif_cizim().Layers

    def katman_var_mi(self, isim):
        """
        Verilen isimde bir katmanın mevcut olup olmadığını kontrol eder.

        Katman koleksiyonundan isme göre erişimi dener; başarılı olursa
        katman var demektir. AutoCAD katman adlarında büyük/küçük harf
        farkı gözetilmez.

        Parametreler:
            isim (str): Kontrol edilecek katmanın adı.

        Dönüş değeri:
            bool — True: katman mevcut, False: katman yok.

        Hatalar:
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        try:
            # Item() metodu katmanı bulamazsa exception fırlatır
            self._katmanlar_koleksiyonu().Item(isim)
            return True
        except Exception:
            return False

    def katman_olustur(self, isim, renk=None, cizgi_tipi=None):
        """
        Belirtilen isimde yeni bir katman oluşturur.

        Katman zaten mevcutsa yeni oluşturmaz, mevcut katmanı döndürür
        (idempotent davranış — defalarca çağrılabilir, hata vermez).

        Renk parametresi Türkçe string ("kirmizi", "mavi" vb.) veya
        doğrudan ACI tam sayısı (1-256) olarak verilebilir.

        Parametreler:
            isim       (str):       Oluşturulacak katmanın adı.
            renk       (str|int):   Katman rengi. Türkçe ad veya ACI değeri.
                                    Verilmezse AutoCAD varsayılanı kullanılır.
            cizgi_tipi (str):       Katman çizgi tipi adı (örn: "DASHED").
                                    Verilmezse "Continuous" kalır.

        Dönüş değeri:
            win32com object — Oluşturulan veya mevcut katman nesnesi.

        Hatalar:
            ValueError      — Türkçe renk adı RENK_ADLARI sözlüğünde yoksa.
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        # Katman zaten varsa mevcut olanı geri döndür
        if self.katman_var_mi(isim):
            return self._katmanlar_koleksiyonu().Item(isim)

        # Yeni katmanı koleksiyona ekle
        yeni_katman = self._katmanlar_koleksiyonu().Add(isim)

        # Renk parametresi verildiyse işle
        if renk is not None:
            if isinstance(renk, str):
                # String ise Türkçe sözlükten ACI değerini al
                if renk not in RENK_ADLARI:
                    raise GecersizRenkHatasi(renk)
                aci_degeri = RENK_ADLARI[renk]
            else:
                # int ise doğrudan kullan
                aci_degeri = int(renk)

            yeni_katman.Color = aci_degeri  # ACI rengini katmana ata

        # Çizgi tipi parametresi verildiyse ata
        if cizgi_tipi is not None:
            # Not: Çizgi tipinin AutoCAD'e önceden yüklenmiş olması gerekir
            yeni_katman.Linetype = cizgi_tipi

        return yeni_katman

    def aktif_katman_yap(self, isim):
        """
        Belirtilen katmanı aktif çizim katmanı olarak ayarlar.

        Aktif katman olarak ayarlanan katmana bundan sonra çizilen
        tüm nesneler otomatik olarak atanır.

        Parametreler:
            isim (str): Aktif yapılacak katmanın adı.

        Dönüş değeri:
            None

        Hatalar:
            ValueError      — Belirtilen katman mevcut değilse.
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        if not self.katman_var_mi(isim):
            raise KatmanBulunamadiHatasi(isim)

        # Katman nesnesini al ve aktif katman olarak ayarla
        katman = self._katmanlar_koleksiyonu().Item(isim)
        self.connector.aktif_cizim().ActiveLayer = katman

    def tum_katmanlar(self):
        """
        Aktif çizimdeki tüm katmanların adlarını liste olarak döndürür.

        Parametreler:
            Yok

        Dönüş değeri:
            list[str] — Katman adlarının listesi.

        Hatalar:
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        katman_listesi = []

        # Koleksiyondaki her katmanın adını listeye ekle
        for katman in self._katmanlar_koleksiyonu():
            katman_listesi.append(katman.Name)

        return katman_listesi

    def katman_sil(self, isim):
        """
        Belirtilen katmanı aktif çizimden siler.

        "0" ve "Defpoints" AutoCAD'in korumalı sistem katmanlarıdır;
        bu katmanlar silinemez.

        Parametreler:
            isim (str): Silinecek katmanın adı.

        Dönüş değeri:
            None

        Hatalar:
            ValueError      — Katman mevcut değilse.
            RuntimeError   — Korumalı sistem katmanı silinmeye çalışılırsa.
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
        """
        if not self.katman_var_mi(isim):
            raise KatmanBulunamadiHatasi(isim)

        # AutoCAD'in korumalı sistem katmanlarını kontrol et
        sistem_katmanlari = ("0", "Defpoints")
        if isim in sistem_katmanlari:
            raise KatmanSilmeHatasi(isim, neden="sistem katmanı")

        # Katmanı al ve sil
        katman = self._katmanlar_koleksiyonu().Item(isim)
        katman.Delete()
