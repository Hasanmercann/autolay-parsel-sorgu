# AutoLay

AutoCAD'e bağlanarak TKGM'den otomatik parsel koordinatı çeken ve çizim yapan Python aracı.

## Ne Yapar?

1. TKGM CBS API'sinden il/ilçe/mahalle/ada/parsel bilgisiyle arsa koordinatlarını çeker
2. AutoCAD'de `TKGM-ARSA` katmanına kapalı LWPolyline olarak çizer
3. Tkinter arayüzüyle dropdown'dan il/ilçe/mahalle seçimi, ada/parsel klavyeyle girilir

## Gereksinimler

- Python 3.10+
- AutoCAD 2026 (açık ve bir .dwg belgesiyle)
- Windows

## Kurulum

```bash
git clone https://github.com/Hasanmercann/autolay.git
cd autolay
python -m venv venv
venv\Scripts\activate
pip install pywin32 requests playwright
playwright install chromium
```

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

### Yeni il eklemek

Önbellekte olmayan iller için Playwright ile bir kez çalıştırılır:

```bash
python autolay/tkgm/id_olustur.py ANKARA
python autolay/tkgm/id_olustur.py ISTANBUL

# Tüm Türkiye (~3-5 saat):
python autolay/tkgm/id_olustur_tumtur.py
python autolay/tkgm/id_olustur_tumtur.py --eksik   # sadece eksikler
```

## Klasör Yapısı

```
autolay/
├── core/        — AutoCAD COM bağlantısı ve hata sınıfları
├── cizim/       — AutoCAD çizim araçları (GeometryDrawer, LayerManager)
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

## Testler

```bash
python tests/test_tkgm.py           # TKGM API testi (internet gerekli)
python tests/test_tkgm_autocad.py   # AutoCAD entegrasyon testi
python tests/test_geometri.py       # Geometri hesapları
```
