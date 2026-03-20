# 📱 PaddleOCR Mobile - Text Detection App

Aplikasi desktop untuk deteksi teks otomatis dari gambar menggunakan **PaddleOCR v5 Mobile**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PaddleOCR](https://img.shields.io/badge/PaddleOCR-v5.0-green.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

---

## ✨ Fitur

- ✅ **GUI Desktop Sederhana** - Mudah digunakan dengan Tkinter
- ✅ **Drag & Drop** - Upload gambar dengan drag & drop
- ✅ **PaddleOCR v5 Mobile** - Ringan dan cepat (~10MB model)
- ✅ **Multi-Bahasa** - Support Bahasa Indonesia & English
- ✅ **Real-time Detection** - Deteksi teks dalam ~100ms
- ✅ **Export Results** - Simpan hasil ke JSON/TXT
- ✅ **Copy to Clipboard** - Copy teks terdeteksi dengan 1 klik
- ✅ **Batch Processing** - Process multiple images (CLI version)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Application

**Option 1: GUI Desktop App (Recommended)**
```bash
python app_gui.py
```

**Option 2: Command Line**
```bash
python main.py image.jpg
```

**Option 3: Double-click**
```
run.bat
```

---

## 📖 Usage

### GUI Desktop App

1. **Upload Gambar**
   - Klik tombol "📁 Upload Image", atau
   - Drag & drop gambar ke area preview

2. **Detect Text**
   - Klik tombol "🔍 Detect Text"
   - Tunggu beberapa detik

3. **View Results**
   - Teks terdeteksi akan muncul di panel kanan
   - Confidence score ditampilkan untuk setiap teks

4. **Export/Copy**
   - "📋 Copy" - Copy teks ke clipboard
   - "💾 Save" - Save hasil ke file JSON/TXT
   - "🗑️ Clear" - Clear semua data

### Command Line

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
python main.py --lang id --gpu image.jpg
python main.py --threshold 0.3 image.jpg
python main.py -o results image.jpg
```

---

## ⚙️ Configuration

Edit file `.env` untuk customize:

```env
# Language: 'en' (English) or 'id' (Indonesian)
OCR_LANG=en

# Use GPU for inference
USE_GPU=False

# Confidence threshold (0.0 - 1.0)
CONF_THRESHOLD=0.5

# Output directory
OUTPUT_DIR=output
```

---

## 📊 Model Information

### PaddleOCR v5 Mobile

| Component | Model | Size |
|-----------|-------|------|
| **Detection** | PP-OCRv5_mobile_det | ~2.5 MB |
| **Recognition** | PP-OCRv5_mobile_rec | ~5.5 MB |
| **Classification** | PP-OCRv5_mobile_cls | ~1.5 MB |
| **Total** | - | **~10 MB** |

### Performance

| Device | Speed | Accuracy |
|--------|-------|----------|
| **CPU** | ~100ms/image | Good |
| **GPU** | ~30ms/image | Good |

### Supported Languages

- ✅ English (`en`)
- ✅ Indonesian (`id`)
- ✅ Chinese (`ch`)
- ✅ Japanese (`japan`)
- ✅ Korean (`korean`)
- ✅ And 80+ more languages

---

## 🎯 Use Cases

- 📄 **Document Digitization** - Extract text from scanned documents
- 📸 **Photo OCR** - Extract text from photos
- 🎫 **Receipt Processing** - Extract information from receipts
- 🪪 **ID Card Recognition** - Extract data from ID cards
- 🚗 **License Plate Recognition** - Extract plate numbers
- 📦 **Package Label Reading** - Extract shipping information

---

## 📁 Output Format

### JSON Output
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

### TXT Output
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

---

## 🔧 Troubleshooting

### PaddleOCR tidak terinstall
```bash
pip install paddlepaddle paddleocr
```

### CUDA/GPU Error
```env
USE_GPU=False  # Fallback ke CPU
```

### Model tidak terdownload
- Pastikan internet aktif
- Download manual dari PaddlePaddle model zoo

### Out of Memory
- Gunakan image dengan resolusi lebih kecil
- Disable GPU jika VRAM terbatas

---

## 📝 Examples

### Example 1: English Text
```bash
python main.py --lang en english_document.jpg
```

### Example 2: Indonesian Text
```bash
python main.py --lang id dokumen_indonesia.jpg
```

### Example 3: Low Quality Image
```bash
python main.py --threshold 0.3 blurry_image.jpg
```

### Example 4: GPU Acceleration
```bash
python main.py --gpu large_document.jpg
```

---

## 🎨 Keyboard Shortcuts (GUI)

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Upload Image |
| `Ctrl+D` | Detect Text |
| `Ctrl+C` | Copy Results |
| `Ctrl+S` | Save Results |
| `Delete` | Clear All |

---

## 📦 Requirements

- **Python:** 3.8+
- **OS:** Windows, Linux, macOS
- **GPU (Optional):** NVIDIA GPU with CUDA support

### Dependencies
```
paddlepaddle>=2.5.0
paddleocr>=2.7.0
opencv-python>=4.8.0
Pillow>=10.0.0
python-dotenv>=1.0.0
```

---

## 📚 Documentation

- **PaddleOCR:** https://github.com/PaddlePaddle/PaddleOCR
- **PaddlePaddle:** https://www.paddlepaddle.org.cn/
- **Documentation:** https://paddleocr.readthedocs.io/

---

## 📄 License

This project uses:
- **PaddleOCR** - Apache License 2.0
- **PaddlePaddle** - Apache License 2.0

---

## 🙏 Acknowledgments

- **PaddlePaddle Team** - For the amazing OCR library
- **Ultralytics** - For inspiration

---

**Created:** 2026-03-04  
**Version:** 1.0.0  
**Folder:** V5_PaddleOCR_Mobile_Only
