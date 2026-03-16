# YOLO Widget - Parking System

Widget reusable untuk deteksi object dengan sistem parkir 4-fase.

Widget ini adalah versi reusable dari aplikasi `non_widget/main.py` dengan **semua fitur lengkap**:
- Object Detection (YOLOv8n)
- Distance Tracking (mendekat/menjauh)
- SIAGA System
- Parking Session (4 Fase: SIAGA → TETAP → LOOP → TAP)
- UI Overlays lengkap
- Signal "Terimakasih" hijau saat parking berhasil

---

## 📦 Struktur Folder

```
import_yolo8n/
├── yolo_widget/              # ✅ WIDGET REUSABLE
│   ├── __init__.py           # Module exports
│   ├── main.py               # Full logic (1806 baris dari non_widget)
│   ├── widget_wrapper.py     # Wrapper untuk import mudah
│   ├── variables.py          # Configuration
│   ├── yolov8n.pt            # YOLO model
│   ├── README.md             # Dokumentasi widget
│   └── ...
│
├── app.py                    # Demo aplikasi menggunakan widget
├── non_widget/               # Aplikasi standalone asli (referensi)
└── README.md                 # Dokumentasi ini
```

---

## 🚀 Cara Menggunakan Widget di Project Lain

### Step 1: Copy Folder Widget

Copy seluruh folder `yolo_widget` ke project Anda:

```
your_project/
├── main.py           # Aplikasi Anda
└── yolo_widget/      # ← COPY folder ini
    ├── __init__.py
    ├── main.py
    ├── widget_wrapper.py
    ├── variables.py
    ├── yolov8n.pt
    └── ...
```

### Step 2: Import Widget

```python
from yolo_widget import YOLOWidget
```

### Step 3: Buat Widget Instance

```python
# Basic usage
widget = YOLOWidget(camera_id=0)

# Dengan custom config
widget = YOLOWidget(
    camera_id=0,
    config={
        'YOLO_CONFIDENCE_THRESHOLD': 0.5,
        'TARGET_CLASSES': [0],  # Hanya detect person
        'CLEAN_UI': False,
    }
)
```

### Step 4: Get Frame dalam Loop

```python
import cv2

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    # Frame SUDAH ADA UI LENGKAP:
    # - Detection boxes
    # - Tracking ID
    # - SIAGA indicator
    # - Info panel
    # - Parking session info
    
    cv2.imshow('My App', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

widget.release()
cv2.destroyAllWindows()
```

---

## 🎯 Contoh Lengkap

### Contoh 1: Basic Detection

```python
from yolo_widget import YOLOWidget
import cv2

widget = YOLOWidget(camera_id=0)

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    # Akses state
    detections = state.get('detections', [])
    tracked_id = state.get('tracked_object_id')
    siaga_active = state.get('siaga_active', False)
    
    print(f"Tracked: {tracked_id}, SIAGA: {siaga_active}")
    
    cv2.imshow('Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

widget.release()
cv2.destroyAllWindows()
```

### Contoh 2: Dengan Parking System

```python
from yolo_widget import YOLOWidget, ParkingPhase
import cv2

widget = YOLOWidget(camera_id=0)

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    phase = state.get('parking_phase')
    session_active = state.get('parking_session_active', False)
    
    # Handle keyboard
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('l'):  # Loop Detector (FASE 3)
        widget.trigger_loop_detector(frame)
    
    elif key == ord('t'):  # Tap Card (FASE 4)
        widget.trigger_tap_card(frame)
    
    elif key == ord('q'):
        break
    
    cv2.imshow('Parking System', frame)

widget.release()
cv2.destroyAllWindows()
```

### Contoh 3: Integrasi dengan Barrier Gate

```python
from yolo_widget import YOLOWidget, ParkingPhase
import cv2
import requests  # Untuk API call

widget = YOLOWidget(camera_id=0)

last_phase = None

while True:
    frame, state = widget.get_frame()
    
    if frame is None:
        break
    
    current_phase = state.get('parking_phase')
    
    # Detect phase change to PREVIEW_READY
    if (last_phase != current_phase and 
        current_phase == ParkingPhase.PREVIEW_READY):
        
        # Kirim signal ke barrier gate
        requests.post('http://localhost:8080/barrier/open')
        print("✅ Barrier opened!")
    
    last_phase = current_phase
    
    cv2.imshow('Parking', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

widget.release()
cv2.destroyAllWindows()
```

### Contoh 4: Custom Layout (Split Screen)

```python
from yolo_widget import YOLOWidget
import cv2
import numpy as np

widget = YOLOWidget(camera_id=0)

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
    
    # Frame kanan: YOLO output
    yolo_resized = cv2.resize(frame, (640, 700))
    full_frame[:, 640:] = yolo_resized
    
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
widget = YOLOWidget(
    camera_id=0,              # Camera device ID (default: 0)
    config=None               # Optional config dict
)
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_frame()` | Get frame dengan semua processing | `(frame, state_dict)` |
| `toggle_yolo()` | Toggle YOLO on/off | `bool` |
| `trigger_loop_detector(frame)` | Trigger loop detector (FASE 3) | - |
| `trigger_tap_card(frame)` | Trigger tap card (FASE 4) | - |
| `reset_tracking()` | Reset semua tracking | - |
| `release()` | Release camera resources | - |

### State Dict Keys

```python
state = {
    'detections': [...],              # List of detections
    'tracked_object_id': 'PERSON_1',  # ID object yang di-track
    'status': 'approaching',          # approaching/moving_away/stable
    'siaga_active': True,             # SIAGA status
    'siaga_cleared': False,           # SIAGA cleared status
    'parking_phase': ParkingPhase.FASE1_SIAGA,
    'parking_session_active': True,
    'session_success_time': 1234567890.123,  # Timestamp saat success
    'fps': 30,
    'yolo_enabled': True,
    'clean_ui': False,
}
```

### ParkingPhase Enum

```python
from yolo_widget import ParkingPhase

ParkingPhase.NO_VEHICLE      # Tidak ada kendaraan
ParkingPhase.FASE1_SIAGA     # SIAGA aktif, capture 3 frame
ParkingPhase.FASE2_TETAP     # Kendaraan berhenti, capture 5 frame
ParkingPhase.FASE3_LOOP      # Menunggu tombol loop detector
ParkingPhase.FASE4_TAP       # Menunggu tombol tap card
ParkingPhase.PREVIEW_READY   # Semua fase selesai
```

---

## ⚙️ Configuration

Default config bisa di-override via constructor:

```python
config = {
    'CLEAN_UI': False,              # Hide UI elements
    'YOLO_SKIP_FRAMES': 2,          # Frame skipping untuk performance
    'YOLO_CONFIDENCE_THRESHOLD': 0.5,
    'TARGET_CLASSES': [0],          # 0=person, 2=car, 3=motorcycle, dst
    'MAX_HISTORY': 30,              # History untuk trend analysis
    'SIAGA_FRAME_THRESHOLD': 3,     # Frame untuk trigger SIAGA
    'SIAGA_HOLD_TIME': 3.0,         # Detik SIAGA hold setelah object hilang
    'FASE1_TARGET': 3,              # Frame target FASE 1
    'FASE2_TARGET': 5,              # Frame target FASE 2
    'FASE3_TARGET': 3,              # Frame target FASE 3
    'FASE4_TARGET': 3,              # Frame target FASE 4
    'SHOW_FPS': True,               # Show FPS counter
}

widget = YOLOWidget(config=config)
```

---

## 🎹 Keyboard Controls

| Key | Function |
|-----|----------|
| `q` / `ESC` | Quit aplikasi |
| `y` | Toggle YOLO on/off |
| `r` | Reset tracking |
| `l` | Trigger Loop Detector (FASE 3) |
| `t` | Trigger Tap Card (FASE 4) |

---

## 📝 Parking Session Flow

```
1. NO_VEHICLE → Tunggu object terdeteksi
2. FASE1_SIAGA → Object mendekat, capture 3 frame
3. FASE2_TETAP → Kendaraan berhenti, capture 5 frame
4. FASE3_LOOP → Trigger loop detector, capture 3 frame
5. FASE4_TAP → Trigger tap card, capture 3 frame
6. PREVIEW_READY → Session selesai
   - Tampil "Terimakasih" hijau selama 2 detik
   - Auto-reset ke NO_VEHICLE
```

---

## ✨ Fitur "Terimakasih"

Saat parking session berhasil selesai (semua 4 fase complete):

1. **Teks berubah**: "Selamat Datang" → "Terimakasih"
2. **Warna**: Hitam → Hijau
3. **Durasi**: 2 detik
4. **Auto-reset**: Kembali ke "Selamat Datang" setelah 2 detik

**Signal success** bisa dilihat dari:
- Log terminal: `[✅ SESSION COMPLETE] Parking berhasil!`
- State dict: `session_success_time` (timestamp)

---

## ⚠️ Troubleshooting

### Error: Module not found

```python
# Pastikan folder yolo_widget sejajar dengan script Anda
# Atau tambahkan ke path:
import sys
sys.path.insert(0, '/path/to/yolo_widget')
from yolo_widget import YOLOWidget
```

### Error: Camera not opened

```python
# Coba camera ID lain
widget = YOLOWidget(camera_id=1)  # atau 2, 3, ...

# Check camera permission di Windows Settings
```

### Error: Model not found

```python
# Pastikan yolov8n.pt ada di folder yolo_widget
# File harus berukuran ~6.5MB

# Atau specify custom path (perlu modifikasi widget_wrapper.py)
```

### Detection lambat

```python
# Increase frame skipping
config = {'YOLO_SKIP_FRAMES': 5}  # Skip lebih banyak frame
widget = YOLOWidget(config=config)
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
- `y` - Toggle YOLO
- `r` - Reset tracking
- `l` - Loop Detector (FASE 3)
- `t` - Tap Card (FASE 4)
