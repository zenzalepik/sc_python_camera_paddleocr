# YOLO Version Comparison Guide

## 📊 YOLOv8 Model Comparison

| Model | File Size | Parameters | mAP val | Inference Speed (CPU) | Inference Speed (GPU) | Use Case |
|-------|-----------|------------|---------|----------------------|----------------------|----------|
| **YOLOv8n** | 6.2 MB | 3.2M | 37.3 | ~80 FPS | ~350 FPS | **Real-time streaming** ✅ |
| **YOLOv8s** | 21.5 MB | 11.2M | 44.9 | ~40 FPS | ~200 FPS | Balanced speed/accuracy |
| **YOLOv8m** | 49.7 MB | 25.9M | 50.2 | ~20 FPS | ~100 FPS | Higher accuracy needed |
| **YOLOv8l** | 97.5 MB | 43.7M | 52.9 | ~12 FPS | ~60 FPS | High accuracy, powerful GPU |
| **YOLOv8x** | 144.4 MB | 68.2M | 53.9 | ~8 FPS | ~45 FPS | Maximum accuracy |

---

## 🎯 Recommendation for Your Project

### ✅ **RECOMMENDED: YOLOv8-Nano (`yolov8n.pt`)**

**Kenapa?**
1. **Tercepat** - 350 FPS pada GPU, 80 FPS pada CPU
2. **Paling Ringan** - Hanya 6.2 MB
3. **Real-time Ready** - Bisa handle 30 FPS camera dengan mudah
4. **Low Memory** - Cocok untuk laptop/PC biasa
5. **Low Power** - Tidak bikin GPU/CPU panas

**Cocok untuk:**
- ✅ Live camera streaming
- ✅ Real-time object detection
- ✅ Video surveillance
- ✅ Embedded systems (Jetson Nano, Raspberry Pi)
- ✅ Low-end devices

**Kurang cocok untuk:**
- ❌ Aplikasi yang butuh akurasi sangat tinggi
- ❌ Deteksi objek sangat kecil
- ❌ Kondisi lighting sangat buruk

---

## 📈 Performance Benchmarks

### On NVIDIA GTX 1060 (6GB VRAM)
```
Model    | FPS    | VRAM Usage | Latency
---------|--------|------------|---------
YOLOv8n  | 350    | ~200 MB    | ~3 ms
YOLOv8s  | 200    | ~400 MB    | ~5 ms
YOLOv8m  | 100    | ~800 MB    | ~10 ms
YOLOv8l  | 60     | ~1.5 GB    | ~17 ms
YOLOv8x  | 45     | ~2.0 GB    | ~22 ms
```

### On Intel i7-8700K (CPU only)
```
Model    | FPS    | CPU Usage | Latency
---------|--------|-----------|---------
YOLOv8n  | 80     | ~30%      | ~12 ms
YOLOv8s  | 40     | ~50%      | ~25 ms
YOLOv8m  | 20     | ~70%      | ~50 ms
YOLOv8l  | 12     | ~85%      | ~83 ms
YOLOv8x  | 8      | ~95%      | ~125 ms
```

---

## 🔧 How to Change Model

Edit file `.env`:

```env
# Fastest (recommended)
YOLO_MODEL=yolov8n.pt

# Balanced
YOLO_MODEL=yolov8s.pt

# More accurate
YOLO_MODEL=yolov8m.pt

# Maximum accuracy
YOLO_MODEL=yolov8l.pt
# or
YOLO_MODEL=yolov8x.pt
```

---

## 🎓 Understanding the Trade-offs

### Speed vs Accuracy

```
Accuracy ↑
    |
    |                                   ● YOLOv8x
    |                               ● YOLOv8l
    |                           ● YOLOv8m
    |                       ● YOLOv8s
    |                   ● YOLOv8n ← SWEET SPOT
    |___________________________________________→ Speed
```

### Model Size vs Performance

```
Size (MB)
  150 |                               ● YOLOv8x (144 MB)
      |
  100 |                       ● YOLOv8l (97 MB)
      |
   50 |               ● YOLOv8m (50 MB)
      |
   20 |       ● YOLOv8s (21 MB)
      |
    5 |   ● YOLOv8n (6 MB) ← BEST FOR REAL-TIME
      |___________________________________________→ Performance
```

---

## 💡 Tips for Best Performance

### 1. Use GPU if Available
```env
USE_GPU=True
HALF_PRECISION=True  # FP16 for 2x speedup on GPU
```

### 2. Optimize Resolution
```env
# For speed (lower resolution)
CAMERA_WIDTH=320
CAMERA_HEIGHT=240

# For accuracy (higher resolution)
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
```

### 3. Adjust Confidence Threshold
```env
# More detections (lower threshold)
CONF_THRESHOLD=0.25

# Fewer, more confident detections
CONF_THRESHOLD=0.5
```

### 4. Filter Classes
```env
# Only detect specific objects
CLASSES_FILTER=person,car,motorcycle

# This speeds up post-processing
```

---

## 🚀 Advanced: Using YOLOv9 or YOLOv10

### YOLOv9 (Newer than v8)
- Better accuracy than v8
- Similar speed
- Not as widely tested

```bash
pip install ultralytics
# Use: yolov9n.pt, yolov9s.pt, etc.
```

### YOLOv10 (Latest)
- State-of-the-art
- Optimized architecture
- May require more setup

```bash
pip install ultralytics
# Use: yolov10n.pt, yolov10s.pt, etc.
```

**Recommendation:** Stick with **YOLOv8** for stability and community support.

---

## 📝 Summary

**For your live streaming camera project:**

✅ **Use: YOLOv8-Nano (`yolov8n.pt`)**
- Fastest real-time performance
- Smallest model size
- Good enough accuracy for most cases
- Works on CPU and GPU

🔄 **Alternative: YOLOv8-Small (`yolov8s.pt`)**
- If you need better accuracy
- Still real-time on GPU
- 3x larger than Nano

❌ **Avoid for real-time:**
- YOLOv8m, YOLOv8l, YOLOv8x (too slow for smooth streaming)

---

**Created:** 2026-03-04
**Project:** V4_Yolo_Only
