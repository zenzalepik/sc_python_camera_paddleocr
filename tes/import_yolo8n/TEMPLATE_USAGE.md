# 📋 Cara Menggunakan Template app.py

Panduan lengkap cara menggunakan dan memodifikasi template `app.py` untuk project Anda.

---

## 🎯 Struktur Template app.py

Template `app.py` saat ini memiliki struktur:

```
┌─────────────────────────────────────────────────────────┐
│              Aplikasi Python - YOLO Widget              │
│                   Window: 1280 x 700                    │
├──────────────────────────────┬──────────────────────────┤
│                              │                          │
│   FRAME KIRI (50%)           │   FRAME KANAN (50%)      │
│   - Teks "Selamat Datang"    │   - YOLO Widget          │
│   - 4 Tombol horizontal      │   - Camera feed          │
│                              │   - Detection UI         │
│                              │                          │
└──────────────────────────────┴──────────────────────────┘
```

---

## 📦 Step-by-Step Memasang Widget ke app.py

### Step 1: Import Widget

```python
import sys
import os

# Tambahkan path ke yolo_widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "yolo_widget"))

# Import widget
from yolo_widget import YOLOWidget
```

### Step 2: Inisialisasi Widget di Class

```python
class ResponsiveApp:
    def __init__(self, window_width=1280, window_height=700):
        self.window_width = window_width
        self.window_height = window_height
        self.window_name = "Aplikasi Python - YOLO Widget"
        
        # ✅ INIT WIDGET DI SINI
        self.widget = YOLOWidget(camera_id=0)
```

### Step 3: Get Frame di Main Loop

```python
def run(self):
    try:
        while True:
            # ✅ GET FRAME DARI WIDGET
            yolo_frame, state = self.widget.get_frame()
            
            if yolo_frame is None:
                break
            
            # Process frame...
            cv2.imshow(self.window_name, yolo_frame)
            
            # Handle keyboard
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
    
    finally:
        # ✅ RELEASE WIDGET
        self.widget.release()
        cv2.destroyAllWindows()
```

---

## 🎨 Kustomisasi Layout

### Opsi 1: Full Screen Camera (Tanpa Split)

```python
def run(self):
    widget = YOLOWidget(camera_id=0)
    
    cv2.namedWindow('Full Camera', cv2.WINDOW_NORMAL)
    
    while True:
        frame, state = widget.get_frame()
        
        if frame is None:
            break
        
        # Langsung tampilkan frame penuh
        cv2.imshow('Full Camera', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    widget.release()
    cv2.destroyAllWindows()
```

### Opsi 2: Split Screen Custom

```python
def draw(self, frame, yolo_frame=None):
    height, width = frame.shape[:2]
    
    # Custom split: 30% kiri, 70% kanan
    left_width = int(width * 0.3)
    right_width = width - left_width
    
    # Frame kiri (30%)
    left_frame = frame[:, :left_width]
    left_frame[:] = 255  # White background
    cv2.putText(left_frame, "Info Panel", (50, 100),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Frame kanan (70%) - YOLO
    if yolo_frame is not None:
        yolo_resized = cv2.resize(yolo_frame, (right_width, height))
        frame[:, left_width:] = yolo_resized
    
    return frame
```

### Opsi 3: Picture-in-Picture (PiP)

```python
def draw_pip(self, frame, yolo_frame):
    # Full background
    frame[:] = (50, 50, 50)  # Dark gray
    
    # YOLO full screen
    yolo_resized = cv2.resize(yolo_frame, (frame.shape[1], frame.shape[0]))
    frame[:] = yolo_resized
    
    # PiP window di pojok kanan atas
    pip_width = 320
    pip_height = 240
    pip_x = frame.shape[1] - pip_width - 20
    pip_y = 20
    
    # Draw PiP border
    cv2.rectangle(frame, (pip_x - 2, pip_y - 2),
                 (pip_x + pip_width + 2, pip_y + pip_height + 2),
                 (255, 255, 255), 3)
    
    # Info box di PiP
    cv2.putText(frame, "Info", (pip_x + 10, pip_y + 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return frame
```

---

## 🔧 Kustomisasi Widget Config

### Contoh 1: Custom Confidence Threshold

```python
self.widget = YOLOWidget(
    camera_id=0,
    config={
        'YOLO_CONFIDENCE_THRESHOLD': 0.7,  # Lebih ketat
    }
)
```

### Contoh 2: Hanya Detect Person

```python
self.widget = YOLOWidget(
    camera_id=0,
    config={
        'TARGET_CLASSES': [0],  # 0 = person
    }
)
```

### Contoh 3: Detect Vehicles Only

```python
self.widget = YOLOWidget(
    camera_id=0,
    config={
        'TARGET_CLASSES': [2, 3, 5, 7],  # car, motorcycle, bus, truck
    }
)
```

### Contoh 4: Clean UI (Tanpa Overlays)

```python
self.widget = YOLOWidget(
    camera_id=0,
    config={
        'CLEAN_UI': True,  # Hide UI overlays
    }
)
```

---

## 🎹 Menambahkan Keyboard Controls

### Template Basic

```python
def run(self):
    while True:
        yolo_frame, state = self.widget.get_frame()
        
        # ... draw frame ...
        
        # Handle keyboard
        key = cv2.waitKey(10) & 0xFF
        
        if key == ord('q'):
            break
        
        elif key == ord('y'):
            # Toggle YOLO
            self.widget.toggle_yolo()
            print(f"YOLO: {'ON' if self.widget.detector.yolo_enabled else 'OFF'}")
        
        elif key == ord('r'):
            # Reset tracking
            self.widget.reset_tracking()
            print("Tracking reset")
        
        elif key == ord('l'):
            # Loop Detector (FASE 3)
            self.widget.trigger_loop_detector(yolo_frame)
            print("Loop Detector triggered")
        
        elif key == ord('t'):
            # Tap Card (FASE 4)
            self.widget.trigger_tap_card(yolo_frame)
            print("Tap Card triggered")
```

### Template Dengan State Check

```python
def run(self):
    while True:
        yolo_frame, state = self.widget.get_frame()
        
        # Check state
        siaga_active = state.get('siaga_active', False)
        phase = state.get('parking_phase')
        
        # Handle keyboard
        key = cv2.waitKey(10) & 0xFF
        
        if key == ord('l'):
            # Hanya trigger jika di FASE 3
            if phase == ParkingPhase.FASE3_LOOP:
                self.widget.trigger_loop_detector(yolo_frame)
            else:
                print("Cannot trigger: Not in FASE 3")
        
        elif key == ord('t'):
            # Hanya trigger jika di FASE 4
            if phase == ParkingPhase.FASE4_TAP:
                self.widget.trigger_tap_card(yolo_frame)
            else:
                print("Cannot trigger: Not in FASE 4")
```

---

## 📊 Mengakses State untuk Custom Logic

### Contoh 1: Trigger Action Saat SIAGA Aktif

```python
def run(self):
    last_siaga_state = False
    
    while True:
        yolo_frame, state = self.widget.get_frame()
        
        siaga_active = state.get('siaga_active', False)
        
        # Detect SIAGA state change
        if siaga_active and not last_siaga_state:
            print("⚠️ SIAGA activated! Object approaching!")
            # Trigger action: play sound, send notification, etc.
        
        last_siaga_state = siaga_active
```

### Contoh 2: Log Parking Session

```python
from datetime import datetime

def run(self):
    last_phase = None
    
    while True:
        yolo_frame, state = self.widget.get_frame()
        
        current_phase = state.get('parking_phase')
        session_active = state.get('parking_session_active', False)
        
        # Log phase changes
        if current_phase != last_phase:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Phase: {current_phase.name}")
            
            # Save to file
            with open('parking_log.txt', 'a') as f:
                f.write(f"{timestamp} - {current_phase.name}\n")
        
        last_phase = current_phase
```

### Contoh 3: Integrate dengan Barrier Gate API

```python
import requests

def run(self):
    last_phase = None
    
    while True:
        yolo_frame, state = self.widget.get_frame()
        
        current_phase = state.get('parking_phase')
        
        # Trigger barrier saat PREVIEW_READY
        if (last_phase != current_phase and 
            current_phase == ParkingPhase.PREVIEW_READY):
            
            # Send API request
            try:
                response = requests.post(
                    'http://barrier-controller:8080/open',
                    json={'action': 'open_barrier'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    print("✅ Barrier opened successfully!")
                else:
                    print(f"❌ API error: {response.status_code}")
            
            except Exception as e:
                print(f"❌ Failed to open barrier: {e}")
        
        last_phase = current_phase
```

---

## 🎨 Custom UI Elements

### Menambahkan Teks Info

```python
def draw_info(self, frame, state):
    """Draw custom info panel."""
    fps = state.get('fps', 0)
    tracked_id = state.get('tracked_object_id', 'None')
    
    # Draw FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Draw tracked object
    cv2.putText(frame, f"Tracking: {tracked_id}", (10, 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
```

### Menambahkan Button Custom

```python
class CustomButton:
    def __init__(self, text, x, y, width, height, color):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, frame):
        cv2.rectangle(frame, (self.x, self.y),
                     (self.x + self.width, self.y + self.height),
                     self.color, -1)
        cv2.putText(frame, self.text, (self.x + 10, self.y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def is_clicked(self, mouse_x, mouse_y):
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)

# Usage
buttons = [
    CustomButton("RESET", 10, 600, 100, 40, (255, 0, 0)),
    CustomButton("LOOP", 120, 600, 100, 40, (0, 255, 0)),
    CustomButton("TAP", 230, 600, 100, 40, (0, 0, 255)),
]

def draw(self, frame):
    for button in buttons:
        button.draw(frame)
```

---

## 📝 Template Lengkap app.py (Minimal)

```python
from yolo_widget import YOLOWidget
import cv2

def main():
    # Init widget
    widget = YOLOWidget(camera_id=0)
    
    # Create window
    cv2.namedWindow('My App', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('My App', 1280, 700)
    
    try:
        while True:
            # Get frame
            frame, state = widget.get_frame()
            
            if frame is None:
                break
            
            # Show frame
            cv2.imshow('My App', frame)
            
            # Handle keyboard
            key = cv2.waitKey(10) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('y'):
                widget.toggle_yolo()
            elif key == ord('r'):
                widget.reset_tracking()
            elif key == ord('l'):
                widget.trigger_loop_detector(frame)
            elif key == ord('t'):
                widget.trigger_tap_card(frame)
    
    finally:
        widget.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```

---

## ⚠️ Common Mistakes

### ❌ Lupa Release Widget

```python
# SALAH
def run(self):
    while True:
        frame, state = self.widget.get_frame()
        # ...
        if key == ord('q'):
            break
    # Lupa release!

# BENAR
def run(self):
    try:
        while True:
            # ...
    finally:
        self.widget.release()  # ✅ Release di finally
        cv2.destroyAllWindows()
```

### ❌ Tidak Check Frame None

```python
# SALAH
frame, state = self.widget.get_frame()
cv2.imshow('App', frame)  # Error jika frame None!

# BENAR
frame, state = self.widget.get_frame()
if frame is not None:
    cv2.imshow('App', frame)
```

### ❌ Wrong Path Import

```python
# SALAH
from yolo_widget import YOLOWidget  # Error jika path salah

# BENAR
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "yolo_widget"))
from yolo_widget import YOLOWidget
```

---

## 🆘 Troubleshooting

### Widget tidak bisa di-import

```python
# Check struktur folder
import os
print(os.listdir('.'))
print(os.listdir('yolo_widget'))

# Pastikan ada __init__.py di folder yolo_widget
```

### Camera tidak terbuka

```python
# Test camera langsung
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(f"Camera opened: {cap.isOpened()}")
print(f"Frame captured: {ret}")
cap.release()
```

### Frame selalu None

```python
# Check camera initialization
widget = YOLOWidget(camera_id=0)

if widget.detector.cap is None or not widget.detector.cap.isOpened():
    print("Camera not opened!")
    # Try different camera ID
    widget = YOLOWidget(camera_id=1)
```

---

## 📚 Resources

- [YOLO Widget README](yolo_widget/README.md)
- [non_widget/main.py](non_widget/main.py) - Full reference
- [app.py](app.py) - Template lengkap

---

**Last Updated:** 2026-03-16
