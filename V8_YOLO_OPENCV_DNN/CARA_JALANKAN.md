# 🚀 CARA MENJALANKAN V8_YOLO_OPENCV_DNN

## ⚠️ PENTING: Download Model Dulu!

Aplikasi tidak bisa jalan tanpa model YOLO. Ikuti langkah ini:

---

## 📥 Step 1: Download Model YOLOv3-Tiny

### Option A: Pakai Script Otomatis (Recommended)

```powershell
cd D:\Github\sc_python_camera_paddleocr\V8_YOLO_OPENCV_DNN

# Jalankan script download
python setup_model.py
```

Script akan download otomatis. Tunggu sampai selesai (~34 MB).

---

### Option B: Download Manual (Jika Script Gagal)

**Cara 1: Pakai PowerShell**

```powershell
cd D:\Github\sc_python_camera_paddleocr\V8_YOLO_OPENCV_DNN

# Download dengan curl
curl -o yolov3-tiny.weights https://pjreddie.com/media/files/yolov3-tiny.weights
```

**Cara 2: Pakai Browser**

1. **Buka browser** (Chrome/Firefox/Edge)
2. **Kunjungi URL ini:**
   ```
   https://pjreddie.com/media/files/yolov3-tiny.weights
   ```
3. **Tunggu download selesai** (~34 MB)
4. **Pindahkan file** ke folder ini:
   ```
   D:\Github\sc_python_camera_paddleocr\V8_YOLO_OPENCV_DNN\yolov3-tiny.weights
   ```

---

## ✅ Step 2: Verify Download

Cek apakah file sudah benar:

```powershell
cd D:\Github\sc_python_camera_paddleocr\V8_YOLO_OPENCV_DNN

# Cek ukuran file
dir yolov3-tiny.weights
```

**Harusnya muncul:**
```
yolov3-tiny.weights    34,000,000 bytes (~34 MB)
```

**Jika < 1 MB atau 9 bytes, download gagal!** Ulangi Step 1.

---

## ▶️ Step 3: Jalankan Aplikasi

```powershell
cd D:\Github\sc_python_camera_paddleocr\V8_YOLO_OPENCV_DNN

# Jalankan aplikasi
python main.py
```

---

## 🎯 Yang Akan Terjadi:

### Console Output (Normal):
```
======================================================================
Object Distance Detection with YOLO - OpenCV DNN
======================================================================

✅ OpenCV DNN Backend (CPU rendah, ~20-30%)
✅ Migration from Ultralytics PyTorch
======================================================================

[⚡ PERFORMANCE MODE] LOW (Throttled - detect setiap 0.1 detik)
    Expected CPU Usage: ~20-30% (OpenCV DNN)

Loading YOLO model (OpenCV DNN)...
Found Darknet model: yolov3-tiny.cfg + yolov3-tiny.weights
[OK] YOLO detector loaded (OpenCV DNN)

[OK] Camera opened: 0
```

### Window Muncul:
- Window dengan **camera feed live**
- **Info panel** di kiri atas (FPS, Parking Session)
- **Legend** di pojok kiri bawah
- **Buttons** di pojok kanan bawah (L - LOOP, T - TAP)

---

## 🐛 Troubleshooting

### Error: "FileNotFoundError: yolov3-tiny.weights"

**Solusi:** File model belum didownload! Lihat **Step 1**.

---

### Error: "cv2.error: Transpose the weights is not implemented"

**Penyebab:** File weights corrupt/invalid (< 1 MB)

**Solusi:**
1. Delete file: `del yolov3-tiny.weights`
2. Download ulang (Step 1)
3. Pastikan ukuran ~34 MB

---

### Error: "Cannot open camera"

**Solusi:**
```powershell
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"

# Jika False, coba camera ID lain
# Edit .env, ganti CAMERA_ID=1
```

---

### CPU Masih 100%

**Check:**
1. PERFORMANCE_MODE di `.env` (harusnya `LOW`)
2. OpenCV version (harusnya 4.5+)

```powershell
# Check OpenCV version
python -c "import cv2; print(cv2.__version__)"
```

---

## 📊 Expected Performance

| Metric | Value |
|--------|-------|
| **CPU Usage** | 20-30% (LOW mode) |
| **Memory** | 200-500 MB |
| **FPS** | 15-20 FPS |
| **Detection Time** | ~200ms |

---

## 🎮 Keyboard Controls

| Key | Function |
|-----|----------|
| `Q` | Quit |
| `R` | Reset tracking |
| `S` | Save snapshot |
| `L` | LOOP DETECTOR (FASE 3) |
| `T` | TAP CARD (FASE 4) |
| `ENTER` | SELESAI (preview) |
| `+/-` | Confidence threshold |

---

## 📁 File Structure

```
V8_YOLO_OPENCV_DNN/
├── main.py                 ✅ Main application
├── yolo_detector.py        ✅ YOLO wrapper
├── yolov3-tiny.cfg         ✅ Config (~2 KB)
├── yolov3-tiny.weights     ⚠️ HARUS DOWNLOAD (~34 MB)
├── setup_model.py          ✅ Auto-download script
├── requirements.txt        ✅ Dependencies
├── .env                    ✅ Configuration
└── README.md               ✅ This file
```

---

## 🔗 Download Links

**Primary:**
- https://pjreddie.com/media/files/yolov3-tiny.weights

**Mirrors:**
- https://github.com/AlexeyAB/darknet/releases
- https://drive.google.com (search "yolov3-tiny.weights")

---

## ✅ Checklist

Sebelum run, pastikan:

- [ ] `yolov3-tiny.cfg` exists (~2 KB)
- [ ] `yolov3-tiny.weights` exists (~34 MB)
- [ ] Camera connected
- [ ] Dependencies installed (`pip install -r requirements.txt`)

---

**Happy Testing! 🚀**

CPU dijamin turun dari 100% → 20-30%!
