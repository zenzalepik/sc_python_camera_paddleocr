# 📋 Cara Menggunakan Template app.py

Panduan lengkap cara menggunakan dan memodifikasi template `app.py` untuk project Anda, serta cara memasang TraceHold Widget.

---

## 🎯 Struktur Template app.py

Template `app.py` saat ini memiliki struktur:

```
┌─────────────────────────────────────────────────────────┐
│              Aplikasi Python - TraceHold Widget         │
│                   Window: 1280 x 700                    │
├──────────────────────────────┬──────────────────────────┤
│                              │                          │
│   FRAME KIRI (50%)           │   FRAME KANAN (50%)      │
│   - Teks "Selamat Datang"    │   - TraceHold Widget     │
│   - 4 Tombol horizontal      │   - ROI Detection        │
│                              │   - Object tracking      │
│                              │   - Auto reset status    │
│                              │                          │
└──────────────────────────────┴──────────────────────────┘
```

---

## 📦 Step-by-Step Memasang Widget ke app.py

### Step 1: Import Widget

```python
import sys
import os

# Tambahkan path ke tracehold_widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tracehold_widget"))

# Import widget
from tracehold_widget import TraceHoldWidget
```

### Step 2: Inisialisasi Widget di Class

```python
class ResponsiveApp:
    def __init__(self, window_width=1280, window_height=700):
        self.window_width = window_width
        self.window_height = window_height
        self.window_name = "Aplikasi Python - TraceHold Widget"
        
        # ✅ INIT WIDGET DI SINI
        self.widget = TraceHoldWidget(camera_id=0)
```

### Step 3: Get Frame di Main Loop

```python
def run(self):
    try:
        while True:
            # ✅ GET FRAME DARI WIDGET
            tracehold_frame, state = self.widget.get_frame()
            
            if tracehold_frame is None:
                break
            
            # Process frame...
            cv2.imshow(self.window_name, tracehold_frame)
            
            # Handle keyboard
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
    
    finally:
        # ✅ RELEASE WIDGET
        self.widget.release()
        cv2.destroyAllWindows()
```

### Step 4: Handle Keyboard Controls

```python
# Handle keyboard
key = cv2.waitKey(10) & 0xFF

if key == ord('q'):
    break
elif key == ord('r'):
    self.widget.reset_background()
    print("[🔄] Background reset")
elif key == ord('o'):
    new_mode = self.widget.toggle_auto_reset()
    print(f"[{'✅' if new_mode else '❌'}] Auto reset: {'ON' if new_mode else 'OFF'}")
elif key == ord('u'):
    preview_shown = self.widget.toggle_preview()
    if preview_shown:
        print(f"\n[PREVIEW] ON - Press 'u' again to close")
    else:
        print(f"\n[PREVIEW] OFF")
        try:
            cv2.destroyWindow('Threshold & Grayscale Preview')
        except:
            pass
```

---

## 🎨 Kustomisasi Layout

### Opsi 1: Full Screen Camera (Tanpa Split)

```python
def run(self):
    widget = TraceHoldWidget(camera_id=0)
    
    cv2.namedWindow('Full Camera', cv2.WINDOW_NORMAL)
    
    while True:
        frame, state = widget.get_frame()
        
        if frame is None:
            break
        
        # Langsung tampilkan frame penuh
        cv2.imshow('Full Camera', frame)
        
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

### Opsi 2: Split Screen Custom

```python
def draw(self, frame, tracehold_frame=None):
    height, width = frame.shape[:2]
    
    # Custom split: 30% kiri, 70% kanan
    left_width = int(width * 0.3)
    right_width = width - left_width
    
    # Frame kiri (30%)
    left_frame = frame[:, :left_width]
    left_frame[:] = 255  # White background
    cv2.putText(left_frame, "Info Panel", (50, 100),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Frame kanan (70%) - TraceHold output
    if tracehold_frame is not None:
        tracehold_resized = cv2.resize(tracehold_frame, (right_width, height))
        frame[:, left_width:] = tracehold_resized
    
    return frame
```

### Opsi 3: Picture-in-Picture (PiP)

```python
def draw_pip(self, frame, tracehold_frame):
    # Full background
    frame[:] = (50, 50, 50)  # Dark gray
    
    # TraceHold full screen
    tracehold_resized = cv2.resize(tracehold_frame, (frame.shape[1], frame.shape[0]))
    frame[:] = tracehold_resized
    
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

### Contoh 1: Enable Auto Reset

```python
self.widget = TraceHoldWidget(
    camera_id=0,
    config={
        'AUTO_RESET_ENABLED': True,  # MOG2 adaptive
    }
)
```

### Contoh 2: Disable Auto Reset (Static Background)

```python
self.widget = TraceHoldWidget(
    camera_id=0,
    config={
        'AUTO_RESET_ENABLED': False,  # Static background reference
    }
)
```

### Contoh 3: Custom ROI Threshold

```python
self.widget = TraceHoldWidget(
    camera_id=0,
    config={
        'NO_MOTION_THRESHOLD': 500,  # frames (~16.7 detik)
        'OBJECT_CONFIRM_THRESHOLD': 5,  # frames untuk konfirmasi
    }
)
```

### Contoh 4: Custom ROI Size

```python
self.widget = TraceHoldWidget(
    camera_id=0,
    config={
        'ROI_WIDTH_FRACTION': 0.8,  # 80% dari width
        'ROI_HEIGHT_FRACTION': 0.6,  # 60% dari height
    }
)
```

### Contoh 5: Custom Detection Sensitivity

```python
self.widget = TraceHoldWidget(
    camera_id=0,
    config={
        'MIN_CONTOUR_AREA': 1000,  # Lebih besar = kurang sensitif
        'BG_DIFF_THRESHOLD': 50,   # Lebih tinggi = kurang sensitif
        'FRAME_DIFF_THRESHOLD': 50,
    }
)
```

---

## 📊 Mengakses State untuk Custom Logic

### Contoh 1: Trigger Action Saat Object di ROI

```python
def run(self):
    last_roi_state = False
    
    while True:
        frame, state = self.widget.get_frame()
        
        if frame is None:
            break
        
        object_in_roi = state.get('object_in_roi', False)
        
        # Detect ROI state change
        if object_in_roi and not last_roi_state:
            print("🎯 Object entered ROI!")
            # Trigger action: play sound, send notification, etc.
        
        last_roi_state = object_in_roi
```

### Contoh 2: Log Auto Reset Countdown

```python
def run(self):
    while True:
        frame, state = self.widget.get_frame()
        
        if frame is None:
            break
        
        roi_empty = state.get('roi_empty_frames', 0)
        auto_reset = state.get('auto_reset_state', False)
        
        if auto_reset and roi_empty > 0:
            print(f"⏳ ROI empty: {roi_empty}/300 frames")
        
        cv2.imshow('App', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
```

### Contoh 3: Integrate dengan Barrier Gate API

```python
import requests

def run(self):
    last_object_present = False
    
    while True:
        frame, state = self.widget.get_frame()
        
        if frame is None:
            break
        
        object_present = state.get('object_present', False)
        
        # Detect object presence change
        if object_present and not last_object_present:
            # Object detected - send API request
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
        
        last_object_present = object_present
```

---

## 🎨 Custom UI Elements

### Menambahkan Teks Info

```python
def draw_info(self, frame, state):
    """Draw custom info panel."""
    object_in_roi = state.get('object_in_roi', False)
    auto_reset = state.get('auto_reset_state', False)
    roi_empty = state.get('roi_empty_frames', 0)
    
    # Draw object status
    status_text = "OBJECT IN ROI" if object_in_roi else "NO OBJECT"
    status_color = (0, 255, 0) if object_in_roi else (0, 0, 255)
    cv2.putText(frame, status_text, (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    
    # Draw auto reset status
    reset_text = f"AUTO RESET: {'ON' if auto_reset else 'OFF'}"
    cv2.putText(frame, reset_text, (10, 70),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Draw ROI empty counter
    if auto_reset and not object_in_roi:
        empty_text = f"ROI Empty: {roi_empty}/300"
        cv2.putText(frame, empty_text, (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
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
    CustomButton("AUTO RESET", 120, 600, 150, 40, (0, 255, 0)),
    CustomButton("PREVIEW", 280, 600, 120, 40, (0, 0, 255)),
]

def draw(self, frame):
    for button in buttons:
        button.draw(frame)
```

---

## 📝 Template Lengkap app.py (Minimal)

```python
from tracehold_widget import TraceHoldWidget
import cv2

def main():
    # Init widget
    widget = TraceHoldWidget(camera_id=0)
    
    # Create window
    cv2.namedWindow('My App', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('My App', 1280, 720)
    
    try:
        while True:
            # Get frame
            frame, state = widget.get_frame()
            
            if frame is None:
                break
            
            # Show frame
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
from tracehold_widget import TraceHoldWidget  # Error jika path salah

# BENAR
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tracehold_widget"))
from tracehold_widget import TraceHoldWidget
```

### ❌ Tidak Handle Preview Window

```python
# SALAH
while True:
    frame, state = widget.get_frame()
    cv2.imshow('App', frame)
    # Preview window tidak di-draw!

# BENAR
while True:
    frame, state = widget.get_frame()
    cv2.imshow('App', frame)
    widget.draw_preview(frame)  # ✅ Draw preview jika aktif
```

---

## 🆘 Troubleshooting

### Widget tidak bisa di-import

```python
# Check struktur folder
import os
print(os.listdir('.'))
print(os.listdir('tracehold_widget'))

# Pastikan ada __init__.py di folder tracehold_widget
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
widget = TraceHoldWidget(camera_id=0)

if widget.cap is None or not widget.cap.isOpened():
    print("Camera not opened!")
    # Try different camera ID
    widget = TraceHoldWidget(camera_id=1)
```

### Preview window tidak muncul

```python
# Pastikan draw_preview dipanggil
while True:
    frame, state = widget.get_frame()
    cv2.imshow('Main', frame)
    widget.draw_preview(frame)  # ✅ Call ini!
    
    # Handle 'u' key
    if cv2.waitKey(1) & 0xFF == ord('u'):
        widget.toggle_preview()
```

### ROI box tidak berkedip biru

```python
# Check state
frame, state = widget.get_frame()
print(f"Object in ROI: {state.get('object_in_roi')}")
print(f"ROI occupied: {state.get('roi_occupied')}")
print(f"Blink state: {state.get('blink_state')}")

# Pastikan:
# 1. Ada object di depan kamera
# 2. Object masuk ke area ROI
# 3. Tunggu 3 frames (OBJECT_CONFIRM_THRESHOLD)
```

---

## 📚 Resources

- [TraceHold Widget README](README.md)
- [non_widget/main.py](non_widget/main.py) - Full reference
- [app.py](app.py) - Template lengkap

---

**Last Updated:** 2026-03-16
