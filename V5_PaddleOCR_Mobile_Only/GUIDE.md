# 📱 PaddleOCR Mobile - Complete Guide

## 🎯 Overview

Aplikasi desktop untuk deteksi teks otomatis dari gambar menggunakan **PaddleOCR v5 Mobile**.

---

## 📦 Project Structure

```
V5_PaddleOCR_Mobile_Only/
├── app_gui.py            # Desktop GUI application (Tkinter)
├── main.py               # Command-line interface
├── test_ocr.py           # Quick test script
├── .env                  # Configuration file
├── requirements.txt      # Python dependencies
├── run.bat               # Windows runner
├── readme.md             # Documentation
└── output/               # Output directory (auto-created)
```

---

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- `paddlepaddle` - Deep learning framework
- `paddleocr` - OCR library
- `opencv-python` - Image processing
- `Pillow` - Image handling for GUI
- `python-dotenv` - Configuration

### 2. First Run

Pada pertama kali run, PaddleOCR akan otomatis download model:
- **PP-OCRv5_mobile_det** (~3MB) - Text detection
- **PP-OCRv5_mobile_rec** (~10MB) - Text recognition

Total download: ~13MB

---

## 💻 Usage

### Option 1: Desktop GUI (Recommended)

```bash
python app_gui.py
```

**Features:**
- 📁 Upload image (browse or drag & drop)
- 🔍 Detect text with one click
- 📋 Copy results to clipboard
- 💾 Save results to JSON/TXT
- 🗑️ Clear all

**Keyboard Shortcuts:**
- `Ctrl+O` - Upload image
- `Ctrl+D` - Detect text
- `Ctrl+C` - Copy results
- `Ctrl+S` - Save results
- `Delete` - Clear all

### Option 2: Command Line

**Single Image:**
```bash
python main.py image.jpg
```

**Batch Processing:**
```bash
python main.py image1.jpg image2.jpg image3.jpg
```

**With Options:**
```bash
python main.py --lang id image.jpg          # Indonesian language
python main.py --threshold 0.3 image.jpg    # Lower threshold
python main.py -o results image.jpg         # Custom output dir
```

### Option 3: Quick Test

```bash
python test_ocr.py
```

---

## ⚙️ Configuration

Edit `.env` file:

```env
# Language
OCR_LANG=en          # 'en' for English, 'id' for Indonesian

# Detection
CONF_THRESHOLD=0.5   # Minimum confidence (0.0-1.0)

# Output
OUTPUT_DIR=output    # Output directory
SAVE_RESULT=True     # Auto-save results
DRAW_BOX=True        # Draw bounding boxes
```

---

## 📊 Model Information

### PaddleOCR v5 Mobile Models

| Component | Model Name | Size | Purpose |
|-----------|-----------|------|---------|
| **Detection** | PP-OCRv5_mobile_det | ~3 MB | Detect text regions |
| **Recognition** | PP-OCRv5_mobile_rec | ~10 MB | Recognize text content |
| **Total** | - | **~13 MB** | Full OCR pipeline |

### Performance

| Metric | Value |
|--------|-------|
| **Inference Time** | ~100ms/image (CPU) |
| **Accuracy** | 95%+ for clear text |
| **Supported Languages** | 80+ languages |
| **Text Orientation** | Multi-direction support |

---

## 🌐 Supported Languages

PaddleOCR v5 supports 80+ languages:

- ✅ `en` - English
- ✅ `id` - Indonesian
- ✅ `ch` - Chinese (Simplified)
- ✅ `tw` - Chinese (Traditional)
- ✅ `japan` - Japanese
- ✅ `korean` - Korean
- ✅ `th` - Thai
- ✅ `vi` - Vietnamese
- ✅ `ar` - Arabic
- ✅ `hi` - Hindi
- ✅ And many more...

To use Indonesian:
```bash
python main.py --lang id image.jpg
```

Or edit `.env`:
```env
OCR_LANG=id
```

---

## 📁 Output Format

### JSON Output (`output/image_result.json`)

```json
{
  "texts": [
    {
      "text": "Hello World",
      "confidence": 0.95,
      "bbox": [[10, 10], [200, 10], [200, 50], [10, 50]]
    }
  ],
  "total_texts": 1,
  "processing_time": 0.123,
  "image_path": "image.jpg",
  "timestamp": "2026-03-04T14:30:25"
}
```

### TXT Output (`output/image_text.txt`)

```
PaddleOCR Text Detection Result
============================================================

Image: image.jpg
Timestamp: 2026-03-04T14:30:25
Processing Time: 0.123s
Total Texts: 1
============================================================

[1] Hello World
    Confidence: 0.95
```

### Image Output (`output/image_output.jpg`)

Image dengan bounding boxes dan teks hasil deteksi.

---

## 🎯 Use Cases

### 1. Document Digitization
```bash
python main.py scanned_document.jpg
```

### 2. Receipt Processing
```bash
python main.py receipt.jpg --lang id
```

### 3. Photo OCR
```bash
python main.py street_sign.jpg
```

### 4. ID Card Recognition
```bash
python main.py id_card.jpg --lang id
```

### 5. License Plate (Experimental)
```bash
python main.py license_plate.jpg --threshold 0.3
```

---

## 🔧 Troubleshooting

### Issue: PaddleOCR tidak terinstall
```
ModuleNotFoundError: No module named 'paddleocr'
```

**Solution:**
```bash
pip install paddlepaddle paddleocr
```

### Issue: Model download gagal
```
ConnectionError: Failed to download model
```

**Solution:**
- Pastikan internet aktif
- Download manual dari PaddlePaddle model zoo
- Set environment variable:
  ```env
  PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
  ```

### Issue: Out of memory
```
RuntimeError: CUDA out of memory
```

**Solution:**
- Gunakan image dengan resolusi lebih kecil
- Close other GPU applications
- Use CPU mode (default)

### Issue: Text tidak terdeteksi
```
No text detected
```

**Solutions:**
1. Turunkan confidence threshold:
   ```bash
   python main.py --threshold 0.3 image.jpg
   ```
2. Pastikan teks cukup besar dan jelas
3. Gunakan image dengan resolusi lebih tinggi
4. Coba language yang sesuai (en/id)

---

## 📝 Tips for Best Results

### 1. Image Quality
- ✅ High resolution (min 300 DPI for documents)
- ✅ Good lighting
- ✅ Clear, sharp text
- ❌ Avoid blurry images
- ❌ Avoid low contrast

### 2. Text Size
- ✅ Minimum text height: 20 pixels
- ✅ Optimal: 30-50 pixels
- ❌ Too small (<10px) may not be detected

### 3. Language Selection
- ✅ Use correct language for best accuracy
- ✅ English (`en`) for Latin alphabet
- ✅ Indonesian (`id`) for Bahasa Indonesia

### 4. Confidence Threshold
- ✅ Default (0.5) works for most cases
- ✅ Lower (0.3) for difficult images
- ✅ Higher (0.7) for high confidence only

---

## 🎨 GUI Features

### Main Window
- **Left Panel**: Image preview with drag & drop
- **Right Panel**: Detection results
- **Bottom**: Status bar and progress indicator

### Buttons
- **📁 Upload Image**: Browse and load image
- **🔍 Detect Text**: Run OCR detection
- **📋 Copy**: Copy results to clipboard
- **💾 Save**: Save results to file
- **🗑️ Clear**: Clear all data

---

## 📚 API Reference

### PaddleOCRDesktopApp

```python
app = PaddleOCRDesktopApp(root)

# Load image
app.load_image("image.jpg")

# Detect text
result = app.detect_text()

# Draw results
output_image = app.draw_result()

# Save results
app.save_result(result, "image.jpg")
```

### Command Line API

```bash
python main.py [options] <images>

Options:
  --lang, -l      Language (en/id) [default: en]
  --threshold, -t Confidence threshold [default: 0.5]
  --output-dir, -o Output directory [default: output]
  --no-save       Don't save results
```

---

## 🔗 Resources

- **PaddleOCR GitHub**: https://github.com/PaddlePaddle/PaddleOCR
- **PaddlePaddle Docs**: https://www.paddlepaddle.org.cn/
- **Documentation**: https://paddleocr.readthedocs.io/
- **Model Zoo**: https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/models_v2.md

---

## 📄 License

- **PaddleOCR**: Apache License 2.0
- **PaddlePaddle**: Apache License 2.0
- **This Project**: Apache License 2.0

---

## 🙏 Credits

Created with:
- PaddleOCR v5 by PaddlePaddle Team
- Tkinter for GUI
- OpenCV for image processing

---

**Created:** 2026-03-04  
**Version:** 1.0.0  
**Folder:** V5_PaddleOCR_Mobile_Only
