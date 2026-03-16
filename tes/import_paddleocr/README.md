# PaddleOCR Widget - OCR Text Detection

Widget reusable untuk deteksi teks dengan PaddleOCR v5 Mobile.

---

## 📦 Struktur Folder

```
import_paddleocr/
├── app.py                    # Demo aplikasi menggunakan widget
├── paddleocr_widget/         # ✅ WIDGET REUSABLE
│   ├── __init__.py           # Module exports
│   ├── widget_wrapper.py     # Class PaddleOCRWidget
│   ├── main.py               # Standalone app (Tkinter GUI)
│   ├── GUIDE.md              # Dokumentasi lengkap
│   └── ...
└── README.md                 # Dokumentasi ini
```

---

## 🚀 Cara Menggunakan Widget di Project Lain

### Step 1: Copy Folder Widget

Copy seluruh folder `paddleocr_widget` ke project Anda:

```
your_project/
├── main.py           # Aplikasi Anda
└── paddleocr_widget/ # ← COPY folder ini
    ├── __init__.py
    ├── widget_wrapper.py
    ├── main.py
    └── ...
```

### Step 2: Import Widget

```python
from paddleocr_widget import PaddleOCRWidget
```

### Step 3: Buat Widget Instance

```python
# Basic usage
widget = PaddleOCRWidget()

# Dengan custom config
widget = PaddleOCRWidget(
    config={
        'OCR_LANG': 'id',              # Language: id, en, dll
        'CONF_THRESHOLD': 0.5,         # Confidence threshold
        'DELETE_SPACE': False,         # Hapus spasi
        'GROUP_BY_LINE': True,         # Group by line
        'LINE_TOLERANCE': 10,          # Line tolerance (pixels)
        'OUTPUT_DIR': 'output',        # Output directory
    }
)
```

### Step 4: Process Image

```python
# Option 1: Process dari file path
result = widget.process_image('path/to/image.jpg')

# Option 2: Process dari OpenCV frame
frame = cv2.imread('image.jpg')
frame_with_boxes, result = widget.process_frame(frame)
```

### Step 5: Get Result

```python
# Get full result dict
result = widget.get_result()
print(f"Detected {result['total_texts']} texts")

# Get texts only
texts = widget.get_texts()
for i, text in enumerate(texts, 1):
    print(f"[{i}] {text}")
```

### Step 6: Export Result

```python
# Export ke TXT
widget.export_to_txt('output.txt')

# Export ke JSON
widget.export_to_json('output.json')

# Copy ke clipboard
widget.copy_to_clipboard()
```

---

## 🎯 Contoh Lengkap

### Contoh 1: Basic OCR

```python
from paddleocr_widget import PaddleOCRWidget

widget = PaddleOCRWidget()

# Process image
result = widget.process_image('document.jpg')

# Print results
texts = widget.get_texts()
print(f"Detected {len(texts)} texts:")
for text in texts:
    print(f"  - {text}")

# Export
widget.export_to_txt('result.txt')
widget.export_to_json('result.json')
```

### Contoh 2: Dengan Custom Config

```python
from paddleocr_widget import PaddleOCRWidget

widget = PaddleOCRWidget(
    config={
        'OCR_LANG': 'en',
        'CONF_THRESHOLD': 0.7,
        'DELETE_SPACE': True,
        'GROUP_BY_LINE': True,
    }
)

result = widget.process_image('english_doc.png')
texts = widget.get_texts()
print(texts)
```

### Contoh 3: Draw Bounding Boxes

```python
from paddleocr_widget import PaddleOCRWidget
import cv2

widget = PaddleOCRWidget()

# Load image
image = cv2.imread('document.jpg')

# Process dan draw boxes
frame_with_boxes, result = widget.process_frame(image)

# Save result
cv2.imwrite('result_with_boxes.jpg', frame_with_boxes)
```

### Contoh 4: Batch Processing

```python
from paddleocr_widget import PaddleOCRWidget
import glob

widget = PaddleOCRWidget()

# Process multiple images
for image_path in glob.glob('images/*.jpg'):
    print(f"\nProcessing {image_path}...")
    result = widget.process_image(image_path)
    
    # Export per image
    widget.export_to_txt(f'output/{image_path}.txt')
    widget.clear_result()
```

### Contoh 5: Integration dengan GUI

```python
from paddleocr_widget import PaddleOCRWidget
import tkinter as tk
from tkinter import filedialog

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.widget = PaddleOCRWidget()
        
        # UI setup
        self.text_area = tk.Text(root)
        self.text_area.pack()
        
        open_btn = tk.Button(root, text="Open", command=self.open_image)
        open_btn.pack()
        
        detect_btn = tk.Button(root, text="Detect", command=self.detect)
        detect_btn.pack()
    
    def open_image(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.current_image = filepath
    
    def detect(self):
        if hasattr(self, 'current_image'):
            result = self.widget.process_image(self.current_image)
            texts = self.widget.get_texts()
            
            self.text_area.delete(1.0, tk.END)
            for text in texts:
                self.text_area.insert(tk.END, text + '\n')

root = tk.Tk()
app = OCRApp(root)
root.mainloop()
```

---

## 📖 API Reference

### Constructor

```python
widget = PaddleOCRWidget(
    config=None  # Optional config dict
)
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `process_image(image_path)` | Process image (path atau numpy array) | `result_dict` |
| `process_frame(frame)` | Process OpenCV frame | `(frame_with_boxes, result_dict)` |
| `get_result()` | Get full OCR result | `result_dict` |
| `get_texts()` | Get list of detected texts | `list[str]` |
| `draw_result(image)` | Draw bounding boxes | `image_with_boxes` |
| `export_to_txt(output_path)` | Export ke TXT file | `output_path` |
| `export_to_json(output_path)` | Export ke JSON file | `output_path` |
| `copy_to_clipboard()` | Copy hasil ke clipboard | `text` |
| `set_config(key, value)` | Set configuration | - |
| `clear_result()` | Clear current result | - |

### Result Dict Keys

```python
result = {
    'texts': [                      # List of detected texts
        {
            'text': 'Hello World',  # Detected text
            'confidence': 0.95,     # Confidence score
            'bbox': [[x1,y1], ...], # Bounding box (4 points)
            'original_text': '...', # Original text (before processing)
            'avg_y': 100.5,         # Average y-coordinate
            'x_min': 50,            # Minimum x-coordinate
            'is_grouped': False     # Whether text is grouped
        },
        ...
    ],
    'total_texts': 10,              # Total texts detected
    'total_lines': 5,               # Total lines (if group_by_line)
    'processing_time': 1.23,        # Processing time in seconds
    'image_path': 'path/to/img',    # Path to processed image
    'timestamp': '2026-03-16...'    # ISO timestamp
}
```

---

## ⚙️ Configuration

Default config bisa di-override via constructor:

```python
config = {
    'OCR_LANG': 'id',                   # Language: id, en, ch, dll
    'CONF_THRESHOLD': 0.5,              # Confidence threshold (0-1)
    'DELETE_SPACE': False,              # Delete spaces in text
    'GROUP_BY_LINE': False,             # Group texts by line
    'LINE_TOLERANCE': 10,               # Line tolerance (pixels)
    'HIDE_POPUP_UNKNOWN_EXCEPTION': False,  # Hide error popups
    'OUTPUT_DIR': 'output',             # Output directory
}

widget = PaddleOCRWidget(config=config)
```

### Supported Languages:

- `id` - Indonesian
- `en` - English
- `ch` - Chinese (simplified)
- `ja` - Japanese
- `ko` - Korean
- `fr` - French
- `de` - German
- `es` - Spanish
- Dan banyak lagi...

---

## 🎹 Keyboard Controls (di app.py)

| Key | Function |
|-----|----------|
| `o` | Open image |
| `d` | Detect text |
| `e` | Export result |
| `c` | Clear all |
| `q` / `ESC` | Quit |

---

## 📝 OCR Flow

```
1. Load Image → cv2.imread()
2. Initialize PaddleOCR → PP-OCRv5_mobile_det + rec
3. Run Prediction → ocr.predict(image)
4. Parse Result → Extract texts, scores, bboxes
5. Process Text → Delete space, group by line
6. Draw Boxes → Visualize on image
7. Export → TXT/JSON/Clipboard
```

---

## ✨ Fitur Utama

### 1. PaddleOCR v5 Mobile

- Model detection: PP-OCRv5_mobile_det
- Model recognition: PP-OCRv5_mobile_rec
- Fast dan akurat untuk mobile/edge devices

### 2. Multi-Language Support

- Support 80+ languages
- Easy switch dengan config `OCR_LANG`

### 3. Bounding Box Visualization

- Green boxes pada detected text
- Label dengan text dan confidence
- 4-point polygon untuk rotated text

### 4. Text Processing Options

- **Delete Space**: Remove spaces from text
- **Group by Line**: Merge texts on same line
- **Line Tolerance**: Pixel tolerance for grouping

### 5. Export Options

- **TXT**: Plain text dengan confidence
- **JSON**: Full result dengan bbox
- **Clipboard**: Copy texts untuk paste

---

## ⚠️ Troubleshooting

### Error: PaddleOCR tidak terinstall

```bash
# Install dependencies
pip install paddlepaddle paddleocr

# Untuk GPU
pip install paddlepaddle-gpu paddleocr
```

### Error: Model tidak ditemukan

```python
# Set environment variable
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

# Atau check internet connection (model download otomatis)
```

### Error: Tidak ada teks terdeteksi

```python
# Lower confidence threshold
widget = PaddleOCRWidget(config={'CONF_THRESHOLD': 0.3})

# Check image quality (resolution, contrast, dll)
```

### Error: Group by line tidak akurat

```python
# Adjust line tolerance
widget = PaddleOCRWidget(config={'LINE_TOLERANCE': 15})
```

---

## 📄 License

Widget ini adalah refactored version dari `paddleocr_widget/main.py`.

---

## 🆘 Support

Untuk contoh lengkap, lihat file `main.py` (standalone Tkinter app) atau `app.py` (OpenCV demo).

**Quick Start:**
```bash
python app.py
```

**Controls:**
- `o` - Open image
- `d` - Detect text
- `e` - Export result
- `c` - Clear all
- `q` - Quit

---

**Last Updated:** 2026-03-16
