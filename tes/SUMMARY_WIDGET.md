# 📦 Widget Reusable - Summary Documentation

**Object Distance Detection Widget - Reusable Package**

Dokumentasi ini merangkum pembuatan widget reusable dari aplikasi `v6_Deteksi_Object_Mendekat\export_to_widget`.

---

## 🎯 Tujuan

Membuat widget yang:
- ✅ **Reusable** - Dapat di-copy paste ke project apapun
- ✅ **Flexible** - Dapat dipasang di frame apapun
- ✅ **No Changes** - Tidak mengubah fitur dan tampilan asli
- ✅ **Easy to Use** - Tinggal panggil untuk menggunakan

---

## 📁 Struktur File Yang Dibuat

### 1. Widget Package
**Location:** `v6_Deteksi_Object_Mendekat\export_to_widget\object_distance_widget\`

```
object_distance_widget/
├── __init__.py              # Package initialization & exports
├── widget_core.py           # Core widget implementation
├── widget_variables.py      # Configuration variables
└── README.md                # Widget documentation
```

### 2. Parent Application (Demo)
**Location:** `tes\`

```
tes/
├── welcome_app.py           # Parent application utama
├── requirements.txt         # Dependencies
├── run.bat                  # Batch file untuk run (Windows)
├── test_import.py           # Script test import
├── README_PARENT_APP.md     # Parent app documentation
├── TEST_IMPORT_GUIDE.md     # Test import guide
└── SUMMARY_WIDGET.md        # This file
```

---

## 🚀 Cara Menggunakan Widget

### Quick Start

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

# Create main window
root = tk.Tk()
root.title("My Application")

# Create widget dan pasang di frame
widget = ObjectDistanceWidget(root, camera_id=0)
widget.pack(fill=tk.BOTH, expand=True)

# Start detection
widget.start()

# Run main loop
root.mainloop()
```

### Copy Widget ke Project Baru

1. **Copy folder widget:**
   ```
   Copy: v6_Deteksi_Object_Mendekat\export_to_widget\object_distance_widget\
   To:   your_project/object_distance_widget/
   ```

2. **Install dependencies:**
   ```bash
   pip install ultralytics opencv-python Pillow numpy
   ```

3. **Import dan gunakan:**
   ```python
   from object_distance_widget import ObjectDistanceWidget
   ```

---

## 📖 Widget API

### Class: ObjectDistanceWidget

Widget Tkinter untuk object distance detection.

#### Constructor Parameters

```python
ObjectDistanceWidget(
    parent,                  # Parent frame/container
    camera_id=0,            # Camera device ID
    confidence_threshold=0.5,  # YOLO confidence threshold
    on_session_complete=None,  # Callback saat session selesai
    **kwargs                # Additional tkinter.Frame options
)
```

#### Public Methods

| Method | Description |
|--------|-------------|
| `start()` | Start object detection |
| `stop()` | Stop object detection |
| `toggle_yolo()` | Toggle YOLO on/off |
| `reset_tracking()` | Reset object tracking |
| `trigger_loop_detector()` | Trigger loop detector (FASE 3) |
| `trigger_tap_card()` | Trigger tap card (FASE 4) |
| `get_parking_session()` | Get current parking session |
| `is_yolo_enabled()` | Check if YOLO is enabled |

---

## ⚙️ Configuration

Edit file `widget_variables.py` untuk mengubah pengaturan:

```python
# Camera Resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# YOLO Settings
YOLO_CONFIDENCE_THRESHOLD = 0.5
TARGET_CLASSES = [0, 67, 1, 2, 3, 5, 7]

# Tracker Settings
SIAGA_FRAME_THRESHOLD = 3
SIAGA_HOLD_TIME = 3.0

# Parking System
FASE1_TARGET = 3
FASE2_TARGET = 5
FASE3_TARGET = 3
FASE4_TARGET = 3

# UI Settings
CLEAN_UI = False
WINDOW_SCALE = 2.0
```

---

## 🎨 Contoh Penggunaan

### 1. Widget di Frame Custom

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()

# Create custom frame
my_frame = tk.Frame(root, bg='white', width=800, height=600)
my_frame.pack()

# Add widget
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
    messagebox.showinfo(
        "Session Complete",
        f"Session {session.session_id} selesai!"
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

### 4. Widget dengan Control Buttons

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()
root.title("Object Detection with Controls")

# Control frame
control_frame = tk.Frame(root)
control_frame.pack(fill=tk.X, padx=10, pady=5)

# Widget
widget = ObjectDistanceWidget(root, camera_id=0)
widget.pack(fill=tk.BOTH, expand=True)

# Control buttons
def on_start():
    widget.start()

def on_stop():
    widget.stop()

def on_toggle():
    widget.toggle_yolo()

def on_reset():
    widget.reset_tracking()

tk.Button(control_frame, text="Start", command=on_start).pack(side=tk.LEFT)
tk.Button(control_frame, text="Stop", command=on_stop).pack(side=tk.LEFT)
tk.Button(control_frame, text="Toggle YOLO", command=on_toggle).pack(side=tk.LEFT)
tk.Button(control_frame, text="Reset", command=on_reset).pack(side=tk.LEFT)

widget.start()
root.mainloop()
```

---

## 🅿️ Parking System

Widget include parking system dengan 4 fase:

### Fase 1: SIAGA (3 frame)
- Trigger: Object terdeteksi mendekat
- Capture: 3 frame otomatis

### Fase 2: TETAP (5 frame)
- Trigger: Object berhenti (status stable)
- Capture: 5 frame otomatis

### Fase 3: LOOP (3 frame)
- Trigger: Tombol loop detector ditekan / method `trigger_loop_detector()`
- Capture: 3 frame

### Fase 4: TAP (3 frame)
- Trigger: Tombol tap card ditekan / method `trigger_tap_card()`
- Capture: 3 frame

### Access Parking Session

```python
session = widget.get_parking_session()

if session.is_active:
    print(f"Session ID: {session.session_id}")
    print(f"Vehicle: {session.vehicle_id}")
    print(f"Phase: {session.phase}")
    print(f"Progress: {session.get_progress()}")
```

---

## 🔧 Integration Checklist

### Untuk Membuat Widget Reusable

- [x] Extract core logic ke `widget_core.py`
- [x] Create configuration file `widget_variables.py`
- [x] Create package `__init__.py` dengan exports
- [x] Widget extends `tk.Frame` untuk flexibility
- [x] Support custom parent frame
- [x] Support callback functions
- [x] Thread-safe execution
- [x] Auto-resize mengikuti parent
- [x] No hardcoded paths
- [x] Complete documentation

### Untuk Menggunakan Widget di Project Baru

- [ ] Copy folder `object_distance_widget` ke project
- [ ] Install dependencies (`ultralytics`, `opencv-python`, `Pillow`, `numpy`)
- [ ] Import widget: `from object_distance_widget import ObjectDistanceWidget`
- [ ] Create widget dengan parent frame
- [ ] Pack/place/grid widget
- [ ] Start detection dengan `widget.start()`

---

## 📊 Features Preserved

Semua fitur dari aplikasi asli dipertahankan 100%:

### Detection Features
- ✅ Real-time object detection dengan YOLOv8
- ✅ Multi-class tracking (person, car, motorcycle, etc.)
- ✅ Distance estimation (mendekat/menjauh/tetap)
- ✅ Object tracking dengan ID unik

### SIAGA System
- ✅ SIAGA alert setelah 3 frame mendekat
- ✅ SIAGA hold timer 3 detik
- ✅ SIAGA persistence mode
- ✅ SIAGA cleared notification

### Parking System
- ✅ 4 fase parking capture
- ✅ Auto capture FASE 1 (SIAGA)
- ✅ Auto capture FASE 2 (TETAP)
- ✅ Manual trigger FASE 3 (LOOP)
- ✅ Manual trigger FASE 4 (TAP)
- ✅ Session management
- ✅ Metadata saving

### UI Features
- ✅ Bounding box dengan warna sesuai status
- ✅ Object ID label
- ✅ Status indicator
- ✅ FPS counter
- ✅ Legend
- ✅ Timestamp
- ✅ Control buttons (L - LOOP, T - TAP)
- ✅ CLEAN_UI mode
- ✅ YOLO toggle indicator

### Optimization
- ✅ Frame skipping support
- ✅ Camera resolution configuration
- ✅ Confidence threshold adjustment
- ✅ Thread-safe execution

---

## 🎯 Differences from Original

Perbedaan dari aplikasi asli:

### 1. Integration Method
- **Original:** Standalone application (`main.py`)
- **Widget:** Reusable Tkinter component

### 2. Window Management
- **Original:** Creates own OpenCV window
- **Widget:** Embeds in Tkinter frame (video displayed via PIL/ImageTk)

### 3. Event Loop
- **Original:** OpenCV `cv2.waitKey()` loop
- **Widget:** Tkinter `mainloop()` dengan threading

### 4. Configuration
- **Original:** `variables.py` (shared)
- **Widget:** `widget_variables.py` (self-contained)

### 5. Entry Point
- **Original:** `python main.py`
- **Widget:** Import dan instantiate class

---

## 📝 Testing

### Test Import

```bash
cd tes
python test_import.py
```

### Test Parent Application

```bash
cd tes
python welcome_app.py
```

### Test Widget Directly

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()
widget = ObjectDistanceWidget(root)
widget.pack()
widget.start()
root.mainloop()
```

---

## 🐛 Troubleshooting

### Widget tidak muncul
- Pastikan parent frame sudah di-pack/place/grid
- Check widget di-pack setelah parent

### Camera tidak terbuka
- Coba camera ID lain (1, 2, 3)
- Tutup aplikasi lain yang menggunakan camera

### Import error
- Pastikan path widget benar
- Install dependencies lengkap

### YOLO model tidak ditemukan
- Download otomatis saat pertama kali run
- Pastikan koneksi internet tersedia

---

## 📚 Documentation Files

### Widget Documentation
- `object_distance_widget/README.md` - Widget usage guide

### Parent App Documentation
- `tes/README_PARENT_APP.md` - Parent application guide
- `tes/TEST_IMPORT_GUIDE.md` - Test import procedures
- `tes/SUMMARY_WIDGET.md` - This summary document

### Original Documentation
- `v6_Deteksi_Object_Mendekat/export_to_widget/README.md` - Original app guide

---

## ✅ Verification

### Widget Package Created
- [x] `object_distance_widget/__init__.py`
- [x] `object_distance_widget/widget_core.py`
- [x] `object_distance_widget/widget_variables.py`
- [x] `object_distance_widget/README.md`

### Parent Application Created
- [x] `tes/welcome_app.py`
- [x] `tes/requirements.txt`
- [x] `tes/run.bat`
- [x] `tes/test_import.py`
- [x] `tes/README_PARENT_APP.md`
- [x] `tes/TEST_IMPORT_GUIDE.md`
- [x] `tes/SUMMARY_WIDGET.md`

### Features Preserved
- [x] All detection features
- [x] SIAGA system
- [x] Parking system (4 fases)
- [x] UI elements (optional with CLEAN_UI)
- [x] Configuration options
- [x] Optimization features

---

## 🎉 Summary

Widget **ObjectDistanceWidget** berhasil dibuat sebagai package reusable yang:

1. ✅ **Dapat di-copy paste** ke project apapun
2. ✅ **Flexible** - dapat dipasang di frame apapun
3. ✅ **Tidak mengubah fitur** dan tampilan asli
4. ✅ **Mudah digunakan** - tinggal import dan instantiate

**Location:**
- Widget: `v6_Deteksi_Object_Mendekat\export_to_widget\object_distance_widget\`
- Demo App: `tes\welcome_app.py`

**Usage:**
```python
from object_distance_widget import ObjectDistanceWidget

widget = ObjectDistanceWidget(parent_frame, camera_id=0)
widget.pack(fill=tk.BOTH, expand=True)
widget.start()
```

---

**Created:** 2026-03-13  
**Version:** 1.0.0  
**Status:** ✅ Complete and Ready to Use
