"""
autolay/utils/logger.py

AutoLay genelinde kullanılan merkezi loglama altyapısı.

Neden print() değil logger?
    - print() mesajları her zaman ekrana çıkar, susturulamaz.
    - Logger'lar seviye filtresi ile çalışır: geliştirme sırasında DEBUG,
      üretimde sadece WARNING mesajlarını görmek için tek satır yeterlidir.
    - Aynı anda hem konsola hem dosyaya yazmak mümkündür.
    - Her mesaj otomatik olarak zaman damgası ve kaynak modül adını taşır;
      sonradan analiz için logs/autolay.log dosyasında kalıcı kayıt oluşur.

Kullanım:
    from autolay.utils.logger import logger_olustur
    log = logger_olustur(__name__)
    log.info("Bağlantı kuruldu.")
    log.warning("Katman zaten mevcut.")
    log.error("AutoCAD yanıt vermedi.")
"""

import logging
import sys
from pathlib import Path

from autolay.config.sabitler import PROJE_ADI


# Proje kök dizini: bu dosyanın konumundan 3 seviye yukarı
# autolay/utils/logger.py → autolay/utils → autolay → proje kökü
_KOK_DIZIN = Path(__file__).resolve().parent.parent.parent

# Log dosyasının yazılacağı klasör ve dosya yolu
_LOG_KLASORU = _KOK_DIZIN / "logs"
_LOG_DOSYASI = _LOG_KLASORU / "autolay.log"

# Konsol ve dosya için ayrı format şablonları
_KONSOL_FORMATI = "%(asctime)s | %(levelname)-8s | %(message)s"
_DOSYA_FORMATI  = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

_KONSOL_TARIH_FORMATI = "%H:%M:%S"
_DOSYA_TARIH_FORMATI  = "%Y-%m-%d %H:%M:%S"

# Kök logger adı: tüm "autolay.*" logger'ları bu logger'ın çocuğudur.
# Handler'lar yalnızca bu kök logger'a eklenir; böylece her modülde
# ayrı handler oluşturulmaz ve log satırları yinelenmez.
_KOK_LOGGER_ADI = PROJE_ADI.lower()  # "autolay"

# Handler'ların kaç kez eklendiğini izlemek için bayrak.
# Python'un logging sistemi aynı logger'a birden fazla kez handler
# eklemeye izin verir; bu bayrak bunu engeller.
_yapilandirildi = False


def logger_olustur(isim: str) -> logging.Logger:
    """
    Belirtilen modül adı için yapılandırılmış bir logger döndürür.

    İlk çağrıda AutoLay kök logger'ını yapılandırır (konsol + dosya handler).
    Sonraki çağrılarda mevcut logger'ı olduğu gibi döndürür; handler tekrar
    eklenmez, log satırları çoğalmaz.

    Parametreler:
        isim (str): Logger adı. Genellikle modülün __name__ değeri verilir.
                    Örn: "autolay.core.baglanti"

    Dönüş değeri:
        logging.Logger — Kullanıma hazır logger nesnesi.

    Kullanım:
        log = logger_olustur(__name__)
        log.info("İşlem başladı.")
    """
    global _yapilandirildi

    # Kök logger'ı yalnızca ilk çağrıda yapılandır
    if not _yapilandirildi:
        _kok_logger_yapilandir()
        _yapilandirildi = True

    # İstenen isimle logger al; kök logger'ın alt logger'ı olur
    # ve mesajlar otomatik olarak kök logger'a iletilir (propagation)
    return logging.getLogger(isim)


def _kok_logger_yapilandir():
    """
    AutoLay kök logger'ını konsol ve dosya handler'larıyla yapılandırır.

    Bu fonksiyon yalnızca logger_olustur() tarafından bir kez çağrılır.
    Doğrudan kullanılmamalıdır.
    """
    kok_logger = logging.getLogger(_KOK_LOGGER_ADI)
    kok_logger.setLevel(logging.INFO)

    # --- Konsol handler ---
    # Mesajları stdout'a yazar; terminalde renklendirilmemiş düz metin.
    konsol_handler = logging.StreamHandler(sys.stdout)
    konsol_handler.setLevel(logging.INFO)
    konsol_formatter = logging.Formatter(
        fmt=_KONSOL_FORMATI,
        datefmt=_KONSOL_TARIH_FORMATI,
    )
    konsol_handler.setFormatter(konsol_formatter)

    # --- Dosya handler ---
    # logs/ klasörü yoksa oluştur; eski kayıtları silmeden append modda yazar.
    _LOG_KLASORU.mkdir(parents=True, exist_ok=True)
    dosya_handler = logging.FileHandler(
        filename=_LOG_DOSYASI,
        mode="a",           # Append: mevcut log'ların üzerine yazma
        encoding="utf-8",   # Türkçe karakterler için UTF-8
    )
    dosya_handler.setLevel(logging.DEBUG)  # Dosyaya her şeyi yaz
    dosya_formatter = logging.Formatter(
        fmt=_DOSYA_FORMATI,
        datefmt=_DOSYA_TARIH_FORMATI,
    )
    dosya_handler.setFormatter(dosya_formatter)

    kok_logger.addHandler(konsol_handler)
    kok_logger.addHandler(dosya_handler)

    # Kök logger'ın üst logger'a (Python root logger) iletim yapmasını engelle.
    # Aksi hâlde bazı ortamlarda mesajlar iki kez basılır.
    kok_logger.propagate = False


def seviye_ayarla(seviye: str) -> None:
    """
    Tüm AutoLay logger'larının log seviyesini değiştirir.

    Geliştirme sırasında "debug" vererek tüm ayrıntıları görmek,
    üretimde "warning" vererek sessiz çalışmak için kullanılır.

    Parametreler:
        seviye (str): Hedef seviye adı. Büyük/küçük harf fark etmez.
                      Geçerli değerler: "debug", "info", "warning",
                                        "error", "critical"

    Dönüş değeri:
        None

    Hatalar:
        ValueError — Geçersiz seviye adı verilirse.

    Kullanım:
        from autolay.utils.logger import seviye_ayarla
        seviye_ayarla("debug")   # Tüm detayları göster
        seviye_ayarla("warning") # Sadece uyarı ve üstünü göster
    """
    seviye_haritasi = {
        "debug":    logging.DEBUG,
        "info":     logging.INFO,
        "warning":  logging.WARNING,
        "error":    logging.ERROR,
        "critical": logging.CRITICAL,
    }

    seviye_kucuk = seviye.lower().strip()
    if seviye_kucuk not in seviye_haritasi:
        raise ValueError(
            f"Geçersiz log seviyesi: '{seviye}'. "
            f"Geçerli değerler: {list(seviye_haritasi.keys())}"
        )

    logging_seviyesi = seviye_haritasi[seviye_kucuk]

    # Kök logger ve tüm alt logger'larının seviyesini güncelle
    kok_logger = logging.getLogger(_KOK_LOGGER_ADI)
    kok_logger.setLevel(logging_seviyesi)
    for handler in kok_logger.handlers:
        handler.setLevel(logging_seviyesi)
