"""
autolay/config/sabitler.py

AutoLay altyapısına ait genel sabitler.

Bu modül YALNIZCA altyapı düzeyindeki sabitleri içerir:
bağlantı, geometri toleransı, katman isimlendirme kuralları ve
AutoCAD COM arayüzü için gerekli değerler gibi.

Mimari, elektrik, mekanik veya diğer uzmanlık alanlarına özgü
sabitler (kat yüksekliği, duvar kalınlığı, devre tipi vb.)
BURAYA GİRMEZ; ilgili uzmanlık modüllerinde ayrıca tanımlanır.
"""


# ---------------------------------------------------------------------------
# BÖLÜM 1: Proje Metadata
# Projeyi tanımlayan temel kimlik bilgileri.
# ---------------------------------------------------------------------------

# Projenin resmi adı; log mesajlarında ve raporlarda kullanılır
PROJE_ADI = "AutoLay"

# Semantik sürüm numarası (major.minor.patch)
PROJE_VERSIYONU = "0.1.0"


# ---------------------------------------------------------------------------
# BÖLÜM 2: Katman Önekleri
# AutoLay'in otomatik oluşturduğu katmanları kullanıcı katmanlarından
# ayırt etmek için tüm katman adları bu önekle başlar.
# Böylece kullanıcının el ile oluşturduğu katmanlar etkilenmez.
# ---------------------------------------------------------------------------

# Otomatik oluşturulan tüm katman adlarına eklenen önek
# Örnek: "DUVARLAR" → "AUTOLAY_DUVARLAR"
KATMAN_ONEKI = "AUTOLAY_"


# ---------------------------------------------------------------------------
# BÖLÜM 3: Geometri Sabitleri
# Koordinat hesaplamalarında ve şekil doğrulamalarında kullanılan
# eşik değerleri ve sınır koşulları.
# ---------------------------------------------------------------------------

# İki koordinatın "aynı nokta" sayılabilmesi için aralarındaki
# maksimum mesafe (milimetre cinsinden).
# Kayan nokta hatalarının yol açtığı yanlış "farklı nokta" tespitlerini önler.
GEOMETRI_TOLERANSI = 0.001  # mm

# Geçerli bir kapalı poligon oluşturmak için gereken minimum köşe sayısı.
# 3'ten az köşe poligon değil, doğru parçası veya noktadır.
MIN_POLIGON_KOSE_SAYISI = 3


# ---------------------------------------------------------------------------
# BÖLÜM 4: AutoCAD COM Sabitleri
# AutoCAD ile iletişimde tutarlılığı sağlamak için sabit tutulan
# birim ve koordinat varsayılanları.
# ---------------------------------------------------------------------------

# AutoLay'in tüm uzunluk hesaplarını yürüttüğü birim.
# AutoCAD çizim birimi de mm olarak ayarlanmış olmalıdır.
AUTOCAD_BIRIM = "mm"

# 2D çizimde Z ekseninin varsayılan değeri.
# Tüm nokta üretiminde Z verilmediğinde bu değer kullanılır.
VARSAYILAN_Z = 0.0
