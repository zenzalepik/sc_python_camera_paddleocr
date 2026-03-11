# PaddleOCR Mobile - Multiple Image Input

Aplikasi desktop untuk upload **multiple gambar** dengan PaddleOCR v5 Mobile untuk deteksi teks otomatis.

## Fitur

- ✅ **Multiple Image Input** - Upload beberapa gambar sekaligus
- ✅ **Batch Detection** - Deteksi teks semua gambar dalam sekali jalan
- ✅ **Grouped Results** - Hasil deteksi digruping berdasarkan gambar
- ✅ **GUI sederhana** dengan Tkinter
- ✅ **Preview gambar** per item
- ✅ **Deteksi teks otomatis** dengan PaddleOCR v5 Mobile
- ✅ **Tampilkan hasil teks** dengan confidence score
- ✅ **Export hasil** ke TXT/JSON
- ✅ **Copy hasil** ke clipboard

## Installation

```bash
cd V5_02_PaddleOCR_Multiple_Input
pip install -r requirements.txt
```

## Usage

### Run Application

```bash
python main.py
```

### Keyboard Shortcuts

- `Ctrl+O` - Add images
- `Ctrl+A` - Detect all images
- `Ctrl+D` - Detect selected image
- `Delete` - Remove selected image
- `Ctrl+BackSpace` - Clear all images

## Configuration

Edit `.env` untuk mengubah pengaturan:

```env
# Language: 'en' (English) atau 'id' (Indonesian)
OCR_LANG=en

# Confidence threshold (0.0 - 1.0)
CONF_THRESHOLD=0.5

# Delete all spaces from detected text
DELETE_SPACE=True

# Group text by horizontal lines
GROUP_BY_LINE=True

# Tolerance for grouping (pixels)
LINE_TOLERANCE=10
```

## How to Use

1. **Add Images**: Klik "Add Images" dan pilih beberapa gambar sekaligus
2. **Preview**: Klik gambar di list untuk melihat preview
3. **Detect**:
   - **Single**: Pilih gambar dan klik "Detect Text (Selected)"
   - **Batch**: Klik "Detect All Images" untuk deteksi semua gambar
4. **View Results**: Hasil ditampilkan di panel kanan, digruping per gambar
5. **Export**: Copy atau save hasil deteksi

## Screenshot

```
┌─────────────────────────────────────────────────────────────────┐
│  PaddleOCR Mobile - Multiple Image Detection                    │
├────────────┬─────────────────────┬──────────────────────────────┤
│ Image List │  Image Preview      │  Detected Text Results       │
│            │                     │                              │
│ 1. img1.jpg│                     │  Image 1: img1.jpg           │
│ 2. img2.jpg│   [Preview]         │  -------------------------   │
│ 3. img3.jpg│                     │    [1] ABC123                │
│            │                     │    [2] DEF456                │
│            │                     │                              │
│            │                     │  Image 2: img2.jpg           │
│            │                     │  -------------------------   │
│            │                     │    [1] XYZ789                │
│            │                     │                              │
├────────────┴─────────────────────┴──────────────────────────────┤
│  Status: Detected 5 text(s) from 3/3 images                     │
└─────────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.8+
- PaddlePaddle
- PaddleOCR
- OpenCV
- Pillow
- python-dotenv

## License

MIT License
