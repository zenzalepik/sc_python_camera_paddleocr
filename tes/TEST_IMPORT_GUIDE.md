# 🧪 Test Import Guide

Panduan untuk test import dan verifikasi widget ObjectDistanceWidget.

---

## 📋 Pre-requisites

Pastikan Python 3.8+ sudah terinstall dengan dependencies:

```bash
pip install ultralytics opencv-python Pillow numpy
```

---

## 🚀 Step-by-Step Test

### Step 1: Test Import Sederhana

Jalankan script test import:

```bash
python test_import.py
```

**Expected Output:**
```
============================================================
Test Import Object Distance Widget
============================================================

[1/3] Importing widget package...
      ✅ Success importing ObjectDistanceWidget
[2/3] Checking widget attributes...
      ✅ ObjectDistanceWidget class exists
      ✅ Has 'start' method: True
      ✅ Has 'stop' method: True
      ✅ Has 'toggle_yolo' method: True
[3/3] Importing configuration...
      ✅ CLEAN_UI: False
      ✅ CAMERA_WIDTH: 640
      ✅ CAMERA_HEIGHT: 480
      ✅ TARGET_CLASSES: [0, 67, 1, 2, 3, 5, 7]

============================================================
✅ SEMUA TEST BERHASIL!
============================================================
```

### Step 2: Test Run Aplikasi Parent

Jalankan aplikasi parent:

```bash
python welcome_app.py
```

atau gunakan batch file (Windows):

```bash
run.bat
```

**Expected Behavior:**
1. Window aplikasi terbuka dengan judul "Selamat Datang - Object Distance Detection System"
2. Panel informasi muncul di sebelah kiri
3. Welcome message muncul di panel kanan
4. Tombol START aktif (enabled)

### Step 3: Test Widget Functionality

1. **Klik START**
   - Widget akan diinisialisasi
   - Camera feed muncul di panel kanan
   - Status berubah menjadi "Running"

2. **Test Toggle YOLO**
   - Klik tombol "Toggle YOLO"
   - Status berubah antara "YOLO ON" dan "YOLO OFF"

3. **Test Reset Tracking**
   - Klik tombol "Reset Tracking"
   - Tracking akan direset

4. **Klik STOP**
   - Widget berhenti
   - Status berubah menjadi "Stopped"

---

## 🔍 Troubleshooting

### Error: ModuleNotFoundError

**Problem:**
```
ModuleNotFoundError: No module named 'object_distance_widget'
```

**Solution:**
Pastikan path widget benar. Script akan otomatis menambahkan path:
```python
widget_path = os.path.join(os.path.dirname(__file__), '..', 'v6_Deteksi_Object_Mendekat', 'export_to_widget')
sys.path.insert(0, widget_path)
```

Atau install widget sebagai package:
```bash
cd ../v6_Deteksi_Object_Mendekat/export_to_widget
pip install -e .
```

### Error: No module named 'ultralytics'

**Problem:**
```
ModuleNotFoundError: No module named 'ultralytics'
```

**Solution:**
```bash
pip install ultralytics
```

### Error: No module named 'cv2'

**Problem:**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solution:**
```bash
pip install opencv-python
```

### Error: No module named 'PIL'

**Problem:**
```
ModuleNotFoundError: No module named 'PIL'
```

**Solution:**
```bash
pip install Pillow
```

### Camera tidak terbuka

**Problem:**
```
[ERROR] Cannot open camera 0
```

**Solution:**
1. Pastikan kamera terhubung
2. Coba camera ID lain:
   ```python
   widget = ObjectDistanceWidget(root, camera_id=1)  # atau 2, 3
   ```
3. Tutup aplikasi lain yang menggunakan kamera

### Widget tidak muncul

**Problem:**
Widget tidak terlihat di parent frame

**Solution:**
Pastikan parent frame sudah di-manage dengan pack/place/grid:
```python
frame.pack(fill=tk.BOTH, expand=True)  # atau place/grid
widget.pack(fill=tk.BOTH, expand=True)
```

---

## ✅ Verification Checklist

Gunakan checklist ini untuk memverifikasi widget berhasil diintegrasikan:

- [ ] Import widget berhasil tanpa error
- [ ] Class `ObjectDistanceWidget` tersedia
- [ ] Method `start()` tersedia
- [ ] Method `stop()` tersedia
- [ ] Method `toggle_yolo()` tersedia
- [ ] Method `reset_tracking()` tersedia
- [ ] Configuration variables dapat diakses
- [ ] Widget dapat di-pack di parent frame
- [ ] Widget dapat di-start tanpa error
- [ ] Camera feed muncul di widget
- [ ] Detection berjalan (bounding box muncul saat object terdeteksi)
- [ ] SIAGA alert berfungsi (saat object mendekat)
- [ ] Tombol kontrol berfungsi (START/STOP/Toggle YOLO/Reset)
- [ ] Keyboard shortcuts berfungsi (Y, R, L, T, Q)
- [ ] Widget dapat di-stop tanpa error
- [ ] Parking session capture berfungsi (opsional)

---

## 📝 Test Script Template

Gunakan template ini untuk test widget di project Anda:

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

def test_widget():
    """Test widget functionality."""
    root = tk.Tk()
    root.title("Widget Test")
    root.geometry("800x600")
    
    # Create widget
    widget = ObjectDistanceWidget(root, camera_id=0)
    widget.pack(fill=tk.BOTH, expand=True)
    
    # Test start
    print("Starting widget...")
    widget.start()
    
    # Test toggle yolo
    print("Toggling YOLO...")
    widget.toggle_yolo()
    
    # Test reset
    print("Resetting tracking...")
    widget.reset_tracking()
    
    # Schedule stop after 5 seconds
    def stop_test():
        print("Stopping widget...")
        widget.stop()
        root.quit()
    
    root.after(5000, stop_test)
    root.mainloop()
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_widget()
```

---

## 📚 Additional Resources

- Widget Documentation: `../v6_Deteksi_Object_Mendekat/export_to_widget/object_distance_widget/README.md`
- Parent App Documentation: `README_PARENT_APP.md`
- Original Project: `../v6_Deteksi_Object_Mendekat/export_to_widget/README.md`

---

**Last Updated:** 2026-03-13  
**Version:** 1.0.0
