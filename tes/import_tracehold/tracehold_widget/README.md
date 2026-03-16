# TraceHold Widget - ROI Object Detection

Widget reusable untuk deteksi object dengan Region of Interest (ROI) menggunakan OpenCV-based motion/contour detection (TANPA YOLO).

---

## 📦 Struktur Folder

```
import_tracehold/
├── app.py                    # Demo aplikasi menggunakan widget
├── non_widget/               # Aplikasi standalone asli (referensi)
└── tracehold_widget/         # ✅ WIDGET REUSABLE
    ├── __init__.py           # Module exports
    ├── widget_wrapper.py     # Class TraceHoldWidget
    ├── main.py               # Standalone app (referensi)
    ├── variables.py          # Configuration
    └── ...
```

---

## 🚀 Cara Menggunakan Widget di Project Lain

### Step 1: Copy Folder Widget

Copy seluruh folder `tracehold_widget` ke project Anda:

```
your_project/
├── main.py           # Aplikasi Anda
└── tracehold_widget/ # ← COPY folder ini
    ├── __init__.py
    ├── widget_wrapper.py
    ├── variables.py
    └── ...
```

### Step 2: Import Widget

```python
from tracehold_widget import TraceHoldWidget
```

### Step 3: Buat Widget Instance

```python
# Basic usage
widget = TraceHoldWidget(camera_id=0)

# Dengan custom config
widget = TraceHoldWidget(
    camera_id=0,
    config={
        'AUTO_RESET_ENABLED': True,
        'NO_MOTION_THRESHOLD': 300,  # frames
        'OBJECT_CONFIRM_THRESHOLD': 3,
    }
)
```

### Step 4: Get Frame dalam Loop

```python
import cv2

widget = TraceHoldWidget(camera_id=0)

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    # Frame SUDAH ADA UI LENGKAP:
    # - ROI box (berkedip biru jika ada object)
    # - Status labels
    # - Debug info
    
    cv2.imshow('My App', frame)
    
    # Handle keyboard
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        widget.reset_background()
    elif key == ord('o'):
        widget.toggle_auto_reset()
    elif key == ord('u'):
        widget.toggle_preview()

widget.release()
cv2.destroyAllWindows()
```

---

## 🎯 Contoh Lengkap

### Contoh 1: Basic Detection

```python
from tracehold_widget import TraceHoldWidget
import cv2

widget = TraceHoldWidget(camera_id=0)

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    # Access state
    object_in_roi = state.get('object_in_roi', False)
    object_present = state.get('object_present', False)
    mode = state.get('mode', 'MOG2')
    
    if object_in_roi:
        print("Object detected in ROI!")
    
    cv2.imshow('Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

widget.release()
cv2.destroyAllWindows()
```

### Contoh 2: Dengan Auto Reset Control

```python
from tracehold_widget import TraceHoldWidget
import cv2

widget = TraceHoldWidget(camera_id=0)

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    auto_reset = state.get('auto_reset_state', False)
    roi_empty = state.get('roi_empty_frames', 0)
    
    print(f"AUTO RESET: {auto_reset}, ROI Empty: {roi_empty}/300")
    
    cv2.imshow('TraceHold', frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('o'):
        new_mode = widget.toggle_auto_reset()
        print(f"Auto reset: {'ON' if new_mode else 'OFF'}")
    elif key == ord('r'):
        widget.reset_background()
        print("Background reset")

widget.release()
cv2.destroyAllWindows()
```

### Contoh 3: Dengan Preview Window

```python
from tracehold_widget import TraceHoldWidget
import cv2

widget = TraceHoldWidget(camera_id=0)

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    cv2.imshow('Main', frame)
    
    # Draw preview window (jika aktif)
    widget.draw_preview(frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('u'):
        preview = widget.toggle_preview()
        print(f"Preview: {'ON' if preview else 'OFF'}")

widget.release()
cv2.destroyAllWindows()
```

### Contoh 4: Custom Layout (Split Screen)

```python
from tracehold_widget import TraceHoldWidget
import cv2
import numpy as np

widget = TraceHoldWidget(camera_id=0)

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    # Buat layout custom: kiri teks, kanan camera
    full_frame = np.zeros((700, 1280, 3), dtype=np.uint8)
    
    # Frame kiri: Teks "Selamat Datang"
    left_frame = full_frame[:, :640]
    left_frame[:] = 255  # White background
    cv2.putText(left_frame, "Selamat Datang", (170, 350),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    
    # Frame kanan: TraceHold output
    tracehold_resized = cv2.resize(frame, (640, 700))
    full_frame[:, 640:] = tracehold_resized
    
    cv2.imshow('Custom Layout', full_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

widget.release()
cv2.destroyAllWindows()
```

---

## 📖 API Reference

### Constructor

```python
widget = TraceHoldWidget(
    camera_id=0,              # Camera device ID (default: 0)
    config=None               # Optional config dict
)
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_frame()` | Get frame dengan semua processing | `(frame, state_dict)` |
| `toggle_auto_reset()` | Toggle auto reset ON/OFF | `bool` |
| `reset_background()` | Manual background reset | - |
| `toggle_preview()` | Toggle preview window | `bool` |
| `draw_preview(frame)` | Draw preview window | - |
| `release()` | Release camera resources | - |

### State Dict Keys

```python
state = {
    'object_in_roi': bool,           # Object di ROI
    'object_present': bool,          # Object confirmed present
    'persistent_object_in_roi': bool, # Persistent tracking
    'roi_occupied': bool,            # ROI occupied status
    'auto_reset_state': bool,        # Auto reset ON/OFF
    'roi_empty_frames': int,         # Counter empty frames
    'has_detected_object': bool,     # Any object detected
    'has_green_box': bool,           # Green box displayed
    'mode': 'MOG2' | 'Static',       # Current mode
    'indicator_on': bool,            # Indicator status
    'blink_state': bool,             # Blink status
    'frame_count': int,              # Frame counter
}
```

---

## ⚙️ Configuration

Default config bisa di-override via constructor:

```python
config = {
    'AUTO_RESET_ENABLED': True,         # MOG2 adaptive background
    'NO_MOTION_THRESHOLD': 300,         # Frames sebelum auto reset (~10 detik)
    'OBJECT_CONFIRM_THRESHOLD': 3,      # Frames untuk konfirmasi object
    'OBJECT_LOST_THRESHOLD': 30,        # Frames sebelum object dianggap pergi
    'ROI_WIDTH_FRACTION': 0.75,         # ROI width (75% dari frame)
    'ROI_HEIGHT_FRACTION': 0.5,         # ROI height (50% dari frame)
    'BLINK_INTERVAL': 10,               # Interval kedipan indikator
    'CAMERA_INDEX': 0,                  # Camera device ID
    'BLUR_KERNEL_SIZE': (5, 5),         # Gaussian blur kernel
    'BG_DIFF_THRESHOLD': 40,            # Background diff threshold
    'FRAME_DIFF_THRESHOLD': 40,         # Frame diff threshold
    'INIT_CAPTURE_COUNT': 1,            # Frames untuk background reference
    'MIN_CONTOUR_AREA': 800,            # Minimum area contour
    'MIN_BOX_WIDTH': 120,               # Minimum width bounding box
    'MIN_BOX_HEIGHT': 120,              # Minimum height bounding box
    'BG_SUBTRACTOR_HISTORY': 200,       # MOG2 history
    'BG_SUBTRACTOR_VAR_THRESHOLD': 30,  # MOG2 variance threshold
}

widget = TraceHoldWidget(config=config)
```

---

## 🎹 Keyboard Controls

| Key | Function |
|-----|----------|
| `q` | Quit aplikasi |
| `r` | Reset background |
| `o` | Toggle auto reset ON/OFF |
| `u` | Toggle preview window |

---

## 📝 Detection Flow

```
1. App Start → Initialize MOG2 atau Static Background
2. Object Masuk ROI → ROI box berkedip BIRU
3. Object Diam → Canny edge backup detection
4. Object Diam > 300 frames (~10 detik) → AUTO RESET
5. MOG2 Learning Phase (100 frames / ~3.3 detik)
6. Ready → Waiting for new motion
```

---

## ✨ Fitur Utama

### 1. Dual Mode Detection

- **AUTO_RESET=True**: MOG2 Background Subtractor (adaptive)
- **AUTO_RESET=False**: Static Background Reference (object diam tetap terdeteksi)

### 2. ROI (Region of Interest)

- Area fokus di tengah frame (75% width × 50% height)
- Kotak ROI berkedip BIRU saat ada object
- Kotak ROI ABU-ABU saat tidak ada object

### 3. Auto Reset

- Reset background setelah ROI kosong selama `NO_MOTION_THRESHOLD` frames
- MOG2 learning phase (100 frames / ~3.3 detik)
- Console log countdown setiap detik

### 4. Canny Edge Backup

- Backup detection saat object diam
- Object tetap terdeteksi meskipun MOG2 sudah "belajar"

### 5. Preview Window

- Toggle dengan tombol 'u'
- Tampilkan grayscale, Canny edge, dan mask views
- Mode MOG2: 3 panel (grayscale, edge, mask)
- Mode Static: 5 panel (current, bg ref, bg diff, frame diff, combined)

---

## ⚠️ Troubleshooting

### Error: Module not found

```python
# Pastikan folder tracehold_widget sejajar dengan script Anda
# Atau tambahkan ke path:
import sys
sys.path.insert(0, '/path/to/tracehold_widget')
from tracehold_widget import TraceHoldWidget
```

### Error: Camera not opened

```python
# Coba camera ID lain
widget = TraceHoldWidget(camera_id=1)  # atau 2, 3, ...

# Check camera permission di Windows Settings
```

### ROI box tidak berkedip biru

```python
# Pastikan:
# 1. Ada object di depan kamera
# 2. Object masuk ke area ROI (kotak di tengah)
# 3. Tunggu 3 frames (OBJECT_CONFIRM_THRESHOLD)
# 4. Check console log untuk debug info
```

### Auto reset tidak jalan

```python
# Check auto reset status
state = widget.get_frame()[1]
print(f"Auto reset: {state.get('auto_reset_state')}")

# Toggle auto reset
widget.toggle_auto_reset()
```

---

## 📄 License

Widget ini adalah refactored version dari `non_widget/main.py`.

---

## 🆘 Support

Untuk contoh lengkap, lihat file `app.py` di folder ini.

**Quick Start:**
```bash
python app.py
```

**Controls:**
- `q` - Quit
- `r` - Reset background
- `o` - Toggle auto reset
- `u` - Toggle preview

---

**Last Updated:** 2026-03-16
