# 🎯 Real-time Object Distance Detection

Aplikasi streaming real-time untuk deteksi object yang mendekat/menjauh dari kamera menggunakan **YOLOv8**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![YOLO](https://img.shields.io/badge/YOLO-v8-purple.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

---

## ✨ Fitur

- ✅ **Real-time Detection** - Deteksi object dengan YOLOv8 Nano (cepat & ringan)
- ✅ **Distance Estimation** - Deteksi apakah object mendekat, menjauh, atau tetap
- ✅ **SIAGA Alert System** - Alert "⚠️ SIAGA" saat object mendekat 3 frame berturut-turut
- ✅ **SIAGA Hold Timer** - Alert tetap aktif 3 detik setelah object hilang
- ✅ **Visual Indicators** - Bounding box dengan warna berbeda untuk setiap status
- ✅ **Blinking SIAGA Alert** - Alert berkedip untuk menarik perhatian
- ✅ **FPS Counter** - Monitoring performa real-time
- ✅ **Snapshot** - Simpan frame dengan deteksi
- ✅ **Adjustable Threshold** - Atur confidence threshold on-the-fly
- ✅ **Multi-object Tracking** - Track multiple objects sekaligus

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Application

```bash
python main.py
```

---

## 🎨 Visual Indicators

| Warna | Status | Keterangan |
|-------|--------|------------|
| 🔴 **MERAH** | **MENDEKAT** | Object semakin dekat dengan kamera |
| 🟢 **HIJAU** | **TETAP** | Object pada jarak yang sama |
| 🔵 **BIRU** | **MENJAUH** | Object semakin jauh dari kamera |
| 🟠 **ORANGE + BLINKING** | **⚠️ SIAGA** | Object terdeteksi mendekat 3x berturut-turut |

---

## 🚨 SIAGA Alert System

### Cara Kerja:

```
1. Object terdeteksi MENDEKAT (bounding box membesar)
        ↓
2. Sistem menghitung frame berturut-turut
        ↓
3. Setelah 3 frame MENDEKAT → SIAGA diaktifkan
        ↓
4. Alert ditampilkan:
   - Badge "⚠️ SIAGA" di atas bounding box
   - Panel alert berkedip di info panel
   - Console log "[⚠️ SIAGA ACTIVE]"
        ↓
5. Object hilang dari frame
        ↓
6. SIAGA tetap aktif selama 3 detik (hold timer)
        ↓
7. Setelah 3 detik → SIAGA cleared
```

### Configuration:

Edit di `main.py`:

```python
# ObjectDistanceTracker parameters
self.tracker = ObjectDistanceTracker(
    max_history=30,              # Frame history untuk tracking
    siaga_frame_threshold=3,     # Frame berturut-turut untuk trigger SIAGA
    siaga_hold_time=3.0          # Detik SIAGA tetap aktif setelah object hilang
)
```

### SIAGA Flow Diagram:

```
Frame 1: MENDEKAT → Counter = 1
Frame 2: MENDEKAT → Counter = 2
Frame 3: MENDEKAT → Counter = 3 → ⚠️ SIAGA ACTIVATED! 🔴
Frame 4: Object hilang → Timer = 3.0s
Frame 5: - → Timer = 2.5s
Frame 6: - → Timer = 2.0s
Frame 7: - → Timer = 1.5s
Frame 8: - → Timer = 1.0s
Frame 9: - → Timer = 0.5s
Frame 10: Timer = 0.0s → ✓ SIAGA CLEARED 🟢
```

---

## 🎯 Cara Kerja

### 1. **Object Detection**
- Menggunakan YOLOv8 untuk mendeteksi object (person, car, dll)
- Setiap object mendapat bounding box

### 2. **Distance Estimation**
- Menghitung **area bounding box** sebagai proxy untuk jarak
- Prinsip: Object yang lebih dekat = bounding box lebih besar

### 3. **Trend Analysis**
- Menganalisa perubahan area selama 5-30 frame terakhir
- Menghitung persentase perubahan area

### 4. **Status Determination**
```
Area bertambah > 10%  → MENDEKAT (Merah)
Area berkurang > 10%  → MENJAUH (Biru)
Perubahan < 10%       → TETAP (Hijau)
```

---

## ⌨️ Keyboard Controls

| Tombol | Fungsi |
|--------|--------|
| `Q` | Quit/Keluar |
| `S` | Save snapshot (screenshot) |
| `+` / `=` | Increase confidence threshold |
| `-` | Decrease confidence threshold |

---

## 📊 Algoritma Distance Estimation

### Flow Chart:
```
Frame Input → YOLO Detection → Bounding Box → Area Calculation
                                                    ↓
                    Status Update ← Trend Analysis ← History Buffer
                        ↓
                Draw Bounding Box (Color-coded)
                        ↓
                  Display Output
```

### Formula:
```python
# Hitung area bounding box
area = (x2 - x1) * (y2 - y1)

# Hitung perubahan area
first_half = mean(areas[:n//2])
second_half = mean(areas[n//2:])

change_percent = ((second_half - first_half) / first_half) * 100

# Tentukan status
if change_percent > 10:
    status = "MENDEKAT"   # Merah
elif change_percent < -10:
    status = "MENJAUH"    # Biru
else:
    status = "TETAP"      # Hijau
```

---

## 🖼️ Output Display

```
┌─────────────────────────────────────────┐
│ FPS: 25.3  Time: 14:30:25              │
│                                          │
│  Legend:                                 │
│  🔴 Mendekat   🔵 Menjauh               │
│  🟢 Tetap                               │
│                                          │
│     ┌─────────┐                          │
│     │ PERSON  │ [MENDEKAT] 🔴            │
│     │ 0.95    │                          │
│     └─────────┘                          │
│        Area: 45000                       │
│                                          │
│           ┌──────┐                       │
│           │ CAR  │ [TETAP] 🟢            │
│           │ 0.87 │                       │
│           └──────┘                       │
│              Area: 120000                │
└─────────────────────────────────────────┘
```

---

## ⚙️ Configuration

Edit di `main.py`:

```python
# Camera ID (0 = default webcam)
camera_id=0

# Confidence threshold (0.0 - 1.0)
confidence_threshold=0.5

# Target classes (COCO dataset)
# 0 = person, 2 = car, 3 = motorcycle, etc.
target_classes = [0]  # Track person only

# History length (frames)
max_history=30

# Movement threshold (%)
movement_threshold=10  # 10% change
```

---

## 🧪 Testing

### Test 1: Basic Detection
```bash
python main.py
```
- Pastikan kamera terdeteksi
- Lihat FPS counter (should be > 15 FPS)
- Test dengan orang bergerak mendekat/menjauh

### Test 2: Snapshot
```
Tekan 'S' saat object terdeteksi
File akan tersimpan: snapshot_YYYYMMDD_HHMMSS.jpg
```

### Test 3: Threshold Adjustment
```
Tekan '+' untuk meningkatkan threshold (deteksi lebih strict)
Tekan '-' untuk menurunkan threshold (deteksi lebih sensitive)
```

---

## 📝 COCO Object Classes

YOLOv8 trained pada COCO dataset (80 classes):

| ID | Class | ID | Class |
|----|-------|----|-------|
| 0 | person | 1 | bicycle |
| 2 | car | 3 | motorcycle |
| 4 | airplane | 5 | bus |
| 6 | train | 7 | truck |
| ... | ... | ... | ... |

Full list: https://cocodataset.org/#home

---

## 🔧 Troubleshooting

### Camera tidak terdeteksi
```python
# Coba camera ID lain
detector = RealTimeDistanceDetector(camera_id=1)  # atau 2, 3, dst
```

### FPS terlalu rendah
```python
# Gunakan model lebih kecil (sudah default: yolov8n.pt)
# atau turunkan resolusi
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

### Deteksi tidak akurat
- Tingkatkan confidence threshold (`+` key)
- Pastikan pencahayaan cukup
- Object harus terlihat jelas di frame

### Status tidak berubah (stuck di "TETAP")
- Object bergerak terlalu lambat → tunggu lebih lama
- Object terlalu jauh → dekati kamera
- History terlalu panjang → kurangi `max_history`

---

## 📈 Performance

| Model | Speed (FPS) | Accuracy | Size |
|-------|-------------|----------|------|
| **YOLOv8n** (default) | ~30 FPS | Good | 3.2 MB |
| YOLOv8s | ~20 FPS | Better | 11 MB |
| YOLOv8m | ~10 FPS | Best | 26 MB |

*Tested on: Intel i5, 8GB RAM, Integrated GPU*

---

## 🎥 Use Cases

- 🏠 **Home Security** - Deteksi orang mendekat ke rumah
- 🚪 **Door Entry** - Monitoring orang masuk/keluar
- 🅿️ **Parking Monitor** - Deteksi mobil mendekat/menjauh
- 🚶 **Pedestrian Tracking** - Analisis pergerakan pejalan kaki
- 📦 **Warehouse** - Monitoring forklift/worker movement

---

## 📚 References

- **YOLOv8:** https://github.com/ultralytics/ultralytics
- **COCO Dataset:** https://cocodataset.org/
- **OpenCV:** https://opencv.org/

---

## 📄 License

Apache License 2.0

---

## 🙏 Credits

- **Ultralytics** - YOLOv8
- **OpenCV Team** - Computer Vision Library
- **COCO Dataset** - Object Detection Dataset

---

**Created:** 2026-03-07  
**Version:** 1.0.0  
**Folder:** V6_Deteksi_Object_Mendekat
