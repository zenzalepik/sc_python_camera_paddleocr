# 👋 Selamat Datang - Parent Application Demo

**Demo aplikasi parent yang mengimport Object Distance Widget**

Folder ini berisi contoh aplikasi parent yang menggunakan widget `ObjectDistanceWidget` yang reusable.

---

## 📁 Struktur Folder

```
tes/
├── welcome_app.py          # Aplikasi parent utama
├── requirements.txt        # Dependencies
└── README_PARENT_APP.md    # Dokumentasi ini
```

Widget location:
```
../v6_Deteksi_Object_Mendekat/export_to_widget/object_distance_widget/
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Aplikasi

```bash
python welcome_app.py
```

### 3. Gunakan Aplikasi

1. Klik tombol **START** untuk memulai deteksi
2. Widget akan menampilkan camera feed dengan object detection
3. Gunakan tombol kontrol untuk:
   - **STOP** - Menghentikan deteksi
   - **Toggle YOLO** - Menyalakan/mematikan YOLO
   - **Reset Tracking** - Reset tracking object

---

## ⌨️ Keyboard Shortcuts

| Tombol | Fungsi |
|--------|--------|
| `Q` | Quit aplikasi |
| `Y` | Toggle YOLO (saat widget aktif) |
| `R` | Reset tracking (saat widget aktif) |
| `L` | Trigger Loop Detector (saat widget aktif) |
| `T` | Trigger Tap Card (saat widget aktif) |

---

## 🎯 Fitur Aplikasi Parent

### 1. Welcome Screen

Aplikasi menampilkan welcome screen dengan:
- Header dengan judul aplikasi
- Panel informasi tentang fitur
- Widget container untuk object detection
- Footer dengan status aplikasi

### 2. Control Panel

Panel kontrol di sebelah kiri dengan:
- Informasi fitur dan cara penggunaan
- Tombol START/STOP
- Tombol Toggle YOLO
- Tombol Reset Tracking

### 3. Widget Integration

Widget `ObjectDistanceWidget` dipasang di frame parent:
- Flexible dan dapat disesuaikan ukurannya
- Auto-resize mengikuti parent frame
- Thread-safe execution

---

## 💡 Cara Mengintegrasikan Widget ke Project Anda

### Step 1: Copy Widget Package

Copy folder `object_distance_widget` ke project Anda:

```
your_project/
├── object_distance_widget/    # Copy dari v6_Deteksi_Object_Mendekat/export_to_widget/
│   ├── __init__.py
│   ├── widget_core.py
│   ├── widget_variables.py
│   └── README.md
├── main.py
└── requirements.txt
```

### Step 2: Install Dependencies

```bash
pip install ultralytics opencv-python Pillow numpy
```

### Step 3: Import dan Gunakan Widget

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()
root.title("My App")

# Create widget
widget = ObjectDistanceWidget(root, camera_id=0)
widget.pack(fill=tk.BOTH, expand=True)

# Start detection
widget.start()

root.mainloop()
```

### Step 4: Customize (Optional)

Edit file `widget_variables.py` untuk mengubah pengaturan:

```python
# Ubah resolusi camera
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Ubah target classes
TARGET_CLASSES = [0]  # Hanya track person

# Enable CLEAN_UI mode
CLEAN_UI = True
```

---

## 🎨 Contoh Penggunaan Lain

### 1. Widget di Frame Custom

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()

# Create custom frame
my_frame = tk.Frame(root, bg='white', width=800, height=600)
my_frame.pack()

# Add widget to custom frame
widget = ObjectDistanceWidget(my_frame)
widget.pack(fill=tk.BOTH, expand=True)

widget.start()
root.mainloop()
```

### 2. Multiple Widgets (Multiple Cameras)

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()
root.title("Multi-Camera System")

# Camera 1
widget1 = ObjectDistanceWidget(root, camera_id=0)
widget1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Camera 2
widget2 = ObjectDistanceWidget(root, camera_id=1)
widget2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

widget1.start()
widget2.start()
root.mainloop()
```

### 3. Widget dengan Callback

```python
import tkinter as tk
from tkinter import messagebox
from object_distance_widget import ObjectDistanceWidget

def on_session_complete(session):
    """Callback saat parking session selesai."""
    messagebox.showinfo(
        "Session Complete",
        f"Session {session.session_id} selesai!\n"
        f"Vehicle: {session.vehicle_id}"
    )

root = tk.Tk()

widget = ObjectDistanceWidget(
    root,
    camera_id=0,
    on_session_complete=on_session_complete
)
widget.pack(fill=tk.BOTH, expand=True)

widget.start()
root.mainloop()
```

---

## 🔧 Troubleshooting

### Widget tidak muncul

Pastikan parent frame sudah di-pack/place/grid:

```python
frame.pack(fill=tk.BOTH, expand=True)  # atau place/grid
widget.pack(fill=tk.BOTH, expand=True)
```

### Camera tidak terdeteksi

```python
# Coba camera ID lain
widget = ObjectDistanceWidget(root, camera_id=1)  # atau 2, 3, dst
```

### Import error

Pastikan path widget sudah benar:

```python
import sys
import os

# Add widget path
widget_path = os.path.join(os.path.dirname(__file__), '..', 'v6_Deteksi_Object_Mendekat', 'export_to_widget')
sys.path.insert(0, widget_path)

from object_distance_widget import ObjectDistanceWidget
```

### YOLO model tidak ditemukan

Model akan didownload otomatis saat pertama kali run. Pastikan koneksi internet tersedia.

---

## 📝 Notes

1. **Widget Reusability**: Widget ini 100% reusable dan dapat dipasang di frame apapun
2. **No Feature Changes**: Semua fitur dan tampilan widget tetap sama dengan aslinya
3. **Thread-Safe**: Widget berjalan di thread terpisah untuk performa optimal
4. **Flexible**: Dapat disesuaikan dengan berbagai ukuran dan konfigurasi

---

## 📊 System Requirements

- **Python**: 3.8+
- **Camera**: Webcam atau USB camera
- **RAM**: Minimal 4GB (8GB recommended)
- **Storage**: ~100MB untuk model YOLO
- **GPU**: Optional (CUDA untuk percepatan)

---

## 🙏 Credits

- **Original Project**: `v6_Deteksi_Object_Mendekat`
- **Widget Implementation**: Reusable Tkinter widget
- **YOLO**: Ultralytics YOLOv8

---

## 📄 License

Apache License 2.0

---

**Created:** 2026-03-13  
**Version:** 1.0.0  
**Folder:** tes
