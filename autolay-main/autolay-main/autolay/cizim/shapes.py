"""
autolay/drawing/shapes.py

AutoCAD'e temel geometrik şekiller çizen modül.

Bu modül, kurulu bir AutoCADConnector bağlantısını kullanarak
Model Uzayına çizgi, kare, dikdörtgen, daire ve poligon ekler.
Tüm koordinatlar AutoCAD'in gerektirdiği VARIANT formatına dönüştürülür.

Kullanım:
    connector = AutoCADConnector()
    connector.baglan()
    cizici = GeometryDrawer(connector)
    cizici.kare_ciz((0, 0), 100)
"""

import win32com.client  # VARIANT nesnesi oluşturmak için
import pythoncom        # VT_ARRAY ve VT_R8 sabitleri için

from autolay.core.hatalar import AutoCADKapaliHatasi, YetersizKoseHatasi
from autolay.config.sabitler import MIN_POLIGON_KOSE_SAYISI, VARSAYILAN_Z


class GeometryDrawer:
    """
    AutoCAD Model Uzayına geometrik şekiller çizen sınıf.

    Bir AutoCADConnector nesnesine bağımlıdır; bağlantı bu nesne
    üzerinden sağlanır. Doğrudan AutoCAD'e bağlanmaz.
    """

    def __init__(self, connector):
        """
        GeometryDrawer nesnesini başlatır.

        Parametreler:
            connector (AutoCADConnector): Kurulu AutoCAD bağlantısı.
                                         baglan() çağrılmış olmalıdır.
        """
        self.connector = connector  # Dışarıdan gelen bağlantı nesnesi

    def _nokta_olustur(self, x, y, z=VARSAYILAN_Z):
        """
        Verilen koordinatlardan AutoCAD'e uygun VARIANT formatında nokta üretir.

        AutoCAD COM arayüzü koordinatları düz Python tuple olarak kabul etmez;
        mutlaka VT_ARRAY | VT_R8 tipinde VARIANT nesnesi olarak verilmelidir.
        Bu metot her çizim metodunun içinde tekrar tekrar yazılması gereken
        bu dönüşümü merkezi olarak yapar.

        Parametreler:
            x (float): Noktanın X koordinatı.
            y (float): Noktanın Y koordinatı.
            z (float): Noktanın Z koordinatı. Varsayılan: 0 (2D çizim).

        Dönüş değeri:
            win32com.client.VARIANT — AutoCAD'e gönderilebilir nokta nesnesi.
        """
        return win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8,   # Double precision float dizisi
            (float(x), float(y), float(z))           # Koordinatları float'a zorla
        )

    def cizgi_ciz(self, baslangic, bitis):
        """
        İki nokta arasına düz çizgi çizer.

        Parametreler:
            baslangic (tuple): Çizginin başlangıç noktası, (x, y) formatında.
            bitis     (tuple): Çizginin bitiş noktası, (x, y) formatında.

        Dönüş değeri:
            win32com object — AutoCAD'de oluşturulan AcDbLine nesnesi.

        Hatalar:
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        if not self.connector.bagli_mi():
            raise AutoCADKapaliHatasi(
                "AutoCAD bağlantısı yok. Önce connector.baglan() çağırın."
            )

        # Başlangıç ve bitiş noktalarını VARIANT formatına dönüştür
        p1 = self._nokta_olustur(baslangic[0], baslangic[1])
        p2 = self._nokta_olustur(bitis[0], bitis[1])

        # Model Uzayına çizgiyi ekle ve nesneyi döndür
        return self.connector.model_uzayi().AddLine(p1, p2)

    def kare_ciz(self, sol_alt, kenar):
        """
        Verilen sol alt köşeden başlayarak belirtilen kenar uzunluğunda kare çizer.

        Kare 4 ayrı çizgiden oluşur:
            Alt kenar  → sağ alt köşeye
            Sağ kenar  → sağ üst köşeye
            Üst kenar  → sol üst köşeye
            Sol kenar  → sol alt köşeye (başa)

        Parametreler:
            sol_alt (tuple): Karenin sol alt köşesi, (x, y) formatında.
            kenar   (float): Karenin kenar uzunluğu.

        Dönüş değeri:
            list — Çizilen 4 AcDbLine nesnesinin listesi.

        Hatalar:
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        return self.dikdortgen_ciz(sol_alt, en=kenar, boy=kenar)

    def dikdortgen_ciz(self, sol_alt, en, boy):
        """
        Verilen sol alt köşeden başlayarak belirtilen en ve boy değerlerinde
        dikdörtgen çizer.

        Dikdörtgen 4 ayrı çizgiden oluşur:
            Alt kenar  → (x, y) → (x+en, y)
            Sağ kenar  → (x+en, y) → (x+en, y+boy)
            Üst kenar  → (x+en, y+boy) → (x, y+boy)
            Sol kenar  → (x, y+boy) → (x, y)

        Parametreler:
            sol_alt (tuple): Dikdörtgenin sol alt köşesi, (x, y) formatında.
            en      (float): X yönündeki uzunluk (yatay).
            boy     (float): Y yönündeki uzunluk (dikey).

        Dönüş değeri:
            list — Çizilen 4 AcDbLine nesnesinin listesi.

        Hatalar:
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        x, y = sol_alt[0], sol_alt[1]

        # Dört köşenin koordinatları
        sol_alt_k  = (x,      y)
        sag_alt_k  = (x + en, y)
        sag_ust_k  = (x + en, y + boy)
        sol_ust_k  = (x,      y + boy)

        # Dört kenarı sırayla çiz ve çizgi nesnelerini topla
        cizgiler = [
            self.cizgi_ciz(sol_alt_k, sag_alt_k),   # Alt kenar
            self.cizgi_ciz(sag_alt_k, sag_ust_k),   # Sağ kenar
            self.cizgi_ciz(sag_ust_k, sol_ust_k),   # Üst kenar
            self.cizgi_ciz(sol_ust_k, sol_alt_k),   # Sol kenar
        ]

        return cizgiler

    def daire_ciz(self, merkez, yaricap):
        """
        Verilen merkez noktası ve yarıçap değeriyle daire çizer.

        Parametreler:
            merkez   (tuple): Dairenin merkez noktası, (x, y) formatında.
            yaricap  (float): Dairenin yarıçapı.

        Dönüş değeri:
            win32com object — AutoCAD'de oluşturulan AcDbCircle nesnesi.

        Hatalar:
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError   — Aktif çizim belgesi yoksa.
        """
        if not self.connector.bagli_mi():
            raise AutoCADKapaliHatasi(
                "AutoCAD bağlantısı yok. Önce connector.baglan() çağırın."
            )

        # Merkez noktasını VARIANT formatına dönüştür
        merkez_varyant = self._nokta_olustur(merkez[0], merkez[1])

        # Daireyi Model Uzayına ekle
        return self.connector.model_uzayi().AddCircle(merkez_varyant, float(yaricap))

    def poligon_ciz(self, koseler):
        """
        Verilen köşe listesiyle kapalı poligon çizer.

        Her ardışık köşe arasına çizgi çeker; son köşeden ilk köşeye de
        çizgi çekerek poligonu kapatır.

        Parametreler:
            koseler (list): Köşe koordinatlarının listesi.
                            Örnek: [(0,0), (100,0), (50,80)]
                            En az 3 köşe gereklidir.

        Dönüş değeri:
            list — Çizilen AcDbLine nesnelerinin listesi.
                   Köşe sayısı kadar çizgi döner (kapalı olduğu için).

        Hatalar:
            ValueError      — 3'ten az köşe verilirse.
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError    — Aktif çizim belgesi yoksa.
        """
        if len(koseler) < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(len(koseler))

        cizgiler = []

        # Ardışık köşeler arasında çizgi çiz
        for i in range(len(koseler) - 1):
            cizgi = self.cizgi_ciz(koseler[i], koseler[i + 1])
            cizgiler.append(cizgi)

        # Son köşeyi ilk köşeye bağlayarak poligonu kapat
        kapatma = self.cizgi_ciz(koseler[-1], koseler[0])
        cizgiler.append(kapatma)

        return cizgiler

    def lwpoligon_ciz(self, koseler):
        """
        Verilen köşe listesiyle kapalı LightWeight Polyline çizer.

        Tüm köşeleri tek bir AcDbPolyline entity olarak ekler; AutoCAD'de
        parsel/arsa sınırlarını temsil etmek için standart yöntemdir.
        Bu şekilde çizilen poligon tek tıklamayla seçilebilir ve
        AutoCAD'in alan/çevre araçlarıyla ölçülebilir.

        poligon_ciz'den farkı:
            poligon_ciz  → N ayrı AcDbLine nesnesi döner
            lwpoligon_ciz → 1 adet kapalı AcDbPolyline nesnesi döner

        Parametreler:
            koseler (list): Köşe koordinatlarının listesi.
                            Örnek: [(0,0), (100,0), (100,100), (0,100)]
                            En az 3 köşe gereklidir.

        Dönüş değeri:
            win32com object — Kapalı AcDbPolyline nesnesi.

        Hatalar:
            ValueError      — 3'ten az köşe verilirse.
            ConnectionError — AutoCAD bağlantısı kurulmamışsa.
            RuntimeError    — Aktif çizim belgesi yoksa.
        """
        if len(koseler) < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(len(koseler))

        if not self.connector.bagli_mi():
            raise AutoCADKapaliHatasi(
                "AutoCAD bağlantısı yok. Önce connector.baglan() çağırın."
            )

        # AddLightWeightPolyline düz bir [x1,y1, x2,y2, ...] dizisi ister
        duz_dizi = []
        for kose in koseler:
            duz_dizi.append(float(kose[0]))
            duz_dizi.append(float(kose[1]))

        koordinat_varyant = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8,
            duz_dizi
        )

        polyline = self.connector.model_uzayi().AddLightWeightPolyline(koordinat_varyant)
        polyline.Closed = True  # Son köşeyi ilk köşeye otomatik bağla

        return polyline
