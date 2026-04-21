"""
cekme.py — CekmeCizici modülü

Türkiye yapı mevzuatında tanımlanan ön, arka ve yan bahçe çekme
mesafelerini arsa sınırından içeri doğru ofset alarak AutoCAD'de çizer.

Bağımlılıklar:
    - AutoCADConnector: AutoCAD COM bağlantısını yönetir
    - GeometryDrawer: Geometrik şekilleri çizer
    - LayerManager: Katman oluşturma ve yönetimi
    - GeometryUtils: Poligon ofset ve alan hesaplamaları
"""

from autolay.core.baglanti import AutoCADConnector
from autolay.mimari.veriler import MimariVeriler
from autolay.drawing.shapes import GeometryDrawer
from autolay.drawing.layers import LayerManager
from autolay.utils.geometri import GeometryUtils
from autolay.utils.logger import logger_olustur
from autolay.core.hatalar import YetersizKoseHatasi
from autolay.config.sabitler import MIN_POLIGON_KOSE_SAYISI


class CekmeCizici:
    """
    Arsa sınırından belirtilen mesafe kadar içeri çekilerek oluşan
    yapı yaklaşma sınırını AutoCAD'de çizen sınıf.

    Kullanım sırası:
        1. CekmeCizici(connector) ile nesne oluştur
        2. arsa_koseleri_ayarla(koseler) ile arsa köşelerini ver
        3. cekme_mesafesi_ayarla(mesafe) ile çekme mesafesini belirle
        4. ciz() ile AutoCAD'e çiz
        5. İsteğe bağlı: cekme_koseleri() ile hesaplanan köşeleri al
    """

    def __init__(self, connector: AutoCADConnector):
        """
        CekmeCizici nesnesini başlatır.

        Parametreler:
            connector (AutoCADConnector): Aktif AutoCAD COM bağlantısı.
        """
        self.connector = connector
        self.layer_mgr = LayerManager(connector)
        self.drawer = GeometryDrawer(connector)
        self.geo = GeometryUtils()
        self.log = logger_olustur(__name__)
        self.arsa_koseleri = None
        self.mesafe = None
        self._cekme_koseleri = None
        self.kenar_mesafeleri = None  # list veya None
        self.KATMAN_ADI = "AUTOLAY_CEKME"
        self.KATMAN_RENGI = "sari"

    def arsa_koseleri_ayarla(self, koseler: list):
        """
        Çekme hesabının yapılacağı arsa köşe koordinatlarını ayarlar.

        Parametreler:
            koseler (list): (x, y) veya (x, y, z) tuple'larından oluşan liste.
                            En az MIN_POLIGON_KOSE_SAYISI kadar köşe olmalıdır.

        Hata:
            YetersizKoseHatasi: Köşe sayısı minimumun altındaysa fırlatılır.
        """
        if len(koseler) < MIN_POLIGON_KOSE_SAYISI:
            raise YetersizKoseHatasi(kose_sayisi=len(koseler))
        self.arsa_koseleri = koseler
        self.log.info(f"{len(koseler)} arsa köşe noktası alındı.")

    def cekme_mesafesi_ayarla(self, mesafe: float):
        """
        Arsa sınırından içeri uygulanacak çekme mesafesini ayarlar.

        Parametreler:
            mesafe (float): Metre cinsinden pozitif çekme mesafesi.
                            Pozitif değer her zaman içeri yönde ofset uygular.

        Hata:
            ValueError: Mesafe sıfır veya negatifse fırlatılır.
        """
        if mesafe <= 0:
            raise ValueError("Çekme mesafesi pozitif olmalı.")
        self.mesafe = mesafe
        self.log.info(f"Çekme mesafesi ayarlandı: {mesafe} m")

    def kenar_mesafesi_ayarla(self, indeks: int, mesafe: float):
        """
        Belirli bir kenara ait çekme mesafesini ayarlar.

        Kenar indeksi i, koseler[i] → koseler[i+1] kenarına karşılık gelir.
        Daha önce kenar_mesafeleri listesi oluşturulmamışsa arsa köşe sayısı
        kadar 0 ile doldurularak oluşturulur; ardından istenen indeks güncellenir.

        Parametreler:
            indeks (int)  : Güncellenmek istenen kenarın sıfır tabanlı indeksi.
            mesafe (float): Pozitif çekme mesafesi (metre).

        Hata:
            ValueError: arsa_koseleri henüz ayarlanmamışsa.
            ValueError: indeks geçerli aralık dışındaysa.
            ValueError: mesafe sıfır veya negatifse.
        """
        if self.arsa_koseleri is None:
            raise ValueError("Önce arsa_koseleri_ayarla çağır.")
        n = len(self.arsa_koseleri)
        if indeks < 0 or indeks >= n:
            raise ValueError(
                f"indeks {indeks} geçersiz. Geçerli aralık: 0–{n - 1}."
            )
        if mesafe <= 0:
            raise ValueError("Mesafe pozitif olmalı.")
        # İlk kez çağrılıyorsa listeyi sıfırlarla başlat
        if self.kenar_mesafeleri is None:
            self.kenar_mesafeleri = [0] * n
        self.kenar_mesafeleri[indeks] = mesafe
        self.log.info(f"Kenar {indeks} mesafesi ayarlandı: {mesafe} m")

    def tum_kenarlar_ayarla(self, mesafeler: list):
        """
        Tüm kenarlara ait çekme mesafelerini tek seferde ayarlar.

        Parametreler:
            mesafeler (list): Her kenara ait çekme mesafesi.
                              len(mesafeler) == len(arsa_koseleri) olmalıdır.

        Hata:
            ValueError: arsa_koseleri henüz ayarlanmamışsa.
            ValueError: liste uzunluğu köşe sayısıyla eşleşmiyorsa.
        """
        if self.arsa_koseleri is None:
            raise ValueError("Önce arsa_koseleri_ayarla çağır.")
        n = len(self.arsa_koseleri)
        if len(mesafeler) != n:
            raise ValueError(
                f"mesafeler uzunluğu ({len(mesafeler)}) köşe sayısıyla "
                f"({n}) eşleşmeli."
            )
        self.kenar_mesafeleri = mesafeler
        self.log.info(f"Tüm kenar mesafeleri ayarlandı: {mesafeler}")

    def verilerden_hesapla(self, veri: MimariVeriler):
        """
        MimariVeriler nesnesinden tüm konfigürasyonu otomatik okuyup uygular.

        Bu metot aşağıdakileri sırasıyla yapar:
        1. Arsa köşelerini veri'den alır
        2. Yapı nizamına göre başlangıç çekme mesafelerini ayarlar:
           - "bitisik" nizam ve bitisik_kenarlar varsa → bitisik_nizam_ayarla çağrılır
           - Diğer durumda → veri.cekme_baslangic_mesafeleri() kullanılır
        3. Kat sayısı > 4 ise kademeli çekme uygulanır
        4. Bina yüksekliği varsa yüksek yapı uyarısı verilir (60.50m+)

        Parametreler:
            veri (MimariVeriler): Tüm proje verilerini içeren nesne.

        Not: Bu metot ciz() çağırmaz. Sadece iç durumu hazırlar.
        Kullanıcı hazırlık sonrası ciz() çağırmalıdır.
        """

        # Adım 1: Arsa köşelerini ayarla
        self.arsa_koseleri_ayarla(veri.arsa_koseleri)

        # Adım 2: Yapı nizamına göre başlangıç mesafeleri
        if veri.yapi_nizami == "bitisik" and len(veri.bitisik_kenarlar) > 0:
            # Bitişik nizam: bitisik_nizam_ayarla kullan
            # diger_mesafeler için cekme_baslangic_mesafeleri'nden bitişik olmayanları al
            baslangic = veri.cekme_baslangic_mesafeleri()
            diger_mesafeler = {
                i: baslangic[i]
                for i in range(len(baslangic))
                if i not in veri.bitisik_kenarlar
            }
            self.bitisik_nizam_ayarla(
                bitisik_kenarlar=veri.bitisik_kenarlar,
                diger_mesafeler=diger_mesafeler
            )
        else:
            # Ayrık nizam (veya bitişik ama bitişik kenar yok — hata)
            baslangic = veri.cekme_baslangic_mesafeleri()
            self.tum_kenarlar_ayarla(baslangic)

        # Adım 3: Kademeli çekme (4 kat üstü)
        if veri.kat_sayisi > 4:
            self.kademeli_cekme_hesapla(
                kat_sayisi=veri.kat_sayisi,
                on_kenar_indeks=veri.on_kenar_indeks,
                park_komsusu_kenarlar=veri.park_komsusu_kenarlar,
                bitisik_kenarlar=veri.bitisik_kenarlar,
            )

        # Adım 4: Yüksek yapı uyarısı (60.50m+)
        if veri.bina_yuksekligi_m is not None and veri.bina_yuksekligi_m >= 60.50:
            self.log.warning(
                f"⚠ Bina yüksekliği {veri.bina_yuksekligi_m}m ≥ 60.50m. "
                f"Yönetmelik gereği tüm kenarlar minimum 15m çekilmelidir. "
                f"Mevcut mesafeler: {self.kenar_mesafeleri}. "
                f"Gerekirse manuel düzenleyin."
            )

        self.log.info(
            f"verilerden_hesapla tamamlandı. "
            f"Mesafeler: {self.kenar_mesafeleri}"
        )

    def bitisik_nizam_ayarla(self, bitisik_kenarlar: list, diger_mesafeler: dict):
        """
        Bitişik nizam yapı için çekme mesafelerini ayarlar.

        Bitişik nizamda bir veya iki yan komşu parsele yapışık inşa edilir.
        Bitişik olunan kenarlarda çekme yapılmaz (mesafe = 0).
        Diğer kenarlarda normal çekme uygulanır.

        Parametreler:
            bitisik_kenarlar (list): Komşuya yapışık kenarların indeksleri.
                                      Bu kenarlarda çekme mesafesi 0 olur.
            diger_mesafeler (dict) : Bitişik olmayan kenarların mesafeleri.
                                      {indeks: mesafe} formatında.
                                      Örnek: {0: 5, 2: 3}

        Hata:
            ValueError: arsa_koseleri henüz ayarlanmamışsa.
            ValueError: Herhangi bir kenar indeksi geçersizse.
            ValueError: bitisik_kenarlar ile diger_mesafeler kesişiyorsa.
            ValueError: bitisik_kenarlar + diger_mesafeler tüm kenarları kapsamıyorsa.
            ValueError: Tüm kenarlar bitişik ise (en az bir çekme olmalı).

        Örnek:
            # Kenar 1 ve 3 komşuya bitişik, kenar 0 (ön) 5m, kenar 2 (arka) 3m
            cekme.bitisik_nizam_ayarla(
                bitisik_kenarlar=[1, 3],
                diger_mesafeler={0: 5, 2: 3}
            )
            # Sonuç: kenar_mesafeleri = [5, 0, 3, 0]
        """

        # --- Adım 1: arsa_koseleri kontrolü ---
        if self.arsa_koseleri is None:
            raise ValueError("Önce arsa_koseleri_ayarla çağır.")

        n = len(self.arsa_koseleri)

        # --- Adım 2: bitisik_kenarlar indeks geçerlilik kontrolü ---
        for i in bitisik_kenarlar:
            if i < 0 or i >= n:
                raise ValueError(
                    f"bitisik_kenarlar içindeki {i} indeksi geçersiz. "
                    f"Geçerli aralık: 0–{n - 1}."
                )

        # --- Adım 3: diger_mesafeler indeks geçerlilik kontrolü ---
        for i in diger_mesafeler:
            if i < 0 or i >= n:
                raise ValueError(
                    f"diger_mesafeler içindeki {i} indeksi geçersiz. "
                    f"Geçerli aralık: 0–{n - 1}."
                )

        # --- Adım 4: Çakışma kontrolü — bir kenar her iki listede olamaz ---
        cakisan = set(bitisik_kenarlar) & set(diger_mesafeler.keys())
        if cakisan:
            raise ValueError(
                f"Şu kenar indeksleri hem bitişik hem mesafeli olarak verildi: "
                f"{sorted(cakisan)}. Her kenar yalnızca bir listede yer almalı."
            )

        # --- Adım 5: Kapsama kontrolü — tüm kenarlar belirtilmeli ---
        tum_belirtilen = set(bitisik_kenarlar) | set(diger_mesafeler.keys())
        eksik = set(range(n)) - tum_belirtilen
        if eksik:
            raise ValueError(
                f"Şu kenar indeksleri belirtilmedi: {sorted(eksik)}. "
                "Her kenar ya bitisik_kenarlar'da ya da diger_mesafeler'de olmalı."
            )

        # --- Adım 6: Tüm kenarlar bitişik olamaz (en az bir çekme şart) ---
        if len(bitisik_kenarlar) == n:
            raise ValueError("En az bir kenarda çekme mesafesi olmalı.")

        # --- Adım 7: kenar_mesafeleri listesini oluştur ---
        # Önce tümünü 0 ile başlat; bitişik kenarlar zaten 0 kalır.
        self.kenar_mesafeleri = [0] * n

        # Çekme yapılacak kenarlara mesafeleri ata
        for i, m in diger_mesafeler.items():
            self.kenar_mesafeleri[i] = m

        # --- Adım 8: Sonucu logla ---
        self.log.info(
            f"Bitişik nizam: bitişik kenarlar={sorted(bitisik_kenarlar)}, "
            f"mesafeler={self.kenar_mesafeleri}"
        )

    def _geometri_uyarilari(self):
        """
        Çekme uygulanmadan önce arsa geometrisinde risk taşıyan durumları tespit eder.

        Kontroller:
            1. Kısa kenar: Kenar uzunluğu, o kenara uygulanacak mesafenin
               2 katından küçükse çekme çizgisi karşı kenarı geçer. Uyarı verir.
            2. Dar açı: Köşe iç açısı 30°'den küçükse çekme köşesi çok uzağa
               kayar. Uyarı verir.

        Uyarılar log.warning ile bildirilir; hata fırlatılmaz.
        """
        import math

        n = len(self.arsa_koseleri)

        # --- Kontrol 1: Kenar uzunlukları ---
        # Her kenarın uzunluğu, o kenara atanan mesafenin en az 2 katı olmalı.
        # Aksi hâlde karşı kenardan taşma oluşur ve sonuç geometrik olarak anlamsızlaşır.
        for i in range(n):
            x1, y1 = self.arsa_koseleri[i]
            x2, y2 = self.arsa_koseleri[(i + 1) % n]
            kenar_uzunlugu = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            # Hangi mod aktifse o kenara ait mesafeyi al
            if self.kenar_mesafeleri is not None:
                kenar_mesafesi = self.kenar_mesafeleri[i]
            else:
                kenar_mesafesi = self.mesafe

            # Mesafe 0 ise (bitişik kenar) bu kontrol anlamsız, atla
            if kenar_mesafesi > 0 and kenar_uzunlugu <= kenar_mesafesi * 2:
                self.log.warning(
                    f"⚠ Kenar {i}: uzunluk {kenar_uzunlugu:.2f}m, "
                    f"çekme mesafesi {kenar_mesafesi}m. "
                    f"Kenar çekme mesafesinin 2 katından küçük, "
                    f"sonuç güvenilmez olabilir."
                )

        # --- Kontrol 2: Köşe iç açıları ---
        # 30°'den küçük açılarda parametrik kesişim noktası çok uzağa kayar;
        # çekme sonucu görsel olarak yanlış görünebilir.
        for i in range(n):
            # Köşe i'ye gelen iki kenarın uç noktaları
            onceki = self.arsa_koseleri[(i - 1) % n]
            merkez = self.arsa_koseleri[i]
            sonraki = self.arsa_koseleri[(i + 1) % n]

            # Merkez köşeden önceki ve sonraki köşeye vektörler
            v1x = onceki[0] - merkez[0]
            v1y = onceki[1] - merkez[1]
            v2x = sonraki[0] - merkez[0]
            v2y = sonraki[1] - merkez[1]

            v1_len = math.sqrt(v1x * v1x + v1y * v1y)
            v2_len = math.sqrt(v2x * v2x + v2y * v2y)

            # Sıfır uzunluklu kenar varsa açı hesaplanamaz, atla
            if v1_len < 1e-10 or v2_len < 1e-10:
                continue

            # İç açı: cos(θ) = (v1 · v2) / (|v1| × |v2|)
            cos_aci = (v1x * v2x + v1y * v2y) / (v1_len * v2_len)
            # Float hataları için [-1, 1] aralığına sıkıştır
            cos_aci = max(-1.0, min(1.0, cos_aci))
            aci_derece = math.degrees(math.acos(cos_aci))

            if aci_derece < 30:
                self.log.warning(
                    f"⚠ Köşe {i}: iç açı {aci_derece:.1f}° — çok keskin. "
                    f"Çekme çizgisi bu köşede çok uzağa kayar, sonucu kontrol edin."
                )

    def ciz(self):
        """
        Çekme sınırı poligonunu hesaplar ve AutoCAD'e çizer.

        Arsa köşelerinden self.mesafe kadar içeri ofset alır,
        AUTOLAY_CEKME katmanında sarı renkte çizer.

        Hata:
            ValueError: arsa_koseleri_ayarla veya cekme_mesafesi_ayarla
                        daha önce çağrılmamışsa fırlatılır.
        """
        if self.arsa_koseleri is None:
            raise ValueError("Önce arsa_koseleri_ayarla çağır.")

        if self.kenar_mesafeleri is not None:
            # Kenar bazlı mod: her kenara ayrı mesafe uygulanır
            if all(m == 0 for m in self.kenar_mesafeleri):
                raise ValueError("En az bir kenara çekme mesafesi atanmalı.")
            # 0 değeri meşru bir durumdur: bitişik nizamda komşu parsele yapışık
            # kenarı ifade eder. Kontrol sadece tümünün 0 olması durumunu engeller.
            self._geometri_uyarilari()
            self._cekme_koseleri = self.geo.poligon_offset_kenar_bazli(
                self.arsa_koseleri, self.kenar_mesafeleri
            )
            mesafe_log = self.kenar_mesafeleri
        elif self.mesafe is not None:
            # Tek mesafe modu: tüm kenarlara aynı mesafe
            self._geometri_uyarilari()
            self._cekme_koseleri = self.geo.poligon_offset(
                self.arsa_koseleri, self.mesafe
            )
            mesafe_log = self.mesafe
        else:
            raise ValueError(
                "Önce cekme_mesafesi_ayarla veya tum_kenarlar_ayarla çağır."
            )

        self.layer_mgr.katman_olustur(self.KATMAN_ADI, renk=self.KATMAN_RENGI)
        self.layer_mgr.aktif_katman_yap(self.KATMAN_ADI)
        self.drawer.poligon_ciz(self._cekme_koseleri)

        self.log.info(
            f"Çekme çizildi. Mesafeler: {mesafe_log}, "
            f"Alan: {self.geo.poligon_alani(self._cekme_koseleri):.2f} m²"
        )

    def kademeli_cekme_hesapla(
        self,
        kat_sayisi: int,
        on_kenar_indeks: int,
        park_komsusu_kenarlar: list = None,
        bitisik_kenarlar: list = None
    ):
        """
        Kat sayısına göre kademeli çekme mesafesi hesaplar ve günceller.

        Kural: 4 kattan fazla her kat için yan/arka kenarlara +0.50m eklenir.
        Park komşusuna bakan kenarlara EKLENMEZ.
        Ön kenara EKLENMEZ (sadece yan/arka).
        Bitişik kenarlara EKLENMEZ (0 kalır).

        Parametreler:
            kat_sayisi (int)             : Binanın toplam kat sayısı.
            on_kenar_indeks (int)        : Ön bahçe kenarının indeksi
                                           (bu kenara ekleme uygulanmaz).
            park_komsusu_kenarlar (list) : Park komşusu olan kenar indeksleri;
                                           bu kenarlara da ekleme yapılmaz.
                                           None ise boş liste kabul edilir.
            bitisik_kenarlar (list)      : Komşuya yapışık kenarların indeksleri.
                                           Bu kenarlara kademeli ekleme yapılmaz
                                           (0 kalır). None ise boş liste kabul edilir.

        Hata:
            ValueError: arsa_koseleri henüz ayarlanmamışsa.
            ValueError: kenar_mesafeleri henüz ayarlanmamışsa.
            ValueError: kat_sayisi <= 0 ise.
            ValueError: on_kenar_indeks geçerli aralık dışındaysa.

        Örnek:
            # 7 katlı bina, ön kenar 0, kenar 2 park komşusu
            cekme.tum_kenarlar_ayarla([5, 3, 3, 3])
            cekme.kademeli_cekme_hesapla(7, on_kenar_indeks=0, park_komsusu_kenarlar=[2])
            # Sonuç: [5, 4.5, 3, 4.5]
        """

        # --- Adım 1: Ön koşul kontrolleri ---
        if self.arsa_koseleri is None:
            raise ValueError("Önce arsa_koseleri_ayarla çağır.")
        if self.kenar_mesafeleri is None:
            raise ValueError("Önce tum_kenarlar_ayarla çağır.")
        if kat_sayisi <= 0:
            raise ValueError(f"kat_sayisi pozitif olmalı, verildi: {kat_sayisi}.")
        n = len(self.arsa_koseleri)
        if on_kenar_indeks < 0 or on_kenar_indeks >= n:
            raise ValueError(
                f"on_kenar_indeks {on_kenar_indeks} geçersiz. "
                f"Geçerli aralık: 0–{n - 1}."
            )

        # --- Adım 2: None parametreleri boş listeye dönüştür ---
        if park_komsusu_kenarlar is None:
            park_komsusu_kenarlar = []
        if bitisik_kenarlar is None:
            bitisik_kenarlar = []

        # --- Adım 3: 4 veya daha az katta kademeli artış gerekmez ---
        if kat_sayisi <= 4:
            self.log.info(
                f"Kat sayısı {kat_sayisi} ≤ 4 — kademeli çekme gerekmez, "
                "mesafeler değiştirilmedi."
            )
            return

        # --- Adım 4: Ekleme miktarını hesapla ---
        # 4'ü aşan her kat için 0.50m ekleme uygulanır
        ekstra_kat = kat_sayisi - 4
        ekleme = ekstra_kat * 0.5
        self.log.info(
            f"Kademeli çekme: {kat_sayisi} kat → "
            f"{ekstra_kat} ekstra kat × 0.50m = +{ekleme:.2f}m"
        )

        # --- Adım 5: Her kenara ekleme uygula (ön ve park komşusu hariç) ---
        for i in range(n):
            # Ön kenar ise atla
            if i == on_kenar_indeks:
                self.log.info(f"  Kenar {i}: ön kenar — atlandı.")
                continue
            # Park komşusu kenar ise atla
            if i in park_komsusu_kenarlar:
                self.log.info(f"  Kenar {i}: park komşusu — atlandı.")
                continue
            # Bitişik kenar ise atla
            if i in bitisik_kenarlar:
                self.log.info(f"  Kenar {i}: bitişik kenar — atlandı (0 kalır).")
                continue
            # Yan veya arka kenar: ekleme uygula
            self.kenar_mesafeleri[i] += ekleme
            self.log.info(
                f"  Kenar {i}: {self.kenar_mesafeleri[i] - ekleme:.2f}m "
                f"→ {self.kenar_mesafeleri[i]:.2f}m"
            )

        # --- Adım 6: Güncel mesafe listesini raporla ---
        self.log.info(
            f"Kademeli çekme tamamlandı. Güncel mesafeler: {self.kenar_mesafeleri}"
        )

    def cekme_koseleri(self) -> list:
        """
        Hesaplanan çekme sınırı köşe koordinatlarını döndürür.

        Dönüş:
            list: Çekme poligonunun (x, y) köşe listesi.

        Hata:
            ValueError: ciz() henüz çağrılmamışsa fırlatılır.
        """
        if self._cekme_koseleri is None:
            raise ValueError("Önce ciz() çağır.")
        return self._cekme_koseleri
