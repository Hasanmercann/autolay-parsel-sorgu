"""
autolay/utils/konsol.py

Windows konsolunda Türkçe ve özel karakterlerin doğru görüntülenmesi için
UTF-8 kodlamasını etkinleştiren yardımcı modül.

Sorun: Windows PowerShell ve CMD varsayılan olarak CP1254 (Türkçe Windows)
veya CP850 kodlamasını kullanır. Bu durum Türkçe karakterlerin (ş, ğ, ü, ı vb.)
bozuk görünmesine neden olur.

Çözüm: Hem Python'un stdout akışını hem de Windows konsolunu UTF-8 moduna alır.
"""

import sys
import os


def utf8_aktif_et():
    """
    Windows konsolunda UTF-8 kodlamasını etkinleştirir.

    İki adımda çalışır:
      1. Python'un standart çıktı akışını (stdout) UTF-8'e yeniden yapılandırır.
      2. Windows konsolunu 'chcp 65001' komutuyla UTF-8 kod sayfasına geçirir.

    Windows dışı sistemlerde (Linux, macOS) UTF-8 zaten varsayılan olduğundan
    hiçbir işlem yapılmaz.

    Parametreler:
        Yok

    Dönüş değeri:
        Yok

    Hatalar:
        Fırlatmaz; reconfigure başarısız olursa sessizce geçer.
    """
    if sys.platform != "win32":
        # Linux ve macOS'ta UTF-8 zaten varsayılan, işlem gerekmez
        return

    try:
        # Python'un stdout akışını UTF-8 olarak yeniden yapılandır
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        # Python 3.7'den eski sürümlerde reconfigure yoktur, geç
        pass

    # Windows konsolunu UTF-8 kod sayfasına (65001) geçir
    # Bu komut olmadan chcp 1254 gibi Türkçe Windows sayfaları aktif kalabilir
    os.system("chcp 65001 > nul 2>&1")  # Komut çıktısını gizle (> nul)
