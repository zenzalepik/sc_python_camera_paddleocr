# PaddleOCR Mobile - Text Detection

Aplikasi desktop sederhana untuk deteksi teks otomatis dari gambar menggunakan PaddleOCR v5 Mobile.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Application

```bash
python main.py
```

atau double-click `run.bat`

## Usage

1. **Run aplikasi** - `python main.py`
2. **Click "Open Image"** - Pilih gambar dari file picker
3. **Click "Detect Text"** - Deteksi teks otomatis
4. **View Results** - Lihat hasil deteksi di panel kanan
5. **Copy/Save** - Copy ke clipboard atau save ke file

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Image |
| `Ctrl+D` | Detect Text |
| `Ctrl+C` | Copy Results |
| `Ctrl+S` | Save Results |
| `Delete` | Clear All |

## Configuration

Edit `.env` file:

```env
OCR_LANG=en          # Language (en/id)
CONF_THRESHOLD=0.5   # Minimum confidence
OUTPUT_DIR=output    # Output directory
```

## Output

Results auto-saved ke folder `output/`:
- `*_result.json` - Full JSON result
- `*_text.txt` - Text summary
- `*_output.jpg` - Image dengan bounding boxes

## Features

- Simple GUI dengan Tkinter
- File picker untuk pilih gambar
- PaddleOCR v5 Mobile (~10MB model)
- Multi-bahasa (EN/ID)
- Real-time detection (~100ms)
- Export ke JSON/TXT
- Copy to clipboard

## Requirements

- Python 3.8+
- paddlepaddle
- paddleocr
- opencv-python
- Pillow
- python-dotenv

## License

Apache License 2.0

---

**Created:** 2026-03-04
**Version:** 1.0.0
