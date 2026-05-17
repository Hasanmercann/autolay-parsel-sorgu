import win32com.client
from win32com.client import VARIANT
import pythoncom

# Çalışan AutoCAD oturumuna bağlan
acad = win32com.client.Dispatch("AutoCAD.Application")

# Aktif çizimin model uzayına (ModelSpace) erişim sağla
model_space = acad.ActiveDocument.ModelSpace

# Dairenin merkez noktası
merkez = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (100.0, 100.0, 0.0))

# Daire çiz: merkez (100, 100), yarıçap 30
model_space.AddCircle(merkez, 30.0)

# Çizime zoom yap ki daireyi gör
acad.ZoomExtents()

print("Merkezi (100, 100), yarıçapı 30 olan daire çizildi!")
