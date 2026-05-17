"""
AutoLay projesine özel hata (exception) sınıfları.

Bu modül, AutoLay genelinde kullanılan tüm özel hata sınıflarını içerir.
Hatalar üç ana kategoriye ayrılmıştır:
  - Bağlantı hataları  : AutoCAD ile iletişim sorunları
  - Geometri hataları  : Koordinat ve şekil işlemleri sorunları
  - Katman hataları    : Katman yönetimi sorunları

Kullanım örneği:
    from autolay.core.hatalar import AutoCADKapaliHatasi
    raise AutoCADKapaliHatasi()
"""


# ---------------------------------------------------------------------------
# Temel sınıf
# ---------------------------------------------------------------------------

class AutoLayError(Exception):
    """
    Tüm AutoLay hatalarının temel sınıfı.

    Projeye özgü tüm hatalar bu sınıftan türetilir.
    Genel bir `except AutoLayError` bloğu ile projenin ürettiği
    her hata yakalanabilir.
    """

    def __init__(self, mesaj: str = "AutoLay hatası oluştu."):
        super().__init__(mesaj)
        self.mesaj = mesaj

    def __str__(self) -> str:
        return self.mesaj


# ---------------------------------------------------------------------------
# Bağlantı hataları
# ---------------------------------------------------------------------------

class BaglantiHatasi(AutoLayError):
    """
    AutoCAD bağlantı sorunları için genel temel sınıf.

    AutoCAD COM arayüzüne erişimde yaşanan her türlü sorun bu
    sınıftan türetilen özel hatalarla raporlanır.
    Örneğin: AutoCAD hiç açık değilse, açık ama çizim yoksa.
    """

    def __init__(self, mesaj: str = "AutoCAD bağlantı hatası oluştu."):
        super().__init__(mesaj)


class AutoCADKapaliHatasi(BaglantiHatasi):
    """
    AutoCAD uygulaması açık değilken bir işlem denendiğinde fırlatılır.

    win32com.client.GetActiveObject("AutoCAD.Application") çağrısı
    başarısız olduğunda, yani sistemde çalışan bir AutoCAD örneği
    bulunamadığında bu hata kullanılır.

    Çözüm: AutoCAD'i başlatıp tekrar deneyin.
    """

    def __init__(self, mesaj: str = "AutoCAD açık değil. Lütfen AutoCAD'i başlatın."):
        super().__init__(mesaj)


class AktifCizimYokHatasi(BaglantiHatasi):
    """
    AutoCAD açık ancak aktif bir .dwg belgesi yokken fırlatılır.

    AutoCAD uygulamasına bağlanılabiliyor fakat
    `acad.ActiveDocument` erişiminde belge bulunamıyorsa kullanılır.
    Örneğin AutoCAD yeni açılmış ve henüz hiçbir dosya yüklenmemişse.

    Çözüm: AutoCAD'de bir .dwg dosyası açın veya yeni bir çizim oluşturun.
    """

    def __init__(self, mesaj: str = "AutoCAD açık ama aktif bir .dwg belgesi yok."):
        super().__init__(mesaj)


# ---------------------------------------------------------------------------
# Geometri hataları
# ---------------------------------------------------------------------------

class GeometriHatasi(AutoLayError):
    """
    Geometri işlemleri sırasında oluşan hatalar için genel temel sınıf.

    Koordinat hesaplama, çizgi, yay veya poligon oluşturma gibi
    geometrik işlemlerde ortaya çıkan sorunlar bu sınıftan türetilir.
    """

    def __init__(self, mesaj: str = "Geometri hatası oluştu."):
        super().__init__(mesaj)


class GecersizKoordinatHatasi(GeometriHatasi):
    """
    Koordinat değeri beklenen formatta veya aralıkta değilse fırlatılır.

    Aşağıdaki durumlarda kullanılır:
      - Koordinat None veya sayısal olmayan bir değer içeriyorsa
      - (x, y) yerine tek elemanlı ya da dört elemanlı tuple geliyorsa
      - Sayısal değer sonsuz (inf) veya tanımsız (NaN) ise

    Örnek:
        raise GecersizKoordinatHatasi("Koordinat None olamaz.")
    """

    def __init__(self, mesaj: str = "Geçersiz koordinat değeri."):
        super().__init__(mesaj)


class YetersizKoseHatasi(GeometriHatasi):
    """
    Poligon veya polilyne oluşturmak için 3'ten az köşe verildiğinde fırlatılır.

    AutoCAD'de kapalı bir poligon en az 3 köşe noktası gerektir.
    İki nokta bir doğru parçası, tek nokta ise anlamsızdır.

    Örnek:
        if len(koseler) < 3:
            raise YetersizKoseHatasi(len(koseler))
    """

    def __init__(self, kose_sayisi: int | None = None,
                 mesaj: str | None = None):
        if mesaj is None:
            if kose_sayisi is not None:
                mesaj = (
                    f"Poligon için en az 3 köşe gereklidir, "
                    f"{kose_sayisi} köşe verildi."
                )
            else:
                mesaj = "Poligon için en az 3 köşe gereklidir."
        self.kose_sayisi = kose_sayisi
        super().__init__(mesaj)


# ---------------------------------------------------------------------------
# Katman hataları
# ---------------------------------------------------------------------------

class KatmanHatasi(AutoLayError):
    """
    Katman yönetimi işlemleri sırasında oluşan hatalar için genel temel sınıf.

    Katman oluşturma, silme, renk ayarlama veya var olan katmana
    erişim gibi işlemlerde ortaya çıkan sorunlar bu sınıftan türetilir.
    """

    def __init__(self, mesaj: str = "Katman hatası oluştu."):
        super().__init__(mesaj)


class KatmanBulunamadiHatasi(KatmanHatasi):
    """
    Var olmayan bir katmana erişim denendiğinde fırlatılır.

    `acad.ActiveDocument.Layers.Item(isim)` çağrısında belirtilen
    isimde bir katman bulunamazsa bu hata kullanılır.

    Örnek:
        raise KatmanBulunamadiHatasi("YAPI_DUVARI")
    """

    def __init__(self, katman_adi: str | None = None,
                 mesaj: str | None = None):
        if mesaj is None:
            if katman_adi is not None:
                mesaj = f"'{katman_adi}' adlı katman bulunamadı."
            else:
                mesaj = "Belirtilen katman bulunamadı."
        self.katman_adi = katman_adi
        super().__init__(mesaj)


class KatmanSilmeHatasi(KatmanHatasi):
    """
    Silinmesi yasak bir katmanı silmeye çalışıldığında fırlatılır.

    Aşağıdaki durumlarda kullanılır:
      - "0" katmanı gibi AutoCAD sistem katmanları silinemez.
      - Üzerinde nesne bulunan (dolu) katmanlar doğrudan silinemez.

    Örnek:
        raise KatmanSilmeHatasi("0", neden="sistem katmanı")
    """

    def __init__(self, katman_adi: str | None = None,
                 neden: str | None = None,
                 mesaj: str | None = None):
        if mesaj is None:
            if katman_adi and neden:
                mesaj = f"'{katman_adi}' katmanı silinemez: {neden}."
            elif katman_adi:
                mesaj = f"'{katman_adi}' katmanı silinemez."
            else:
                mesaj = "Katman silinemez."
        self.katman_adi = katman_adi
        self.neden = neden
        super().__init__(mesaj)


class GecersizRenkHatasi(KatmanHatasi):
    """
    RENK_ADLARI sözlüğünde tanımlı olmayan bir renk adı kullanıldığında fırlatılır.

    AutoLay, AutoCAD ACI (AutoCAD Color Index) renklerini
    okunabilir Türkçe isimlerle (ör. "kırmızı", "sarı") yönetir.
    Tanımlı listede bulunmayan bir renk adı girildiğinde bu hata kullanılır.

    Örnek:
        raise GecersizRenkHatasi("mor")
    """

    def __init__(self, renk_adi: str | None = None,
                 mesaj: str | None = None):
        if mesaj is None:
            if renk_adi is not None:
                mesaj = (
                    f"'{renk_adi}' geçerli bir renk adı değil. "
                    "Geçerli renkler için RENK_ADLARI sabitine bakın."
                )
            else:
                mesaj = "Geçersiz renk adı. RENK_ADLARI sabitine bakın."
        self.renk_adi = renk_adi
        super().__init__(mesaj)
