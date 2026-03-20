# 📋 Terminal Logging Guide

Panduan lengkap untuk logging terminal pada setiap tombol di Multiple Image OCR App.

---

## 🎯 Logging Overview

Setiap tombol sekarang memiliki **logging terminal yang lengkap dan komprehensif** untuk memudahkan debugging dan monitoring.

---

## 📝 Log Format per Tombol

### 1️⃣ OPEN BUTTON

```
======================================================================
  [OPEN] OPEN BUTTON CLICKED
======================================================================
[OPEN] Timestamp: 2026-03-19 10:30:45
[OPEN] Current queue size: 0
[OPEN] Preparing file dialog...
[OPEN] Showing file dialog...
[OPEN] Supported formats: JPG, JPEG, PNG, BMP, TIFF, WEBP
[OPEN] Files selected: 3

[OPEN] File list:
  [1] image1.png (1024.5 KB)
      Path: C:\path\to\image1.png
  [2] image2.png (2048.3 KB)
      Path: C:\path\to\image2.png
  [3] image3.png (512.1 KB)
      Path: C:\path\to\image3.png

[OPEN] Adding 3 images to queue...
[OPEN] Set preview to image #1
[OK] Added 3 images to queue
[OK] New queue size: 3
[OK] Queue status: 3 pending
======================================================================
```

**Informasi yang dicatat:**
- ✅ Timestamp
- ✅ Queue size sebelum/sesudah
- ✅ List files yang dipilih (nama, size, path)
- ✅ Status queue update
- ✅ Preview image yang di-set

---

### 2️⃣ DETECT ALL BUTTON

```
======================================================================
  [DETECT] DETECT ALL BUTTON CLICKED
======================================================================
[DETECT] Timestamp: 2026-03-19 10:31:00
[DETECT] Queue information:
  - Total images: 3
  - Pending: 3
  - Completed: 0
  - Failed: 0
[DETECT] Clearing previous results...
[DETECT] Previous results cleared
[DETECT] Setting state flags...
  - ocr_processing: True
  - ocr_complete: False
  - is_loading: True
[DETECT] Starting batch processing...
  - Images to process: 3
  - Estimated time: ~15 seconds (3 images × ~5s each)
[OK] OCR thread started (ID: 12345)
[OK] Processing in background...
======================================================================
```

**Informasi yang dicatat:**
- ✅ Timestamp
- ✅ Queue info (total, pending, completed, failed)
- ✅ State flags
- ✅ Estimasi waktu processing
- ✅ Thread ID

---

### 3️⃣ OCR THREAD (Background Processing)

```
======================================================================
  [THREAD 12345] OCR PROCESSING STARTED
======================================================================
[THREAD] Thread ID: 12345
[THREAD] Started at: 2026-03-19 10:31:00
[THREAD] Images to process: 3
======================================================================

[THREAD] Calling widget.process_all()...

[BATCH] Processing 3 images...
============================================================
[1/3] Processing: image1.png
  [OK] Detected 5 texts
[2/3] Processing: image2.png
  [OK] Detected 3 texts
[3/3] Processing: image3.png
  [OK] Detected 7 texts
============================================================
[BATCH] Complete! Success: 3, Failed: 0

[THREAD] Processing complete!
[THREAD] Total results: 3
[THREAD] Setting preview to first completed image...
[THREAD] Set preview to image #1: image1.png

======================================================================
[THREAD] BATCH PROCESSING RESULTS
======================================================================

[SUMMARY] Processing Summary:
  - Total images: 3
  - Completed: 3 ✓
  - Failed: 0 ✗
  - Success rate: 100.0%

[RESULTS] Per-image Results:
  [1] image1.png ✓
      - Texts detected: 5
  [2] image2.png ✓
      - Texts detected: 3
  [3] image3.png ✓
      - Texts detected: 7

[SUCCESS] Batch processing complete!
======================================================================

======================================================================
[THREAD 12345] CLEANUP
======================================================================
[THREAD] Elapsed time: 15.23s
[THREAD] Setting flags:
  - is_loading: False
  - ocr_processing: False
  - cooldown_complete: True
[THREAD] Ready for next operation
======================================================================
```

**Informasi yang dicatat:**
- ✅ Thread ID & timestamp
- ✅ Progress per image
- ✅ Texts detected per image
- ✅ Summary (completed, failed, success rate)
- ✅ Per-image results detail
- ✅ Elapsed time
- ✅ Flag cleanup

---

### 4️⃣ EXPORT BUTTON

```
======================================================================
  [EXPORT] EXPORT BUTTON CLICKED
======================================================================
[EXPORT] Timestamp: 2026-03-19 10:31:20
[EXPORT] Analyzing data...
[EXPORT] Data available:
  - Total images processed: 3
  - Total texts detected: 15
  - License plates detected: 1
[EXPORT] Images to export:
  [1] image1.png
      - Texts: 5
  [2] image2.png
      - Texts: 3
  [3] image3.png
      - Texts: 7
      - Plate: B 1234 CD
[EXPORT] Exporting batch results...
[EXPORT] Formats: TXT + JSON
[OK] Export successful!
[OK] Files created:
  ✓ TXT: output\batch_20260319_103120.txt
      Size: 1,234 bytes (1.2 KB)
  ✓ JSON: output\batch_20260319_103120.json
      Size: 5,678 bytes (5.5 KB)
[EXPORT] Export completed successfully
[EXPORT] Files saved to: output/
======================================================================
```

**Informasi yang dicatat:**
- ✅ Timestamp
- ✅ Data summary (images, texts, plates)
- ✅ Per-image detail
- ✅ Export file paths
- ✅ File sizes (bytes + KB)
- ✅ Success/failure status

---

### 5️⃣ CLEAR BUTTON

```
======================================================================
  [CLEAR] CLEAR BUTTON CLICKED
======================================================================
[CLEAR] Timestamp: 2026-03-19 10:31:30
[CLEAR] Current state:
  - Images in queue: 3
  - Completed: 3
  - Pending: 0
  - Current result texts: 5
[CLEAR] Clearing all data...
[CLEAR] Clearing widget queue...
[CLEAR] Clearing app state...
[CLEAR] Resetting flags...
  - images_loaded: False
  - ocr_processing: False
  - ocr_complete: False
  - cooldown_complete: True
[CLEAR] Verifying clear...
[CLEAR] Final queue size: 0
[OK] All data cleared successfully
[CLEAR] Ready for new operation
======================================================================
```

**Informasi yang dicatat:**
- ✅ Timestamp
- ✅ Current state (queue, completed, pending)
- ✅ Clearing process
- ✅ Flag reset
- ✅ Verification (final queue size)
- ✅ Ready status

---

## 🔍 Error Logging

### Error pada OPEN
```
[OPEN] No files selected (user canceled)
======================================================================
```

### Error pada DETECT
```
[WARNING] No images in queue!
[WARNING] Please click 'Open' first to add images
======================================================================
```

### Error pada EXPORT
```
[ERROR] Export failed!
[ERROR] Error: [detail error]
[ERROR] Traceback: [stack trace]
======================================================================
```

### Error pada THREAD
```
======================================================================
[THREAD 12345] [ERROR] OCR FAILED!
======================================================================
[ERROR] Error type: Exception
[ERROR] Error message: [detail]
[ERROR] Traceback:
[stack trace lengkap]
======================================================================
```

---

## 📊 Log Analysis

### Cara Membaca Log:

1. **Header** - Menandai awal operasi
   ```
   ======================================================================
     [BUTTON] OPERATION NAME
   ======================================================================
   ```

2. **Timestamp** - Waktu operasi dimulai
   ```
   [BUTTON] Timestamp: YYYY-MM-DD HH:MM:SS
   ```

3. **Status Info** - Informasi state sebelum operasi
   ```
   - Queue size, flags, dll
   ```

4. **Process** - Detail eksekusi
   ```
   - Steps yang dilakukan
   - Progress
   ```

5. **Result** - Hasil operasi
   ```
   - Success/failure
   - Output detail
   ```

6. **Footer** - Penutup operasi
   ```
   ======================================================================
   ```

---

## 🎯 Use Cases

### Debugging:
- Check timestamp untuk track waktu operasi
- Lihat error messages dan traceback
- Monitor queue status

### Performance Monitoring:
- Track elapsed time pada thread
- Monitor success rate
- Check processing speed

### Audit Trail:
- Track semua operasi user
- Monitor file yang diproses
- Record export history

---

## 💡 Tips

1. **Simpan log** untuk debugging:
   ```bash
   python app.py > log_$(date +%Y%m%d_%H%M%S).txt 2>&1
   ```

2. **Monitor real-time** dengan tail (Linux/Mac):
   ```bash
   python app.py | tee -a app.log
   ```

3. **Search errors** di log:
   ```bash
   grep "ERROR" app.log
   grep "WARNING" app.log
   ```

---

## 📁 Log File Example

Untuk menyimpan log ke file:

```bash
# Windows PowerShell
python app.py > output\app_log_$(Get-Date -Format "yyyyMMdd_HHmmss").txt 2>&1

# Linux/Mac
python app.py > output/app_log_$(date +%Y%m%d_%H%M%S).txt 2>&1
```

---

**Last Updated:** 2026-03-19  
**Version:** 2.1.0 (dengan comprehensive logging)
