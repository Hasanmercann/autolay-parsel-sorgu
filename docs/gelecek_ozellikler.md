# AutoLay Gelecek Özellikler

Bu dosya AutoLay için planlanan ama henüz yapılmamış özellikleri içerir.
Her özellik versiyonuna göre gruplandırılmıştır.

## v0.2 - Çekme Mesafeleri Geliştirmeleri

- [ ] Kenar bazlı çekme mesafesi (her kenara farklı mesafe)
- [ ] Dar açılı köşede uyarı sistemi
- [ ] En kısa kenar / 2 < çekme kontrolü

## v0.3 - İmar Hesaplamaları

- [ ] MimariVeriler sınıfı (tüm imar verilerini toplayan)
- [ ] TAKS hesabı (taban alanı katsayısı)
- [ ] KAKS hesabı (kat alanı katsayısı / emsal)
- [ ] Maksimum inşaat alanı hesabı
- [ ] Emsal harici alan takibi (çıkma, balkon)

## v0.4 - Çıkma Mesafeleri Modülü

- [ ] Kapalı çıkma hesabı
- [ ] Açık çıkma (balkon) hesabı
- [ ] Yol genişliğine göre izin verilen çıkma
- [ ] Komşu parsele yaklaşma kontrolü
- [ ] Düşey güvenlik (zemin kotundan yükseklik)

## v0.5 - AutoCAD İnteraktif Seçim

- [ ] AutoCAD'de fareyle arsa seçimi (GetEntity)
- [ ] AutoCAD komut satırında soru-cevap (GetReal, GetString)
- [ ] Kenar etiketleme (fareyle tıklayıp ön/yan/arka atama)
- [ ] Çizim üzerinde canlı uyarı gösterimi

## v0.6 - Geometrik Karmaşıklık

- [ ] Yay (arc) destekli arsa sınırları
- [ ] Kavisli kenar offset algoritması
- [ ] Konkav (içbükey) poligon desteği
- [ ] Köşe parsel özel çekme kuralları
- [ ] Straight skeleton algoritması (gelişmiş)

## v0.7 - Mevzuat Motoru

- [ ] Minimum kolon kesiti kontrolü (30x60, 900 cm²)
- [ ] Kolon aks açıklığı kontrolü
- [ ] Merdiven 2h+g kuralı kontrolü
- [ ] Yangın merdiveni genişliği
- [ ] Sığınak alan kontrolü
- [ ] Otopark rampa eğimi kontrolü

## v0.8 - Kullanıcı Arayüzü (GUI)

- [ ] Tkinter veya PyQt ile pencere arayüzü
- [ ] Form tabanlı veri girişi
- [ ] Adım adım sihirbaz (wizard)
- [ ] Anlık önizleme
- [ ] Hata ve uyarı paneli

## v0.9 - Paketleme ve Dağıtım

- [ ] PyInstaller ile .exe dosyası
- [ ] AutoCAD komut tanımlama (.lsp dosyası)
- [ ] Kurulum yönergesi (README)
- [ ] Kullanım kılavuzu
- [ ] Örnek proje dosyaları

## v1.0 - İlk Resmi Sürüm

- [ ] Tam test kapsaması
- [ ] GitHub release
- [ ] Türkiye yönetmelik güncel kontrolü
- [ ] Kullanıcı geri bildirimi sistemi

## v1.1+ - İleri Özellikler

- [ ] TKGM otomatik ada/parsel çekimi
- [ ] Plankote DWG okuma
- [ ] 3D İmar Fanusu
- [ ] Otomatik tefriş (mobilya yerleştirme)
- [ ] Metraj çıkarma
- [ ] Kesit/görünüş üretimi
- [ ] PDF vektör dönüşümü
- [ ] Bilgisayarlı görü (etiketsiz çizim okuma)

## v1.5+ - AI Entegrasyonu (Opsiyonel)

- [ ] Claude/OpenAI API entegrasyonu
- [ ] AI tefriş önerileri (3 seçenek üretimi)
- [ ] AI tasarım kontrolü ("yanlış ne?" sorusu)
- [ ] AI proje özeti yazımı
- [ ] AI doğal dil soru-cevap
- [ ] Kullanıcı API anahtarı yönetimi
- [ ] AI maliyet gösterimi

---
> **Not:** Araştırma dosyaları kullanıcı tarafından doldurulup imarhesap ve cekmecizici v0.2'ye entegre edilecek.
> Bkz: `docs/arastirma/cekme_mesafeleri.md`, `docs/arastirma/taks_kaks.md`

## v2.0+ - Dallanma

- [ ] Elektrik iç tesisat modülü (autolay/elektrik/)
- [ ] Mekanik tesisat modülü
- [ ] Peyzaj modülü
