# 📋 Cara Menggunakan Template app.py

Panduan lengkap cara menggunakan dan memodifikasi template `app.py` untuk project Anda, serta cara memasang PaddleOCR Widget.

---

## 🎯 Struktur Template app.py

Template `app.py` saat ini memiliki struktur:

```
┌─────────────────────────────────────────────────────────┐
│           Aplikasi Python - PaddleOCR Widget            │
│                   Window: 1280 x 700                    │
├──────────────────────────────┬──────────────────────────┤
│                              │                          │
│   FRAME KIRI (50%)           │   FRAME KANAN (50%)      │
│   - Teks "Selamat Datang"    │   - PaddleOCR Widget     │
│   - 4 Tombol horizontal      │   - Image preview        │
│                              │   - Bounding boxes       │
│                              │   - OCR results          │
│                              │                          │
└──────────────────────────────┴──────────────────────────┘
```

---

## 📦 Step-by-Step Memasang Widget ke app.py

### Step 1: Import Widget

```python
import sys
import os

# Tambahkan path ke paddleocr_widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_widget"))

# Import widget
from paddleocr_widget import PaddleOCRWidget
```

### Step 2: Inisialisasi Widget di Class

```python
class ResponsiveApp:
    def __init__(self, window_width=1280, window_height=700):
        self.window_width = window_width
        self.window_height = window_height
        
        # ✅ INIT WIDGET DI SINI
        self.widget = PaddleOCRWidget()
        self.current_image = None
```

### Step 3: Open Image

```python
def open_image(self):
    """Open file dialog untuk pilih gambar."""
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()
    
    filepath = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image files", "*.jpg *.png *.bmp")]
    )
    
    if filepath:
        self.current_image = cv2.imread(filepath)
        self.current_image_path = filepath
```

### Step 4: Process Image

```python
def detect_text(self):
    """Detect text dalam gambar."""
    if self.current_image is None:
        print("No image loaded!")
        return
    
    # Process dengan widget
    frame_with_boxes, result = self.widget.process_frame(self.current_image)
    
    # Update image dengan bounding boxes
    self.current_image = frame_with_boxes
    
    # Get results
    texts = self.widget.get_texts()
    print(f"Detected {len(texts)} texts")
```

---

## 🎨 Kustomisasi Layout

### Opsi 1: Full Screen Image (Tanpa Split)

```python
def run(self):
    widget = PaddleOCRWidget()
    
    cv2.namedWindow('OCR', cv2.WINDOW_NORMAL)
    
    while True:
        # Open image
        if self.open_image():
            # Process
            frame_with_boxes, result = widget.process_frame(self.current_image)
            
            # Show full screen
            cv2.imshow('OCR', frame_with_boxes)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    widget.clear_result()
    cv2.destroyAllWindows()
```

### Opsi 2: Split Screen Custom

```python
def draw(self, frame, ocr_frame=None):
    height, width = frame.shape[:2]
    
    # Custom split: 30% kiri (controls), 70% kanan (image)
    left_width = int(width * 0.3)
    
    # Frame kiri (controls)
    left_frame = frame[:, :left_width]
    left_frame[:] = 255  # White background
    
    # Draw buttons di kiri
    # ...
    
    # Frame kanan (70%) - OCR output
    if ocr_frame is not None:
        ocr_resized = cv2.resize(ocr_frame, (width - left_width, height))
        frame[:, left_width:] = ocr_resized
    
    return frame
```

### Opsi 3: Side-by-Side Comparison

```python
def draw_comparison(self, original, processed):
    """Display original dan processed side-by-side."""
    # Resize to same height
    h = 700
    w1 = int(original.shape[1] * h / original.shape[0])
    w2 = int(processed.shape[1] * h / processed.shape[0])
    
    original_resized = cv2.resize(original, (w1, h))
    processed_resized = cv2.resize(processed, (w2, h))
    
    # Concatenate horizontally
    combined = np.hstack([original_resized, processed_resized])
    
    # Add labels
    cv2.putText(combined, "Original", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(combined, "OCR Result", (w1 + 10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return combined
```

---

## 🔧 Kustomisasi Widget Config

### Contoh 1: English OCR

```python
self.widget = PaddleOCRWidget(
    config={
        'OCR_LANG': 'en',
    }
)
```

### Contoh 2: High Confidence Threshold

```python
self.widget = PaddleOCRWidget(
    config={
        'CONF_THRESHOLD': 0.8,  # Hanya text dengan confidence > 80%
    }
)
```

### Contoh 3: Group by Line

```python
self.widget = PaddleOCRWidget(
    config={
        'GROUP_BY_LINE': True,
        'LINE_TOLERANCE': 15,  # Pixels tolerance
    }
)
```

### Contoh 4: Delete Spaces

```python
self.widget = PaddleOCRWidget(
    config={
        'DELETE_SPACE': True,  # Remove all spaces
    }
)
```

### Contoh 5: Custom Output Directory

```python
self.widget = PaddleOCRWidget(
    config={
        'OUTPUT_DIR': 'my_outputs',
    }
)
```

---

## 📊 Mengakses Result untuk Custom Logic

### Contoh 1: Filter Text by Confidence

```python
def detect_text(self):
    frame_with_boxes, result = self.widget.process_frame(self.current_image)
    
    # Filter high confidence texts
    high_conf_texts = [
        t for t in result['texts']
        if t['confidence'] > 0.9
    ]
    
    print(f"High confidence texts: {len(high_conf_texts)}")
    for text in high_conf_texts:
        print(f"  {text['text']} ({text['confidence']:.2f})")
```

### Contoh 2: Extract Specific Pattern

```python
import re

def detect_text(self):
    frame_with_boxes, result = self.widget.process_frame(self.current_image)
    
    texts = self.widget.get_texts()
    
    # Extract emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' '.join(texts))
    print(f"Found {len(emails)} emails: {emails}")
    
    # Extract phone numbers
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', ' '.join(texts))
    print(f"Found {len(phones)} phone numbers: {phones}")
```

### Contoh 3: Save to Database

```python
import sqlite3

def detect_text(self):
    frame_with_boxes, result = self.widget.process_frame(self.current_image)
    
    # Connect to DB
    conn = sqlite3.connect('ocr_results.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocr_results (
            id INTEGER PRIMARY KEY,
            text TEXT,
            confidence REAL,
            image_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert results
    for item in result['texts']:
        cursor.execute(
            'INSERT INTO ocr_results (text, confidence, image_path) VALUES (?, ?, ?)',
            (item['text'], item['confidence'], self.current_image_path)
        )
    
    conn.commit()
    conn.close()
    
    print(f"Saved {result['total_texts']} results to database")
```

---

## 🎨 Custom UI Elements

### Menambahkan Result Panel

```python
def draw_result_panel(self, frame, y_offset=0):
    """Draw result panel di bawah image."""
    if self.widget.current_result is None:
        return
    
    texts = self.widget.get_texts()
    
    # Draw text list
    y = 50 + y_offset
    for i, text in enumerate(texts[:10], 1):  # Show first 10
        label = f"{i}. {text}"
        cv2.putText(frame, label, (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y += 25
```

### Menambahkan Progress Bar

```python
def draw_progress(self, frame, progress=0):
    """Draw progress bar."""
    bar_width = 200
    bar_height = 20
    x, y = 10, frame.shape[0] - 50
    
    # Background
    cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                 (128, 128, 128), -1)
    
    # Progress
    filled_width = int(bar_width * progress / 100)
    cv2.rectangle(frame, (x, y), (x + filled_width, y + bar_height),
                 (0, 255, 0), -1)
    
    # Text
    cv2.putText(frame, f"{progress}%", (x + bar_width + 10, y + 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
```

---

## 📝 Template Lengkap app.py (Minimal)

```python
from paddleocr_widget import PaddleOCRWidget
import cv2

def main():
    # Init widget
    widget = PaddleOCRWidget()
    
    # Create window
    cv2.namedWindow('OCR', cv2.WINDOW_NORMAL)
    
    while True:
        # Open image (press 'o')
        # ... file dialog code ...
        
        # Process
        frame, result = widget.process_frame(image)
        
        # Show
        cv2.imshow('OCR', frame)
        
        # Handle keyboard
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            widget.export_to_txt('output.txt')
    
    widget.clear_result()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```

---

## ⚠️ Common Mistakes

### ❌ Tidak Initialize Widget

```python
# SALAH
widget = PaddleOCRWidget  # Missing ()

# BENAR
widget = PaddleOCRWidget()  # ✅ Call constructor
```

### ❌ Tidak Check Image Loaded

```python
# SALAH
result = widget.process_image(image_path)  # Error jika file tidak ada!

# BENAR
if os.path.exists(image_path):
    result = widget.process_image(image_path)
else:
    print("File not found!")
```

### ❌ Tidak Clear Result

```python
# SALAH
while True:
    widget.process_image(image1)
    widget.process_image(image2)  # Result tertumpuk!

# BENAR
while True:
    widget.clear_result()
    widget.process_image(image1)
```

### ❌ Tidak Handle Exception

```python
# SALAH
result = widget.process_image(image)  # Bisa crash!

# BENAR
try:
    result = widget.process_image(image)
except Exception as e:
    print(f"OCR failed: {e}")
```

---

## 🆘 Troubleshooting

### Widget tidak bisa di-import

```python
# Pastikan folder paddleocr_widget sejajar dengan script Anda
# Atau tambahkan ke path:
import sys
sys.path.insert(0, '/path/to/paddleocr_widget')
from paddleocr_widget import PaddleOCRWidget
```

### PaddleOCR tidak terinstall

```bash
# Install dependencies
pip install paddlepaddle paddleocr

# Untuk GPU
pip install paddlepaddle-gpu paddleocr
```

### Model tidak ditemukan

```python
# Set environment variable
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

# Atau check internet connection (model download otomatis)
```

### OCR result kosong

```python
# Check confidence threshold
widget = PaddleOCRWidget(config={'CONF_THRESHOLD': 0.3})

# Check image quality
print(f"Image shape: {image.shape}")
print(f"Image dtype: {image.dtype}")
```

---

## 📚 Resources

- [PaddleOCR Widget README](README.md)
- [paddleocr_widget/main.py](paddleocr_widget/main.py) - Full Tkinter app
- [app.py](app.py) - OpenCV demo

---

**Last Updated:** 2026-03-16
