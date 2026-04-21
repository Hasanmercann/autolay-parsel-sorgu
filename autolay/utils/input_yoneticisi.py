"""
autolay/utils/input_yoneticisi.py

Kullanıcıdan terminal üzerinden veri alan yardımcı sınıf.

UYARI: InputManager sadece GELİŞTİRME VE TEST amaçlıdır.
Gerçek kullanıcı arayüzü ileride GUI katmanında ayrıca yazılacak.
Bu sınıf hiçbir zaman production mimari modüllerinden çağrılmamalıdır.
"""

from autolay.utils.logger import logger_olustur
from autolay.core.hatalar import GecersizKoordinatHatasi


class InputManager:
    """
    Terminal üzerinden kullanıcı girdisi alan yardımcı sınıf.

    Yalnızca geliştirme ve test senaryolarında kullanılır.
    """

    def __init__(self):
        """
        InputManager nesnesini başlatır.

        Maksimum deneme sayısını 3 olarak ayarlar.
        """
        self.log = logger_olustur(__name__)
        self.max_deneme = 3

    def sayi_al(self, mesaj: str, min=None, max=None, ondalikli: bool = True):
        """
        Kullanıcıdan sayısal değer alır; isteğe bağlı aralık doğrulaması yapar.

        Parametreler:
            mesaj      (str):   Kullanıcıya gösterilecek soru metni.
            min        (float): İzin verilen minimum değer. Verilmezse alt sınır yok.
            max        (float): İzin verilen maksimum değer. Verilmezse üst sınır yok.
            ondalikli  (bool):  True → float, False → int beklenir.

        Dönüş değeri:
            float veya int — Kullanıcının girdiği geçerli sayı.

        Hatalar:
            GecersizKoordinatHatasi — 3 başarısız denemeden sonra fırlatılır.

        Kullanım:
            deger = im.sayi_al("Parsel genişliği", min=1.0, max=500.0)
            kat = im.sayi_al("Kat sayısı", min=1, max=20, ondalikli=False)
        """
        tip = float if ondalikli else int
        tip_adi = "ondalıklı sayı" if ondalikli else "tam sayı"

        for deneme in range(1, self.max_deneme + 1):
            girdi = input(f"{mesaj}: ").strip()
            try:
                deger = tip(girdi)
            except ValueError:
                self.log.warning(
                    f"Geçersiz giriş '{girdi}': {tip_adi} bekleniyor. "
                    f"({deneme}/{self.max_deneme})"
                )
                continue

            if min is not None and deger < min:
                self.log.warning(
                    f"'{deger}' çok küçük: minimum {min}. "
                    f"({deneme}/{self.max_deneme})"
                )
                continue

            if max is not None and deger > max:
                self.log.warning(
                    f"'{deger}' çok büyük: maksimum {max}. "
                    f"({deneme}/{self.max_deneme})"
                )
                continue

            return deger

        raise GecersizKoordinatHatasi(
            f"'{mesaj}' için {self.max_deneme} denemede geçerli değer alınamadı."
        )

    def koordinat_al(self, mesaj: str) -> tuple[float, float]:
        """
        Kullanıcıdan 2D koordinat alır.

        Virgül veya boşlukla ayrılmış iki sayı kabul edilir.
        Geçerli formatlar: "10, 20" / "10,20" / "10.5 20.3"

        Parametreler:
            mesaj (str): Kullanıcıya gösterilecek soru metni.

        Dönüş değeri:
            tuple[float, float] — (x, y) koordinat çifti.

        Hatalar:
            GecersizKoordinatHatasi — 3 başarısız denemeden sonra fırlatılır.

        Kullanım:
            x, y = im.koordinat_al("Parsel sol alt köşesi")
        """
        for deneme in range(1, self.max_deneme + 1):
            girdi = input(f"{mesaj} (x, y formatında): ").strip()

            # Virgülü boşlukla değiştirip token'lara böl
            parcalar = girdi.replace(",", " ").split()

            if len(parcalar) != 2:
                self.log.warning(
                    f"Geçersiz format '{girdi}': tam olarak 2 değer gereklidir. "
                    f"({deneme}/{self.max_deneme})"
                )
                continue

            try:
                x, y = float(parcalar[0]), float(parcalar[1])
            except ValueError:
                self.log.warning(
                    f"Geçersiz koordinat '{girdi}': sayısal değerler bekleniyor. "
                    f"({deneme}/{self.max_deneme})"
                )
                continue

            return (x, y)

        raise GecersizKoordinatHatasi(
            f"'{mesaj}' için {self.max_deneme} denemede geçerli koordinat alınamadı."
        )

    def evet_hayir(self, mesaj: str, varsayilan: bool | None = None) -> bool:
        """
        Kullanıcıdan evet/hayır yanıtı alır.

        Parametreler:
            mesaj      (str):        Kullanıcıya gösterilecek soru metni.
            varsayilan (bool|None):  True → Enter'da "evet" kabul edilir,
                                     False → Enter'da "hayır" kabul edilir,
                                     None → boş giriş kabul edilmez.

        Dönüş değeri:
            bool — True: evet, False: hayır.

        Hatalar:
            ValueError — 3 başarısız denemeden sonra fırlatılır.

        Kullanım:
            devam = im.evet_hayir("Devam edilsin mi", varsayilan=True)
        """
        # Varsayılana göre seçenek göstergesini belirle
        if varsayilan is True:
            secenek = "(E/h)"
        elif varsayilan is False:
            secenek = "(e/H)"
        else:
            secenek = "(E/H)"

        evet_degerleri = {"e", "evet", "y", "yes"}
        hayir_degerleri = {"h", "hayir", "hayır", "n", "no"}

        for deneme in range(1, self.max_deneme + 1):
            girdi = input(f"{mesaj} {secenek}: ").strip().lower()

            if girdi == "" and varsayilan is not None:
                return varsayilan

            if girdi in evet_degerleri:
                return True

            if girdi in hayir_degerleri:
                return False

            self.log.warning(
                f"Geçersiz yanıt '{girdi}': e/evet/y/yes veya h/hayır/n/no giriniz. "
                f"({deneme}/{self.max_deneme})"
            )

        raise ValueError(
            f"'{mesaj}' için {self.max_deneme} denemede geçerli yanıt alınamadı."
        )
