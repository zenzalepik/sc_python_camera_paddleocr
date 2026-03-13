# 🎯 Object Distance Detection Widget

**Reusable Widget untuk Real-time Object Distance Detection dengan YOLO**

Widget ini dapat dipasang di frame apapun dan bersifat flexible. Copy paste folder `object_distance_widget` ke project manapun dan langsung gunakan!

---

## 📦 Instalasi

### 1. Copy Widget Package

Copy folder `object_distance_widget` ke project Anda:

```
your_project/
├── object_distance_widget/    # Copy folder ini
│   ├── __init__.py
│   ├── widget_core.py
│   └── widget_variables.py
├── main.py
└── requirements.txt
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies yang diperlukan:
- `ultralytics` - YOLO model
- `opencv-python` - Camera processing
- `Pillow` - Image processing untuk tkinter
- `numpy` - Numerical operations
- `tkinter` - GUI framework (biasanya sudah include dengan Python)

---

## 🚀 Quick Start

### Contoh Minimal

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

def on_session_complete(session):
    print(f"Session complete: {session.session_id}")

# Create main window
root = tk.Tk()
root.title("Object Distance Detection")
root.geometry("800x600")

# Create and pack widget
widget = ObjectDistanceWidget(
    root,
    camera_id=0,
    on_session_complete=on_session_complete
)
widget.pack(fill=tk.BOTH, expand=True)

# Start detection
widget.start()

# Run main loop
root.mainloop()
```

---

## 📖 API Reference

### ObjectDistanceWidget

Widget utama untuk object distance detection.

#### Constructor

```python
widget = ObjectDistanceWidget(
    parent,              # Parent frame/container
    camera_id=0,         # Camera device ID (default: 0)
    confidence_threshold=0.5,  # YOLO confidence threshold
    on_session_complete=None,  # Callback saat session selesai
    **kwargs             # Additional tkinter.Frame options
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `start()` | Start detection |
| `stop()` | Stop detection |
| `toggle_yolo()` | Toggle YOLO on/off |
| `reset_tracking()` | Reset tracking |
| `trigger_loop_detector()` | Trigger loop detector capture (FASE 3) |
| `trigger_tap_card()` | Trigger tap card capture (FASE 4) |
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
TARGET_CLASSES = [0, 67, 1, 2, 3, 5, 7]  # person, cell phone, bicycle, car, motorcycle, bus, truck

# Tracker Settings
SIAGA_FRAME_THRESHOLD = 3  # Frame berturut-turut untuk trigger SIAGA
SIAGA_HOLD_TIME = 3.0      # Detik SIAGA tetap aktif setelah object hilang

# Parking System
FASE1_TARGET = 3  # SIAGA - approaching
FASE2_TARGET = 5  # TETAP - stopped
FASE3_TARGET = 3  # LOOP detector
FASE4_TARGET = 3  # TAP card

# UI Settings
CLEAN_UI = False   # True = Hide all UI elements
WINDOW_SCALE = 2.0 # Window display scale
```

---

## 🎨 Usage Examples

### 1. Widget di Frame

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()
root.title("My Application")

# Create frame
frame = tk.Frame(root, bg='white')
frame.pack(fill=tk.BOTH, expand=True)

# Add widget to frame
widget = ObjectDistanceWidget(frame)
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

### 3. With Control Buttons

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

def on_session_complete(session):
    print(f"✅ Session {session.session_id} completed!")

root = tk.Tk()
root.title("Object Detection with Controls")

# Control frame
control_frame = tk.Frame(root)
control_frame.pack(fill=tk.X, padx=10, pady=5)

# Create widget
widget = ObjectDistanceWidget(
    root,
    camera_id=0,
    on_session_complete=on_session_complete
)
widget.pack(fill=tk.BOTH, expand=True)

# Control buttons
def on_start():
    widget.start()

def on_stop():
    widget.stop()

def on_toggle_yolo():
    widget.toggle_yolo()

def on_reset():
    widget.reset_tracking()

tk.Button(control_frame, text="Start", command=on_start).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Stop", command=on_stop).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Toggle YOLO", command=on_toggle_yolo).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Reset", command=on_reset).pack(side=tk.LEFT, padx=5)

root.mainloop()
```

### 4. Keyboard Controls

```python
import tkinter as tk
from object_distance_widget import ObjectDistanceWidget

root = tk.Tk()
root.title("Keyboard Controls Example")

widget = ObjectDistanceWidget(root, camera_id=0)
widget.pack(fill=tk.BOTH, expand=True)

def on_key_press(event):
    if event.char == 'y':
        widget.toggle_yolo()
    elif event.char == 'r':
        widget.reset_tracking()
    elif event.char == 'l':
        widget.trigger_loop_detector()
    elif event.char == 't':
        widget.trigger_tap_card()
    elif event.char == 'q':
        root.quit()

root.bind('<Key>', on_key_press)
widget.start()
root.mainloop()
```

---

## 🅿️ Parking System

Widget ini include parking system dengan 4 fase:

1. **FASE 1 (SIAGA)** - Capture 3 frame saat object mendekat
2. **FASE 2 (TETAP)** - Capture 5 frame saat object berhenti
3. **FASE 3 (LOOP)** - Capture 3 frame saat loop detector trigger
4. **FASE 4 (TAP)** - Capture 3 frame saat tap card trigger

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

## 🎯 Target Classes

Default target classes (COCO dataset):

| ID | Class | Description |
|----|-------|-------------|
| 0 | person | Orang |
| 1 | bicycle | Sepeda |
| 2 | car | Mobil |
| 3 | motorcycle | Motor |
| 5 | bus | Bus |
| 7 | truck | Truk |
| 67 | cell phone | Ponsel |

Ubah di `widget_variables.py`:
```python
TARGET_CLASSES = [0]  # Hanya track person
```

---

## ⚡ Performance Optimization

### Camera Resolution

Lower resolution = smoother performance:

```python
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
```

### YOLO Frame Skipping

Skip frames untuk performa lebih baik:

```python
YOLO_SKIP_FRAMES = 1  # Skip 1 frame (balanced)
```

### CLEAN_UI Mode

Hide UI elements untuk performa maksimal:

```python
CLEAN_UI = True
```

---

## 🔧 Troubleshooting

### Camera tidak terdeteksi

```python
# Coba camera ID lain
widget = ObjectDistanceWidget(root, camera_id=1)  # atau 2, 3, dst
```

### Widget tidak muncul

Pastikan parent frame sudah di-pack/place/grid:

```python
frame.pack(fill=tk.BOTH, expand=True)  # atau place/grid
widget.pack(fill=tk.BOTH, expand=True)
```

### YOLO model tidak ditemukan

Download model otomatis saat pertama kali run, atau download manual:

```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

---

## 📝 License

Apache License 2.0

---

## 🙏 Credits

- **Ultralytics** - YOLOv8 model
- **OpenCV Team** - Computer Vision Library
- **COCO Dataset** - Object Detection Dataset

---

**Version:** 1.0.0  
**Created:** 2026-03-13  
**Folder:** object_distance_widget
