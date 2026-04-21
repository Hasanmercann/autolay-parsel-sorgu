# AutoLay — Claude Code Talimat Dosyası

Bu dosya, Claude Code'un bu projede nasıl davranması gerektiğini tanımlar.
Her yeni seansta bu dosyayı oku ve kurallara uy.

## Dil

- Kullanıcı ile iletişim **Türkçe** kurulur.
- Kod içindeki yorum satırları **Türkçe** yazılır.
- Değişken ve fonksiyon adları İngilizce olabilir, ancak açıklamaları Türkçe olmalıdır.

## Teknik Ortam

- **Python sürümü:** 3.14
- **Temel kütüphane:** pywin32 (COM arayüzü için)
- **Hedef yazılım:** AutoCAD 2026
- **İşletim sistemi:** Windows 11

## AutoCAD Koordinat Formatı

AutoCAD'e koordinat gönderirken MUTLAKA aşağıdaki format kullanılmalıdır:

```python
import pythoncom
import win32com.client

# Doğru format — her zaman bu şekilde kullan:
nokta = win32com.client.VARIANT(
    pythoncom.VT_ARRAY | pythoncom.VT_R8,
    (x, y, z)
)
```

Bu formatın dışına çıkılmamalıdır; aksi takdirde AutoCAD hata verir.

## Onay Kuralları

- Dosya silme, taşıma veya yeniden adlandırma işlemlerinden önce kullanıcıdan onay al.
- Mimari kararlar (yeni modül ekleme, klasör yapısı değişikliği, bağımlılık ekleme) kullanıcıya danışılmadan alınmaz.
- Her görev grubunun sonunda dur ve devam için onay iste.
- Kritik işlemleri (AutoCAD'e yazma, dosya üretimi) gerçekleştirmeden önce kullanıcıya özetle ve onay al.

## Kod Kalitesi

- Her fonksiyon ve modül **kapsamlı Türkçe yorum satırları** içermelidir.
- Fonksiyonun ne yaptığı, parametreleri ve dönüş değeri açıklanmalıdır.
- Karmaşık AutoCAD COM çağrıları satır satır açıklanmalıdır.

## Proje Amacı

Türkiye yapı mevzuatına (TBDY, planlama yönetmelikleri) uygun mimari ruhsat projelerini
Python + AutoCAD otomasyonu ile üretmek.
