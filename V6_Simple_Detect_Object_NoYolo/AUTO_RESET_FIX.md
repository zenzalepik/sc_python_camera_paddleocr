# Auto Reset Logic Fix

## Masalah yang Ditemukan

### Gejala:
- Kotak ROI masih berkedip-kedip (blinking) tanpa sebab yang jelas
- Tidak ada object masuk di area ROI
- Tidak ada bounding box hijau terdeteksi (baik di dalam atau di luar ROI)

### Penyebab:
Logic state management sebelumnya tidak mereset indikator dengan benar ketika tidak ada object terdeteksi. Variabel `indicator_on` dan `blink_state` bisa tetap `True` meskipun tidak ada `has_green_box`.

## Solusi yang Diterapkan

### 1. Auto Reset Logic (Line ~233-257)
```python
if auto_reset_state:
    if not has_green_box:
        no_motion_frames += 1
        
        if no_motion_frames >= NO_MOTION_THRESHOLD:
            # RESET background reference
            background_reference = blurred.copy()
            no_motion_frames = 0
            
            # NEW: Reset indikator saat auto-reset
            indicator_on = False
            blink_state = False
            object_present = False
            print(f"[AUTO RESET] Background base updated - frame {frame_count}")
    else:
        no_motion_frames = 0
```

**Penambahan:** Reset indikator (`indicator_on`, `blink_state`, `object_present`) saat auto-reset terjadi.

### 2. State Management Logic (Line ~259-295)
Logic baru yang lebih sederhana dan eksplisit:

```python
# === STATE MANAGEMENT untuk ROI INDIKATOR ===
# Logic sederhana:
# - Jika object_in_roi = True → indikator berkedip
# - Jika object_in_roi = False → indikator mati (tidak berkedip)

# Reset semua counter jika tidak ada object hijau terdeteksi sama sekali
if not has_green_box:
    # Tidak ada object sama sekali → matikan indikator
    object_detected_frames = 0
    object_lost_frames = 0
    object_present = False
    indicator_on = False
    blink_state = False
elif object_in_roi:
    # Ada object di ROI → indikator berkedip
    object_detected_frames += 1
    object_lost_frames = 0
    
    if object_detected_frames >= OBJECT_CONFIRM_THRESHOLD:
        object_present = True
        indicator_on = True
        
        if frame_count % BLINK_INTERVAL == 0:
            blink_state = not blink_state
else:
    # Ada object hijau, tapi TIDAK di ROI
    object_detected_frames = 0
    object_lost_frames += 1
    
    if object_lost_frames >= OBJECT_LOST_THRESHOLD:
        object_present = False
        indicator_on = False
        blink_state = False
```

## Flow Logic Baru

### Skenario 1: Tidak Ada Object Sama Sekali
```
has_green_box = False
  ↓
indicator_on = False
blink_state = False
  ↓
ROI box: GRAY (tidak berkedip)
```

### Skenario 2: Ada Object di ROI
```
has_green_box = True AND object_in_roi = True
  ↓
object_detected_frames += 1
  ↓
if object_detected_frames >= OBJECT_CONFIRM_THRESHOLD:
    indicator_on = True
    blink_state toggles setiap BLINK_INTERVAL
  ↓
ROI box: BLUE (berkedip)
```

### Skenario 3: Ada Object tapi Tidak di ROI
```
has_green_box = True AND object_in_roi = False
  ↓
object_lost_frames += 1
  ↓
if object_lost_frames >= OBJECT_LOST_THRESHOLD:
    indicator_on = False
    blink_state = False
  ↓
ROI box: GRAY (tidak berkedip)
```

### Skenario 4: Auto Reset Terjadi
```
auto_reset_state = True
no_motion_frames >= NO_MOTION_THRESHOLD
  ↓
background_reference = blurred.copy()
indicator_on = False
blink_state = False
object_present = False
  ↓
ROI box: GRAY (tidak berkedip)
Background reference di-capture ulang
```

## Testing

### Cara Testing:
1. Jalankan program dengan `AUTO_RESET_ENABLED = True`
2. Pastikan tidak ada object di depan kamera
3. Tunggu hingga `no_motion_frames` mencapai `NO_MOTION_THRESHOLD` (300 frames ≈ 10 detik)
4. Verifikasi bahwa:
   - ROI box tetap GRAY (tidak berkedip)
   - Console print "[AUTO RESET] Background base updated"
   - Tidak ada bounding box hijau

### Expected Behavior:
- ✅ ROI box TIDAK berkedip ketika tidak ada object
- ✅ ROI box berkedip BIRU ketika ada object di ROI
- ✅ Auto reset background terjadi setelah NO_MOTION_THRESHOLD frames tanpa object
- ✅ Indikator reset ke GRAY setelah auto-reset

## File yang Diubah
- `main.py` - Line ~233-295 (Auto Reset Logic dan State Management)

## Catatan Penting
Logic auto-reset sekarang sangat sederhana:
1. Cek `AUTO_RESET_ENABLED`
2. Jika ON, cek apakah ada bounding box hijau (`has_green_box`)
3. Jika TIDAK ADA selama `NO_MOTION_THRESHOLD` → reset background reference
4. Capture ulang threshold dan jadikan base patokan baru
5. Reset semua indikator ke kondisi "no object detect"
