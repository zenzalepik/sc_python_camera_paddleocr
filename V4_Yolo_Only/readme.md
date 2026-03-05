# YOLOv8 Live Streaming Camera

Real-time object detection menggunakan YOLOv8 dengan live camera streaming.

## 🎯 Model YOLO yang Digunakan

**YOLOv8-Nano (`yolov8n.pt`)** - Pilihan terbaik untuk real-time:

| Model | Size | Parameters | mAP | CPU Speed | GPU Speed |
|-------|------|------------|-----|-----------|-----------|
| **YOLOv8n** | 6.2 MB | 3.2M | 37.3 | ~80 FPS | ~350 FPS ✅ |
| YOLOv8s | 21.5 MB | 11.2M | 44.9 | ~40 FPS | ~200 FPS |
| YOLOv8m | 49.7 MB | 25.9M | 50.2 | ~20 FPS | ~100 FPS |
| YOLOv8l | 97.5 MB | 43.7M | 52.9 | ~12 FPS | ~60 FPS |
| YOLOv8x | 144.4 MB | 68.2M | 53.9 | ~8 FPS | ~45 FPS |

### Kenapa YOLOv8-Nano?

✅ **Tercepat** - Real-time inference (30+ FPS)
✅ **Ringan** - Hanya 6.2 MB
✅ **Cukup Akurat** - 37.3 mAP untuk 80 COCO classes
✅ **Low Latency** - Cocok untuk live streaming
✅ **Low Resource** - Bisa jalan di CPU biasa

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run

**Option 1: Pakai batch file**
```bash
run.bat
```

**Option 2: Manual**
```bash
python main.py
```

## 🎮 Controls

| Key | Function |
|-----|----------|
| `q` | Quit |
| `s` | Save snapshot |
| `r` | Start/stop recording |
| `c` | Change confidence threshold |
| `f` | Toggle class filter (person only / all) |
| `+` | Increase confidence |
| `-` | Decrease confidence |

## ⚙️ Configuration

Edit file `.env` untuk customize:

### Camera Settings
```env
CAMERA_ID=0                  # Camera device ID
CAMERA_WIDTH=640             # Frame width
CAMERA_HEIGHT=480            # Frame height
CAMERA_FPS=30                # Target FPS
```

### Model Settings
```env
YOLO_MODEL=yolov8n.pt        # Nano = fastest
CONF_THRESHOLD=0.4           # Minimum confidence
IOU_THRESHOLD=0.45           # NMS IoU threshold
CLASSES_FILTER=              # Empty = all classes
```

### Performance
```env
USE_GPU=True                 # Use CUDA if available
HALF_PRECISION=True          # FP16 for faster inference
```

## 📁 Output

### Snapshots
Snapshot akan disimpan di folder `snapshots/` dengan format:
```
snapshots/snapshot_20260304_143025.jpg
```

### Recording
Video recording akan disimpan di folder `recordings/` dengan format:
```
recordings/recording_20260304_143025.avi
```

## 🎯 Detected Objects (80 COCO Classes)

- **Vehicles**: car, motorcycle, bus, truck, bicycle, boat, train, airplane
- **People**: person
- **Animals**: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
- **Objects**: backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket
- **Furniture**: bottle, wine glass, cup, fork, knife, spoon, bowl, chair, couch, potted plant, bed, dining table, toilet
- **Electronics**: tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase
- **Food**: banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake
- **Others**: traffic light, fire hydrant, stop sign, parking meter, bench, scissors, teddy bear, hair drier, toothbrush

## 📊 Performance Tips

### Untuk FPS Lebih Tinggi:
1. Gunakan `yolov8n.pt` (sudah default)
2. Turunkan resolusi camera:
   ```env
   CAMERA_WIDTH=320
   CAMERA_HEIGHT=240
   ```
3. Enable GPU:
   ```env
   USE_GPU=True
   HALF_PRECISION=True
   ```

### Untuk Akurasi Lebih Baik:
1. Ganti model ke yang lebih besar:
   ```env
   YOLO_MODEL=yolov8s.pt    # atau yolov8m.pt
   ```
2. Turunkan confidence threshold:
   ```env
   CONF_THRESHOLD=0.25
   ```

## 🔧 Troubleshooting

### Camera tidak terbuka:
```env
CAMERA_ID=1                  # Coba camera ID lain
```

### Out of memory (GPU):
```env
USE_GPU=False                # Fallback ke CPU
```

### Model tidak terdownload:
- Pastikan internet aktif
- Download manual dari https://github.com/ultralytics/assets/releases

## 📝 License

This project uses:
- **YOLOv8** by Ultralytics - AGPL-3.0 License
- **OpenCV** - Apache 2.0 License

## 🙏 Credits

- **Ultralytics** - https://github.com/ultralytics/ultralytics
- **YOLOv8** - https://docs.ultralytics.com/

---

**Created:** 2026-03-04
**Version:** 1.0.0
**Folder:** V4_Yolo_Only
