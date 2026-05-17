import win32com.client

# Çalışan AutoCAD oturumuna bağlan
acad = win32com.client.Dispatch("AutoCAD.Application")

# Bağlantıyı doğrula: AutoCAD sürümünü ekrana yazdır
print("AutoCAD'e baglandik!")
print("AutoCAD surumu:", acad.Version)
print("Aktif dosya:", acad.ActiveDocument.Name)