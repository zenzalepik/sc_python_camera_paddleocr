# 📱 Multiple Image OCR - PaddleOCR

Aplikasi OCR untuk multiple images dengan deteksi teks otomatis menggunakan PaddleOCR v5 Mobile.

---

## ✨ Fitur

- ✅ **Multiple Image Selection** - Pilih banyak gambar sekaligus
- ✅ **Batch Processing** - Process semua gambar dalam satu kali detect
- ✅ **Queue Tracking** - Status tracking (pending, processing, completed, failed)
- ✅ **Export Batch** - Export semua hasil ke TXT + JSON
- ✅ **Bounding Boxes** - Visualisasi hasil OCR pada gambar
- ✅ **License Plate Detection** - Deteksi plat nomor Indonesia
- ✅ **High Accuracy** - ~90% confidence rate
- ✅ **Fast Processing** - ~5 detik per image

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install paddlepaddle paddleocr opencv-python Pillow python-dotenv
```

### 2. Run Aplikasi

```bash
cd D:\Github\sc_python_camera_paddleocr\tes\import_paddleocr_multiple
python app.py
```

---

## 🎮 Cara Menggunakan

### **Step 1: Open Images**
- Klik **"Open"** atau tekan **'o'**
- Pilih multiple images (Ctrl+Click untuk select banyak)
- Klik **"Open"**

### **Step 2: Detect All**
- Klik **"Detect All"** atau tekan **'d'**
- Tunggu processing (~5 detik per image)
- Lihat hasil di panel

### **Step 3: Export**
- Klik **"Export"** atau tekan **'e'**
- Files tersimpan di `output/`:
  - `batch_YYYYMMDD_HHMMSS.txt`
  - `batch_YYYYMMDD_HHMMSS.json`

### **Step 4: Clear**
- Klik **"Clear"** atau tekan **'c'**
- Reset semua data

### **Quit**
- Tekan **'q'** atau **'ESC'**

---

## ⌨️ Keyboard Shortcuts

| Key | Function |
|-----|----------|
| `o` | Open images (multiple) |
| `d` | Detect all |
| `e` | Export results |
| `c` | Clear all |
| `q` / `ESC` | Quit |

---

## 📊 Layout UI

```
┌─────────────────────────────────────────────────────────┐
│           Multiple Image OCR                            │
│                   1280 x 700                            │
├──────────────────────┬──────────────────────────────────┤
│  LEFT (50%)          │  RIGHT (50%)                     │
│                      │                                  │
│  Selamat Datang     │  Image Preview                   │
│  ✓ Export Berhasil  │  (dengan bounding boxes)         │
│                      │                                  │
│  [Open] [Detect All]│                                  │
│  [Export] [Clear]   │                                  │
│                      │                                  │
│  Queue: 5 | ✓: 3    │                                  │
│                      │                                  │
│  Hasil Deteksi:     │                                  │
│  Image 1: doc.jpg   │                                  │
│  - Text 1 (0.95)    │                                  │
│  - Text 2 (0.87)    │                                  │
└──────────────────────┴──────────────────────────────────┘
```

---

## ⚙️ Configuration (.env)

```env
# OCR Settings
OCR_LANG=id                    # Language: id, en, ch, japan, korean
CONF_THRESHOLD=0.5             # Confidence threshold (0.0-1.0)

# Text Processing
DELETE_SPACE=True              # Remove spaces from text
GROUP_BY_LINE=True             # Group texts by horizontal line
LINE_TOLERANCE=10              # Pixel tolerance for line grouping

# License Plate Detection
DETECT_LICENSE_PLATE=True      # Enable Indonesian plate detection

# Output Settings
OUTPUT_DIR=output              # Output directory
```

---

## 📁 Output Format

### TXT Output
```
PaddleOCR Multiple Image Text Detection Result
============================================================

Image 1: Screenshot_2026-03-07_142543.png
Timestamp: 2026-03-18T17:29:27
Total Texts: 5
============================================================

[1] S
    Confidence: 0.8982

[2] 2470
    Confidence: 0.9860
```

### JSON Output
```json
{
  "batch_results": [
    {
      "texts": [
        {"text": "S", "confidence": 0.898, "bbox": [[...]]},
        {"text": "2470", "confidence": 0.986, "bbox": [[...]]}
      ],
      "total_texts": 5,
      "image_filename": "Screenshot_2026-03-07_142543.png"
    }
  ],
  "total_images": 1,
  "processed_count": 1
}
```

---

## 🔧 Troubleshooting

### File Dialog Tidak Muncul
- **Alt+Tab** setelah klik "Open"
- File dialog mungkin di belakang window OpenCV

### PaddleOCR Tidak Terinstall
```bash
pip install paddlepaddle paddleocr
```

### Error: Module Not Found
```bash
# Pastikan run dari folder yang benar
cd D:\Github\sc_python_camera_paddleocr\tes\import_paddleocr_multiple
python app.py
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Processing Speed** | ~5s per image |
| **Accuracy** | ~90% avg confidence |
| **Export Speed** | < 1s |
| **Supported Formats** | JPG, PNG, BMP, TIFF, WEBP |

---

## 📝 Test Images

Test image tersedia: `Screenshot_2026-03-07_142543.png`

---

**Created:** 2026-03-18  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
