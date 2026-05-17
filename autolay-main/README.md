
# AutoLay

AutoLay, AutoCAD'e bağlanarak TKGM CBS API'sinden otomatik parsel koordinatı çeken ve çizim yapan modern bir Python uygulamasıdır. İmar hesapları, çekme mesafeleri ve mimari analizler için güçlü bir altyapı sunar.

---

## Proje Özellikleri

- **TKGM CBS API** ile il/ilçe/mahalle/ada/parsel bilgisinden arsa koordinatlarını çeker
- **AutoCAD 2026** ile doğrudan bağlantı kurar, parseli LWPolyline olarak çizer
- **Kapsamlı GUI**: Tkinter tabanlı kullanıcı dostu arayüz
- **İmar Hesapları**: TAKS/KAKS, çekme mesafeleri, emsal harici alanlar
- **Modüler Mimari**: Kolayca geliştirilebilir ve test edilebilir yapı

---

## Tanıtım Görselleri

### 1. Başlangıç Ekranı
![Başlangıç Ekranı](docs/tanitim/1.PNG)
Kullanıcı, uygulamanın ana ekranında temel seçenekleri görebilir.

### 2. Parsel Seçimi
![Parsel Seçimi](docs/tanitim/2.PNG)
Parsel seçimi yapılarak işleme başlanır.

### 3. Parametre Girişi
![Parametre Girişi](docs/tanitim/3.PNG)
Gerekli parametreler kullanıcı tarafından girilir.

### 4. Sonuçların Görüntülenmesi
![Sonuçların Görüntülenmesi](docs/tanitim/4.PNG)
Hesaplama sonrası sonuçlar ekranda gösterilir.

### 5. Çizim ve Rapor
![Çizim ve Rapor](docs/tanitim/5.PNG)
Oluşturulan çizim ve raporlar kullanıcıya sunulur.

---

## Gereksinimler

- Python 3.10+
- AutoCAD 2026
- Windows

---

## Kurulum

```bash
git clone https://github.com/Hasanmercann/autolay.git
cd autolay
python -m venv venv
venv\Scripts\activate
pip install pywin32 requests playwright
playwright install chromium
```

---

## Kullanım

```bash
# GUI ile çalıştır (Ana kullanım)
python -m autolay
```
AutoCAD açık olmalı. Pencerede il/ilçe/mahalle seçip ada ve parsel numarasını girin, parsel AutoCAD'e çizilir.

### Sadece TKGM sorgusu (AutoCAD gerekmez)

```python
from autolay.tkgm import TKGMOkuyucu
ok = TKGMOkuyucu()
sonuc = ok.parsel_sorgula("KONYA", "ILGIN", "TEKELER", "175", "1")
print(sonuc.koseler)   # [(x1,y1), ...] rölatif metre
print(sonuc.alan_m2)   # 41747.0
```

---

## Klasör Yapısı

```
autolay/
├── core/        — AutoCAD bağlantısı ve hata sınıfları
├── cizim/       — Çizim araçları (GeometryDrawer, LayerManager)
├── tkgm/        — TKGM parsel sorgu ve çizim paketi
│   ├── okuyucu.py         TKGM CBS API istemcisi
│   ├── cizici.py          AutoCAD'e çizim
│   ├── idler.json         il/ilçe/mahalle ID önbelleği
│   ├── id_olustur.py      tek il için önbellek oluşturucu
│   └── id_olustur_tumtur.py  81 il için önbellek oluşturucu
├── gui/         — Tkinter parsel giriş penceresi
├── mimari/      — İmar hesapları (çekme mesafeleri, TAKS/KAKS)
├── utils/       — Logger, konsol, geometri yardımcıları
└── config/      — Sabitler
tests/           — Test dosyaları
```

---

## Kodun Temel Bileşenleri

### AutoCAD Bağlantısı (core/baglanti.py)
- `AutoCADConnector`: AutoCAD ile COM tabanlı bağlantı kurar, aktif çizim ve model uzayına erişim sağlar.

### Katman Yönetimi (cizim/layers.py)
- `LayerManager`: Katman oluşturma, silme, aktif yapma ve renk atama işlemlerini yönetir.

### Geometrik Çizim (cizim/shapes.py)
- `GeometryDrawer`: Çizgi, kare, dikdörtgen, daire ve poligon gibi temel şekilleri çizer.

### TKGM Parsel Sorgu (tkgm/okuyucu.py)
- `TKGMOkuyucu`: TKGM CBS API'sinden parsel köşe koordinatlarını çeker.

### İmar Hesapları (mimari/imar_hesap.py)
- `ImarHesap`: TAKS, KAKS, emsal harici alan ve mimari kontrolleri yapar, rapor ve uyarı üretir.

---

## Testler

```bash
python tests/test_tkgm.py           # TKGM API testi (internet gerekli)
python tests/test_tkgm_autocad.py   # AutoCAD entegrasyon testi
python tests/test_geometri.py       # Geometri hesapları
```

---

## Geliştirme Günlüğü ve Yol Haritası

- Güncel gelişmeler ve planlanan özellikler için:
	- `docs/gunluk.md` — Geliştirme günlüğü
	- `docs/gelecek_ozellikler.md` — Yol haritası ve planlanan modüller

---

## Katkı ve Lisans

Her türlü katkıya açıktır. Kodunuzu forkladıktan sonra PR gönderebilirsiniz. Lisans bilgisi için projenin kök dizinindeki LICENSE dosyasına bakınız.

---

<div align="center">
<b>AutoLay ile mimari çizim ve imar analizlerini kolaylaştırın!</b>
</div>
