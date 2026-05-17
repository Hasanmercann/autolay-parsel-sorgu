import win32com.client
from win32com.client import VARIANT
import pythoncom

# Çalışan AutoCAD oturumuna bağlan
acad = win32com.client.Dispatch("AutoCAD.Application")

# Aktif çizimin model uzayına (ModelSpace) erişim sağla
model_space = acad.ActiveDocument.ModelSpace

# Karenin köşe noktalarını hazırla (60x60, sol alt köşesi 0,0'da)
# AutoCAD COM, koordinatları VARIANT tipinde çift sayı dizisi olarak bekler
nokta1 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (0.0, 0.0, 0.0))
nokta2 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (60.0, 0.0, 0.0))
nokta3 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (60.0, 60.0, 0.0))
nokta4 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (0.0, 60.0, 0.0))

# Karenin dört kenarını çiz
model_space.AddLine(nokta1, nokta2)  # Alt kenar
model_space.AddLine(nokta2, nokta3)  # Sağ kenar
model_space.AddLine(nokta3, nokta4)  # Ust kenar
model_space.AddLine(nokta4, nokta1)  # Sol kenar

# Çizime zoom yap ki kareyi gör
acad.ZoomExtents()

print("60x60 kare cizildi!")