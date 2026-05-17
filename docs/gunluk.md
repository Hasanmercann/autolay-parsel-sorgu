# AutoLay Geliştirme Günlüğü

## 18 Nisan 2026

- Python 3.14 kurulumu yapıldı, sanal ortam (venv) oluşturuldu
- pywin32 paketi kurularak AutoCAD COM bağlantısı için altyapı hazırlandı
- AutoCAD 2026 ile Python arasında bağlantı testi gerçekleştirildi (`baglanti_testi.py`)
- İlk çizim denemesi: 60x60 boyutunda kare çizildi (`kare_ciz.py`)
- Daire çizimi denemesi yapıldı, koordinat formatı (VARIANT) öğrenildi (`daire_ciz.py`)
- Proje mimarisi kuruldu: paket klasörleri, `__init__.py` dosyaları ve dokümantasyon oluşturuldu

## 18 Nisan 2026 - Tam Gün Özeti

### Sabah Yapılanlar
- Python 3.14 + pywin32 311 kurulumu
- venv sanal ortam
- UTF-8 karakter desteği (utf8_aktif_et fonksiyonu)
- AutoCAD 2026 ile canlı bağlantı kuruldu
- İlk 60x60 kare ve daire çizildi (eski_denemeler/)

### Öğleden Sonra - Altyapı Kurulumu
- autolay/ paketi profesyonel mimariyle kuruldu (core, drawing, utils, config alt paketleri)
- autolay/core/baglanti.py — AutoCADConnector sınıfı
- autolay/drawing/shapes.py — GeometryDrawer (cizgi, kare, dikdortgen, daire, poligon)
- autolay/drawing/layers.py — LayerManager (katman_olustur, aktif_katman_yap, tum_katmanlar, katman_sil)
- RENK_ADLARI sözlüğü (Türkçe renk isimleri → ACI değerleri)
- autolay/utils/konsol.py — utf8_aktif_et
- Dokümantasyon: README.md, CLAUDE.md, docs/gunluk.md

### Akşam - Altyapı Tamamlama
- autolay/core/hatalar.py — 11 özel hata sınıfı (AutoLayError, BaglantiHatasi, GeometriHatasi, KatmanHatasi ve alt sınıfları)
- autolay/config/sabitler.py — tarafsız altyapı sabitleri (KATMAN_ONEKI, GEOMETRI_TOLERANSI, MIN_POLIGON_KOSE_SAYISI, VARSAYILAN_Z)
- autolay/utils/logger.py — merkezi loglama (konsol + logs/autolay.log)
- autolay/utils/input_yoneticisi.py — InputManager (sayi_al, koordinat_al, evet_hayir)
- Entegrasyon: Tüm mevcut sınıflar yeni hata sınıflarına, sabitlere, logger'a geçirildi
- baglanti.py'ye fail-fast eklendi: aktif çizim yoksa başta hata verir

### Test Dosyaları (hepsi başarılı)
- tests/test_baglanti.py
- tests/test_geometry.py (5 şekil çizildi)
- tests/test_layers.py (3 katman, renkli)
- tests/test_input_yoneticisi.py (canlı terminal → AutoCAD etkileşimi)

### Öğrenilen Kavramlar
- Sınıf, nesne, self, __init__, docstring
- try/except, raise, return, f-string
- Dependency Injection (AutoCADConnector üzerinden)
- DRY prensibi, idempotent davranış
- Paket/modül yapısı, PEP 8
- Exception hiyerarşisi
- Python logging modülü
- Sabit dosyalar ve config yönetimi
- Fail fast prensibi
- Regression testing
- isinstance, tuple unpacking, for + range

### Sonraki Seans İçin Kritik Bilgi
- Altyapı %90 bitti. KALAN: autolay/utils/geometri.py (GeometryUtils sınıfı)
- GeometryUtils içeriği:
  - iki_nokta_arasi_mesafe
  - poligon_alani (shoelace formülü)
  - poligon_merkezi (centroid)
  - nokta_poligon_icinde_mi
  - poligon_offset (içeri/dışarı daraltma — çekme mesafesi için KRİTİK)
- GeometryUtils bittikten sonra: autolay/mimari/ klasörü açılacak, ilk modül ArsaCizici olacak.

### Önemli Proje Kararları
- Altyapı tarafsız kalacak (mimari, elektrik, mekanik alanlarına özel şeyler altyapıya girmeyecek)
- Gelecekte aynı altyapı hem mimari ruhsat hem elektrik iç tesisat projesi için kullanılabilir olacak
- Mimari sabitler autolay/mimari/ klasöründe tanımlanacak (ileride)

## 18 Nisan 2026 - Tüm Gün

**Yapılan Sınıflar:**
- autolay/core/baglanti.py (AutoCADConnector)
- autolay/core/hatalar.py (11 hata sınıfı)
- autolay/drawing/shapes.py (GeometryDrawer)
- autolay/drawing/layers.py (LayerManager, RENK_ADLARI)
- autolay/config/sabitler.py (tarafsız altyapı sabitleri)
- autolay/utils/konsol.py (utf8_aktif_et)
- autolay/utils/logger.py (merkezi loglama)
- autolay/utils/input_yoneticisi.py (InputManager)

**Yapılan Testler (hepsi başarılı):**
- test_baglanti.py, test_geometry.py, test_layers.py, test_input_yoneticisi.py

**Entegrasyonlar:**
- Tüm sınıflar yeni hata sınıflarına geçirildi
- shapes.py config sabitlerini kullanıyor
- baglanti.py logger ve fail-fast eklendi

**Sonraki Adım:** autolay/utils/geometri.py (GeometryUtils) — mesafe, alan, poligon offset, merkez, nokta içinde mi.

**Sonra:** autolay/mimari/ klasörü ile ArsaCizici.

## 18 Nisan 2026 - Gece - Git & GitHub Kurulumu

- Git bilgisayara kuruldu (zaten varmış, 2.53.0)
- GitHub hesabı açıldı: elifecemercan
- Proje klasörü Git deposuna dönüştürüldü (git init)
- .gitignore dosyası oluşturuldu (venv, pycache, logs, .vscode dışta)
- İlk commit: "İlk sürüm: AutoLay altyapısı tamamlandı" (41 dosya, 2384 satır)
- Temizlik commit: pycache ve log dosyaları Git takibinden çıkarıldı
- GitHub'da depo oluşturuldu (private): https://github.com/elifecemercan/autolay
- Tüm kod GitHub'a yüklendi (git push)

### Sonraki Seans Kullanımı
- Her seans sonu: git add . && git commit -m "..." && git push
- Yeni bilgisayardan çalışmak için: git clone https://github.com/elifecemercan/autolay
- Yerel yedek: C:\Projeler\Autolay_Yedek_18Nisan (manuel kopya)

## 18 Nisan 2026 - Gece - GeometryUtils Tamamlandı

- autolay/utils/geometri.py — GeometryUtils sınıfı yazıldı
- 5 metot: mesafe, poligon_alani (Shoelace), poligon_merkezi, nokta_poligon_icinde_mi (Ray Casting), poligon_offset (köşe açıortay yöntemi)
- poligon_offset'te CW/CCW yön tespiti eklendi: pozitif mesafe her zaman içeri, negatif her zaman dışarı
- tests/test_geometri.py — 10/10 test başarılı
- ALTYAPI %100 TAMAMLANDI

### Yarın Başlanacak
- autolay/mimari/ klasörü açılacak
- İlk modül: ArsaCizici (autolay/mimari/arsa.py)
- ArsaCizici, AutoCADConnector + GeometryDrawer + LayerManager + GeometryUtils'i birleştirip kullanacak
- Kullanıcıdan köşe koordinatları alacak, AUTOLAY_ARSA katmanında poligon çizecek, alan hesaplayacak

## 20 Nisan 2026

### Yapılanlar
- autolay/mimari/veriler.py — MimariVeriler sınıfı (213 satır)
  - Merkezi veri taşıyıcı: arsa_koseleri, yapi_nizami, kat_sayisi, on_kenar_indeks, park_komsusu_kenarlar, bitisik_kenarlar, imar_durumu, bina_yuksekligi_m
  - 8 adım validation
  - cekme_baslangic_mesafeleri() metodu (ön/yan/arka/bitişik mantığı)
  - ozet() metodu (log için)
- CekmeCizici.verilerden_hesapla(veri) entegrasyonu
  - MimariVeriler'den otomatik okuma
  - Nizam kontrolü → bitisik_nizam_ayarla veya tum_kenarlar_ayarla
  - Kademeli çekme otomatik (kat > 4)
  - Yüksek yapı uyarısı otomatik (bina_yuksekligi >= 60.50m)
- kademeli_cekme_hesapla metoduna bitisik_kenarlar parametresi eklendi (bug fix)

### Testler (18 test geçti)
- tests/test_veriler.py — 13 validation ve mantık testi
- tests/test_cekme.py'ye test_verilerden_hesapla eklendi — 5 entegrasyon testi

### Bug Fix
- Bitişik kenara kademeli ekleme yapılıyordu (0 olması gerekirken 1.5m çıkıyordu)
- kademeli_cekme_hesapla artık bitisik_kenarlar'ı da atlıyor

### Sonraki Adım (21 Nisan)
- İmarHesap sınıfı (autolay/mimari/imar_hesap.py)
  - TAKS hesabı (taban alanı katsayısı)
  - KAKS/Emsal hesabı (kat alanı katsayısı)
  - Maksimum inşaat alanı
  - Emsal harici alan takibi (balkon, çıkma, çatı arası)
- MimariVeriler'e taks, kaks, emsal_harici gibi alanlar eklenecek
