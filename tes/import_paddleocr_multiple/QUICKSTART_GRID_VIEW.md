# 🚀 Quick Start - Grid View Multiple Image OCR

## 📋 Cara Menjalankan

### **Option 1: Grid View (NEW - Recommended)**
```bash
cd D:\Github\sc_python_camera_paddleocr\tes\import_paddleocr_multiple
python app_grid.py
```

### **Option 2: Original View**
```bash
cd D:\Github\sc_python_camera_paddleocr\tes\import_paddleocr_multiple
python app.py
```

---

## 🎮 Quick Tutorial (5 Steps)

### **Step 1: Open Images**
```
1. Klik tombol "Open" (biru)
2. Select multiple images (Ctrl+Click)
3. Klik "Open"
```
✅ Grid menampilkan semua thumbnail

---

### **Step 2: Detect All**
```
Klik "Detect All" (hijau)
```
✅ Progress bar muncul  
✅ Status update: ○ → ⏳ → ✓  
✅ Text count muncul otomatis

---

### **Step 3: Navigate**
```
Klik thumbnail mana saja
```
✅ Detail panel menampilkan hasil  
✅ Thumbnail terpilih highlight kuning

---

### **Step 4: Export**
```
Klik "Export" (orange)
```
✅ Popup "✓ Export Berhasil!"  
✅ Files tersimpan di `output/`

---

### **Step 5: Clear**
```
Klik "Clear" (ungu)
```
✅ Semua data di-reset

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `o` | Open images |
| `d` | Detect all |
| `e` | Export |
| `c` | Clear |
| `q` atau `ESC` | Quit |

---

## 🎨 Layout Overview

```
┌──────────────────────────────────────────────┐
│ [Open][Detect All][Export][Clear] | Queue... │
├──────────────────────────────────────────────┤
│ ┌────┬────┬────┬────┬────┐                  │
│ │ #1 │ #2 │ #3 │ #4 │ #5 │ ← Grid Thumbnails│
│ └────┴────┴────┴────┴────┘                  │
├──────────────────────────────────────────────┤
│ Image #3: screenshot.png | Status: DONE      │
│ 1. TEXT ONE (0.95)                           │
│ 2. TEXT TWO (0.87)                           │
│ ...                                          │
└──────────────────────────────────────────────┘
```

---

## ✅ Status Icons

| Icon | Meaning | Color |
|------|---------|-------|
| ✓ | Completed | Green |
| ⏳ | Processing | Orange |
| ✗ | Failed | Red |
| ○ | Pending | Gray |

---

## 📁 Output Files

Setelah export, files tersimpan di:
```
output/
├── batch_20260319_HHMMSS.txt
└── batch_20260319_HHMMSS.json
```

---

## 🐛 Troubleshooting

### **Error: "btn_y is not defined"**
✅ **FIXED!** Sudah diperbaiki di versi terbaru.

### **App tidak muncul**
```bash
# Pastikan dependencies terinstall
pip install paddlepaddle paddleocr opencv-python Pillow python-dotenv
```

### **No images in queue**
- Klik "Open" dulu untuk select images
- File dialog akan muncul

### **Export failed**
- Pastikan sudah klik "Detect All" dulu
- Harus ada hasil detect untuk di-export

---

## 🎯 Tips

1. **Select banyak images**: Tahan `Ctrl` saat select di file dialog
2. **Quick navigation**: Klik thumbnail untuk ganti gambar
3. **Monitor progress**: Lihat progress bar di top
4. **Batch export**: Semua hasil di-export sekaligus

---

## 📊 Recommended Specs

| Item | Minimum | Recommended |
|------|---------|-------------|
| **Images** | 1-10 | 10-50 |
| **Image Size** | < 5MB | < 2MB |
| **RAM** | 4GB | 8GB+ |
| **Python** | 3.8+ | 3.10+ |

---

## 🆚 Grid View vs Original View

| Feature | Grid View | Original |
|---------|-----------|----------|
| **Layout** | 5-col grid | Split 50/50 |
| **Overview** | Semua gambar | 1 gambar |
| **Navigation** | Click thumbnail | Click list |
| **Best For** | 10-50 images | 1-10 images |
| **File** | `app_grid.py` | `app.py` |

---

## 🎊 Ready to Use!

**Pilih salah satu:**
- `python app_grid.py` ← Grid View (NEW!)
- `python app.py` ← Original View

**Selamat menggunakan!** 🚀

---

**Last Updated:** 2026-03-19  
**Version:** 3.0.1 (Grid View - Bug Fixed)
