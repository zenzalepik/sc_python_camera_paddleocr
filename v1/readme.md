# Live Camera OCR

Aplikasi live camera view dengan PaddleOCR untuk auto-detect teks.

## Cara Menjalankan

```powershell
# Aktifkan virtual environment
& d:\Github\sc_python_camera_paddleocr\ocr_env\Scripts\Activate.ps1

# Jalankan aplikasi
python main.py
```

## Kontrol

- **q** - Keluar dari aplikasi

## Konfigurasi (.env)

| Parameter | Default | Keterangan |
|-----------|---------|------------|
| CAMERA_WIDTH | 640 | Lebar resolusi kamera |
| CAMERA_HEIGHT | 480 | Tinggi resolusi kamera |
| OCR_INTERVAL | 5 | Proses OCR setiap N frame |
| PADDLE_LANG | en | Bahasa OCR (en/id) |
| PADDLE_USE_ANGLE_CLS | True | Gunakan klasifikasi sudut |
